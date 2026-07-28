from __future__ import annotations

import datetime as dt
import unittest
from unittest.mock import patch

from omnisource.agents.analyst import Analyst
from omnisource.agents.editor import build_context
from omnisource.models import Signal
from omnisource.topic_taxonomy import flatten_topics, match_topic


class FakeProvider:
    model = "fake"

    def __init__(self, topic: str):
        self.topic = topic
        self.system = ""

    def complete_json(self, system: str, user: str) -> dict:
        self.system = system
        return {
            "relevance": 0.9,
            "novelty": 0.7,
            "i18n": {
                "zh": {
                    "why_it_matters": "它让研究者更容易判断是否值得跟进。",
                },
                "en": {
                    "why_it_matters": "It helps researchers decide whether to follow up.",
                },
            },
            "read_priority": "high",
            "topic": self.topic,
        }


def make_signal() -> Signal:
    return Signal(
        id="paper",
        title="A useful paper",
        url="https://example.com/paper",
        type="paper",
        published_at=dt.datetime(2026, 7, 3, tzinfo=dt.timezone.utc),
        summary="A method for attention and reasoning.",
        sources=["test"],
    )


class TopicTaxonomyTests(unittest.TestCase):
    def test_flatten_topics_supports_flat_and_nested_shapes(self) -> None:
        self.assertEqual(flatten_topics(["model architecture", "evaluation"]), [
            "model architecture",
            "evaluation",
        ])

        topics = [
            {
                "name": "模型与训练方法",
                "children": [
                    {
                        "name": "架构设计",
                        "children": [
                            "Transformer / attention variants",
                            "diffusion / generative modeling",
                        ],
                    }
                ],
            }
        ]

        self.assertEqual(flatten_topics(topics), [
            "模型与训练方法 > 架构设计 > Transformer / attention variants",
            "模型与训练方法 > 架构设计 > diffusion / generative modeling",
        ])

    def test_match_topic_normalizes_spacing_and_case(self) -> None:
        leaves = ["Systems > Inference > KV cache"]

        self.assertEqual(match_topic("systems> inference > kv cache", leaves), leaves[0])

    def test_analyst_prompts_for_leaf_paths_and_records_matched_topic(self) -> None:
        topics = [
            {
                "name": "模型与训练方法",
                "children": [
                    {"name": "架构设计", "children": ["Transformer / attention variants"]},
                ],
            }
        ]
        leaf = "模型与训练方法 > 架构设计 > Transformer / attention variants"
        provider = FakeProvider(leaf)
        signal = make_signal()

        Analyst(provider).analyze(signal, {
            "name": "test-track",
            "description": "demo",
            "topics": topics,
            "output": {"language": "中文", "languages": ["中文", "English"]},
        })

        self.assertIn("taxonomy leaf path", provider.system)
        self.assertIn(leaf, provider.system)
        self.assertEqual(signal.topic, leaf)
        self.assertEqual(signal.why_it_matters, "它让研究者更容易判断是否值得跟进。")
        self.assertEqual(signal.extra["i18n"]["en"]["why_it_matters"], "It helps researchers decide whether to follow up.")

    def test_analyst_includes_repository_owner_feedback_summary(self) -> None:
        provider = FakeProvider("other")
        with patch(
            "omnisource.agents.analyst.feedback_prompt_clause",
            return_value="\n<feedback_memory>Prefer deployment evidence.</feedback_memory>",
        ):
            Analyst(provider).analyze(make_signal(), {
                "name": "test-track",
                "description": "demo",
                "output": {"language": "English"},
            })

        self.assertIn("feedback_memory", provider.system)
        self.assertIn("deployment evidence", provider.system)

    def test_editor_clusters_by_hierarchical_leaf_path(self) -> None:
        signal = make_signal()
        signal.topic = "模型与训练方法 > 架构设计 > Transformer / attention variants"
        context = build_context(
            {"paper": [signal]},
            {
                "name": "test-track",
                "sources": ["test"],
                "topics": [{"name": "模型与训练方法", "children": ["架构设计"]}],
                "output": {"language": "中文"},
            },
            "2026-07-03",
            "Daily",
        )

        self.assertEqual(
            context["sections"][0]["groups"][0]["topic"],
            "模型与训练方法 > 架构设计 > Transformer / attention variants",
        )


if __name__ == "__main__":
    unittest.main()
