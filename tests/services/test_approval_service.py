"""Tests for ApprovalService — human-in-the-loop approval gates.

Implements I-045 (list_pending), I-046 (approve_gate), I-047 (reject_gate).
Every test uses a real PostgreSQL database via testcontainers.
No mocking of the database — ever (per TESTING.md Doc 13, Section 3).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio

from services.approval_service import (
    ApprovalNotFoundError,
    ApprovalService,
    ApprovalStateError,
)
from schemas.data_shapes import ApprovalStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def service(db_pool: asyncpg.Pool) -> ApprovalService:
    """Fresh ApprovalService for each test."""
    return ApprovalService(db_pool)


@pytest_asyncio.fixture
async def seed_agent(db_pool: asyncpg.Pool):
    """Insert a test agent (needed for pipeline_steps FK if referenced)."""
    agent_id = f"approval-agent-{uuid4().hex[:8]}"
    await db_pool.execute(
        """
        INSERT INTO agent_registry (agent_id, name, phase, archetype, model, status)
        VALUES ($1, $2, 'govern', 'gate-keeper', 'claude-sonnet-4-6', 'active')
        ON CONFLICT (agent_id) DO NOTHING
        """,
        agent_id,
        f"Approval Test Agent {agent_id}",
    )
    yield agent_id
    await db_pool.execute("DELETE FROM agent_registry WHERE agent_id = $1", agent_id)


@pytest_asyncio.fixture
async def seed_pipeline_run(db_pool: asyncpg.Pool):
    """Insert a pipeline_run to satisfy the approval_requests FK on run_id.

    Returns (run_id, project_id).
    """
    run_id = uuid4()
    project_id = f"approval-proj-{uuid4().hex[:8]}"
    await db_pool.execute(
        """
        INSERT INTO pipeline_runs (run_id, project_id, pipeline_name, status, triggered_by)
        VALUES ($1, $2, 'full-stack-first', 'running', 'test')
        """,
        run_id,
        project_id,
    )
    yield run_id, project_id
    # Clean up approval_requests first (FK), then pipeline_runs
    await db_pool.execute("DELETE FROM approval_requests WHERE run_id = $1", run_id)
    await db_pool.execute("DELETE FROM pipeline_runs WHERE run_id = $1", run_id)


@pytest.fixture
def session_id():
    return uuid4()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _create_request(
    service: ApprovalService,
    session_id,
    run_id,
    project_id: str,
    step_number: int = 5,
    step_name: str = "quality-gate",
    summary: str = "Review quality gate for step 5",
    risk_level: str = "medium",
    expires_in_seconds: int = 3600,
) -> object:
    """Shorthand to create an approval request."""
    return await service.create_request(
        session_id=session_id,
        run_id=run_id,
        project_id=project_id,
        pipeline_name="full-stack-first",
        step_number=step_number,
        step_name=step_name,
        summary=summary,
        risk_level=risk_level,
        expires_in_seconds=expires_in_seconds,
    )


# ===================================================================
# Tests: create_request
# ===================================================================

class TestCreateRequest:
    """create_request inserts a new pending approval."""

    @pytest.mark.asyncio
    async def test_creates_pending_request(
        self, service: ApprovalService, session_id, seed_pipeline_run, db_pool,
    ):
        """Created request has status PENDING and correct fields."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)

        assert req.status == ApprovalStatus.PENDING
        assert req.approval_id is not None
        assert req.pipeline_name == "full-stack-first"
        assert req.summary == "Review quality gate for step 5"
        assert req.expires_at > req.requested_at

    @pytest.mark.asyncio
    async def test_create_stores_in_db(
        self, service: ApprovalService, session_id, seed_pipeline_run, db_pool,
    ):
        """Verify the row exists in the database."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)

        row = await db_pool.fetchrow(
            "SELECT * FROM approval_requests WHERE approval_id = $1",
            req.approval_id,
        )
        assert row is not None
        assert row["status"] == "pending"
        assert row["risk_level"] == "medium"
        assert row["step_name"] == "quality-gate"

    @pytest.mark.asyncio
    async def test_create_with_custom_expiry(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Custom expiry time is respected."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(
            service, session_id, run_id, project_id,
            expires_in_seconds=60,
        )
        delta = req.expires_at - req.requested_at
        assert delta.total_seconds() <= 65  # allow a few seconds slack


# ===================================================================
# Tests: list_pending (I-045)
# ===================================================================

class TestListPending:
    """I-045: list_pending returns pending requests sorted by urgency."""

    @pytest.mark.asyncio
    async def test_list_returns_pending(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Pending requests show up in the list."""
        run_id, project_id = seed_pipeline_run
        await _create_request(service, session_id, run_id, project_id)
        await _create_request(
            service, session_id, run_id, project_id,
            step_number=6, step_name="deploy-gate",
        )

        pending = await service.list_pending(project_id)
        assert len(pending) >= 2
        assert all(p.status == ApprovalStatus.PENDING for p in pending)

    @pytest.mark.asyncio
    async def test_list_sorted_by_urgency(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Most urgent (earliest expiry) comes first."""
        run_id, project_id = seed_pipeline_run
        # Create one with short expiry, then one with long expiry
        urgent = await _create_request(
            service, session_id, run_id, project_id,
            step_number=1, step_name="urgent-gate",
            expires_in_seconds=60,
        )
        relaxed = await _create_request(
            service, session_id, run_id, project_id,
            step_number=2, step_name="relaxed-gate",
            expires_in_seconds=7200,
        )

        pending = await service.list_pending(project_id)
        assert len(pending) >= 2
        # First item should expire before or at the same time as second
        assert pending[0].expires_at <= pending[1].expires_at

    @pytest.mark.asyncio
    async def test_list_excludes_approved(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Approved requests are not listed as pending."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)
        await service.approve(req.approval_id, decision_by="admin")

        pending = await service.list_pending(project_id)
        ids = {p.approval_id for p in pending}
        assert req.approval_id not in ids

    @pytest.mark.asyncio
    async def test_list_excludes_rejected(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Rejected requests are not listed as pending."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)
        await service.reject(req.approval_id, decision_by="admin", reason="Not ready")

        pending = await service.list_pending(project_id)
        ids = {p.approval_id for p in pending}
        assert req.approval_id not in ids

    @pytest.mark.asyncio
    async def test_list_filter_by_project(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """list_pending with project_id only returns that project's requests."""
        run_id, project_id = seed_pipeline_run
        await _create_request(service, session_id, run_id, project_id)

        # Other project should be empty
        other = await service.list_pending("other-project-xyz")
        assert len(other) == 0


# ===================================================================
# Tests: approve (I-046)
# ===================================================================

class TestApprove:
    """I-046: approve_gate transitions pending to approved."""

    @pytest.mark.asyncio
    async def test_approve_updates_status(
        self, service: ApprovalService, session_id, seed_pipeline_run, db_pool,
    ):
        """Approving a pending request sets status to APPROVED."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)

        result = await service.approve(req.approval_id, decision_by="lead-eng")
        assert result.status == ApprovalStatus.APPROVED
        assert result.decision_by == "lead-eng"
        assert result.decided_at is not None

        # Verify in DB
        row = await db_pool.fetchrow(
            "SELECT status, decision_by FROM approval_requests WHERE approval_id = $1",
            req.approval_id,
        )
        assert row["status"] == "approved"
        assert row["decision_by"] == "lead-eng"

    @pytest.mark.asyncio
    async def test_approve_with_comment(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Optional comment is stored."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)

        result = await service.approve(
            req.approval_id, decision_by="admin", comment="Looks good"
        )
        assert result.decision_comment == "Looks good"

    @pytest.mark.asyncio
    async def test_cannot_approve_already_approved(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Approving an already-approved request raises ApprovalStateError."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)
        await service.approve(req.approval_id, decision_by="admin")

        with pytest.raises(ApprovalStateError, match="approved"):
            await service.approve(req.approval_id, decision_by="another-admin")

    @pytest.mark.asyncio
    async def test_cannot_approve_rejected(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Approving a rejected request raises ApprovalStateError."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)
        await service.reject(req.approval_id, decision_by="admin", reason="Bad quality")

        with pytest.raises(ApprovalStateError, match="rejected"):
            await service.approve(req.approval_id, decision_by="another-admin")

    @pytest.mark.asyncio
    async def test_cannot_approve_expired(
        self, service: ApprovalService, session_id, seed_pipeline_run, db_pool,
    ):
        """Approving an expired request raises ApprovalStateError."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(
            service, session_id, run_id, project_id,
            expires_in_seconds=3600,
        )
        # Manually set expires_at to the past
        await db_pool.execute(
            "UPDATE approval_requests SET expires_at = NOW() - INTERVAL '1 hour' WHERE approval_id = $1",
            req.approval_id,
        )

        with pytest.raises(ApprovalStateError, match="expired"):
            await service.approve(req.approval_id, decision_by="admin")

    @pytest.mark.asyncio
    async def test_approve_nonexistent_raises(self, service: ApprovalService):
        """Approving a nonexistent approval_id raises ApprovalNotFoundError."""
        with pytest.raises(ApprovalNotFoundError):
            await service.approve(uuid4(), decision_by="admin")


