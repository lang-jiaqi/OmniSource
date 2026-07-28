"""Quality distill stage for the daily Signal pipeline.

The analyst is the expensive semantic judge. This stage is a cheap deterministic
shortlist pass: score basic evidence of quality, drop obvious weak candidates,
and keep a bounded per-section buffer for the analyst.
"""
from __future__ import annotations

import math

from ..models import Signal

QUOTA_KEYS = {
    "paper": "top_papers",
    "repo": "top_repos",
    "blog": "top_blogs",
    "social": "top_social",
}

DEFAULT_MIN_SCORE = 0.18
DEFAULT_BUFFER = 8


def distill_quality(signals: list[Signal], track: dict) -> list[Signal]:
    """Score and shortlist ranked signals before the LLM analyst step."""
    raw_cfg = track.get("quality_distill")
    if raw_cfg is False:
        for signal in signals:
            signal.quality_score = score_quality(signal, track)
        return signals
    cfg = raw_cfg if isinstance(raw_cfg, dict) else {}
    if cfg.get("enabled", True) is False:
        for signal in signals:
            signal.quality_score = score_quality(signal, track)
        return signals

    min_score = float(cfg.get("min_score", DEFAULT_MIN_SCORE))
    buffer = int(cfg.get("buffer", DEFAULT_BUFFER))
    output = track.get("output", {})

    indexed = []
    scored: list[tuple[int, Signal]] = []
    for index, signal in enumerate(signals):
        signal.quality_score = score_quality(signal, track)
        scored.append((index, signal))
        if signal.quality_score >= min_score:
            indexed.append((index, signal))

    keep_ids: set[int] = set()
    grouped: dict[str, list[tuple[int, Signal]]] = {}
    for item in indexed:
        grouped.setdefault(item[1].type, []).append(item)

    fill_quota_types = set(cfg.get("fill_quota_types", []))
    scored_by_type: dict[str, list[tuple[int, Signal]]] = {}
    for item in scored:
        scored_by_type.setdefault(item[1].type, []).append(item)

    for typ, items in grouped.items():
        quota = int(output.get(QUOTA_KEYS.get(typ, ""), 0) or 0)
        limit = quota + buffer if quota > 0 else len(items)
        selected = sorted(
            items,
            key=lambda item: (
                item[1].quality_score or 0.0,
                item[1].keyword_hits,
                item[1].popularity,
                -item[0],
            ),
            reverse=True,
        )[:limit]
        keep_ids.update(id(signal) for _index, signal in selected)

    for typ in fill_quota_types:
        quota = int(output.get(QUOTA_KEYS.get(typ, ""), 0) or 0)
        if quota <= 0:
            continue
        limit = quota + buffer
        current = [item for item in scored_by_type.get(typ, []) if id(item[1]) in keep_ids]
        if len(current) >= limit:
            continue
        selected_ids = {id(signal) for _index, signal in current}
        fill = sorted(
            [item for item in scored_by_type.get(typ, []) if id(item[1]) not in selected_ids],
            key=lambda item: (
                item[1].quality_score or 0.0,
                item[1].keyword_hits,
                item[1].popularity,
                -item[0],
            ),
            reverse=True,
        )[: limit - len(current)]
        keep_ids.update(id(signal) for _index, signal in fill)

    return [signal for _index, signal in scored if id(signal) in keep_ids]


def score_quality(signal: Signal, track: dict) -> float:
    """Return a cheap 0..1 quality estimate using only normalized Signal fields."""
    keyword_score = _keyword_score(signal, track)
    content_score = _content_score(signal)
    source_score = min(1.0, len(set(signal.sources)) / 2.0)
    popularity_score = _popularity_score(signal.popularity)
    code_score = 1.0 if signal.code_url else 0.0

    return min(
        1.0,
        0.38 * keyword_score
        + 0.22 * content_score
        + 0.16 * source_score
        + 0.14 * popularity_score
        + 0.10 * code_score,
    )


def _keyword_score(signal: Signal, track: dict) -> float:
    keywords = track.get("keywords", [])
    if not keywords:
        return 0.0
    target = min(3, max(1, len(keywords)))
    return min(1.0, signal.keyword_hits / target)


def _content_score(signal: Signal) -> float:
    title_score = 1.0 if signal.title.strip() else 0.0
    summary_words = len(signal.summary.split())
    summary_score = min(1.0, summary_words / 40.0)
    return 0.4 * title_score + 0.6 * summary_score


def _popularity_score(popularity: int) -> float:
    if popularity <= 0:
        return 0.0
    return min(1.0, math.log1p(popularity) / math.log1p(1000))
