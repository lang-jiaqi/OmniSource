from __future__ import annotations

import datetime as dt
import json
import subprocess
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from omnisource.source_evidence import source_signal_items
from omnisource.models import Signal
from omnisource.sources.xiaohongshu import XiaohongshuSource, _count
from omnisource.sources.xiaohongshu_client import OpenCLIConfig, OpenCLIError, OpenCLIXiaohongshuClient


TZ = ZoneInfo("Asia/Shanghai")


def note_id(moment: dt.datetime) -> str:
    timestamp = int(moment.astimezone(dt.timezone.utc).timestamp())
    return f"{timestamp:08x}" + "0" * 16


class _FakeClient:
    def __init__(self, rows_by_user: dict[str, object], details: dict[str, object] | None = None) -> None:
        self.rows_by_user = rows_by_user
        self.details = details or {}
        self.detail_urls: list[str] = []

    def user_notes(self, user_id: str, limit: int = 20) -> list[dict]:
        value = self.rows_by_user[user_id]
        if isinstance(value, Exception):
            raise value
        return value[:limit]

    def note_detail(self, signed_url: str) -> dict:
        self.detail_urls.append(signed_url)
        value = self.details.get(signed_url, {})
        if isinstance(value, Exception):
            raise value
        return value


class XiaohongshuSourceTests(unittest.TestCase):
    def test_collects_creator_and_filters_to_local_calendar_day(self) -> None:
        now = dt.datetime(2026, 7, 11, 12, 0, tzinfo=TZ)
        current_id = note_id(dt.datetime(2026, 7, 11, 8, 30, tzinfo=TZ))
        old_id = note_id(dt.datetime(2026, 7, 10, 23, 59, tzinfo=TZ))
        signed_url = f"https://www.xiaohongshu.com/explore/{current_id}?xsec_token=secret&xsec_source=pc_feed"
        client = _FakeClient(
            {"creator1": [
                {"id": old_id, "title": "old", "url": f"https://www.xiaohongshu.com/explore/{old_id}"},
                {"id": current_id, "title": "list title", "likes": "1.2万", "url": signed_url},
            ]},
            {signed_url: {
                "title": "Agent infrastructure update",
                "author": "Alice",
                "content": "A detailed post about LLM serving and agents.",
                "likes": "1.3万",
                "collects": "240",
                "comments": "31",
                "tags": "AI Agent, LLM serving",
            }},
        )
        track = {"days": 7, "xiaohongshu": {
            "days": 1,
            "creators": [{"name": "Alice", "user_id": "creator1"}],
        }}

        signals = XiaohongshuSource(client=client, now=now).fetch(track)

        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal.id, f"xhs:{current_id}")
        self.assertEqual(signal.url, signed_url)
        self.assertIn("xsec_token", signal.url)
        self.assertNotIn("xsec_token", json.dumps(signal.extra))
        self.assertEqual(signal.title, "Agent infrastructure update")
        self.assertEqual(signal.authors, ["Alice"])
        self.assertEqual(signal.popularity, 13_000)
        self.assertEqual(signal.extra["collects"], 240)
        self.assertEqual(signal.extra["comments"], 31)
        self.assertEqual(signal.published_at.date(), now.date())
        self.assertEqual(client.detail_urls, [signed_url])

    def test_accepts_profile_url_and_isolates_creator_failures(self) -> None:
        now = dt.datetime(2026, 7, 11, 12, 0, tzinfo=TZ)
        current_id = note_id(now)
        client = _FakeClient({
            "broken": OpenCLIError("login expired"),
            "creator2": [{"id": current_id, "title": "Useful agent post", "url": ""}],
        })
        track = {"xiaohongshu": {
            "creators": [
                {"name": "Broken", "user_id": "broken"},
                {"name": "Bob", "profile_url": "https://www.xiaohongshu.com/user/profile/creator2"},
            ],
            "fetch_details": False,
        }}

        with patch("builtins.print"):
            signals = XiaohongshuSource(client=client, now=now).fetch(track)

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].authors, ["Bob"])

    def test_source_evidence_has_localized_label(self) -> None:
        now = dt.datetime(2026, 7, 11, 12, 0, tzinfo=TZ)
        current_id = note_id(now)
        client = _FakeClient({"creator": [{"id": current_id, "title": "Post"}]})
        signal = XiaohongshuSource(client=client, now=now).fetch({"xiaohongshu": {
            "creators": [{"user_id": "creator"}],
            "fetch_details": False,
        }})[0]

        self.assertEqual(source_signal_items(signal, "zh")[0]["label"], "小红书博主动态")
        self.assertEqual(source_signal_items(signal, "en")[0]["label"], "Xiaohongshu creator post")

    def test_folded_paper_keeps_xiaohongshu_source_evidence(self) -> None:
        paper = Signal(
            id="2607.00001",
            title="Paper",
            url="https://arxiv.org/abs/2607.00001",
            type="paper",
            published_at=dt.datetime(2026, 7, 11, tzinfo=dt.timezone.utc),
            summary="Abstract",
            sources=["arxiv", "xiaohongshu"],
            extra={"source_evidence": [{
                "sources": ["xiaohongshu"],
                "title": "Creator discussion",
                "url": "https://www.xiaohongshu.com/explore/abc",
                "popularity": 20,
            }]},
        )

        labels = [item["label"] for item in source_signal_items(paper, "zh")]

        self.assertIn("小红书博主动态 👍 20", labels)

    def test_count_parses_compact_counts(self) -> None:
        self.assertEqual(_count("1.2万"), 12_000)
        self.assertEqual(_count("3.4k"), 3_400)
        self.assertEqual(_count("1,234"), 1_234)
        self.assertEqual(_count("赞"), 0)


