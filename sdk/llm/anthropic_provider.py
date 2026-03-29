"""AnthropicProvider — Claude models (Haiku, Sonnet, Opus).

This is the reference implementation of LLMProvider.
Other providers follow the same pattern.
"""

from __future__ import annotations

import time

from anthropic import AsyncAnthropic

from sdk.llm.provider import LLMProvider, LLMResponse, ModelTier, ProviderConfig

# Pricing per million tokens (as of 2026-03)
_PRICING: dict[str, tuple[float, float]] = {
    # model_id: (input_per_M, output_per_M)
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-opus-4-6": (15.00, 75.00),
    # Legacy fallbacks
    "claude-3-5-haiku-20241022": (1.00, 5.00),
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
}

_TIER_MAP: dict[ModelTier, str] = {
    ModelTier.FAST: "claude-haiku-4-5-20251001",
    ModelTier.BALANCED: "claude-sonnet-4-6",
    ModelTier.POWERFUL: "claude-opus-4-6",
}


class AnthropicProvider(LLMProvider):
    """Claude models via the Anthropic API."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._client = AsyncAnthropic(
            api_key=config.api_key,
            base_url=config.base_url or None,
            timeout=max(config.timeout_seconds, 300.0),  # Min 300s for large outputs (Opus BRD etc)
            max_retries=config.max_retries,
        )

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        start = time.monotonic()

        response = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            stop_sequences=stop_sequences or [],
        )

        elapsed_ms = (time.monotonic() - start) * 1000
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        content = response.content[0].text if response.content else ""

        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self.calculate_cost(input_tokens, output_tokens, model),
            model=model,
            provider="anthropic",
            latency_ms=elapsed_ms,
            finish_reason=response.stop_reason or "stop",
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        input_rate, output_rate = _PRICING.get(model, (3.00, 15.00))
        return (input_tokens * input_rate + output_tokens * output_rate) / 1_000_000

    def resolve_model(self, tier: ModelTier) -> str:
        return _TIER_MAP[tier]

    def list_models(self) -> dict[ModelTier, str]:
        return dict(_TIER_MAP)

    async def health_check(self) -> bool:
        try:
            response = await self._client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return bool(response.content)
        except Exception:
            return False
