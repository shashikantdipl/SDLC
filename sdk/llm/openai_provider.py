"""OpenAIProvider — GPT models (GPT-4o, GPT-4o-mini, GPT-4.5).

Same interface as AnthropicProvider — the platform doesn't know the difference.
"""

from __future__ import annotations

import time

from sdk.llm.provider import LLMProvider, LLMResponse, ModelTier, ProviderConfig

# Pricing per million tokens (as of 2026-03)
_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gpt-4.5-preview": (75.00, 150.00),
    "o3-mini": (1.10, 4.40),
}

_TIER_MAP: dict[ModelTier, str] = {
    ModelTier.FAST: "gpt-4o-mini",
    ModelTier.BALANCED: "gpt-4o",
    ModelTier.POWERFUL: "gpt-4.5-preview",
}


class OpenAIProvider(LLMProvider):
    """GPT models via the OpenAI API."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        # Lazy import — only needed if this provider is actually used
        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise ImportError(
                "OpenAI provider requires the openai package. Install with: pip install openai"
            ) from e

        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or None,
            timeout=config.timeout_seconds,
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

        response = await self._client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            stop=stop_sequences,
        )

        elapsed_ms = (time.monotonic() - start) * 1000
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        content = response.choices[0].message.content if response.choices else ""
        finish = response.choices[0].finish_reason if response.choices else "stop"

        return LLMResponse(
            content=content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self.calculate_cost(input_tokens, output_tokens, model),
            model=model,
            provider="openai",
            latency_ms=elapsed_ms,
            finish_reason=finish or "stop",
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        input_rate, output_rate = _PRICING.get(model, (2.50, 10.00))
        return (input_tokens * input_rate + output_tokens * output_rate) / 1_000_000

    def resolve_model(self, tier: ModelTier) -> str:
        return _TIER_MAP[tier]

    def list_models(self) -> dict[ModelTier, str]:
        return dict(_TIER_MAP)

    async def health_check(self) -> bool:
        try:
            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return bool(response.choices)
        except Exception:
            return False
