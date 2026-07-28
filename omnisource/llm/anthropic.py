"""Anthropic (Claude) provider. Reads ANTHROPIC_API_KEY from the environment."""
from __future__ import annotations

import os

from anthropic import Anthropic

from .base import LLMProvider, parse_json

DEFAULT_MODEL = "claude-haiku-4-5"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__(model)
        # Fail fast (like OpenAIProvider) so make_analyst degrades cleanly to
        # keyword ranking instead of erroring on every signal.
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic()

    def complete_json(self, system: str, user: str) -> dict:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.2,
            system=system + "\nReturn only the JSON object, no prose.",
            messages=[{"role": "user", "content": user}],
        )
        return parse_json(message.content[0].text)
