"""AgentService — Business logic for agent lifecycle and management.

Implements interactions: I-020 through I-027 from INTERACTION-MAP.
Called by: MCP agents-server tools, REST /api/v1/agents/* routes.
Never import from mcp_servers/ or api/.

Data shapes returned: AgentSummary, AgentDetail, AgentHealth, AgentVersion,
                      AgentMaturity, AgentInvocationResult
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import asyncpg

from schemas.data_shapes import (
    AgentDetail,
    AgentHealth,
    AgentInvocationResult,
    AgentMaturity,
    AgentPhase,
    AgentStatus,
    AgentSummary,
    AgentVersion,
    MaturityLevel,
)

# --- Mapping from DB enum values to data-shape enum values ---
# The DB schema (migration 001/009) uses different enum strings than the
# Pydantic data shapes from INTERACTION-MAP.  We bridge them here.

_DB_STATUS_TO_AGENT_STATUS: dict[str, AgentStatus] = {
    "active": AgentStatus.ACTIVE,
    "degraded": AgentStatus.DEGRADED,
    "offline": AgentStatus.INACTIVE,
    "canary": AgentStatus.ACTIVE,  # canary agents are still active
}

_DB_MATURITY_TO_LEVEL: dict[str, MaturityLevel] = {
    "supervised": MaturityLevel.APPRENTICE,
    "assisted": MaturityLevel.JOURNEYMAN,
    "autonomous": MaturityLevel.PROFESSIONAL,
    "fully_autonomous": MaturityLevel.EXPERT,
}

_LEVEL_TO_DB_MATURITY: dict[MaturityLevel, str] = {v: k for k, v in _DB_MATURITY_TO_LEVEL.items()}


class AgentNotFoundError(Exception):
    """Raised when an agent_id does not exist in the registry."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        super().__init__(f"Agent not found: {agent_id}")


