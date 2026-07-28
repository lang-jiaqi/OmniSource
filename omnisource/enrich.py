"""OpenAlex enrichment for selected papers.

Looks up the papers we've *already chosen* (not a crawl source) and fills
disambiguated author ids, affiliations, and citation count. Cheap: a few
cached lookups per run. Feeds quality signals, watchlist matching, and the
future author graph. OpenAlex is free and needs no key (a mailto gets the
"polite pool" rate limits).
"""
from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import requests
from pypdf import PdfReader
from rapidfuzz import fuzz

from .config import CACHE_DIR, CACHE_TTL
from .dedup import normalized_title
from .memory.cache import cached_get
from .models import Signal

API = "https://api.openalex.org/works"
S2_PAPER = "https://api.semanticscholar.org/graph/v1/paper"
MAILTO = "omnisource@users.noreply.github.com"
TITLE_MATCH_THRESHOLD = 85
NAME_MATCH_THRESHOLD = 88
_ARXIV_ID = re.compile(r"arxiv\.org/abs/([0-9]+\.[0-9]+)", re.I)
# Comma / colon / pipe are reserved delimiters in OpenAlex's filter syntax, so a
# title containing them (e.g. "Foo: A Bar, Baz Study") makes title.search return
# a 400. Strip them before building the filter — the search is fuzzy anyway.
_OPENALEX_RESERVED = re.compile(r"[,:|]+")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")
_PDF_ABSTRACT_RE = re.compile(r"\babstract\b", re.I)
_PDF_AFFILIATION_KEYWORDS = re.compile(
    r"\b("
    r"university|institute|college|school|department|laborator(?:y|ies)|lab|"
    r"academy|research|center|centre|systems|science|technology|engineering|"
    r"openai|anthropic|deepmind|google|microsoft|meta|nvidia|amazon|adobe|huawei|"
    r"baidu|tencent|alibaba|bytedance|tsinghua|stanford|berkeley|mit|cmu|"
    r"eth|epfl|kaist|hkust|thu|cuhk|sjtu|zhejiang"
    r")\b",
    re.I,
)
_PDF_MARKED_INST_RE = re.compile(r"^(?P<mark>[0-9]{1,2}|[a-z])[\)\].,\s]+(?P<inst>.+)$", re.I)
_PDF_AUTHOR_MARK_RE = re.compile(r"(?P<name>[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+)+)\s*(?P<mark>[0-9]{1,2}|[a-z])\b")
_PDF_INLINE_DIGIT_MARK_RE = re.compile(r"(?<!\d)(?P<mark>[0-9]{1,2})\s*(?=[A-Z][A-Za-zÀ-ÖØ-öø-ÿ’'&.-])")


def _norm_name(name: str) -> str:
    return re.sub(r"[^a-z ]", "", (name or "").lower()).strip()


def _s2_author_profile(author_id: object) -> str:
    if not author_id:
        return ""
    return "https://www.semanticscholar.org/author/" + str(author_id)


def _all_author_institutions(signal: Signal) -> bool:
    return bool(signal.author_nodes) and all(node.get("institutions") for node in signal.author_nodes)


def _clean_pdf_line(line: str) -> str:
    line = _EMAIL_RE.sub(" ", line)
    line = re.sub(r"https?://\S+", " ", line)
    line = re.sub(r"\s+", " ", line).strip(" ,;")
    return line


def _arxiv_pdf_url(url: str) -> str | None:
    m = _ARXIV_ID.search(url or "")
    if not m:
        return None
    return f"https://arxiv.org/pdf/{m.group(1)}"


def _cached_get_bytes(url: str, ttl: int = CACHE_TTL, timeout: int = 30) -> bytes:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    import hashlib

    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    path = CACHE_DIR / f"{key}.bin"
    if path.exists() and time.time() - path.stat().st_mtime < ttl:
        return path.read_bytes()
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (OmniSource)"})
    resp.raise_for_status()
    path.write_bytes(resp.content)
    return resp.content


def _extract_pdf_first_page_text(pdf_body: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_body))
    if not reader.pages:
        return ""
    return reader.pages[0].extract_text() or ""


