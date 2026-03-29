"""Tests for MCP agents-server tool handler layer.

Verifies: tool registration, input delegation, response formatting, error handling.
Services are mocked — we tested them with real DB in Phase 2.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from mcp_servers.agents_server.server import (
    ALL_TOOLS,
    call_tool,
    init_services,
    list_tools,
    server,
)
from schemas.data_shapes import (
    AgentDetail,
    AgentHealth,
    AgentInvocationResult,
    AgentMaturity,
    AgentPhase,
    AgentStatus,
    AgentSummary,
    AgentVersion,
    FleetHealth,
    MaturityLevel,
    PipelineConfig,
    PipelineDocument,
    PipelineRun,
    PipelineStatus,
    ValidationResult,
)
from services.agent_service import AgentNotFoundError
from services.pipeline_service import PipelineNotFoundError, PipelineStateError


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture(autouse=True)
def _inject_mock_services():
    """Inject mock services before each test and clean up after."""
    pipeline_svc = AsyncMock()
    agent_svc = AsyncMock()
    health_svc = AsyncMock()
    init_services(pipeline_svc, agent_svc, health_svc)
    yield pipeline_svc, agent_svc, health_svc
    init_services(None, None, None)


@pytest.fixture
def pipeline_svc(_inject_mock_services):
    return _inject_mock_services[0]


@pytest.fixture
def agent_svc(_inject_mock_services):
    return _inject_mock_services[1]


@pytest.fixture
def health_svc(_inject_mock_services):
    return _inject_mock_services[2]


def _sample_pipeline_run(**overrides) -> PipelineRun:
    defaults = dict(
        run_id=uuid4(),
        project_id="proj-1",
        pipeline_name="document-stack",
        status=PipelineStatus.PENDING,
        current_step=0,
        total_steps=22,
        triggered_by="test",
        started_at=datetime.now(tz=timezone.utc),
        completed_at=None,
        cost_usd=Decimal("0.00"),
    )
    defaults.update(overrides)
    return PipelineRun(**defaults)


def _sample_agent_summary(**overrides) -> AgentSummary:
    defaults = dict(
        agent_id="ag-roadmap-01",
        name="Roadmap Agent",
        phase=AgentPhase.GOVERN,
        archetype="generator",
        model="claude-sonnet-4-20250514",
        status=AgentStatus.ACTIVE,
        active_version="1.0.0",
        maturity=MaturityLevel.APPRENTICE,
    )
    defaults.update(overrides)
    return AgentSummary(**defaults)


def _sample_agent_detail(**overrides) -> AgentDetail:
    defaults = dict(
        agent_id="ag-roadmap-01",
        name="Roadmap Agent",
        phase=AgentPhase.GOVERN,
        archetype="generator",
        model="claude-sonnet-4-20250514",
        status=AgentStatus.ACTIVE,
        active_version="1.0.0",
        maturity=MaturityLevel.APPRENTICE,
    )
    defaults.update(overrides)
    return AgentDetail(**defaults)


# ======================================================================
# 1. Tool Registration
# ======================================================================

class TestToolRegistration:
    """Verify list_tools returns the correct set of tools."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_18_tools(self):
        tools = await list_tools()
        assert len(tools) == 18

    @pytest.mark.asyncio
    async def test_all_tool_names_are_unique(self):
        tools = await list_tools()
        names = [t.name for t in tools]
        assert len(names) == len(set(names)), f"Duplicate tool names: {names}"

    @pytest.mark.asyncio
    async def test_pipeline_tool_names(self):
        tools = await list_tools()
        names = {t.name for t in tools}
        expected = {
            "trigger_pipeline", "get_pipeline_status", "list_pipeline_runs",
            "resume_pipeline", "cancel_pipeline", "get_pipeline_documents",
            "retry_pipeline_step", "get_pipeline_config", "validate_pipeline_input",
        }
        assert expected.issubset(names)

    @pytest.mark.asyncio
    async def test_agent_tool_names(self):
        tools = await list_tools()
        names = {t.name for t in tools}
        expected = {
            "list_agents", "get_agent", "invoke_agent", "check_agent_health",
            "promote_agent_version", "rollback_agent_version",
            "set_canary_traffic", "get_agent_maturity",
        }
        assert expected.issubset(names)

    @pytest.mark.asyncio
    async def test_system_tool_names(self):
        tools = await list_tools()
        names = {t.name for t in tools}
        assert "get_fleet_health" in names

    @pytest.mark.asyncio
    async def test_all_tools_have_valid_json_schema(self):
        """Every tool inputSchema must be a dict with 'type': 'object' and 'properties'."""
        tools = await list_tools()
        for tool in tools:
            schema = tool.inputSchema
            assert isinstance(schema, dict), f"{tool.name}: inputSchema is not a dict"
            assert schema.get("type") == "object", f"{tool.name}: inputSchema type must be 'object'"
            assert "properties" in schema, f"{tool.name}: inputSchema missing 'properties'"
            assert "required" in schema, f"{tool.name}: inputSchema missing 'required'"

    @pytest.mark.asyncio
    async def test_all_tools_have_descriptions(self):
        tools = await list_tools()
        for tool in tools:
            assert tool.description, f"{tool.name}: missing description"
            assert len(tool.description) > 10, f"{tool.name}: description too short"


