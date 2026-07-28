from __future__ import annotations

import datetime as dt
import subprocess
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

from omnisource.sources.zhihu import ZhihuSource
from omnisource.sources.zhihu_client import OpenCLIZhihuError
from omnisource.sources.zhihu_client import OpenCLIZhihuClient


TZ = ZoneInfo("Asia/Shanghai")


class FakeClient:
    def __init__(self):
        self.opened = []

    def user_articles(self, user, limit=20):
        return [
            {"title": "Old", "created": "2026-05-01", "url": "https://zhuanlan.zhihu.com/p/1"},
            {"title": "Fresh", "created": "2026-07-10", "excerpt": "A concise LLM serving overview.",
             "url": "https://zhuanlan.zhihu.com/p/2"},
        ]

    def user_answers(self, user, limit=20):
        return []

    def article_detail(self, url):
        self.opened.append(url)
        return {"title": "Detailed", "author": "Alice", "publish_time": "编辑于 2026-07-10 08:30",
                "content": "Useful LLM serving content", "url": url}

    def answer_detail(self, url):
        raise AssertionError("not expected")


class ZhihuSourceTests(unittest.TestCase):
    def test_filters_creator_list_before_reading_detail(self):
        client = FakeClient()
        source = ZhihuSource(client=client, now=dt.datetime(2026, 7, 11, 12, tzinfo=TZ))
        signals = source.fetch({"days": 7, "zhihu": {
            "days": 7,
            "creators": [{"user": "alice", "answers": False}],
        }})
        self.assertEqual(len(signals), 1)
        self.assertNotIn("https://zhuanlan.zhihu.com/p/1", client.opened)
        self.assertEqual(signals[0].sources, ["zhihu"])
        self.assertEqual(signals[0].type, "blog")
        self.assertEqual(signals[0].summary, "A concise LLM serving overview.")

    def test_keeps_article_when_detail_navigation_fails(self):
        class FailingDetailClient(FakeClient):
            def user_articles(self, user, limit=20):
                return [
                    {"title": "Fresh systems note", "created": "2026-07-10",
                     "url": "https://zhuanlan.zhihu.com/p/3"},
                ]

            def article_detail(self, url):
                raise OpenCLIZhihuError("Navigation rejected")

        source = ZhihuSource(client=FailingDetailClient(), now=dt.datetime(2026, 7, 11, 12, tzinfo=TZ))
        signals = source.fetch({"days": 7, "zhihu": {
            "days": 7,
            "creators": [{"user": "alice", "answers": False}],
        }})

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].id, "zhihu:article:3")
        self.assertEqual(signals[0].title, "Fresh systems note")
        self.assertEqual(signals[0].summary, "")

    @patch("omnisource.sources.zhihu_client.time.sleep")
    @patch("omnisource.sources.zhihu_client.shutil.which", return_value="/usr/local/bin/opencli")
    @patch("omnisource.sources.zhihu_client.subprocess.run")
    def test_client_retries_a_navigation_rejection_once(self, run, _which, sleep):
        run.side_effect = [
            subprocess.CompletedProcess([], 1, stdout="", stderr="Navigation rejected."),
            subprocess.CompletedProcess([], 0, stdout='[{"title":"Fresh"}]', stderr=""),
        ]
        client = OpenCLIZhihuClient()

        self.assertEqual(client.user_articles("alice", limit=1), [{"title": "Fresh"}])
        self.assertEqual(run.call_count, 2)
        sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
