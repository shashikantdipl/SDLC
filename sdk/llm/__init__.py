"""LLM Provider abstraction — makes the platform LLM-agnostic.

The platform supports ANY LLM provider through the LLMProvider interface.
To add a new provider, implement LLMProvider and register it in the factory.

Usage:
    provider = create_provider("anthropic")  # or "openai", "ollama"
    response = await provider.generate(system_prompt, user_message, model_id, max_tokens)
"""

from sdk.llm.provider import LLMProvider, LLMResponse, ModelTier, ProviderConfig
from sdk.llm.factory import create_provider, get_default_provider, list_providers

__all__ = [
    "LLMProvider",
    "LLMResponse",
    "ModelTier",
    "ProviderConfig",
    "create_provider",
    "get_default_provider",
    "list_providers",
]
