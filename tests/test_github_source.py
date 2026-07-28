from __future__ import annotations

import datetime as dt
import json
import unittest
from unittest.mock import patch

from omnisource.sources.github import API_URL, REPO_API_URL, TRENDING_URL, GitHubSource


TRENDING_HTML = """
<article class="Box-row">
  <h2 class="h3 lh-condensed">
    <a href="/example/llm-serving-lab"> example / llm-serving-lab </a>
  </h2>
  <p class="col-9">Fast LLM serving runtime for inference clusters.</p>
  <span itemprop="programmingLanguage">Python</span>
  <span class="d-inline-block float-sm-right">42 stars today</span>
</article>
<article class="Box-row">
  <h2 class="h3 lh-condensed">
    <a href="/example/css-theme"> example / css-theme </a>
  </h2>
  <p class="col-9">A theme for personal websites.</p>
  <span itemprop="programmingLanguage">CSS</span>
  <span class="d-inline-block float-sm-right">500 stars today</span>
</article>
"""


def repo_payload(full_name: str, **overrides) -> str:
    payload = {
        "full_name": full_name,
        "html_url": f"https://github.com/{full_name}",
        "description": "Fast LLM serving runtime for inference clusters.",
        "owner": {"login": full_name.split("/")[0]},
        "created_at": "2026-06-01T00:00:00Z",
        "pushed_at": "2026-07-04T00:00:00Z",
        "stargazers_count": 1200,
        "forks_count": 80,
        "open_issues_count": 12,
        "topics": ["llm-serving", "inference"],
        "license": {"spdx_id": "MIT"},
        "homepage": "",
        "language": "Python",
    }
    payload.update(overrides)
    return json.dumps(payload)


class GitHubSourceTests(unittest.TestCase):
    def test_fetch_prefers_track_relevant_trending_repos(self) -> None:
        track = {
            "keywords": ["LLM serving", "inference"],
            "github_query": "LLM serving OR inference engine",
            "github_top": 5,
            "github_trending": True,
            "github_trending_periods": ["daily"],
            "github_fallback_search": False,
        }

        def fake_get(url, params=None, headers=None, ttl=None, timeout=None):
            if url == TRENDING_URL:
                self.assertEqual(params, {"since": "daily"})
                return TRENDING_HTML
            if url == REPO_API_URL.format(full_name="example/llm-serving-lab"):
                return repo_payload("example/llm-serving-lab")
            raise AssertionError(f"unexpected request: {url}")

        with patch("omnisource.sources.github.cached_get", side_effect=fake_get):
            signals = GitHubSource().fetch(track)

        self.assertEqual([signal.id for signal in signals], ["github:example/llm-serving-lab"])
        self.assertEqual(signals[0].popularity, 42)
        self.assertEqual(signals[0].extra["repo_discovery"], "trending")
        self.assertEqual(signals[0].extra["trending_stars"], 42)
        self.assertEqual(signals[0].extra["total_stars"], 1200)

    def test_search_fallback_excludes_old_incumbents(self) -> None:
        track = {
            "keywords": ["LLM serving", "inference"],
            "github_query": "LLM serving OR inference engine",
            "github_top": 5,
            "github_trending": False,
            "github_fallback_created_days": 120,
        }
        now = dt.datetime.now(dt.timezone.utc)
        old_popular = json.loads(repo_payload(
            "vllm-project/vllm",
            created_at=(now - dt.timedelta(days=2500)).strftime("%Y-%m-%dT00:00:00Z"),
            stargazers_count=85000,
            description="A high-throughput LLM serving and inference engine.",
        ))
        fresh_repo = json.loads(repo_payload(
            "example/new-inference-engine",
            created_at=(now - dt.timedelta(days=20)).strftime("%Y-%m-%dT00:00:00Z"),
            stargazers_count=500,
            description="A new LLM serving and inference engine.",
        ))

        def fake_get(url, params=None, headers=None, ttl=None, timeout=None):
            if url == API_URL:
                self.assertEqual(params["sort"], "stars")
                self.assertIn("created:>=", params["q"])
                return json.dumps({"items": [old_popular, fresh_repo]})
            raise AssertionError(f"unexpected request: {url}")

        with patch("omnisource.sources.github.cached_get", side_effect=fake_get):
            signals = GitHubSource().fetch(track)

        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal.id, "github:example/new-inference-engine")
        self.assertEqual(signal.extra["repo_discovery"], "fresh_search")
        self.assertEqual(signal.extra["total_stars"], 500)
        self.assertLess(signal.popularity, signal.extra["total_stars"])
        self.assertGreater(signal.extra["star_velocity"], 0)

    def test_search_fallback_compacts_long_boolean_queries(self) -> None:
        track = {
            "keywords": ["LLM serving", "inference"],
            "github_query": "a OR b OR c OR d OR e OR f OR g",
            "github_top": 5,
            "github_trending": False,
        }

        def fake_get(url, params=None, headers=None, ttl=None, timeout=None):
            if url == API_URL:
                self.assertIn("a OR b OR c OR d OR e", params["q"])
                self.assertNotIn(" OR f", params["q"])
                return json.dumps({"items": []})
            raise AssertionError(f"unexpected request: {url}")

        with patch("omnisource.sources.github.cached_get", side_effect=fake_get):
            signals = GitHubSource().fetch(track)

        self.assertEqual(signals, [])


if __name__ == "__main__":
    unittest.main()
