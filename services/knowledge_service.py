"""KnowledgeService — Business logic for knowledge base and exception management.

Implements interactions: I-060, I-061, I-062, I-063 from INTERACTION-MAP.
Called by: MCP knowledge-server tools, REST /api/v1/knowledge/* routes.
Never import from mcp_servers/ or api/.

Data shapes returned: KnowledgeException
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import asyncpg

from schemas.data_shapes import KnowledgeException, KnowledgeTier, Severity

# Tier promotion order: client (0) → stack (1) → universal (2)
_TIER_RANK: dict[str, int] = {
    "client": 0,
    "stack": 1,
    "universal": 2,
}


class KnowledgeService:
    """Knowledge exception management.

    All public methods return INTERACTION-MAP data shapes.
    """

    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # I-060: search_exceptions
    # ------------------------------------------------------------------
    async def search(
        self,
        query: str,
        tier: str | None = None,
        limit: int = 20,
    ) -> list[KnowledgeException]:
        """I-060: Full-text search on knowledge exceptions (title + rule).

        Uses PostgreSQL to_tsvector/plainto_tsquery for full-text search.
        """
        conditions: list[str] = [
            "to_tsvector('english', title || ' ' || rule) @@ plainto_tsquery('english', $1)"
        ]
        params: list[object] = [query]
        idx = 2

        if tier is not None:
            conditions.append(f"tier = ${idx}")
            params.append(tier)
            idx += 1

        where = " WHERE " + " AND ".join(conditions)

        rows = await self._db.fetch(
            f"""
            SELECT exception_id, title, rule, severity, tier,
                   stack_name, client_id, active, fire_count,
                   created_by, created_at
            FROM knowledge_exceptions
            {where}
            ORDER BY created_at DESC
            LIMIT ${idx}
            """,
            *params,
            limit,
        )
        return [self._row_to_exception(row) for row in rows]

    # ------------------------------------------------------------------
    # I-061: create_exception
    # ------------------------------------------------------------------
    async def create_exception(
        self,
        title: str,
        rule: str,
        severity: str,
        tier: str,
        created_by: str,
        stack_name: str | None = None,
        client_id: str | None = None,
        tags: list[str] | None = None,
    ) -> KnowledgeException:
        """I-061: Create a new knowledge exception."""
        exception_id = f"EXC-{uuid4().hex[:8]}"

        # Validate tier constraints
        if tier == "client" and not client_id:
            raise ValueError("client_id is required for client-tier exceptions")
        if tier == "stack" and not stack_name:
            raise ValueError("stack_name is required for stack-tier exceptions")

        row = await self._db.fetchrow(
            """
            INSERT INTO knowledge_exceptions
                (exception_id, title, rule, severity, tier,
                 stack_name, client_id, active, tags, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE, $8, $9)
            RETURNING exception_id, title, rule, severity, tier,
                      stack_name, client_id, active, fire_count,
                      created_by, created_at
            """,
            exception_id,
            title,
            rule,
            severity,
            tier,
            stack_name,
            client_id,
            tags or [],
            created_by,
        )
        return self._row_to_exception(row)

    # ------------------------------------------------------------------
    # I-062: promote_exception
    # ------------------------------------------------------------------
    async def promote(
        self,
        exception_id: str,
        target_tier: str,
        promoted_by: str,
    ) -> KnowledgeException:
        """I-062: Promote exception to higher tier (client → stack → universal).

        Raises ValueError if promotion direction is invalid (sideways or down).
        """
        # Fetch current tier
        current = await self._db.fetchrow(
            "SELECT tier FROM knowledge_exceptions WHERE exception_id = $1",
            exception_id,
        )
        if current is None:
            raise ValueError(f"Exception not found: {exception_id}")

        current_rank = _TIER_RANK.get(current["tier"])
        target_rank = _TIER_RANK.get(target_tier)

        if target_rank is None:
            raise ValueError(f"Invalid target tier: {target_tier!r}")
        if current_rank is None or target_rank <= current_rank:
            raise ValueError(
                f"Cannot promote from {current['tier']} to {target_tier}; "
                f"promotion must go UP (client → stack → universal)"
            )

        row = await self._db.fetchrow(
            """
            UPDATE knowledge_exceptions
            SET tier = $2,
                promoted_by = $3,
                promoted_at = NOW(),
                updated_at = NOW()
            WHERE exception_id = $1
            RETURNING exception_id, title, rule, severity, tier,
                      stack_name, client_id, active, fire_count,
                      created_by, created_at
            """,
            exception_id,
            target_tier,
            promoted_by,
        )
        return self._row_to_exception(row)

    # ------------------------------------------------------------------
    # I-063: list_exceptions
    # ------------------------------------------------------------------
    async def list_exceptions(
        self,
        tier: str | None = None,
        active_only: bool = True,
        limit: int = 50,
    ) -> list[KnowledgeException]:
        """I-063: List exceptions by tier."""
        conditions: list[str] = []
        params: list[object] = []
        idx = 1

        if tier is not None:
            conditions.append(f"tier = ${idx}")
            params.append(tier)
            idx += 1

        if active_only:
            conditions.append("active = TRUE")

        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

        rows = await self._db.fetch(
            f"""
            SELECT exception_id, title, rule, severity, tier,
                   stack_name, client_id, active, fire_count,
                   created_by, created_at
            FROM knowledge_exceptions
            {where}
            ORDER BY created_at DESC
            LIMIT ${idx}
            """,
            *params,
            limit,
        )
        return [self._row_to_exception(row) for row in rows]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_exception(row: asyncpg.Record) -> KnowledgeException:
        """Convert a DB row to KnowledgeException data shape."""
        return KnowledgeException(
            exception_id=row["exception_id"],
            title=row["title"],
            rule=row["rule"],
            severity=Severity(row["severity"]),
            tier=KnowledgeTier(row["tier"]),
            stack_name=row["stack_name"],
            client_id=row["client_id"],
            active=row["active"],
            fire_count=row["fire_count"],
            created_by=row["created_by"],
            created_at=row["created_at"],
        )
