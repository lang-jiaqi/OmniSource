"""Merging duplicate signals.

Two layers:
- merge_by_id: exact merge on the (canonicalized) id — L1.
- merge_near_duplicates: lexical near-duplicate merge for items that escaped the
  id merge — same normalized title, or a fuzzy title match backed by author
  overlap — L3. High-precision: a fuzzy title alone never merges; it must also
  share an author (or be an almost-exact title), so distinct same-topic papers
  are not falsely collapsed.

The fold keeps the highest-priority artifact type (paper/repo over blog/social),
so a blog/tweet variant folds into the real paper as buzz.
"""
from __future__ import annotations

import re

from rapidfuzz import fuzz

from .models import Signal
from .source_evidence import append_fold_evidence

TYPE_PRIORITY = {"paper": 3, "repo": 2, "benchmark": 2, "release": 2, "blog": 1, "social": 0}

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalized_title(title: str) -> str:
    return _NON_ALNUM.sub(" ", title.lower()).strip()


def _author_key(name: str) -> str:
    return _NON_ALNUM.sub("", name.lower())


def author_overlap(a: Signal, b: Signal) -> bool:
    ka = {_author_key(x) for x in a.authors if x}
    kb = {_author_key(x) for x in b.authors if x}
    return bool(ka & kb)


def fold(base: Signal, other: Signal) -> None:
    """Merge `other` into `base` (sources, popularity, code, authors)."""
    append_fold_evidence(base, other)
    for src in other.sources:
        if src not in base.sources:
            base.sources.append(src)
    base.popularity = max(base.popularity, other.popularity)
    base.code_url = base.code_url or other.code_url
    if not base.authors:
        base.authors = other.authors


def merge_by_id(signals: list[Signal]) -> list[Signal]:
    """L1: collapse signals sharing an id; the highest-priority type is the base."""
    groups: dict[str, list[Signal]] = {}
    for s in signals:
        groups.setdefault(s.id, []).append(s)
    merged: list[Signal] = []
    for group in groups.values():
        base = max(group, key=lambda s: TYPE_PRIORITY.get(s.type, 0))
        for s in group:
            if s is not base:
                fold(base, s)
        merged.append(base)
    return merged


def merge_near_duplicates(signals: list[Signal], threshold: int = 90) -> list[Signal]:
    """L3: merge same-work items that escaped the id merge. Exact normalized
    title always merges; a fuzzy title merges only with author overlap (or an
    almost-exact title), keeping precision high."""
    result: list[Signal] = []
    by_norm: dict[str, int] = {}
    for s in signals:
        nt = normalized_title(s.title)
        if nt and nt in by_norm:
            fold(result[by_norm[nt]], s)
            continue
        matched = None
        if s.type == "paper" and nt:
            for idx, base in enumerate(result):
                if base.type != "paper":
                    continue
                ratio = fuzz.token_set_ratio(nt, normalized_title(base.title))
                if ratio >= threshold and (author_overlap(s, base) or ratio >= 97):
                    matched = idx
                    break
        if matched is not None:
            fold(result[matched], s)
        else:
            if nt:
                by_norm[nt] = len(result)
            result.append(s)
    return result
