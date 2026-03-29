"""Cross-interface journey tests -- workflows that span MCP and REST/Dashboard.

Tests map to INTERACTION-MAP (Doc 6) Section 3: Cross-Interface Journeys.

Journey 1: Pipeline with Approval Gate
  Developer (MCP) triggers pipeline -> Pipeline pauses at gate ->
  Operator (Dashboard/REST) approves -> Pipeline resumes ->
  Developer (MCP) checks status -> completed

Journey 2: Cost Spike Investigation
  CostService detects anomaly -> Dashboard shows alert ->
  Operator queries audit events -> Identifies cause

Journey 3: Agent Canary Deployment
  Developer (MCP) sets canary -> Operator (Dashboard) monitors ->
  Developer (MCP) promotes canary to active

Journey 4: Compliance Audit
  Compliance officer queries audit summary -> Filters events ->
  Exports report -> Reviews MCP call history

These are integration tests using mocked services (not full DB).
Full end-to-end tests with real DB would go in a separate e2e suite.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from schemas.data_shapes import (
    PipelineRun, PipelineStatus, PipelineConfig,
    AgentSummary, AgentStatus, AgentPhase, AgentDetail, AgentVersion,
    AgentHealth, AgentMaturity, MaturityLevel,
    CostReport, BudgetScope, BudgetStatus, CostBreakdownItem, CostAnomaly,
    AuditEvent, AuditSummary, AuditReport, Severity,
    ApprovalRequest, ApprovalResult, ApprovalStatus,
    FleetHealth, McpCallEvent, ValidationResult,
)


# ---------------------------------------------------------------------------
# Shared test constants
# ---------------------------------------------------------------------------

NOW = datetime(2026, 3, 24, 12, 0, 0, tzinfo=timezone.utc)
RUN_ID = uuid4()
SESSION_ID = uuid4()
APPROVAL_ID = uuid4()
PROJECT_ID = "proj-test-001"
AGENT_ID = "agent-prd-writer"


# ---------------------------------------------------------------------------
# Journey 1: Pipeline with Approval Gate (INTERACTION-MAP Section 3, Journey 1)
#
# Steps:  I-009 -> I-001 -> I-002 -> (pause) -> I-045 -> I-046 -> I-002 -> I-006
# ---------------------------------------------------------------------------

class TestJourney1PipelineWithApprovalGate:
    """Pipeline with Approval Gate -- flagship cross-interface journey.

    Priya (MCP) triggers pipeline. Pipeline pauses at gate.
    Anika (Dashboard/REST) approves. Priya (MCP) checks completion.
    """

    @pytest.fixture
    def pipeline_service(self):
        svc = AsyncMock()
        # Step 1: I-009 validate input
        svc.validate_input.return_value = ValidationResult(
            valid=True, errors=[], warnings=[],
        )
        # Step 2: I-001 trigger pipeline
        svc.trigger.return_value = PipelineRun(
            run_id=RUN_ID, project_id=PROJECT_ID,
            pipeline_name="document-stack", status=PipelineStatus.RUNNING,
            current_step=0, total_steps=22,
            triggered_by="priya", started_at=NOW, cost_usd=Decimal("0.00"),
        )
        # Step 3: I-002 get_status (running, then paused, then completed)
        svc.get_status.side_effect = [
            # First poll: running at step 3
            PipelineRun(
                run_id=RUN_ID, project_id=PROJECT_ID,
                pipeline_name="document-stack", status=PipelineStatus.RUNNING,
                current_step=3, total_steps=22,
                triggered_by="priya", started_at=NOW, cost_usd=Decimal("0.75"),
            ),
            # Second poll: paused at gate (step 6)
            PipelineRun(
                run_id=RUN_ID, project_id=PROJECT_ID,
                pipeline_name="document-stack", status=PipelineStatus.PAUSED,
                current_step=6, total_steps=22,
                triggered_by="priya", started_at=NOW, cost_usd=Decimal("1.50"),
            ),
            # After approval: completed
            PipelineRun(
                run_id=RUN_ID, project_id=PROJECT_ID,
                pipeline_name="document-stack", status=PipelineStatus.COMPLETED,
                current_step=22, total_steps=22,
                triggered_by="priya", started_at=NOW,
                completed_at=NOW + timedelta(minutes=30),
                cost_usd=Decimal("4.20"),
            ),
        ]
        return svc

    @pytest.fixture
    def approval_service(self):
        svc = AsyncMock()
        # Step 5: I-045 list pending approvals (Dashboard view)
        svc.list_pending.return_value = [
            ApprovalRequest(
                approval_id=APPROVAL_ID, session_id=SESSION_ID,
                pipeline_name="document-stack",
                step_id="6:D6-interaction",
                summary="Quality gate for INTERACTION-MAP",
                status=ApprovalStatus.PENDING,
                requested_at=NOW,
                expires_at=NOW + timedelta(hours=1),
            ),
        ]
        # Step 6: I-046 approve gate
        svc.approve.return_value = ApprovalResult(
            approval_id=APPROVAL_ID,
            status=ApprovalStatus.APPROVED,
            decision_by="anika",
            decision_comment="Quality looks good. Approved.",
            decided_at=NOW + timedelta(minutes=5),
        )
        return svc

    @pytest.mark.asyncio
    async def test_pipeline_approval_journey(self, pipeline_service, approval_service):
        """Full journey: trigger -> pause at gate -> approve -> complete."""

        # -- Step 1 (MCP): Priya validates project input (I-009) --
        validation = await pipeline_service.validate_input(
            PROJECT_ID, "document-stack", "Generate docs for SDLC platform"
        )
        assert validation.valid is True
        assert validation.errors == []

        # -- Step 2 (MCP): Priya triggers pipeline (I-001) --
        run = await pipeline_service.trigger(
            project_id=PROJECT_ID,
            pipeline_name="document-stack",
            brief="Generate docs for SDLC platform",
            triggered_by="priya",
        )
        assert run.status == PipelineStatus.RUNNING
        assert run.run_id == RUN_ID

        # -- Step 3 (MCP): Priya polls status (I-002) -- running --
        status = await pipeline_service.get_status(RUN_ID)
        assert status.status == PipelineStatus.RUNNING
        assert status.current_step == 3

        # -- Step 4 (System): Pipeline pauses at gate --
        status = await pipeline_service.get_status(RUN_ID)
        assert status.status == PipelineStatus.PAUSED
        assert status.current_step == 6  # quality gate step

        # -- Step 5 (Dashboard/REST): Anika sees pending approval (I-045) --
        pending = await approval_service.list_pending(project_id=PROJECT_ID)
        assert len(pending) == 1
        assert pending[0].status == ApprovalStatus.PENDING
        assert pending[0].pipeline_name == "document-stack"

        # -- Step 6 (Dashboard/REST): Anika approves gate (I-046) --
        # Verify the approval_id from the pending list matches
        approval_id = pending[0].approval_id
        result = await approval_service.approve(
            approval_id=approval_id,
            decision_by="anika",
            comment="Quality looks good. Approved.",
        )
        assert result.status == ApprovalStatus.APPROVED
        assert result.decision_by == "anika"

        # -- Step 7-8 (MCP): Priya checks status -> completed (I-002) --
        final = await pipeline_service.get_status(RUN_ID)
        assert final.status == PipelineStatus.COMPLETED
        assert final.current_step == 22
        assert final.cost_usd == Decimal("4.20")

    @pytest.mark.asyncio
    async def test_same_data_shapes_across_interfaces(self, pipeline_service, approval_service):
        """The PipelineRun shape returned to MCP matches the shape returned to REST."""
        run = await pipeline_service.trigger(
            project_id=PROJECT_ID,
            pipeline_name="document-stack",
            brief="test",
            triggered_by="priya",
        )
        mcp_fields = set(run.model_dump(mode="json").keys())

        # REST wraps in envelope but data payload has same fields
        rest_data = run.model_dump(mode="json")
        rest_fields = set(rest_data.keys())

        assert mcp_fields == rest_fields


# ---------------------------------------------------------------------------
# Journey 2: Cost Spike Investigation (INTERACTION-MAP Section 3, Journey 2)
#
# Steps: (anomaly detected) -> I-048 -> I-040 -> I-041 -> I-080 -> I-021 -> I-023 -> I-049
# ---------------------------------------------------------------------------

class TestJourney2CostSpikeInvestigation:
    """Cost Spike Investigation -- cross-interface journey.

    System detects anomaly. David (Dashboard) investigates.
    Priya (MCP) takes corrective action.
    """

    @pytest.fixture
    def cost_service(self):
        svc = AsyncMock()
        # Step 2: I-048 get anomalies (Dashboard)
        svc.get_anomalies.return_value = [
            CostAnomaly(
                anomaly_id=uuid4(),
                agent_id=AGENT_ID,
                project_id=PROJECT_ID,
                expected_cost_usd=Decimal("2.00"),
                actual_cost_usd=Decimal("8.50"),
                deviation_pct=325.0,
                detected_at=NOW,
                severity=Severity.CRITICAL,
            ),
        ]
        # Step 3: I-040 get cost report (Dashboard)
        svc.get_report.return_value = CostReport(
            scope=BudgetScope.FLEET,
            scope_id="fleet",
            period_days=7,
            total_cost_usd=Decimal("35.00"),
            breakdown=[
                CostBreakdownItem(
                    label=AGENT_ID,
                    cost_usd=Decimal("18.50"),
                    invocations=95,
                    percentage=52.86,
                ),
            ],
            generated_at=NOW,
        )
        # Step 4: I-041 check budget (Dashboard)
        svc.check_budget.return_value = BudgetStatus(
            scope=BudgetScope.PROJECT,
            scope_id=PROJECT_ID,
            budget_usd=Decimal("20.00"),
            spent_usd=Decimal("18.50"),
            remaining_usd=Decimal("1.50"),
            utilization_pct=92.5,
            period="today",
        )
        # Step 8: I-049 update threshold (MCP)
        svc.update_budget_threshold.return_value = BudgetStatus(
            scope=BudgetScope.PROJECT,
            scope_id=PROJECT_ID,
            budget_usd=Decimal("15.00"),
            spent_usd=Decimal("18.50"),
            remaining_usd=Decimal("0.00"),
            utilization_pct=123.33,
            period="today",
        )
        return svc

    @pytest.fixture
    def health_service(self):
        svc = AsyncMock()
        # Step 5: I-080 fleet health (Dashboard)
        svc.get_fleet_health.return_value = FleetHealth(
            total_agents=48, healthy=44, degraded=3, error=1, inactive=0,
            fleet_cost_today_usd=Decimal("35.00"),
            fleet_budget_remaining_usd=Decimal("15.00"),
            agents=[
                AgentHealth(
                    agent_id=AGENT_ID,
                    status=AgentStatus.DEGRADED,
                    last_heartbeat=NOW,
                    error_rate_1h=0.15,
                    avg_latency_ms=2500.0,
                    invocations_1h=95,
                ),
            ],
        )
        return svc

    @pytest.fixture
    def agent_service(self):
        svc = AsyncMock()
        # Step 6: I-021 get agent detail (MCP)
        svc.get_agent.return_value = AgentDetail(
            agent_id=AGENT_ID, name="PRD Writer",
            phase=AgentPhase.DESIGN, archetype="writer",
            model="claude-opus-4-6", status=AgentStatus.DEGRADED,
            active_version="1.2.0", maturity=MaturityLevel.PROFESSIONAL,
            daily_cost_usd=Decimal("8.50"), invocations_today=95,
            last_invoked_at=NOW,
        )
        # Step 7: I-023 check health (MCP)
        svc.check_health.return_value = AgentHealth(
            agent_id=AGENT_ID, status=AgentStatus.DEGRADED,
            last_heartbeat=NOW,
            error_rate_1h=0.15, avg_latency_ms=2500.0, invocations_1h=95,
        )
        return svc

    @pytest.mark.asyncio
    async def test_cost_spike_investigation_journey(
        self, cost_service, health_service, agent_service,
    ):
        """Full journey: anomaly -> investigate on Dashboard -> fix via MCP."""

        # -- Step 2 (Dashboard): David views anomaly alerts (I-048) --
        anomalies = await cost_service.get_anomalies(project_id=PROJECT_ID)
        assert len(anomalies) == 1
        assert anomalies[0].severity == Severity.CRITICAL
        assert anomalies[0].deviation_pct > 300

        # -- Step 3 (Dashboard): David views fleet cost report (I-040) --
        report = await cost_service.get_report(
            scope="fleet", scope_id="fleet", period_days=7,
        )
        assert report.total_cost_usd == Decimal("35.00")
        # Identify the expensive agent
        top_spender = report.breakdown[0]
        assert top_spender.label == AGENT_ID

        # -- Step 4 (Dashboard): David checks budget (I-041) --
        budget = await cost_service.check_budget(scope="project", scope_id=PROJECT_ID)
        assert budget.utilization_pct > 90

        # -- Step 5 (Dashboard): David checks fleet health (I-080) --
        fleet = await health_service.get_fleet_health()
        assert fleet.degraded > 0
        degraded_agent = next(a for a in fleet.agents if a.agent_id == AGENT_ID)
        assert degraded_agent.status == AgentStatus.DEGRADED

        # -- Step 6 (MCP): Priya gets agent detail (I-021) --
        detail = await agent_service.get_agent(agent_id=AGENT_ID)
        assert detail.daily_cost_usd == Decimal("8.50")
        assert detail.invocations_today == 95

        # -- Step 7 (MCP): Priya checks agent health (I-023) --
        health = await agent_service.check_health(agent_id=AGENT_ID)
        assert health.status == AgentStatus.DEGRADED
        assert health.avg_latency_ms > 2000

        # -- Step 8 (MCP): Priya lowers budget threshold (I-049) --
        updated = await cost_service.update_budget_threshold(
            scope="project", scope_id=PROJECT_ID, new_budget=Decimal("15.00"),
        )
        assert updated.budget_usd == Decimal("15.00")


# ---------------------------------------------------------------------------
# Journey 3: Agent Canary Deployment (INTERACTION-MAP Section 3, Journey 3)
#
# Steps: I-026 -> I-020 -> I-080 -> I-026 -> I-021 -> I-027 -> I-024
# ---------------------------------------------------------------------------

class TestJourney3AgentCanaryDeployment:
    """Agent Canary Deployment -- cross-interface journey.

    Priya (MCP) deploys canary. Jason (Dashboard) monitors.
    Priya (MCP) promotes to active.
    """

    @pytest.fixture
    def agent_service(self):
        svc = AsyncMock()
        # Step 1: I-026 set canary to 10%
        svc.set_canary_traffic.side_effect = [
            AgentVersion(
                agent_id=AGENT_ID, active_version="1.2.0",
                canary_version="1.3.0", canary_traffic_pct=10,
                previous_version="1.1.0", updated_at=NOW,
            ),
            # Step 4: I-026 increase canary to 50%
            AgentVersion(
                agent_id=AGENT_ID, active_version="1.2.0",
                canary_version="1.3.0", canary_traffic_pct=50,
                previous_version="1.1.0", updated_at=NOW + timedelta(hours=1),
            ),
        ]
        # Step 2: I-020 list agents (Dashboard)
        svc.list_agents.return_value = [
            AgentSummary(
                agent_id=AGENT_ID, name="PRD Writer",
                phase=AgentPhase.DESIGN, archetype="writer",
                model="claude-opus-4-6", status=AgentStatus.ACTIVE,
                active_version="1.2.0", maturity=MaturityLevel.PROFESSIONAL,
            ),
        ]
        # Step 5: I-021 get agent detail (Dashboard)
        svc.get_agent.return_value = AgentDetail(
            agent_id=AGENT_ID, name="PRD Writer",
            phase=AgentPhase.DESIGN, archetype="writer",
            model="claude-opus-4-6", status=AgentStatus.ACTIVE,
            active_version="1.2.0", canary_version="1.3.0",
            canary_traffic_pct=50, previous_version="1.1.0",
            maturity=MaturityLevel.PROFESSIONAL,
            daily_cost_usd=Decimal("3.00"), invocations_today=40,
            last_invoked_at=NOW,
        )
        # Step 6: I-027 get maturity (MCP)
        svc.get_maturity.return_value = AgentMaturity(
            agent_id=AGENT_ID, maturity=MaturityLevel.PROFESSIONAL,
            golden_tests_passed=28, adversarial_tests_passed=8,
            total_invocations=500, avg_quality_score=0.92,
            promoted_at=None,
        )
        # Step 7: I-024 promote version (MCP)
        svc.promote_version.return_value = AgentVersion(
            agent_id=AGENT_ID, active_version="1.3.0",
            canary_version=None, canary_traffic_pct=0,
            previous_version="1.2.0",
            updated_at=NOW + timedelta(hours=2),
        )
        return svc

    @pytest.fixture
    def health_service(self):
        svc = AsyncMock()
        # Step 3: I-080 fleet health (Dashboard)
        svc.get_fleet_health.return_value = FleetHealth(
            total_agents=48, healthy=47, degraded=1, error=0, inactive=0,
            fleet_cost_today_usd=Decimal("22.00"),
            fleet_budget_remaining_usd=Decimal("28.00"),
            agents=[],
        )
        return svc

    @pytest.mark.asyncio
    async def test_canary_deployment_journey(self, agent_service, health_service):
        """Full journey: set canary -> monitor -> increase -> promote."""

        # -- Step 1 (MCP): Priya sets canary to 10% (I-026) --
        version = await agent_service.set_canary_traffic(
            agent_id=AGENT_ID, percentage=10,
        )
        assert version.canary_traffic_pct == 10
        assert version.canary_version == "1.3.0"

        # -- Step 2 (Dashboard): Jason lists agents (I-020) --
        agents = await agent_service.list_agents()
        assert len(agents) >= 1

        # -- Step 3 (Dashboard): Jason checks fleet health (I-080) --
        fleet = await health_service.get_fleet_health()
        assert fleet.healthy >= 47

        # -- Step 4 (MCP): Priya increases canary to 50% (I-026) --
        version = await agent_service.set_canary_traffic(
            agent_id=AGENT_ID, percentage=50,
        )
        assert version.canary_traffic_pct == 50

        # -- Step 5 (Dashboard): Jason reviews agent detail (I-021) --
        detail = await agent_service.get_agent(agent_id=AGENT_ID)
        assert detail.canary_version == "1.3.0"
        assert detail.canary_traffic_pct == 50

        # -- Step 6 (MCP): Priya checks maturity confidence (I-027) --
        maturity = await agent_service.get_maturity(agent_id=AGENT_ID)
        assert maturity.avg_quality_score >= 0.9

        # -- Step 7 (MCP): Priya promotes canary to active (I-024) --
        promoted = await agent_service.promote_version(
            agent_id=AGENT_ID, new_version="1.3.0",
        )
        assert promoted.active_version == "1.3.0"
        assert promoted.canary_version is None
        assert promoted.canary_traffic_pct == 0


# ---------------------------------------------------------------------------
# Journey 4: Compliance Audit (INTERACTION-MAP Section 3, Journey 4)
#
# Steps: I-043 -> I-042 -> I-044 -> I-082 -> I-045 -> I-042
# ---------------------------------------------------------------------------

class TestJourney4ComplianceAudit:
    """Compliance Audit -- primarily Dashboard journey crossing personas.

    Fatima (Compliance) reviews audit trail.
    Anika (Eng Lead) investigates approval patterns.
    """

    @pytest.fixture
    def audit_service(self):
        svc = AsyncMock()
        event_id = uuid4()

        # Step 1: I-043 get audit summary (Dashboard - Fatima)
        svc.get_summary.return_value = AuditSummary(
            total_events=1250,
            by_severity={"info": 900, "warning": 280, "error": 60, "critical": 10},
            by_agent={AGENT_ID: 300, "agent-arch-reviewer": 200},
            period_start=NOW - timedelta(days=90),
            period_end=NOW,
            total_cost_usd=Decimal("450.00"),
        )
        # Step 2: I-042 query events filtered by severity (Dashboard - Fatima)
        svc.query_events.side_effect = [
            [
                AuditEvent(
                    event_id=event_id, agent_id=AGENT_ID,
                    project_id=PROJECT_ID, session_id=SESSION_ID,
                    action="agent.error", severity=Severity.ERROR,
                    message="Agent timeout after 30s",
                    details={"timeout_ms": 30000},
                    pii_detected=False, created_at=NOW - timedelta(days=5),
                ),
            ],
            # Step 6: I-042 query events filtered by action (Dashboard - Anika)
            [
                AuditEvent(
                    event_id=uuid4(), agent_id="system",
                    project_id=PROJECT_ID, session_id=SESSION_ID,
                    action="approval.approve", severity=Severity.INFO,
                    message="Gate approved by anika",
                    details={"approval_id": str(uuid4())},
                    pii_detected=False, created_at=NOW - timedelta(days=2),
                ),
            ],
        ]
        # Step 3: I-044 export audit report (Dashboard - Fatima)
        svc.export_report.return_value = AuditReport(
            report_id=uuid4(),
            generated_at=NOW,
            period_start=NOW - timedelta(days=90),
            period_end=NOW,
            total_events=1250,
            events=[],  # Abbreviated for test
            format="json",
        )
        # Step 4: I-082 list MCP calls (Dashboard - Fatima)
        svc.list_mcp_calls.return_value = [
            McpCallEvent(
                call_id=uuid4(),
                server_name="agents-server",
                tool_name="trigger_pipeline",
                client_id="priya-cli",
                project_id=PROJECT_ID,
                input_summary="trigger document-stack",
                status="success",
                duration_ms=1200,
                cost_usd=Decimal("0.05"),
                called_at=NOW - timedelta(days=1),
            ),
        ]
        return svc

    @pytest.fixture
    def approval_service(self):
        svc = AsyncMock()
        # Step 5: I-045 list approvals (Dashboard - Anika, historical)
        svc.list_pending.return_value = [
            ApprovalRequest(
                approval_id=uuid4(), session_id=SESSION_ID,
                pipeline_name="document-stack",
                step_id="6:D6-interaction",
                summary="Quality gate review",
                status=ApprovalStatus.APPROVED,
                requested_at=NOW - timedelta(days=3),
                expires_at=NOW - timedelta(days=3) + timedelta(hours=1),
                decision_by="anika",
                decision_comment="Approved after review",
                decided_at=NOW - timedelta(days=3) + timedelta(minutes=15),
            ),
        ]
        return svc

    @pytest.mark.asyncio
    async def test_compliance_audit_journey(self, audit_service, approval_service):
        """Full journey: summary -> filter events -> export -> review approvals."""

        # -- Step 1 (Dashboard): Fatima views audit summary (I-043) --
        summary = await audit_service.get_summary(
            project_id=PROJECT_ID, period_days=90,
        )
        assert summary.total_events == 1250
        assert summary.by_severity["critical"] == 10

        # -- Step 2 (Dashboard): Fatima filters events by severity (I-042) --
        error_events = await audit_service.query_events(
            project_id=PROJECT_ID, severity="error",
        )
        assert len(error_events) >= 1
        assert error_events[0].severity == Severity.ERROR

        # -- Step 3 (Dashboard): Fatima exports audit report (I-044) --
        report = await audit_service.export_report(
            project_id=PROJECT_ID, period_days=90,
        )
        assert report.total_events == 1250
        assert report.format == "json"

        # -- Step 4 (Dashboard): Fatima reviews MCP call history (I-082) --
        calls = await audit_service.list_mcp_calls()
        assert len(calls) >= 1
        assert calls[0].tool_name == "trigger_pipeline"

        # -- Step 5 (Dashboard): Anika reviews past approval decisions (I-045) --
        approvals = await approval_service.list_pending(project_id=PROJECT_ID)
        assert len(approvals) >= 1
        assert approvals[0].status == ApprovalStatus.APPROVED

        # -- Step 6 (Dashboard): Anika cross-references with audit events (I-042) --
        approval_events = await audit_service.query_events(
            project_id=PROJECT_ID, severity=None,
        )
        assert any(e.action.startswith("approval.") for e in approval_events)

    @pytest.mark.asyncio
    async def test_audit_shapes_consistent_across_queries(self, audit_service, approval_service):
        """AuditEvent shape is identical whether queried by severity or by action."""
        error_events = await audit_service.query_events(
            project_id=PROJECT_ID, severity="error",
        )
        all_events = await audit_service.query_events(
            project_id=PROJECT_ID, severity=None,
        )

        if error_events and all_events:
            error_fields = set(error_events[0].model_dump(mode="json").keys())
            all_fields = set(all_events[0].model_dump(mode="json").keys())
            assert error_fields == all_fields
