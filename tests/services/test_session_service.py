"""Tests for SessionService — the most critical service.

SessionService enables inter-agent context passing in the 12-doc pipeline.
Every test uses a real PostgreSQL database via testcontainers.
No mocking of the database — ever (per TESTING.md Doc 13, Section 3).
"""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio

from services.session_service import SessionService


@pytest_asyncio.fixture
async def service(db_pool):
    """Fresh SessionService for each test."""
    return SessionService(db_pool)


@pytest.fixture
def session_id():
    """Unique session ID per test to ensure isolation."""
    return uuid4()


class TestWrite:
    """Tests for SessionService.write()."""

    @pytest.mark.asyncio
    async def test_write_stores_value(self, service: SessionService, session_id, db_pool):
        """Write a key and verify it's stored in the database."""
        await service.write(session_id, "prd_doc", "# PRD Content", written_by="D1-prd")

        row = await db_pool.fetchrow(
            "SELECT value, written_by FROM session_context WHERE session_id = $1 AND key = $2",
            session_id,
            "prd_doc",
        )
        assert row is not None
        assert row["written_by"] == "D1-prd"

    @pytest.mark.asyncio
    async def test_write_overwrites_on_retry(self, service: SessionService, session_id):
        """Writing the same key twice should update (for retry after quality gate failure)."""
        await service.write(session_id, "arch_doc", "v1 content", written_by="D2-arch")
        await service.write(session_id, "arch_doc", "v2 improved content", written_by="D2-arch")

        result = await service.read(session_id, "arch_doc")
        assert result == "v2 improved content"

    @pytest.mark.asyncio
    async def test_write_different_keys_same_session(self, service: SessionService, session_id):
        """Multiple agents write different keys to the same session."""
        await service.write(session_id, "prd_doc", "prd content", written_by="D1-prd")
        await service.write(session_id, "arch_doc", "arch content", written_by="D2-arch")

        keys = await service.list_keys(session_id)
        assert "prd_doc" in keys
        assert "arch_doc" in keys


class TestRead:
    """Tests for SessionService.read()."""

    @pytest.mark.asyncio
    async def test_read_existing_key(self, service: SessionService, session_id):
        """Read a key that was previously written."""
        await service.write(session_id, "roadmap_doc", "roadmap content", written_by="D0-roadmap")
        result = await service.read(session_id, "roadmap_doc")
        assert result == "roadmap content"

    @pytest.mark.asyncio
    async def test_read_nonexistent_key_returns_none(self, service: SessionService, session_id):
        """Reading a key that doesn't exist returns None (not an exception)."""
        result = await service.read(session_id, "nonexistent_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_read_wrong_session_returns_none(self, service: SessionService, session_id):
        """Keys are scoped to session_id — cross-session reads return None."""
        await service.write(session_id, "prd_doc", "content", written_by="D1-prd")
        other_session = uuid4()
        result = await service.read(other_session, "prd_doc")
        assert result is None


class TestReadMany:
    """Tests for SessionService.read_many()."""

    @pytest.mark.asyncio
    async def test_read_many_all_present(self, service: SessionService, session_id):
        """Read multiple keys when all are present."""
        await service.write(session_id, "prd_doc", "prd", written_by="D1")
        await service.write(session_id, "arch_doc", "arch", written_by="D2")
        await service.write(session_id, "quality_doc", "quality", written_by="D4")

        result = await service.read_many(session_id, ["prd_doc", "arch_doc", "quality_doc"])
        assert result["prd_doc"] == "prd"
        assert result["arch_doc"] == "arch"
        assert result["quality_doc"] == "quality"

    @pytest.mark.asyncio
    async def test_read_many_missing_key_raises(self, service: SessionService, session_id):
        """read_many raises KeyError if any required key is missing."""
        await service.write(session_id, "prd_doc", "prd", written_by="D1")

        with pytest.raises(KeyError, match="Missing session keys"):
            await service.read_many(session_id, ["prd_doc", "arch_doc"])


class TestExists:
    """Tests for SessionService.exists()."""

    @pytest.mark.asyncio
    async def test_exists_true(self, service: SessionService, session_id):
        await service.write(session_id, "prd_doc", "content", written_by="D1")
        assert await service.exists(session_id, "prd_doc") is True

    @pytest.mark.asyncio
    async def test_exists_false(self, service: SessionService, session_id):
        assert await service.exists(session_id, "nonexistent") is False


class TestListKeys:
    """Tests for SessionService.list_keys()."""

    @pytest.mark.asyncio
    async def test_list_keys_returns_all(self, service: SessionService, session_id):
        await service.write(session_id, "a_key", "val1", written_by="agent1")
        await service.write(session_id, "b_key", "val2", written_by="agent2")

        keys = await service.list_keys(session_id)
        assert "a_key" in keys
        assert "b_key" in keys

    @pytest.mark.asyncio
    async def test_list_keys_empty_session(self, service: SessionService, session_id):
        keys = await service.list_keys(session_id)
        assert keys == []

    @pytest.mark.asyncio
    async def test_list_keys_isolation(self, service: SessionService, session_id):
        """Keys from other sessions are not returned."""
        other = uuid4()
        await service.write(session_id, "my_key", "mine", written_by="me")
        await service.write(other, "other_key", "theirs", written_by="them")

        keys = await service.list_keys(session_id)
        assert "my_key" in keys
        assert "other_key" not in keys


class TestDelete:
    """Tests for SessionService.delete()."""

    @pytest.mark.asyncio
    async def test_delete_existing_key(self, service: SessionService, session_id):
        await service.write(session_id, "temp_key", "val", written_by="agent")
        deleted = await service.delete(session_id, "temp_key")
        assert deleted is True
        assert await service.exists(session_id, "temp_key") is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, service: SessionService, session_id):
        deleted = await service.delete(session_id, "no_such_key")
        assert deleted is False


class TestPipelineScenario:
    """Integration test: simulate a mini-pipeline with 3 agents writing/reading context."""

    @pytest.mark.asyncio
    async def test_three_agent_pipeline(self, service: SessionService):
        """Simulate: D0 writes roadmap -> D2 reads roadmap + writes arch -> D3 reads both."""
        run_id = uuid4()

        # Step 1: D0-roadmap writes roadmap_doc
        await service.write(run_id, "roadmap_doc", "# Roadmap v1\n8 phases, 12 milestones", written_by="D0-roadmap")

        # Step 2: D2-arch reads roadmap, writes arch_doc
        roadmap = await service.read(run_id, "roadmap_doc")
        assert roadmap is not None
        assert "Roadmap v1" in roadmap
        await service.write(run_id, "arch_doc", "# Architecture\nShared service layer + 3 MCP servers", written_by="D2-arch")

        # Step 3: D3-claude reads both roadmap and arch
        docs = await service.read_many(run_id, ["roadmap_doc", "arch_doc"])
        assert len(docs) == 2
        assert "Roadmap v1" in docs["roadmap_doc"]
        assert "Shared service layer" in docs["arch_doc"]

        # Verify all keys present
        keys = await service.list_keys(run_id)
        assert set(keys) == {"roadmap_doc", "arch_doc"}
