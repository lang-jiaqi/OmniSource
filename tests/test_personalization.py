from __future__ import annotations

import datetime as dt
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from omnisource.agents import curator, editor
from omnisource.models import Signal
from omnisource.personalization import (
    adjusted_score,
    apply_feedback,
    is_followed_author_signal,
    personalization_adjustment,
)
from omnisource.prompt_feedback import load_feedback_events, record_feedback_event
from omnisource.repository_feedback import (
    ISSUE_MARKER_V2,
    feedback_events_from_issues,
    feedback_selector_url,
)


def signal(
    item_id: str,
    title: str,
    *,
    summary: str = "",
    authors: list[str] | None = None,
    topic: str | None = None,
) -> Signal:
    return Signal(
        id=item_id,
        title=title,
        url=f"https://example.com/{item_id}",
        type="paper",
        published_at=dt.datetime(2026, 7, 29, tzinfo=dt.timezone.utc),
        summary=summary,
        authors=authors or [],
        sources=["arxiv"],
        topic=topic,
    )


def write_events(path: Path, events: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")


class PersonalizationTests(unittest.TestCase):
    def test_records_and_loads_all_four_actions_without_reasons(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.jsonl"
            record_feedback_event(action="like", track="research/ai", item_id="p1", path=path)
            record_feedback_event(action="ignore", track="research/ai", item_id="p2", path=path)
            record_feedback_event(action="lower-similar", track="research/ai", item_id="p3", path=path)
            record_feedback_event(
                action="follow-author",
                track="research/ai",
                target_author="Ada Lovelace",
                path=path,
            )
            events = load_feedback_events(path)

        self.assertEqual(
            [event["action"] for event in events],
            ["like", "ignore", "lower_similar", "follow_author"],
        )

    def test_ignore_is_exact_and_track_scoped(self) -> None:
        events = [{"action": "ignore", "track": "research/ai", "item_type": "paper", "item_id": "p1"}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.jsonl"
            write_events(path, events)
            kept = apply_feedback(
                [signal("p1", "Ignored"), signal("p2", "Kept")],
                {"name": "ai", "_reference": "research/ai"},
                path=path,
            )
            other_track = apply_feedback(
                [signal("p1", "Still kept elsewhere")],
                {"name": "robotics", "_reference": "research/robotics"},
                path=path,
            )

        self.assertEqual([item.id for item in kept], ["p2"])
        self.assertEqual([item.id for item in other_track], ["p1"])

    def test_latest_item_action_replaces_an_older_ignore(self) -> None:
        events = [
            {"action": "ignore", "track": "research/ai", "item_type": "paper", "item_id": "p1"},
            {
                "action": "like",
                "track": "research/ai",
                "item_type": "paper",
                "item_id": "p1",
                "keywords": ["agent"],
            },
        ]
        candidate = signal("p1", "Agent paper", summary="agent")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.jsonl"
            write_events(path, events)
            kept = apply_feedback(
                [candidate],
                {"name": "ai", "_reference": "research/ai", "keywords": ["agent"]},
                path=path,
            )

        self.assertEqual(kept, [candidate])
        self.assertGreater(personalization_adjustment(candidate), 0)

    def test_like_and_lower_similar_adjust_ranking_in_opposite_directions(self) -> None:
        events = [
            {
                "action": "like",
                "track": "research/ai",
                "item_type": "paper",
                "item_id": "old-like",
                "title": "Agent planning with tools",
                "keywords": ["agent", "planning"],
            },
            {
                "action": "lower_similar",
                "track": "research/ai",
                "item_type": "paper",
                "item_id": "old-lower",
                "title": "Generic benchmark leaderboard",
                "keywords": ["benchmark"],
            },
        ]
        track = {
            "name": "ai",
            "_reference": "research/ai",
            "keywords": ["agent", "planning", "benchmark"],
        }
        liked = signal("new-like", "Tool agent planning", summary="An agent planning method")
        lowered = signal("new-lower", "Another benchmark", summary="Generic benchmark results")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.jsonl"
            write_events(path, events)
            apply_feedback([liked, lowered], track, path=path)

        self.assertGreater(personalization_adjustment(liked), 0)
        self.assertLess(personalization_adjustment(lowered), 0)
        self.assertGreater(adjusted_score(0.5, liked), adjusted_score(0.5, lowered))

    def test_followed_author_passes_keyword_gate_and_gets_boost(self) -> None:
        event = {
            "action": "follow_author",
            "track": "research/ai",
            "item_type": "paper",
            "item_id": "old-paper",
            "target_author": "Ada Lovelace",
        }
        candidate = signal("new-paper", "Unmatched title", authors=["Ada Lovelace"])
        track = {"name": "ai", "_reference": "research/ai", "keywords": ["serving"]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.jsonl"
            write_events(path, [event])
            with patch.dict(os.environ, {"OMNISOURCE_FEEDBACK_EVENTS": str(path)}):
                ranked = curator.rank([candidate], track)

        self.assertEqual(ranked, [candidate])
        self.assertTrue(is_followed_author_signal(candidate))
        self.assertGreater(personalization_adjustment(candidate), 0.2)

    def test_topic_feedback_is_reapplied_after_topic_classification(self) -> None:
        event = {
            "action": "like",
            "track": "research/ai",
            "item_type": "paper",
            "item_id": "old-paper",
            "topic": "Systems > Inference",
        }
        candidate = signal("new-paper", "Different wording", topic="Systems > Inference")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.jsonl"
            write_events(path, [event])
            apply_feedback([candidate], {"name": "ai", "_reference": "research/ai"}, path=path)

        self.assertGreater(personalization_adjustment(candidate), 0)

    def test_report_renders_one_compact_selector_and_imports_checked_action(self) -> None:
        item = signal("p1", "Useful systems paper", authors=["Ada Lovelace", "Grace Hopper"])
        track = {
            "name": "ai",
            "_reference": "research/ai",
            "keywords": ["systems"],
            "sources": ["arxiv"],
            "output": {"language": "中文"},
        }
        url = feedback_selector_url(item, track, repository="alice/OmniSource", language="中文")
        query = parse_qs(urlparse(url).query)
        body = query["body"][0]
        checked = body.replace("- [ ] `follow_author:1`", "- [x] `follow_author:1`")
        issue = {
            "number": 7,
            "author": {"login": "alice"},
            "body": checked,
            "createdAt": "2026-07-29T10:00:00Z",
            "updatedAt": "2026-07-29T10:00:00Z",
        }
        events = feedback_events_from_issues([issue], "alice")
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "alice/OmniSource"}):
            markdown = editor.render({"paper": [item]}, track, "2026-07-29")

        self.assertIn(ISSUE_MARKER_V2, body)
        self.assertLess(len(url), 3000)
        self.assertEqual(events[0]["action"], "follow_author")
        self.assertEqual(events[0]["target_author"], "Grace Hopper")
        self.assertEqual(markdown.count("issues/new?"), 1)
        self.assertIn("喜欢 / 忽略 / 降低此类 / 关注作者", markdown)

    def test_multiple_checked_actions_are_rejected(self) -> None:
        item = signal("p1", "Paper")
        track = {"name": "ai", "_reference": "research/ai", "output": {"language": "English"}}
        url = feedback_selector_url(item, track, repository="alice/OmniSource", language="English")
        body = parse_qs(urlparse(url).query)["body"][0]
        body = body.replace("- [ ] `like`", "- [x] `like`")
        body = body.replace("- [ ] `ignore`", "- [x] `ignore`")
        issue = {
            "number": 8,
            "author": {"login": "alice"},
            "body": body,
            "createdAt": "2026-07-29T10:00:00Z",
            "updatedAt": "2026-07-29T10:00:00Z",
        }

        self.assertEqual(feedback_events_from_issues([issue], "alice"), [])

    def test_large_report_with_feedback_controls_stays_below_issue_body_limit(self) -> None:
        items = [
            Signal(
                id=f"blog-{index}",
                title=f"AI startup market signal {index} with a representative product launch",
                url=f"https://example.com/blog-{index}",
                type="blog",
                published_at=dt.datetime(2026, 7, 29, tzinfo=dt.timezone.utc),
                summary=(
                    "A representative summary describing the company, product, funding, "
                    "market evidence, and why the signal could matter to an entrepreneur."
                ),
                sources=["rss"],
                topic="Product",
            )
            for index in range(50)
        ]
        track = {
            "name": "entrepreneur",
            "_reference": "venture/entrepreneur",
            "keywords": ["AI", "startup", "product", "funding", "market"],
            "sources": ["rss"],
            "topics": ["Product"],
            "output": {"language": "中文"},
        }
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "alice/OmniSource"}):
            markdown = editor.render({"blog": items}, track, "2026-07-29")

        self.assertEqual(markdown.count("issues/new?"), 50)
        self.assertLess(len(markdown.encode("utf-8")), 65_536)

    def test_daily_and_weekly_workflows_import_feedback_before_reporting(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for name in ("daily-issue-report.yml", "weekly-issue-report.yml"):
            workflow = (root / ".github" / "workflows" / name).read_text(encoding="utf-8")
            profile_step = workflow.index("Build personalization profile from owner feedback")
            report_step = workflow.index("Generate one")
            self.assertLess(profile_step, report_step)
            self.assertIn("gh issue list", workflow)
            self.assertIn("import-feedback-issues", workflow)
            self.assertIn("summarize-feedback", workflow)
            self.assertIn("OMNISOURCE_FEEDBACK_OWNER", workflow)


if __name__ == "__main__":
    unittest.main()
