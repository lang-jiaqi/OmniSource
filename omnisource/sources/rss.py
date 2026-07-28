"""RSS source: recent posts from AI lab / company blogs.

This is what makes the radar more than a paper feed — it surfaces non-paper
signals (model releases, engineering posts, research announcements). Blogs are
sparse, so it uses a wider window than arXiv by default.
"""
from __future__ import annotations

import datetime as dt
import html
import re

from ..memory.cache import cached_get
from ..models import Signal
from .base import Source

_TAG_RE = re.compile(r"<[^>]+>")
# Some blog hosts block feedparser's default UA, so fetch with a browser-like one.
_HEADERS = {"User-Agent": "Mozilla/5.0 (OmniSource research radar)"}

DEFAULT_FEEDS = [
    "https://huggingface.co/blog/feed.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://blog.research.google/feeds/posts/default",
    "https://openai.com/news/rss.xml",
]


def _clean(text: str | None) -> str:
    return html.unescape(_TAG_RE.sub("", text or "")).strip()


def _entry_dt(entry) -> dt.datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return dt.datetime(*parsed[:6], tzinfo=dt.timezone.utc)


class RSSSource(Source):
    name = "rss"

    def fetch(self, track: dict) -> list[Signal]:
        try:
            import feedparser
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install feedparser to use the rss source") from exc

        feeds = track.get("rss_feeds", DEFAULT_FEEDS)
        days = track.get("rss_days", track.get("days", 3))
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)

        signals: list[Signal] = []
        for url in feeds:
            try:
                parsed = feedparser.parse(cached_get(url, headers=_HEADERS))
            except Exception as exc:  # one bad feed shouldn't lose the others
                print(f"    ! rss feed failed: {url} ({exc})")
                continue
            for entry in parsed.entries:
                published = _entry_dt(entry)
                if published and published < cutoff:
                    continue
                link = entry.get("link")
                if not link:
                    continue
                signals.append(
                    Signal(
                        id=link,  # the post URL is its canonical id
                        title=_clean(entry.get("title")),
                        url=link,
                        type="blog",
                        published_at=published,
                        summary=_clean(entry.get("summary"))[:2000],
                        authors=[entry["author"]] if entry.get("author") else [],
                        sources=[self.name],
                    )
                )
        return signals