# ===================================================================
# Tests: reject (I-047)
# ===================================================================

class TestReject:
    """I-047: reject_gate transitions pending to rejected with mandatory reason."""

    @pytest.mark.asyncio
    async def test_reject_updates_status(
        self, service: ApprovalService, session_id, seed_pipeline_run, db_pool,
    ):
        """Rejecting a pending request sets status to REJECTED."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)

        result = await service.reject(
            req.approval_id, decision_by="lead-eng", reason="Quality score below threshold"
        )
        assert result.status == ApprovalStatus.REJECTED
        assert result.decision_by == "lead-eng"
        assert result.decision_comment == "Quality score below threshold"

        # Verify in DB
        row = await db_pool.fetchrow(
            "SELECT status, decision_comment FROM approval_requests WHERE approval_id = $1",
            req.approval_id,
        )
        assert row["status"] == "rejected"
        assert row["decision_comment"] == "Quality score below threshold"

    @pytest.mark.asyncio
    async def test_reject_requires_reason(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Rejecting without a reason raises ValueError."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)

        with pytest.raises(ValueError, match="reason is required"):
            await service.reject(req.approval_id, decision_by="admin", reason="")

    @pytest.mark.asyncio
    async def test_reject_whitespace_reason_rejected(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Whitespace-only reason is treated as empty and rejected."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)

        with pytest.raises(ValueError, match="reason is required"):
            await service.reject(req.approval_id, decision_by="admin", reason="   ")

    @pytest.mark.asyncio
    async def test_cannot_reject_already_rejected(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Rejecting an already-rejected request raises ApprovalStateError."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)
        await service.reject(req.approval_id, decision_by="admin", reason="First rejection")

        with pytest.raises(ApprovalStateError, match="rejected"):
            await service.reject(req.approval_id, decision_by="another", reason="Second try")

    @pytest.mark.asyncio
    async def test_cannot_reject_approved(
        self, service: ApprovalService, session_id, seed_pipeline_run,
    ):
        """Rejecting an approved request raises ApprovalStateError."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(service, session_id, run_id, project_id)
        await service.approve(req.approval_id, decision_by="admin")

        with pytest.raises(ApprovalStateError, match="approved"):
            await service.reject(req.approval_id, decision_by="another", reason="Too late")

    @pytest.mark.asyncio
    async def test_cannot_reject_expired(
        self, service: ApprovalService, session_id, seed_pipeline_run, db_pool,
    ):
        """Rejecting an expired request raises ApprovalStateError."""
        run_id, project_id = seed_pipeline_run
        req = await _create_request(
            service, session_id, run_id, project_id,
            expires_in_seconds=3600,
        )
        # Manually expire it
        await db_pool.execute(
            "UPDATE approval_requests SET expires_at = NOW() - INTERVAL '1 hour' WHERE approval_id = $1",
            req.approval_id,
        )

        with pytest.raises(ApprovalStateError, match="expired"):
            await service.reject(req.approval_id, decision_by="admin", reason="Too late")

    @pytest.mark.asyncio
    async def test_reject_nonexistent_raises(self, service: ApprovalService):
        """Rejecting a nonexistent approval_id raises ApprovalNotFoundError."""
        with pytest.raises(ApprovalNotFoundError):
            await service.reject(uuid4(), decision_by="admin", reason="Not found")
