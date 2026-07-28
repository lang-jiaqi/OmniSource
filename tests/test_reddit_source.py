from __future__ import annotations

import json
import subprocess
import unittest
from unittest.mock import patch

from omnisource.sources.reddit import RedditSource


class RedditSourceTests(unittest.TestCase):
    def test_opencli_collects_search_and_fixed_subreddits(self) -> None:
        track = {
            "days": 7,
            "reddit": {
                "mode": "opencli",
                "profile": "work",
                "max_results": 10,
                "summary_max_chars": 12,
                "search": {
                    "queries": ["LLM agents"],
                    "sort": "new",
                    "max_results_per_query": 5,
                },
                "subreddits": {
                    "names": ["r/Codex", "ClaudeAI"],
                    "sort": "new",
                    "max_results_per_subreddit": 4,
                },
            },
        }
        search_rows = [{
            "id": "a", "title": "New agent runtime", "subreddit": "r/LocalLLaMA",
            "author": "alice", "score": "12", "comments": "3",
            "url": "https://www.reddit.com/r/LocalLLaMA/comments/a/new_agent_runtime/",
            "created_utc": 4102444800,
            "selftext": "Details", "url_overridden_by_dest": "https://github.com/org/repo",
        }]
        subreddit_rows = [{
            "id": "b", "title": "Codex workflow", "subreddit": "r/Codex",
            "author": "bob", "upvotes": 21, "comments": 8,
            "url": "https://www.reddit.com/r/Codex/comments/b/codex_workflow/",
            "created_utc": 4102444800, "selftext": "A useful workflow",
        }]

        def run(command, **kwargs):
            rows = search_rows if command[2] == "search" else subreddit_rows
            return subprocess.CompletedProcess(command, 0, json.dumps(rows), "")

        with patch("omnisource.sources.reddit.shutil.which", return_value="/opt/homebrew/bin/opencli"):
            with patch("omnisource.sources.reddit.subprocess.run", side_effect=run) as execute:
                signals = RedditSource().fetch(track)

        self.assertEqual(len(signals), 2)
        self.assertEqual(signals[0].id, "https://github.com/org/repo")
        self.assertEqual(signals[0].authors, ["u/alice"])
        self.assertEqual(signals[0].extra["subreddit"], "r/LocalLLaMA")
        self.assertEqual(signals[0].extra["collector"], "opencli")
        self.assertTrue(signals[0].summary.endswith("Details"))
        self.assertEqual(signals[1].popularity, 21)
        self.assertEqual(execute.call_args_list[0].args[0][:3], ["opencli", "reddit", "search"])
        self.assertIn("--time", execute.call_args_list[0].args[0])
        self.assertEqual(execute.call_args_list[0].kwargs["env"]["OPENCLI_PROFILE"], "work")
        self.assertEqual(execute.call_args_list[1].args[0][:4], ["opencli", "reddit", "subreddit", "Codex"])
        self.assertEqual(execute.call_args_list[2].args[0][:4], ["opencli", "reddit", "subreddit", "ClaudeAI"])

    def test_opencli_uses_legacy_subreddit_config_by_default(self) -> None:
        track = {"reddit_subreddits": ["r/Codex"], "reddit_top": 25}
        with patch("omnisource.sources.reddit.shutil.which", return_value="opencli"):
            with patch("omnisource.sources.reddit.subprocess.run") as execute:
                execute.return_value = subprocess.CompletedProcess([], 0, "[]", "")
                signals = RedditSource().fetch(track)

        self.assertEqual(signals, [])
        command = execute.call_args.args[0]
        self.assertEqual(command[:4], ["opencli", "reddit", "subreddit", "Codex"])

    def test_opencli_uses_configured_bridge_command(self) -> None:
        track = {"reddit_subreddits": ["r/Codex"]}
        bridge = "/Applications/OpenCLIApp.app/Contents/Resources/node_modules/node/bin/node"
        main = "/Applications/OpenCLIApp.app/Contents/Resources/node_modules/@jackwener/opencli/dist/src/main.js"
        with patch.dict("os.environ", {"OPENCLI_COMMAND": f"{bridge} {main}"}, clear=False):
            with patch("omnisource.sources.reddit.subprocess.run") as execute:
                execute.return_value = subprocess.CompletedProcess([], 0, "[]", "")
                signals = RedditSource().fetch(track)

        self.assertEqual(signals, [])
        command = execute.call_args.args[0]
        self.assertEqual(command[:6], [bridge, main, "reddit", "subreddit", "Codex", "--sort"])

    def test_opencli_deduplicates_and_isolates_failed_commands(self) -> None:
        track = {
            "reddit": {
                "search": {"queries": ["bad", "good"]},
                "subreddits": {"enabled": False},
            }
        }
        row = {
            "id": "c", "title": "Good post", "author": "carol", "score": 7,
            "url": "https://www.reddit.com/r/Codex/comments/c/good_post/",
            "created_utc": 4102444800,
        }

        def run(command, **kwargs):
            if command[3] == "bad":
                raise subprocess.CalledProcessError(1, command)
            return subprocess.CompletedProcess(command, 0, json.dumps([row, row]), "")

        with patch("omnisource.sources.reddit.shutil.which", return_value="opencli"):
            with patch("omnisource.sources.reddit.subprocess.run", side_effect=run):
                with patch("builtins.print"):
                    signals = RedditSource().fetch(track)

        self.assertEqual(len(signals), 1)

    def test_oauth_mode_still_skips_without_credentials(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with patch("builtins.print") as output:
                signals = RedditSource().fetch({"reddit": {"mode": "oauth"}})

        self.assertEqual(signals, [])
        self.assertIn("reddit(oauth)", output.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
