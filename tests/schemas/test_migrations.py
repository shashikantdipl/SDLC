"""Tests for database migration integrity.

Verifies all migration SQL files:
- Have valid UP sections
- Reference expected tables
- Follow naming convention (NNN_description.sql)
"""
from __future__ import annotations

from pathlib import Path

import pytest


MIGRATIONS_DIR = Path(__file__).parent.parent.parent / "migrations"


class TestMigrationFiles:
    """Verify migration file structure and naming."""

    def test_migrations_directory_exists(self):
        assert MIGRATIONS_DIR.exists(), f"Missing migrations directory: {MIGRATIONS_DIR}"

    def test_migration_files_sorted(self):
        files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        if not files:
            pytest.skip("No migration files found")
        # Check files are numbered sequentially
        numbers = []
        for f in files:
            parts = f.stem.split("_", 1)
            assert len(parts) >= 1, f"Migration {f.name} missing number prefix"
            numbers.append(int(parts[0]))
        # Numbers should be sequential (001, 002, ...)
        for i, num in enumerate(numbers):
            assert num == i + 1, f"Expected migration {i+1:03d}, got {num:03d}"

    def test_migration_files_have_up_section(self):
        files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        if not files:
            pytest.skip("No migration files found")
        for f in files:
            content = f.read_text(encoding="utf-8")
            # Should have CREATE TABLE or ALTER TABLE
            has_ddl = "CREATE TABLE" in content or "ALTER TABLE" in content or "CREATE INDEX" in content
            assert has_ddl, f"Migration {f.name} has no DDL statements"

    def test_migration_files_have_content(self):
        files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        if not files:
            pytest.skip("No migration files found")
        for f in files:
            content = f.read_text(encoding="utf-8").strip()
            assert len(content) > 10, f"Migration {f.name} appears empty"
