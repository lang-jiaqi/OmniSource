"""OpenAI-compatible provider for hosted gateways and self-managed endpoints.

Use this for non-OpenAI services that expose the OpenAI chat completions API,
for example a lab gateway, vLLM, or another hosted model service. Secrets are
read from dedicated environment variables so they do not get mixed up with the
official OpenAI provider.
"""
from __future__ import annotations

import os

from openai import OpenAI

from .base import LLMProvider, parse_json

DEFAULT_MODEL = "gpt-5.5"


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw in (None, ""):
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class OpenAICompatibleProvider(LLMProvider):
    name = "openai_compatible"

    def __init__(self, model: str = DEFAULT_MODEL):
        super().__init__(model)
        api_key = os.environ.get("OPENAI_COMPATIBLE_API_KEY")
        base_url = os.environ.get("OPENAI_COMPATIBLE_BASE_URL")
        if not api_key:
            raise RuntimeError("OPENAI_COMPATIBLE_API_KEY is required")
        if not base_url:
            raise RuntimeError("OPENAI_COMPATIBLE_BASE_URL is required")
        timeout = _env_float("OPENAI_COMPATIBLE_TIMEOUT_SECONDS", 180.0)
        max_retries = _env_int("OPENAI_COMPATIBLE_MAX_RETRIES", 1)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
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
