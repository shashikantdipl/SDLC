"""Tests for agent REST API routes.

Routes are thin wrappers around AgentService.
Mock the service (tested separately with real DB in Phase 2).
Test: request parsing, service delegation, response envelope, error codes.
"""
import pytest
from aiohttp import web
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone

from api.app import create_app
from schemas.data_shapes import (
    AgentSummary,
    AgentDetail,
    AgentHealth,
    AgentVersion,
    AgentMaturity,
    AgentInvocationResult,
    AgentStatus,
    AgentPhase,
    MaturityLevel,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
API_KEY = "dev-api-key"
AUTH_HEADERS = {"X-API-Key": API_KEY}

NOW = datetime.now(timezone.utc)


def _make_summary(**overrides) -> AgentSummary:
    defaults = dict(
        agent_id="architect-agent",
        name="Architect Agent",
        phase=AgentPhase.DESIGN,
        archetype="planner",
        model="claude-opus-4",
        status=AgentStatus.ACTIVE,
        active_version="1.0.0",
        maturity=MaturityLevel.PROFESSIONAL,
    )
    defaults.update(overrides)
    return AgentSummary(**defaults)


def _make_detail(**overrides) -> AgentDetail:
    defaults = dict(
        agent_id="architect-agent",
        name="Architect Agent",
        phase=AgentPhase.DESIGN,
        archetype="planner",
        model="claude-opus-4",
        status=AgentStatus.ACTIVE,
        active_version="1.0.0",
        canary_version=None,
        canary_traffic_pct=0,
        previous_version=None,
        maturity=MaturityLevel.PROFESSIONAL,
        daily_cost_usd=Decimal("1.50"),
        invocations_today=42,
        last_invoked_at=NOW,
        description="Designs system architecture",
    )
    defaults.update(overrides)
    return AgentDetail(**defaults)


@pytest.fixture
async def app():
    """Create app without real DB — services will be mocked per-test."""
    application = await create_app(db_pool=None)
    return application


@pytest.fixture
async def client(aiohttp_client, app):
    """aiohttp test client."""
    return await aiohttp_client(app)


# ---------------------------------------------------------------------------
# I-020  GET /api/v1/agents — list agents
# ---------------------------------------------------------------------------
class TestListAgents:

    @pytest.mark.asyncio
    async def test_list_returns_200_with_agents(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_agents.return_value = [
            _make_summary(agent_id="agent-1"),
            _make_summary(agent_id="agent-2"),
        ]
        app["agent_service"] = mock_svc

        resp = await client.get("/api/v1/agents", headers=AUTH_HEADERS)
        assert resp.status == 200
        body = await resp.json()
        assert "data" in body
        assert len(body["data"]) == 2
        assert "meta" in body
        mock_svc.list_agents.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_passes_phase_filter(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_agents.return_value = []
        app["agent_service"] = mock_svc

        resp = await client.get(
            "/api/v1/agents?phase=design&status=active",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        mock_svc.list_agents.assert_called_once_with(
            phase="design", status="active",
        )

    @pytest.mark.asyncio
    async def test_list_empty_returns_empty_list(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_agents.return_value = []
        app["agent_service"] = mock_svc

        resp = await client.get("/api/v1/agents", headers=AUTH_HEADERS)
        body = await resp.json()
        assert body["data"] == []


# ---------------------------------------------------------------------------
# I-021  GET /api/v1/agents/{agent_id} — agent detail
# ---------------------------------------------------------------------------
class TestGetAgent:

    @pytest.mark.asyncio
    async def test_get_agent_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.get_agent.return_value = _make_detail()
        app["agent_service"] = mock_svc

        resp = await client.get(
            "/api/v1/agents/architect-agent",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["agent_id"] == "architect-agent"
        assert body["data"]["phase"] == "design"
        mock_svc.get_agent.assert_called_once_with(agent_id="architect-agent")

    @pytest.mark.asyncio
    async def test_get_agent_not_found_returns_404(self, client, app):
        from services.agent_service import AgentNotFoundError

        mock_svc = AsyncMock()
        mock_svc.get_agent.side_effect = AgentNotFoundError(
            "Agent 'missing-agent' not found"
        )
        app["agent_service"] = mock_svc

        resp = await client.get(
            "/api/v1/agents/missing-agent",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 404
        body = await resp.json()
        assert body["error"]["code"] == "AGENT_NOT_FOUND"


# ---------------------------------------------------------------------------
# I-022  POST /api/v1/agents/{agent_id}/invoke — invoke agent
# ---------------------------------------------------------------------------
class TestInvokeAgent:

    @pytest.mark.asyncio
    async def test_invoke_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.invoke_agent.return_value = AgentInvocationResult(
            invocation_id=uuid4(),
            agent_id="architect-agent",
            status="success",
            output="Architecture document generated",
            cost_usd=Decimal("0.05"),
            duration_ms=1200,
            quality_score=0.92,
        )
        app["agent_service"] = mock_svc

        resp = await client.post(
            "/api/v1/agents/architect-agent/invoke",
            json={"action": "generate", "params": {"doc": "03-ARCH"}},
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["agent_id"] == "architect-agent"
        assert body["data"]["status"] == "success"
        mock_svc.invoke_agent.assert_called_once_with(
            agent_id="architect-agent",
            action="generate",
            params={"doc": "03-ARCH"},
        )


# ---------------------------------------------------------------------------
# I-023  GET /api/v1/agents/{agent_id}/health — agent health
# ---------------------------------------------------------------------------
class TestGetAgentHealth:

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.get_agent_health.return_value = AgentHealth(
            agent_id="architect-agent",
            status=AgentStatus.ACTIVE,
            last_heartbeat=NOW,
            error_rate_1h=0.01,
            avg_latency_ms=150.0,
            invocations_1h=23,
        )
        app["agent_service"] = mock_svc

        resp = await client.get(
            "/api/v1/agents/architect-agent/health",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["agent_id"] == "architect-agent"
        assert body["data"]["status"] == "active"


# ---------------------------------------------------------------------------
# I-024  POST /api/v1/agents/{agent_id}/promote — promote agent
# ---------------------------------------------------------------------------
class TestPromoteAgent:

    @pytest.mark.asyncio
    async def test_promote_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.promote_agent.return_value = AgentVersion(
            agent_id="architect-agent",
            active_version="2.0.0",
            canary_version=None,
            canary_traffic_pct=0,
            previous_version="1.0.0",
            updated_at=NOW,
        )
        app["agent_service"] = mock_svc

        resp = await client.post(
            "/api/v1/agents/architect-agent/promote",
            json={"target_level": "expert", "promoted_by": "admin"},
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["active_version"] == "2.0.0"
        assert body["data"]["previous_version"] == "1.0.0"
        mock_svc.promote_agent.assert_called_once_with(
            agent_id="architect-agent",
            target_level="expert",
            promoted_by="admin",
        )

    @pytest.mark.asyncio
    async def test_promote_missing_agent_returns_404(self, client, app):
        from services.agent_service import AgentNotFoundError

        mock_svc = AsyncMock()
        mock_svc.promote_agent.side_effect = AgentNotFoundError("not found")
        app["agent_service"] = mock_svc

        resp = await client.post(
            "/api/v1/agents/missing-agent/promote",
            json={"target_level": "expert"},
            headers=AUTH_HEADERS,
        )
        assert resp.status == 404


# ---------------------------------------------------------------------------
# I-025  POST /api/v1/agents/{agent_id}/rollback
# ---------------------------------------------------------------------------
class TestRollbackAgent:

    @pytest.mark.asyncio
    async def test_rollback_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.rollback_agent.return_value = AgentVersion(
            agent_id="architect-agent",
            active_version="1.0.0",
            canary_version=None,
            canary_traffic_pct=0,
            previous_version="2.0.0",
            updated_at=NOW,
        )
        app["agent_service"] = mock_svc

        resp = await client.post(
            "/api/v1/agents/architect-agent/rollback",
            json={"target_version": "1.0.0", "reason": "regression"},
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["active_version"] == "1.0.0"
        mock_svc.rollback_agent.assert_called_once_with(
            agent_id="architect-agent",
            target_version="1.0.0",
            reason="regression",
        )


# ---------------------------------------------------------------------------
# I-026  PATCH /api/v1/agents/{agent_id}/canary — set canary weight
# ---------------------------------------------------------------------------
class TestSetCanary:

    @pytest.mark.asyncio
    async def test_set_canary_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.set_canary.return_value = AgentVersion(
            agent_id="architect-agent",
            active_version="1.0.0",
            canary_version="2.0.0",
            canary_traffic_pct=20,
            previous_version=None,
            updated_at=NOW,
        )
        app["agent_service"] = mock_svc

        resp = await client.patch(
            "/api/v1/agents/architect-agent/canary",
            json={"weight": 20},
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["canary_traffic_pct"] == 20
        mock_svc.set_canary.assert_called_once_with(
            agent_id="architect-agent",
            weight=20,
        )


# ---------------------------------------------------------------------------
# I-027  GET /api/v1/agents/{agent_id}/maturity
# ---------------------------------------------------------------------------
class TestGetAgentMaturity:

    @pytest.mark.asyncio
    async def test_maturity_returns_200(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.get_agent_maturity.return_value = AgentMaturity(
            agent_id="architect-agent",
            maturity=MaturityLevel.PROFESSIONAL,
            golden_tests_passed=45,
            adversarial_tests_passed=12,
            total_invocations=1500,
            avg_quality_score=0.89,
            promoted_at=NOW,
        )
        app["agent_service"] = mock_svc

        resp = await client.get(
            "/api/v1/agents/architect-agent/maturity",
            headers=AUTH_HEADERS,
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["maturity"] == "professional"
        assert body["data"]["golden_tests_passed"] == 45


# ---------------------------------------------------------------------------
# Auth middleware (agent routes)
# ---------------------------------------------------------------------------
class TestAgentAuthMiddleware:

    @pytest.mark.asyncio
    async def test_missing_api_key_returns_401(self, client, app):
        resp = await client.get("/api/v1/agents")
        assert resp.status == 401
        body = await resp.json()
        assert body["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_wrong_api_key_returns_403(self, client, app):
        resp = await client.get(
            "/api/v1/agents",
            headers={"X-API-Key": "wrong-key"},
        )
        assert resp.status == 403
        body = await resp.json()
        assert body["error"]["code"] == "FORBIDDEN"


# ---------------------------------------------------------------------------
# Response envelope (agent routes)
# ---------------------------------------------------------------------------
class TestAgentResponseEnvelope:

    @pytest.mark.asyncio
    async def test_success_envelope_structure(self, client, app):
        mock_svc = AsyncMock()
        mock_svc.list_agents.return_value = []
        app["agent_service"] = mock_svc

        resp = await client.get("/api/v1/agents", headers=AUTH_HEADERS)
        body = await resp.json()
        assert "data" in body
        assert "meta" in body
        assert "request_id" in body["meta"]
        assert "timestamp" in body["meta"]

    @pytest.mark.asyncio
    async def test_error_envelope_structure(self, client, app):
        from services.agent_service import AgentNotFoundError

        mock_svc = AsyncMock()
        mock_svc.get_agent.side_effect = AgentNotFoundError("not found")
        app["agent_service"] = mock_svc

        resp = await client.get(
            "/api/v1/agents/nonexistent",
            headers=AUTH_HEADERS,
        )
        body = await resp.json()
        assert "error" in body
        assert "code" in body["error"]
        assert "message" in body["error"]
        assert "meta" in body
        assert "request_id" in body["meta"]
        assert "timestamp" in body["meta"]
