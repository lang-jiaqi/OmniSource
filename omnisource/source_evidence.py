"""Human-readable cross-source evidence for merged Signals."""
from __future__ import annotations

import re

from . import i18n
from .models import Signal

_ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}$")


def evidence_from_signal(signal: Signal) -> dict:
    return {
        "sources": list(signal.sources),
        "type": signal.type,
        "title": signal.title,
        "url": signal.url,
        "authors": list(signal.authors[:4]),
        "popularity": signal.popularity,
    }


def append_fold_evidence(base: Signal, other: Signal) -> None:
    entries = base.extra.setdefault("source_evidence", [])
    if not isinstance(entries, list):
        entries = []
        base.extra["source_evidence"] = entries
    if not entries:
        entries.append(evidence_from_signal(base))

    candidates = []
    prior = other.extra.get("source_evidence") if isinstance(other.extra, dict) else None
    if isinstance(prior, list):
        candidates.extend(e for e in prior if isinstance(e, dict))
    candidates.append(evidence_from_signal(other))

    seen = {
        (tuple(entry.get("sources", [])), entry.get("url"), entry.get("title"))
        for entry in entries
        if isinstance(entry, dict)
    }
    for entry in candidates:
        key = (tuple(entry.get("sources", [])), entry.get("url"), entry.get("title"))
        if key not in seen:
            entries.append(entry)
            seen.add(key)


def source_signal_items(signal: Signal, language: str | None) -> list[dict[str, str]]:
    if signal.type == "paper":
        return _paper_source_signal_items(signal, language)
    return _artifact_source_signal_items(signal, language)


def paper_source_signal_items(signal: Signal, language: str | None) -> list[dict[str, str]]:
    return _paper_source_signal_items(signal, language)


def _paper_source_signal_items(signal: Signal, language: str | None) -> list[dict[str, str]]:
    if signal.type != "paper":
        return []
    lang = i18n.norm_lang(language)
    zh = lang == "zh"
    sources = set(signal.sources)
    parts: list[dict[str, str]] = []

    if signal.followed:
        label = f"论文作者名单命中 {signal.followed}" if zh else f"Paper author watchlist: {signal.followed}"
        parts.append({"source": "watchlist", "label": label, "url": ""})

    if "arxiv" in sources:
        parts.append({
            "source": "arxiv",
            "label": "arXiv 收录" if zh else "arXiv indexed",
            "url": _arxiv_url(signal),
        })
    if "hf_papers" in sources:
        label = "Hugging Face Daily Papers"
        popularity = _source_popularity(signal, "hf_papers")
        if popularity is None:
            popularity = signal.popularity
        if popularity:
            suffix = f"社区点赞 👍 {popularity}" if zh else f"community upvotes 👍 {popularity}"
            label += f"（{suffix}）" if zh else f" ({suffix})"
        parts.append({"source": "hf_papers", "label": label, "url": _hf_url(signal)})

    twitter = _entries_for(signal, "twitter")
    if "twitter" in sources:
        if twitter:
            for entry in twitter:
                handle = _handles([entry], limit=1)
                label = "X/Twitter"
                if handle:
                    verb = "提到" if zh else "mentioned by"
                    label = f"{label} {verb} {handle[0]}"
                else:
                    label = f"{label} {'提到' if zh else 'mentioned'}"
                likes = int(entry.get("popularity") or 0)
                if likes:
                    label += f" 👍 {likes}"
                parts.append({"source": "twitter", "label": label, "url": str(entry.get("url") or "")})
        else:
            parts.append({
                "source": "twitter",
                "label": f"X/Twitter {'提到' if zh else 'mentioned'}",
                "url": "",
            })

    if "hackernews" in sources:
        parts.extend(_discussion_items(signal, "hackernews", "Hacker News 讨论" if zh else "Hacker News discussion"))
    if "reddit" in sources:
        parts.extend(_discussion_items(signal, "reddit", "Reddit 讨论" if zh else "Reddit discussion"))
    if "xiaohongshu" in sources:
        parts.extend(_discussion_items(
            signal,
            "xiaohongshu",
            "小红书博主动态" if zh else "Xiaohongshu creator post",
        ))
    if "zhihu" in sources:
        parts.extend(_discussion_items(signal, "zhihu", "知乎内容" if zh else "Zhihu post"))
    if any(source in sources for source in ("rss", "blog", "blogrxiv")):
        parts.extend(_blog_items(signal, zh))

    return parts


