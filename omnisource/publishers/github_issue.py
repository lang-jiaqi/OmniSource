"""Open the daily report as a GitHub issue.

By default, use GITHUB_TOKEN + GITHUB_REPOSITORY, which GitHub Actions sets
automatically. The upstream repository can set an explicit target repository
and token so its reports land in a separate private/workspace repository. Forks
leave those override variables empty and continue publishing to themselves.
"""
from __future__ import annotations

import os

import requests

from .base import Publisher, Report

API = "https://api.github.com"


class GitHubIssuePublisher(Publisher):
    name = "github_issue"

    def publish(self, report: Report) -> None:
        target_repo = os.environ.get("OMNISOURCE_ISSUE_REPOSITORY")
        if target_repo:
            repo = target_repo
            token = os.environ.get("OMNISOURCE_ISSUE_TOKEN")
            if not token:
                raise RuntimeError(
                    f"github_issue: target repository {repo} is configured but "
                    "OMNISOURCE_ISSUE_TOKEN is missing"
                )
        else:
            repo = os.environ.get("GITHUB_REPOSITORY")  # "owner/name"
            token = os.environ.get("GITHUB_TOKEN")
        if not token or not repo:
            print("  github_issue: skipped (no issue token / repository)")
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
            detail = resp.text[:200]
            raise RuntimeError(f"github_issue: failed ({resp.status_code}) {detail}")
        print(f"  github_issue: {resp.json().get('html_url')}")
