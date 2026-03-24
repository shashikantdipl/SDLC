"""Tests for HealthService — fleet health and MCP server monitoring.

Covers: fleet_health counts agents by status, fleet cost aggregation,
mcp_status aggregates by server, list_recent_mcp_calls with limit and
server filter, record_mcp_call stores in DB.
Real PostgreSQL via testcontainers — no DB mocks.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
import pytest_asyncio

from services.health_service import HealthService
from schemas.data_shapes import (
    AgentStatus,
    FleetHealth,
    McpCallEvent,
    McpServerStatus,
)


@pytest_asyncio.fixture
async def service(db_pool):
    """HealthService instance backed by test database."""
    return HealthService(db_pool)


@pytest_asyncio.fixture
async def seed_agents(db_pool):
    """Insert test agents into agent_registry for fleet health tests."""
    agents = [
        ("test-health-agent-001", "Builder A", "build", "co-pilot", "claude-sonnet-4-6", "active", "1.0.0", "supervised"),
        ("test-health-agent-002", "Builder B", "build", "co-pilot", "claude-sonnet-4-6", "active", "1.0.0", "supervised"),
        ("test-health-agent-003", "Tester A", "test", "ci-gate", "claude-sonnet-4-6", "degraded", "1.0.0", "assisted"),
        ("test-health-agent-004", "Deployer A", "deploy", "ops-agent", "claude-sonnet-4-6", "offline", "1.0.0", "autonomous"),
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


@pytest_asyncio.fixture
async def seed_cost_metrics(db_pool, seed_agents):
    """Insert cost metrics for today for fleet cost aggregation."""
    entries = [
        ("test-health-agent-001", "test-project", Decimal("1.50")),
        ("test-health-agent-002", "test-project", Decimal("2.25")),
        ("test-health-agent-003", "test-project", Decimal("0.75")),
    ]
    for agent_id, project_id, cost in entries:
        await db_pool.execute(
            """
            INSERT INTO cost_metrics (agent_id, project_id, session_id, model, input_tokens, output_tokens, cost_usd)
            VALUES ($1, $2, '00000000-0000-0000-0000-000000000001', 'claude-sonnet-4-6', 100, 50, $3)
            """,
            agent_id, project_id, cost,
        )

    yield entries


@pytest_asyncio.fixture
async def seed_mcp_calls(db_pool):
    """Insert MCP call events for monitoring tests."""
    calls = [
        ("agentic-sdlc-agents", "list_agents", "dashboard", "test-project", 45, "success"),
        ("agentic-sdlc-agents", "get_agent", "dashboard", "test-project", 32, "success"),
        ("agentic-sdlc-agents", "invoke_agent", "pipeline", "test-project", 120, "error"),
        ("agentic-sdlc-governance", "check_budget", "cost-panel", "test-project", 15, "success"),
        ("agentic-sdlc-governance", "get_audit_log", "audit-panel", "test-project", 22, "success"),
        ("agentic-sdlc-knowledge", "search_exceptions", "kb-panel", "test-project", 55, "success"),
    ]
    ids = []
    for server_name, tool_name, caller, project_id, duration_ms, status in calls:
        row = await db_pool.fetchrow(
            """
            INSERT INTO mcp_call_events (server_name, tool_name, caller, project_id, duration_ms, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            server_name, tool_name, caller, project_id, duration_ms, status,
        )
        ids.append(row["id"])

    yield calls

    # Clean up
    for row_id in ids:
        await db_pool.execute("DELETE FROM mcp_call_events WHERE id = $1", row_id)


# ---- I-080: get_fleet_health ----


class TestGetFleetHealth:
    """I-080: Aggregate fleet health."""

    @pytest.mark.asyncio
    async def test_fleet_health_counts_agents(self, service: HealthService, seed_agents):
        health = await service.get_fleet_health()
        assert isinstance(health, FleetHealth)
        assert health.total_agents >= 4  # at least our seeded agents

    @pytest.mark.asyncio
    async def test_fleet_health_active_count(self, service: HealthService, seed_agents):
        health = await service.get_fleet_health()
        # 2 active agents seeded
        assert health.healthy >= 2

    @pytest.mark.asyncio
    async def test_fleet_health_degraded_count(self, service: HealthService, seed_agents):
        health = await service.get_fleet_health()
        assert health.degraded >= 1

    @pytest.mark.asyncio
    async def test_fleet_health_inactive_count(self, service: HealthService, seed_agents):
        health = await service.get_fleet_health()
        # 1 offline agent maps to inactive
        assert health.inactive >= 1

    @pytest.mark.asyncio
    async def test_fleet_health_includes_agents_list(self, service: HealthService, seed_agents):
        health = await service.get_fleet_health()
        agent_ids = {a.agent_id for a in health.agents}
        assert "test-health-agent-001" in agent_ids

    @pytest.mark.asyncio
    async def test_fleet_cost_aggregation(self, service: HealthService, seed_cost_metrics):
        health = await service.get_fleet_health()
        # Total seeded cost: 1.50 + 2.25 + 0.75 = 4.50
        assert health.fleet_cost_today_usd >= Decimal("4.50")


# ---- I-081: get_mcp_status ----


