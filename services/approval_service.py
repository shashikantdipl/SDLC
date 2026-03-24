"""ApprovalService — Business logic for human-in-the-loop approval gates.

Implements interactions: I-045, I-046, I-047 from INTERACTION-MAP.
Called by: MCP governance-server tools, REST /api/v1/approvals/* routes.
Never import from mcp_servers/ or api/.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import asyncpg

from schemas.data_shapes import (
    ApprovalRequest,
    ApprovalResult,
    ApprovalStatus,
)


# ---------------------------------------------------------------------------
# Custom errors
# ---------------------------------------------------------------------------

class ApprovalNotFoundError(Exception):
    """Raised when an approval_id does not exist."""

    def __init__(self, approval_id: UUID) -> None:
        self.approval_id = approval_id
        super().__init__(f"Approval request not found: {approval_id}")


class ApprovalStateError(Exception):
    """Raised when attempting to decide on an already-decided or expired request."""

    def __init__(self, approval_id: UUID, current_status: str, attempted_action: str) -> None:
        self.approval_id = approval_id
        self.current_status = current_status
        self.attempted_action = attempted_action
        super().__init__(
            f"Cannot {attempted_action} approval {approval_id}: "
            f"current status is '{current_status}' (only 'pending' allowed)"
        )


class ApprovalService:
    """Human-in-the-loop approval gate service.

    Pipeline gate steps create approval requests; humans approve or reject them.
    Only PENDING requests can be approved/rejected. Expired requests are
    detected at decision time.
    """

    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # create_request  (called by PipelineService at gate steps)
    # ------------------------------------------------------------------
    async def create_request(
        self,
        session_id: UUID,
        run_id: UUID,
        project_id: str,
        pipeline_name: str,
        step_number: int,
        step_name: str,
        summary: str,
        risk_level: str = "medium",
        expires_in_seconds: int = 3600,
    ) -> ApprovalRequest:
        """Create a new approval request triggered by a pipeline gate step."""
        now = datetime.now(tz=timezone.utc)
        expires_at = now + timedelta(seconds=expires_in_seconds)

        row = await self._db.fetchrow(
            """
            INSERT INTO approval_requests
                (session_id, run_id, project_id, pipeline_name,
                 step_number, step_name, summary, risk_level,
                 status, requested_at, expires_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'pending', $9, $10)
            RETURNING approval_id, requested_at, expires_at
            """,
            session_id,
            run_id,
            project_id,
            pipeline_name,
            step_number,
            step_name,
            summary,
            risk_level,
            now,
            expires_at,
        )

        return ApprovalRequest(
            approval_id=row["approval_id"],
            session_id=session_id,
            pipeline_name=pipeline_name,
            step_id=f"{step_number}:{step_name}",
            summary=summary,
            status=ApprovalStatus.PENDING,
            requested_at=row["requested_at"],
            expires_at=row["expires_at"],
        )

    # ------------------------------------------------------------------
    # I-045: list_pending
    # ------------------------------------------------------------------
    async def list_pending(
        self, project_id: str | None = None
    ) -> list[ApprovalRequest]:
        """List pending approval requests, sorted by expires_at ASC (most urgent first).

        Optionally filter by project_id.
        """
        if project_id is not None:
            rows = await self._db.fetch(
                """
                SELECT approval_id, session_id, pipeline_name, step_number,
                       step_name, summary, status, approver_channel,
                       requested_at, expires_at, decision_by, decision_comment,
                       decided_at
                FROM approval_requests
                WHERE status = 'pending'
                  AND project_id = $1
                  AND expires_at > NOW()
                ORDER BY expires_at ASC
                """,
                project_id,
            )
        else:
            rows = await self._db.fetch(
                """
                SELECT approval_id, session_id, pipeline_name, step_number,
                       step_name, summary, status, approver_channel,
                       requested_at, expires_at, decision_by, decision_comment,
                       decided_at
                FROM approval_requests
                WHERE status = 'pending'
                  AND expires_at > NOW()
                ORDER BY expires_at ASC
                """
            )

        return [_row_to_request(r) for r in rows]

    # ------------------------------------------------------------------
    # I-046: approve_gate
    # ------------------------------------------------------------------
    async def approve(
        self,
        approval_id: UUID,
        decision_by: str,
        comment: str | None = None,
    ) -> ApprovalResult:
        """Approve a pending request.

        State guard: only PENDING requests that have not expired can be approved.
        Raises ApprovalNotFoundError or ApprovalStateError.
        """
        row = await self._fetch_and_validate(approval_id, "approve")

        now = datetime.now(tz=timezone.utc)
        await self._db.execute(
            """
            UPDATE approval_requests
            SET status = 'approved',
                decision_by = $2,
                decision_comment = $3,
                decided_at = $4
            WHERE approval_id = $1
            """,
            approval_id,
            decision_by,
            comment,
            now,
        )

        return ApprovalResult(
            approval_id=approval_id,
            status=ApprovalStatus.APPROVED,
            decision_by=decision_by,
            decision_comment=comment,
            decided_at=now,
        )

    # ------------------------------------------------------------------
    # I-047: reject_gate
    # ------------------------------------------------------------------
    async def reject(
        self,
        approval_id: UUID,
        decision_by: str,
        reason: str,
    ) -> ApprovalResult:
        """Reject a pending request with mandatory reason.

        State guard: only PENDING requests that have not expired can be rejected.
        reason is REQUIRED (enforced here and by DB constraint chk_rejection_comment).
        Raises ApprovalNotFoundError, ApprovalStateError, or ValueError.
        """
        if not reason or not reason.strip():
            raise ValueError("Rejection reason is required and cannot be empty")

        row = await self._fetch_and_validate(approval_id, "reject")

        now = datetime.now(tz=timezone.utc)
        await self._db.execute(
            """
            UPDATE approval_requests
            SET status = 'rejected',
                decision_by = $2,
                decision_comment = $3,
                decided_at = $4
            WHERE approval_id = $1
            """,
            approval_id,
            decision_by,
            reason,
            now,
        )

        return ApprovalResult(
            approval_id=approval_id,
            status=ApprovalStatus.REJECTED,
            decision_by=decision_by,
            decision_comment=reason,
            decided_at=now,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _fetch_and_validate(
        self, approval_id: UUID, action: str
    ) -> asyncpg.Record:
        """Fetch an approval request and validate it can be acted upon.

        Raises ApprovalNotFoundError if not found.
        Raises ApprovalStateError if not pending or if expired.
        """
        row = await self._db.fetchrow(
            """
            SELECT approval_id, status, expires_at
            FROM approval_requests
            WHERE approval_id = $1
            """,
            approval_id,
        )

        if row is None:
            raise ApprovalNotFoundError(approval_id)

        current_status = row["status"]

        # Check for expiration first (even if DB still says 'pending')
        if current_status == "pending" and row["expires_at"] < datetime.now(tz=timezone.utc):
            # Mark as expired in DB
            await self._db.execute(
                "UPDATE approval_requests SET status = 'expired' WHERE approval_id = $1",
                approval_id,
            )
            raise ApprovalStateError(approval_id, "expired", action)

        if current_status != "pending":
            raise ApprovalStateError(approval_id, current_status, action)

        return row


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _row_to_request(r: asyncpg.Record) -> ApprovalRequest:
    """Convert a DB row to an ApprovalRequest data shape."""
    return ApprovalRequest(
        approval_id=r["approval_id"],
        session_id=r["session_id"],
        pipeline_name=r["pipeline_name"],
        step_id=f"{r['step_number']}:{r['step_name']}",
        summary=r["summary"],
        status=ApprovalStatus(r["status"]),
        approver_channel=r["approver_channel"],
        requested_at=r["requested_at"],
        expires_at=r["expires_at"],
        decision_by=r["decision_by"],
        decision_comment=r["decision_comment"],
        decided_at=r["decided_at"],
    )
