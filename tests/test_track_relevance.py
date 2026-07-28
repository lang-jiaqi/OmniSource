from __future__ import annotations

import datetime as dt
import unittest

from omnisource.agents import curator
from omnisource.models import Signal


def make_paper(signal_id: str, title: str, summary: str, categories: list[str]) -> Signal:
    return Signal(
        id=signal_id,
        title=title,
        url=f"https://arxiv.org/abs/{signal_id}",
        type="paper",
        published_at=dt.datetime(2026, 7, 3, tzinfo=dt.timezone.utc),
        summary=summary,
        sources=["arxiv"],
        extra={"arxiv_categories": categories, "primary_arxiv_category": categories[0]},
    )


class TrackRelevanceTests(unittest.TestCase):
    def test_infra_filter_prioritizes_systems_categories_and_anchors(self) -> None:
        track = {
            "keywords": ["inference", "serving", "cluster"],
            "relevance_filter": {
                "paper": {
                    "preferred_arxiv_categories": ["cs.DC", "cs.OS"],
                    "broad_arxiv_categories": ["cs.AI", "cs.LG"],
                    "category_boosts": {"cs.DC": 4, "cs.OS": 3},
                    "min_anchor_hits": 1,
                    "broad_category_min_anchor_hits": 1,
                    "anchor_keywords": ["serving", "cluster", "KV cache", "scheduler"],
                }
            },
        }
        algorithm_only = make_paper(
            "algo",
            "Multi-Block Diffusion Language Models",
            "A new inference objective for diffusion language models.",
            ["cs.LG"],
        )
        serving = make_paper(
            "serving",
            "Fast LLM Serving with KV Cache Batching",
            "An inference serving system that batches KV cache updates.",
            ["cs.LG"],
        )
        distributed = make_paper(
            "distributed",
            "Cluster Scheduling for Large AI Training",
            "A cluster scheduler for distributed training workloads.",
            ["cs.DC"],
        )

        ranked = curator.rank([algorithm_only, serving, distributed], track)

        self.assertEqual([signal.id for signal in ranked], ["distributed", "serving"])
        self.assertEqual(ranked[0].extra["track_relevance"]["arxiv_category_hits"], ["cs.DC"])
        self.assertIn("KV cache", ranked[1].extra["track_relevance"]["anchor_hits"])

    def test_curated_blog_fallback_can_survive_without_keyword_hit(self) -> None:
        track = {
            "keywords": ["serving"],
            "relevance_filter": {"blog": {"allow_keyword_fallback": True}},
        }
        blog = Signal(
            id="blog",
            title="Systems engineering update",
            url="https://example.com/blog",
            type="blog",
            published_at=dt.datetime(2026, 7, 3, tzinfo=dt.timezone.utc),
            summary="A lab note about production reliability.",
            sources=["rss"],
        )

        ranked = curator.rank([blog], track)

        self.assertEqual([signal.id for signal in ranked], ["blog"])
        self.assertEqual(blog.keyword_hits, 0)

    def test_startup_blog_requires_an_explicit_ai_anchor(self) -> None:
        track = {
            "keywords": ["startup", "funding"],
            "relevance_filter": {
                "blog": {
                    "allow_keyword_fallback": False,
                    "min_anchor_hits": 1,
                    "anchor_keywords": ["AI", "machine learning", "LLM"],
                }
            },
        }
        non_ai = Signal(
            id="non-ai",
            title="Fintech startup raises a new round",
            url="https://example.com/non-ai",
            type="blog",
            published_at=dt.datetime(2026, 7, 3, tzinfo=dt.timezone.utc),
            summary="The company raised funding for its finance platform.",
            sources=["rss"],
        )
        ai = Signal(
            id="ai",
            title="AI startup launches a machine learning platform",
            url="https://example.com/ai",
            type="blog",
            published_at=dt.datetime(2026, 7, 3, tzinfo=dt.timezone.utc),
            summary="The company builds an LLM workflow for enterprise teams.",
            sources=["rss"],
        )

        ranked = curator.rank([non_ai, ai], track)

        self.assertEqual([signal.id for signal in ranked], ["ai"])
        self.assertIn("AI", ranked[0].extra["track_relevance"]["anchor_hits"])

    def test_short_ai_anchor_uses_word_boundaries(self) -> None:
        track = {
            "keywords": ["startup"],
            "relevance_filter": {
                "blog": {
                    "allow_keyword_fallback": False,
                    "min_anchor_hits": 1,
                    "anchor_keywords": ["AI"],
                }
            },
        }
        blog = Signal(
            id="plain",
            title="A startup raises capital",
            url="https://example.com/plain",
            type="blog",
            published_at=dt.datetime(2026, 7, 3, tzinfo=dt.timezone.utc),
            summary="A plain company update with no artificial intelligence focus.",
            sources=["rss"],
        )

        self.assertEqual(curator.rank([blog], track), [])

    def test_section_selection_respects_analysis_buffer(self) -> None:
        class CountingAnalyst:
            def __init__(self) -> None:
                self.seen: list[str] = []

            def analyze(self, signal: Signal, track: dict) -> None:
                self.seen.append(signal.id)
                signal.llm_relevance = 0.5
                signal.novelty = 0.5

        signals = [
            make_paper(f"paper-{index}", f"Paper {index}", "inference serving", ["cs.DC"])
            for index in range(5)
        ]
        analyst = CountingAnalyst()
        track = {
            "output": {"top_papers": 2, "analysis_buffer": 1},
            "ranking": {"relevance": 1.0, "novelty": 0.0, "popularity": 0.0, "code_available": 0.0},
        }

        sections = curator.select_sections(signals, track, analyst)  # type: ignore[arg-type]

        self.assertEqual(analyst.seen, ["paper-0", "paper-1", "paper-2"])
        self.assertEqual(len(sections["paper"]), 2)

    def test_section_selection_retains_candidates_for_web_personalization(self) -> None:
        signals = [
            make_paper(f"paper-{index}", f"Paper {index}", "inference serving", ["cs.DC"])
            for index in range(4)
        ]
        track = {"output": {"top_papers": 2, "analysis_buffer": 1}}

        sections, candidates = curator.select_sections_with_candidates(signals, track, analyst=None)
        merged = curator.merge_candidate_sections(sections, candidates)

        self.assertEqual(len(sections["paper"]), 2)
        self.assertEqual(len(merged["paper"]), 3)
        self.assertEqual(merged["paper"][:2], sections["paper"])


if __name__ == "__main__":
    unittest.main()
