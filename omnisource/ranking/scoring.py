"""Weighted final score from a track's ranking weights.

Each item carries component signals from different stages:
- relevance: LLM judgment of fit to the track (0..1)
- novelty:   LLM judgment of how new the idea is (0..1)
- popularity: source signal (HF upvotes / GitHub stars), normalized within the group
- code_available: 1 if there's a code link, else 0

The track decides how much each matters via `ranking:` weights.
"""
from __future__ import annotations

from ..models import Signal
from ..personalization import adjusted_score

DEFAULT_WEIGHTS = {
    "relevance": 0.4,
    "novelty": 0.3,
    "popularity": 0.2,
    "code_available": 0.1,
}


def score_final(signals: list[Signal], weights: dict | None = None) -> None:
    """Set final_score on each signal. Popularity is normalized within this
    group, so upvotes and stars are compared on the same 0..1 scale per section."""
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    max_pop = max((s.popularity for s in signals), default=0) or 1
    for s in signals:
        base = (
            w["relevance"] * (s.llm_relevance or 0.0)
            + w["novelty"] * (s.novelty or 0.0)
            + w["popularity"] * (s.popularity / max_pop)
            + w["code_available"] * (1.0 if s.code_url else 0.0)
        )
        s.final_score = adjusted_score(base, s)
