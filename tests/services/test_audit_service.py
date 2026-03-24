"""Tests for AuditService — audit logging and compliance reporting.

Implements I-042 (query_audit_events), I-043 (get_audit_summary), I-044 (export_audit_report).
Every test uses a real PostgreSQL database via testcontainers.
No mocking of the database — ever (per TESTING.md Doc 13, Section 3).
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio

from services.audit_service import AuditService
from schemas.data_shapes import Severity


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def service(db_pool: asyncpg.Pool) -> AuditService:
    """Fresh AuditService for each test."""
    return AuditService(db_pool)


@pytest_asyncio.fixture
async def seed_agent(db_pool: asyncpg.Pool):
    """Insert a test agent into agent_registry and clean up after.

    Required to satisfy FK constraints if audit_events references agent_registry.
    """
    agent_id = f"audit-agent-{uuid4().hex[:8]}"
    await db_pool.execute(
        """
        INSERT INTO agent_registry (agent_id, name, phase, archetype, model, status)
        VALUES ($1, $2, 'govern', 'compliance-auditor', 'claude-sonnet-4-6', 'active')
        ON CONFLICT (agent_id) DO NOTHING
        """,
        agent_id,
        f"Audit Test Agent {agent_id}",
    )
    yield agent_id
    # Cleanup: audit_events is immutable (no DELETE), but agent_registry can be cleaned
    # We rely on unique project_ids per test so audit rows don't interfere.
    await db_pool.execute("DELETE FROM agent_registry WHERE agent_id = $1", agent_id)


@pytest_asyncio.fixture
async def seed_agents_pair(db_pool: asyncpg.Pool):
    """Insert two test agents for multi-agent tests."""
    a = f"audit-a-{uuid4().hex[:8]}"
    b = f"audit-b-{uuid4().hex[:8]}"
    for aid in (a, b):
        await db_pool.execute(
            """
            INSERT INTO agent_registry (agent_id, name, phase, archetype, model, status)
            VALUES ($1, $2, 'govern', 'compliance-auditor', 'claude-sonnet-4-6', 'active')
            ON CONFLICT (agent_id) DO NOTHING
            """,
            aid,
            f"Audit Test Agent {aid}",
        )
    yield a, b
    for aid in (a, b):
        await db_pool.execute("DELETE FROM agent_registry WHERE agent_id = $1", aid)


@pytest.fixture
def project_id() -> str:
    """Unique project_id per test for isolation."""
    return f"audit-proj-{uuid4().hex[:8]}"


@pytest.fixture
def session_id():
    return uuid4()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _record(
    service: AuditService,
    agent_id: str,
    project_id: str,
    action: str = "test.action",
    severity: str = "info",
    message: str = "Test event",
    **kwargs,
):
    """Shorthand to record an audit event."""
    return await service.record_event(
        agent_id=agent_id,
        project_id=project_id,
        session_id=kwargs.pop("session_id", uuid4()),
        action=action,
        severity=severity,
        message=message,
        **kwargs,
    )


# ===================================================================
# Tests: record_event
# ===================================================================

class TestRecordEvent:
    """record_event inserts into the immutable audit_events table."""

    @pytest.mark.asyncio
    async def test_creates_record(
        self, service: AuditService, seed_agent: str, project_id: str, session_id, db_pool,
    ):
        """Verify the row lands in audit_events with correct values."""
        event = await service.record_event(
            agent_id=seed_agent,
            project_id=project_id,
            session_id=session_id,
            action="pipeline.started",
            severity="info",
            message="Pipeline execution started",
            cost_usd=Decimal("0.05"),
            tokens_in=500,
            tokens_out=200,
            duration_ms=1200,
        )

        assert event.event_id is not None
        assert event.agent_id == seed_agent
        assert event.project_id == project_id
        assert event.action == "pipeline.started"
        assert event.severity == Severity.INFO
        assert event.created_at is not None

        # Verify in DB
        row = await db_pool.fetchrow(
            "SELECT * FROM audit_events WHERE event_id = $1",
            event.event_id,
        )
        assert row is not None
        assert row["action"] == "pipeline.started"
        assert row["tokens_in"] == 500

    @pytest.mark.asyncio
    async def test_record_with_details(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Event with details dict stores as JSONB."""
        details = {"step": 3, "quality_score": 0.95, "agent": "D2-arch"}
        event = await _record(
            service, seed_agent, project_id,
            action="quality.check",
            details=details,
        )
        assert event.details == details

    @pytest.mark.asyncio
    async def test_record_with_pii_flag(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """PII detected flag is stored correctly."""
        event = await _record(
            service, seed_agent, project_id,
            action="pii.detected",
            severity="warning",
            pii_detected=True,
        )
        assert event.pii_detected is True

    @pytest.mark.asyncio
    async def test_record_multiple_events(
        self, service: AuditService, seed_agent: str, project_id: str, db_pool,
    ):
        """Multiple events accumulate in the table."""
        await _record(service, seed_agent, project_id, action="step.1")
        await _record(service, seed_agent, project_id, action="step.2")
        await _record(service, seed_agent, project_id, action="step.3")

        row = await db_pool.fetchrow(
            "SELECT COUNT(*) AS cnt FROM audit_events WHERE project_id = $1",
            project_id,
        )
        assert row["cnt"] == 3


# ===================================================================
# Tests: immutability
# ===================================================================

class TestImmutability:
    """audit_events is immutable — UPDATE and DELETE are blocked by triggers."""

    @pytest.mark.asyncio
    async def test_update_blocked(
        self, service: AuditService, seed_agent: str, project_id: str, db_pool,
    ):
        """UPDATE on audit_events must raise an exception."""
        event = await _record(service, seed_agent, project_id)

        with pytest.raises(asyncpg.RaiseError, match="immutable"):
            await db_pool.execute(
                "UPDATE audit_events SET message = 'tampered' WHERE event_id = $1",
                event.event_id,
            )

    @pytest.mark.asyncio
    async def test_delete_blocked(
        self, service: AuditService, seed_agent: str, project_id: str, db_pool,
    ):
        """DELETE on audit_events must raise an exception."""
        event = await _record(service, seed_agent, project_id)

        with pytest.raises(asyncpg.RaiseError, match="immutable"):
            await db_pool.execute(
                "DELETE FROM audit_events WHERE event_id = $1",
                event.event_id,
            )


# ===================================================================
# Tests: query_events (I-042)
# ===================================================================

class TestQueryEvents:
    """I-042: query_audit_events with filters."""

    @pytest.mark.asyncio
    async def test_query_all_for_project(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Query returns all events for a project."""
        await _record(service, seed_agent, project_id, action="a1")
        await _record(service, seed_agent, project_id, action="a2")

        events = await service.query_events(project_id)
        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_query_filter_by_severity(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Filter by severity returns only matching events."""
        await _record(service, seed_agent, project_id, severity="info")
        await _record(service, seed_agent, project_id, severity="error")
        await _record(service, seed_agent, project_id, severity="error")

        errors = await service.query_events(project_id, severity="error")
        assert len(errors) == 2
        assert all(e.severity == Severity.ERROR for e in errors)

    @pytest.mark.asyncio
    async def test_query_filter_by_agent(
        self, service: AuditService, seed_agents_pair: tuple[str, str], project_id: str,
    ):
        """Filter by agent_id returns only that agent's events."""
        agent_a, agent_b = seed_agents_pair
        await _record(service, agent_a, project_id, action="a.work")
        await _record(service, agent_b, project_id, action="b.work")
        await _record(service, agent_a, project_id, action="a.more")

        events = await service.query_events(project_id, agent_id=agent_a)
        assert len(events) == 2
        assert all(e.agent_id == agent_a for e in events)

    @pytest.mark.asyncio
    async def test_query_limit_and_offset(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Limit and offset work for pagination."""
        for i in range(5):
            await _record(service, seed_agent, project_id, action=f"action.{i}")

        page1 = await service.query_events(project_id, limit=2, offset=0)
        page2 = await service.query_events(project_id, limit=2, offset=2)
        assert len(page1) == 2
        assert len(page2) == 2
        # Pages should not overlap
        ids_1 = {e.event_id for e in page1}
        ids_2 = {e.event_id for e in page2}
        assert ids_1.isdisjoint(ids_2)

    @pytest.mark.asyncio
    async def test_query_empty_project(self, service: AuditService):
        """Query for nonexistent project returns empty list."""
        events = await service.query_events("nonexistent-project")
        assert events == []


# ===================================================================
# Tests: get_summary (I-043)
# ===================================================================

class TestGetSummary:
    """I-043: get_audit_summary aggregates correctly."""

    @pytest.mark.asyncio
    async def test_summary_totals(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Summary counts total events correctly."""
        await _record(service, seed_agent, project_id, severity="info")
        await _record(service, seed_agent, project_id, severity="error")
        await _record(service, seed_agent, project_id, severity="info")

        summary = await service.get_summary(project_id, period_days=1)
        assert summary.total_events == 3

    @pytest.mark.asyncio
    async def test_summary_by_severity(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Summary breaks down by severity."""
        await _record(service, seed_agent, project_id, severity="info")
        await _record(service, seed_agent, project_id, severity="error")
        await _record(service, seed_agent, project_id, severity="error")
        await _record(service, seed_agent, project_id, severity="critical")

        summary = await service.get_summary(project_id, period_days=1)
        assert summary.by_severity["info"] == 1
        assert summary.by_severity["error"] == 2
        assert summary.by_severity["critical"] == 1

    @pytest.mark.asyncio
    async def test_summary_by_agent(
        self, service: AuditService, seed_agents_pair: tuple[str, str], project_id: str,
    ):
        """Summary breaks down by agent."""
        agent_a, agent_b = seed_agents_pair
        await _record(service, agent_a, project_id)
        await _record(service, agent_a, project_id)
        await _record(service, agent_b, project_id)

        summary = await service.get_summary(project_id, period_days=1)
        assert summary.by_agent[agent_a] == 2
        assert summary.by_agent[agent_b] == 1

    @pytest.mark.asyncio
    async def test_summary_empty_project(self, service: AuditService):
        """Summary for nonexistent project returns zero totals."""
        summary = await service.get_summary("nonexistent-project", period_days=1)
        assert summary.total_events == 0
        assert summary.by_severity == {}
        assert summary.by_agent == {}

    @pytest.mark.asyncio
    async def test_summary_includes_cost(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Summary aggregates total cost."""
        await _record(service, seed_agent, project_id, cost_usd=Decimal("0.10"))
        await _record(service, seed_agent, project_id, cost_usd=Decimal("0.25"))

        summary = await service.get_summary(project_id, period_days=1)
        assert summary.total_cost_usd >= Decimal("0.35")


# ===================================================================
# Tests: export_report (I-044)
# ===================================================================

class TestExportReport:
    """I-044: export_audit_report returns all events."""

    @pytest.mark.asyncio
    async def test_export_contains_all_events(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Report contains all events for the period."""
        for i in range(5):
            await _record(service, seed_agent, project_id, action=f"export.{i}")

        report = await service.export_report(project_id, period_days=1)
        assert report.total_events == 5
        assert len(report.events) == 5
        assert report.format == "json"
        assert report.report_id is not None

    @pytest.mark.asyncio
    async def test_export_empty_project(self, service: AuditService):
        """Report for nonexistent project returns empty events list."""
        report = await service.export_report("nonexistent-project", period_days=1)
        assert report.total_events == 0
        assert report.events == []

    @pytest.mark.asyncio
    async def test_export_events_ordered_chronologically(
        self, service: AuditService, seed_agent: str, project_id: str,
    ):
        """Exported events are in chronological order (ASC)."""
        await _record(service, seed_agent, project_id, action="first")
        await _record(service, seed_agent, project_id, action="second")
        await _record(service, seed_agent, project_id, action="third")

        report = await service.export_report(project_id, period_days=1)
        assert report.events[0].action == "first"
        assert report.events[-1].action == "third"