def _infer_pdf_institutions(first_page_text: str) -> tuple[list[str], dict[str, str]]:
    """Best-effort institution extraction from an arXiv first page.

    Returns (institutions, marker_map). marker_map maps footnote markers such as
    "1" or "a" to an institution when the PDF text preserves those markers.
    """
    pre_abstract = _PDF_ABSTRACT_RE.split(first_page_text, maxsplit=1)[0]
    raw_lines = [_clean_pdf_line(line) for line in pre_abstract.splitlines()]
    lines = [line for line in raw_lines if len(line) >= 4]
    institutions: list[str] = []
    marker_map: dict[str, str] = {}
    for line in lines:
        if not _PDF_AFFILIATION_KEYWORDS.search(line):
            continue
        if len(line.split()) > 28:
            continue
        chunks = _split_pdf_institution_chunks(line)
        for chunk in chunks:
            if not _PDF_AFFILIATION_KEYWORDS.search(chunk):
                continue
            marker = None
            match = _PDF_MARKED_INST_RE.match(chunk)
            if match:
                marker, chunk = match.group("mark").lower(), match.group("inst").strip(" ,;")
            chunk = re.sub(r"^\W+", "", chunk).strip(" ,;")
            if not chunk or (len(chunk) < 4 and not chunk.isupper()):
                continue
            if chunk not in institutions:
                institutions.append(chunk)
            if marker and marker not in marker_map:
                marker_map[marker] = chunk
    return institutions[:8], marker_map


def _split_pdf_institution_chunks(line: str) -> list[str]:
    matches = list(_PDF_INLINE_DIGIT_MARK_RE.finditer(line))
    if matches and (len(matches) > 1 or matches[0].start() <= 2):
        chunks = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(line)
            inst = line[match.end():end].strip(" ,;")
            if inst:
                chunks.append(f"{match.group('mark')} {inst}")
        if chunks:
            return chunks
    return [chunk.strip(" ,;") for chunk in re.split(r"\s*[;•]\s*", line) if chunk.strip(" ,;")]


def _assign_pdf_institutions(signal: Signal, institutions: list[str], marker_map: dict[str, str], first_page_text: str) -> int:
    if not institutions:
        return 0
    if not signal.author_nodes and signal.authors:
        signal.author_nodes = [{"name": name, "institutions": []} for name in signal.authors]
    for inst in institutions:
        if inst not in signal.affiliations:
            signal.affiliations.append(inst)

    assigned = 0
    if marker_map:
        author_marks = {m.group("name").lower(): m.group("mark").lower() for m in _PDF_AUTHOR_MARK_RE.finditer(first_page_text)}
        for node in signal.author_nodes:
            if node.get("institutions"):
                continue
            name = str(node.get("name") or "")
            norm = name.lower()
            mark = author_marks.get(norm)
            if not mark:
                best, best_score = None, 0
                for candidate, candidate_mark in author_marks.items():
                    score = fuzz.token_set_ratio(norm, candidate)
                    if score > best_score:
                        best, best_score = candidate_mark, score
                if best_score >= NAME_MATCH_THRESHOLD:
                    mark = best
            inst = marker_map.get(mark or "")
            if inst:
                node.setdefault("institutions", []).append(inst)
                assigned += 1

    if assigned:
        return assigned
    if len(institutions) == 1:
        for node in signal.author_nodes:
            if node.get("institutions"):
                continue
            node.setdefault("institutions", []).append(institutions[0])
            assigned += 1
    return assigned


def enrich_openalex(signals: list[Signal]) -> int:
    """Enrich paper signals in place. Returns how many were enriched."""
    enriched = 0
    for s in signals:
        if s.type != "paper" or not s.title:
            continue
        work = _lookup(s.title)
        if work is None:
            continue
        s.citation_count = work.get("cited_by_count")
        affs, ids, nodes = [], [], []
        for a in work.get("authorships", []):
            author = a.get("author") or {}
            aid = (author.get("id") or "").rsplit("/", 1)[-1]
            insts = [i.get("display_name") for i in a.get("institutions", []) if i.get("display_name")]
            for name in insts:
                if name not in affs:
                    affs.append(name)
            if aid:
                ids.append(aid)
            nodes.append({"name": author.get("display_name") or "?", "id": aid, "institutions": insts})
        s.affiliations = affs
        s.author_ids = ids
        s.author_nodes = nodes
        enriched += 1
    return enriched


