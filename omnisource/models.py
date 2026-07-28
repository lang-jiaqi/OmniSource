"""Unified data model shared across all sources.

A Signal is the one shape every Source must produce. Whatever the upstream
format (arXiv Atom, HF JSON, RSS, ...), a Source normalizes it into a Signal so
the rest of the pipeline — dedup, ranking, rendering — never has to know where
an item came from.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field


@dataclass
class Signal:
    id: str  # canonical id used for dedup (bare arXiv id for papers, e.g. "2606.21638")
    title: str
    url: str
    type: str  # paper | blog | repo | release | benchmark | social
    published_at: dt.datetime
    summary: str
    authors: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)  # which sources surfaced it
    code_url: str | None = None
    popularity: int = 0  # e.g. HF upvotes; 0 when the source has no such signal
    keyword_hits: int = 0  # filled in by ranking, not by sources
    quality_score: float | None = None  # filled in by the quality distill step

    # Filled in by the Analyst (LLM) step or a track's deterministic taxonomy.
    llm_relevance: float | None = None  # semantic relevance to the track, 0..1
    novelty: float | None = None  # how novel vs incremental, 0..1
    topic: str | None = None  # taxonomy leaf path within the track, e.g. "A > B > C"
    why_it_matters: str | None = None
    key_idea: str | None = None
    read_priority: str | None = None  # high | medium | low

    # Filled in by ranking: weighted combination of the component scores.
    final_score: float | None = None

    # Filled in by OpenAlex enrichment (selected papers only). Feeds quality
    # signals, watchlist matching, and the (future) author graph.
    citation_count: int | None = None
    affiliations: list[str] = field(default_factory=list)  # institution names
    author_ids: list[str] = field(default_factory=list)  # OpenAlex author ids
    # Per-author structure for the relationship graph: [{name, id, institutions}].
    author_nodes: list[dict] = field(default_factory=list)

    # Set by the paper-author watchlist step: which author/lab name matched.
    followed: str | None = None

    # Filled in by the distiller review pass (papers only): a six-expert review
    # of the paper. review_scores holds the five mean dimensions (novelty,
    # workload, open_source_completeness, insight_contribution, paper_presentation).
    review_scores: dict | None = None
    review_decision: str | None = None  # keep | human_review | filter (advisory)
    review_reason: str | None = None
    review_score: float | None = None   # age-adjusted aggregate, 0..1

    # Source-specific metadata that doesn't warrant a top-level field, e.g. a
    # repo's created_at / forks / topics / license for the quality scorer.
    extra: dict = field(default_factory=dict)
