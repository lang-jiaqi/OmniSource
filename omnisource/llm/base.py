"""LLM provider base class.

Like Source, providers are pluggable: the pipeline asks for a JSON completion
and doesn't care whether it came from OpenAI, Anthropic, or a local model.
"""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def parse_json(text: str) -> dict:
    """Parse JSON from a model reply that may be fenced or have surrounding prose.
    Providers without a strict JSON mode (Anthropic, local models) use this."""
    text = text.strip()
    fenced = _FENCE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
    return json.loads(text)


class LLMProvider(ABC):
    name: str

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def complete_json(self, system: str, user: str) -> dict:
        """Return the model's response parsed as a JSON object."""
        raise NotImplementedError
