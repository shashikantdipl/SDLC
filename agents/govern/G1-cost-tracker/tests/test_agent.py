"""Tests for G1-cost-tracker agent.

Tests run in dry-run mode (no API key needed) and with mocked API responses.
Real API tests require ANTHROPIC_API_KEY and are marked with @pytest.mark.live.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import sys
# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestG1DryRun:
    """Tests using dry_run=True (no API key needed)."""

    @pytest.mark.asyncio
    async def test_dry_run_returns_result(self):
        from agents.govern.G1_cost_tracker.agent import G1CostTracker
        # Note: Python can't import hyphenated dirs, we need to handle this
        # For now, test with BaseAgent directly
        from sdk.base_agent import BaseAgent

        agent = BaseAgent(
            agent_dir=Path(__file__).parent.parent,
            dry_run=True,
        )

        result = await agent.invoke(
            input_data={
                "scope": "project",
                "scope_id": "proj-001",
                "cost_data": [{"agent_id": "D1", "cost_usd": 0.50, "invocations": 2}],
                "budget_config": {"budget_usd": 20.00},
            },
            project_id="test-project",
        )

        assert result["dry_run"] is True
        assert result["agent_id"] is not None
        assert result["cost_usd"] == 0.0
        assert result["duration_ms"] >= 0

    @pytest.mark.asyncio
    async def test_dry_run_loads_manifest(self):
        from sdk.base_agent import BaseAgent

        agent = BaseAgent(
            agent_dir=Path(__file__).parent.parent,
            dry_run=True,
        )

        assert agent.agent_id == "G1-cost-tracker"
        assert agent.phase == "govern"
        assert agent.model == "claude-haiku-4-5-20251001"
        assert agent.temperature == 0.0
        assert float(agent.max_budget_usd) == 0.05

    @pytest.mark.asyncio
    async def test_dry_run_loads_prompt(self):
        from sdk.base_agent import BaseAgent

        agent = BaseAgent(
            agent_dir=Path(__file__).parent.parent,
            dry_run=True,
        )

        assert "cost monitoring agent" in agent.system_prompt.lower()
        assert len(agent.system_prompt) > 500  # Prompt must be substantial

    @pytest.mark.asyncio
    async def test_agent_info(self):
        from sdk.base_agent import BaseAgent

        agent = BaseAgent(
            agent_dir=Path(__file__).parent.parent,
            dry_run=True,
        )

        info = agent.info
        assert info["agent_id"] == "G1-cost-tracker"
        assert info["phase"] == "govern"
        assert info["model"] == "claude-haiku-4-5-20251001"

    @pytest.mark.asyncio
    async def test_no_api_key_raises(self):
        from sdk.base_agent import BaseAgent
        import os

        # Ensure no API key
        old_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        old_provider = os.environ.pop("LLM_PROVIDER", None)
        try:
            agent = BaseAgent(
                agent_dir=Path(__file__).parent.parent,
                dry_run=False,
            )
            with pytest.raises((ValueError, RuntimeError)):
                await agent.invoke({"scope": "fleet", "scope_id": "all"})
        finally:
            if old_key:
                os.environ["ANTHROPIC_API_KEY"] = old_key
            if old_provider:
                os.environ["LLM_PROVIDER"] = old_provider


class TestG1PiiDetection:
    """Test PII scanning in hooks."""

    @pytest.mark.asyncio
    async def test_pii_detected_in_output(self):
        from sdk.base_hooks import BaseHooks

        hooks = BaseHooks()
        assert hooks._scan_pii("Contact john@example.com for details") is True
        assert hooks._scan_pii("Cost report: $0.50 for 3 invocations") is False
        assert hooks._scan_pii("SSN: 123-45-6789") is True


class TestG1CostEstimation:
    """Test cost estimation via LLM provider (LLM-agnostic)."""

    @pytest.mark.asyncio
    async def test_provider_cost_calculation(self):
        from sdk.llm.anthropic_provider import AnthropicProvider
        from sdk.llm.provider import ProviderConfig

        config = ProviderConfig(provider_name="anthropic", api_key="test-key")
        provider = AnthropicProvider(config)

        # Haiku pricing: $1.00/1M input, $5.00/1M output
        cost = provider.calculate_cost(input_tokens=1000, output_tokens=500, model="claude-haiku-4-5-20251001")
        expected = (1000 * 1.00 + 500 * 5.00) / 1_000_000  # 0.0035
        assert abs(cost - expected) < 0.0001


# Golden tests would go in tests/golden/ with known input -> expected output
# Adversarial tests would go in tests/adversarial/ with edge cases