class AgentService:
    """Agent lifecycle management.

    All public methods return INTERACTION-MAP data shapes.
    """

    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # I-020: list_agents
    # ------------------------------------------------------------------
    async def list_agents(
        self,
        phase: str | None = None,
        status: str | None = None,
    ) -> list[AgentSummary]:
        """I-020: List agents, optionally filtered by phase and/or status."""
        conditions: list[str] = []
        params: list[object] = []
        idx = 1

        if phase is not None:
            conditions.append(f"phase = ${idx}")
            params.append(phase)
            idx += 1
        if status is not None:
            # Map data-shape status back to DB status for filtering
            db_statuses = [
                db_val
                for db_val, shape_val in _DB_STATUS_TO_AGENT_STATUS.items()
                if shape_val.value == status
            ]
            if db_statuses:
                placeholders = ", ".join(f"${idx + i}" for i in range(len(db_statuses)))
                conditions.append(f"status IN ({placeholders})")
                params.extend(db_statuses)
                idx += len(db_statuses)
            else:
                # Direct match attempt (user passed DB-level value)
                conditions.append(f"status = ${idx}")
                params.append(status)
                idx += 1

        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

        rows = await self._db.fetch(
            f"""
            SELECT agent_id, name, phase, archetype, model, status,
                   active_version, maturity_level
            FROM agent_registry
            {where}
            ORDER BY phase, name
            """,
            *params,
        )
        return [self._row_to_agent_summary(row) for row in rows]

    # ------------------------------------------------------------------
    # I-021: get_agent
    # ------------------------------------------------------------------
    async def get_agent(self, agent_id: str) -> AgentDetail:
        """I-021: Get full detail for a single agent."""
        row = await self._db.fetchrow(
            """
            SELECT agent_id, name, phase, archetype, model, status,
                   active_version, canary_version, canary_traffic_pct,
                   previous_version, maturity_level, updated_at
            FROM agent_registry
            WHERE agent_id = $1
            """,
            agent_id,
        )
        if row is None:
            raise AgentNotFoundError(agent_id)

        # Aggregate cost and invocation stats from cost_metrics
        stats = await self._db.fetchrow(
            """
            SELECT COALESCE(SUM(cost_usd), 0) AS daily_cost_usd,
                   COUNT(*)                     AS invocations_today,
                   MAX(recorded_at)             AS last_invoked_at
            FROM cost_metrics
            WHERE agent_id = $1
              AND recorded_at >= CURRENT_DATE
            """,
            agent_id,
        )

        return AgentDetail(
            agent_id=row["agent_id"],
            name=row["name"],
            phase=AgentPhase(row["phase"]),
            archetype=row["archetype"],
            model=row["model"],
            status=_DB_STATUS_TO_AGENT_STATUS.get(row["status"], AgentStatus.INACTIVE),
            active_version=row["active_version"] or "0.0.0",
            canary_version=row["canary_version"],
            canary_traffic_pct=row["canary_traffic_pct"],
            previous_version=row["previous_version"],
            maturity=_DB_MATURITY_TO_LEVEL.get(row["maturity_level"], MaturityLevel.APPRENTICE),
            daily_cost_usd=Decimal(str(stats["daily_cost_usd"])) if stats else Decimal("0.00"),
            invocations_today=stats["invocations_today"] if stats else 0,
            last_invoked_at=stats["last_invoked_at"] if stats else None,
        )

    # ------------------------------------------------------------------
    # I-022: invoke_agent
    # ------------------------------------------------------------------
    async def invoke_agent(self, agent_id: str, input_text: str) -> AgentInvocationResult:
        """I-022: Invoke an agent with input and return the result.

        In production this dispatches to the agent runtime; here we record
        the invocation and return a placeholder result.
        """
        # Verify agent exists
        row = await self._db.fetchrow(
            "SELECT agent_id, model FROM agent_registry WHERE agent_id = $1",
            agent_id,
        )
        if row is None:
            raise AgentNotFoundError(agent_id)

        invocation_id = uuid4()
        # Record in cost_metrics as a lightweight invocation log
        await self._db.execute(
            """
            INSERT INTO cost_metrics (agent_id, project_id, session_id, model, input_tokens, output_tokens, cost_usd)
            VALUES ($1, 'invoke', $2, $3, $4, $5, $6)
            """,
            agent_id,
            invocation_id,
            row["model"],
            len(input_text.split()),  # rough token estimate
            0,
            Decimal("0.000000"),
        )

        return AgentInvocationResult(
            invocation_id=invocation_id,
            agent_id=agent_id,
            status="completed",
            output="",
            cost_usd=Decimal("0.00"),
            duration_ms=0,
            quality_score=None,
        )

    # ------------------------------------------------------------------
    # I-023: check_health
    # ------------------------------------------------------------------
    async def check_health(self, agent_id: str) -> AgentHealth:
        """I-023: Return health status for a single agent."""
        row = await self._db.fetchrow(
            "SELECT agent_id, status, updated_at FROM agent_registry WHERE agent_id = $1",
            agent_id,
        )
        if row is None:
            raise AgentNotFoundError(agent_id)

        # Compute 1-hour error rate and invocation count from cost_metrics
        stats = await self._db.fetchrow(
            """
            SELECT COUNT(*)                                          AS invocations_1h,
                   AVG(EXTRACT(EPOCH FROM (NOW() - recorded_at)))    AS avg_latency_proxy
            FROM cost_metrics
            WHERE agent_id = $1
              AND recorded_at >= NOW() - INTERVAL '1 hour'
            """,
            agent_id,
        )

        return AgentHealth(
            agent_id=row["agent_id"],
            status=_DB_STATUS_TO_AGENT_STATUS.get(row["status"], AgentStatus.INACTIVE),
            last_heartbeat=row["updated_at"],
            error_rate_1h=0.0,
            avg_latency_ms=float(stats["avg_latency_proxy"] or 0) * 1000 if stats else 0.0,
            invocations_1h=stats["invocations_1h"] if stats else 0,
        )

    # ------------------------------------------------------------------
    # I-024: promote_version
    # ------------------------------------------------------------------
    async def promote_version(self, agent_id: str, new_version: str) -> AgentVersion:
        """I-024: Promote an agent to a new version.

        Sets active_version = new_version, previous_version = old active,
        and resets canary fields.
        """
        row = await self._db.fetchrow(
            """
            UPDATE agent_registry
            SET previous_version  = active_version,
                active_version    = $2,
                canary_version    = NULL,
                canary_traffic_pct = 0,
                promoted_at       = NOW(),
                updated_at        = NOW()
            WHERE agent_id = $1
            RETURNING agent_id, active_version, canary_version,
                      canary_traffic_pct, previous_version, updated_at
            """,
            agent_id,
            new_version,
        )
        if row is None:
            raise AgentNotFoundError(agent_id)

        return self._row_to_agent_version(row)

    # ------------------------------------------------------------------
    # I-025: rollback_version
    # ------------------------------------------------------------------
    async def rollback_version(self, agent_id: str) -> AgentVersion:
        """I-025: Roll back to the previous version.

        Raises AgentNotFoundError if agent missing.
        Raises ValueError if there is no previous_version to roll back to.
        """
        current = await self._db.fetchrow(
            "SELECT agent_id, active_version, previous_version FROM agent_registry WHERE agent_id = $1",
            agent_id,
        )
        if current is None:
            raise AgentNotFoundError(agent_id)
        if current["previous_version"] is None:
            raise ValueError(f"Agent {agent_id} has no previous version to roll back to")

        row = await self._db.fetchrow(
            """
            UPDATE agent_registry
            SET active_version    = previous_version,
                previous_version  = active_version,
                canary_version    = NULL,
                canary_traffic_pct = 0,
                rolled_back_at    = NOW(),
                updated_at        = NOW()
            WHERE agent_id = $1
            RETURNING agent_id, active_version, canary_version,
                      canary_traffic_pct, previous_version, updated_at
            """,
            agent_id,
        )
        return self._row_to_agent_version(row)

    # ------------------------------------------------------------------
    # I-026: set_canary_traffic
    # ------------------------------------------------------------------
    async def set_canary_traffic(self, agent_id: str, percentage: int) -> AgentVersion:
        """I-026: Set canary traffic percentage (0-100)."""
        if not (0 <= percentage <= 100):
            raise ValueError(f"Canary percentage must be 0-100, got {percentage}")

        row = await self._db.fetchrow(
            """
            UPDATE agent_registry
            SET canary_traffic_pct = $2,
                updated_at = NOW()
            WHERE agent_id = $1
            RETURNING agent_id, active_version, canary_version,
                      canary_traffic_pct, previous_version, updated_at
            """,
            agent_id,
            percentage,
        )
        if row is None:
            raise AgentNotFoundError(agent_id)

        return self._row_to_agent_version(row)

    # ------------------------------------------------------------------
    # I-027: get_maturity
    # ------------------------------------------------------------------
    async def get_maturity(self, agent_id: str) -> AgentMaturity:
        """I-027: Return the maturity level and stats for an agent."""
        row = await self._db.fetchrow(
            "SELECT agent_id, maturity_level, promoted_at FROM agent_registry WHERE agent_id = $1",
            agent_id,
        )
        if row is None:
            raise AgentNotFoundError(agent_id)

        # Aggregate invocation stats
        stats = await self._db.fetchrow(
            """
            SELECT COUNT(*) AS total_invocations
            FROM cost_metrics
            WHERE agent_id = $1
            """,
            agent_id,
        )

        return AgentMaturity(
            agent_id=row["agent_id"],
            maturity=_DB_MATURITY_TO_LEVEL.get(row["maturity_level"], MaturityLevel.APPRENTICE),
            golden_tests_passed=0,
            adversarial_tests_passed=0,
            total_invocations=stats["total_invocations"] if stats else 0,
            avg_quality_score=0.0,
            promoted_at=row["promoted_at"],
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_agent_summary(row: asyncpg.Record) -> AgentSummary:
        """Convert a DB row to AgentSummary data shape."""
        return AgentSummary(
            agent_id=row["agent_id"],
            name=row["name"],
            phase=AgentPhase(row["phase"]),
            archetype=row["archetype"],
            model=row["model"],
            status=_DB_STATUS_TO_AGENT_STATUS.get(row["status"], AgentStatus.INACTIVE),
            active_version=row["active_version"] or "0.0.0",
            maturity=_DB_MATURITY_TO_LEVEL.get(row["maturity_level"], MaturityLevel.APPRENTICE),
        )

    @staticmethod
    def _row_to_agent_version(row: asyncpg.Record) -> AgentVersion:
        """Convert a DB row to AgentVersion data shape."""
        return AgentVersion(
            agent_id=row["agent_id"],
            active_version=row["active_version"],
            canary_version=row["canary_version"],
            canary_traffic_pct=row["canary_traffic_pct"],
            previous_version=row["previous_version"],
            updated_at=row["updated_at"],
        )
