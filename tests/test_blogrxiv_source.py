from __future__ import annotations

import datetime as dt
import json
import unittest
from unittest.mock import patch

from omnisource.sources.blogrxiv import BlogrXivSource


class BlogrXivSourceTests(unittest.TestCase):
    def test_fetches_published_recent_entries_and_preserves_curated_context(self) -> None:
        config = "const config = { url: 'https://supabase.example', publishableKey: 'public-key' };"
        rows = [
            {
                "id": "fresh",
                "title": "Efficient Inference Notes",
                "excerpt": "A careful discussion of serving tradeoffs.",
                "author": "Ada Lovelace",
                "category": "Efficient AI",
                "tags": ["Serving", "KV Cache"],
                "read_time": "10 min read",
                "publish_date": "2026-07-22",
                "source_name": "Research Lab",
                "url": "https://example.com/efficient-inference",
                "status": "published",
            },
            {
                "id": "old",
                "title": "Old Note",
                "excerpt": "Outside the lookback window.",
                "publish_date": "2026-06-01",
                "url": "https://example.com/old",
                "status": "published",
            },
        ]

        with patch("omnisource.sources.blogrxiv.cached_get", side_effect=[config, json.dumps(rows)]):
            signals = BlogrXivSource(now=dt.datetime(2026, 7, 23, tzinfo=dt.timezone.utc)).fetch({"blogrxiv_days": 7})

        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal.id, "https://example.com/efficient-inference")
        self.assertEqual(signal.sources, ["blogrxiv"])
        self.assertEqual(signal.authors, ["Ada Lovelace"])
        self.assertIn("Category: Efficient AI", signal.summary)
        self.assertIn("Tags: Serving, KV Cache", signal.summary)
        self.assertEqual(signal.extra["blogrxiv_category"], "Efficient AI")
        self.assertEqual(signal.extra["read_time"], "10 min read")

    def test_disabled_source_does_not_fetch_public_config(self) -> None:
        with patch("omnisource.sources.blogrxiv.cached_get") as fetch:
            self.assertEqual(BlogrXivSource().fetch({"blogrxiv": {"enabled": False}}), [])
        fetch.assert_not_called()

    def test_calendar_day_mode_only_keeps_today_entries(self) -> None:
        config = "const config = { url: 'https://supabase.example', publishableKey: 'public-key' };"
        rows = [
            {"id": "today", "title": "Today", "publish_date": "2026-07-23", "url": "https://example.com/today"},
            {"id": "yesterday", "title": "Yesterday", "publish_date": "2026-07-22", "url": "https://example.com/yesterday"},
        ]

        with patch("omnisource.sources.blogrxiv.cached_get", side_effect=[config, json.dumps(rows)]):
            signals = BlogrXivSource(now=dt.datetime(2026, 7, 23, 12, tzinfo=dt.timezone.utc)).fetch({
                "blogrxiv_days": 1,
                "blogrxiv_calendar_days": True,
            })

        self.assertEqual([signal.title for signal in signals], ["Today"])


if __name__ == "__main__":
    unittest.main()
