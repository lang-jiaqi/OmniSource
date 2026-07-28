"""Track-specific relevance helpers for the curator.

The LLM remains the semantic judge, but some tracks need cheap guardrails before
the LLM budget is spent. For example, AI infrastructure should favor systems
categories and require concrete systems evidence when a paper comes from broad
AI/ML categories.
"""
from __future__ import annotations

import re

from ..models import Signal


def allows_keyword_fallback(signal: Signal, track: dict) -> bool:
    """Whether this signal type may survive the keyword gate with zero hits."""
    cfg = _type_cfg(signal, track)
    return bool(cfg.get("allow_keyword_fallback"))


def annotate_track_relevance(signal: Signal, track: dict) -> bool:
    """Attach deterministic relevance metadata and return whether to keep it."""
    cfg = _type_cfg(signal, track)
    if not cfg:
        return True

    text = _text(signal)
    anchors = _matching_terms(text, cfg.get("anchor_keywords", []))
    categories = _arxiv_categories(signal)
    preferred = _category_hits(categories, cfg.get("preferred_arxiv_categories", []))
    broad = _category_hits(categories, cfg.get("broad_arxiv_categories", []))
    category_bonus = _category_bonus(categories, cfg.get("category_boosts", {}))

    signal.extra.setdefault("track_relevance", {})
    signal.extra["track_relevance"].update(
        {
            "anchor_hits": anchors,
            "arxiv_category_hits": preferred,
            "broad_arxiv_category_hits": broad,
            "bonus": category_bonus + min(len(anchors), 3),
        }
    )

    min_anchor = int(cfg.get("min_anchor_hits", 0) or 0)
    if min_anchor and not preferred and len(anchors) < min_anchor:
        return False

    broad_min_anchor = int(cfg.get("broad_category_min_anchor_hits", 0) or 0)
    if broad and not preferred and len(anchors) < broad_min_anchor:
        return False

    noise_terms = _matching_terms(text, cfg.get("noise_keywords", []))
    if noise_terms and not preferred and len(anchors) == 0:
        signal.extra["track_relevance"]["noise_hits"] = noise_terms
        return False

    return True


def track_relevance_bonus(signal: Signal) -> int:
    data = signal.extra.get("track_relevance") if isinstance(signal.extra, dict) else None
    if not isinstance(data, dict):
        return 0
    try:
        return int(data.get("bonus", 0) or 0)
    except (TypeError, ValueError):
        return 0


def _type_cfg(signal: Signal, track: dict) -> dict:
    raw = track.get("relevance_filter") or {}
    if not isinstance(raw, dict):
        return {}
    cfg = raw.get(signal.type) or {}
    return cfg if isinstance(cfg, dict) else {}


def _text(signal: Signal) -> str:
    parts = [signal.title, signal.summary, " ".join(signal.authors)]
    extra = signal.extra if isinstance(signal.extra, dict) else {}
    if extra:
        parts.append(" ".join(str(item) for item in extra.get("topics", []) or []))
        parts.append(str(extra.get("homepage", "")))
    return " ".join(part for part in parts if part).lower()


def _matching_terms(text: str, terms: list[str] | tuple[str, ...]) -> list[str]:
    matched = []
    for term in terms:
        value = str(term).strip()
        normalized = value.lower()
        if not normalized:
            continue
        # Short technical acronyms need word boundaries: ``AI`` should not
        # match the middle of an unrelated word, while ``OpenAI`` remains an
        # explicit company anchor when it is listed separately.
        if re.fullmatch(r"[a-z0-9+#.-]{1,4}", normalized):
            found = re.search(rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])", text)
        else:
            found = normalized in text
        if found:
            matched.append(term)
    return matched


def _arxiv_categories(signal: Signal) -> list[str]:
    extra = signal.extra if isinstance(signal.extra, dict) else {}
    raw = extra.get("arxiv_categories") or []
    categories = [str(category) for category in raw]
    primary = extra.get("primary_arxiv_category")
    if primary:
        categories.insert(0, str(primary))
    seen: set[str] = set()
    result: list[str] = []
    for category in categories:
        if category not in seen:
            result.append(category)
            seen.add(category)
    return result


def _category_hits(categories: list[str], wanted: list[str] | tuple[str, ...]) -> list[str]:
    wanted_set = {str(category) for category in wanted}
    return [category for category in categories if category in wanted_set]


def _category_bonus(categories: list[str], bonuses: dict | None) -> int:
    if not isinstance(bonuses, dict):
        return 0
    best = 0
    for category in categories:
        try:
            best = max(best, int(bonuses.get(category, 0) or 0))
        except (TypeError, ValueError):
            continue
    return best
