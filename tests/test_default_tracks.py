from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from omnisource.config import DEFAULT_TRACK, track_path, track_references
from omnisource.topic_taxonomy import flatten_topics


class DefaultTrackTests(unittest.TestCase):
    def _load_track(self, name: str) -> dict:
        with track_path(name).open(encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_default_track_is_ai_infra(self) -> None:
        self.assertEqual(DEFAULT_TRACK, "builder/ai-infra")

    def test_tracks_are_grouped_by_audience(self) -> None:
        references = track_references()
        self.assertIn("research/ai-algorithm", references)
        self.assertIn("venture/entrepreneur", references)
        self.assertIn("builder/ai-infra", references)
        self.assertNotIn("researcher/ai-algorithm", references)

    def test_public_ai_tools_track_is_a_tool_radar(self) -> None:
        track = self._load_track("builder/ai-tools")
        self.assertEqual(track["name"], "ai-tools")
        self.assertEqual(track["sources"], ["github", "hackernews", "rss", "twitter", "xiaohongshu", "zhihu"])
        self.assertEqual(track["output"]["top_papers"], 0)
        self.assertEqual(track["output"]["top_repos"], 10)
        self.assertEqual(track["output"]["top_blogs"], 10)
        self.assertTrue(track["topics"])

    def test_default_tracks_are_valid_research_directions(self) -> None:
        for name in ("ai-algorithm", "ai-infra"):
            with self.subTest(track=name):
                track = self._load_track(name)

                self.assertEqual(track["name"], name)
                self.assertTrue(track.get("display_name"))
                self.assertEqual(track["display_names"]["zh"], track["display_name"])
                self.assertTrue(track["display_names"]["en"])
                self.assertTrue(any("\u4e00" <= ch <= "\u9fff" for ch in track["description"]))
                self.assertTrue(track["descriptions"]["en"])
                self.assertEqual(track["output"]["top_papers"], 15)
                self.assertEqual(track["output"]["top_repos"], 5)
                self.assertEqual(track["output"]["top_blogs"], 5)
                self.assertEqual(track["output"]["top_social"], 5)
                self.assertEqual(track["output"]["analysis_buffer"], 0)
                self.assertEqual(track["output"]["languages"], ["中文", "English"])
                self.assertEqual(track["graph_author_enrichment_top_papers"], 15)
                self.assertEqual(track["graph_author_enrichment_timeout_seconds"], 600)
                self.assertEqual(track["graph_max_authors_per_paper"], 12)
                self.assertIn("arxiv", track["sources"])
                self.assertIn("hf_papers", track["sources"])
                self.assertIn("github", track["sources"])
                self.assertIn("hackernews", track["sources"])
                self.assertIn("blogrxiv", track["sources"])
                # Social sources are listed on every public track, but users
                # must add their own backend/account configuration to use them.
                self.assertIn("twitter", track["sources"])
                self.assertIn("xiaohongshu", track["sources"])
                self.assertIn("zhihu", track["sources"])
                self.assertTrue(track["categories"])
                self.assertTrue(track["keywords"])
                self.assertTrue(track["topics"])
                leaves = flatten_topics(track["topics"])
                self.assertGreaterEqual(len(leaves), 8)
                self.assertTrue(any(" > " in leaf for leaf in leaves))

    def test_default_tracks_match_the_two_product_pillars(self) -> None:
        algorithm = self._load_track("ai-algorithm")
        infra = self._load_track("ai-infra")

        self.assertIn("cs.AI", algorithm["categories"])
        self.assertIn("cs.LG", algorithm["categories"])
        self.assertIn("cs.DC", infra["categories"])
        self.assertIn("cs.OS", infra["categories"])
        self.assertEqual(infra["categories"][0], "cs.DC")
        self.assertIn("cs.DC", infra["relevance_filter"]["paper"]["preferred_arxiv_categories"])
        self.assertIn("serving", infra["relevance_filter"]["paper"]["anchor_keywords"])
        self.assertIn("blog", infra["quality_distill"]["fill_quota_types"])
        self.assertGreaterEqual(infra["rss_days"], 45)

    def test_builtin_tracks_use_a_public_openai_default(self) -> None:
        with (Path(__file__).resolve().parents[1] / "omnisource.yaml").open(encoding="utf-8") as handle:
            app = yaml.safe_load(handle)
        for name in track_references():
            track = self._load_track(name)
            self.assertEqual(track["llm"]["provider"], "openai", name)
            self.assertEqual(track["llm"]["model"], "gpt-4.1-mini", name)

        entrepreneur = self._load_track("venture/entrepreneur")
        self.assertIn("venture/entrepreneur", app["active_tracks"])
        self.assertIn("rss", entrepreneur["sources"])
        self.assertIn("hackernews", entrepreneur["sources"])
        self.assertEqual(entrepreneur["output"]["top_blogs"], 40)
        self.assertNotIn("github", entrepreneur["sources"])

    def test_ai_infra_keeps_ci_safe_twitter_configuration(self) -> None:
        track = self._load_track("builder/ai-infra")
        self.assertEqual(track["twitter"]["mode"], "apify")
        self.assertTrue(track["twitter"]["queries"])
        self.assertTrue(track["twitter"]["handles"])
        self.assertNotIn("creators", track.get("xiaohongshu", {}))
        self.assertNotIn("creators", track.get("zhihu", {}))


if __name__ == "__main__":
    unittest.main()
