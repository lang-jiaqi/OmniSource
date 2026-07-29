"""Curator agent: turn collected signals into the ranked, sectioned shortlist.

Keyword-filters and ranks, builds the Analyst, then selects the top signals per
type (so papers don't crowd out repos and blogs), scoring each via the track's
ranking weights.
"""
from __future__ import annotations

import os

from ..llm import get_provider
from ..models import Signal
from ..ranking import score_final
from ..tool_scoring import score_tool
from .analyst import Analyst
from .relevance import allows_keyword_fallback, annotate_track_relevance, track_relevance_bonus

# Signal type -> track output quota key. Section headings are localized (i18n).
SECTIONS: list[tuple[str, str]] = [
    ("paper", "top_papers"),
    ("repo", "top_repos"),
    ("blog", "top_blogs"),
    ("social", "top_social"),
]


def rank(signals: list[Signal], track: dict) -> list[Signal]:
    """Keyword filter, then sort. Primary key is keyword relevance; ties broken
    by community popularity, then cross-source corroboration, then recency."""
    keywords = track.get("keywords", [])
    negatives = track.get("negative_keywords", [])
    kept: list[Signal] = []
    for s in signals:
        text = f"{s.title} {s.summary}".lower()
        if any(neg.lower() in text for neg in negatives):
            continue
        s.keyword_hits = sum(1 for kw in keywords if kw.lower() in text)
        # GitHub repos are already pre-filtered by the source's github_query, so
        # don't drop them just because the short description misses a keyword.
        # Tracks can also allow curated feeds (for example infra blogs) through
        # as fallback candidates; the analyst/reviewer will judge relevance.
        if s.keyword_hits == 0 and "github" not in s.sources and not allows_keyword_fallback(s, track):
            continue
        if not annotate_track_relevance(s, track):
            continue
        kept.append(s)
    kept.sort(
        key=lambda s: (
            track_relevance_bonus(s),
            s.keyword_hits,
            s.popularity,
            len(s.sources),
            s.published_at,
        ),
        reverse=True,
    )
    if track.get("tool_radar"):
        _apply_tool_scores(kept)
        kept.sort(key=lambda s: s.final_score or 0.0, reverse=True)
    return kept


def make_analyst(track: dict, enabled: bool) -> Analyst | None:
    """Build the Analyst once, or None if the LLM is unavailable/disabled."""
    llm_cfg = track.get("llm", {})
    provider_name = os.environ.get("OMNISOURCE_LLM_PROVIDER") or llm_cfg.get("provider")
    model = os.environ.get("OMNISOURCE_LLM_MODEL") or llm_cfg.get("model")
    if not enabled or not provider_name:
        return None
    try:
        provider = get_provider(provider_name, model)
    except Exception as exc:
        if os.environ.get("OMNISOURCE_REQUIRE_LLM") == "1":
            raise RuntimeError(f"LLM is required but unavailable: {exc}") from exc
        print(f"  ! LLM disabled ({exc}); keeping keyword ranking")
        return None
    print(f"  LLM: {provider_name}/{provider.model}")
    return Analyst(provider)


def _apply_tool_scores(signals: list[Signal]) -> None:
    """Attach the shared six-dimension tool evaluation to each candidate."""
    for signal in signals:
        category, evaluation, aggregate = score_tool(signal)
        extra = signal.extra if isinstance(signal.extra, dict) else {}
        extra["tool_category"] = category
        extra["tool_evaluation"] = evaluation
        extra["tool_score"] = aggregate
        signal.extra = extra
        signal.final_score = aggregate / 5.0


def enrich_and_rank(signals: list[Signal], track: dict, analyst: Analyst | None) -> list[Signal]:
    """Run the Analyst over candidates, compute the weighted final score, and
    sort by it. Without an analyst, fall back to keyword/popularity order."""
    if analyst is None:
        if track.get("tool_radar"):
            _apply_tool_scores(signals)
            signals.sort(key=lambda s: s.final_score or 0.0, reverse=True)
            return signals
        signals.sort(key=lambda s: (s.keyword_hits, s.popularity), reverse=True)
        return signals
    for s in signals:
        analyst.analyze(s, track)
    successes = getattr(analyst, "successes", None)
    failures = getattr(analyst, "failures", None)
    if successes == 0 and failures:
        message = "LLM analysis failed for every shortlisted item; refusing to publish fallback-only results"
        if os.environ.get("OMNISOURCE_REQUIRE_LLM") == "1":
            raise RuntimeError(message)
        print(f"  ! {message}")
    if track.get("tool_radar"):
        _apply_tool_scores(signals)
    else:
        score_final(signals, track.get("ranking"))
    signals.sort(key=lambda s: s.final_score or 0.0, reverse=True)
    return signals


def select_sections_with_candidates(
    ranked: list[Signal],
    track: dict,
    analyst: Analyst | None,
) -> tuple[dict[str, list[Signal]], dict[str, list[Signal]]]:
    """Select report items and retain the analyzed buffer for web personalization."""
    out = track.get("output", {})
    analysis_buffer = max(0, int(out.get("analysis_buffer", 5) or 0))
    sections: dict[str, list[Signal]] = {}
    candidates: dict[str, list[Signal]] = {}
    for typ, quota_key in SECTIONS:
        quota = out.get(quota_key, 0)
        if quota <= 0:
            continue
        items = [s for s in ranked if s.type == typ][: quota + analysis_buffer]
        enrich_and_rank(items, track, analyst)
        candidates[typ] = items
        sections[typ] = items[:quota]
    return sections, candidates


def select_sections(ranked: list[Signal], track: dict, analyst: Analyst | None) -> dict[str, list[Signal]]:
    """Pick the top signals per type so papers don't crowd out repos and blogs."""
    sections, _candidates = select_sections_with_candidates(ranked, track, analyst)
    return sections


def merge_candidate_sections(
    sections: dict[str, list[Signal]],
    candidates: dict[str, list[Signal]],
) -> dict[str, list[Signal]]:
    """Keep final report order first, followed by unselected personalization candidates."""
    merged: dict[str, list[Signal]] = {}
    for typ, items in candidates.items():
        selected = sections.get(typ, [])
        selected_ids = {signal.id for signal in selected}
        merged[typ] = [*selected, *(signal for signal in items if signal.id not in selected_ids)]
    return merged
