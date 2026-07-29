from __future__ import annotations

import datetime as dt
import unittest
from unittest.mock import patch

from omnisource.agents import curator
from omnisource.agents.analyst import Analyst
from omnisource.models import Signal


class FailingProvider:
    def complete_json(self, system: str, user: str) -> dict:
        raise RuntimeError("gateway timed out")


def make_signal() -> Signal:
    return Signal(
        id="required-llm",
        title="Required LLM signal",
        url="https://example.com/required-llm",
        type="paper",
        published_at=dt.datetime(2026, 7, 21, tzinfo=dt.timezone.utc),
        summary="A paper summary.",
        sources=["arxiv"],
    )


class RequiredLLMTests(unittest.TestCase):
    def test_actions_can_override_track_provider_and_model(self) -> None:
        track = {"llm": {"provider": "openai", "model": "gpt-4.1-mini"}}
        provider = type("Provider", (), {"model": "gateway-model"})()
        environment = {
            "OMNISOURCE_LLM_PROVIDER": "openai_compatible",
            "OMNISOURCE_LLM_MODEL": "gateway-model",
        }

        with patch.dict("os.environ", environment, clear=True):
            with patch.object(curator, "get_provider", return_value=provider) as get_provider:
                analyst = curator.make_analyst(track, enabled=True)

        get_provider.assert_called_once_with("openai_compatible", "gateway-model")
        self.assertIsInstance(analyst, Analyst)

    def test_required_llm_does_not_silently_disable_on_setup_error(self) -> None:
        track = {"llm": {"provider": "openai_compatible", "model": "test"}}
        with patch.dict("os.environ", {"OMNISOURCE_REQUIRE_LLM": "1"}):
            with patch.object(curator, "get_provider", side_effect=RuntimeError("missing key")):
                with self.assertRaisesRegex(RuntimeError, "LLM is required"):
                    curator.make_analyst(track, enabled=True)

    def test_required_llm_rejects_all_failed_analyses(self) -> None:
        analyst = Analyst(FailingProvider())
        track = {"name": "test", "output": {"language": "中文"}}
        with patch.dict("os.environ", {"OMNISOURCE_REQUIRE_LLM": "1"}):
            with self.assertRaisesRegex(RuntimeError, "failed for every shortlisted item"):
                curator.enrich_and_rank([make_signal()], track, analyst)
