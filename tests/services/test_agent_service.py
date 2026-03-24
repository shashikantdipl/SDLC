"""Tests for AgentService — agent lifecycle and management.

Covers: list_agents, get_agent, invoke_agent, check_health,
promote_version, rollback_version, set_canary_traffic, get_maturity,
and data-shape compliance.
Real PostgreSQL via testcontainers — no DB mocks.
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from services.agent_service import AgentNotFoundError, AgentService
from schemas.data_shapes import (
    AgentDetail,
    AgentHealth,
    AgentInvocationResult,
    AgentMaturity,
    AgentPhase,
    AgentStatus,
    AgentSummary,
    AgentVersion,
    MaturityLevel,
)


@pytest_asyncio.fixture
async def service(db_pool):
    """AgentService instance backed by test database."""
    return AgentService(db_pool)


@pytest_asyncio.fixture
async def seed_agents(db_pool):
    """Insert 3 test agents into agent_registry and clean up after."""
    agents = [
        ("test-agent-build-001", "Code Generator", "build", "co-pilot", "claude-sonnet-4-6", "active", "1.0.0", "supervised"),
        ("test-agent-test-002", "Test Runner", "test", "ci-gate", "claude-sonnet-4-6", "degraded", "2.0.0", "assisted"),
        ("test-agent-deploy-003", "Deploy Bot", "deploy", "ops-agent", "claude-sonnet-4-6", "active", "1.5.0", "autonomous"),
    ]
    for agent_id, name, phase, archetype, model, status, version, maturity in agents:
        await db_pool.execute(
            """
            INSERT INTO agent_registry (agent_id, name, phase, archetype, model, status, active_version, maturity_level)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (agent_id) DO NOTHING
            """,
            agent_id, name, phase, archetype, model, status, version, maturity,
        )

    yield agents

    # Clean up
    for agent_id, *_ in agents:
        await db_pool.execute("DELETE FROM cost_metrics WHERE agent_id = $1", agent_id)
        await db_pool.execute("DELETE FROM agent_registry WHERE agent_id = $1", agent_id)


# ---- I-020: list_agents ----


class TestListAgents:
    """I-020: List agents with optional filtering."""

    @pytest.mark.asyncio
    async def test_list_agents_returns_all(self, service: AgentService, seed_agents):
        agents = await service.list_agents()
        agent_ids = {a.agent_id for a in agents}
        assert "test-agent-build-001" in agent_ids
        assert "test-agent-test-002" in agent_ids
        assert "test-agent-deploy-003" in agent_ids

    @pytest.mark.asyncio
    async def test_list_agents_filter_by_phase(self, service: AgentService, seed_agents):
        agents = await service.list_agents(phase="build")
        assert all(a.phase == AgentPhase.BUILD for a in agents)
        assert any(a.agent_id == "test-agent-build-001" for a in agents)

    @pytest.mark.asyncio
    async def test_list_agents_filter_by_status(self, service: AgentService, seed_agents):
        agents = await service.list_agents(status="active")
        assert all(a.status == AgentStatus.ACTIVE for a in agents)

    @pytest.mark.asyncio
    async def test_list_agents_empty_result(self, service: AgentService, seed_agents):
        agents = await service.list_agents(phase="oversight")
        # May be empty if no oversight agents seeded
        test_ids = {a.agent_id for a in agents}
        assert "test-agent-build-001" not in test_ids


# ---- I-021: get_agent ----


class TestGetAgent:
    """I-021: Get agent detail."""

    @pytest.mark.asyncio
    async def test_get_agent_found(self, service: AgentService, seed_agents):
        detail = await service.get_agent("test-agent-build-001")
        assert detail.agent_id == "test-agent-build-001"
        assert detail.name == "Code Generator"
        assert detail.phase == AgentPhase.BUILD
        assert detail.active_version == "1.0.0"
        assert isinstance(detail, AgentDetail)

    @pytest.mark.asyncio
    async def test_get_agent_not_found_raises(self, service: AgentService, seed_agents):
        with pytest.raises(AgentNotFoundError, match="nonexistent-agent"):
            await service.get_agent("nonexistent-agent")


# ---- I-022: invoke_agent ----


class TestInvokeAgent:
    """I-022: Invoke an agent."""

    @pytest.mark.asyncio
    async def test_invoke_agent_returns_result(self, service: AgentService, seed_agents):
        result = await service.invoke_agent("test-agent-build-001", "Generate a REST handler")
        assert result.agent_id == "test-agent-build-001"
        assert result.status == "completed"
        assert isinstance(result, AgentInvocationResult)

    @pytest.mark.asyncio
    async def test_invoke_agent_not_found(self, service: AgentService, seed_agents):
        with pytest.raises(AgentNotFoundError):
            await service.invoke_agent("ghost-agent", "hello")


# ---- I-024: promote_version ----


class TestPromoteVersion:
    """I-024: Promote agent to new version."""

    @pytest.mark.asyncio
    async def test_promote_updates_active_version(self, service: AgentService, seed_agents):
        version = await service.promote_version("test-agent-build-001", "2.0.0")
        assert version.active_version == "2.0.0"
        assert version.previous_version == "1.0.0"
        assert version.canary_version is None
        assert version.canary_traffic_pct == 0
        assert isinstance(version, AgentVersion)

    @pytest.mark.asyncio
    async def test_promote_sets_previous_version(self, service: AgentService, seed_agents):
        await service.promote_version("test-agent-deploy-003", "2.0.0")
        version = await service.promote_version("test-agent-deploy-003", "3.0.0")
        assert version.active_version == "3.0.0"
        assert version.previous_version == "2.0.0"

    @pytest.mark.asyncio
    async def test_promote_not_found_raises(self, service: AgentService, seed_agents):
        with pytest.raises(AgentNotFoundError):
            await service.promote_version("nonexistent-agent", "9.9.9")


# ---- I-025: rollback_version ----


class TestRollbackVersion:
    """I-025: Rollback to previous version."""

    @pytest.mark.asyncio
    async def test_rollback_swaps_versions(self, service: AgentService, seed_agents):
        # First promote so there is a previous_version
        await service.promote_version("test-agent-build-001", "2.0.0")
        version = await service.rollback_version("test-agent-build-001")
        assert version.active_version == "1.0.0"
        assert version.previous_version == "2.0.0"

    @pytest.mark.asyncio
    async def test_rollback_no_previous_raises(self, service: AgentService, seed_agents):
        # Fresh agent has no previous_version
        with pytest.raises(ValueError, match="no previous version"):
            await service.rollback_version("test-agent-build-001")

    @pytest.mark.asyncio
    async def test_rollback_not_found_raises(self, service: AgentService, seed_agents):
        with pytest.raises(AgentNotFoundError):
            await service.rollback_version("nonexistent-agent")


# ---- I-026: set_canary_traffic ----


class TestSetCanaryTraffic:
    """I-026: Set canary traffic percentage."""

    @pytest.mark.asyncio
    async def test_set_canary_valid_percentage(self, service: AgentService, seed_agents):
        version = await service.set_canary_traffic("test-agent-build-001", 25)
        assert version.canary_traffic_pct == 25
        assert isinstance(version, AgentVersion)

    @pytest.mark.asyncio
    async def test_set_canary_over_100_raises(self, service: AgentService, seed_agents):
        with pytest.raises(ValueError, match="0-100"):
            await service.set_canary_traffic("test-agent-build-001", 101)

    @pytest.mark.asyncio
    async def test_set_canary_negative_raises(self, service: AgentService, seed_agents):
        with pytest.raises(ValueError, match="0-100"):
            await service.set_canary_traffic("test-agent-build-001", -1)

    @pytest.mark.asyncio
    async def test_set_canary_zero_resets(self, service: AgentService, seed_agents):
        await service.set_canary_traffic("test-agent-build-001", 50)
        version = await service.set_canary_traffic("test-agent-build-001", 0)
        assert version.canary_traffic_pct == 0


# ---- I-027: get_maturity ----


class TestGetMaturity:
    """I-027: Get agent maturity level."""

    @pytest.mark.asyncio
    async def test_get_maturity_returns_level(self, service: AgentService, seed_agents):
        maturity = await service.get_maturity("test-agent-build-001")
        assert maturity.agent_id == "test-agent-build-001"
        assert maturity.maturity == MaturityLevel.APPRENTICE  # supervised -> apprentice
        assert isinstance(maturity, AgentMaturity)

    @pytest.mark.asyncio
    async def test_get_maturity_autonomous_maps_to_professional(self, service: AgentService, seed_agents):
        maturity = await service.get_maturity("test-agent-deploy-003")
        assert maturity.maturity == MaturityLevel.PROFESSIONAL  # autonomous -> professional

    @pytest.mark.asyncio
    async def test_get_maturity_not_found(self, service: AgentService, seed_agents):
        with pytest.raises(AgentNotFoundError):
            await service.get_maturity("nonexistent-agent")


# ---- Data shape compliance ----


class TestDataShapeCompliance:
    """Verify returned objects match INTERACTION-MAP shapes exactly."""

    @pytest.mark.asyncio
    async def test_agent_summary_has_all_fields(self, service: AgentService, seed_agents):
        agents = await service.list_agents()
        agent = next(a for a in agents if a.agent_id == "test-agent-build-001")
        assert hasattr(agent, "agent_id")
        assert hasattr(agent, "name")
        assert hasattr(agent, "phase")
        assert hasattr(agent, "archetype")
        assert hasattr(agent, "model")
        assert hasattr(agent, "status")
        assert hasattr(agent, "active_version")
        assert hasattr(agent, "maturity")

    @pytest.mark.asyncio
    async def test_agent_detail_serializes_to_json(self, service: AgentService, seed_agents):
        detail = await service.get_agent("test-agent-build-001")
        json_data = detail.model_dump(mode="json")
        assert "agent_id" in json_data
        assert "phase" in json_data
        assert "maturity" in json_data
        assert "daily_cost_usd" in json_data
        assert "invocations_today" in json_data

    @pytest.mark.asyncio
    async def test_agent_version_serializes_to_json(self, service: AgentService, seed_agents):
        version = await service.promote_version("test-agent-build-001", "2.0.0")
        json_data = version.model_dump(mode="json")
        assert "agent_id" in json_data
        assert "active_version" in json_data
        assert "canary_version" in json_data
        assert "canary_traffic_pct" in json_data
        assert "previous_version" in json_data
        assert "updated_at" in json_data

    @pytest.mark.asyncio
    async def test_agent_maturity_serializes_to_json(self, service: AgentService, seed_agents):
        maturity = await service.get_maturity("test-agent-build-001")
        json_data = maturity.model_dump(mode="json")
        assert "agent_id" in json_data
        assert "maturity" in json_data
        assert "golden_tests_passed" in json_data
        assert "adversarial_tests_passed" in json_data
        assert "total_invocations" in json_data
        assert "avg_quality_score" in json_data
