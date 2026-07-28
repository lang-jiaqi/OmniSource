"""Candidate canonicalization and deduplication."""
from __future__ import annotations

from difflib import SequenceMatcher

from .models import PaperCandidate, canonical_arxiv_id, normalized_title


def canonical_key(candidate: PaperCandidate) -> str:
    return candidate.canonical_id


def dedup_candidates(candidates: list[PaperCandidate]) -> list[PaperCandidate]:
    by_key: dict[str, PaperCandidate] = {}
    for candidate in candidates:
        key = canonical_key(candidate)
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = candidate
            continue
        _merge_into(existing, candidate)

    merged = list(by_key.values())
    # Conservative fuzzy title pass for records lacking DOI/arXiv IDs.
    out: list[PaperCandidate] = []
    for candidate in merged:
        match = next((item for item in out if _same_title_record(item, candidate)), None)
        if match is None:
            out.append(candidate)
        else:
            _merge_into(match, candidate)
    return out


def _same_title_record(a: PaperCandidate, b: PaperCandidate) -> bool:
    a_arxiv = canonical_arxiv_id(a.arxiv_id)
    b_arxiv = canonical_arxiv_id(b.arxiv_id)
    if a_arxiv and b_arxiv and a_arxiv != b_arxiv:
        return False
    if a.doi and b.doi and a.doi.lower().strip() != b.doi.lower().strip():
        return False
    if abs(a.year - b.year) > 1:
        return False
    ratio = SequenceMatcher(None, normalized_title(a.title), normalized_title(b.title)).ratio()
    author_overlap = bool(set(a.authors[:3]) & set(b.authors[:3]))
    return ratio >= 0.94 and author_overlap


def _merge_into(existing: PaperCandidate, incoming: PaperCandidate) -> None:
    existing.abstract = max([existing.abstract, incoming.abstract], key=len)
    existing.authors = existing.authors or incoming.authors
    existing.published_at = min(existing.published_at, incoming.published_at)
    existing.primary_leaf = existing.primary_leaf or incoming.primary_leaf
    existing.secondary_leaves = sorted(set(existing.secondary_leaves) | set(incoming.secondary_leaves))
    existing.arxiv_id = canonical_arxiv_id(existing.arxiv_id) or canonical_arxiv_id(incoming.arxiv_id)
    existing.doi = existing.doi or incoming.doi
    existing.venue = existing.venue or incoming.venue
    existing.url = existing.url or incoming.url
    existing.pdf_url = existing.pdf_url or incoming.pdf_url
    existing.github_url = existing.github_url or incoming.github_url
    existing.source_tags = sorted(set(existing.source_tags) | set(incoming.source_tags))
    existing.full_text = max([existing.full_text or "", incoming.full_text or ""], key=len) or None
    existing.citation_count = max(existing.citation_count or 0, incoming.citation_count or 0) or None
    existing.influential_citation_count = max(existing.influential_citation_count or 0, incoming.influential_citation_count or 0) or None
    existing.field_year_normalized_citation = max(existing.field_year_normalized_citation or 0.0, incoming.field_year_normalized_citation or 0.0) or None
    existing.hf_upvotes = max(existing.hf_upvotes or 0, incoming.hf_upvotes or 0) or None
    existing.normalized_hf_upvote = max(existing.normalized_hf_upvote or 0.0, incoming.normalized_hf_upvote or 0.0) or None
    existing.github_stars = max(existing.github_stars or 0, incoming.github_stars or 0) or None
    existing.normalized_github_star = max(existing.normalized_github_star or 0.0, incoming.normalized_github_star or 0.0) or None
