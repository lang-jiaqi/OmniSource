"""Deterministic personalization from repository-synced feedback events.

Feedback influences the cheap shortlist as well as the final LLM-backed score:

* ``like`` promotes related items;
* ``ignore`` removes the exact item if it is collected again;
* ``lower_similar`` demotes related items;
* ``follow_author`` promotes new work by a named author.

The adjustment is deliberately bounded. A large feedback history must not
overpower track relevance or turn the score into a count of old clicks.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .models import Signal
from .prompt_feedback import load_feedback_events

DEFAULT_LIKE_BOOST = 0.12
DEFAULT_LOWER_PENALTY = 0.18
DEFAULT_FOLLOW_AUTHOR_BOOST = 0.24
DEFAULT_SIMILARITY_THRESHOLD = 0.25
MAX_ADJUSTMENT = 0.35

_WORD = re.compile(r"[a-z0-9][a-z0-9+#.-]{2,}", re.IGNORECASE)
_ZH_RUN = re.compile(r"[\u3400-\u9fff]+")
_NON_ALNUM = re.compile(r"[^a-z0-9\u3400-\u9fff]+")
_STOPWORDS = {
    "and", "are", "for", "from", "into", "our", "the", "this", "that", "their",
    "using", "via", "with", "without", "new", "model", "models", "paper", "study",
}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        values = value
    else:
        values = str(value or "").split(",")
    return [text for item in values if (text := _text(item))]


def _author_key(value: str) -> str:
    return _NON_ALNUM.sub("", value.lower())


def _tokens(value: str) -> set[str]:
    text = value.lower()
    tokens = {token for token in _WORD.findall(text) if token not in _STOPWORDS}
    for run in _ZH_RUN.findall(text):
        if len(run) <= 3:
            tokens.add(run)
        else:
            tokens.update(run[index : index + 2] for index in range(len(run) - 1))
    return tokens


def _overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / min(len(left), len(right))


def _matching_keywords(signal: Signal, track: dict) -> list[str]:
    text = f"{signal.title} {signal.summary}".lower()
    matches: list[str] = []
    for raw in track.get("keywords", []) or []:
        keyword = _text(raw)
        normalized = keyword.lower()
        if not normalized:
            continue
        if re.fullmatch(r"[a-z0-9+#.-]{1,4}", normalized):
            found = re.search(rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])", text)
        else:
            found = normalized in text
        if found:
            matches.append(keyword)
    return matches


def feedback_terms_for_signal(signal: Signal, track: dict) -> list[str]:
    """Return stable track terms embedded in report feedback payloads."""
    return _matching_keywords(signal, track)[:20]


def _track_ids(track: dict) -> set[str]:
    values = {track.get("name"), track.get("_reference")}
    return {_text(value).lower() for value in values if _text(value)}


def _event_matches_track(event: dict[str, Any], track: dict) -> bool:
    event_track = _text(event.get("track")).lower()
    return bool(event_track and event_track in _track_ids(track))


def _event_key(event: dict[str, Any]) -> tuple[str, str]:
    return (_text(event.get("item_type") or "item").lower(), _text(event.get("item_id")).lower())


def _event_similarity(event: dict[str, Any], signal: Signal, track: dict) -> float:
    event_type = _text(event.get("item_type")).lower()
    if event_type and event_type not in {"item", signal.type.lower()}:
        return 0.0

    score = 0.0
    event_topic = _text(event.get("topic")).lower()
    if event_topic and event_topic == _text(signal.topic).lower():
        score += 0.55

    event_keywords = {item.lower() for item in _list(event.get("keywords"))}
    signal_keywords = {item.lower() for item in _matching_keywords(signal, track)}
    score += 0.50 * _overlap(event_keywords, signal_keywords)

    event_title_tokens = _tokens(_text(event.get("title")))
    signal_tokens = _tokens(f"{signal.title} {signal.summary}")
    score += 0.35 * _overlap(event_title_tokens, signal_tokens)

    event_authors = {_author_key(item) for item in _list(event.get("authors")) if _author_key(item)}
    signal_authors = {_author_key(item) for item in signal.authors if _author_key(item)}
    if event_authors & signal_authors:
        score += 0.35
    return min(1.0, score)


def _number(config: dict, key: str, default: float) -> float:
    try:
        return float(config.get(key, default))
    except (TypeError, ValueError):
        return default


def _build_profile(events: list[dict[str, Any]], track: dict) -> dict[str, Any]:
    relevant = [event for event in events if _event_matches_track(event, track)]
    preferences: dict[tuple[str, str], dict[str, Any]] = {}
    followed: dict[str, str] = {}
    for event in relevant:
        action = _text(event.get("action")).lower()
        key = _event_key(event)
        if action in {"like", "ignore", "lower_similar"} and key[1]:
            preferences[key] = event
        elif action == "follow_author":
            author = _text(event.get("target_author"))
            if author and _author_key(author):
                followed[_author_key(author)] = author
    return {
        "dispositions": preferences,
        "liked": [event for event in preferences.values() if event.get("action") == "like"],
        "lowered": [event for event in preferences.values() if event.get("action") == "lower_similar"],
        "followed": followed,
    }


def apply_feedback(
    signals: list[Signal],
    track: dict,
    *,
    path: Path | None = None,
) -> list[Signal]:
    """Annotate signals with bounded adjustments and remove exact ignores."""
    config = track.get("personalization") or {}
    if config is False or (isinstance(config, dict) and config.get("enabled", True) is False):
        return signals
    config = config if isinstance(config, dict) else {}
    events = load_feedback_events(path)
    profile = _build_profile(events, track)
    if not events or not any(profile.values()):
        for signal in signals:
            if isinstance(signal.extra, dict):
                signal.extra.pop("personalization", None)
        return signals

    like_boost = _number(config, "like_boost", DEFAULT_LIKE_BOOST)
    lower_penalty = _number(config, "lower_similar_penalty", DEFAULT_LOWER_PENALTY)
    follow_boost = _number(config, "follow_author_boost", DEFAULT_FOLLOW_AUTHOR_BOOST)
    threshold = _number(config, "similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD)
    kept: list[Signal] = []

    for signal in signals:
        key = (signal.type.lower(), signal.id.lower())
        generic_key = ("item", signal.id.lower())
        disposition = profile["dispositions"].get(key) or profile["dispositions"].get(generic_key)
        if disposition and disposition.get("action") == "ignore":
            continue

        like_matches = [
            (_event_similarity(event, signal, track), event)
            for event in profile["liked"]
        ]
        lower_matches = [
            (_event_similarity(event, signal, track), event)
            for event in profile["lowered"]
        ]
        liked_similarity, liked_event = max(like_matches, default=(0.0, None), key=lambda item: item[0])
        lowered_similarity, lowered_event = max(lower_matches, default=(0.0, None), key=lambda item: item[0])
        if liked_similarity < threshold:
            liked_similarity, liked_event = 0.0, None
        if lowered_similarity < threshold:
            lowered_similarity, lowered_event = 0.0, None

        signal_authors = {_author_key(author): author for author in signal.authors if _author_key(author)}
        followed_keys = sorted(set(signal_authors) & set(profile["followed"]))
        followed_authors = [profile["followed"][author] for author in followed_keys]
        adjustment = like_boost * liked_similarity - lower_penalty * lowered_similarity
        if followed_authors:
            adjustment += follow_boost
        adjustment = max(-MAX_ADJUSTMENT, min(MAX_ADJUSTMENT, adjustment))

        signal.extra.setdefault("personalization", {})
        signal.extra["personalization"] = {
            "adjustment": round(adjustment, 6),
            "liked_similarity": round(liked_similarity, 6),
            "lowered_similarity": round(lowered_similarity, 6),
            "liked_item": _text((liked_event or {}).get("title")),
            "lowered_item": _text((lowered_event or {}).get("title")),
            "followed_authors": followed_authors,
        }
        kept.append(signal)
    return kept


def personalization_adjustment(signal: Signal) -> float:
    data = signal.extra.get("personalization") if isinstance(signal.extra, dict) else None
    if not isinstance(data, dict):
        return 0.0
    try:
        return float(data.get("adjustment", 0.0) or 0.0)
    except (TypeError, ValueError):
        return 0.0


def is_followed_author_signal(signal: Signal) -> bool:
    data = signal.extra.get("personalization") if isinstance(signal.extra, dict) else None
    return bool(isinstance(data, dict) and data.get("followed_authors"))


def adjusted_score(score: float, signal: Signal) -> float:
    """Apply personalization while keeping public scores in the 0..1 range."""
    return max(0.0, min(1.0, score + personalization_adjustment(signal)))
