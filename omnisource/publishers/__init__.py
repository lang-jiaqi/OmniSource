"""Publishers. Each delivers the finished report somewhere."""
from __future__ import annotations

import os

from .base import Publisher, Report
from .github_issue import GitHubIssuePublisher
from .markdown import MarkdownPublisher

PUBLISHER_REGISTRY: dict[str, type[Publisher]] = {
    "markdown": MarkdownPublisher,
    "github_issue": GitHubIssuePublisher,
}


DEFAULT_PUBLISHERS = ["markdown", "github_issue"]


def build_publishers(track: dict) -> list[Publisher]:
    publishers: list[Publisher] = []
    configured = os.environ.get("OMNISOURCE_PUBLISHERS", "").strip()
    names = [item.strip() for item in configured.split(",") if item.strip()] if configured else track.get("publishers", DEFAULT_PUBLISHERS)
    for name in names:
        cls = PUBLISHER_REGISTRY.get(name)
        if cls is None:
            print(f"  ! unknown publisher '{name}', skipping")
            continue
        publishers.append(cls())
    return publishers


__all__ = ["Publisher", "Report", "PUBLISHER_REGISTRY", "build_publishers"]
