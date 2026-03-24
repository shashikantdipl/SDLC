"""CostService — Business logic for cost tracking and budget management.

Implements interactions: I-040, I-041, I-048, I-049 from INTERACTION-MAP.
Called by: MCP governance-server tools, REST /api/v1/cost/* routes.
Never import from mcp_servers/ or api/.

Data shapes returned: CostReport, BudgetStatus, CostAnomaly, CostBreakdownItem
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import asyncpg

from schemas.data_shapes import (
    BudgetScope,
    BudgetStatus,
    CostAnomaly,
    CostBreakdownItem,
    CostReport,
    Severity,
)

# ---------------------------------------------------------------------------
# Budget defaults (from MASTER-BUILD-SPEC)
# ---------------------------------------------------------------------------
BUDGET_DEFAULTS: dict[str, Decimal] = {
    "fleet": Decimal(os.environ.get("FLEET_DAILY_BUDGET_USD", "50.00")),
    "project": Decimal(os.environ.get("PROJECT_DAILY_BUDGET_USD", "20.00")),
    "agent": Decimal(os.environ.get("AGENT_DAILY_BUDGET_USD", "5.00")),
}

INVOCATION_LIMIT_USD = Decimal(os.environ.get("INVOCATION_LIMIT_USD", "0.50"))


class BudgetExceededError(Exception):
    """Raised when spend would exceed budget for the given scope."""

    def __init__(self, scope: str, scope_id: str, budget: Decimal, spent: Decimal) -> None:
        self.scope = scope
        self.scope_id = scope_id
        self.budget = budget
        self.spent = spent
        super().__init__(
            f"Budget exceeded for {scope}/{scope_id}: "
            f"spent ${spent} of ${budget} daily limit"
        )


class CostService:
    """Cost tracking and budget enforcement service.

    FAIL-SAFE by design: if the database is unreachable, record_spend raises
    and the agent invocation is BLOCKED.  This prevents runaway costs.
    """

    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # INTERNAL: record_spend  (called by BaseHooks after each invocation)
    # ------------------------------------------------------------------
    async def record_spend(
        self,
        agent_id: str,
        project_id: str,
        session_id: UUID,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: Decimal,
    ) -> None:
        """Insert a cost record.  FAIL-SAFE: raises on DB error, never silently succeeds."""
        await self._db.execute(
            """
            INSERT INTO cost_metrics
                (agent_id, project_id, session_id, model,
                 input_tokens, output_tokens, cost_usd)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            agent_id,
            project_id,
            session_id,
            model,
            input_tokens,
            output_tokens,
            cost_usd,
        )

    # ------------------------------------------------------------------
    # I-041: check_budget
    # ------------------------------------------------------------------
    async def check_budget(self, scope: str, scope_id: str) -> BudgetStatus:
        """Check remaining budget for a scope (fleet | project | agent).

        Sums cost_usd for today (UTC) and compares against BUDGET_DEFAULTS.
        """
        budget = BUDGET_DEFAULTS.get(scope)
        if budget is None:
            raise ValueError(f"Unknown budget scope: {scope!r}; expected one of {list(BUDGET_DEFAULTS)}")

        if scope == "fleet":
            row = await self._db.fetchrow(
                """
                SELECT COALESCE(SUM(cost_usd), 0) AS spent
                FROM cost_metrics
                WHERE recorded_at >= date_trunc('day', NOW() AT TIME ZONE 'UTC')
                """
            )
        elif scope == "project":
            row = await self._db.fetchrow(
                """
                SELECT COALESCE(SUM(cost_usd), 0) AS spent
                FROM cost_metrics
                WHERE project_id = $1
                  AND recorded_at >= date_trunc('day', NOW() AT TIME ZONE 'UTC')
                """,
                scope_id,
            )
        elif scope == "agent":
            row = await self._db.fetchrow(
                """
                SELECT COALESCE(SUM(cost_usd), 0) AS spent
                FROM cost_metrics
                WHERE agent_id = $1
                  AND recorded_at >= date_trunc('day', NOW() AT TIME ZONE 'UTC')
                """,
                scope_id,
            )
        else:
            raise ValueError(f"Invalid scope: {scope!r}")

        spent = Decimal(str(row["spent"]))
        remaining = max(budget - spent, Decimal("0"))
        utilization = float(spent / budget * 100) if budget > 0 else 0.0

        return BudgetStatus(
            scope=BudgetScope(scope),
            scope_id=scope_id,
            budget_usd=budget,
            spent_usd=spent,
            remaining_usd=remaining,
            utilization_pct=round(utilization, 2),
            period="today",
        )

    # ------------------------------------------------------------------
    # I-049: update_budget_threshold
    # ------------------------------------------------------------------
    async def update_budget_threshold(
        self, scope: str, scope_id: str, new_budget: Decimal
    ) -> BudgetStatus:
        """Update the budget threshold for a scope and return refreshed status.

        In-memory only for now (per-process); a production implementation
        would persist to a budget_thresholds table.
        """
        if scope not in BUDGET_DEFAULTS:
            raise ValueError(f"Unknown budget scope: {scope!r}")
        if new_budget <= 0:
            raise ValueError("Budget must be positive")

        BUDGET_DEFAULTS[scope] = new_budget
        return await self.check_budget(scope, scope_id)

    # ------------------------------------------------------------------
    # I-040: get_report
    # ------------------------------------------------------------------
    async def get_report(
        self, scope: str, scope_id: str, period_days: int = 7
    ) -> CostReport:
        """Aggregate cost data for *scope* over the last *period_days* days."""
        if scope not in ("fleet", "project", "agent"):
            raise ValueError(f"Invalid scope: {scope!r}")

        # Build query depending on scope
        if scope == "fleet":
            rows = await self._db.fetch(
                """
                SELECT agent_id,
                       COALESCE(SUM(cost_usd), 0) AS total,
                       COUNT(*) AS invocations
                FROM cost_metrics
                WHERE recorded_at >= NOW() - ($1 || ' days')::INTERVAL
                GROUP BY agent_id
                ORDER BY total DESC
                """,
                str(period_days),
            )
        elif scope == "project":
            rows = await self._db.fetch(
                """
                SELECT agent_id,
                       COALESCE(SUM(cost_usd), 0) AS total,
                       COUNT(*) AS invocations
                FROM cost_metrics
                WHERE recorded_at >= NOW() - ($1 || ' days')::INTERVAL
                  AND project_id = $2
                GROUP BY agent_id
                ORDER BY total DESC
                """,
                str(period_days),
                scope_id,
            )
        else:  # agent
            rows = await self._db.fetch(
                """
                SELECT agent_id,
                       COALESCE(SUM(cost_usd), 0) AS total,
                       COUNT(*) AS invocations
                FROM cost_metrics
                WHERE recorded_at >= NOW() - ($1 || ' days')::INTERVAL
                  AND agent_id = $2
                GROUP BY agent_id
                ORDER BY total DESC
                """,
                str(period_days),
                scope_id,
            )

        total = Decimal("0")
        items: list[CostBreakdownItem] = []
        for r in rows:
            cost = Decimal(str(r["total"]))
            total += cost
            items.append(
                CostBreakdownItem(
                    label=r["agent_id"],
                    cost_usd=cost,
                    invocations=r["invocations"],
                    percentage=0.0,  # filled below
                )
            )

        # Calculate percentages
        if total > 0:
            for item in items:
                item.percentage = round(float(item.cost_usd / total * 100), 2)

        return CostReport(
            scope=BudgetScope(scope),
            scope_id=scope_id,
            period_days=period_days,
            total_cost_usd=total,
            breakdown=items,
            generated_at=datetime.now(tz=timezone.utc),
        )

    # ------------------------------------------------------------------
    # I-048: get_anomalies
    # ------------------------------------------------------------------
    async def get_anomalies(self, project_id: str) -> list[CostAnomaly]:
        """Detect cost anomalies: any agent whose today-spend > 2x the average.

        Simplified heuristic: compute average daily spend per agent over the
        past 7 days (excluding today), then compare against today's spend.
        """
        rows = await self._db.fetch(
            """
            WITH daily AS (
                SELECT agent_id,
                       date_trunc('day', recorded_at) AS day,
                       SUM(cost_usd) AS daily_cost
                FROM cost_metrics
                WHERE project_id = $1
                  AND recorded_at >= NOW() - INTERVAL '7 days'
                GROUP BY agent_id, date_trunc('day', recorded_at)
            ),
            avg_cost AS (
                SELECT agent_id,
                       AVG(daily_cost) AS avg_daily
                FROM daily
                WHERE day < date_trunc('day', NOW() AT TIME ZONE 'UTC')
                GROUP BY agent_id
            ),
            today AS (
                SELECT agent_id,
                       SUM(cost_usd) AS today_cost
                FROM cost_metrics
                WHERE project_id = $1
                  AND recorded_at >= date_trunc('day', NOW() AT TIME ZONE 'UTC')
                GROUP BY agent_id
            )
            SELECT t.agent_id,
                   COALESCE(a.avg_daily, 0) AS expected,
                   t.today_cost AS actual
            FROM today t
            LEFT JOIN avg_cost a ON a.agent_id = t.agent_id
            WHERE t.today_cost > 2 * COALESCE(a.avg_daily, 0)
              AND COALESCE(a.avg_daily, 0) > 0
            """,
            project_id,
        )

        anomalies: list[CostAnomaly] = []
        now = datetime.now(tz=timezone.utc)
        for r in rows:
            expected = Decimal(str(r["expected"]))
            actual = Decimal(str(r["actual"]))
            deviation = float((actual - expected) / expected * 100) if expected > 0 else 0.0
            severity = Severity.CRITICAL if deviation > 300 else Severity.WARNING

            anomalies.append(
                CostAnomaly(
                    anomaly_id=uuid4(),
                    agent_id=r["agent_id"],
                    project_id=project_id,
                    expected_cost_usd=expected,
                    actual_cost_usd=actual,
                    deviation_pct=round(deviation, 2),
                    detected_at=now,
                    severity=severity,
                )
            )

        return anomalies
