"""OpenAI-compatible provider for hosted gateways and self-managed endpoints.

Use this for non-OpenAI services that expose the OpenAI chat completions API,
for example a lab gateway, vLLM, or another hosted model service. Secrets are
read from dedicated environment variables so they do not get mixed up with the
official OpenAI provider.
"""
from __future__ import annotations

import os
from collections.abc import Mapping

from openai import OpenAI

from .base import LLMProvider, parse_json

DEFAULT_MODEL = "gpt-5.5"


def _response_content(response: object) -> str:
    """Extract assistant text from common OpenAI-compatible response shapes."""
    if isinstance(response, str):
        return response
    if isinstance(response, bytes):
        return response.decode("utf-8")

    choices = response.get("choices") if isinstance(response, Mapping) else getattr(response, "choices", None)
    if not isinstance(choices, (list, tuple)) or not choices:
        raise RuntimeError(
            "OpenAI-compatible response has no choices; "
            f"received {type(response).__name__}"
        )

    choice = choices[0]
    message = choice.get("message") if isinstance(choice, Mapping) else getattr(choice, "message", None)
    content = message.get("content") if isinstance(message, Mapping) else getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, bytes):
        return content.decode("utf-8")
    if isinstance(content, (list, tuple)):
        parts: list[str] = []
        for part in content:
            text = part.get("text") if isinstance(part, Mapping) else getattr(part, "text", None)
            if isinstance(text, str):
                parts.append(text)
        if parts:
            return "".join(parts)

    raise RuntimeError(
        "OpenAI-compatible response has no text content; "
        f"received {type(content).__name__}"
    )


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
        return parse_json(_response_content(resp))
