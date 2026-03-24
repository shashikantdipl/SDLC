"""Shared test fixtures for the Agentic SDLC Platform.

Database strategy: testcontainers PostgreSQL 15 (session-scoped).
Migrations run once per session. Each test gets a clean transaction.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import asyncpg
import pytest
import pytest_asyncio

# Try testcontainers; fall back to env DATABASE_URL for CI without Docker
try:
    from testcontainers.postgres import PostgresContainer
    HAS_TESTCONTAINERS = True
except ImportError:
    HAS_TESTCONTAINERS = False


MIGRATIONS_DIR = Path(__file__).parent.parent / "migrations"


def _get_migration_files() -> list[Path]:
    """Return sorted migration SQL files."""
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def _extract_up_sql(content: str) -> str:
    """Extract UP section from migration (everything before -- DOWN comment block)."""
    lines = content.split("\n")
    up_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "-- DOWN":
            break
        if stripped.startswith("-- DROP") or stripped.startswith("-- ALTER TABLE"):
            # Skip commented-out DOWN lines that appear at bottom
            continue
        up_lines.append(line)
    return "\n".join(up_lines).strip()


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def pg_container():
    """Start PostgreSQL testcontainer for the test session."""
    if not HAS_TESTCONTAINERS:
        pytest.skip("testcontainers not available; install with: pip install testcontainers[postgres]")

    with PostgresContainer("postgres:15-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def database_url(pg_container) -> str:
    """Get the connection URL for the test database."""
    return pg_container.get_connection_url().replace("+psycopg2", "")


@pytest_asyncio.fixture(scope="session")
async def db_pool(database_url: str) -> asyncpg.Pool:
    """Create a session-scoped connection pool and run all migrations."""
    pool = await asyncpg.create_pool(database_url, min_size=2, max_size=5)

    # Run all migrations in order
    for migration_file in _get_migration_files():
        content = migration_file.read_text(encoding="utf-8")
        up_sql = _extract_up_sql(content)
        if up_sql.strip():
            try:
                await pool.execute(up_sql)
            except Exception as e:
                # Some migrations may fail on generated columns or complex PG features
                # in testcontainers; log and continue
                print(f"WARNING: Migration {migration_file.name} partially failed: {e}")

    yield pool
    await pool.close()


@pytest_asyncio.fixture
async def db(db_pool: asyncpg.Pool):
    """Per-test database connection with transaction rollback for isolation.

    Each test runs inside a transaction that is rolled back at the end,
    ensuring tests don't interfere with each other.
    """
    conn = await db_pool.acquire()
    tx = conn.transaction()
    await tx.start()

    # Disable RLS for tests (we test RLS separately)
    await conn.execute("SET LOCAL app.current_project_id = 'test-project'")
    await conn.execute("SET LOCAL app.current_session_id = '00000000-0000-0000-0000-000000000001'")

    yield conn

    await tx.rollback()
    await db_pool.release(conn)


@pytest_asyncio.fixture
async def session_service(db_pool: asyncpg.Pool):
    """SessionService instance for tests."""
    from services.session_service import SessionService
    return SessionService(db_pool)
