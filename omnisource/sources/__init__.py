"""Source plugins. Each Source turns one upstream feed into Signals."""
from __future__ import annotations

from .arxiv import ArxivSource
from .base import Source
from .blogrxiv import BlogrXivSource
from .github import GitHubSource
from .hackernews import HackerNewsSource
from .hf import HFPapersSource
from .reddit import RedditSource
from .rss import RSSSource
from .twitter import TwitterSource
from .xiaohongshu import XiaohongshuSource
from .zhihu import ZhihuSource

# Name -> Source class. Tracks reference sources by these names.
# "twitter" is opt-in (off by default) — see docs/twitter-setup.md.
SOURCE_REGISTRY: dict[str, type[Source]] = {
    "blogrxiv": BlogrXivSource,
    "arxiv": ArxivSource,
    "hf_papers": HFPapersSource,
    "rss": RSSSource,
    "github": GitHubSource,
    "hackernews": HackerNewsSource,
    "reddit": RedditSource,
    "twitter": TwitterSource,
    "xiaohongshu": XiaohongshuSource,
    "zhihu": ZhihuSource,
}

__all__ = [
    "Source", "BlogrXivSource", "ArxivSource", "HFPapersSource", "RSSSource", "GitHubSource",
    "HackerNewsSource", "RedditSource", "TwitterSource", "XiaohongshuSource", "ZhihuSource",
    "SOURCE_REGISTRY",
]