# ======================================================================
# 2. Pipeline Tool Handlers
# ======================================================================

class TestPipelineTools:
    """Verify pipeline tools delegate to PipelineService correctly."""

    @pytest.mark.asyncio
    async def test_trigger_pipeline_calls_service(self, pipeline_svc):
        run = _sample_pipeline_run()
        pipeline_svc.trigger.return_value = run

        result = await call_tool("trigger_pipeline", {
            "project_id": "proj-1",
            "pipeline_name": "document-stack",
            "brief": "Build the platform",
        })

        pipeline_svc.trigger.assert_awaited_once_with(
            project_id="proj-1",
            pipeline_name="document-stack",
            brief="Build the platform",
            triggered_by="system",
        )
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["project_id"] == "proj-1"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_trigger_pipeline_with_triggered_by(self, pipeline_svc):
        run = _sample_pipeline_run(triggered_by="alice")
        pipeline_svc.trigger.return_value = run

        await call_tool("trigger_pipeline", {
            "project_id": "proj-1",
            "pipeline_name": "document-stack",
            "brief": "Build it",
            "triggered_by": "alice",
        })

        pipeline_svc.trigger.assert_awaited_once_with(
            project_id="proj-1",
            pipeline_name="document-stack",
            brief="Build it",
            triggered_by="alice",
        )

    @pytest.mark.asyncio
    async def test_get_pipeline_status_calls_service(self, pipeline_svc):
        run_id = uuid4()
        run = _sample_pipeline_run(run_id=run_id)
        pipeline_svc.get_status.return_value = run

        result = await call_tool("get_pipeline_status", {"run_id": str(run_id)})

        pipeline_svc.get_status.assert_awaited_once_with(run_id=run_id)
        data = json.loads(result[0].text)
        assert data["run_id"] == str(run_id)

    @pytest.mark.asyncio
    async def test_list_pipeline_runs_calls_service(self, pipeline_svc):
        pipeline_svc.list_runs.return_value = [_sample_pipeline_run(), _sample_pipeline_run()]

        result = await call_tool("list_pipeline_runs", {"project_id": "proj-1"})

        pipeline_svc.list_runs.assert_awaited_once_with(
            project_id="proj-1", status=None, limit=50,
        )
        data = json.loads(result[0].text)
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_pipeline_config_calls_service(self, pipeline_svc):
        config = PipelineConfig(
            pipeline_name="document-stack",
            steps=["D0-roadmap"],
            cost_ceiling_usd=Decimal("25.00"),
            parallel_groups=[],
            gate_types={},
        )
        pipeline_svc.get_config.return_value = config

        result = await call_tool("get_pipeline_config", {"pipeline_name": "document-stack"})

        pipeline_svc.get_config.assert_awaited_once_with(pipeline_name="document-stack")
        data = json.loads(result[0].text)
        assert data["pipeline_name"] == "document-stack"

    @pytest.mark.asyncio
    async def test_validate_pipeline_input_calls_service(self, pipeline_svc):
        validation = ValidationResult(valid=True, errors=[], warnings=[])
        pipeline_svc.validate_input.return_value = validation

        result = await call_tool("validate_pipeline_input", {
            "project_id": "proj-1",
            "pipeline_name": "document-stack",
            "brief": "A valid brief text here",
        })

        pipeline_svc.validate_input.assert_awaited_once()
        data = json.loads(result[0].text)
        assert data["valid"] is True


