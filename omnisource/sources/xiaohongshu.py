"""Xiaohongshu source backed by OpenCLI and the user's logged-in Chrome.

The source monitors explicitly configured creators. It never searches arbitrary
users, posts comments, or persists browser credentials. Xiaohongshu currently
requires the per-note ``xsec_token`` share URL for direct links, so that URL is
kept as the Signal link; browser cookies and session credentials are never stored.
"""
from __future__ import annotations

import datetime as dt
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..models import Signal
from .base import Source
from .xiaohongshu_client import OpenCLIConfig, OpenCLIError, OpenCLIXiaohongshuClient


_PROFILE_RE = re.compile(r"/user/profile/([A-Za-z0-9]+)")
_NOTE_RE = re.compile(r"/(?:explore|search_result|note)/([0-9a-f]{24})(?:[/?#]|$)", re.I)
_COUNT_RE = re.compile(r"^([0-9]+(?:\.[0-9]+)?)([wWkK万千]?)")


class XiaohongshuSource(Source):
    name = "xiaohongshu"

    def __init__(self, client=None, now=None) -> None:
        self._client = client
        self._now = now

    def fetch(self, track: dict) -> list[Signal]:
        cfg = track.get("xiaohongshu") or {}
        if not isinstance(cfg, dict) or cfg.get("enabled", True) is False:
            return []
        backend = str(cfg.get("backend") or "opencli").strip().lower()
        if backend != "opencli":
            raise ValueError(f"Unsupported xiaohongshu backend: {backend}")
        creators = cfg.get("creators") or []
        if not isinstance(creators, list) or not creators:
            print("    ! xiaohongshu has no configured creators; skipping")
            return []

        timezone = _timezone(str(cfg.get("timezone") or "Asia/Shanghai"))
        days = max(1, int(cfg.get("days", track.get("days", 1)) or 1))
        limit = max(1, int(cfg.get("max_notes_per_creator", 20) or 20))
        fetch_details = bool(cfg.get("fetch_details", True))
        include_unknown_dates = bool(cfg.get("include_unknown_dates", False))
        now = self._now or dt.datetime.now(timezone)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone)
        else:
            now = now.astimezone(timezone)
        first_date = now.date() - dt.timedelta(days=days - 1)
        cutoff = dt.datetime.combine(first_date, dt.time.min, tzinfo=timezone)

        client = self._client or OpenCLIXiaohongshuClient(OpenCLIConfig(
            command=str(cfg.get("command") or "opencli"),
            timeout_seconds=float(cfg.get("timeout_seconds", 120) or 120),
        ))

        signals: list[Signal] = []
        seen: set[str] = set()
        for creator in creators:
            if not isinstance(creator, dict):
                continue
            creator_name = str(creator.get("name") or "").strip()
            try:
                user_id = _creator_id(creator)
                rows = client.user_notes(user_id, limit=limit)
            except (OpenCLIError, ValueError) as exc:
                label = creator_name or str(creator.get("user_id") or "unknown creator")
                print(f"    ! xiaohongshu creator failed: {label} ({exc})")
                continue

            for row in rows:
                note_id = _note_id(row)
                if not note_id or note_id in seen:
                    continue
                signed_url = str(row.get("url") or "").strip()
                published = _published_at(row, note_id, timezone)
                if published is None and not include_unknown_dates:
                    continue
                if published is not None and published < cutoff:
                    continue

                detail = {}
                if fetch_details and signed_url:
                    try:
                        detail = client.note_detail(signed_url)
                    except OpenCLIError as exc:
                        print(f"    ! xiaohongshu note detail failed: {note_id} ({exc})")

                # Prefer a real timestamp if a future/newer OpenCLI adapter exposes it.
                detail_published = _published_at(detail, note_id, timezone, infer_from_id=False)
                if detail_published is not None:
                    published = detail_published
                    if published < cutoff:
                        continue

                signal = _to_signal(
                    row=row,
                    detail=detail,
                    note_id=note_id,
                    creator_id=user_id,
                    creator_name=creator_name,
                    published_at=published,
                )
                signals.append(signal)
                seen.add(note_id)
        return signals


def _creator_id(creator: dict) -> str:
    direct = str(creator.get("user_id") or "").strip()
    if direct:
        return direct
    profile_url = str(creator.get("profile_url") or "").strip()
    match = _PROFILE_RE.search(profile_url)
    if match:
        return match.group(1)
    raise ValueError("creator requires user_id or a valid Xiaohongshu profile_url")