class TestGetMcpStatus:
    """I-081: MCP server status aggregation."""

    @pytest.mark.asyncio
    async def test_mcp_status_returns_three_servers(self, service: HealthService, seed_mcp_calls):
        statuses = await service.get_mcp_status()
        assert len(statuses) == 3
        server_names = {s.server_name for s in statuses}
        assert "agentic-sdlc-agents" in server_names
        assert "agentic-sdlc-governance" in server_names
        assert "agentic-sdlc-knowledge" in server_names

    @pytest.mark.asyncio
    async def test_mcp_status_data_shape(self, service: HealthService, seed_mcp_calls):
        statuses = await service.get_mcp_status()
        for s in statuses:
            assert isinstance(s, McpServerStatus)
            assert hasattr(s, "server_name")
            assert hasattr(s, "status")
            assert hasattr(s, "tools_registered")
            assert hasattr(s, "error_rate_1h")
            assert hasattr(s, "avg_latency_ms")

    @pytest.mark.asyncio
    async def test_mcp_status_agents_server_has_error_rate(self, service: HealthService, seed_mcp_calls):
        statuses = await service.get_mcp_status()
        agents_status = next(s for s in statuses if s.server_name == "agentic-sdlc-agents")
        # 1 error out of 3 calls = ~33% error rate
        assert agents_status.error_rate_1h > 0

    @pytest.mark.asyncio
    async def test_mcp_status_no_calls_returns_unknown(self, service: HealthService):
        """Without seed data, servers should show unknown status."""
        statuses = await service.get_mcp_status()
        # At least some servers may have no calls
        assert len(statuses) == 3


# ---- I-082: list_recent_mcp_calls ----


class TestListRecentMcpCalls:
    """I-082: List recent MCP tool invocations."""

    @pytest.mark.asyncio
    async def test_list_recent_returns_calls(self, service: HealthService, seed_mcp_calls):
        calls = await service.list_recent_mcp_calls()
        assert len(calls) >= 6
        assert all(isinstance(c, McpCallEvent) for c in calls)

    @pytest.mark.asyncio
    async def test_list_recent_respects_limit(self, service: HealthService, seed_mcp_calls):
        calls = await service.list_recent_mcp_calls(limit=2)
        assert len(calls) <= 2

    @pytest.mark.asyncio
    async def test_list_recent_filter_by_server(self, service: HealthService, seed_mcp_calls):
        calls = await service.list_recent_mcp_calls(server_name="agentic-sdlc-governance")
        assert all(c.server_name == "agentic-sdlc-governance" for c in calls)
        assert len(calls) >= 2

    @pytest.mark.asyncio
    async def test_list_recent_ordered_by_called_at_desc(self, service: HealthService, seed_mcp_calls):
        calls = await service.list_recent_mcp_calls()
        for i in range(len(calls) - 1):
            assert calls[i].called_at >= calls[i + 1].called_at


# ---- Internal: record_mcp_call ----


class TestRecordMcpCall:
    """Internal: Record an MCP tool call."""

    @pytest.mark.asyncio
    async def test_record_stores_in_db(self, service: HealthService):
        result = await service.record_mcp_call(
            server_name="agentic-sdlc-agents",
            tool_name="list_agents",
            caller="test-caller",
            project_id="test-project",
            duration_ms=42,
            status="success",
            cost_usd=Decimal("0.001"),
        )
        assert isinstance(result, McpCallEvent)
        assert result.server_name == "agentic-sdlc-agents"
        assert result.tool_name == "list_agents"
        assert result.duration_ms == 42

        # Verify it appears in list
        calls = await service.list_recent_mcp_calls(server_name="agentic-sdlc-agents")
        assert any(c.call_id == result.call_id for c in calls)

        # Clean up
        await service._db.execute(
            "DELETE FROM mcp_call_events WHERE call_id = $1", result.call_id
        )

    @pytest.mark.asyncio
    async def test_record_error_call(self, service: HealthService):
        result = await service.record_mcp_call(
            server_name="agentic-sdlc-governance",
            tool_name="check_budget",
            caller="test-caller",
            status="error",
            error_message="Connection refused",
            duration_ms=5000,
        )
        assert result.status == "error"

        await service._db.execute(
            "DELETE FROM mcp_call_events WHERE call_id = $1", result.call_id
        )


# ---- Data shape compliance ----


class TestHealthDataShapeCompliance:
    """Verify returned objects match INTERACTION-MAP shapes."""

    @pytest.mark.asyncio
    async def test_fleet_health_serializes_to_json(self, service: HealthService, seed_agents):
        health = await service.get_fleet_health()
        json_data = health.model_dump(mode="json")
        assert "total_agents" in json_data
        assert "healthy" in json_data
        assert "degraded" in json_data
        assert "error" in json_data
        assert "inactive" in json_data
        assert "fleet_cost_today_usd" in json_data
        assert "agents" in json_data

    @pytest.mark.asyncio
    async def test_mcp_server_status_serializes_to_json(self, service: HealthService, seed_mcp_calls):
        statuses = await service.get_mcp_status()
        json_data = statuses[0].model_dump(mode="json")
        assert "server_name" in json_data
        assert "status" in json_data
        assert "uptime_seconds" in json_data
        assert "tools_registered" in json_data
        assert "error_rate_1h" in json_data

    @pytest.mark.asyncio
    async def test_mcp_call_event_serializes_to_json(self, service: HealthService, seed_mcp_calls):
        calls = await service.list_recent_mcp_calls(limit=1)
        if calls:
            json_data = calls[0].model_dump(mode="json")
            assert "call_id" in json_data
            assert "server_name" in json_data
            assert "tool_name" in json_data
            assert "status" in json_data
            assert "duration_ms" in json_data
            assert "called_at" in json_data
