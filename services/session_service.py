"""SessionService — Business logic for session context management.

Implements the SessionStore from AGENT-HANDOFF-PROTOCOL (Doc 14).
Enables inter-agent context passing within pipeline runs.
Each agent writes ONE key; downstream agents read it.

Interactions: I-080 (internal, used by pipeline orchestrator)
Called by: PipelineService, MCP agents-server (internal), REST /api/v1/sessions/*
Never import from mcp_servers/ or api/.
"""

from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

import asyncpg


class SessionService:
    """Session key-value store backed by PostgreSQL session_context table.

    Storage rules (from AGENT-HANDOFF-PROTOCOL):
    - Every agent writes exactly ONE session key
    - Session is scoped to a run_id (pipeline execution)
    - Values are stored as JSONB
    - TTL default: 86400 seconds (24 hours)
    - Persists across restarts (PostgreSQL-backed)
    """

    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    async def write(
        self,
        session_id: UUID,
        key: str,
        value: str,
        written_by: str,
        ttl_seconds: int = 86400,
    ) -> None:
        """Store a document/value in the session context.

        Uses INSERT ... ON CONFLICT UPDATE to allow overwriting the same key
        (e.g., on retry after quality gate failure).
        """
        await self._db.execute(
            """
            INSERT INTO session_context (session_id, key, value, written_by, ttl_seconds)
            VALUES ($1, $2, $3::jsonb, $4, $5)
            ON CONFLICT (session_id, key)
            DO UPDATE SET
                value = EXCLUDED.value,
                written_by = EXCLUDED.written_by,
                written_at = NOW(),
                ttl_seconds = EXCLUDED.ttl_seconds
            """,
            session_id,
            key,
            json.dumps(value),
            written_by,
            ttl_seconds,
        )

    async def read(self, session_id: UUID, key: str) -> str | None:
        """Read a document/value from session context.

        Returns None if the key doesn't exist or has expired.
        """
        row = await self._db.fetchrow(
            """
            SELECT value FROM session_context
            WHERE session_id = $1 AND key = $2
              AND (expires_at IS NULL OR expires_at > NOW())
            """,
            session_id,
            key,
        )
        if row is None:
            return None
        # Value is stored as JSONB; unwrap the JSON string
        raw = row["value"]
        if isinstance(raw, str):
            return json.loads(raw)
        return raw

    async def read_many(self, session_id: UUID, keys: list[str]) -> dict[str, str]:
        """Read multiple keys in one query. Raises KeyError if any required key is missing."""
        rows = await self._db.fetch(
            """
            SELECT key, value FROM session_context
            WHERE session_id = $1 AND key = ANY($2)
              AND (expires_at IS NULL OR expires_at > NOW())
            """,
            session_id,
            keys,
        )
        result = {}
        for row in rows:
            raw = row["value"]
            result[row["key"]] = json.loads(raw) if isinstance(raw, str) else raw

        missing = set(keys) - set(result.keys())
        if missing:
            raise KeyError(f"Missing session keys: {missing}")

        return result

    async def exists(self, session_id: UUID, key: str) -> bool:
        """Check if a key exists and has not expired."""
        row = await self._db.fetchrow(
            """
            SELECT 1 FROM session_context
            WHERE session_id = $1 AND key = $2
              AND (expires_at IS NULL OR expires_at > NOW())
            """,
            session_id,
            key,
        )
        return row is not None

    async def list_keys(self, session_id: UUID) -> list[str]:
        """List all non-expired keys for a session."""
        rows = await self._db.fetch(
            """
            SELECT key FROM session_context
            WHERE session_id = $1
              AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY written_at
            """,
            session_id,
        )
        return [row["key"] for row in rows]

    async def delete(self, session_id: UUID, key: str) -> bool:
        """Delete a specific key. Returns True if deleted, False if not found."""
        result = await self._db.execute(
            "DELETE FROM session_context WHERE session_id = $1 AND key = $2",
            session_id,
            key,
        )
        return result == "DELETE 1"

    async def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of deleted rows."""
        result = await self._db.execute(
            "DELETE FROM session_context WHERE expires_at < NOW()"
        )
        # Result is like "DELETE 42"
        count = int(result.split()[-1])
        return count
