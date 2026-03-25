"""BaseAgent — Foundation class for all 48 SDLC agents.

LLM-AGNOSTIC: Uses LLMProvider interface, NOT any specific LLM SDK.
The provider is resolved from manifest.yaml or environment config.

Every agent extends this class. It provides:
- Manifest loading (9-subsystem anatomy from YAML)
- LLM invocation via LLMProvider (Anthropic, OpenAI, Ollama, or any custom)
- Pre/post hooks (audit, cost, PII detection)
- Budget enforcement (per-invocation ceiling)
- Dry-run mode (validate without calling LLM)
- Structured output via output schema

Usage:
    agent = BaseAgent(agent_dir=Path("agents/govern/G1-cost-tracker"))
    result = await agent.invoke({"scope": "project", ...})

    # With explicit provider:
    from sdk.llm import create_provider
    provider = create_provider("openai")
    agent = BaseAgent(agent_dir=..., provider=provider)
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4
from typing import Any

import yaml

from sdk.base_hooks import BaseHooks
from sdk.llm.provider import LLMProvider, LLMResponse, ModelTier


class BaseAgent:
    """Base class for all SDLC agents.

    LLM-agnostic: accepts any LLMProvider implementation.
    If no provider is given, creates one from manifest or environment.
    """

    def __init__(
        self,
        agent_dir: Path | str,
        provider: LLMProvider | None = None,
        hooks: BaseHooks | None = None,
        dry_run: bool = False,
    ) -> None:
        self.agent_dir = Path(agent_dir)
        self.dry_run = dry_run
        self._hooks = hooks or BaseHooks()

        # Load manifest
        manifest_path = self.agent_dir / "manifest.yaml"
        if manifest_path.exists():
            with open(manifest_path) as f:
                self.manifest = yaml.safe_load(f)
        else:
            self.manifest = {}

        # Load prompt
        prompt_path = self.agent_dir / "prompt.md"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""

        # Extract identity
        identity = self.manifest.get("identity", {})
        self.agent_id = identity.get("id", self.agent_dir.name)
        self.name = identity.get("name", self.agent_id)
        self.version = identity.get("version", "1.0.0")
        self.phase = identity.get("phase", "unknown")

        # Extract model config (LLM-agnostic)
        fm = self.manifest.get("foundation_model", {})
        self._model_tier = ModelTier(fm.get("tier", "fast"))
        self._model_override = fm.get("model", None)  # Provider-specific override
        self._preferred_provider = fm.get("provider", None)  # e.g., "anthropic", "openai"
        self.temperature = fm.get("temperature", 0.2)
        self.max_tokens = fm.get("max_tokens", 8192)

        # Extract safety config
        safety = self.manifest.get("safety", {})
        self.max_budget_usd = Decimal(str(safety.get("max_budget_usd", 0.50)))
        self.autonomy_tier = safety.get("autonomy_tier", "T2")
        self.audit_logging = safety.get("audit_logging", True)
        self.pii_scanning = safety.get("pii_scanning", True)

        # Output config
        output = self.manifest.get("output", {})
        self.output_key = output.get("writes_to", None)

        # LLM Provider (resolve lazily if not provided)
        self._provider = provider
        self._resolved_model: str | None = None

    @property
    def provider(self) -> LLMProvider:
        """Get or create the LLM provider."""
        if self._provider is None:
            self._provider = self._create_default_provider()
        return self._provider

    @property
    def model(self) -> str:
        """Get the resolved model ID for the current provider."""
        if self._resolved_model is None:
            if self._model_override:
                self._resolved_model = self._model_override
            else:
                self._resolved_model = self.provider.resolve_model(self._model_tier)
        return self._resolved_model

    @property
    def provider_name(self) -> str:
        """Name of the active LLM provider."""
        return self.provider.provider_name

    def _create_default_provider(self) -> LLMProvider:
        """Create provider from manifest preference or environment."""
        from sdk.llm.factory import create_provider, get_default_provider

        if self._preferred_provider:
            return create_provider(self._preferred_provider)
        return get_default_provider()

    async def invoke(
        self,
        input_data: dict[str, Any],
        session_id: UUID | None = None,
        project_id: str = "default",
    ) -> dict[str, Any]:
        """Invoke the agent with input data.

        Flow:
        1. Pre-hooks (audit start, budget check)
        2. Call LLM via provider (or dry-run)
        3. Post-hooks (audit complete, cost recording, PII scan)
        4. Return structured result
        """
        invocation_id = uuid4()
        session_id = session_id or uuid4()
        start_time = time.monotonic()

        # Pre-hooks
        await self._hooks.pre_invoke(
            agent_id=self.agent_id,
            invocation_id=invocation_id,
            session_id=session_id,
            project_id=project_id,
            input_data=input_data,
        )

        # Build user message
        user_message = json.dumps(input_data, indent=2, default=str)

        # Invoke LLM
        if self.dry_run:
            output_text = json.dumps({
                "dry_run": True,
                "agent_id": self.agent_id,
                "model": self.model,
                "provider": self.provider_name,
                "model_tier": self._model_tier.value,
                "input_keys": list(input_data.keys()),
                "would_write_to": self.output_key,
            })
            input_tokens = 0
            output_tokens = 0
            cost_usd = Decimal("0.00")
            provider_name = self.provider_name
        else:
            # Call LLM through the provider interface
            llm_response: LLMResponse = await self.provider.generate(
                system_prompt=self.system_prompt,
                user_message=user_message,
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            output_text = llm_response.content
            input_tokens = llm_response.input_tokens
            output_tokens = llm_response.output_tokens
            cost_usd = Decimal(str(llm_response.cost_usd)).quantize(Decimal("0.000001"))
            provider_name = llm_response.provider

        duration_ms = int((time.monotonic() - start_time) * 1000)

        # Post-hooks
        await self._hooks.post_invoke(
            agent_id=self.agent_id,
            invocation_id=invocation_id,
            session_id=session_id,
            project_id=project_id,
            output_text=output_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            duration_ms=duration_ms,
        )

        return {
            "invocation_id": str(invocation_id),
            "agent_id": self.agent_id,
            "output": output_text,
            "cost_usd": float(cost_usd),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_ms": duration_ms,
            "model": self.model,
            "provider": provider_name,
            "model_tier": self._model_tier.value,
            "dry_run": self.dry_run,
        }

    @property
    def info(self) -> dict[str, Any]:
        """Agent metadata for health checks and registry."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "phase": self.phase,
            "model": self.model,
            "provider": self.provider_name,
            "model_tier": self._model_tier.value,
            "autonomy_tier": self.autonomy_tier,
            "max_budget_usd": float(self.max_budget_usd),
        }
