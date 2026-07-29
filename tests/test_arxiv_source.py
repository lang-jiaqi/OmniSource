from __future__ import annotations

import datetime as dt
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from omnisource.sources.arxiv import ArxivSource


class RetryableArxivError(Exception):
    pass


class ArxivSourceTests(unittest.TestCase):
    def test_retries_with_exponential_delay_after_transient_failures(self) -> None:
        client_delays: list[float] = []

        class FakeClient:
            def __init__(self, page_size: int, delay_seconds: float, num_retries: int):
                client_delays.append(delay_seconds)

            def results(self, search):
                if len(client_delays) < 3:
                    raise RetryableArxivError("HTTP 429")
                return [
                    SimpleNamespace(
                        published=dt.datetime.now(dt.timezone.utc),
                        categories=["cs.AI"],
                        primary_category="cs.AI",
                        title="Agent paper",
                        entry_id="https://arxiv.org/abs/2607.00001",
                        summary="Summary",
                        authors=[SimpleNamespace(name="Ada")],
                        get_short_id=lambda: "2607.00001v1",
                    )
                ]

        fake_arxiv = SimpleNamespace(
            Client=FakeClient,
            HTTPError=RetryableArxivError,
            UnexpectedEmptyPageError=RetryableArxivError,
            Search=lambda **kwargs: kwargs,
            SortCriterion=SimpleNamespace(SubmittedDate="submitted"),
        )
        track = {
            "categories": ["cs.AI"],
            "days": 7,
            "pool_size": 10,
            "arxiv_retry_attempts": 3,
            "arxiv_delay_seconds": 2,
            "arxiv_client_retries": 1,
        }

        with patch.dict(sys.modules, {"arxiv": fake_arxiv}):
            with patch("omnisource.sources.arxiv.time.sleep") as sleep:
                signals = ArxivSource().fetch(track)

        self.assertEqual(client_delays, [2.0, 4.0, 8.0])
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [2.0, 4.0])
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].id, "2607.00001")


if __name__ == "__main__":
    unittest.main()
