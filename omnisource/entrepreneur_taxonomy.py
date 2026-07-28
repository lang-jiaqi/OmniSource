"""Deterministic taxonomy for the entrepreneur track.

The entrepreneur report must remain useful when no LLM is configured.  Keep
the business-event classifier here so the Markdown report and the private
website use the same source of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


ENTREPRENEUR_TRACK = "entrepreneur"


@dataclass(frozen=True)
class EntrepreneurClassification:
    """The shared classification for one startup signal."""

    # Website-facing bucket.  The website keeps these four concise filters.
    event_type: str
    # Report-facing bucket, matching the four website filters.
    topic: str


@dataclass(frozen=True)
class _Rule:
    event_type: str
    topic: str
    terms: tuple[str, ...]
    priority: int


_RULES: tuple[_Rule, ...] = (
    _Rule(
        "融资",
        "融资",
        (
            "acquisition", "acqui-hire", "acquire", "acquires", "acquired",
            "merger", "buyout", "并购", "收购", "合并",
        ),
        0,
    ),
    _Rule(
        "融资",
        "融资",
        (
            "funding", "fundraise", "fundraising", "raise", "raised", "raises",
            "series a", "series b", "series c", "seed round", "venture capital",
            "valuation", "investment", "investor", "融资", "投资", "估值",
        ),
        1,
    ),
    _Rule(
        "产品",
        "产品",
        (
            "launch", "launched", "release", "released", "pricing", "product",
            "platform", "api", "model", "ships", "general availability", "rollout",
            "feature", "发布", "产品", "定价", "平台", "模型", "上线",
        ),
        2,
    ),
    _Rule(
        "团队",
        "团队",
        (
            "founder", "cofounder", "co-founder", "联合创始人", "创始人",
        ),
        3,
    ),
    _Rule(
        "团队",
        "团队",
        (
            "hiring", "hire", "recruit", "joined", "joins", "appointed", "executive",
            "leadership", "team", "organization", "talent", "layoff", "招聘", "团队",
            "组织", "高管", "人才",
        ),
        4,
    ),
    _Rule(
        "市场",
        "市场",
        (
            "customer", "customers", "adoption", "partnership", "partnered", "enterprise",
            "contract", "revenue", "sales", "expansion", "demand", "market", "competition",
            "competitive", "regulation", "regulatory", "procurement", "deployment",
            "go-to-market", "客户", "采用", "合作", "收入", "销售", "扩张", "需求",
            "市场", "竞争", "监管", "部署",
        ),
        5,
    ),
)

_DEFAULT = EntrepreneurClassification(
    event_type="市场",
    topic="市场",
)


def is_entrepreneur_track(track: dict | None) -> bool:
    """Return whether a track uses the built-in startup taxonomy."""
    if not isinstance(track, dict):
        return False
    return str(track.get("name") or "").strip().lower() == ENTREPRENEUR_TRACK


def classify_entrepreneur(title: object, summary: object = "") -> EntrepreneurClassification:
    """Classify a startup signal using title-weighted keyword evidence.

    A title hit scores three points and a summary hit scores one point.  This
    keeps a headline such as "Company launches API" in the product bucket even
    when the body also mentions an earlier funding round.
    """
    title_text = str(title or "").lower()
    body_text = str(summary or "").lower()
    scored: list[tuple[int, int, _Rule]] = []
    for rule in _RULES:
        score = sum(
            (3 if term in title_text else 0) + (1 if term in body_text else 0)
            for term in rule.terms
        )
        if score:
            scored.append((score, rule.priority, rule))
    if not scored:
        return _DEFAULT
    _score, _priority, best = max(scored, key=lambda item: (item[0], -item[1]))
    return EntrepreneurClassification(event_type=best.event_type, topic=best.topic)


def classify_entrepreneur_signal(signal: object) -> EntrepreneurClassification:
    """Classify an object exposing ``title`` and ``summary`` fields."""
    return classify_entrepreneur(
        getattr(signal, "title", ""),
        getattr(signal, "summary", ""),
    )


def assign_entrepreneur_topics(signals: Iterable[object], track: dict | None) -> None:
    """Write deterministic taxonomy topics onto entrepreneur-track signals."""
    if not is_entrepreneur_track(track):
        return
    for signal in signals:
        signal.topic = classify_entrepreneur_signal(signal).topic