def enrich_author_stats(signal: Signal, max_authors: int | None = None) -> None:
    """Fill each author node with citations / h-index / works (for graph node
    sizing). One cached OpenAlex call per author; only for papers we graph."""
    nodes = [node for node in signal.author_nodes if node.get("id")]
    if max_authors:
        nodes = nodes[:max_authors]

    def fetch(node: dict) -> tuple[dict, dict | None]:
        aid = node.get("id")
        try:
            body = cached_get(f"https://api.openalex.org/authors/{aid}", params={"mailto": MAILTO}, timeout=8)
            return node, json.loads(body)
        except Exception:
            return node, None

    if not nodes:
        return
    with ThreadPoolExecutor(max_workers=min(6, len(nodes))) as executor:
        responses = executor.map(fetch, nodes)
        for node, data in responses:
            if not data:
                continue
            node["citations"] = data.get("cited_by_count") or 0
            node["h_index"] = (data.get("summary_stats") or {}).get("h_index") or 0
            node["works"] = data.get("works_count") or 0
            # Contact / lookup links for the graph tooltip + click-through.
            node["profile"] = data.get("id") or ""        # OpenAlex author page
            if data.get("orcid"):
                node["orcid"] = data["orcid"]              # full https://orcid.org/... URL


def enrich_coauthorship(signal: Signal, max_authors: int | None = None) -> None:
    """For each author, fetch their collaboration histogram (OpenAlex group_by)
    and record how many papers they've co-authored with the OTHER authors of this
    paper — the prior-collaboration strength that thickens graph edges."""
    paper_author_ids = {n["id"] for n in signal.author_nodes if n.get("id")}
    nodes = [node for node in signal.author_nodes if node.get("id")]
    if max_authors:
        nodes = nodes[:max_authors]

    def fetch(node: dict) -> tuple[dict, list[dict]]:
        aid = node.get("id")
        try:
            body = cached_get(API, params={
                "filter": f"authorships.author.id:{aid}",
                "group_by": "authorships.author.id",
                "mailto": MAILTO,
            }, timeout=8)
            return node, json.loads(body).get("group_by", [])
        except Exception:
            return node, []

    if not nodes:
        return
    with ThreadPoolExecutor(max_workers=min(6, len(nodes))) as executor:
        responses = executor.map(fetch, nodes)
        for node, buckets in responses:
            collabs = {}
            for bucket in buckets:
                oid = (bucket.get("key") or "").rsplit("/", 1)[-1]
                if oid in paper_author_ids and oid != node.get("id"):
                    collabs[oid] = bucket.get("count", 0)
            node["collabs"] = collabs


def enrich_semantic_scholar(signal: Signal) -> None:
    """Fill gaps OpenAlex leaves on fresh preprints: Semantic Scholar often has
    author affiliations + a homepage where OpenAlex is still blank. We match S2
    authors to our nodes by name and *union* the affiliations, then attach the
    homepage for the graph's contact tooltip. One cached call per paper; S2's
    keyless pool is rate-limited, so we back off and degrade gracefully."""
    m = _ARXIV_ID.search(signal.url or "")
    if not m:
        return
    aid = m.group(1)
    fields = "authors.authorId,authors.name,authors.affiliations,authors.homepage,authors.hIndex"
    body = None
    for attempt in range(3):
        try:
            body = cached_get(f"{S2_PAPER}/arXiv:{aid}", params={"fields": fields}, timeout=12)
            break
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 429 and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            return
        except Exception:
            return
    if not body:
        return
    s2_authors = json.loads(body).get("authors", [])
    if not signal.author_nodes:
        nodes = []
        affs = []
        for author in s2_authors:
            name = author.get("name") or "?"
            insts = [inst for inst in (author.get("affiliations") or []) if inst]
            for inst in insts:
                if inst not in affs:
                    affs.append(inst)
            node = {
                "id": "s2:" + str(author.get("authorId") or name),
                "name": name,
                "institutions": insts,
                "h_index": author.get("hIndex") or 0,
            }
            if author.get("authorId"):
                node["profile"] = _s2_author_profile(author["authorId"])
            if author.get("homepage"):
                hp = author["homepage"].strip()
                node["homepage"] = hp if hp.startswith("http") else "https://" + hp
            nodes.append(node)
        signal.author_nodes = nodes
        signal.affiliations = affs
        return
    for s2 in s2_authors:
        s2_norm = _norm_name(s2.get("name", ""))
        if not s2_norm:
            continue
        # match to the OpenAlex node with the closest name
        best, best_score = None, 0
        for node in signal.author_nodes:
            score = fuzz.token_set_ratio(s2_norm, _norm_name(node.get("name", "")))
            if score > best_score:
                best, best_score = node, score
        if not best or best_score < NAME_MATCH_THRESHOLD:
            continue
        for inst in (s2.get("affiliations") or []):
            if inst and inst not in best.setdefault("institutions", []):
                best["institutions"].append(inst)
        if s2.get("homepage") and not best.get("homepage"):
            hp = s2["homepage"].strip()
            best["homepage"] = hp if hp.startswith("http") else "https://" + hp
        if s2.get("authorId") and not best.get("profile"):
            best["profile"] = _s2_author_profile(s2["authorId"])
        if s2.get("hIndex") and not best.get("h_index"):
            best["h_index"] = s2["hIndex"]


