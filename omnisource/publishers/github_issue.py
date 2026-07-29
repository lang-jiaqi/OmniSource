"""Open the daily report as a GitHub issue.

Uses GITHUB_TOKEN + GITHUB_REPOSITORY, which GitHub Actions sets automatically.
Outside CI (no token/repo) it just skips, so local runs aren't affected.
"""
from __future__ import annotations

import os

import requests

from .base import Publisher, Report

API = "https://api.github.com"


class GitHubIssuePublisher(Publisher):
    name = "github_issue"

    def publish(self, report: Report) -> None:
        token = os.environ.get("GITHUB_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY")  # "owner/name"
        if not token or not repo:
            print("  github_issue: skipped (no GITHUB_TOKEN / GITHUB_REPOSITORY)")
            return
        title = f"OmniSource {report.period} — {report.track['name']} — {report.date}"
        resp = requests.post(
            f"{API}/repos/{repo}/issues",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
            json={"title": title, "body": report.markdown},
            timeout=30,
        )
        if resp.status_code >= 300:
            print(f"  github_issue: failed ({resp.status_code}) {resp.text[:200]}")
            return
        print(f"  github_issue: {resp.json().get('html_url')}")
