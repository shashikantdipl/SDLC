"""Tests for CostService — cost tracking and budget enforcement.

Every test uses a real PostgreSQL database via testcontainers.
No mocking of the database — ever (per TESTING.md Doc 13, Section 3).
"""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio

from services.cost_service import (
    BUDGET_DEFAULTS,
    BudgetExceededError,
    CostService,
)
from schemas.data_shapes import BudgetScope


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def service(db_pool: asyncpg.Pool) -> CostService:
    """Fresh CostService for each test."""
    return CostService(db_pool)


@pytest_asyncio.fixture
async def seed_agent(db_pool: asyncpg.Pool):
    """Insert a test agent into agent_registry and clean up after.

    Returns the agent_id for use in tests.
    """
    agent_id = f"test-agent-{uuid4().hex[:8]}"
    await db_pool.execute(
        """
        INSERT INTO agent_registry (agent_id, name, phase, archetype, model, status)
        VALUES ($1, $2, 'build', 'ci-gate', 'claude-sonnet-4-6', 'active')
        ON CONFLICT (agent_id) DO NOTHING
        """,
        agent_id,
        f"Test Agent {agent_id}",
    )
    yield agent_id
    # Cleanup: remove cost rows then agent row
    await db_pool.execute("DELETE FROM cost_metrics WHERE agent_id = $1", agent_id)
    await db_pool.execute("DELETE FROM agent_registry WHERE agent_id = $1", agent_id)


@pytest_asyncio.fixture
async def seed_agents_pair(db_pool: asyncpg.Pool):
    """Insert two test agents for anomaly / multi-agent tests.

    Yields (agent_a, agent_b).
    """
    a = f"test-a-{uuid4().hex[:8]}"
    b = f"test-b-{uuid4().hex[:8]}"
    for aid in (a, b):
        await db_pool.execute(
            """
            INSERT INTO agent_registry (agent_id, name, phase, archetype, model, status)
            VALUES ($1, $2, 'build', 'ci-gate', 'claude-sonnet-4-6', 'active')
            ON CONFLICT (agent_id) DO NOTHING
            """,
            aid,
            f"Test Agent {aid}",
        )
    yield a, b
    for aid in (a, b):
        await db_pool.execute("DELETE FROM cost_metrics WHERE agent_id = $1", aid)
        await db_pool.execute("DELETE FROM agent_registry WHERE agent_id = $1", aid)


@pytest.fixture
def project_id() -> str:
    return f"proj-{uuid4().hex[:8]}"


@pytest.fixture
def session_id():
    return uuid4()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _record(
    service: CostService,
    agent_id: str,
    project_id: str,
    cost: str = "0.10",
    model: str = "claude-sonnet-4-6",
    input_tokens: int = 500,
    output_tokens: int = 200,
) -> None:
    """Shorthand to record a spend entry."""
    await service.record_spend(
        agent_id=agent_id,
        project_id=project_id,
        session_id=uuid4(),
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=Decimal(cost),
    )


# ===================================================================
# Tests: record_spend
# ===================================================================

class TestRecordSpend:
    """record_spend stores a cost row and is FAIL-SAFE."""

    @pytest.mark.asyncio
    async def test_stores_cost_record(
        self, service: CostService, seed_agent: str, project_id: str, session_id, db_pool,
    ):
        """Verify the row lands in cost_metrics with correct values."""
        await service.record_spend(
            agent_id=seed_agent,
            project_id=project_id,
            session_id=session_id,
            model="claude-sonnet-4-6",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=Decimal("0.123456"),
        )

        row = await db_pool.fetchrow(
            "SELECT * FROM cost_metrics WHERE agent_id = $1 AND session_id = $2",
            seed_agent,
            session_id,
        )
        assert row is not None
        assert row["project_id"] == project_id
        assert row["model"] == "claude-sonnet-4-6"
        assert row["input_tokens"] == 1000
        assert row["output_tokens"] == 500
        assert Decimal(str(row["cost_usd"])) == Decimal("0.123456")

    @pytest.mark.asyncio
    async def test_fail_safe_propagates_db_error(
        self, seed_agent: str, project_id: str,
    ):
        """If the DB is unreachable, record_spend must raise — never silently succeed."""
        # Create a pool pointed at a non-existent host to simulate DB failure
        with pytest.raises(Exception):
            bad_pool = await asyncpg.create_pool(
                "postgresql://nobody:nope@127.0.0.1:1/nodb",
                min_size=0,
                max_size=1,
                timeout=1,
            )
            bad_service = CostService(bad_pool)
            await bad_service.record_spend(
                agent_id=seed_agent,
                project_id=project_id,
                session_id=uuid4(),
                model="claude-sonnet-4-6",
                input_tokens=100,
                output_tokens=50,
                cost_usd=Decimal("0.01"),
            )

    @pytest.mark.asyncio
    async def test_record_spend_multiple_entries(
        self, service: CostService, seed_agent: str, project_id: str, db_pool,
    ):
        """Multiple spend records for the same agent accumulate."""
        await _record(service, seed_agent, project_id, cost="0.10")
        await _record(service, seed_agent, project_id, cost="0.20")
        await _record(service, seed_agent, project_id, cost="0.05")

        row = await db_pool.fetchrow(
            "SELECT COUNT(*) AS cnt, SUM(cost_usd) AS total FROM cost_metrics WHERE agent_id = $1 AND project_id = $2",
            seed_agent,
            project_id,
        )
        assert row["cnt"] == 3
        assert Decimal(str(row["total"])) == Decimal("0.35")


