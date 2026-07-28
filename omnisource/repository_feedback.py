"""Import structured recommendation feedback from GitHub Issues."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .prompt_feedback import FEEDBACK_EVENTS_PATH

ISSUE_MARKER = "<!-- omnisource-feedback:v1"
ISSUE_END = "-->"
MAX_FIELD_LENGTH = 500


def _text(value: Any, limit: int = MAX_FIELD_LENGTH) -> str:
    return " ".join(str(value or "").split())[:limit]


def _issue_author(issue: dict[str, Any]) -> str:
    author = issue.get("author")
    if isinstance(author, dict):
        return _text(author.get("login"), 100)
    return _text(author, 100)


def _payload(body: Any) -> dict[str, Any] | None:
    text = str(body or "")
    start = text.find(ISSUE_MARKER)
    if start < 0:
        return None
    start += len(ISSUE_MARKER)
    end = text.find(ISSUE_END, start)
    if end < 0:
        return None
    try:
        value = json.loads(text[start:end].strip())
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _event(issue: dict[str, Any], owner: str) -> dict[str, str] | None:
    if _issue_author(issue).lower() != owner.strip().lower():
        return None
    payload = _payload(issue.get("body"))
    if not payload or payload.get("version") != 1:
        return None
    vote = _text(payload.get("vote"), 20).lower()
    if vote not in {"up", "down"}:
        return None
    track = _text(payload.get("track"), 100)
    item_type = _text(payload.get("item_type") or payload.get("type") or "item", 30)
    item_id = _text(payload.get("item_id") or payload.get("id"), 200)
    reason = _text(payload.get("reason"))
    if not track or not item_id or not reason:
        return None
    sources = payload.get("sources")
    if isinstance(sources, list):
        sources = ", ".join(_text(source, 80) for source in sources if _text(source, 80))
    return {
        "created_at": _text(issue.get("updatedAt") or issue.get("createdAt"), 50),
        "track": track,
        "language": _text(payload.get("language"), 20),
        "item_type": item_type,
        "item_id": item_id,
        "title": _text(payload.get("title"), 300),
        "url": _text(payload.get("url"), 500),
        "sources": _text(sources),
        "vote": vote,
        "reason": reason,
    }


def feedback_events_from_issues(issues: list[Any], owner: str) -> list[dict[str, str]]:
    """Return the latest valid owner-authored feedback for each report item."""
    latest: dict[tuple[str, str, str], dict[str, str]] = {}
    valid_issues = [issue for issue in issues if isinstance(issue, dict)]
    valid_issues.sort(key=lambda issue: (_text(issue.get("updatedAt") or issue.get("createdAt"), 50), int(issue.get("number") or 0)))
    for issue in valid_issues:
        event = _event(issue, owner)
        if event:
            key = (event["track"].lower(), event["item_type"].lower(), event["item_id"].lower())
            latest[key] = event
    return sorted(latest.values(), key=lambda event: event["created_at"])


def import_feedback_issues(
    issue_path: Path,
    owner: str,
    output_path: Path | None = None,
) -> tuple[Path, int, int]:
    """Convert a ``gh issue list --json ...`` response into feedback JSONL."""
    raw = json.loads(issue_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("GitHub issue input must be a JSON array")
    events = feedback_events_from_issues(raw, owner)
    target = output_path or FEEDBACK_EVENTS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(json.dumps(event, ensure_ascii=False) for event in events)
    target.write_text(content + ("\n" if content else ""), encoding="utf-8")
    return target, len(raw), len(events)
