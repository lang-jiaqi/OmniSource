from __future__ import annotations

import datetime as dt
import unittest

from omnisource.agents import curator
from omnisource.models import Signal
from omnisource.tool_scoring import aggregate_tool_score, score_tool


class ToolScoringTests(unittest.TestCase):
    def test_tool_score_has_the_six_shared_dimensions(self) -> None:
        signal = Signal(
            id="tool",
            title="example/agent-browser",
            url="https://github.com/example/agent-browser",
            type="repo",
            published_at=dt.datetime(2026, 7, 25, tzinfo=dt.timezone.utc),
            summary="An open-source browser automation agent and MCP workflow tool.",
            sources=["github"],
            popularity=120,
            extra={
                "total_stars": 120,
                "trending_stars": 20,
                "star_velocity": 5,
                "homepage": "https://example.com",
                "license": "MIT",
                "created_at": "2026-07-20T00:00:00Z",
            },
        )

        category, evaluation, aggregate = score_tool(signal, dt.date(2026, 7, 27))

        self.assertEqual(category, "automation")
        self.assertEqual(
            set(evaluation),
            {"relevance", "practical_value", "freshness", "usability", "credibility", "differentiation"},
        )
        self.assertTrue(all(1 <= value <= 5 for value in evaluation.values()))
        self.assertEqual(aggregate, aggregate_tool_score(evaluation))

    def test_tool_track_ranks_by_shared_score_and_keeps_evaluation(self) -> None:
        strong = Signal(
            id="strong",
            title="example/new-agent-tool",
            url="https://github.com/example/new-agent-tool",
            type="repo",
            published_at=dt.datetime(2026, 7, 26, tzinfo=dt.timezone.utc),
            summary="A new open-source AI coding agent with MCP and browser workflow support.",
            sources=["github"],
            popularity=200,
            extra={"total_stars": 200, "trending_stars": 30, "license": "MIT"},
        )
        weak = Signal(
            id="weak",
            title="old-tool",
            url="https://github.com/example/old-tool",
            type="repo",
            published_at=dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc),
            summary="A generic tool.",
            sources=["github"],
            popularity=1,
            extra={"created_at": "2020-01-01T00:00:00Z"},
        )
        strong.keyword_hits = weak.keyword_hits = 1

        ranked = curator.enrich_and_rank([weak, strong], {"tool_radar": True}, analyst=None)

        self.assertEqual(ranked[0].id, "strong")
        self.assertIn("tool_evaluation", ranked[0].extra)


if __name__ == "__main__":
    unittest.main()
