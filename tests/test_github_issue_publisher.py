from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omnisource.publishers.base import Report
from omnisource.publishers.github_issue import GitHubIssuePublisher


def report() -> Report:
    return Report(
        track={"name": "ai-algorithm"},
        date="2026-07-28",
        markdown="# Daily report",
        sections={},
        reports_dir=Path(tempfile.gettempdir()),
    )


class GitHubIssuePublisherTests(unittest.TestCase):
    @patch("omnisource.publishers.github_issue.requests.post")
    def test_override_publishes_to_workspace_repository(self, post) -> None:
        post.return_value.status_code = 201
        post.return_value.json.return_value = {"html_url": "https://github.com/example/issues/1"}
        with patch.dict(
            os.environ,
            {
                "OMNISOURCE_ISSUE_REPOSITORY": "lang-jiaqi/OmniSource-workspace",
                "OMNISOURCE_ISSUE_TOKEN": "workspace-token",
                "GITHUB_REPOSITORY": "lang-jiaqi/OmniSource",
                "GITHUB_TOKEN": "default-token",
            },
            clear=False,
        ):
            GitHubIssuePublisher().publish(report())

        self.assertEqual(post.call_args.args[0], "https://api.github.com/repos/lang-jiaqi/OmniSource-workspace/issues")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer workspace-token")

    @patch("omnisource.publishers.github_issue.requests.post")
    def test_without_override_publishes_to_current_repository(self, post) -> None:
        post.return_value.status_code = 201
        post.return_value.json.return_value = {"html_url": "https://github.com/example/issues/1"}
        with patch.dict(
            os.environ,
            {
                "OMNISOURCE_ISSUE_REPOSITORY": "",
                "OMNISOURCE_ISSUE_TOKEN": "",
                "GITHUB_REPOSITORY": "someone/OmniSource",
                "GITHUB_TOKEN": "fork-token",
            },
            clear=False,
        ):
            GitHubIssuePublisher().publish(report())

        self.assertEqual(post.call_args.args[0], "https://api.github.com/repos/someone/OmniSource/issues")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer fork-token")


if __name__ == "__main__":
    unittest.main()
