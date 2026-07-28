"""Six-expert review pass for the daily report (the CS Paper Distiller engine,
folded into the report workflow as a scoring layer rather than a hard gate).

The distiller's hub was calibrated for *settled* papers — it leans on accumulated
citations and an absolute keep-threshold, which filters out every fresh preprint
(no citations yet). For the daily radar we want *promising new* work, so we keep
only the engine's content review (the five per-dimension scores, which are
intrinsic and available on day one) and combine them with other *leading*
signals — author/lab track record, early velocity, and the LLM's novelty read —
into a single "potential" score. Lagging totals (citation counts) are not used.
"""
from __future__ import annotations

import math
import re
from statistics import mean

from ..models import Signal

_ENGINE = None  # lazily built; reused across papers in a run


def _engine():
    global _ENGINE
    if _ENGINE is None:
        from ..distiller.reviewer import RuleBasedReviewer
        from ..distiller.router import PaperRouter
        from ..distiller.selection import ExpertSelector
        from ..distiller.skills import load_skill_library
        from ..distiller.taxonomy import load_taxonomy
        tax = load_taxonomy("cs-foundation-v1")
        skills = load_skill_library(tax)
        _ENGINE = (tax, PaperRouter(tax), ExpertSelector(tax),
                   RuleBasedReviewer(tax, skills))
    return _ENGINE


def _to_candidate(s: Signal):
    from ..distiller.models import PaperCandidate
    return PaperCandidate(
        paper_id=s.id, title=s.title, abstract=s.summary or "",
        authors=s.authors, published_at=s.published_at,
        arxiv_id=s.id, url=s.url, github_url=s.code_url,
        citation_count=s.citation_count, hf_upvotes=s.popularity or 0,
    )


# --- leading-indicator components (all available on the day of publication) ---

def _author_reputation(s: Signal) -> float:
    """Strongest author's track record. A high-h-index author or a paper from a
    productive lab predicts value before any citation has landed. 0..1."""
    hs = [n.get("h_index", 0) or 0 for n in (s.author_nodes or [])]
    return min(1.0, (max(hs) if hs else 0) / 60.0)


_INSTITUTION_PRIORS = {
    "openai": 1.00,
    "deepmind": 1.00,
    "anthropic": 0.98,
    "stanford": 0.98,
    "massachusetts institute of technology": 0.98,
    "mit": 0.98,
    "carnegie mellon": 0.97,
    "university of california berkeley": 0.96,
    "uc berkeley": 0.96,
    "berkeley": 0.96,
    "princeton": 0.95,
    "harvard": 0.95,
    "caltech": 0.95,
    "university of oxford": 0.94,
    "university of cambridge": 0.94,
    "eth zurich": 0.93,
    "epfl": 0.92,
    "tsinghua": 0.92,
    "peking university": 0.92,
    "university of washington": 0.91,
    "cornell": 0.91,
    "university of illinois urbana champaign": 0.90,
    "uiuc": 0.90,
    "university of toronto": 0.90,
    "new york university": 0.88,
    "columbia university": 0.88,
    "university of california san diego": 0.88,
    "ucla": 0.88,
    "national university of singapore": 0.88,
    "nanyang technological university": 0.86,
    "microsoft research": 0.94,
    "google research": 0.94,
    "meta ai": 0.93,
    "nvidia": 0.92,
    "bytedance": 0.86,
}


