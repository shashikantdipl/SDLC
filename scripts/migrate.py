#!/usr/bin/env python3
"""Database migration runner for the Agentic SDLC Platform.

Usage:
    python scripts/migrate.py up              # Apply all pending migrations
    python scripts/migrate.py up 006          # Apply up to migration 006
    python scripts/migrate.py status          # Show migration status
    python scripts/migrate.py down 009        # Rollback migration 009 (requires manual uncommenting of DOWN section)

Reads DATABASE_URL from environment variable.
Default: postgresql://postgres:postgres@localhost:5432/agentic_sdlc
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

import asyncpg


MIGRATIONS_DIR = Path(__file__).parent.parent / "migrations"
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/agentic_sdlc",
)


async def get_connection() -> asyncpg.Connection:
    """Create a database connection."""
    return await asyncpg.connect(DATABASE_URL)


async def ensure_migrations_table(conn: asyncpg.Connection) -> None:
    """Create the schema_migrations tracking table if it doesn't exist."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version     VARCHAR(16) PRIMARY KEY,
            filename    VARCHAR(256) NOT NULL,
            applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)


def get_migration_files() -> list[tuple[str, Path]]:
    """Return sorted list of (version, path) tuples for all migration SQL files."""
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    result = []
    for f in files:
        match = re.match(r"^(\d+)", f.name)
        if match:
            result.append((match.group(1), f))
    return result


def extract_up_sql(content: str) -> str:
    """Extract the UP section from a migration file.

    UP section is everything after '-- UP' and before '-- DOWN'.
    If no markers, the entire content (minus commented-out DOWN lines) is UP.
    """
    lines = content.split("\n")
    up_lines = []
    in_down = False
    for line in lines:
        stripped = line.strip()
        if stripped == "-- UP":
            in_down = False
            continue
        if stripped == "-- DOWN":
            in_down = True
            continue
        if not in_down and not stripped.startswith("-- DOWN"):
            up_lines.append(line)
    return "\n".join(up_lines).strip()


def extract_down_sql(content: str) -> str:
    """Extract the DOWN section from a migration file.

    DOWN section is everything after '-- DOWN' marker to end of file.
    Commented-out SQL lines (prefixed with '-- ') within the DOWN section
    are uncommented automatically for rollback execution.
    """
    lines = content.split("\n")
    down_lines = []
    in_down = False
    for line in lines:
        stripped = line.strip()
        if stripped == "-- DOWN":
            in_down = True
            continue
        if stripped == "-- UP":
            in_down = False
            continue
        if in_down:
            # Uncomment SQL lines that were commented out for safety
            if stripped.startswith("-- ") and not stripped.startswith("-- UP") and not stripped.startswith("-- DOWN"):
                down_lines.append(line.replace("-- ", "", 1))
            else:
                down_lines.append(line)
    return "\n".join(down_lines).strip()


async def get_applied_versions(conn: asyncpg.Connection) -> set[str]:
    """Return set of already-applied migration versions."""
    rows = await conn.fetch("SELECT version FROM schema_migrations ORDER BY version")
    return {row["version"] for row in rows}


async def apply_migration(conn: asyncpg.Connection, version: str, filepath: Path) -> None:
    """Apply a single migration file."""
    content = filepath.read_text(encoding="utf-8")
    up_sql = extract_up_sql(content)

    if not up_sql.strip():
        print(f"  SKIP {version} {filepath.name} (empty UP section)")
        return

    async with conn.transaction():
        await conn.execute(up_sql)
        await conn.execute(
            "INSERT INTO schema_migrations (version, filename) VALUES ($1, $2)",
            version,
            filepath.name,
        )
    print(f"  OK   {version} {filepath.name}")


async def rollback_migration(conn: asyncpg.Connection, version: str, filepath: Path) -> None:
    """Rollback a single migration file using its DOWN section."""
    content = filepath.read_text(encoding="utf-8")
    down_sql = extract_down_sql(content)

    if not down_sql.strip():
        print(f"  FAIL {version} {filepath.name} (no DOWN section found)")
        print("       Add a '-- DOWN' section to the migration file with rollback SQL.")
        return

    async with conn.transaction():
        await conn.execute(down_sql)
        await conn.execute(
            "DELETE FROM schema_migrations WHERE version = $1",
            version,
        )
    print(f"  OK   {version} {filepath.name} (rolled back)")


async def cmd_up(target: str | None = None) -> None:
    """Apply all pending migrations (or up to target version)."""
    conn = await get_connection()
    try:
        await ensure_migrations_table(conn)
        applied = await get_applied_versions(conn)
        migrations = get_migration_files()

        pending = [
            (v, p) for v, p in migrations
            if v not in applied and (target is None or v <= target)
        ]

        if not pending:
            print("All migrations are up to date.")
            return

        print(f"Applying {len(pending)} migration(s)...")
        for version, filepath in pending:
            await apply_migration(conn, version, filepath)

        print(f"Done. {len(pending)} migration(s) applied.")
    finally:
        await conn.close()


async def cmd_down(target: str) -> None:
    """Rollback a specific migration version."""
    conn = await get_connection()
    try:
        await ensure_migrations_table(conn)
        applied = await get_applied_versions(conn)

        if target not in applied:
            print(f"Migration {target} is not currently applied. Nothing to rollback.")
            return

        migrations = get_migration_files()
        migration_map = {v: p for v, p in migrations}

        if target not in migration_map:
            print(f"Migration file for version {target} not found in {MIGRATIONS_DIR}")
            sys.exit(1)

        filepath = migration_map[target]
        print(f"Rolling back migration {target}...")
        await rollback_migration(conn, target, filepath)
        print("Done.")
    finally:
        await conn.close()


async def cmd_status() -> None:
    """Show migration status."""
    conn = await get_connection()
    try:
        await ensure_migrations_table(conn)
        applied = await get_applied_versions(conn)
        migrations = get_migration_files()

        print(f"{'Version':<10} {'File':<50} {'Status':<10}")
        print("-" * 70)
        for version, filepath in migrations:
            status = "applied" if version in applied else "PENDING"
            print(f"{version:<10} {filepath.name:<50} {status:<10}")
    finally:
        await conn.close()


async def main() -> None:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "up":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        await cmd_up(target)
    elif command == "down":
        if len(sys.argv) < 3:
            print("Usage: migrate.py down <version>")
            print("Example: migrate.py down 009")
            sys.exit(1)
        target = sys.argv[2]
        await cmd_down(target)
    elif command == "status":
        await cmd_status()
    else:
        print(f"Unknown command: {command}")
        print("Usage: migrate.py [up|down|status]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
