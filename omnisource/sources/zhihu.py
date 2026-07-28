"""Zhihu source backed by OpenCLI and the user's logged-in Chrome."""
from __future__ import annotations

import datetime as dt
import html
import re
from zoneinfo import ZoneInfo

from ..models import Signal
from .base import Source
from .zhihu_client import OpenCLIZhihuClient, OpenCLIZhihuConfig, OpenCLIZhihuError


_ARTICLE_RE = re.compile(r"zhuanlan\.zhihu\.com/p/(\d+)")
_ANSWER_RE = re.compile(r"/question/(\d+)/answer/(\d+)")


class ZhihuSource(Source):
    name = "zhihu"

    def __init__(self, client=None, now=None) -> None:
        self._client = client
        self._now = now

    def fetch(self, track: dict) -> list[Signal]:
        cfg = track.get("zhihu") or {}
        if not isinstance(cfg, dict) or cfg.get("enabled", True) is False:
            return []
        days = max(1, int(cfg.get("days", track.get("days", 7)) or 7))
        timezone = ZoneInfo(str(cfg.get("timezone") or "Asia/Shanghai"))
        now = self._now or dt.datetime.now(timezone)
        now = now.replace(tzinfo=timezone) if now.tzinfo is None else now.astimezone(timezone)
        cutoff = dt.datetime.combine(now.date() - dt.timedelta(days=days - 1), dt.time.min, tzinfo=timezone)
        creator_limit = max(1, int(cfg.get("max_items_per_creator", 20) or 20))
        summary_max_chars = max(100, int(cfg.get("summary_max_chars", 500) or 500))
        client = self._client or OpenCLIZhihuClient(OpenCLIZhihuConfig(
            command=str(cfg.get("command") or "opencli"),
            timeout_seconds=float(cfg.get("timeout_seconds", 120) or 120),
        ))

        candidates: list[dict] = []
        for creator in cfg.get("creators") or []:
            user = str(creator.get("user") or creator.get("profile_url") or "").strip()
            if not user:
                continue
            if creator.get("articles", True):
                try:
                    candidates.extend(client.user_articles(user, creator_limit))
                except OpenCLIZhihuError as exc:
                    print(f"    ! zhihu creator articles failed: {user} ({exc})")
            if creator.get("answers", True):
                try:
                    candidates.extend(client.user_answers(user, creator_limit))
                except OpenCLIZhihuError as exc:
                    print(f"    ! zhihu creator answers failed: {user} ({exc})")

        signals: list[Signal] = []
        seen: set[str] = set()
        for row in candidates:
            url = str(row.get("url") or "").strip()
            identity = _identity(url)
            if not identity or identity in seen:
                continue
            listed_at = _datetime(row.get("created") or row.get("created_at"), timezone)
            if listed_at is not None and listed_at < cutoff:
                continue  # cheap creator-list prefilter before opening detail
            detail = {}
            # The creator article list already contains an excerpt and exact
            # creation time. Avoid downloading the full article unless either
            # field is missing. Answers still need answer-detail for a summary.
            needs_detail = not identity.startswith("article:") or not row.get("excerpt") or listed_at is None
            if needs_detail:
                try:
                    detail = client.article_detail(url) if identity.startswith("article:") else client.answer_detail(url)
                except OpenCLIZhihuError as exc:
                    if identity.startswith("article:") and listed_at is not None:
                        print(f"    ! zhihu detail failed: {url} ({exc}); using creator-list metadata")
                        detail = {}
                    else:
                        print(f"    ! zhihu detail failed: {url} ({exc})")
                        continue
            published = (
                _datetime(detail.get("created_at") or detail.get("publish_time"), timezone)
                or listed_at
            )
            if published is None or published < cutoff:
                continue
            signals.append(_signal(row, detail, identity, published, summary_max_chars))
            seen.add(identity)
        return signals


def _identity(url: str) -> str:
    article = _ARTICLE_RE.search(url)
    if article:
        return f"article:{article.group(1)}"
    answer = _ANSWER_RE.search(url)
    if answer:
        return f"answer:{answer.group(2)}"
    return ""


def _datetime(value, timezone: ZoneInfo) -> dt.datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip().isdigit()):
        stamp = float(value)
        if stamp > 10_000_000_000:
            stamp /= 1000
        return dt.datetime.fromtimestamp(stamp, dt.timezone.utc).astimezone(timezone)
    text = str(value).strip()
    match = re.search(r"(20\d{2})[-年/](\d{1,2})[-月/](\d{1,2})(?:日)?(?:\s+(\d{1,2}):(\d{2}))?", text)
    if not match:
        return None
    year, month, day, hour, minute = match.groups()
    return dt.datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0), tzinfo=timezone)


def _signal(row: dict, detail: dict, identity: str, published: dt.datetime, summary_max_chars: int) -> Signal:
    article = identity.startswith("article:")
    title = str(detail.get("question_title") or detail.get("title") or row.get("title") or row.get("question") or "知乎内容").strip()
    content = str(row.get("excerpt") or detail.get("content") or "").strip()
    content = _summary(content, summary_max_chars)
    author = str(detail.get("author") or row.get("author") or "").strip()
    votes = _int(detail.get("votes", row.get("votes")))
    comments = _int(detail.get("comments", row.get("comments")))
    url = str(detail.get("url") or row.get("url") or "").strip()
    return Signal(
        id=f"zhihu:{identity}", title=title, url=url,
        type="blog" if article else "social", published_at=published,
        summary=content, authors=[author] if author and author != "-" else [],
        sources=["zhihu"], popularity=votes,
        extra={"platform": "zhihu", "content_type": "article" if article else "answer", "votes": votes, "comments": comments},
    )


def _int(value) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _summary(value: str, max_chars: int = 500) -> str:
    """Return a compact plain-text lead instead of publishing Zhihu full text."""
    text = html.unescape(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!?\[[^]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"[`#>*_|~-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    lead = text[:max_chars]
    boundary = max(lead.rfind(mark) for mark in ("。", "！", "？", ".", "!", "?"))
    if boundary >= max_chars // 2:
        lead = lead[:boundary + 1]
    return lead.rstrip() + "…"