def _norm_inst(name: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", (name or "").lower()).strip()


def _institution_reputation(s: Signal) -> float:
    """Weak prestige prior from author affiliations. This is deliberately small
    and additive: affiliation can help prioritize a crowded daily queue, but it
    should never override content quality, novelty, or evidence."""
    names = set(s.affiliations or [])
    for node in s.author_nodes or []:
        names.update(node.get("institutions") or [])
    best = 0.0
    for name in names:
        norm = _norm_inst(name)
        for raw_alias, score in _INSTITUTION_PRIORS.items():
            alias = _norm_inst(raw_alias)
            if alias and (alias == norm or alias in norm):
                best = max(best, score)
    return best


def _early_velocity(s: Signal, today) -> float:
    """Buzz *per day since release*, not the raw total — a paper pulling upvotes
    three days out is a stronger signal than an old one with the same total. 0..1."""
    pop = s.popularity or 0
    if pop <= 0:
        return 0.0
    age_days = max(1, (today - s.published_at.date()).days)
    velocity = pop / age_days
    return min(1.0, math.log1p(velocity) / math.log1p(30))


def _llm_quality(s: Signal) -> float | None:
    """The analyst's age-independent read of the paper, if the LLM step ran."""
    vals = [v for v in (s.llm_relevance, s.novelty) if v is not None]
    return mean(vals) if vals else None


def _verified_open_source(s: Signal) -> float:
    """Binary open-source check from inspecting the linked repo (enrich_code_repo):
    1.0 only if the repo is reachable, has real code, AND carries an open-source
    license. Everything else — no link, non-GitHub page, empty/private repo, or
    code with no license (legally all-rights-reserved) — is 0."""
    if not s.code_url:
        return 0.0
    repo = (s.extra or {}).get("repo")
    if not repo or not repo.get("github") or not repo.get("ok"):
        return 0.0  # product/cloud page, or unreachable/private repo
    has_code = (repo.get("size", 0) > 50) and bool(repo.get("language"))
    has_license = repo.get("license") not in (None, "NOASSERTION")
    return 1.0 if (has_code and has_license) else 0.0


_TIERS = [(0.60, "high_potential"), (0.45, "promising")]
_DIMS = ("novelty", "workload", "open_source_completeness",
         "insight_contribution", "paper_presentation")
_HARNESS = "cs-distiller-mvp-v1"


def review_papers(signals: list[Signal], today=None) -> int:
    """Annotate paper signals in place with the six-expert review + potential
    score. Advisory only: nothing is dropped here. Returns how many were scored."""
    import datetime as dt
    today = today or dt.date.today()
    papers = [s for s in signals if s.type == "paper"]
    if not papers:
        return 0
    _tax, router, selector, reviewer = _engine()

    for s in papers:
        cand = _to_candidate(s)
        router.route(cand)
        specs = selector.select(cand.primary_leaf or "ai.ml_foundations",
                                cand.canonical_id, _HARNESS)
        reviews = [reviewer.review(cand, spec) for spec in specs]
        dims = {d: round(mean(getattr(r.scores, d) for r in reviews), 3) for d in _DIMS}
        # Replace the engine's link-presence guess with a real repo inspection.
        dims["open_source_completeness"] = _verified_open_source(s)
        s.review_scores = dims

        # Content quality from the engine: the four intrinsic dimensions (workload
        # leans on full-text/scale evidence we don't fetch daily, so it's excluded).
        content = mean([dims["novelty"], dims["insight_contribution"],
                        dims["open_source_completeness"], dims["paper_presentation"]])
        author_rep = _author_reputation(s)
        inst_rep = _institution_reputation(s)
        dims["institution_signal"] = round(inst_rep, 3)
        velocity = _early_velocity(s, today)
        code = 1.0 if s.code_url else 0.0
        llm = _llm_quality(s)

        # Blend leading signals. Without the LLM read, fold its weight into content.
        if llm is not None:
            potential = (0.30 * content + 0.21 * llm + 0.18 * author_rep
                         + 0.13 * velocity + 0.10 * code + 0.08 * inst_rep)
        else:
            potential = (0.42 * content + 0.22 * author_rep
                         + 0.16 * velocity + 0.10 * code + 0.10 * inst_rep)
        s.review_score = round(min(1.0, potential), 3)

        s.review_decision = next((name for cut, name in _TIERS if s.review_score >= cut),
                                 "speculative")
        s.review_reason = _reason(content, author_rep, inst_rep, velocity, llm)
    return len(papers)


def _reason(content: float, author_rep: float, inst_rep: float, velocity: float,
            llm: float | None) -> str:
    parts = [("content", content), ("author track-record", author_rep),
             ("institution signal", inst_rep), ("early buzz", velocity)]
    if llm is not None:
        parts.append(("LLM novelty", llm))
    top = max(parts, key=lambda p: p[1])
    return f"driven by {top[0]} ({top[1]:.2f})"


# --- shared helpers ---------------------------------------------------------

def _log_norm(value: float, ceiling: float) -> float:
    """Squash a positive unbounded value into 0..1 via log, hitting ~1 at ceiling."""
    if value <= 0:
        return 0.0
    return min(1.0, math.log1p(value) / math.log1p(ceiling))


def _age_days(iso: str | None, today) -> int | None:
    if not iso:
        return None
    import datetime as dt
    try:
        d = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    except ValueError:
        return None
    return max(0, (today - d).days)


def _tier(score: float) -> str:
    return next((name for cut, name in _TIERS if score >= cut), "speculative")


# --- repos: predict a valuable open-source project before stars pile up ------

def review_repos(signals: list[Signal], today=None) -> int:
    """Score each repo's potential from leading signals: star *velocity* (not the
    total), project maturity, topical relevance, and adoption. In place; advisory."""
    import datetime as dt
    today = today or dt.date.today()
    repos = [s for s in signals if s.type == "repo"]
    for s in repos:
        ex = s.extra or {}
        stars = int(ex.get("total_stars") or s.popularity or 0)
        age = _age_days(ex.get("created_at"), today)
        # Momentum favors actual GitHub Trending evidence when present. Search
        # fallback repos use estimated lifetime stars/day so old incumbents do
        # not win merely because they have accumulated many stars.
        trend_stars = int(ex.get("trending_stars") or 0)
        if trend_stars:
            period_days = {"daily": 1, "weekly": 7, "monthly": 30}.get(str(ex.get("trending_period")), 1)
            momentum = _log_norm(trend_stars / max(1, period_days), 40)
        else:
            velocity = float(ex.get("star_velocity") or 0.0)
            if not velocity and age is not None:
                velocity = stars / max(1, age)
            momentum = _log_norm(velocity, 8) if velocity else _log_norm(s.popularity or 0, 4000)
        # maturity: the trappings of a real, maintained project
        push_age = _age_days(ex.get("pushed_at"), today)
        maturity = sum([
            0.30 if ex.get("license") else 0.0,
            0.25 if ex.get("topics") else 0.0,
            0.20 if (s.summary or "").strip() else 0.0,
            0.25 if (push_age is not None and push_age <= 30) else 0.0,
        ])
        adoption = 0.7 * _log_norm(stars, 4000) + 0.3 * _log_norm(ex.get("forks", 0), 600)
        relevance = _llm_quality(s)
        rel = relevance if relevance is not None else 0.5
        # paper-linked repos (code for a paper) are a strong quality signal
        blob = f"{ex.get('homepage','')} {s.summary or ''} {' '.join(ex.get('topics', []))}".lower()
        paper_link = 1.0 if ("arxiv.org" in blob or "paper" in blob) else 0.0

        potential = (0.34 * rel + 0.30 * momentum + 0.18 * maturity
                     + 0.12 * adoption + 0.06 * paper_link)
        s.review_score = round(min(1.0, potential), 3)
        s.review_scores = {"momentum": round(momentum, 3), "maturity": round(maturity, 3),
                           "relevance": round(rel, 3), "adoption": round(adoption, 3)}
        s.review_decision = _tier(s.review_score)
        top = max([("momentum", momentum), ("maturity", maturity),
                   ("relevance", rel), ("adoption", adoption)], key=lambda p: p[1])
        s.review_reason = f"driven by {top[0]} ({top[1]:.2f})"
    return len(repos)


# --- blogs: curated reputable feeds, so judge substance over popularity ------

_BLOG_AUTHORITY = {
    "openai.com": 1.0, "deepmind.google": 1.0, "blog.research.google": 0.95,
    "research.google": 0.95, "ai.meta.com": 0.95, "bair.berkeley.edu": 0.9,
    "huggingface.co": 0.85, "anthropic.com": 1.0,
}


def _domain(url: str | None) -> str:
    if not url:
        return ""
    from urllib.parse import urlparse
    return (urlparse(url).netloc or "").lower().removeprefix("www.")


def review_blogs(signals: list[Signal], today=None) -> int:
    """Score each blog post's potential. Lab blogs are already curated, so weight
    source authority + the LLM's substance read over (scarce) social buzz."""
    import datetime as dt
    today = today or dt.date.today()
    blogs = [s for s in signals if s.type == "blog"]
    for s in blogs:
        ex = s.extra or {}
        authority = _BLOG_AUTHORITY.get(_domain(s.url), 0.6)
        # substance: the LLM's novelty read, reinforced by how much was actually
        # written (full text if we fetched it, else the RSS summary length).
        words = ex.get("word_count") or len((s.summary or "").split())
        length_signal = _log_norm(words, 1500)
        nov = s.novelty if s.novelty is not None else 0.5
        substance = 0.6 * nov + 0.4 * length_signal
        relevance = s.llm_relevance if s.llm_relevance is not None else 0.5
        # freshness: recency + any early social pickup (rare for lab blogs)
        post_age = max(1, (today - s.published_at.date()).days) if s.published_at else 30
        recency = max(0.0, 1.0 - post_age / 30.0)
        velocity = _log_norm((s.popularity or 0) / post_age, 20)
        freshness = max(recency, velocity)

        potential = (0.34 * relevance + 0.30 * substance
                     + 0.22 * authority + 0.14 * freshness)
        s.review_score = round(min(1.0, potential), 3)
        s.review_scores = {"substance": round(substance, 3), "relevance": round(relevance, 3),
                           "authority": round(authority, 3), "freshness": round(freshness, 3)}
        s.review_decision = _tier(s.review_score)
        top = max([("substance", substance), ("relevance", relevance),
                   ("authority", authority), ("freshness", freshness)], key=lambda p: p[1])
        s.review_reason = f"driven by {top[0]} ({top[1]:.2f})"
    return len(blogs)
