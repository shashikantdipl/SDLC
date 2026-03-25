"""OllamaProvider — Local models via Ollama (Llama, Mistral, Phi, etc.).

Zero cost, runs entirely on-premise. Useful for:
- Development without API keys
- Sensitive data that can't leave the network
- Cost optimization for high-volume low-complexity tasks
"""

from __future__ import annotations

import time

import httpx

from sdk.llm.provider import LLMProvider, LLMResponse, ModelTier, ProviderConfig

_TIER_MAP: dict[ModelTier, str] = {
    ModelTier.FAST: "llama3.2",
    ModelTier.BALANCED: "mistral-large",
    ModelTier.POWERFUL: "llama3.1:405b",
}


class OllamaProvider(LLMProvider):
    """Local models via Ollama HTTP API."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._base_url = config.base_url or "http://localhost:11434"
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=config.timeout_seconds,
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

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "stop": stop_sequences or [],
            },
        }

        response = await self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

        elapsed_ms = (time.monotonic() - start) * 1000
        content = data.get("message", {}).get("content", "")
        input_tokens = data.get("prompt_eval_count", 0)
        output_tokens = data.get("eval_count", 0)

        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=0.0,  # Local models are free
            model=model,
            provider="ollama",
            latency_ms=elapsed_ms,
            finish_reason="stop",
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return 0.0  # Local models are free

    def resolve_model(self, tier: ModelTier) -> str:
        return _TIER_MAP.get(tier, "llama3.2")

    def list_models(self) -> dict[ModelTier, str]:
        return dict(_TIER_MAP)

    async def health_check(self) -> bool:
        try:
            response = await self._client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False