def enrich_arxiv_pdf_affiliations(signal: Signal) -> int:
    """Best-effort fallback for fresh arXiv papers whose metadata lacks
    affiliations. Downloads the arXiv PDF, extracts first-page text, and fills
    missing author institutions only when the guess is reasonably conservative."""
    if signal.type != "paper" or _all_author_institutions(signal):
        return 0
    pdf_url = _arxiv_pdf_url(signal.url or "")
    if not pdf_url:
        return 0
    try:
        text = _extract_pdf_first_page_text(_cached_get_bytes(pdf_url, timeout=12))
    except Exception:
        return 0
    institutions, marker_map = _infer_pdf_institutions(text)
    return _assign_pdf_institutions(signal, institutions, marker_map, text)


_TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", re.S)
_GITHUB_REPO = re.compile(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", re.I)
_GITHUB_NONREPO = {"blog", "about", "features", "topics", "sponsors", "orgs", "settings"}


def enrich_code_repo(signals: list[Signal]) -> int:
    """Actually look inside a paper's linked code repo — a link alone doesn't mean
    open source (could be a product page, an empty/private/archived repo, or code
    with no license). Fetch the GitHub repo's license / size / status into
    signal.extra['repo'] so the quality scorer can judge real openness."""
    import os
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    done = 0
    for s in signals:
        if not s.code_url:
            continue
        m = _GITHUB_REPO.search(s.code_url)
        if not m or m.group(1).split("/")[1] in _GITHUB_NONREPO:
            s.extra["repo"] = {"github": False}  # non-GitHub link (cloud/product page)
            continue
        repo = re.sub(r"\.git$", "", m.group(1)).strip("/")
        try:
            data = json.loads(cached_get(f"https://api.github.com/repos/{repo}", headers=headers))
        except Exception:
            s.extra["repo"] = {"github": True, "ok": False}  # 404 / private / unreachable
            continue
        s.extra["repo"] = {
            "github": True, "ok": True,
            "license": (data.get("license") or {}).get("spdx_id"),
            "size": data.get("size", 0),
            "language": data.get("language"),
            "archived": bool(data.get("archived")),
            "fork": bool(data.get("fork")),
            "stars": data.get("stargazers_count", 0),
        }
        done += 1
    return done


def enrich_blog_fulltext(signals: list[Signal]) -> int:
    """Best-effort: fetch each blog post and record its body word count, a
    substance signal for the quality scorer. Degrades silently — many lab blogs
    block scrapers, in which case the scorer falls back to the RSS summary."""
    blogs = [s for s in signals if s.type == "blog" and s.url]
    done = 0
    for s in blogs:
        try:
            html_body = cached_get(s.url, headers={"User-Agent": "Mozilla/5.0 (OmniSource)"})
        except Exception:
            continue
        text = _TAG_RE.sub(" ", html_body)
        words = len(text.split())
        if words > 0:
            s.extra["word_count"] = words
            done += 1
    return done


def _lookup(title: str) -> dict | None:
    """Title search + fuzzy verify, so we don't attach the wrong paper's data."""
    try:
        body = cached_get(API, params={
            "filter": f"title.search:{_OPENALEX_RESERVED.sub(' ', title).strip()}",
            "per_page": 1,
            "mailto": MAILTO,
        })
        results = json.loads(body).get("results", [])
    except Exception as exc:
        print(f"    ! openalex lookup failed: {exc}")
        return None
    if not results:
        return None
    work = results[0]
    if fuzz.token_set_ratio(normalized_title(title), normalized_title(work.get("title", ""))) < TITLE_MATCH_THRESHOLD:
        return None
    return work