# ===================================================================
# Tests: check_budget
# ===================================================================

class TestCheckBudget:
    """I-041: check_budget returns correct remaining for each scope."""

    @pytest.mark.asyncio
    async def test_zero_spend_full_budget(
        self, service: CostService, seed_agent: str,
    ):
        """With no spend today, remaining == full budget."""
        status = await service.check_budget("agent", seed_agent)
        assert status.scope == BudgetScope.AGENT
        assert status.spent_usd == Decimal("0")
        assert status.remaining_usd == BUDGET_DEFAULTS["agent"]
        assert status.utilization_pct == 0.0
        assert status.period == "today"

    @pytest.mark.asyncio
    async def test_partial_spend(
        self, service: CostService, seed_agent: str, project_id: str,
    ):
        """After spending $1.50, remaining should decrease accordingly."""
        await _record(service, seed_agent, project_id, cost="1.00")
        await _record(service, seed_agent, project_id, cost="0.50")

        status = await service.check_budget("agent", seed_agent)
        assert status.spent_usd == Decimal("1.50") or status.spent_usd == Decimal("1.500000")
        expected_remaining = BUDGET_DEFAULTS["agent"] - Decimal("1.50")
        assert status.remaining_usd == expected_remaining

    @pytest.mark.asyncio
    async def test_overspend_remaining_clamped_to_zero(
        self, service: CostService, seed_agent: str, project_id: str,
    ):
        """If spend exceeds budget, remaining should be clamped to 0."""
        # Agent budget default is $5.00; spend $6.00
        await _record(service, seed_agent, project_id, cost="6.00")

        status = await service.check_budget("agent", seed_agent)
        assert status.remaining_usd == Decimal("0")
        assert status.utilization_pct > 100.0

    @pytest.mark.asyncio
    async def test_fleet_scope(
        self, service: CostService, seed_agent: str, project_id: str,
    ):
        """Fleet scope sums ALL cost_metrics for today."""
        await _record(service, seed_agent, project_id, cost="2.00")

        status = await service.check_budget("fleet", "all")
        assert status.scope == BudgetScope.FLEET
        # spent_usd should be at least $2.00 (could be more if other tests ran)
        assert status.spent_usd >= Decimal("2.00")

    @pytest.mark.asyncio
    async def test_project_scope(
        self, service: CostService, seed_agent: str, project_id: str,
    ):
        """Project scope only sums costs for a specific project_id."""
        await _record(service, seed_agent, project_id, cost="3.00")

        status = await service.check_budget("project", project_id)
        assert status.scope == BudgetScope.PROJECT
        assert status.spent_usd >= Decimal("3.00")

    @pytest.mark.asyncio
    async def test_invalid_scope_raises(self, service: CostService):
        """Unknown scope raises ValueError."""
        with pytest.raises(ValueError, match="Unknown budget scope"):
            await service.check_budget("universe", "42")


# ===================================================================
# Tests: get_report
# ===================================================================

class TestGetReport:
    """I-040: get_report aggregates cost data over a period."""

    @pytest.mark.asyncio
    async def test_empty_report(self, service: CostService):
        """Report with no matching data returns zero totals and empty breakdown."""
        report = await service.get_report("project", "nonexistent-project", period_days=7)
        assert report.total_cost_usd == Decimal("0")
        assert report.breakdown == []
        assert report.period_days == 7

    @pytest.mark.asyncio
    async def test_report_aggregates_by_agent(
        self, service: CostService, seed_agents_pair: tuple[str, str], project_id: str,
    ):
        """Report should group costs by agent_id."""
        agent_a, agent_b = seed_agents_pair
        await _record(service, agent_a, project_id, cost="1.00")
        await _record(service, agent_a, project_id, cost="0.50")
        await _record(service, agent_b, project_id, cost="2.00")

        report = await service.get_report("project", project_id, period_days=1)
        assert report.total_cost_usd == Decimal("3.50") or report.total_cost_usd == Decimal("3.500000")

        agent_ids = {item.label for item in report.breakdown}
        assert agent_a in agent_ids
        assert agent_b in agent_ids

        # Find agent_a's breakdown
        a_item = next(i for i in report.breakdown if i.label == agent_a)
        assert a_item.invocations == 2
        assert Decimal(str(a_item.cost_usd)) == Decimal("1.50") or Decimal(str(a_item.cost_usd)) == Decimal("1.500000")

    @pytest.mark.asyncio
    async def test_report_percentages_sum_to_100(
        self, service: CostService, seed_agents_pair: tuple[str, str], project_id: str,
    ):
        """Breakdown percentages should sum to approximately 100%."""
        agent_a, agent_b = seed_agents_pair
        await _record(service, agent_a, project_id, cost="3.00")
        await _record(service, agent_b, project_id, cost="7.00")

        report = await service.get_report("project", project_id, period_days=1)
        total_pct = sum(item.percentage for item in report.breakdown)
        assert abs(total_pct - 100.0) < 0.1

    @pytest.mark.asyncio
    async def test_report_agent_scope(
        self, service: CostService, seed_agent: str, project_id: str,
    ):
        """Agent scope only returns data for that specific agent."""
        await _record(service, seed_agent, project_id, cost="0.50")

        report = await service.get_report("agent", seed_agent, period_days=1)
        assert len(report.breakdown) == 1
        assert report.breakdown[0].label == seed_agent


