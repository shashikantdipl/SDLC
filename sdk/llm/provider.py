"""LLMProvider — Abstract interface for LLM backends.

Every LLM provider (Anthropic, OpenAI, Ollama, Bedrock, etc.)
implements this interface. The rest of the platform never imports
a specific provider — it only imports LLMProvider.

Design decisions:
- generate() is the only method agents call
- calculate_cost() is separate for budget enforcement (can be called without generating)
- ModelTier maps abstract tiers (fast/balanced/powerful) to provider-specific model IDs
- ProviderConfig holds connection settings (API key, base URL, timeout)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ModelTier(str, Enum):
    """Abstract model tiers — mapped to provider-specific model IDs.

    fast:      Cheapest, fastest, best for simple tasks (haiku, gpt-4o-mini, llama3.2)
    balanced:  Mid-range, good quality/cost ratio (sonnet, gpt-4o, mistral-large)
    powerful:  Most capable, highest quality (opus, gpt-4.5, llama3.1-405b)
    """

    FAST = "fast"
    BALANCED = "balanced"
    POWERFUL = "powerful"


@dataclass(frozen=True)
class ProviderConfig:
    """Configuration for an LLM provider instance."""

    provider_name: str
    api_key: str = ""
    base_url: str = ""
    timeout_seconds: float = 120.0
    max_retries: int = 2
    extra: dict = field(default_factory=dict)


@dataclass(frozen=True)
class LLMResponse:
    """Standard response from any LLM provider.

    Every provider returns this exact shape — the rest of the platform
    never needs to know which provider generated the response.
    """

    content: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model: str
    provider: str
    latency_ms: float = 0.0
    finish_reason: str = "stop"
    raw_response: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract LLM provider interface.

    Implementations:
    - AnthropicProvider (Claude models)
    - OpenAIProvider (GPT models)
    - OllamaProvider (local models)
    - Add your own by implementing this interface
    """

    def __init__(self, config: ProviderConfig) -> None:
        self._config = config

    @property
    def provider_name(self) -> str:
        return self._config.provider_name

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        """Generate a completion from the LLM.

        Args:
            system_prompt: System message (agent role, instructions)
            user_message: User input (the task for the agent)
            model: Provider-specific model ID (e.g., "claude-haiku-4-5-20251001", "gpt-4o-mini")
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            stop_sequences: Optional stop sequences

        Returns:
            LLMResponse with content, token counts, cost, and metadata
        """
        ...

    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate the cost in USD for a given token count and model.

        Used by budget enforcement BEFORE generation (to estimate cost)
        and AFTER generation (to record actual cost).
        """
        ...

    @abstractmethod
    def resolve_model(self, tier: ModelTier) -> str:
        """Map an abstract tier to a provider-specific model ID.

        Examples:
            AnthropicProvider: FAST → "claude-haiku-4-5-20251001"
            OpenAIProvider:    FAST → "gpt-4o-mini"
            OllamaProvider:    FAST → "llama3.2"
        """
        ...

    @abstractmethod
    def list_models(self) -> dict[ModelTier, str]:
        """Return the tier-to-model mapping for this provider."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify the provider is reachable and the API key is valid.

        Returns True if healthy, False otherwise. Never raises.
        """
        ...
