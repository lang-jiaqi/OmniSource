"""OpenAI provider. Reads OPENAI_API_KEY from the environment."""
from __future__ import annotations

import json

from openai import OpenAI

from .base import LLMProvider

DEFAULT_MODEL = "gpt-4o-mini"


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__(model)
        self.client = OpenAI()  # raises if OPENAI_API_KEY is missing

    def complete_json(self, system: str, user: str) -> dict:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(resp.choices[0].message.content)
