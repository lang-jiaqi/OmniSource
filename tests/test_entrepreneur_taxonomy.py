from __future__ import annotations

import datetime as dt
import unittest

from omnisource.agents.editor import build_context
from omnisource.entrepreneur_taxonomy import classify_entrepreneur
from omnisource.models import Signal


class EntrepreneurTaxonomyTests(unittest.TestCase):
    def test_classifies_business_events_and_report_topics(self) -> None:
        cases = (
            (
                "AI startup raises a Series A",
                "The company will expand its product.",
                "融资",
                "资本与公司 > 融资与投资",
            ),
            (
                "AI company announces acquisition",
                "The acquisition follows a funding round.",
                "融资",
                "资本与公司 > 并购与公司动作",
            ),
            (
                "AI startup launches a developer API",
                "The product is available today.",
                "产品",
                "产品与市场 > 产品发布与定价",
            ),
            (
                "AI startup founders join forces",
                "The founder team is building a new company.",
                "团队",
                "团队与招聘 > 创业团队与联合创始人",
            ),
            (
                "AI company announces hiring plans",
                "The team is recruiting engineers.",
                "团队",
                "团队与招聘 > 招聘与组织变化",
            ),
            (
                "Enterprise customer adopts an AI platform",
                "The partnership expands deployment.",
                "市场",
                "产品与市场 > 企业采用与开发者生态",
            ),
        )
        for title, summary, event_type, topic in cases:
            with self.subTest(title=title):
                classification = classify_entrepreneur(title, summary)
                self.assertEqual(classification.event_type, event_type)
                self.assertEqual(classification.topic, topic)

    def test_report_gets_topics_without_an_llm(self) -> None:
        signal = Signal(
            id="startup",
            title="AI startup launches a developer API",
            url="https://example.com/startup",
            type="blog",
            published_at=dt.datetime(2026, 7, 29, tzinfo=dt.timezone.utc),
            summary="The product is available today.",
            sources=["test"],
        )
        context = build_context(
            {"blog": [signal]},
            {
                "name": "entrepreneur",
                "sources": ["rss"],
                "topics": [
                    {"name": "资本与公司", "children": ["融资与投资", "并购与公司动作"]},
                    {"name": "产品与市场", "children": ["产品发布与定价", "企业采用与开发者生态"]},
                    {"name": "团队与招聘", "children": ["创业团队与联合创始人", "招聘与组织变化"]},
                ],
                "output": {"language": "中文"},
            },
            "2026-07-29",
            "Daily",
        )

        self.assertEqual(signal.topic, "产品与市场 > 产品发布与定价")
        self.assertEqual(
            context["sections"][0]["groups"][0]["topic"],
            "产品与市场 > 产品发布与定价",
        )


if __name__ == "__main__":
    unittest.main()
