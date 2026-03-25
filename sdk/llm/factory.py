"""Provider factory — creates LLMProvider instances by name.

Usage:
    provider = create_provider("anthropic")  # reads API key from env
    provider = create_provider("openai", api_key="sk-...")
    provider = create_provider("ollama", base_url="http://gpu-server:11434")

To add a new provider:
    1. Create sdk/llm/my_provider.py implementing LLMProvider
    2. Add it to _REGISTRY below
    3. That's it — the rest of the platform picks it up automatically
"""

from __future__ import annotations

import os

from sdk.llm.provider import LLMProvider, ProviderConfig

# Registry of available providers (lazy-loaded)
_REGISTRY: dict[str, type] = {}


def _ensure_registry() -> None:
    """Populate the registry on first use (avoids import errors for uninstalled providers)."""
    if _REGISTRY:
        return

    # Anthropic — always available (primary provider)
    try:
        from sdk.llm.anthropic_provider import AnthropicProvider
        _REGISTRY["anthropic"] = AnthropicProvider
    except ImportError:
        pass

    # OpenAI — available if openai package installed
    try:
        from sdk.llm.openai_provider import OpenAIProvider
        _REGISTRY["openai"] = OpenAIProvider
    except ImportError:
        pass

    # Ollama — available if ollama server is reachable (no special package needed)
    try:
        from sdk.llm.ollama_provider import OllamaProvider
        _REGISTRY["ollama"] = OllamaProvider
    except ImportError:
        pass


# Environment variable to API key mapping
_ENV_KEY_MAP: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "ollama": "",  # No API key needed
}


def create_provider(
    provider_name: str,
    api_key: str | None = None,
    base_url: str = "",
    timeout_seconds: float = 120.0,
    max_retries: int = 2,
) -> LLMProvider:
    """Create an LLMProvider instance by name.

    If api_key is not provided, reads from environment variable:
        anthropic → ANTHROPIC_API_KEY
        openai    → OPENAI_API_KEY
        ollama    → (no key needed)

    Raises:
        ValueError: If provider_name is not in the registry
        ValueError: If API key is required but not found
    """
    _ensure_registry()

    if provider_name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys())) or "none (install anthropic or openai)"
        raise ValueError(
            f"Unknown LLM provider: '{provider_name}'. Available: {available}"
        )

    # Resolve API key from env if not provided
    if api_key is None:
        env_var = _ENV_KEY_MAP.get(provider_name, "")
        if env_var:
            api_key = os.environ.get(env_var, "")
            if not api_key:
                raise ValueError(
                    f"LLM provider '{provider_name}' requires API key. "
                    f"Set {env_var} environment variable or pass api_key parameter."
                )
        else:
            api_key = ""

    config = ProviderConfig(
        provider_name=provider_name,
        api_key=api_key,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
    )

    return _REGISTRY[provider_name](config)


def get_default_provider() -> LLMProvider:
    """Create the default provider from LLM_PROVIDER env var (defaults to 'anthropic')."""
    provider_name = os.environ.get("LLM_PROVIDER", "anthropic")
    return create_provider(provider_name)


def list_providers() -> list[str]:
    """Return names of all available providers (installed and importable)."""
    _ensure_registry()
    return sorted(_REGISTRY.keys())
