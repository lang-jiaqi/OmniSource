from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from omnisource.repository_feedback import ISSUE_MARKER, feedback_events_from_issues, import_feedback_issues


def issue(number: int, author: str, payload: dict, updated_at: str) -> dict:
    return {
        "number": number,
        "author": {"login": author},
        "body": f"{ISSUE_MARKER}\n{json.dumps(payload)}\n-->",
        "createdAt": updated_at,
        "updatedAt": updated_at,
    }


class RepositoryFeedbackTests(unittest.TestCase):
    def test_imports_only_latest_owner_feedback_per_item(self) -> None:
        base = {
            "version": 1,
            "track": "ai-infra",
            "item_type": "paper",
            "item_id": "paper-1",
            "title": "Serving Paper",
            "sources": "arxiv",
            "reason": "Includes real deployment evidence.",
        }
        issues = [
            issue(1, "alice", {**base, "vote": "up"}, "2026-07-20T08:00:00Z"),
            issue(2, "mallory", {**base, "vote": "down"}, "2026-07-21T08:00:00Z"),
            issue(3, "alice", {**base, "vote": "down"}, "2026-07-22T08:00:00Z"),
        ]

        events = feedback_events_from_issues(issues, "Alice")

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["vote"], "down")
        self.assertEqual(events[0]["item_id"], "paper-1")

    def test_ignores_malformed_or_incomplete_feedback(self) -> None:
        issues = [
            {"number": 1, "author": {"login": "alice"}, "body": "ordinary issue"},
            issue(2, "alice", {"version": 1, "vote": "up"}, "2026-07-21T08:00:00Z"),
            issue(3, "alice", {"version": 1, "track": "ai", "item_id": "x", "vote": "maybe", "reason": "x"}, "2026-07-21T09:00:00Z"),
        ]

        self.assertEqual(feedback_events_from_issues(issues, "alice"), [])

    def test_writes_feedback_jsonl_for_existing_summary_command(self) -> None:
        payload = {
            "version": 1,
            "track": "ai-algorithm",
            "item_type": "paper",
            "item_id": "paper-2",
            "vote": "up",
            "reason": "Strong reasoning method.",
        }
        with tempfile.TemporaryDirectory() as tmp:
            issue_path = Path(tmp) / "issues.json"
            output_path = Path(tmp) / "feedback.jsonl"
            issue_path.write_text(json.dumps([issue(7, "alice", payload, "2026-07-21T10:00:00Z")]), encoding="utf-8")

            target, issue_count, event_count = import_feedback_issues(issue_path, "alice", output_path)
            event = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(issue_count, 1)
        self.assertEqual(event_count, 1)
        self.assertEqual(event["reason"], "Strong reasoning method.")


if __name__ == "__main__":
    unittest.main()
