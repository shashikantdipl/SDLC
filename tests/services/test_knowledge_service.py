"""Tests for KnowledgeService — knowledge base and exception management.

Covers: create_exception, search by query, search by tier,
promote client→stack, promote stack→universal, promote backwards raises ValueError,
list by tier, list active only, and data-shape compliance.
Real PostgreSQL via testcontainers — no DB mocks.
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from services.knowledge_service import KnowledgeService
from schemas.data_shapes import (
    KnowledgeException,
    KnowledgeTier,
    Severity,
)


@pytest_asyncio.fixture
async def service(db_pool):
    """KnowledgeService instance backed by test database."""
    return KnowledgeService(db_pool)


@pytest_asyncio.fixture
async def seed_exceptions(db_pool):
    """Insert test knowledge exceptions and clean up after."""
    exceptions = [
        ("EXC-seed0001", "No hardcoded secrets", "All secrets must use vault references", "warning", "universal", None, None, True),
        ("EXC-seed0002", "React 18 hook rules", "Hooks must be called at top level only", "high", "stack", "react-stack", None, True),
        ("EXC-seed0003", "Client retry policy", "API calls must retry 3 times with backoff", "critical", "client", None, "client-acme", True),
        ("EXC-seed0004", "Deprecated pattern", "Do not use legacy auth module", "warning", "universal", None, None, False),
    ]
    for exc_id, title, rule, severity, tier, stack_name, client_id, active in exceptions:
        await db_pool.execute(
            """
            INSERT INTO knowledge_exceptions
                (exception_id, title, rule, severity, tier, stack_name, client_id, active, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'test-harness')
            ON CONFLICT (exception_id) DO NOTHING
            """,
            exc_id, title, rule, severity, tier, stack_name, client_id, active,
        )

    yield exceptions

    # Clean up
    for exc_id, *_ in exceptions:
        await db_pool.execute(
            "DELETE FROM knowledge_exceptions WHERE exception_id = $1", exc_id
        )


# ---- I-061: create_exception ----


class TestCreateException:
    """I-061: Create a new knowledge exception."""

    @pytest.mark.asyncio
    async def test_create_universal_exception(self, service: KnowledgeService):
        result = await service.create_exception(
            title="Test universal rule",
            rule="All modules must have docstrings",
            severity="warning",
            tier="universal",
            created_by="test-user",
        )
        assert result.exception_id.startswith("EXC-")
        assert result.title == "Test universal rule"
        assert result.tier == KnowledgeTier.UNIVERSAL
        assert result.active is True
        assert isinstance(result, KnowledgeException)

        # Clean up
        await service._db.execute(
            "DELETE FROM knowledge_exceptions WHERE exception_id = $1",
            result.exception_id,
        )

    @pytest.mark.asyncio
    async def test_create_client_exception_requires_client_id(self, service: KnowledgeService):
        with pytest.raises(ValueError, match="client_id is required"):
            await service.create_exception(
                title="Client rule",
                rule="Must use client SDK",
                severity="warning",
                tier="client",
                created_by="test-user",
            )

    @pytest.mark.asyncio
    async def test_create_stack_exception_requires_stack_name(self, service: KnowledgeService):
        with pytest.raises(ValueError, match="stack_name is required"):
            await service.create_exception(
                title="Stack rule",
                rule="Must use stack conventions",
                severity="warning",
                tier="stack",
                created_by="test-user",
            )

    @pytest.mark.asyncio
    async def test_create_client_exception_with_client_id(self, service: KnowledgeService):
        result = await service.create_exception(
            title="Client-specific rule",
            rule="Use ACME auth provider",
            severity="critical",
            tier="client",
            created_by="test-user",
            client_id="client-acme",
        )
        assert result.tier == KnowledgeTier.CLIENT
        assert result.client_id == "client-acme"

        await service._db.execute(
            "DELETE FROM knowledge_exceptions WHERE exception_id = $1",
            result.exception_id,
        )

    @pytest.mark.asyncio
    async def test_create_stack_exception_with_stack_name(self, service: KnowledgeService):
        result = await service.create_exception(
            title="Stack convention",
            rule="Use Next.js app router",
            severity="high",
            tier="stack",
            created_by="test-user",
            stack_name="nextjs-stack",
        )
        assert result.tier == KnowledgeTier.STACK
        assert result.stack_name == "nextjs-stack"

        await service._db.execute(
            "DELETE FROM knowledge_exceptions WHERE exception_id = $1",
            result.exception_id,
        )


# ---- I-060: search_exceptions ----


class TestSearchExceptions:
    """I-060: Full-text search on knowledge exceptions."""

    @pytest.mark.asyncio
    async def test_search_by_title_keyword(self, service: KnowledgeService, seed_exceptions):
        results = await service.search("secrets")
        assert any(e.exception_id == "EXC-seed0001" for e in results)

    @pytest.mark.asyncio
    async def test_search_by_rule_keyword(self, service: KnowledgeService, seed_exceptions):
        results = await service.search("vault")
        assert any(e.exception_id == "EXC-seed0001" for e in results)

    @pytest.mark.asyncio
    async def test_search_with_tier_filter(self, service: KnowledgeService, seed_exceptions):
        results = await service.search("hook", tier="stack")
        assert all(e.tier == KnowledgeTier.STACK for e in results)
        assert any(e.exception_id == "EXC-seed0002" for e in results)

    @pytest.mark.asyncio
    async def test_search_no_results(self, service: KnowledgeService, seed_exceptions):
        results = await service.search("zzzznonexistenttermzzzz")
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_respects_limit(self, service: KnowledgeService, seed_exceptions):
        results = await service.search("must", limit=1)
        assert len(results) <= 1


# ---- I-062: promote_exception ----


class TestPromoteException:
    """I-062: Promote exception to higher tier."""

    @pytest.mark.asyncio
    async def test_promote_client_to_stack(self, service: KnowledgeService, seed_exceptions):
        result = await service.promote("EXC-seed0003", "stack", "admin-user")
        assert result.tier == KnowledgeTier.STACK

    @pytest.mark.asyncio
    async def test_promote_stack_to_universal(self, service: KnowledgeService, seed_exceptions):
        result = await service.promote("EXC-seed0002", "universal", "admin-user")
        assert result.tier == KnowledgeTier.UNIVERSAL

    @pytest.mark.asyncio
    async def test_promote_backwards_raises_error(self, service: KnowledgeService, seed_exceptions):
        """Cannot demote: universal → stack or stack → client."""
        with pytest.raises(ValueError, match="promotion must go UP"):
            await service.promote("EXC-seed0001", "stack", "admin-user")

    @pytest.mark.asyncio
    async def test_promote_same_tier_raises_error(self, service: KnowledgeService, seed_exceptions):
        with pytest.raises(ValueError, match="promotion must go UP"):
            await service.promote("EXC-seed0001", "universal", "admin-user")

    @pytest.mark.asyncio
    async def test_promote_nonexistent_raises_error(self, service: KnowledgeService, seed_exceptions):
        with pytest.raises(ValueError, match="Exception not found"):
            await service.promote("EXC-ghost", "universal", "admin-user")


# ---- I-063: list_exceptions ----


class TestListExceptions:
    """I-063: List exceptions by tier."""

    @pytest.mark.asyncio
    async def test_list_all_active(self, service: KnowledgeService, seed_exceptions):
        results = await service.list_exceptions(active_only=True)
        exc_ids = {e.exception_id for e in results}
        assert "EXC-seed0001" in exc_ids
        assert "EXC-seed0002" in exc_ids
        assert "EXC-seed0003" in exc_ids
        # EXC-seed0004 is inactive
        assert "EXC-seed0004" not in exc_ids

    @pytest.mark.asyncio
    async def test_list_includes_inactive(self, service: KnowledgeService, seed_exceptions):
        results = await service.list_exceptions(active_only=False)
        exc_ids = {e.exception_id for e in results}
        assert "EXC-seed0004" in exc_ids

    @pytest.mark.asyncio
    async def test_list_by_tier_universal(self, service: KnowledgeService, seed_exceptions):
        results = await service.list_exceptions(tier="universal", active_only=False)
        assert all(e.tier == KnowledgeTier.UNIVERSAL for e in results)
        exc_ids = {e.exception_id for e in results}
        assert "EXC-seed0001" in exc_ids

    @pytest.mark.asyncio
    async def test_list_by_tier_client(self, service: KnowledgeService, seed_exceptions):
        results = await service.list_exceptions(tier="client")
        assert all(e.tier == KnowledgeTier.CLIENT for e in results)

    @pytest.mark.asyncio
    async def test_list_respects_limit(self, service: KnowledgeService, seed_exceptions):
        results = await service.list_exceptions(active_only=False, limit=2)
        assert len(results) <= 2


# ---- Data shape compliance ----


class TestKnowledgeDataShapeCompliance:
    """Verify returned objects match INTERACTION-MAP shapes exactly."""

    @pytest.mark.asyncio
    async def test_knowledge_exception_has_all_fields(self, service: KnowledgeService, seed_exceptions):
        results = await service.list_exceptions()
        exc = results[0]
        assert hasattr(exc, "exception_id")
        assert hasattr(exc, "title")
        assert hasattr(exc, "rule")
        assert hasattr(exc, "severity")
        assert hasattr(exc, "tier")
        assert hasattr(exc, "active")
        assert hasattr(exc, "fire_count")
        assert hasattr(exc, "created_by")
        assert hasattr(exc, "created_at")

    @pytest.mark.asyncio
    async def test_knowledge_exception_serializes_to_json(self, service: KnowledgeService, seed_exceptions):
        results = await service.list_exceptions()
        json_data = results[0].model_dump(mode="json")
        assert "exception_id" in json_data
        assert "tier" in json_data
        assert "severity" in json_data
        assert "active" in json_data
