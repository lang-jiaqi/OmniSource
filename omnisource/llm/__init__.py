"""LLM providers. Each turns a (system, user) prompt into a JSON object."""
from __future__ import annotations

from .anthropic import AnthropicProvider
from .base import LLMProvider
from .local import LocalProvider
from .openai import OpenAIProvider
from .openai_compatible import OpenAICompatibleProvider

PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "local": LocalProvider,
    "openai_compatible": OpenAICompatibleProvider,
}


def get_provider(name: str, model: str | None = None) -> LLMProvider:
    cls = PROVIDER_REGISTRY[name]
    return cls(model) if model else cls()


__all__ = [
    "LLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalProvider",
    "OpenAICompatibleProvider",
    "PROVIDER_REGISTRY",
    "get_provider",
]
