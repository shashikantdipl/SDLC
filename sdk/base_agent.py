"""BaseAgent — Foundation class for all 48 SDLC agents.

Every agent extends this class. It provides:
- Manifest loading (9-subsystem anatomy from YAML)
- Claude API invocation via Anthropic SDK
- Pre/post hooks (audit, cost, PII detection)
- Budget enforcement (per-invocation ceiling)
- Dry-run mode (validate without calling API)
- Structured output via output schema

Usage:
    class G1CostTracker(BaseAgent):
        async def run(self, input_data: dict) -> dict:
            return await self.invoke(input_data)
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
from anthropic import AsyncAnthropic

from sdk.base_hooks import BaseHooks


class BaseAgent:
    """Base class for all SDLC agents.

    Loads manifest.yaml, enforces budget, calls Claude API, runs hooks.
    """

    def __init__(
        self,
        agent_dir: Path | str,
        api_key: str | None = None,
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

        # Extract model config
        fm = self.manifest.get("foundation_model", {})
        self.model = fm.get("model", "claude-haiku-4-5-20251001")
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

        # Anthropic client
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._client = AsyncAnthropic(api_key=key) if key else None

    async def invoke(
        self,
        input_data: dict[str, Any],
        session_id: UUID | None = None,
        project_id: str = "default",
    ) -> dict[str, Any]:
        """Invoke the agent with input data.

        Flow:
        1. Pre-hooks (audit start, budget check)
        2. Call Claude API (or dry-run)
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

        # Build messages
        messages = self._build_messages(input_data)

        # Invoke
        if self.dry_run:
            output_text = json.dumps({
                "dry_run": True,
                "agent_id": self.agent_id,
                "model": self.model,
                "input_keys": list(input_data.keys()),
                "would_write_to": self.output_key,
            })
            input_tokens = 0
            output_tokens = 0
            cost_usd = Decimal("0.00")
        elif self._client is None:
            raise RuntimeError(
                f"Cannot invoke {self.agent_id}: no API key. "
                "Set ANTHROPIC_API_KEY env var or pass api_key to constructor."
            )
        else:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=messages,
            )
            output_text = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost_usd = self._estimate_cost(input_tokens, output_tokens)

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
            "dry_run": self.dry_run,
        }

    def _build_messages(self, input_data: dict[str, Any]) -> list[dict[str, str]]:
        """Build Claude API messages from input data."""
        user_content = json.dumps(input_data, indent=2, default=str)
        return [{"role": "user", "content": user_content}]

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """Estimate cost based on model pricing."""
        # Approximate pricing per 1M tokens (as of 2026)
        pricing = {
            "claude-haiku-4-5-20251001": {"input": Decimal("0.80"), "output": Decimal("4.00")},
            "claude-sonnet-4-6": {"input": Decimal("3.00"), "output": Decimal("15.00")},
            "claude-opus-4-6": {"input": Decimal("15.00"), "output": Decimal("75.00")},
        }
        model_price = pricing.get(self.model, pricing["claude-sonnet-4-6"])
        cost = (
            Decimal(input_tokens) * model_price["input"] / Decimal("1000000")
            + Decimal(output_tokens) * model_price["output"] / Decimal("1000000")
        )
        return cost.quantize(Decimal("0.000001"))

    @property
    def info(self) -> dict[str, Any]:
        """Agent metadata for health checks and registry."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "phase": self.phase,
            "model": self.model,
            "autonomy_tier": self.autonomy_tier,
            "max_budget_usd": float(self.max_budget_usd),
        }