def _note_id(row: dict) -> str:
    for key in ("id", "note_id", "noteId"):
        value = str(row.get(key) or "").strip()
        if re.fullmatch(r"[0-9a-f]{24}", value, re.I):
            return value.lower()
    match = _NOTE_RE.search(str(row.get("url") or ""))
    return match.group(1).lower() if match else ""


def _published_at(row: dict, note_id: str, timezone: ZoneInfo, *, infer_from_id: bool = True) -> dt.datetime | None:
    for key in ("published_at", "publishedAt", "time", "create_time", "createTime"):
        value = row.get(key)
        parsed = _parse_datetime(value, timezone)
        if parsed is not None:
            return parsed
    return _note_id_datetime(note_id, timezone) if infer_from_id else None


def _parse_datetime(value, timezone: ZoneInfo) -> dt.datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip().isdigit()):
        timestamp = float(value)
        if timestamp > 10_000_000_000:
            timestamp /= 1000.0
        try:
            return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).astimezone(timezone)
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone)
    return parsed.astimezone(timezone)


def _note_id_datetime(note_id: str, timezone: ZoneInfo) -> dt.datetime | None:
    if not re.fullmatch(r"[0-9a-f]{24}", note_id, re.I):
        return None
    timestamp = int(note_id[:8], 16)
    if timestamp < 1_000_000_000 or timestamp > 4_000_000_000:
        return None
    return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).astimezone(timezone)


def _to_signal(*, row: dict, detail: dict, note_id: str, creator_id: str,
               creator_name: str, published_at: dt.datetime | None) -> Signal:
    title = _text(detail.get("title")) or _text(row.get("title"))
    content = (
        _text(detail.get("content"))
        or _text(detail.get("desc"))
        or _text(row.get("content"))
        or _text(row.get("desc"))
    )
    if not title:
        title = content[:60].strip() or f"Xiaohongshu note {note_id}"
    author = (
        _text(detail.get("author"))
        or creator_name
        or _text(row.get("author"))
        or _text(row.get("user"))
        or creator_id
    )
    tags = _tags(detail.get("tags") or row.get("tags"))
    summary = content
    if tags:
        summary = f"{summary}\nTopics: {', '.join(tags)}".strip()

    likes = _count(detail.get("likes", row.get("likes")))
    collects = _count(detail.get("collects", row.get("collects")))
    comments = _count(detail.get("comments", row.get("comments")))
    # Unsigned /explore URLs currently redirect to Xiaohongshu's error page.
    # The per-note share signature is not a browser credential and is required
    # for a report link that users can actually open.
    report_url = _text(row.get("url")) or f"https://www.xiaohongshu.com/explore/{note_id}"
    return Signal(
        id=f"xhs:{note_id}",
        title=title,
        url=report_url,
        type="social",
        published_at=published_at,
        summary=summary,
        authors=[author] if author else [],
        sources=["xiaohongshu"],
        popularity=likes,
        extra={
            "platform": "xiaohongshu",
            "note_id": note_id,
            "creator_id": creator_id,
            "creator_name": author,
            "note_type": _text(detail.get("type") or row.get("type")),
            "likes": likes,
            "collects": collects,
            "comments": comments,
            "tags": tags,
        },
    )


def _text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        for key in ("nickname", "nick_name", "name", "text", "content"):
            if value.get(key):
                return str(value[key]).strip()
    return str(value).strip()


def _tags(value) -> list[str]:
    if isinstance(value, str):
        return [part.strip().lstrip("#") for part in value.split(",") if part.strip()]
    if isinstance(value, list):
        return [str(part).strip().lstrip("#") for part in value if str(part).strip()]
    return []


def _count(value) -> int:
    if isinstance(value, (int, float)):
        return max(0, int(value))
    text = str(value or "").replace(",", "").replace("，", "").strip()
    match = _COUNT_RE.match(text)
    if not match:
        return 0
    number = float(match.group(1))
    unit = match.group(2).lower()
    multiplier = 10_000 if unit in {"w", "万"} else 1_000 if unit in {"k", "千"} else 1
    return max(0, int(round(number * multiplier)))


def _timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown xiaohongshu timezone: {name}") from exc
