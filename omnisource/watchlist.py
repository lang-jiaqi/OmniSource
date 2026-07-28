"""Paper-author watchlist: surface papers from named authors, regardless of ranking.

This is the personalization layer. The daily briefing is a generic top-N; this
watchlist guarantees that anything from named paper authors shows up — even if
it didn't make the curated cut. Matched against the full fetched pool (in the
track's categories), so author-watchlist matches override the relevance/quality
filter.

Matching is by author name (fuzzy, to tolerate "Yann LeCun" vs "Y. LeCun").
Name collisions are possible for common names; OpenAlex author-id matching
(precise) is a later refinement.
"""
from __future__ import annotations

import datetime as dt
import re

from rapidfuzz import fuzz

from .models import Signal

_NON_ALNUM = re.compile(r"[^a-z0-9 ]+")
NAME_THRESHOLD = 90


def _norm(name: str) -> str:
    return _NON_ALNUM.sub("", name.lower()).strip()


def match_watchlist(signals: list[Signal], track: dict) -> list[Signal]:
    """Return paper signals authored by someone on the track's watchlist."""
    cfg = track.get("watchlist") or {}
    follows = cfg.get("authors", [])
    if not follows:
        return []
    norm_follows = [(name, _norm(name)) for name in follows]

    matched: list[Signal] = []
    for s in signals:
        if s.type != "paper":
            continue
        for author in s.authors:
            na = _norm(author)
            hit = next((orig for orig, nf in norm_follows if fuzz.ratio(na, nf) >= NAME_THRESHOLD), None)
            if hit:
                s.followed = hit
                matched.append(s)
                break

    matched.sort(key=lambda s: s.published_at or dt.datetime.min.replace(tzinfo=dt.timezone.utc), reverse=True)
    return matched[: int(cfg.get("top", 10))]
