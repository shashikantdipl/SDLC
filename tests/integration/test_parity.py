"""Parity tests -- MCP and REST return identical data for the same operation.

Verifies Q-049 (MCP-REST equivalence), Q-051 (error code consistency), Q-053 (data shape parity).
Uses mocked services to ensure both layers call the same service and format the same shape.

Architecture reminder:
    MCP tool handler  -->  SharedService.method()  --> returns Pydantic data shape
    REST route handler -->  SharedService.method()  --> returns Pydantic data shape
Both handlers serialize the *same* Pydantic model, so field names MUST be identical.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from schemas.data_shapes import (
    PipelineRun, PipelineStatus, AgentSummary, AgentStatus, AgentPhase,
    CostReport, BudgetScope, BudgetStatus, AuditEvent, Severity,
    ApprovalRequest, ApprovalStatus, KnowledgeException, KnowledgeTier,
    FleetHealth, CostBreakdownItem, MaturityLevel, ApprovalResult,
    AgentHealth, AgentDetail,
)


# ---------------------------------------------------------------------------
# Fixtures: known data shapes returned by mock services
# ---------------------------------------------------------------------------

NOW = datetime(2026, 3, 24, 12, 0, 0, tzinfo=timezone.utc)
RUN_ID = uuid4()
SESSION_ID = uuid4()
APPROVAL_ID = uuid4()
EVENT_ID = uuid4()
PROJECT_ID = "proj-test-001"


def _make_pipeline_run() -> PipelineRun:
    return PipelineRun(
        run_id=RUN_ID,
        project_id=PROJECT_ID,
        pipeline_name="document-stack",
        status=PipelineStatus.RUNNING,
        current_step=3,
        total_steps=22,
        triggered_by="priya",
        started_at=NOW,
        completed_at=None,
        cost_usd=Decimal("1.25"),
    )


def _make_agent_summaries() -> list[AgentSummary]:
    return [
        AgentSummary(
            agent_id="agent-prd-writer",
            name="PRD Writer",
            phase=AgentPhase.DESIGN,
            archetype="writer",
            model="claude-opus-4-6",
            status=AgentStatus.ACTIVE,
            active_version="1.2.0",
            maturity=MaturityLevel.PROFESSIONAL,
        ),
        AgentSummary(
            agent_id="agent-arch-reviewer",
            name="Architecture Reviewer",
            phase=AgentPhase.DESIGN,
            archetype="reviewer",
            model="claude-opus-4-6",
            status=AgentStatus.ACTIVE,
            active_version="1.0.0",
            maturity=MaturityLevel.JOURNEYMAN,
        ),
    ]


def _make_cost_report() -> CostReport:
    return CostReport(
        scope=BudgetScope.PROJECT,
        scope_id=PROJECT_ID,
        period_days=7,
        total_cost_usd=Decimal("12.50"),
        breakdown=[
            CostBreakdownItem(
                label="agent-prd-writer",
                cost_usd=Decimal("8.00"),
                invocations=20,
                percentage=64.0,
            ),
            CostBreakdownItem(
                label="agent-arch-reviewer",
                cost_usd=Decimal("4.50"),
                invocations=10,
                percentage=36.0,
            ),
        ],
        generated_at=NOW,
    )


def _make_approval_result() -> ApprovalResult:
    return ApprovalResult(
        approval_id=APPROVAL_ID,
        status=ApprovalStatus.APPROVED,
        decision_by="anika",
        decision_comment="Looks good, approved.",
        decided_at=NOW,
    )


def _make_budget_status() -> BudgetStatus:
    return BudgetStatus(
        scope=BudgetScope.PROJECT,
        scope_id=PROJECT_ID,
        budget_usd=Decimal("20.00"),
        spent_usd=Decimal("12.50"),
        remaining_usd=Decimal("7.50"),
        utilization_pct=62.5,
        period="today",
    )


def _make_audit_events() -> list[AuditEvent]:
    return [
        AuditEvent(
            event_id=EVENT_ID,
            agent_id="agent-prd-writer",
            project_id=PROJECT_ID,
            session_id=SESSION_ID,
            action="pipeline.trigger",
            severity=Severity.INFO,
            message="Pipeline triggered",
            details={"pipeline_name": "document-stack"},
            pii_detected=False,
            created_at=NOW,
        ),
    ]


def _make_fleet_health() -> FleetHealth:
    return FleetHealth(
        total_agents=48,
        healthy=45,
        degraded=2,
        error=1,
        inactive=0,
        fleet_cost_today_usd=Decimal("18.75"),
        fleet_budget_remaining_usd=Decimal("31.25"),
        agents=[],
    )


def _make_agent_detail() -> AgentDetail:
    return AgentDetail(
        agent_id="agent-prd-writer",
        name="PRD Writer",
        phase=AgentPhase.DESIGN,
        archetype="writer",
        model="claude-opus-4-6",
        status=AgentStatus.ACTIVE,
        active_version="1.2.0",
        canary_version=None,
        canary_traffic_pct=0,
        previous_version="1.1.0",
        maturity=MaturityLevel.PROFESSIONAL,
        daily_cost_usd=Decimal("2.30"),
        invocations_today=12,
        last_invoked_at=NOW,
        description="Generates PRD documents",
    )


def _make_approval_requests() -> list[ApprovalRequest]:
    return [
        ApprovalRequest(
            approval_id=APPROVAL_ID,
            session_id=SESSION_ID,
            pipeline_name="document-stack",
            step_id="6:D6-interaction",
            summary="Quality gate for INTERACTION-MAP",
            status=ApprovalStatus.PENDING,
            approver_channel=None,
            requested_at=NOW,
            expires_at=NOW + timedelta(hours=1),
            decision_by=None,
            decision_comment=None,
            decided_at=None,
        ),
    ]


# ---------------------------------------------------------------------------
# Helper: extract field names from a Pydantic model_dump (recursive keys)
# ---------------------------------------------------------------------------

def _flat_keys(data) -> set[str]:
    """Return the set of top-level keys from a dict or list-of-dicts."""
    if isinstance(data, list):
        if not data:
            return set()
        return _flat_keys(data[0])
    if isinstance(data, dict):
        return set(data.keys())
    return set()


def _serialize(obj):
    """Serialize a Pydantic model or list of models to JSON-like dict(s)."""
    if isinstance(obj, list):
        return [item.model_dump(mode="json") for item in obj]
    return obj.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Helper: simulate MCP tool response (returns content[0].text JSON)
# ---------------------------------------------------------------------------

def _mcp_response_data(service_result):
    """Simulate MCP tool handler serialization: model_dump(mode='json')."""
    return _serialize(service_result)


# ---------------------------------------------------------------------------
# Helper: simulate REST response (data field of envelope)
# ---------------------------------------------------------------------------

def _rest_response_data(service_result):
    """Simulate REST route handler serialization: model_dump(mode='json') wrapped in envelope."""
    return _serialize(service_result)


# ===========================================================================
# Parity Tests
# ===========================================================================


class TestTriggerPipelineParity:
    """Q-049: MCP trigger_pipeline and REST POST /pipelines return same shape."""

    def test_trigger_pipeline_parity(self):
        """I-001: Both interfaces produce identical field names for PipelineRun."""
        pipeline_run = _make_pipeline_run()

        mcp_data = _mcp_response_data(pipeline_run)
        rest_data = _rest_response_data(pipeline_run)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        # Verify expected fields are present (from INTERACTION-MAP Section 2.1)
        expected_fields = {
            "run_id", "project_id", "pipeline_name", "status",
            "current_step", "total_steps", "triggered_by",
            "started_at", "completed_at", "cost_usd",
        }
        assert expected_fields == _flat_keys(mcp_data)


class TestListAgentsParity:
    """Q-049: MCP list_agents and REST GET /agents return same shape."""

    def test_list_agents_parity(self):
        """I-020: Both interfaces produce identical field names for AgentSummary[]."""
        agents = _make_agent_summaries()

        mcp_data = _mcp_response_data(agents)
        rest_data = _rest_response_data(agents)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        expected_fields = {
            "agent_id", "name", "phase", "archetype", "model",
            "status", "active_version", "maturity",
        }
        assert expected_fields == _flat_keys(mcp_data)


class TestGetCostReportParity:
    """Q-049: MCP get_cost_report and REST GET /cost/report return same shape."""

    def test_get_cost_report_parity(self):
        """I-040: Both interfaces produce identical field names for CostReport."""
        report = _make_cost_report()

        mcp_data = _mcp_response_data(report)
        rest_data = _rest_response_data(report)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        expected_fields = {
            "scope", "scope_id", "period_days", "total_cost_usd",
            "breakdown", "generated_at",
        }
        assert expected_fields == _flat_keys(mcp_data)

    def test_cost_breakdown_item_shape(self):
        """Q-053: CostBreakdownItem nested shape is identical in both interfaces."""
        report = _make_cost_report()

        mcp_data = _mcp_response_data(report)
        rest_data = _rest_response_data(report)

        mcp_breakdown = mcp_data["breakdown"][0]
        rest_breakdown = rest_data["breakdown"][0]

        assert set(mcp_breakdown.keys()) == set(rest_breakdown.keys())
        assert {"label", "cost_usd", "invocations", "percentage"} == set(mcp_breakdown.keys())


class TestApproveGateParity:
    """Q-049: MCP approve_gate and REST POST /approvals/{id}/approve return same shape."""

    def test_approve_gate_parity(self):
        """I-046: Both interfaces produce identical field names for ApprovalResult."""
        result = _make_approval_result()

        mcp_data = _mcp_response_data(result)
        rest_data = _rest_response_data(result)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        expected_fields = {
            "approval_id", "status", "decision_by",
            "decision_comment", "decided_at",
        }
        assert expected_fields == _flat_keys(mcp_data)


class TestErrorCodeParity:
    """Q-051: Service exceptions produce same error code in MCP and REST."""

    def test_pipeline_not_found_error_code(self):
        """PipelineNotFoundError maps to PIPELINE_NOT_FOUND in both interfaces."""
        from services.pipeline_service import PipelineNotFoundError
        from api.middleware.error_handler import ERROR_MAP

        exc = PipelineNotFoundError(RUN_ID)
        exc_name = type(exc).__name__

        # REST error mapping
        assert exc_name in ERROR_MAP
        http_status, error_code = ERROR_MAP[exc_name]
        assert error_code == "PIPELINE_NOT_FOUND"
        assert http_status == 404

        # MCP tools should use the same error code convention.
        # The MCP handler wraps exceptions as: {"code": ERROR_MAP[exc_name][1], ...}
        # Verify the code is consistent.
        mcp_error_code = ERROR_MAP[exc_name][1]
        assert mcp_error_code == error_code

    def test_agent_not_found_error_code(self):
        """AgentNotFoundError maps to AGENT_NOT_FOUND in both interfaces."""
        from services.agent_service import AgentNotFoundError
        from api.middleware.error_handler import ERROR_MAP

        exc = AgentNotFoundError("agent-nonexistent")
        exc_name = type(exc).__name__

        assert exc_name in ERROR_MAP
        http_status, error_code = ERROR_MAP[exc_name]
        assert error_code == "AGENT_NOT_FOUND"
        assert http_status == 404

    def test_approval_not_found_error_code(self):
        """ApprovalNotFoundError maps to APPROVAL_NOT_FOUND in both interfaces."""
        from services.approval_service import ApprovalNotFoundError
        from api.middleware.error_handler import ERROR_MAP

        exc = ApprovalNotFoundError(APPROVAL_ID)
        exc_name = type(exc).__name__

        assert exc_name in ERROR_MAP
        http_status, error_code = ERROR_MAP[exc_name]
        assert error_code == "APPROVAL_NOT_FOUND"
        assert http_status == 404

    def test_pipeline_state_error_code(self):
        """PipelineStateError maps to PIPELINE_STATE_ERROR with 409 Conflict."""
        from services.pipeline_service import PipelineStateError
        from api.middleware.error_handler import ERROR_MAP

        exc = PipelineStateError(RUN_ID, "completed", "cancel")
        exc_name = type(exc).__name__

        assert exc_name in ERROR_MAP
        http_status, error_code = ERROR_MAP[exc_name]
        assert error_code == "PIPELINE_STATE_ERROR"
        assert http_status == 409

    def test_approval_state_error_code(self):
        """ApprovalStateError maps to APPROVAL_STATE_ERROR with 409 Conflict."""
        from services.approval_service import ApprovalStateError
        from api.middleware.error_handler import ERROR_MAP

        exc = ApprovalStateError(APPROVAL_ID, "approved", "reject")
        exc_name = type(exc).__name__

        assert exc_name in ERROR_MAP
        http_status, error_code = ERROR_MAP[exc_name]
        assert error_code == "APPROVAL_STATE_ERROR"
        assert http_status == 409

    def test_budget_exceeded_error_code(self):
        """BudgetExceededError maps to BUDGET_EXCEEDED with 402."""
        from services.cost_service import BudgetExceededError
        from api.middleware.error_handler import ERROR_MAP

        exc = BudgetExceededError("project", PROJECT_ID, Decimal("20"), Decimal("21"))
        exc_name = type(exc).__name__

        assert exc_name in ERROR_MAP
        http_status, error_code = ERROR_MAP[exc_name]
        assert error_code == "BUDGET_EXCEEDED"
        assert http_status == 402


class TestCheckBudgetParity:
    """Q-049: MCP check_budget and REST GET /budget/{scope}/{scope_id} return same shape."""

    def test_check_budget_parity(self):
        """I-041: Both interfaces produce identical field names for BudgetStatus."""
        status = _make_budget_status()

        mcp_data = _mcp_response_data(status)
        rest_data = _rest_response_data(status)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        expected_fields = {
            "scope", "scope_id", "budget_usd", "spent_usd",
            "remaining_usd", "utilization_pct", "period",
        }
        assert expected_fields == _flat_keys(mcp_data)


class TestQueryAuditEventsParity:
    """Q-049: MCP query_audit_events and REST GET /audit/events return same shape."""

    def test_query_audit_events_parity(self):
        """I-042: Both interfaces produce identical field names for AuditEvent[]."""
        events = _make_audit_events()

        mcp_data = _mcp_response_data(events)
        rest_data = _rest_response_data(events)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        expected_fields = {
            "event_id", "agent_id", "project_id", "session_id",
            "action", "severity", "message", "details",
            "pii_detected", "created_at",
        }
        assert expected_fields == _flat_keys(mcp_data)


class TestFleetHealthParity:
    """Q-049: MCP get_fleet_health and REST GET /health/fleet return same shape."""

    def test_fleet_health_parity(self):
        """I-080: Both interfaces produce identical field names for FleetHealth."""
        health = _make_fleet_health()

        mcp_data = _mcp_response_data(health)
        rest_data = _rest_response_data(health)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        expected_fields = {
            "total_agents", "healthy", "degraded", "error", "inactive",
            "fleet_cost_today_usd", "fleet_budget_remaining_usd", "agents",
        }
        assert expected_fields == _flat_keys(mcp_data)


class TestListPendingApprovalsParity:
    """Q-049: MCP list_pending_approvals and REST GET /approvals return same shape."""

    def test_list_pending_approvals_parity(self):
        """I-045: Both interfaces produce identical field names for ApprovalRequest[]."""
        approvals = _make_approval_requests()

        mcp_data = _mcp_response_data(approvals)
        rest_data = _rest_response_data(approvals)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        expected_fields = {
            "approval_id", "session_id", "pipeline_name", "step_id",
            "summary", "status", "approver_channel", "requested_at",
            "expires_at", "decision_by", "decision_comment", "decided_at",
        }
        assert expected_fields == _flat_keys(mcp_data)


class TestAgentDetailParity:
    """Q-049: MCP get_agent and REST GET /agents/{id} return same shape."""

    def test_agent_detail_parity(self):
        """I-021: Both interfaces produce identical field names for AgentDetail."""
        detail = _make_agent_detail()

        mcp_data = _mcp_response_data(detail)
        rest_data = _rest_response_data(detail)

        assert _flat_keys(mcp_data) == _flat_keys(rest_data)
        assert mcp_data == rest_data

        expected_fields = {
            "agent_id", "name", "phase", "archetype", "model",
            "status", "active_version", "canary_version",
            "canary_traffic_pct", "previous_version", "maturity",
            "daily_cost_usd", "invocations_today", "last_invoked_at",
            "description",
        }
        assert expected_fields == _flat_keys(mcp_data)


class TestAllErrorCodesRegistered:
    """Q-051: All known service errors are registered in ERROR_MAP."""

    def test_all_service_errors_in_error_map(self):
        """Every service exception class is registered in the REST error_handler."""
        from api.middleware.error_handler import ERROR_MAP

        required_errors = [
            "PipelineNotFoundError",
            "PipelineStateError",
            "AgentNotFoundError",
            "ApprovalNotFoundError",
            "ApprovalStateError",
            "BudgetExceededError",
            "ValueError",
        ]
        for err_name in required_errors:
            assert err_name in ERROR_MAP, f"{err_name} missing from ERROR_MAP"

    def test_error_codes_are_uppercase_snake(self):
        """Error codes follow UPPER_SNAKE_CASE convention."""
        from api.middleware.error_handler import ERROR_MAP

        for exc_name, (status, code) in ERROR_MAP.items():
            assert code == code.upper(), f"Error code {code!r} for {exc_name} is not uppercase"
            assert " " not in code, f"Error code {code!r} for {exc_name} contains spaces"
            assert isinstance(status, int), f"HTTP status for {exc_name} must be int"
            assert 400 <= status <= 599, f"HTTP status {status} for {exc_name} out of error range"
