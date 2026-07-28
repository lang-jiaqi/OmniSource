"""Shared six-dimension scoring for the AI-tool radar.

The official website and the public ``builder/ai-tools`` track use the same
scoring vocabulary and formulas.  Collection and publishing stay separate:
the website has fixed official sources, while an open-source user can add
sources in their own track.
"""
from __future__ import annotations

import datetime as dt
import re
from urllib.parse import urlparse

from .models import Signal

TOOL_CATEGORIES = [
    "discovery",
    "coding",
    "automation",
    "builder",
    "research",
]

_CATEGORY_HINTS = {
    "coding": (
        "coding", "code", "developer", "devtool", "ide", "editor", "vscode",
        "jetbrains", "terminal", "cli", "programming", "agentic coding",
    ),
    "automation": (
        "automation", "browser", "agent", "mcp", "connector", "workflow",
        "integration", "api", "scraper", "orchestration",
    ),
    "builder": (
        "app builder", "builder", "rag", "agent app", "workflow app",
        "low-code", "low code", "studio", "prototype", "deploy",
    ),
    "research": (
        "research", "paper", "scholar", "search", "literature", "pdf",
        "citation", "notebook", "knowledge", "reading",
    ),
    "discovery": (
        "radar", "trending", "newsletter", "curation", "discover",
        "monitor", "feed", "directory", "awesome",
    ),
}
_AI_HINTS = (
    "ai", "llm", "agent", "copilot", "chatbot", "rag", "mcp", "model",
    "prompt", "assistant", "automation", "workflow", "research", "coding",
    "openai", "anthropic", "claude", "gemini", "cursor", "codex",
)
_TOOL_HINTS = (
    "tool", "cli", "app", "platform", "browser", "extension", "sdk",
    "framework", "library", "workflow", "dashboard", "ide", "agent",
)
_GENERIC_INCUMBENTS = {
    "tensorflow", "pytorch", "transformers", "langchain", "llama.cpp",
    "vllm", "kubernetes", "ray", "dify", "ollama",
}


def _clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _parse_dt(value: object) -> dt.datetime | None:
    if isinstance(value, dt.datetime):
        return value
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _blob(signal: Signal) -> str:
    pieces = [
        signal.title,
        signal.summary,
        signal.url,
        " ".join(signal.authors or []),
        " ".join(signal.sources or []),
    ]
    if isinstance(signal.extra, dict):
        pieces.extend(str(item) for item in signal.extra.get("topics") or [])
        pieces.append(str(signal.extra.get("language") or ""))
    return " ".join(_clean(piece).lower() for piece in pieces if piece)


def tool_name(signal: Signal) -> str:
    title = _clean(signal.title)
    if signal.type == "repo" and "/" in title:
        return title.split("/", 1)[1]
    parsed = urlparse(signal.url)
    if parsed.netloc == "github.com":
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            return parts[1]
    return title[:80] or "AI tool"


def categorize_tool(signal: Signal) -> str:
    text = _blob(signal)
    scores = {
        category: sum(1 for hint in hints if hint in text)
        for category, hints in _CATEGORY_HINTS.items()
    }
    category, score = max(scores.items(), key=lambda item: item[1])
    if score:
        return category
    if signal.type == "repo":
        return "coding"
    if signal.type == "blog":
        return "research"
    return "discovery"


def _score_bucket(value: float, thresholds: tuple[float, float, float, float]) -> int:
    if value >= thresholds[3]:
        return 5
    if value >= thresholds[2]:
        return 4
    if value >= thresholds[1]:
        return 3
    if value >= thresholds[0]:
        return 2
    return 1


def evaluate_tool(signal: Signal, category: str | None = None,
                  today: dt.date | None = None) -> dict[str, int]:
    """Score relevance, practical value, freshness, usability, credibility,
    and differentiation on a 1..5 scale."""
    category = category or categorize_tool(signal)
    today = today or dt.date.today()
    text = _blob(signal)
    ai_hits = sum(1 for hint in _AI_HINTS if hint in text)
    tool_hits = sum(1 for hint in _TOOL_HINTS if hint in text)
    relevance = min(5, max(1, 2 + ai_hits + min(1, tool_hits)))

    extra = signal.extra if isinstance(signal.extra, dict) else {}
    popularity = max(0, int(signal.popularity or 0))
    total_stars = int(extra.get("total_stars") or 0)
    trending_stars = int(extra.get("trending_stars") or 0)
    star_velocity = float(extra.get("star_velocity") or 0.0)
    signal_strength = max(popularity, trending_stars, star_velocity)
    practical_value = _score_bucket(signal_strength, (3, 15, 60, 200))
    if category in {"coding", "automation", "builder"} and signal.type == "repo":
        practical_value = min(5, practical_value + 1)

    published = _parse_dt(signal.published_at)
    if not published:
        published = _parse_dt(extra.get("pushed_at") or extra.get("created_at"))
    age = 30.0 if not published else max(0.0, float((today - published.date()).days))
    freshness = 5 if age <= 2 else 4 if age <= 7 else 3 if age <= 21 else 2 if age <= 60 else 1
    if trending_stars:
        freshness = min(5, freshness + 1)

    usability = 3
    if signal.type == "repo":
        usability += 1
        if extra.get("homepage"):
            usability += 1
        if extra.get("license"):
            usability = min(5, usability + 2)
    elif signal.url:
        usability += 1
    usability = min(5, usability)

    credibility = _score_bucket(max(total_stars, popularity), (10, 100, 1_000, 5_000))
    if signal.type == "repo" and extra.get("license"):
        credibility = min(5, credibility + 1)
    if "rss" in (signal.sources or []):
        credibility = max(3, credibility)

    created = _parse_dt(extra.get("created_at"))
    repo_age = None if not created else max(1.0, float((today - created.date()).days))
    name = tool_name(signal).lower()
    incumbent = name in _GENERIC_INCUMBENTS or signal.title.lower() in _GENERIC_INCUMBENTS
    differentiation = 3
    diff_terms = ("new", "agent", "mcp", "browser", "local", "open-source", "workflow", "multimodal")
    differentiation += min(2, sum(1 for term in diff_terms if term in text))
    if incumbent and not trending_stars:
        differentiation -= 2
    if repo_age and repo_age > 365 and not trending_stars:
        differentiation -= 1
    differentiation = min(5, max(1, differentiation))

    return {
        "relevance": relevance,
        "practical_value": practical_value,
        "freshness": freshness,
        "usability": usability,
        "credibility": credibility,
        "differentiation": differentiation,
    }


def aggregate_tool_score(evaluation: dict[str, int]) -> float:
    weights = {
        "relevance": 0.22,
        "practical_value": 0.22,
        "freshness": 0.20,
        "usability": 0.14,
        "credibility": 0.10,
        "differentiation": 0.12,
    }
    return sum(evaluation[key] * weight for key, weight in weights.items())


def score_tool(signal: Signal, today: dt.date | None = None) -> tuple[str, dict[str, int], float]:
    category = categorize_tool(signal)
    evaluation = evaluate_tool(signal, category, today)
    return category, evaluation, aggregate_tool_score(evaluation)
