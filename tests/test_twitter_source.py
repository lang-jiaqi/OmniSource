from __future__ import annotations

import json
import subprocess
import unittest
from unittest.mock import patch

from omnisource.canonical import canonicalize
from omnisource.sources.twitter import TwitterSource


class _Response:
    def __init__(self, data: list[dict]) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        return None

    def json(self) -> list[dict]:
        return self._data


class TwitterSourceTests(unittest.TestCase):
    def test_opencli_collects_search_and_fixed_account_timelines(self) -> None:
        track = {
            "days": 3,
            "twitter": {
                "mode": "opencli",
                "profile": "work",
                "max_results": 10,
                "search": {
                    "queries": ["LLM serving"],
                    "product": "live",
                    "language": "en",
                    "has": "links",
                    "exclude_replies": True,
                    "exclude_retweets": True,
                    "max_results_per_query": 5,
                },
                "accounts": {
                    "handles": ["@karpathy"],
                    "max_results_per_handle": 4,
                    "page_delay": 1,
                    "include_retweets": False,
                },
            },
        }
        search_rows = [{
            "id": "1", "author": "alice", "text": "New https://github.com/org/repo",
            "created_at": "2099-07-12T00:00:00Z", "likes": "1.2K",
            "views": "8K", "url": "https://x.com/alice/status/1",
        }]
        account_rows = [
            {
                "id": "2", "author": "karpathy", "text": "A useful thread",
                "created_at": "2099-07-12T00:00:00Z", "likes": 50,
                "retweets": 4, "replies": 3, "is_retweet": False,
                "url": "https://x.com/karpathy/status/2",
            },
            {
                "id": "3", "author": "someone", "text": "reshared",
                "created_at": "2099-07-12T00:00:00Z", "is_retweet": True,
                "url": "https://x.com/someone/status/3",
            },
        ]

        def run(command, **kwargs):
            rows = search_rows if command[2] == "search" else account_rows
            return subprocess.CompletedProcess(command, 0, json.dumps(rows), "")

        with patch("omnisource.sources.twitter.shutil.which", return_value="/opt/homebrew/bin/opencli"):
            with patch("omnisource.sources.twitter.subprocess.run", side_effect=run) as execute:
                signals = TwitterSource().fetch(track)

        self.assertEqual([signal.url for signal in signals], [
            "https://x.com/alice/status/1",
            "https://x.com/karpathy/status/2",
        ])
        self.assertEqual(signals[0].popularity, 1200)
        self.assertEqual(signals[0].extra["views"], 8000)
        self.assertEqual(signals[0].extra["collector"], "opencli")
        search_command = execute.call_args_list[0].args[0]
        self.assertEqual(search_command[:3], ["opencli", "twitter", "search"])
        self.assertIn("lang:en", search_command[3])
        self.assertIn("since:", search_command[3])
        self.assertIn("-filter:replies", search_command[3])
        self.assertIn("-filter:nativeretweets", search_command[3])
        self.assertIn("--has", search_command)
        self.assertEqual(execute.call_args_list[0].kwargs["env"]["OPENCLI_PROFILE"], "work")
        account_command = execute.call_args_list[1].args[0]
        self.assertEqual(account_command[:4], ["opencli", "twitter", "tweets", "karpathy"])

    def test_opencli_supports_legacy_queries_and_handles(self) -> None:
        track = {
            "twitter": {
                "mode": "opencli",
                "queries": ["agents"],
                "handles": ["fchollet"],
                "max_results": 5,
            }
        }
        with patch("omnisource.sources.twitter.shutil.which", return_value="/usr/local/bin/opencli"):
            with patch("omnisource.sources.twitter.subprocess.run") as execute:
                execute.return_value = subprocess.CompletedProcess([], 0, "[]", "")
                signals = TwitterSource().fetch(track)

        self.assertEqual(signals, [])
        self.assertEqual(execute.call_count, 2)
        self.assertEqual(execute.call_args_list[0].args[0][2], "search")
        self.assertEqual(execute.call_args_list[1].args[0][2], "tweets")

    def test_opencli_honors_configured_command_prefix(self) -> None:
        track = {
            "twitter": {
                "mode": "opencli",
                "search": {"queries": ["agents"]},
            }
        }
        with patch.dict("os.environ", {"OPENCLI_COMMAND": "custom-opencli --runtime"}, clear=True):
            with patch("omnisource.sources.twitter.shutil.which", return_value="/usr/local/bin/custom-opencli"):
                with patch("omnisource.sources.twitter.subprocess.run") as execute:
                    execute.return_value = subprocess.CompletedProcess([], 0, "[]", "")
                    TwitterSource().fetch(track)

        self.assertEqual(
            execute.call_args_list[0].args[0][:4],
            ["custom-opencli", "--runtime", "twitter", "search"],
        )

    def test_opencli_isolates_a_failed_command(self) -> None:
        track = {
            "twitter": {
                "mode": "opencli",
                "search": {"queries": ["bad", "good"]},
            }
        }

        def run(command, **kwargs):
            if command[3] == "bad":
                raise subprocess.CalledProcessError(1, command)
            return subprocess.CompletedProcess(command, 0, json.dumps([{
                "id": "4", "author": "bob", "text": "works", "created_at": "2099-01-01T00:00:00Z",
                "url": "https://x.com/bob/status/4",
            }]), "")

        with patch("omnisource.sources.twitter.shutil.which", return_value="opencli"):
            with patch("omnisource.sources.twitter.subprocess.run", side_effect=run):
                with patch("builtins.print"):
                    signals = TwitterSource().fetch(track)

        self.assertEqual([signal.id for signal in signals], ["https://x.com/bob/status/4"])

    def test_apify_uses_danek_actor_and_normalizes_tweets(self) -> None:
        track = {
            "twitter": {
                "mode": "apify",
                "queries": ["LLM serving"],
                "handles": ["OpenAI"],
                "tweet_language": "en",
                "query_suffix": "filter:links",
                "max_results": 5,
            }
        }
        payload = [
            {
                "tweet_id": "1",
                "screen_name": "alice",
                "text": "New paper https://arxiv.org/abs/2607.00001",
                "user_info": {"screen_name": "alice"},
                "favorites": 12,
                "created_at": "2026-07-06T00:00:00Z",
            }
        ]

        with patch.dict("os.environ", {"APIFY_TOKEN": "test-token"}, clear=True):
            with patch("omnisource.sources.twitter.requests.post", return_value=_Response(payload)) as post:
                signals = TwitterSource().fetch(track)

        self.assertEqual(len(signals), 2)
        self.assertEqual(signals[0].authors, ["@alice"])
        self.assertEqual(signals[0].url, "https://x.com/alice/status/1")
        self.assertEqual(signals[0].popularity, 12)
        urls = [call.args[0] for call in post.call_args_list]
        self.assertTrue(all("danek~twitter-scraper" in url for url in urls))
        request_payloads = [call.kwargs["json"] for call in post.call_args_list]
        self.assertEqual(request_payloads[0]["query"], '("LLM serving") filter:links lang:en')
        self.assertEqual(request_payloads[0]["max_posts"], 5)
        self.assertEqual(request_payloads[1]["query"], "(from:OpenAI) filter:links lang:en")
        self.assertEqual(request_payloads[1]["max_posts"], 5)

    def test_apify_ignores_demo_and_no_result_rows(self) -> None:
        track = {"twitter": {"mode": "apify", "queries": ["LLM serving"]}}
        payload = [{"demo": True}, {"noResults": True}]

        with patch.dict("os.environ", {"APIFY_TOKEN": "test-token"}, clear=True):
            with patch("omnisource.sources.twitter.requests.post", return_value=_Response(payload)):
                with patch("builtins.print"):
                    signals = TwitterSource().fetch(track)

        self.assertEqual(signals, [])

    def test_apify_expanded_urls_can_canonicalize_tweets(self) -> None:
        track = {"twitter": {"mode": "apify", "queries": ["reasoning model"], "max_results": 5}}
        payload = [
            {
                "tweet_id": "2",
                "screen_name": "biglab",
                "text": "Interesting paper https://t.co/short",
                "entities": {
                    "urls": [
                        {
                            "url": "https://t.co/short",
                            "expanded_url": "https://arxiv.org/abs/2607.00001",
                        }
                    ]
                },
                "favorite_count": 7,
                "created_at": "2026-07-06T00:00:00Z",
            }
        ]

        with patch.dict("os.environ", {"APIFY_TOKEN": "test-token"}, clear=True):
            with patch("omnisource.sources.twitter.requests.post", return_value=_Response(payload)):
                signals = TwitterSource().fetch(track)

        self.assertEqual(len(signals), 1)
        self.assertIn("https://arxiv.org/abs/2607.00001", signals[0].summary)
        self.assertEqual(signals[0].extra["reference_urls"], ["https://arxiv.org/abs/2607.00001"])

        canonicalize(signals[0])
        self.assertEqual(signals[0].id, "2607.00001")

    def test_apify_resolves_tco_links_when_expanded_url_is_missing(self) -> None:
        track = {"twitter": {"mode": "apify", "queries": ["reasoning model"], "max_results": 5}}
        payload = [
            {
                "tweet_id": "3",
                "screen_name": "biglab",
                "text": "High-signal paper https://t.co/short",
                "favorite_count": 900,
                "created_at": "2026-07-06T00:00:00Z",
            }
        ]

        with patch.dict("os.environ", {"APIFY_TOKEN": "test-token"}, clear=True):
            with patch("omnisource.sources.twitter.requests.post", return_value=_Response(payload)):
                with patch("omnisource.sources.twitter.requests.head") as head:
                    head.return_value.url = "https://huggingface.co/papers/2607.00002"
                    signals = TwitterSource().fetch(track)

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].extra["reference_urls"], ["https://huggingface.co/papers/2607.00002"])

        canonicalize(signals[0])
        self.assertEqual(signals[0].id, "2607.00002")


if __name__ == "__main__":
    unittest.main()
