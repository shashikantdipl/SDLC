"""AuditService — Business logic for audit logging and compliance reporting.

Implements interactions: I-042, I-043, I-044 from INTERACTION-MAP.
Called by: MCP governance-server tools, REST /api/v1/audit/* routes.
Never import from mcp_servers/ or api/.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import asyncpg

from schemas.data_shapes import (
    AuditEvent,
    AuditReport,
    AuditSummary,
    Severity,
)


class AuditService:
    """Append-only audit trail service backed by PostgreSQL.

    The audit_events table is IMMUTABLE — UPDATE and DELETE are blocked
    by database triggers (migration 003). This service only INSERTs.
    """

    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # INTERNAL: record_event  (called by other services / MCP tools)
    # ------------------------------------------------------------------
    async def record_event(
        self,
        agent_id: str,
        project_id: str,
        session_id: UUID,
        action: str,
        severity: str = "info",
        message: str = "",
        details: dict | None = None,
        pii_detected: bool = False,
        cost_usd: Decimal = Decimal("0"),
        tokens_in: int = 0,
        tokens_out: int = 0,
        duration_ms: int = 0,
    ) -> AuditEvent:
        """Insert into audit_events (append-only, immutable).

        Returns the created AuditEvent with its generated event_id.
        """
        row = await self._db.fetchrow(
            """
            INSERT INTO audit_events
                (agent_id, project_id, session_id, action, severity,
                 message, details, pii_detected, cost_usd,
                 tokens_in, tokens_out, duration_ms)
            VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9, $10, $11, $12)
            RETURNING event_id, created_at
            """,
            agent_id,
            project_id,
            session_id,
            action,
            severity,
            message,
            json.dumps(details) if details is not None else "{}",
            pii_detected,
            cost_usd,
            tokens_in,
            tokens_out,
            duration_ms,
        )

        return AuditEvent(
            event_id=row["event_id"],
            agent_id=agent_id,
            project_id=project_id,
            session_id=session_id,
            action=action,
            severity=Severity(severity),
            message=message,
            details=details,
            pii_detected=pii_detected,
            created_at=row["created_at"],
        )

    # ------------------------------------------------------------------
    # I-042: query_audit_events
    # ------------------------------------------------------------------
    async def query_events(
        self,
        project_id: str,
        severity: str | None = None,
        agent_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEvent]:
        """Query audit events with optional severity and agent_id filters.

        Results are ordered by created_at DESC (most recent first).
        """
        conditions = ["project_id = $1"]
        params: list = [project_id]
        idx = 2

        if severity is not None:
            conditions.append(f"severity = ${idx}")
            params.append(severity)
            idx += 1

        if agent_id is not None:
            conditions.append(f"agent_id = ${idx}")
            params.append(agent_id)
            idx += 1

        where = " AND ".join(conditions)
        params.append(limit)
        params.append(offset)

        rows = await self._db.fetch(
            f"""
            SELECT event_id, agent_id, project_id, session_id, action,
                   severity, message, details, pii_detected, created_at
            FROM audit_events
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
            """,
            *params,
        )

        return [_row_to_event(r) for r in rows]

    # ------------------------------------------------------------------
    # I-043: get_audit_summary
    # ------------------------------------------------------------------
    async def get_summary(
        self, project_id: str, period_days: int = 7
    ) -> AuditSummary:
        """Aggregate summary: total events, counts by severity and by agent."""
        interval = f"{period_days} days"

        # Total count
        total_row = await self._db.fetchrow(
            """
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(cost_usd), 0) AS total_cost
            FROM audit_events
            WHERE project_id = $1
              AND created_at >= NOW() - $2::INTERVAL
            """,
            project_id,
            interval,
        )

        # By severity
        sev_rows = await self._db.fetch(
            """
            SELECT severity, COUNT(*) AS cnt
            FROM audit_events
            WHERE project_id = $1
              AND created_at >= NOW() - $2::INTERVAL
            GROUP BY severity
            """,
            project_id,
            interval,
        )
        by_severity = {r["severity"]: r["cnt"] for r in sev_rows}

        # By agent
        agent_rows = await self._db.fetch(
            """
            SELECT agent_id, COUNT(*) AS cnt
            FROM audit_events
            WHERE project_id = $1
              AND created_at >= NOW() - $2::INTERVAL
            GROUP BY agent_id
            """,
            project_id,
            interval,
        )
        by_agent = {r["agent_id"]: r["cnt"] for r in agent_rows}

        now = datetime.now(tz=timezone.utc)

        return AuditSummary(
            total_events=total_row["total"],
            by_severity=by_severity,
            by_agent=by_agent,
            period_start=datetime.fromtimestamp(
                now.timestamp() - period_days * 86400, tz=timezone.utc
            ),
            period_end=now,
            total_cost_usd=Decimal(str(total_row["total_cost"])),
        )

    # ------------------------------------------------------------------
    # I-044: export_audit_report
    # ------------------------------------------------------------------
    async def export_report(
        self, project_id: str, period_days: int = 30
    ) -> AuditReport:
        """Full audit report containing all events for the given period."""
        interval = f"{period_days} days"

        rows = await self._db.fetch(
            """
            SELECT event_id, agent_id, project_id, session_id, action,
                   severity, message, details, pii_detected, created_at
            FROM audit_events
            WHERE project_id = $1
              AND created_at >= NOW() - $2::INTERVAL
            ORDER BY created_at ASC
            """,
            project_id,
            interval,
        )

        events = [_row_to_event(r) for r in rows]
        now = datetime.now(tz=timezone.utc)

        return AuditReport(
            report_id=uuid4(),
            generated_at=now,
            period_start=datetime.fromtimestamp(
                now.timestamp() - period_days * 86400, tz=timezone.utc
            ),
            period_end=now,
            total_events=len(events),
            events=events,
            format="json",
        )


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _row_to_event(r: asyncpg.Record) -> AuditEvent:
    """Convert a DB row to an AuditEvent data shape."""
    details = r["details"]
    if isinstance(details, str):
        details = json.loads(details)
    return AuditEvent(
        event_id=r["event_id"],
        agent_id=r["agent_id"],
        project_id=r["project_id"],
        session_id=r["session_id"],
        action=r["action"],
        severity=Severity(r["severity"]),
        message=r["message"] or "",
        details=details if details else None,
        pii_detected=r["pii_detected"],
        created_at=r["created_at"],
    )
