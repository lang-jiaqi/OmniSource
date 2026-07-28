"""BlogrXiv's curated AI research writing index.

BlogrXiv serves its published catalogue from a public Supabase table rather
than an RSS feed. The public frontend configuration is discovered from the
site's own data script, so OmniSource does not need to copy or store a key.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from zoneinfo import ZoneInfo

from ..memory.cache import cached_get
from ..models import Signal
from .base import Source

DATA_SCRIPT_URL = "https://openenvision.github.io/BlogrXiv/site/assets/js/blog-data.js?v=2"
_CONFIG_RE = re.compile(r"\b(?P<name>url|publishableKey):\s*'(?P<value>[^']+)'", re.I)
_TAG_RE = re.compile(r"<[^>]+>")
_HEADERS = {"User-Agent": "OmniSource research radar"}
_REPORT_TZ = ZoneInfo("Asia/Shanghai")


def _clean(text: object) -> str:
    return html.unescape(_TAG_RE.sub(" ", str(text or ""))).strip()


def _public_config(script: str) -> tuple[str, str]:
    values = {match.group("name"): match.group("value") for match in _CONFIG_RE.finditer(script)}
    base_url = values.get("url", "").rstrip("/")
    publishable_key = values.get("publishableKey", "")
    if not base_url or not publishable_key:
        raise ValueError("BlogrXiv public data configuration is incomplete")
    return base_url, publishable_key


def _published_at(value: object) -> dt.datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


class BlogrXivSource(Source):
    name = "blogrxiv"

    def __init__(self, now: dt.datetime | None = None) -> None:
        self._now = now

    def fetch(self, track: dict) -> list[Signal]:
        cfg = track.get("blogrxiv") or {}
        if not isinstance(cfg, dict) or cfg.get("enabled", True) is False:
            return []

        days = max(1, int(cfg.get("days", track.get("blogrxiv_days", track.get("days", 3))) or 3))
        calendar_days = bool(cfg.get("calendar_days", track.get("blogrxiv_calendar_days", False)))
        limit = max(1, int(cfg.get("max_entries", 200) or 200))
        now = self._now or dt.datetime.now(dt.timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=dt.timezone.utc)
        now = now.astimezone(dt.timezone.utc)
        cutoff = now - dt.timedelta(days=days)
        local_now = now.astimezone(_REPORT_TZ)
        first_local_date = local_now.date() - dt.timedelta(days=days - 1)

        script_url = str(cfg.get("data_script_url") or DATA_SCRIPT_URL)
        script = cached_get(script_url, headers=_HEADERS)
        base_url, publishable_key = _public_config(script)
        rows = json.loads(cached_get(
            f"{base_url}/rest/v1/blogs",
            params={
                "select": "id,title,excerpt,author,category,tags,read_time,publish_date,source_name,url,status",
                "status": "eq.published",
                "order": "publish_date.desc,id.asc",
                "limit": str(limit),
            },
            headers={
                **_HEADERS,
                "apikey": publishable_key,
                "Authorization": f"Bearer {publishable_key}",
            },
        ))
        if not isinstance(rows, list):
            raise ValueError("BlogrXiv returned an invalid blog list")

        signals: list[Signal] = []
        for row in rows:
            if not isinstance(row, dict) or row.get("status") not in (None, "published"):
                continue
            published = _published_at(row.get("publish_date"))
            url = str(row.get("url") or "").strip()
            title = _clean(row.get("title"))
            if not published or not url or not title:
                continue
            if calendar_days:
                published_local_date = published.astimezone(_REPORT_TZ).date()
                if not (first_local_date <= published_local_date <= local_now.date()):
                    continue
            elif published < cutoff:
                continue
            category = _clean(row.get("category"))
            tags = [str(tag).strip() for tag in (row.get("tags") or []) if str(tag).strip()]
            context = []
            if category:
                context.append(f"Category: {category}")
            if tags:
                context.append("Tags: " + ", ".join(tags))
            excerpt = _clean(row.get("excerpt"))
            summary = "\n".join(part for part in (excerpt, " · ".join(context)) if part).strip()
            author = _clean(row.get("author"))
            signals.append(Signal(
                id=url,
                title=title,
                url=url,
                type="blog",
                published_at=published,
                summary=summary[:3000],
                authors=[author] if author else [],
                sources=[self.name],
                extra={
                    "blogrxiv_id": row.get("id"),
                    "blogrxiv_category": category,
                    "blogrxiv_tags": tags,
                    "blogrxiv_source_name": _clean(row.get("source_name")),
                    "read_time": _clean(row.get("read_time")),
                },
            ))
        return signals
