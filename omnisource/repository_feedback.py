"""Import structured recommendation feedback from GitHub Issues."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from . import i18n
from .models import Signal
from .personalization import feedback_terms_for_signal
from .prompt_feedback import FEEDBACK_EVENTS_PATH

ISSUE_MARKER = "<!-- omnisource-feedback:v1"
ISSUE_MARKER_V2 = "<!-- omnisource-feedback:v2"
ISSUE_END = "-->"
MAX_FIELD_LENGTH = 500
VALID_ACTIONS = {"like", "ignore", "lower_similar", "follow_author"}
ACTION_CODES = {"l": "like", "i": "ignore", "d": "lower_similar", "f": "follow_author"}
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _text(value: Any, limit: int = MAX_FIELD_LENGTH) -> str:
    return " ".join(str(value or "").split())[:limit]


def _issue_author(issue: dict[str, Any]) -> str:
    author = issue.get("author")
    if isinstance(author, dict):
        return _text(author.get("login"), 100)
    return _text(author, 100)


def _payload(body: Any) -> dict[str, Any] | None:
    text = str(body or "")
    for marker in (ISSUE_MARKER_V2, ISSUE_MARKER):
        start = text.find(marker)
        if start < 0:
            continue
        start += len(marker)
        end = text.find(ISSUE_END, start)
        if end < 0:
            return None
        try:
            value = json.loads(text[start:end].strip())
        except json.JSONDecodeError:
            return None
        if not isinstance(value, dict):
            return None
        if "v" in value:
            action = ACTION_CODES.get(_text(value.get("a"), 2), _text(value.get("a"), 30))
            return {
                "version": value.get("v"),
                "action": action,
                "track": value.get("t"),
                "item_type": value.get("y"),
                "item_id": value.get("i"),
                "title": value.get("n"),
                "topic": value.get("o"),
                "authors": value.get("u"),
                "keywords": value.get("k"),
                "target_author": value.get("f"),
                "reason": "",
            }
        return value
    return None


def _checked_action(body: Any, payload: dict[str, Any]) -> tuple[str, str]:
    """Read exactly one checked action from a pre-filled feedback Issue."""
    checked = re.findall(r"^- \[[xX]\] `([^`]+)`", str(body or ""), flags=re.MULTILINE)
    if len(checked) != 1:
        return "", ""
    token = checked[0].strip()
    if token in {"like", "ignore", "lower_similar"}:
        return token, ""
    if token.startswith("follow_author:"):
        try:
            index = int(token.split(":", 1)[1])
            authors = payload.get("authors") or []
            author = _text(authors[index], 200) if isinstance(authors, list) else ""
        except (ValueError, IndexError):
            return "", ""
        return ("follow_author", author) if author else ("", "")
    return "", ""


def _event(issue: dict[str, Any], owner: str) -> dict[str, Any] | None:
    if _issue_author(issue).lower() != owner.strip().lower():
        return None
    payload = _payload(issue.get("body"))
    if not payload or payload.get("version") not in {1, 2}:
        return None
    vote = _text(payload.get("vote"), 20).lower()
    action = _text(payload.get("action"), 30).lower()
    if not action and vote in {"up", "down"}:
        action = "like" if vote == "up" else "lower_similar"
    target_author = _text(payload.get("target_author"), 200)
    if action not in VALID_ACTIONS:
        action, target_author = _checked_action(issue.get("body"), payload)
        if action not in VALID_ACTIONS:
            return None
    track = _text(payload.get("track"), 100)
    item_type = _text(payload.get("item_type") or payload.get("type") or "item", 30)
    item_id = _text(payload.get("item_id") or payload.get("id"), 200)
    if not track or not item_id or (action == "follow_author" and not target_author):
        return None
    sources = payload.get("sources")
    if isinstance(sources, list):
        sources = ", ".join(_text(source, 80) for source in sources if _text(source, 80))
    event: dict[str, Any] = {
        "version": int(payload.get("version") or 1),
        "created_at": _text(issue.get("updatedAt") or issue.get("createdAt"), 50),
        "track": track,
        "language": _text(payload.get("language"), 20),
        "item_type": item_type,
        "item_id": item_id,
        "title": _text(payload.get("title"), 300),
        "url": _text(payload.get("url"), 500),
        "sources": _text(sources),
        "topic": _text(payload.get("topic"), 300),
        "authors": [_text(author, 200) for author in payload.get("authors", []) if _text(author, 200)]
        if isinstance(payload.get("authors"), list) else _text(payload.get("authors")),
        "keywords": [_text(keyword, 100) for keyword in payload.get("keywords", []) if _text(keyword, 100)]
        if isinstance(payload.get("keywords"), list) else _text(payload.get("keywords")),
        "action": action,
        "target_author": target_author,
        "reason": _text(payload.get("reason")),
    }
    if action in {"like", "lower_similar"}:
        event["vote"] = "up" if action == "like" else "down"
    return event


def _event_group(event: dict[str, Any]) -> str:
    action = event["action"]
    if action == "follow_author":
        return f"author:{_text(event.get('target_author')).lower()}"
    return "item-preference"


def feedback_events_from_issues(issues: list[Any], owner: str) -> list[dict[str, Any]]:
    """Return the latest valid owner-authored feedback for each action target."""
    latest: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    valid_issues = [issue for issue in issues if isinstance(issue, dict)]
    valid_issues.sort(key=lambda issue: (_text(issue.get("updatedAt") or issue.get("createdAt"), 50), int(issue.get("number") or 0)))
    for issue in valid_issues:
        event = _event(issue, owner)
        if event:
            key = (
                event["track"].lower(),
                event["item_type"].lower(),
                event["item_id"].lower(),
                _event_group(event),
            )
            latest[key] = event
    return sorted(latest.values(), key=lambda event: event["created_at"])


def _repository(value: str | None = None) -> str:
    repository = _text(value or os.environ.get("OMNISOURCE_FEEDBACK_REPOSITORY") or os.environ.get("GITHUB_REPOSITORY"), 200)
    return repository if REPOSITORY_PATTERN.fullmatch(repository) else ""


def _feedback_payload(signal: Signal, track: dict, action: str, *, target_author: str = "") -> dict[str, Any]:
    return {
        "version": 2,
        "action": action,
        "track": _text(track.get("_reference") or track.get("name"), 100),
        "language": i18n.norm_lang((track.get("output") or {}).get("language")),
        "item_type": _text(signal.type, 30),
        "item_id": _text(signal.id, 200),
        "title": _text(signal.title, 100),
        "topic": _text(signal.topic, 80),
        "authors": [_text(author, 80) for author in signal.authors[:3]],
        "keywords": [_text(keyword, 60) for keyword in feedback_terms_for_signal(signal, track)[:6]],
        "target_author": _text(target_author, 80),
        "reason": "",
    }


def _compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    action_codes = {value: key for key, value in ACTION_CODES.items()}
    compact = {
        "v": 2,
        "t": payload.get("track"),
        "y": payload.get("item_type"),
        "i": payload.get("item_id"),
        "n": payload.get("title"),
        "o": payload.get("topic"),
        "u": payload.get("authors"),
        "k": payload.get("keywords"),
    }
    if payload.get("action"):
        compact["a"] = action_codes.get(str(payload["action"]), payload["action"])
    if payload.get("target_author"):
        compact["f"] = payload["target_author"]
    return {key: value for key, value in compact.items() if value is not None and value != "" and value != []}


def feedback_issue_url(
    signal: Signal,
    track: dict,
    action: str,
    *,
    target_author: str = "",
    repository: str | None = None,
    language: str | None = None,
) -> str:
    """Build a confirm-before-submit GitHub Issue URL for one feedback action."""
    repo = _repository(repository)
    if not repo or action not in VALID_ACTIONS:
        return ""
    labels = i18n.strings(language)
    action_label = labels[f"feedback_action_{action}"]
    payload = _feedback_payload(signal, track, action, target_author=target_author)
    title_target = target_author or signal.title
    title = f"[OmniSource feedback] {action_label}: {_text(title_target, 120)}"
    body = (
        f"## {labels['feedback']}\n\n"
        f"- **{labels['feedback_action']}:** {action_label}\n"
        f"- **Track:** {payload['track']}\n"
        f"- **Item:** [{signal.title}]({signal.url})\n"
        + (f"- **{labels['authors']}:** {target_author}\n" if target_author else "")
        + f"\n{labels['feedback_confirm_help']}\n\n"
        + f"{ISSUE_MARKER_V2}\n{json.dumps(_compact_payload(payload), ensure_ascii=True, separators=(',', ':'))}\n{ISSUE_END}\n"
    )
    return f"https://github.com/{repo}/issues/new?{urlencode({'title': title, 'body': body})}"


def feedback_selector_url(
    signal: Signal,
    track: dict,
    *,
    repository: str | None = None,
    language: str | None = None,
) -> str:
    """Build one compact selector link instead of four large URLs per item."""
    repo = _repository(repository)
    if not repo:
        return ""
    payload = _feedback_payload(signal, track, "")
    title = f"[OmniSource feedback] {_text(signal.title, 80)}"
    options = [
        "- [ ] `like`",
        "- [ ] `ignore`",
        "- [ ] `lower_similar`",
    ]
    options.extend(
        f"- [ ] `follow_author:{index}` {author}"
        for index, author in enumerate(signal.authors[:3])
    )
    body = (
        "Select exactly one / 只选一项:\n\n"
        + "\n".join(options)
        + "\n\nSubmit this Issue / 然后提交 Issue.\n\n"
        + f"{ISSUE_MARKER_V2}\n{json.dumps(_compact_payload(payload), ensure_ascii=True, separators=(',', ':'))}\n{ISSUE_END}\n"
    )
    return f"https://github.com/{repo}/issues/new?{urlencode({'title': title, 'body': body})}"


def feedback_controls_markdown(
    signal: Signal,
    track: dict,
    language: str | None = None,
    repository: str | None = None,
) -> str:
    """Render the four requested feedback controls for Markdown reports."""
    repo = _repository(repository)
    if not repo:
        return ""
    labels = i18n.strings(language)
    url = feedback_selector_url(signal, track, repository=repo, language=language)
    return f"[{labels['feedback_open']}]({url})"


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