class OpenCLIXiaohongshuClientTests(unittest.TestCase):
    @patch("omnisource.sources.xiaohongshu_client.shutil.which", return_value="/usr/local/bin/opencli")
    @patch("omnisource.sources.xiaohongshu_client.subprocess.run")
    def test_normalizes_user_and_note_json(self, run, _which) -> None:
        run.side_effect = [
            subprocess.CompletedProcess([], 0, stdout='log line\n{"data":{"items":[{"id":"abc"}]}}\n', stderr=""),
            subprocess.CompletedProcess([], 0, stdout='[{"field":"title","value":"A post"},{"field":"content","value":"Body"}]', stderr=""),
        ]
        client = OpenCLIXiaohongshuClient(OpenCLIConfig(timeout_seconds=10))

        self.assertEqual(client.user_notes("creator"), [{"id": "abc"}])
        self.assertEqual(client.note_detail("https://example.test/note"), {"title": "A post", "content": "Body"})
        self.assertEqual(run.call_args_list[0].args[0][:4], ["opencli", "xiaohongshu", "user", "creator"])

    @patch("omnisource.sources.xiaohongshu_client.shutil.which", return_value="/usr/local/bin/opencli")
    @patch("omnisource.sources.xiaohongshu_client.subprocess.run")
    def test_redacts_xsec_token_from_errors(self, run, _which) -> None:
        run.return_value = subprocess.CompletedProcess([], 1, stdout="", stderr="failed https://x.test/n?xsec_token=very-secret&x=1")
        client = OpenCLIXiaohongshuClient()

        with self.assertRaises(OpenCLIError) as raised:
            client.note_detail("https://x.test/n?xsec_token=very-secret")

        self.assertNotIn("very-secret", str(raised.exception))
        self.assertIn("<redacted>", str(raised.exception))

    @patch("omnisource.sources.xiaohongshu_client.time.sleep")
    @patch("omnisource.sources.xiaohongshu_client.shutil.which", return_value="/usr/local/bin/opencli")
    @patch("omnisource.sources.xiaohongshu_client.subprocess.run")
    def test_retries_a_navigation_rejection_once(self, run, _which, sleep) -> None:
        run.side_effect = [
            subprocess.CompletedProcess([], 1, stdout="", stderr="Navigation rejected."),
            subprocess.CompletedProcess([], 0, stdout='[{"id":"abc"}]', stderr=""),
        ]
        client = OpenCLIXiaohongshuClient()

        self.assertEqual(client.user_notes("creator"), [{"id": "abc"}])
        self.assertEqual(run.call_count, 2)
        sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