# ===================================================================
# Tests: get_anomalies
# ===================================================================

class TestGetAnomalies:
    """I-048: get_anomalies detects agents with cost > 2x average."""

    @pytest.mark.asyncio
    async def test_no_anomalies_when_no_history(
        self, service: CostService, project_id: str,
    ):
        """No historical data means no anomalies (requires avg > 0)."""
        anomalies = await service.get_anomalies(project_id)
        assert anomalies == []

    @pytest.mark.asyncio
    async def test_no_anomaly_when_spend_is_normal(
        self, service: CostService, seed_agent: str, project_id: str, db_pool,
    ):
        """Agent spending within 2x historical average is not flagged."""
        # Insert historical rows for past 3 days at ~$1/day
        for days_ago in range(1, 4):
            await db_pool.execute(
                """
                INSERT INTO cost_metrics
                    (agent_id, project_id, session_id, model, input_tokens, output_tokens, cost_usd, recorded_at)
                VALUES ($1, $2, $3, 'claude-sonnet-4-6', 500, 200, $4,
                        NOW() - ($5 || ' days')::INTERVAL)
                """,
                seed_agent,
                project_id,
                uuid4(),
                Decimal("1.00"),
                str(days_ago),
            )

        # Today's spend is $1.50 (within 2x of $1.00 average)
        await _record(service, seed_agent, project_id, cost="1.50")

        anomalies = await service.get_anomalies(project_id)
        flagged_agents = {a.agent_id for a in anomalies}
        assert seed_agent not in flagged_agents

    @pytest.mark.asyncio
    async def test_detects_anomaly_when_spend_exceeds_2x(
        self, service: CostService, seed_agent: str, project_id: str, db_pool,
    ):
        """Agent spending > 2x historical average IS flagged as anomaly."""
        # Insert historical rows for past 3 days at ~$1/day
        for days_ago in range(1, 4):
            await db_pool.execute(
                """
                INSERT INTO cost_metrics
                    (agent_id, project_id, session_id, model, input_tokens, output_tokens, cost_usd, recorded_at)
                VALUES ($1, $2, $3, 'claude-sonnet-4-6', 500, 200, $4,
                        NOW() - ($5 || ' days')::INTERVAL)
                """,
                seed_agent,
                project_id,
                uuid4(),
                Decimal("1.00"),
                str(days_ago),
            )

        # Today's spend is $5.00 (5x the $1.00 average — well above 2x threshold)
        await _record(service, seed_agent, project_id, cost="5.00")

        anomalies = await service.get_anomalies(project_id)
        flagged_agents = {a.agent_id for a in anomalies}
        assert seed_agent in flagged_agents

        anomaly = next(a for a in anomalies if a.agent_id == seed_agent)
        assert anomaly.project_id == project_id
        assert anomaly.deviation_pct > 100.0
        assert anomaly.actual_cost_usd > anomaly.expected_cost_usd


# ===================================================================
# Tests: update_budget_threshold (I-049)
# ===================================================================

class TestUpdateBudgetThreshold:
    """I-049: update_budget_threshold changes budget and returns status."""

    @pytest.mark.asyncio
    async def test_updates_budget_and_returns_status(
        self, service: CostService, seed_agent: str,
    ):
        """After updating agent budget to $10, check_budget should reflect it."""
        original = BUDGET_DEFAULTS["agent"]
        try:
            status = await service.update_budget_threshold("agent", seed_agent, Decimal("10.00"))
            assert status.budget_usd == Decimal("10.00")
            assert status.scope == BudgetScope.AGENT
        finally:
            # Restore default to not pollute other tests
            BUDGET_DEFAULTS["agent"] = original

    @pytest.mark.asyncio
    async def test_rejects_zero_budget(self, service: CostService):
        """Budget must be positive."""
        with pytest.raises(ValueError, match="Budget must be positive"):
            await service.update_budget_threshold("agent", "any", Decimal("0"))

    @pytest.mark.asyncio
    async def test_rejects_negative_budget(self, service: CostService):
        """Negative budgets are rejected."""
        with pytest.raises(ValueError, match="Budget must be positive"):
            await service.update_budget_threshold("project", "any", Decimal("-5"))

    @pytest.mark.asyncio
    async def test_rejects_unknown_scope(self, service: CostService):
        """Unknown scope raises ValueError."""
        with pytest.raises(ValueError, match="Unknown budget scope"):
            await service.update_budget_threshold("galaxy", "milkyway", Decimal("100"))