def _artifact_source_signal_items(signal: Signal, language: str | None) -> list[dict[str, str]]:
    lang = i18n.norm_lang(language)
    zh = lang == "zh"
    sources = set(signal.sources)
    parts: list[dict[str, str]] = []

    if signal.type == "repo" or "github" in sources:
        discovery = str((signal.extra or {}).get("repo_discovery") or "")
        if discovery == "trending":
            label = "GitHub Trending" if not zh else "GitHub Trending"
            trending = int((signal.extra or {}).get("trending_stars") or 0)
            period = str((signal.extra or {}).get("trending_period") or "")
            if trending:
                label += f" ↗ {trending} {period}".rstrip()
        else:
            label = "GitHub 新项目/搜索" if zh else "GitHub fresh/search"
        parts.append({"source": "github", "label": label, "url": signal.url})

    if signal.type == "blog" or any(source in sources for source in ("rss", "blog", "blogrxiv")):
        if "zhihu" in sources:
            label = "知乎文章" if zh else "Zhihu article"
            parts.append({"source": "zhihu", "label": label, "url": signal.url})
        elif "blogrxiv" in sources:
            label = "BlogrXiv 精选" if zh else "BlogrXiv curated"
            parts.append({"source": "blogrxiv", "label": label, "url": signal.url})
        else:
            label = "RSS/博客源" if zh else "RSS/blog feed"
            parts.append({"source": "rss", "label": label, "url": signal.url})

    if signal.type == "social":
        for source, label in (
            ("twitter", "X/Twitter" if not zh else "X/Twitter"),
            ("hackernews", "Hacker News 讨论" if zh else "Hacker News discussion"),
            ("reddit", "Reddit 讨论" if zh else "Reddit discussion"),
            ("xiaohongshu", "小红书博主动态" if zh else "Xiaohongshu creator post"),
            ("zhihu", "知乎内容" if zh else "Zhihu post"),
        ):
            if source in sources:
                item_label = label
                if signal.popularity:
                    item_label += f" 👍 {signal.popularity}"
                parts.append({"source": source, "label": item_label, "url": signal.url})

    if signal.type != "social" and "xiaohongshu" in sources:
        parts.extend(_discussion_items(
            signal,
            "xiaohongshu",
            "小红书博主动态" if zh else "Xiaohongshu creator post",
        ))

    if parts:
        return parts
    return [
        {
            "source": source,
            "label": _source_label(source, zh),
            "url": signal.url,
        }
        for source in signal.sources
    ]


def paper_source_signal_text(signal: Signal, language: str | None) -> str:
    return " · ".join(item["label"] for item in paper_source_signal_items(signal, language))


def source_signal_markdown(signal: Signal, language: str | None) -> str:
    return _source_signal_markdown(source_signal_items(signal, language))


def paper_source_signal_markdown(signal: Signal, language: str | None) -> str:
    return _source_signal_markdown(paper_source_signal_items(signal, language))


def _source_signal_markdown(items: list[dict[str, str]]) -> str:
    parts = []
    for item in items:
        label = _markdown_escape(item["label"])
        url = item.get("url")
        if url:
            parts.append(f"[{label}]({url})")
        else:
            parts.append(label)
    return " · ".join(parts)


def _source_label(source: str, zh: bool) -> str:
    labels = {
        "arxiv": "arXiv 收录" if zh else "arXiv indexed",
        "hf_papers": "Hugging Face Daily Papers",
        "github": "GitHub",
        "rss": "RSS/博客源" if zh else "RSS/blog feed",
        "blog": "博客" if zh else "Blog",
        "blogrxiv": "BlogrXiv 精选" if zh else "BlogrXiv curated",
        "twitter": "X/Twitter",
        "hackernews": "Hacker News 讨论" if zh else "Hacker News discussion",
        "reddit": "Reddit 讨论" if zh else "Reddit discussion",
        "xiaohongshu": "小红书博主动态" if zh else "Xiaohongshu creator post",
        "zhihu": "知乎内容" if zh else "Zhihu post",
    }
    return labels.get(source, source)


def _entries_for(signal: Signal, source: str) -> list[dict]:
    raw = signal.extra.get("source_evidence") if isinstance(signal.extra, dict) else None
    if not isinstance(raw, list):
        return []
    return [
        entry
        for entry in raw
        if isinstance(entry, dict) and source in set(entry.get("sources") or [])
    ]


def _source_popularity(signal: Signal, source: str) -> int | None:
    values = [int(entry.get("popularity") or 0) for entry in _entries_for(signal, source)]
    return max(values) if values else None


def _handles(entries: list[dict], limit: int = 3) -> list[str]:
    handles: list[str] = []
    for entry in entries:
        for author in entry.get("authors") or []:
            handle = str(author).strip()
            if not handle:
                continue
            if not handle.startswith("@"):
                handle = f"@{handle}"
            if handle not in handles:
                handles.append(handle)
            if len(handles) >= limit:
                return handles
    return handles


def _source_url(signal: Signal, source: str) -> str:
    for entry in _entries_for(signal, source):
        url = str(entry.get("url") or "").strip()
        if url:
            return url
    return ""


def _arxiv_url(signal: Signal) -> str:
    url = _source_url(signal, "arxiv") or signal.url
    if "arxiv.org" in url:
        return url
    if _ARXIV_ID.match(signal.id):
        return f"https://arxiv.org/abs/{signal.id}"
    return url


def _hf_url(signal: Signal) -> str:
    if _ARXIV_ID.match(signal.id):
        return f"https://huggingface.co/papers/{signal.id}"
    url = _source_url(signal, "hf_papers")
    if "huggingface.co/papers/" in url:
        return url
    return ""


def _discussion_items(signal: Signal, source: str, base_label: str) -> list[dict[str, str]]:
    entries = _entries_for(signal, source)
    if not entries:
        return [{"source": source, "label": base_label, "url": ""}]
    items = []
    for entry in entries:
        label = base_label
        popularity = int(entry.get("popularity") or 0)
        if popularity:
            label += f" 👍 {popularity}"
        items.append({"source": source, "label": label, "url": str(entry.get("url") or "")})
    return items


def _blog_items(signal: Signal, zh: bool) -> list[dict[str, str]]:
    items = []
    for source in ("rss", "blog", "blogrxiv"):
        for entry in _entries_for(signal, source):
            title = str(entry.get("title") or "").strip()
            label = (
                "BlogrXiv 精选" if zh else "BlogrXiv curated"
            ) if source == "blogrxiv" else ("博客" if zh else "Blog")
            if title:
                label += f": {title[:48]}{'...' if len(title) > 48 else ''}"
            items.append({"source": source, "label": label, "url": str(entry.get("url") or "")})
    return items


def _markdown_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