# ======================================================================
# 3. Agent Tool Handlers
# ======================================================================

class TestAgentTools:
    """Verify agent tools delegate to AgentService correctly."""

    @pytest.mark.asyncio
    async def test_list_agents_calls_service(self, agent_svc):
        agent_svc.list_agents.return_value = [_sample_agent_summary()]

        result = await call_tool("list_agents", {})

        agent_svc.list_agents.assert_awaited_once_with(phase=None, status=None)
        data = json.loads(result[0].text)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["agent_id"] == "ag-roadmap-01"

    @pytest.mark.asyncio
    async def test_list_agents_with_filters(self, agent_svc):
        agent_svc.list_agents.return_value = []

        await call_tool("list_agents", {"phase": "govern", "status": "active"})

        agent_svc.list_agents.assert_awaited_once_with(phase="govern", status="active")

    @pytest.mark.asyncio
    async def test_get_agent_calls_service(self, agent_svc):
        agent_svc.get_agent.return_value = _sample_agent_detail()

        result = await call_tool("get_agent", {"agent_id": "ag-roadmap-01"})

        agent_svc.get_agent.assert_awaited_once_with(agent_id="ag-roadmap-01")
        data = json.loads(result[0].text)
        assert data["agent_id"] == "ag-roadmap-01"

    @pytest.mark.asyncio
    async def test_invoke_agent_calls_service(self, agent_svc):
        invocation = AgentInvocationResult(
            invocation_id=uuid4(),
            agent_id="ag-roadmap-01",
            status="completed",
            output="Generated roadmap.",
            cost_usd=Decimal("0.05"),
            duration_ms=1200,
        )
        agent_svc.invoke_agent.return_value = invocation

        result = await call_tool("invoke_agent", {
            "agent_id": "ag-roadmap-01",
            "input_text": "Create a roadmap",
        })

        agent_svc.invoke_agent.assert_awaited_once_with(
            agent_id="ag-roadmap-01",
            input_text="Create a roadmap",
        )
        data = json.loads(result[0].text)
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_check_agent_health_calls_service(self, agent_svc):
        health = AgentHealth(
            agent_id="ag-roadmap-01",
            status=AgentStatus.ACTIVE,
            last_heartbeat=datetime.now(tz=timezone.utc),
        )
        agent_svc.check_health.return_value = health

        result = await call_tool("check_agent_health", {"agent_id": "ag-roadmap-01"})

        agent_svc.check_health.assert_awaited_once_with(agent_id="ag-roadmap-01")
        data = json.loads(result[0].text)
        assert data["agent_id"] == "ag-roadmap-01"
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_promote_agent_version_calls_service(self, agent_svc):
        version = AgentVersion(
            agent_id="ag-roadmap-01",
            active_version="2.0.0",
            previous_version="1.0.0",
            updated_at=datetime.now(tz=timezone.utc),
        )
        agent_svc.promote_version.return_value = version

        result = await call_tool("promote_agent_version", {
            "agent_id": "ag-roadmap-01",
            "new_version": "2.0.0",
        })

        agent_svc.promote_version.assert_awaited_once_with(
            agent_id="ag-roadmap-01", new_version="2.0.0",
        )
        data = json.loads(result[0].text)
        assert data["active_version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_get_agent_maturity_calls_service(self, agent_svc):
        maturity = AgentMaturity(
            agent_id="ag-roadmap-01",
            maturity=MaturityLevel.JOURNEYMAN,
            golden_tests_passed=10,
            adversarial_tests_passed=5,
            total_invocations=100,
            avg_quality_score=0.85,
        )
        agent_svc.get_maturity.return_value = maturity

        result = await call_tool("get_agent_maturity", {"agent_id": "ag-roadmap-01"})

        agent_svc.get_maturity.assert_awaited_once_with(agent_id="ag-roadmap-01")
        data = json.loads(result[0].text)
        assert data["maturity"] == "journeyman"


# ======================================================================
# 4. System Tool Handler
# ======================================================================

class TestSystemTools:
    """Verify system tools delegate to HealthService correctly."""

    @pytest.mark.asyncio
    async def test_get_fleet_health_calls_service(self, health_svc):
        fleet = FleetHealth(
            total_agents=48,
            healthy=45,
            degraded=2,
            error=1,
            inactive=0,
            fleet_cost_today_usd=Decimal("12.50"),
            fleet_budget_remaining_usd=Decimal("37.50"),
        )
        health_svc.get_fleet_health.return_value = fleet

        result = await call_tool("get_fleet_health", {})

        health_svc.get_fleet_health.assert_awaited_once()
        data = json.loads(result[0].text)
        assert data["total_agents"] == 48
        assert data["healthy"] == 45


# ======================================================================
# 5. Error Handling
# ======================================================================

class TestErrorHandling:
    """Verify structured error responses for all exception types."""

    @pytest.mark.asyncio
    async def test_pipeline_not_found_returns_structured_error(self, pipeline_svc):
        run_id = uuid4()
        pipeline_svc.get_status.side_effect = PipelineNotFoundError(run_id)

        result = await call_tool("get_pipeline_status", {"run_id": str(run_id)})

        data = json.loads(result[0].text)
        assert data["error"] is True
        assert data["code"] == "PIPELINE_NOT_FOUND"
        assert str(run_id) in data["message"]

    @pytest.mark.asyncio
    async def test_pipeline_state_error_returns_structured_error(self, pipeline_svc):
        run_id = uuid4()
        pipeline_svc.resume.side_effect = PipelineStateError(run_id, "completed", "resume")

        result = await call_tool("resume_pipeline", {"run_id": str(run_id)})

        data = json.loads(result[0].text)
        assert data["error"] is True
        assert data["code"] == "PIPELINE_STATE_ERROR"

    @pytest.mark.asyncio
    async def test_agent_not_found_returns_structured_error(self, agent_svc):
        agent_svc.get_agent.side_effect = AgentNotFoundError("ag-missing")

        result = await call_tool("get_agent", {"agent_id": "ag-missing"})

        data = json.loads(result[0].text)
        assert data["error"] is True
        assert data["code"] == "AGENT_NOT_FOUND"
        assert "ag-missing" in data["message"]

    @pytest.mark.asyncio
    async def test_internal_error_returns_structured_error(self, pipeline_svc):
        pipeline_svc.trigger.side_effect = RuntimeError("DB connection lost")

        result = await call_tool("trigger_pipeline", {
            "project_id": "proj-1",
            "pipeline_name": "document-stack",
            "brief": "test",
        })

        data = json.loads(result[0].text)
        assert data["error"] is True
        assert data["code"] == "INTERNAL_ERROR"
        assert "DB connection lost" in data["message"]

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self):
        result = await call_tool("nonexistent_tool", {})

        data = json.loads(result[0].text)
        assert data["error"] is True
        assert data["code"] == "UNKNOWN_TOOL"

    @pytest.mark.asyncio
    async def test_rollback_no_previous_version_returns_error(self, agent_svc):
        agent_svc.rollback_version.side_effect = ValueError("no previous version")

        result = await call_tool("rollback_agent_version", {"agent_id": "ag-roadmap-01"})

        data = json.loads(result[0].text)
        assert data["error"] is True
        assert data["code"] == "ROLLBACK_ERROR"

    @pytest.mark.asyncio
    async def test_invalid_canary_percentage_returns_error(self, agent_svc):
        agent_svc.set_canary_traffic.side_effect = ValueError("percentage must be 0-100")

        result = await call_tool("set_canary_traffic", {
            "agent_id": "ag-roadmap-01",
            "percentage": 150,
        })

        data = json.loads(result[0].text)
        assert data["error"] is True
        assert data["code"] == "INVALID_PERCENTAGE"
