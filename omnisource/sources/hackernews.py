"""Hacker News source — community discussion as buzz signal.

Uses the free Algolia HN Search API (no key). Each story's external link is kept
in the signal so canonicalization folds an HN post that links an arXiv paper /
GitHub repo onto that artifact as buzz, rather than a standalone social item.
"""
from __future__ import annotations

import datetime as dt
import json
import re

from ..memory.cache import cached_get
from ..models import Signal
from .base import Source

API = "https://hn.algolia.com/api/v1/search"
_OR_RE = re.compile(r"\s+OR\s+", re.I)


def _compact_query(value: str, limit: int = 8) -> str:
    terms: list[str] = []
    for term in _OR_RE.split(str(value)):
        cleaned = term.strip().strip('"').strip("'")
        if cleaned and cleaned not in terms:
            terms.append(cleaned)
        if len(terms) >= limit:
            break
    return " OR ".join(terms)


class HackerNewsSource(Source):
    name = "hackernews"

    def fetch(self, track: dict) -> list[Signal]:
        days = track.get("days", 3)
        query = _compact_query(track.get("hn_query") or " OR ".join(track.get("keywords", [])[:8]))
        cutoff = int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).timestamp())

        body = cached_get(API, params={
            "query": query,
            "tags": "story",
            "numericFilters": f"created_at_i>{cutoff}",
            "hitsPerPage": track.get("hn_top", 50),
        })

        signals: list[Signal] = []
        for h in json.loads(body).get("hits", []):
            external = h.get("url")
            item_url = f"https://news.ycombinator.com/item?id={h['objectID']}"
            created = h.get("created_at_i")
            signals.append(
                Signal(
                    id=external or item_url,  # canonicalize remaps to the linked artifact
                    title=h.get("title", ""),
                    url=item_url,
                    type="social",
                    published_at=dt.datetime.fromtimestamp(created, dt.timezone.utc) if created else None,
                    summary=f"{h.get('title', '')} {external or ''}".strip(),
                    authors=[h["author"]] if h.get("author") else [],
                    sources=[self.name],
                    popularity=int(h.get("points") or 0),
                )
            )
        return signals
