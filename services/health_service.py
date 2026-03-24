"""HealthService — Business logic for fleet health and MCP server monitoring.

Implements interactions: I-080, I-081, I-082 from INTERACTION-MAP.
Called by: MCP agents-server tools, REST /api/v1/health/* routes.
Never import from mcp_servers/ or api/.

Data shapes returned: FleetHealth, McpServerStatus, McpCallEvent
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import asyncpg

from schemas.data_shapes import (
    AgentHealth,
    AgentStatus,
    FleetHealth,
    McpCallEvent,
    McpServerStatus,
)

# Known MCP servers (from migration 009 CHECK constraint)
_MCP_SERVERS = [
    "agentic-sdlc-agents",
    "agentic-sdlc-governance",
    "agentic-sdlc-knowledge",
]

# Map DB agent status to data-shape status
_DB_STATUS_TO_AGENT_STATUS: dict[str, AgentStatus] = {
    "active": AgentStatus.ACTIVE,
    "degraded": AgentStatus.DEGRADED,
    "offline": AgentStatus.INACTIVE,
    "canary": AgentStatus.ACTIVE,
}


class HealthService:
    """Fleet health and MCP monitoring service.

    All public methods return INTERACTION-MAP data shapes.
    """

    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # I-080: get_fleet_health
    # ------------------------------------------------------------------
    async def get_fleet_health(self) -> FleetHealth:
        """I-080: Aggregate fleet health from agent_registry + cost_metrics.

        Counts agents by status and sums today's fleet cost.
        """
        # Count agents by status
        status_rows = await self._db.fetch(
            """
            SELECT status, COUNT(*) AS cnt
            FROM agent_registry
            GROUP BY status
            """
        )

        counts: dict[str, int] = {}
        total = 0
        for row in status_rows:
            mapped = _DB_STATUS_TO_AGENT_STATUS.get(row["status"], AgentStatus.INACTIVE)
            counts[mapped.value] = counts.get(mapped.value, 0) + row["cnt"]
            total += row["cnt"]

        # Today's fleet cost
        cost_row = await self._db.fetchrow(
            """
            SELECT COALESCE(SUM(cost_usd), 0) AS fleet_cost
            FROM cost_metrics
            WHERE recorded_at >= date_trunc('day', NOW() AT TIME ZONE 'UTC')
            """
        )
        fleet_cost = Decimal(str(cost_row["fleet_cost"])) if cost_row else Decimal("0.00")

        # Per-agent health (latest info)
        agent_rows = await self._db.fetch(
            """
            SELECT agent_id, status, updated_at
            FROM agent_registry
            ORDER BY agent_id
            """
        )
        agents = [
            AgentHealth(
                agent_id=r["agent_id"],
                status=_DB_STATUS_TO_AGENT_STATUS.get(r["status"], AgentStatus.INACTIVE),
                last_heartbeat=r["updated_at"],
                error_rate_1h=0.0,
                avg_latency_ms=0.0,
                invocations_1h=0,
            )
            for r in agent_rows
        ]

        return FleetHealth(
            total_agents=total,
            healthy=counts.get("active", 0),
            degraded=counts.get("degraded", 0),
            error=counts.get("error", 0),
            inactive=counts.get("inactive", 0),
            fleet_cost_today_usd=fleet_cost,
            fleet_budget_remaining_usd=Decimal("50.00") - fleet_cost,
            agents=agents,
        )

    # ------------------------------------------------------------------
    # I-081: get_mcp_status
    # ------------------------------------------------------------------
    async def get_mcp_status(self) -> list[McpServerStatus]:
        """I-081: Get MCP server status (computed from mcp_call_events).

        Aggregates recent mcp_call_events by server_name.
        Returns one entry per known MCP server.
        """
        rows = await self._db.fetch(
            """
            SELECT server_name,
                   COUNT(*) AS total_calls,
                   COUNT(DISTINCT tool_name) AS tools_registered,
                   COUNT(*) FILTER (WHERE status = 'error') AS error_count,
                   AVG(duration_ms) AS avg_latency,
                   MIN(called_at) AS first_call
            FROM mcp_call_events
            WHERE called_at >= NOW() - INTERVAL '1 hour'
            GROUP BY server_name
            """
        )

        # Build a lookup from aggregated data
        data: dict[str, asyncpg.Record] = {r["server_name"]: r for r in rows}
        now = datetime.now(tz=timezone.utc)

        results: list[McpServerStatus] = []
        for server in _MCP_SERVERS:
            if server in data:
                r = data[server]
                total = r["total_calls"]
                error_rate = float(r["error_count"] / total * 100) if total > 0 else 0.0
                avg_latency = float(r["avg_latency"] or 0)
                first_call = r["first_call"]
                uptime = int((now - first_call).total_seconds()) if first_call else 0
                status = "error" if error_rate > 50 else ("degraded" if error_rate > 10 else "healthy")
                tools = r["tools_registered"]
            else:
                error_rate = 0.0
                avg_latency = 0.0
                uptime = 0
                status = "unknown"
                tools = 0

            results.append(
                McpServerStatus(
                    server_name=server,
                    status=status,
                    uptime_seconds=uptime,
                    tools_registered=tools,
                    resources_registered=0,
                    error_rate_1h=round(error_rate, 2),
                    avg_latency_ms=round(avg_latency, 2),
                )
            )

        return results

    # ------------------------------------------------------------------
    # I-082: list_recent_mcp_calls
    # ------------------------------------------------------------------
    async def list_recent_mcp_calls(
        self,
        limit: int = 50,
        server_name: str | None = None,
    ) -> list[McpCallEvent]:
        """I-082: List recent MCP tool invocations."""
        if server_name is not None:
            rows = await self._db.fetch(
                """
                SELECT call_id, server_name, tool_name, caller,
                       project_id, status, duration_ms, cost_usd, called_at
                FROM mcp_call_events
                WHERE server_name = $1
                ORDER BY called_at DESC
                LIMIT $2
                """,
                server_name,
                limit,
            )
        else:
            rows = await self._db.fetch(
                """
                SELECT call_id, server_name, tool_name, caller,
                       project_id, status, duration_ms, cost_usd, called_at
                FROM mcp_call_events
                ORDER BY called_at DESC
                LIMIT $1
                """,
                limit,
            )
        return [self._row_to_mcp_call(row) for row in rows]

    # ------------------------------------------------------------------
    # Internal: record_mcp_call
    # ------------------------------------------------------------------
    async def record_mcp_call(
        self,
        server_name: str,
        tool_name: str,
        caller: str,
        project_id: str | None = None,
        duration_ms: int = 0,
        status: str = "success",
        error_message: str | None = None,
        tokens_used: int = 0,
        cost_usd: Decimal | float | int = 0,
    ) -> McpCallEvent:
        """Internal: Record an MCP tool call (called by MCP server middleware)."""
        row = await self._db.fetchrow(
            """
            INSERT INTO mcp_call_events
                (server_name, tool_name, caller, project_id,
                 duration_ms, status, error_message, tokens_used, cost_usd)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING call_id, server_name, tool_name, caller,
                      project_id, status, duration_ms, cost_usd, called_at
            """,
            server_name,
            tool_name,
            caller,
            project_id,
            duration_ms,
            status,
            error_message,
            tokens_used,
            Decimal(str(cost_usd)),
        )
        return self._row_to_mcp_call(row)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_mcp_call(row: asyncpg.Record) -> McpCallEvent:
        """Convert a DB row to McpCallEvent data shape."""
        return McpCallEvent(
            call_id=row["call_id"],
            server_name=row["server_name"],
            tool_name=row["tool_name"],
            client_id=row["caller"],
            project_id=row["project_id"],
            input_summary="",
            status=row["status"],
            duration_ms=row["duration_ms"],
            cost_usd=Decimal(str(row["cost_usd"])),
            called_at=row["called_at"],
        )
