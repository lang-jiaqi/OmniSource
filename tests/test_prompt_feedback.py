from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from omnisource.prompt_feedback import (
    feedback_prompt_clause,
    load_feedback_events,
    load_prompt_feedback,
    render_preference_summary,
    write_preference_summary,
)


class PromptFeedbackTests(unittest.TestCase):
    def test_loads_compact_preference_summary_for_prompt_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preference_summary.md"
            path.write_text(
                "# OmniSource Preference Summary\n\n"
                "## Stable Preferences\n\n"
                "- Prefer paper recommendations for ai-infra when: deployment evidence is strong.\n",
                encoding="utf-8",
            )

            self.assertIn("deployment evidence", load_prompt_feedback(path))
            clause = feedback_prompt_clause(path)

        self.assertIn("<feedback_memory>", clause)
        self.assertIn("User preference summary", clause)
        self.assertIn("stable preferences", clause)
        self.assertIn("Do not copy it verbatim", clause)

    def test_ignores_empty_preference_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preference_summary.md"
            path.write_text(
                "# OmniSource Preference Summary\n\nNo learned preferences yet.\n",
                encoding="utf-8",
            )

            self.assertEqual(load_prompt_feedback(path), "")
            self.assertEqual(feedback_prompt_clause(path), "")

    def test_loads_feedback_events_from_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback_events.jsonl"
            events = [
                {
                    "created_at": "2026-07-08T08:00:00Z",
                    "track": "ai-infra",
                    "item_type": "paper",
                    "item_id": "2607.1",
                    "title": "Useful Systems Paper",
                    "sources": "arxiv, twitter",
                    "vote": "up",
                    "reason": "Real serving workload and deployment details.",
                },
                {"vote": "down", "reason": ""},
            ]
            path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")

            loaded = load_feedback_events(path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["vote"], "up")
        self.assertEqual(loaded[0]["reason"], "Real serving workload and deployment details.")

    def test_renders_preference_summary_from_recent_reasons(self) -> None:
        events = [
            {
                "created_at": "2026-07-08T09:00:00Z",
                "track": "ai-infra",
                "item_type": "paper",
                "title": "Too Generic",
                "vote": "down",
                "reason": "Only generic LLM benchmark results.",
            },
            {
                "created_at": "2026-07-08T10:00:00Z",
                "track": "ai-infra",
                "item_type": "repo",
                "title": "Fresh Kernel Repo",
                "vote": "up",
                "reason": "Fresh implementation with clear kernel-level contribution.",
            },
        ]

        summary = render_preference_summary(events, max_preferences=10)

        self.assertIn("Source feedback events: 2", summary)
        self.assertIn("Prefer repo recommendations", summary)
        self.assertIn("Avoid paper recommendations", summary)
        self.assertLess(summary.index("Fresh implementation"), summary.index("Only generic"))

    def test_write_preference_summary_returns_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            event_path = Path(tmp) / "feedback_events.jsonl"
            output_path = Path(tmp) / "preference_summary.md"
            event_path.write_text(
                json.dumps({
                    "track": "ai-algorithm",
                    "type": "paper",
                    "title": "Reasoning Paper",
                    "vote": "recommended",
                    "reason": "Strong reasoning method and convincing ablation.",
                }),
                encoding="utf-8",
            )

            target, event_count, preference_count = write_preference_summary(event_path, output_path)

            self.assertEqual(target, output_path)
            self.assertEqual(event_count, 1)
            self.assertEqual(preference_count, 1)
            self.assertIn("Strong reasoning method", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
