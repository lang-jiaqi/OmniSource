"""Collector agent: fetch from every source the track lists, then dedup.

The first stage of the pipeline. Its only job is to gather candidate signals
and collapse duplicates — across sources (by canonical id) and near-duplicates
(same/fuzzy title) — no filtering or scoring.
"""
from __future__ import annotations

from ..canonical import canonicalize
from ..dedup import merge_by_id, merge_near_duplicates
from ..models import Signal
from ..sources import SOURCE_REGISTRY


class Collector:
    def collect(self, track: dict) -> list[Signal]:
        raw = self._fetch(track)
        for s in raw:
            canonicalize(s)  # L2: remap blogs/social onto the artifact they link
        merged = merge_by_id(raw)  # L1: exact id
        deduped = merge_near_duplicates(merged)  # L3: title/fuzzy near-dups
        print(f"Merged {len(raw)} -> {len(merged)} by id -> {len(deduped)} after near-dup")
        return deduped

    def _fetch(self, track: dict) -> list[Signal]:
        """Fetch from every listed source, isolating per-source failures."""
        signals: list[Signal] = []
        for name in track.get("sources", ["arxiv"]):
            source_cls = SOURCE_REGISTRY.get(name)
            if source_cls is None:
                print(f"  ! unknown source '{name}', skipping")
                continue
            try:
                items = source_cls().fetch(track)
                print(f"  {name}: {len(items)} signals")
                signals += items
            except Exception as exc:  # one bad source shouldn't sink the report
                print(f"  ! {name} failed: {exc}")
        return signals
