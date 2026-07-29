from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch

from omnisource.llm import OpenAICompatibleProvider, get_provider


class LLMProviderRegistryTests(unittest.TestCase):
    @staticmethod
    def _provider_with_response(response: object) -> OpenAICompatibleProvider:
        provider = object.__new__(OpenAICompatibleProvider)
        provider.model = "test-model"
        provider.client = Mock()
        provider.client.chat.completions.create.return_value = response
        return provider

    def test_openai_compatible_provider_uses_dedicated_env_vars(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "OPENAI_COMPATIBLE_API_KEY": "test-key",
                "OPENAI_COMPATIBLE_BASE_URL": "http://example.test/v1",
                "OPENAI_COMPATIBLE_TIMEOUT_SECONDS": "240",
                "OPENAI_COMPATIBLE_MAX_RETRIES": "3",
            },
            clear=False,
        ):
            with patch("omnisource.llm.openai_compatible.OpenAI") as openai_cls:
                provider = get_provider("openai_compatible", "gpt-5.5")

        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertEqual(provider.model, "gpt-5.5")
        openai_cls.assert_called_once_with(
            api_key="test-key",
            base_url="http://example.test/v1",
            timeout=240.0,
            max_retries=3,
        )

    def test_openai_compatible_provider_requires_base_url(self) -> None:
        with patch.dict("os.environ", {"OPENAI_COMPATIBLE_API_KEY": "test-key"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_COMPATIBLE_BASE_URL"):
                OpenAICompatibleProvider("gpt-5.5")

    def test_openai_compatible_provider_accepts_sdk_dict_and_string_responses(self) -> None:
        expected = {"topic": "agents"}
        responses = (
            SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content='{"topic":"agents"}'))]
            ),
            {"choices": [{"message": {"content": '{"topic":"agents"}'}}]},
            '{"topic":"agents"}',
        )
        for response in responses:
            with self.subTest(response_type=type(response).__name__):
                provider = self._provider_with_response(response)
                self.assertEqual(provider.complete_json("system", "user"), expected)

    def test_openai_compatible_provider_rejects_malformed_response_clearly(self) -> None:
        provider = self._provider_with_response({"result": "missing choices"})

        with self.assertRaisesRegex(RuntimeError, "response has no choices"):
            provider.complete_json("system", "user")


if __name__ == "__main__":
    unittest.main()
