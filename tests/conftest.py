"""Shared test fixtures for the Agentic SDLC Platform.

Database strategy: testcontainers PostgreSQL (session-scoped).
Each test uses a transaction that rolls back for isolation.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import asyncpg
import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# NOTE: Testcontainers fixture will be added in Phase 1 when migrations are ready.
# For now, this placeholder ensures pytest discovers the conftest.
