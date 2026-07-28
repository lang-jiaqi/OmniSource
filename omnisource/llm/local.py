"""Local / OpenAI-compatible provider (Ollama, vLLM, LM Studio, ...).

Points the OpenAI client at a local server via OPENAI_BASE_URL (default Ollama).
No real API key needed. Local models often lack a strict JSON mode, so the reply
is parsed leniently.
"""
from __future__ import annotations

import os

from openai import OpenAI

from .base import LLMProvider, parse_json

DEFAULT_MODEL = "llama3.1"
DEFAULT_BASE_URL = "http://localhost:11434/v1"


class LocalProvider(LLMProvider):
    name = "local"

    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__(model)
        self.client = OpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL),
            api_key=os.environ.get("OPENAI_API_KEY", "not-needed"),
        )

    def complete_json(self, system: str, user: str) -> dict:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system + "\nReturn only the JSON object."},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return parse_json(resp.choices[0].message.content)
