"""Editor agent: organize the curated sections into the final report.

Groups items by sub-topic within each section, flattens each Signal into the
fields a template needs (so templates stay presentational), and renders markdown
through Jinja. Templates live in omnisource/templates/.
"""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .. import i18n
from ..models import Signal
from ..source_evidence import source_signal_markdown
from ..topic_taxonomy import flatten_topics
from .curator import SECTIONS

# autoescape off so markdown isn't HTML-escaped.
JINJA = Environment(
    loader=FileSystemLoader(Path(__file__).resolve().parent.parent / "templates"),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _localized_text(s: Signal, language: str | None) -> dict:
    raw = s.extra.get("i18n") if isinstance(s.extra, dict) else None
    if isinstance(raw, dict):
        value = raw.get(i18n.norm_lang(language))
        if isinstance(value, dict):
            return value
    return {}


def _method_brief(localized: dict) -> dict[str, str]:
    raw = localized.get("method_brief")
    if not isinstance(raw, dict):
        return {}
    result = {
        "problem": str(raw.get("problem") or "").strip(),
        "method": str(raw.get("method") or "").strip(),
        "difference": str(raw.get("difference") or "").strip(),
        "evidence": str(raw.get("evidence") or "").strip(),
    }
    return result if any(result.values()) else {}


def _localized_abstract(s: Signal, localized: dict, language: str | None) -> str:
    translated = str(localized.get("abstract") or localized.get("summary") or "").strip()
    if translated:
        return translated
    if i18n.norm_lang(language) == "zh":
        key_idea = str(localized.get("key_idea") or "").strip()
        if key_idea:
            return key_idea
    return s.summary


def _popularity_meta(s: Signal) -> list[str]:
    if s.type == "paper":
        return []
    if s.type != "repo":
        return [f"👍 {s.popularity}"] if s.popularity else []
    extra = s.extra or {}
    bits = []
    trending = int(extra.get("trending_stars") or 0)
    if trending:
        period = extra.get("trending_period") or "recent"
        bits.append(f"↗ {trending} {period}")
    else:
        velocity = float(extra.get("star_velocity") or 0.0)
        if velocity:
            bits.append(f"↗ {velocity:.1f}/day")
    total = int(extra.get("total_stars") or 0)
    if total:
        bits.append(f"⭐ {total}")
    if not bits and s.popularity:
        bits.append(f"👍 {s.popularity}")
    return bits


def _extra_link_line(s: Signal, t: dict) -> str:
    if not s.code_url or s.code_url == s.url:
        return ""
    return f"**{t['code']}:** {s.code_url}"


def _item_context(s: Signal, n: int, t: dict, language: str | None = None) -> dict:
    """Flatten a Signal into the fields a template needs — the conditional
    'which meta to show' logic stays here so templates stay presentational."""
    authors = ", ".join(s.authors[:5]) + (" et al." if len(s.authors) > 5 else "")
    meta = []
    if s.citation_count:
        meta.append(f"cites {s.citation_count}")
    if s.read_priority:
        meta.append(f"priority {s.read_priority}")
    if s.llm_relevance is not None:
        meta.append(f"rel {s.llm_relevance:.2f}")
    if s.novelty is not None:
        meta.append(f"nov {s.novelty:.2f}")
    if s.review_score is not None:
        meta.append(f"{t['potential']} {int(round(s.review_score * 100))}")
    tool_evaluation = (s.extra or {}).get("tool_evaluation") if isinstance(s.extra, dict) else None
    if isinstance(tool_evaluation, dict):
        if i18n.norm_lang(language) == "zh":
            labels = {
                "relevance": "相关性",
                "practical_value": "实用价值",
                "freshness": "新鲜度",
                "usability": "可用性",
                "credibility": "可信度",
                "differentiation": "差异化",
            }
            prefix = "工具评分："
        else:
            labels = {
                "relevance": "relevance",
                "practical_value": "practical value",
                "freshness": "freshness",
                "usability": "usability",
                "credibility": "credibility",
                "differentiation": "differentiation",
            }
            prefix = "Tool scores: "
        score_line = " / ".join(
            f"{labels.get(key, key)} {int(value)}/5"
            for key, value in tool_evaluation.items()
        )
        meta.append(f"{prefix}{score_line}")
    meta.append(s.published_at.strftime("%Y-%m-%d") if s.published_at else "n/a")
    meta.extend(_popularity_meta(s))
    localized = _localized_text(s, language)
    why_it_matters = localized.get("why_it_matters") or s.why_it_matters
    method_brief = _method_brief(localized) if s.type == "paper" else {}
    enriched = bool(why_it_matters)
    return {
        "n": n,
        "title": s.title,
        "authors": authors,
        "meta": "  ·  ".join(meta),
        "link_line": _extra_link_line(s, t),
        "source_signal_line": source_signal_markdown(s, language),
        "why_it_matters": why_it_matters,
        "abstract": _localized_abstract(s, localized, language) if s.type == "paper" else "",
        "method_brief": method_brief,
        "summary": None if s.type == "paper" or enriched else s.summary,
    }


def group_by_topic(items: list[Signal]) -> list[tuple[str, list[Signal]]]:
    """Group items by sub-topic, ordered by group size then best score. Items
    keep their score order within a group. Returns [(topic, items), ...]."""
    groups: dict[str, list[Signal]] = {}
    for s in items:
        groups.setdefault(s.topic or "other", []).append(s)
    return sorted(
        groups.items(),
        key=lambda kv: (len(kv[1]), max((s.final_score or 0.0) for s in kv[1])),
        reverse=True,
    )


def build_context(sections: dict[str, list[Signal]], track: dict, date_str: str, period: str,
                  watchlist: list[Signal] | None = None, language: str | None = None) -> dict:
    language = language or track.get("output", {}).get("language")
    t = i18n.strings(language)
    cluster = bool(flatten_topics(track.get("topics")))
    topic_counts: dict[str, int] = {}
    section_ctx = []
    if watchlist:
        entries = [_item_context(s, i, t, language) for i, s in enumerate(watchlist, 1)]
        section_ctx.append({"heading": t["watchlist"], "groups": [{"topic": None, "entries": entries}]})
    for typ, _quota_key in SECTIONS:
        items = sections.get(typ)
        if not items:
            continue
        groups = []
        n = 0
        if cluster:
            for topic, group in group_by_topic(items):
                rendered = []
                for s in group:
                    n += 1
                    rendered.append(_item_context(s, n, t, language))
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
                groups.append({"topic": topic, "entries": rendered})
        else:
            groups.append({"topic": None, "entries": [_item_context(s, i, t, language) for i, s in enumerate(items, 1)]})
        section_ctx.append({"heading": t[typ], "groups": groups})
    return {
        "period": period,
        "track_name": i18n.track_display_name(track, language),
        "date": date_str,
        "total": sum(len(v) for v in sections.values()),
        "sources": ", ".join(track.get("sources", [])),
        "topic_counts": sorted(topic_counts.items(), key=lambda kv: kv[1], reverse=True),
        "sections": section_ctx,
        "labels": t,
    }


def render(sections: dict[str, list[Signal]], track: dict, date_str: str,
           period: str = "Daily", template: str = "daily_report.md.j2",
           watchlist: list[Signal] | None = None) -> str:
    context = build_context(sections, track, date_str, period, watchlist)
    return JINJA.get_template(template).render(**context)
