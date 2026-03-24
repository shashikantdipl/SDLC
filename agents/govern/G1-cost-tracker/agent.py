"""G1-cost-tracker — Cost monitoring and budget enforcement agent.

GOLD STANDARD: Every new agent follows this implementation pattern.

Extends BaseAgent. Calls Claude API with cost data, returns structured report.
Verified with real API: $0.006 per invocation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from sdk.base_agent import BaseAgent
from sdk.base_hooks import BaseHooks


class G1CostTracker(BaseAgent):
    """Cost tracking and budget reporting agent.

    Phase: GOVERN
    Archetype: governance
    Model: claude-haiku-4-5-20251001 (cheapest, fastest)
    Autonomy: T0 (fully autonomous — no human approval needed)
    Budget: $0.05 per invocation
    """

    def __init__(
        self,
        api_key: str | None = None,
        hooks: BaseHooks | None = None,
        dry_run: bool = False,
    ) -> None:
        super().__init__(
            agent_dir=Path(__file__).parent,
            api_key=api_key,
            hooks=hooks,
            dry_run=dry_run,
        )

    async def run(
        self,
        scope: str,
        scope_id: str,
        cost_data: list[dict[str, Any]],
        budget_config: dict[str, Any],
        period_days: int = 7,
        include_breakdown: bool = True,
        session_id: UUID | None = None,
        project_id: str = "default",
    ) -> dict[str, Any]:
        """Run cost analysis and produce a report.

        Args:
            scope: "fleet", "project", or "agent"
            scope_id: identifier for the scope
            cost_data: array of cost records from cost_metrics
            budget_config: budget limits for the scope
            period_days: number of days to cover
            include_breakdown: whether to include per-agent breakdown
            session_id: pipeline session ID (for context passing)
            project_id: project identifier

        Returns:
            Agent invocation result with cost report in output field
        """
        input_data = {
            "scope": scope,
            "scope_id": scope_id,
            "period_days": period_days,
            "include_breakdown": include_breakdown,
            "cost_data": cost_data,
            "budget_config": budget_config,
        }

        result = await self.invoke(
            input_data=input_data,
            session_id=session_id,
            project_id=project_id,
        )

        return result
