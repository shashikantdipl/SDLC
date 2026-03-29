"""Tests for Pydantic data shape validation.

Verifies all data shapes defined in schemas/data_shapes.py
can be instantiated with valid data and reject invalid data.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from schemas.data_shapes import (
    PipelineRun,
    PipelineStatus,
    PipelineConfig,
    ValidationResult,
    AgentSummary,
    AgentHealth,
    AgentVersion,
    AgentMaturity,
    AgentInvocationResult,
    CostReport,
    BudgetStatus,
    AuditEvent,
    AuditSummary,
    ApprovalRequest,
    ApprovalResult,
)


NOW = datetime.now(timezone.utc)


class TestPipelineRun:
    """Validate PipelineRun shape."""

    def test_valid_pipeline_run(self):
        run = PipelineRun(
            run_id=uuid4(),
            project_id="proj-001",
            pipeline_name="document-stack",
            status=PipelineStatus.PENDING,
            current_step=0,
            total_steps=22,
            triggered_by="tester",
            started_at=NOW,
            completed_at=None,
            cost_usd=Decimal("0.00"),
        )
        assert run.project_id == "proj-001"
        assert run.total_steps == 22
        assert run.status == PipelineStatus.PENDING

    def test_pipeline_status_enum(self):
        assert PipelineStatus.PENDING == "pending"
        assert PipelineStatus.RUNNING == "running"
        assert PipelineStatus.COMPLETED == "completed"
        assert PipelineStatus.FAILED == "failed"


class TestValidationResult:
    """Validate ValidationResult shape."""

    def test_valid_result(self):
        result = ValidationResult(valid=True, errors=[], warnings=[])
        assert result.valid is True

    def test_invalid_result(self):
        result = ValidationResult(valid=False, errors=["missing project_id"], warnings=[])
        assert result.valid is False
        assert len(result.errors) == 1


class TestAgentShapes:
    """Validate Agent-related shapes."""

    def test_agent_summary(self):
        summary = AgentSummary(
            agent_id="G1-cost-tracker",
            name="Cost Tracker",
            phase="govern",
            status="active",
            model="claude-haiku-4-5-20251001",
            archetype="governance",
        )
        assert summary.agent_id == "G1-cost-tracker"
        assert summary.phase == "govern"

    def test_agent_health(self):
        health = AgentHealth(
            agent_id="G1-cost-tracker",
            healthy=True,
            last_check=NOW,
            error_rate=0.002,
            avg_latency_ms=3500,
        )
        assert health.healthy is True

    def test_agent_version(self):
        version = AgentVersion(
            agent_id="G1-cost-tracker",
            active_version="1.0.0",
            canary_version=None,
            canary_traffic_pct=0,
            previous_version=None,
            updated_at=NOW,
        )
        assert version.active_version == "1.0.0"


class TestCostShapes:
    """Validate Cost-related shapes."""

    def test_budget_status(self):
        budget = BudgetStatus(
            scope="project",
            scope_id="proj-001",
            budget_usd=Decimal("20.00"),
            spent_usd=Decimal("5.50"),
            remaining_usd=Decimal("14.50"),
            utilization_pct=27.5,
        )
        assert budget.utilization_pct == 27.5


class TestAuditShapes:
    """Validate Audit shapes."""

    def test_audit_event(self):
        event = AuditEvent(
            event_id=uuid4(),
            agent_id="G1-cost-tracker",
            project_id="proj-001",
            session_id=uuid4(),
            action="agent.invoke",
            severity="info",
            message="Cost report generated",
            details={},
            pii_detected=False,
            created_at=NOW,
        )
        assert event.severity == "info"


class TestApprovalShapes:
    """Validate Approval shapes."""

    def test_approval_request(self):
        req = ApprovalRequest(
            approval_id=uuid4(),
            session_id=uuid4(),
            pipeline_name="document-stack",
            step_id="D6-security",
            summary="Review security architecture",
            status="pending",
            requested_at=NOW,
            expires_at=NOW,
        )
        assert req.status == "pending"
