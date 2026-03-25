# TESTING — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 13 of 14 | Status: Draft
**Reads from:** ARCH (Doc 2), QUALITY (Doc 4), INTERACTION-MAP (Doc 6), MCP-TOOL-SPEC (Doc 7), DESIGN-SPEC (Doc 8), DATA-MODEL (Doc 9), API-CONTRACTS (Doc 10), BACKLOG (Doc 11)

---

## Table of Contents

1. [Test Pyramid](#1-test-pyramid)
2. [Test Frameworks](#2-test-frameworks)
3. [Database Strategy](#3-database-strategy)
4. [Test Directory Structure](#4-test-directory-structure)
5. [Shared Service Tests](#5-shared-service-tests)
6. [MCP Tool Tests](#6-mcp-tool-tests)
7. [REST API Tests](#7-rest-api-tests)
8. [Dashboard Tests](#8-dashboard-tests)
9. [Cross-Interface Tests](#9-cross-interface-tests)
10. [Agent Tests](#10-agent-tests)
11. [Performance Tests](#11-performance-tests)
12. [Coverage Thresholds](#12-coverage-thresholds)
13. [CI Pipeline](#13-ci-pipeline)
14. [Error Handling and Recovery Strategy](#14-error-handling-and-recovery-strategy)
15. [Test Data Strategy](#15-test-data-strategy)

---

## Purpose

In Full-Stack-First, three interface layers (MCP, REST, Dashboard) are designed in parallel and connected to a single Shared Service Layer. Testing must verify not only that each layer works in isolation, but that all three return consistent data shapes for the same operation. This document defines the complete test strategy, framework choices, directory layout, code patterns, and CI pipeline that enforce behavioral parity across interfaces while maintaining the coverage thresholds mandated by QUALITY (Doc 4).

---

## 1. Test Pyramid

Full-Stack-First inverts the traditional test pyramid at the top. Cross-interface tests are the most architecturally significant, but the fewest in number. Shared service tests are the foundation with the highest count.

```
┌──────────────────────────────────┐
│  Cross-Interface Tests           │  MCP trigger -> Dashboard approval (fewest)
│  ~25 tests                       │  Parity + Journey tests
├──────────────────────────────────┤
│  Interface Tests                 │  MCP protocol, REST API, Dashboard render
│  ~180 tests                      │  Per-handler unit + integration
├──────────────────────────────────┤
│  Service Tests                   │  Shared service unit + integration (most tests)
│  ~320 tests                      │  8 services x ~40 tests each
├──────────────────────────────────┤
│  Schema Tests                    │  Data shape validation, migration UP/DOWN
│  ~60 tests                       │  22 shapes + 9 migrations x 2 (up + down)
└──────────────────────────────────┘
```

### Test Count Breakdown

| Layer | Category | Est. Count | Speed | DB Required |
|-------|----------|-----------|-------|-------------|
| Schema | Data shape validation (22 shapes) | 22 | Fast | No |
| Schema | Migration UP + DOWN (9 migrations) | 18 | Medium | Yes (testcontainers) |
| Schema | Index verification | 10 | Medium | Yes |
| Schema | RLS policy verification | 10 | Medium | Yes |
| Service | Unit tests (mocked DB, 8 services) | 200 | Fast | No |
| Service | Integration tests (real DB, 8 services) | 120 | Medium | Yes |
| MCP | Handler unit tests (35 tools) | 70 | Fast | No |
| MCP | Protocol compliance (3 servers) | 15 | Fast | No |
| MCP | Auth enforcement | 10 | Fast | No |
| MCP | Integration (tool -> service -> DB) | 35 | Medium | Yes |
| REST | Route unit tests (8 route modules) | 60 | Fast | No |
| REST | Auth tests (JWT, API key, unauthorized) | 15 | Fast | No |
| REST | Integration (route -> service -> DB) | 40 | Medium | Yes |
| Dashboard | Component render tests (5 pages) | 25 | Fast | No |
| Dashboard | Accessibility (axe-core per page) | 5 | Fast | No |
| Cross-Interface | Parity tests (MCP vs REST shape) | 10 | Medium | Yes |
| Cross-Interface | Journey tests (4 journeys) | 4 | Slow | Yes |
| Cross-Interface | Data freshness (Q-052) | 5 | Medium | Yes |
| Cross-Interface | Error code parity (Q-050) | 6 | Fast | No |
| Provider | Provider portability (same agent on Anthropic + OpenAI) | 6 | Slow | No |
| Provider | Provider failover (simulate provider failure, verify fallback) | 4 | Medium | No |
| Provider | Provider unit tests (AnthropicProvider, OpenAIProvider, OllamaProvider) | 15 | Fast | No |
| Agent | Golden path (48 agents x 3) | 144 | Slow | No |
| Agent | Adversarial (48 agents x 1) | 48 | Slow | No |
| Performance | MCP latency (Q-001, Q-002) | 3 | Slow | Yes |
| Performance | REST latency (Q-004) | 3 | Slow | Yes |
| Performance | Dashboard load (Q-005, Q-006) | 5 | Slow | Yes |
| **Total** | | **~908** | | |

---

## 2. Test Frameworks

| Layer | Framework | Version | Purpose |
|-------|-----------|---------|---------|
| Schema | `jsonschema` + `pydantic v2` | 4.x / 2.x | Validate all 22 INTERACTION-MAP data shapes against canonical definitions |
| Schema | `pytest` + `testcontainers-postgres` | 8.x / 0.9.x | Run migrations forward and backward on real PostgreSQL 15 |
| Service | `pytest` + `pytest-asyncio` | 8.x / 0.23.x | Async unit tests with mocked DB pool for business logic |
| Service | `testcontainers-postgres` | 0.9.x | Real PostgreSQL for integration tests (no mocks for DB per CLAUDE Doc 3) |
| MCP | `pytest` + `mcp` (Python SDK) | 8.x / 1.x | MCP client library for protocol-level testing of tool handlers |
| MCP | MCP Inspector | latest | Protocol compliance: validate tool schemas, descriptions, error formats |
| REST | `pytest` + `httpx` | 8.x / 0.27.x | Async HTTP client for aiohttp route testing |
| REST | `aiohttp.test_utils` | 3.9.x | `TestServer` + `TestClient` for in-process route tests |
| Dashboard | `pytest` + `streamlit.testing` | 8.x / 1.x | `AppTest` framework for component render verification |
| Dashboard | `axe-core` (via `playwright`) | latest | Automated WCAG 2.1 AA accessibility checks |
| Cross-Interface | `pytest` (full stack) | 8.x | End-to-end tests spanning MCP + REST + DB + Dashboard |
| Agent | `pytest` | 8.x | Golden tests (expected output structure) + adversarial (edge cases) |
| Performance | `k6` | latest | Load testing for MCP and REST latency benchmarks |
| Performance | Lighthouse CI | latest | Dashboard page load and performance scoring |
| Coverage | `pytest-cov` + `coverage.py` | latest | Line and branch coverage reporting with fail-under thresholds |
| Mutation | `mutmut` | latest | Mutation testing for shared service layer (Q-040, nightly) |

### pytest Configuration

```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests with mocked dependencies (fast)",
    "integration: Integration tests with real DB (medium)",
    "e2e: End-to-end cross-interface tests (slow)",
    "parity: MCP vs REST data shape parity tests",
    "journey: Cross-interface journey tests",
    "golden: Agent golden-path tests",
    "adversarial: Agent adversarial tests",
    "performance: Performance benchmark tests (nightly only)",
    "slow: Tests that take > 10s",
]
addopts = [
    "--strict-markers",
    "--tb=short",
    "-q",
    "--cov-config=pyproject.toml",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning:streamlit.*",
]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 85
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

---

## 3. Database Strategy

### Testcontainers Setup

PostgreSQL 15 runs inside a Docker container managed by `testcontainers-python`. One container per test session (not per test) for speed.

```python
# tests/conftest.py
import asyncio
from typing import AsyncGenerator

import asyncpg
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async fixtures."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def pg_container():
    """Start a PostgreSQL 15 container once per test session."""
    with PostgresContainer(
        image="postgres:15-alpine",
        user="test_user",
        password="test_password",
        dbname="test_agentic_sdlc",
    ) as pg:
        yield pg


@pytest.fixture(scope="session")
async def db_pool(pg_container) -> AsyncGenerator[asyncpg.Pool, None]:
    """Create a connection pool to the test database."""
    pool = await asyncpg.create_pool(
        host=pg_container.get_container_host_ip(),
        port=pg_container.get_exposed_port(5432),
        user="test_user",
        password="test_password",
        database="test_agentic_sdlc",
        min_size=2,
        max_size=10,
    )
    # Run all migrations in order
    await _run_migrations(pool)
    yield pool
    await pool.close()


async def _run_migrations(pool: asyncpg.Pool) -> None:
    """Apply all 9 migrations in order."""
    import importlib
    migration_files = [
        "001_agent_registry",
        "002_cost_metrics",
        "003_audit_events",
        "004_pipeline_runs_and_steps",
        "005_knowledge_exceptions",
        "006_session_context",
        "007_approval_requests",
        "008_pipeline_checkpoints",
        "009_mcp_call_events_and_alter_agent_registry",
    ]
    async with pool.acquire() as conn:
        for migration in migration_files:
            module = importlib.import_module(f"src.db.migrations.{migration}")
            await conn.execute(module.UP)
```

### Transaction Isolation (Per-Test Rollback)

Each test runs inside a transaction that is rolled back after the test completes. This provides perfect isolation without the overhead of recreating the database.

```python
# tests/conftest.py (continued)

@pytest.fixture
async def clean_db(db_pool: asyncpg.Pool) -> AsyncGenerator[asyncpg.Connection, None]:
    """Provide a connection inside a transaction that rolls back after each test."""
    conn = await db_pool.acquire()
    tx = conn.transaction()
    await tx.start()
    yield conn
    await tx.rollback()
    await db_pool.release(conn)
```

### Seed Data Fixtures

```python
# tests/conftest.py (continued)

@pytest.fixture
async def seed_agents(clean_db: asyncpg.Connection) -> list[dict]:
    """Insert standard set of 48 agents into agent_registry."""
    agents = []
    phases = ["plan", "design", "build", "verify", "deploy"]
    archetypes = ["writer", "reviewer", "orchestrator", "validator"]

    for i in range(48):
        agent = {
            "agent_id": f"agent-{i:03d}",
            "name": f"Test Agent {i}",
            "phase": phases[i % len(phases)],
            "archetype": archetypes[i % len(archetypes)],
            "status": "active",
            "active_version": "1.0.0",
            "maturity_level": "supervised",
            "model": "claude-opus-4-6",
        }
        await clean_db.execute(
            """
            INSERT INTO agent_registry (agent_id, name, phase, archetype, status,
                                        active_version, maturity_level, model)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            agent["agent_id"], agent["name"], agent["phase"], agent["archetype"],
            agent["status"], agent["active_version"], agent["maturity_level"],
            agent["model"],
        )
        agents.append(agent)
    return agents


@pytest.fixture
async def seed_pipelines(clean_db: asyncpg.Connection) -> list[dict]:
    """Insert sample pipeline runs in various states."""
    import uuid
    from datetime import datetime, timezone

    runs = []
    statuses = ["pending", "running", "paused", "completed", "failed", "cancelled"]
    for i, status in enumerate(statuses):
        run = {
            "run_id": str(uuid.uuid4()),
            "project_id": f"proj-{i:03d}",
            "pipeline_name": "full-stack-first-14-doc",
            "status": status,
            "current_step": min(i * 2, 13),
            "total_steps": 14,
            "current_step_name": f"{i * 2:02d}-DOC",
            "started_at": datetime.now(timezone.utc),
            "cost_usd": round(i * 3.50, 2),
            "triggered_by": "test-user",
        }
        await clean_db.execute(
            """
            INSERT INTO pipeline_runs (run_id, project_id, pipeline_name, status,
                                       current_step, total_steps, current_step_name,
                                       started_at, cost_usd, triggered_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            run["run_id"], run["project_id"], run["pipeline_name"], run["status"],
            run["current_step"], run["total_steps"], run["current_step_name"],
            run["started_at"], run["cost_usd"], run["triggered_by"],
        )
        runs.append(run)
    return runs


@pytest.fixture
async def seed_audit_events(clean_db: asyncpg.Connection) -> list[dict]:
    """Insert sample audit events across severities."""
    import uuid
    from datetime import datetime, timezone

    events = []
    severities = ["info", "warning", "error", "critical"]
    actions = ["pipeline.trigger", "agent.invoke", "approval.approve", "cost.alert"]

    for i in range(20):
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "agent_id": f"agent-{i % 48:03d}",
            "session_id": str(uuid.uuid4()),
            "project_id": f"proj-{i % 6:03d}",
            "action": actions[i % len(actions)],
            "severity": severities[i % len(severities)],
            "details": "{}",
            "cost_usd": round(0.05 * i, 2),
            "tokens_in": 100 * (i + 1),
            "tokens_out": 200 * (i + 1),
            "duration_ms": 50 * (i + 1),
            "pii_detected": i % 7 == 0,
        }
        await clean_db.execute(
            """
            INSERT INTO audit_events (event_id, timestamp, agent_id, session_id,
                                      project_id, action, severity, details, cost_usd,
                                      tokens_in, tokens_out, duration_ms, pii_detected)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, $11, $12, $13)
            """,
            event["event_id"], event["timestamp"], event["agent_id"],
            event["session_id"], event["project_id"], event["action"],
            event["severity"], event["details"], event["cost_usd"],
            event["tokens_in"], event["tokens_out"], event["duration_ms"],
            event["pii_detected"],
        )
        events.append(event)
    return events


@pytest.fixture
async def seed_approval_requests(clean_db: asyncpg.Connection) -> list[dict]:
    """Insert sample approval requests in various states."""
    import uuid
    from datetime import datetime, timedelta, timezone

    requests = []
    statuses = ["pending", "approved", "rejected", "expired", "escalated"]
    for i, status in enumerate(statuses):
        now = datetime.now(timezone.utc)
        req = {
            "approval_id": str(uuid.uuid4()),
            "session_id": str(uuid.uuid4()),
            "run_id": str(uuid.uuid4()),
            "pipeline_name": "full-stack-first-14-doc",
            "step_number": 6,
            "step_name": "06-INTERACTION-MAP",
            "summary": f"Approval needed for step 6 (test {i})",
            "risk_level": "medium",
            "status": status,
            "requested_at": now,
            "expires_at": now + timedelta(hours=24),
            "context": "{}",
        }
        await clean_db.execute(
            """
            INSERT INTO approval_requests (approval_id, session_id, run_id,
                                           pipeline_name, step_number, step_name,
                                           summary, risk_level, status, requested_at,
                                           expires_at, context)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12::jsonb)
            """,
            req["approval_id"], req["session_id"], req["run_id"],
            req["pipeline_name"], req["step_number"], req["step_name"],
            req["summary"], req["risk_level"], req["status"], req["requested_at"],
            req["expires_at"], req["context"],
        )
        requests.append(req)
    return requests
```

---

## 4. Test Directory Structure

```
tests/
├── conftest.py                    # shared fixtures (db, services, clients)
├── factories.py                   # factory functions for test data
├── schemas/
│   ├── test_data_shapes.py        # validate all 22 INTERACTION-MAP shapes
│   ├── test_migrations.py         # UP + DOWN for all 9 migrations
│   ├── test_indexes.py            # verify indexes exist and are used
│   └── test_rls_policies.py       # verify RLS prevents cross-project access
├── services/
│   ├── test_pipeline_service.py   # unit + integration (~50 tests)
│   ├── test_agent_service.py      # unit + integration (~50 tests)
│   ├── test_cost_service.py       # unit + integration (~40 tests)
│   ├── test_audit_service.py      # unit + integration (~35 tests)
│   ├── test_approval_service.py   # unit + integration (~35 tests)
│   ├── test_knowledge_service.py  # unit + integration (~30 tests)
│   ├── test_session_service.py    # unit + integration (~20 tests)
│   └── test_health_service.py     # unit + integration (~20 tests)
├── mcp/
│   ├── test_agents_server.py      # all 18 tools on agents server
│   ├── test_governance_server.py  # all 10 tools on governance server
│   ├── test_knowledge_server.py   # all 4 tools on knowledge server
│   ├── test_system_tools.py       # 3 system tools (I-080, I-081, I-082)
│   ├── test_mcp_auth.py           # auth enforcement (Q-019)
│   └── test_mcp_protocol.py       # schema validation via MCP Inspector
├── api/
│   ├── test_pipeline_routes.py    # POST/GET /api/v1/pipelines/*
│   ├── test_agent_routes.py       # GET/POST /api/v1/agents/*
│   ├── test_cost_routes.py        # GET/PUT /api/v1/cost/*
│   ├── test_audit_routes.py       # GET/POST /api/v1/audit/*
│   ├── test_approval_routes.py    # GET/POST /api/v1/approvals/*
│   ├── test_knowledge_routes.py   # GET/POST /api/v1/knowledge/*
│   ├── test_system_routes.py      # GET /health, /api/v1/system/*
│   └── test_auth_routes.py        # POST /auth/login, JWT/API key validation
├── dashboard/
│   ├── test_fleet_health.py       # Fleet Health page render + widgets
│   ├── test_cost_monitor.py       # Cost Monitor page render + widgets
│   ├── test_pipeline_runs.py      # Pipeline Runs page render + widgets
│   ├── test_audit_log.py          # Audit Log page render + widgets
│   ├── test_approval_queue.py     # Approval Queue page render + widgets
│   └── test_accessibility.py      # axe-core WCAG 2.1 AA checks for all pages
├── integration/
│   ├── test_parity.py             # MCP vs REST return same data (Q-049, Q-051)
│   ├── test_error_parity.py       # MCP vs REST same error codes (Q-050)
│   ├── test_schema_version.py     # MCP vs REST schema version parity (Q-053)
│   ├── test_data_freshness.py     # Dashboard staleness < 5s (Q-052)
│   ├── test_pipeline_approval.py  # Journey 1: MCP trigger -> dashboard approve
│   ├── test_cost_investigation.py # Journey 2: alert -> dashboard investigate
│   ├── test_canary_deploy.py      # Journey 3: MCP promote -> dashboard monitor
│   └── test_compliance_audit.py   # Journey 4: dashboard audit -> export
├── agents/
│   ├── manifest.json              # required test counts per agent (meta)
│   ├── test_agent_coverage.py     # meta-test: asserts manifest coverage (Q-039)
│   ├── test_g1_cost_tracker.py    # 3 golden + 1 adversarial
│   ├── test_g2_prd_writer.py      # 3 golden + 1 adversarial
│   ├── test_g3_arch_writer.py     # 3 golden + 1 adversarial
│   └── ...                        # one file per agent (48 files)
└── performance/
    ├── test_mcp_latency.py        # Q-001 (read < 500ms), Q-002 (write < 2s)
    ├── test_api_latency.py        # Q-004 (GET < 500ms, POST < 1s)
    ├── test_dashboard_load.py     # Q-005 (< 2s), Q-006 (Fleet Health < 1s)
    ├── k6/
    │   ├── mcp_read_load.js       # k6 script: 200 requests per MCP read tool
    │   ├── mcp_write_load.js      # k6 script: 100 requests per MCP write tool
    │   └── rest_load.js           # k6 script: 50 concurrent users for 60s
    └── lighthouse/
        └── config.js              # Lighthouse CI configuration
```

---

## 5. Shared Service Tests

The shared service layer is the most important test target. All three interfaces delegate to these 8 services. Coverage requirement: 90% line, 85% branch (Q-034).

### 5.1 Unit Test Pattern (Mocked DB)

Unit tests mock the database connection pool to test business logic in isolation. They run fast (no I/O) and cover edge cases, validation, and error paths.

```python
# tests/services/test_pipeline_service.py
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.pipeline_service import PipelineService
from src.models.pipeline import PipelineRun, PipelineStatus


class TestPipelineServiceUnit:
    """Unit tests for PipelineService with mocked DB pool."""

    @pytest.fixture
    def mock_pool(self):
        """Create a mock asyncpg pool."""
        pool = AsyncMock()
        conn = AsyncMock()
        pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
        pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
        return pool, conn

    @pytest.fixture
    def service(self, mock_pool):
        pool, _ = mock_pool
        return PipelineService(db_pool=pool)

    # --- trigger() ---

    @pytest.mark.unit
    async def test_trigger_creates_run_with_pending_status(self, service, mock_pool):
        """trigger() should create a new pipeline run with status 'pending'."""
        _, mock_conn = mock_pool
        mock_conn.fetchrow.return_value = {
            "run_id": str(uuid.uuid4()),
            "project_id": "proj-001",
            "pipeline_name": "full-stack-first-14-doc",
            "status": "pending",
            "current_step": 0,
            "total_steps": 14,
            "current_step_name": "00-ROADMAP",
            "started_at": datetime.now(timezone.utc),
            "completed_at": None,
            "cost_usd": 0.0,
            "triggered_by": "priya",
            "error_message": None,
            "checkpoint_step": None,
        }

        result = await service.trigger(
            project_id="proj-001",
            pipeline_name="full-stack-first-14-doc",
            brief="Generate docs for Project Alpha",
            triggered_by="priya",
        )

        assert isinstance(result, PipelineRun)
        assert result.status == PipelineStatus.PENDING
        assert result.total_steps == 14
        assert result.cost_usd == 0.0
        mock_conn.fetchrow.assert_called_once()

    @pytest.mark.unit
    async def test_trigger_rejects_empty_brief(self, service):
        """trigger() should raise ValueError if brief is empty."""
        with pytest.raises(ValueError, match="brief cannot be empty"):
            await service.trigger(
                project_id="proj-001",
                pipeline_name="full-stack-first-14-doc",
                brief="",
                triggered_by="priya",
            )

    @pytest.mark.unit
    async def test_trigger_rejects_invalid_pipeline_name(self, service):
        """trigger() should raise ValueError for unknown pipeline names."""
        with pytest.raises(ValueError, match="Unknown pipeline"):
            await service.trigger(
                project_id="proj-001",
                pipeline_name="nonexistent-pipeline",
                brief="Generate docs",
                triggered_by="priya",
            )

    @pytest.mark.unit
    async def test_trigger_assigns_uuid_run_id(self, service, mock_pool):
        """trigger() should assign a valid UUID v4 as run_id."""
        _, mock_conn = mock_pool
        mock_conn.fetchrow.return_value = {
            "run_id": "550e8400-e29b-41d4-a716-446655440000",
            "project_id": "proj-001",
            "pipeline_name": "full-stack-first-14-doc",
            "status": "pending",
            "current_step": 0,
            "total_steps": 14,
            "current_step_name": "00-ROADMAP",
            "started_at": datetime.now(timezone.utc),
            "completed_at": None,
            "cost_usd": 0.0,
            "triggered_by": "priya",
            "error_message": None,
            "checkpoint_step": None,
        }

        result = await service.trigger(
            project_id="proj-001",
            pipeline_name="full-stack-first-14-doc",
            brief="test",
            triggered_by="priya",
        )

        # Verify the run_id is a valid UUID
        parsed = uuid.UUID(result.run_id)
        assert parsed.version == 4

    # --- get_status() ---

    @pytest.mark.unit
    async def test_get_status_returns_run(self, service, mock_pool):
        """get_status() should return the pipeline run for a valid run_id."""
        _, mock_conn = mock_pool
        run_id = str(uuid.uuid4())
        mock_conn.fetchrow.return_value = {
            "run_id": run_id,
            "project_id": "proj-001",
            "pipeline_name": "full-stack-first-14-doc",
            "status": "running",
            "current_step": 5,
            "total_steps": 14,
            "current_step_name": "05-FEATURE-CATALOG",
            "started_at": datetime.now(timezone.utc),
            "completed_at": None,
            "cost_usd": 8.50,
            "triggered_by": "priya",
            "error_message": None,
            "checkpoint_step": 4,
        }

        result = await service.get_status(run_id=run_id)

        assert result.run_id == run_id
        assert result.status == PipelineStatus.RUNNING
        assert result.current_step == 5

    @pytest.mark.unit
    async def test_get_status_raises_not_found(self, service, mock_pool):
        """get_status() should raise NotFoundError for nonexistent run_id."""
        _, mock_conn = mock_pool
        mock_conn.fetchrow.return_value = None

        with pytest.raises(Exception, match="not found"):
            await service.get_status(run_id=str(uuid.uuid4()))

    # --- resume() ---

    @pytest.mark.unit
    async def test_resume_only_paused_runs(self, service, mock_pool):
        """resume() should reject runs that are not in 'paused' or 'failed' status."""
        _, mock_conn = mock_pool
        mock_conn.fetchrow.return_value = {
            "run_id": str(uuid.uuid4()),
            "status": "running",
        }

        with pytest.raises(Exception, match="Cannot resume"):
            await service.resume(run_id=str(uuid.uuid4()))

    # --- cancel() ---

    @pytest.mark.unit
    async def test_cancel_sets_cancelled_status(self, service, mock_pool):
        """cancel() should transition status to 'cancelled'."""
        _, mock_conn = mock_pool
        run_id = str(uuid.uuid4())
        mock_conn.fetchrow.return_value = {
            "run_id": run_id,
            "project_id": "proj-001",
            "pipeline_name": "full-stack-first-14-doc",
            "status": "cancelled",
            "current_step": 3,
            "total_steps": 14,
            "current_step_name": "03-CLAUDE",
            "started_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc),
            "cost_usd": 5.25,
            "triggered_by": "priya",
            "error_message": None,
            "checkpoint_step": 2,
        }

        result = await service.cancel(run_id=run_id)
        assert result.status == PipelineStatus.CANCELLED
```

### 5.2 Integration Test Pattern (Real DB)

Integration tests use a real PostgreSQL container. They verify SQL queries, transaction behavior, and data persistence.

```python
# tests/services/test_pipeline_service.py (continued)


class TestPipelineServiceIntegration:
    """Integration tests for PipelineService with real PostgreSQL."""

    @pytest.fixture
    def service(self, db_pool):
        return PipelineService(db_pool=db_pool)

    @pytest.mark.integration
    async def test_trigger_persists_to_db(self, service, clean_db):
        """trigger() should persist the pipeline run to pipeline_runs table."""
        result = await service.trigger(
            project_id="proj-integ-001",
            pipeline_name="full-stack-first-14-doc",
            brief="Integration test pipeline",
            triggered_by="test-user",
        )

        # Verify it is in the database
        row = await clean_db.fetchrow(
            "SELECT * FROM pipeline_runs WHERE run_id = $1",
            result.run_id,
        )
        assert row is not None
        assert row["status"] == "pending"
        assert row["total_steps"] == 14
        assert row["cost_usd"] == 0.0

    @pytest.mark.integration
    async def test_trigger_creates_pipeline_steps(self, service, clean_db):
        """trigger() should create 14 pipeline_steps rows for the run."""
        result = await service.trigger(
            project_id="proj-integ-002",
            pipeline_name="full-stack-first-14-doc",
            brief="Integration test steps",
            triggered_by="test-user",
        )

        steps = await clean_db.fetch(
            "SELECT * FROM pipeline_steps WHERE run_id = $1 ORDER BY step_number",
            result.run_id,
        )
        assert len(steps) == 14
        assert steps[0]["step_name"] == "00-ROADMAP"
        assert steps[5]["step_name"] == "05-FEATURE-CATALOG"
        assert steps[13]["step_name"] == "13-TESTING"

    @pytest.mark.integration
    async def test_get_status_with_step_join(self, service, clean_db, seed_pipelines):
        """get_status() should join current_step_name from pipeline_steps."""
        running_run = next(r for r in seed_pipelines if r["status"] == "running")
        result = await service.get_status(run_id=running_run["run_id"])

        assert result.current_step_name is not None
        assert result.status == PipelineStatus.RUNNING

    @pytest.mark.integration
    async def test_list_runs_with_status_filter(self, service, clean_db, seed_pipelines):
        """list_runs() should filter by status when provided."""
        result = await service.list_runs(status="completed")

        assert all(r.status == PipelineStatus.COMPLETED for r in result)

    @pytest.mark.integration
    async def test_cancel_updates_completed_at(self, service, clean_db, seed_pipelines):
        """cancel() should set completed_at timestamp."""
        running_run = next(r for r in seed_pipelines if r["status"] == "running")
        result = await service.cancel(run_id=running_run["run_id"])

        assert result.completed_at is not None
        assert result.status == PipelineStatus.CANCELLED
```

### 5.3 Error Case Testing Pattern

Every service method has explicit error tests covering database failures, constraint violations, and invalid state transitions.

```python
# tests/services/test_pipeline_service.py (continued)


class TestPipelineServiceErrors:
    """Error case tests for PipelineService."""

    @pytest.mark.unit
    async def test_trigger_handles_db_connection_error(self, mock_pool):
        """trigger() should raise ServiceUnavailableError on DB connection failure."""
        pool, mock_conn = mock_pool
        mock_conn.fetchrow.side_effect = ConnectionError("DB unavailable")
        service = PipelineService(db_pool=pool)

        with pytest.raises(Exception, match="unavailable"):
            await service.trigger(
                project_id="proj-001",
                pipeline_name="full-stack-first-14-doc",
                brief="test",
                triggered_by="priya",
            )

    @pytest.mark.unit
    async def test_trigger_handles_duplicate_run(self, mock_pool):
        """trigger() should handle unique constraint violation gracefully."""
        pool, mock_conn = mock_pool
        mock_conn.fetchrow.side_effect = asyncpg.UniqueViolationError(
            "duplicate key value"
        )
        service = PipelineService(db_pool=pool)

        with pytest.raises(Exception, match="duplicate"):
            await service.trigger(
                project_id="proj-001",
                pipeline_name="full-stack-first-14-doc",
                brief="test",
                triggered_by="priya",
            )

    @pytest.mark.unit
    async def test_resume_non_resumable_state(self, mock_pool):
        """resume() should raise InvalidStateError for completed runs."""
        pool, mock_conn = mock_pool
        mock_conn.fetchrow.return_value = {
            "run_id": str(uuid.uuid4()),
            "status": "completed",
        }
        service = PipelineService(db_pool=pool)

        with pytest.raises(Exception, match="Cannot resume"):
            await service.resume(run_id=str(uuid.uuid4()))
```

### 5.4 All 8 Services Test Summary

| Service | Interactions Covered | Unit Tests | Integration Tests | Key Behaviors |
|---------|---------------------|------------|-------------------|---------------|
| `PipelineService` | I-001 to I-009 | ~30 | ~20 | trigger, status, list, resume, cancel, get_documents, retry_step, get_config, validate_input |
| `AgentService` | I-020 to I-027 | ~28 | ~22 | list, get, invoke, health_check, promote, rollback, set_canary, get_maturity |
| `CostService` | I-040, I-041, I-048, I-049 | ~25 | ~15 | get_report (aggregation), check_budget (threshold logic), get_anomalies (detection), set_threshold |
| `AuditService` | I-042, I-043, I-044, I-082 | ~22 | ~13 | query_events (filters), get_summary (aggregation), export_report (file generation), list_mcp_calls |
| `ApprovalService` | I-045, I-046, I-047 | ~20 | ~15 | list_pending, approve (pipeline resume), reject (mandatory comment), expiration, escalation |
| `KnowledgeService` | I-060 to I-063 | ~18 | ~12 | search, create, promote (tier escalation), list_by_tier |
| `SessionService` | Internal | ~12 | ~8 | create, get, update, cleanup (24h TTL) |
| `HealthService` | I-080, I-081 | ~12 | ~8 | get_fleet_health (cross-table aggregation), get_mcp_status (in-memory) |

---

## 6. MCP Tool Tests

### 6.1 Handler Unit Tests (Mocked Service)

Each MCP tool handler is tested with a mocked shared service. The test verifies input validation, response format, and error handling.

```python
# tests/mcp/test_agents_server.py
import pytest
from unittest.mock import AsyncMock, patch

from src.mcp.servers.agents.handlers import trigger_pipeline_handler
from src.models.pipeline import PipelineRun, PipelineStatus


class TestTriggerPipelineTool:
    """Tests for the trigger_pipeline MCP tool handler."""

    @pytest.fixture
    def mock_service(self):
        service = AsyncMock()
        service.trigger.return_value = PipelineRun(
            run_id="550e8400-e29b-41d4-a716-446655440000",
            project_id="proj-001",
            pipeline_name="full-stack-first-14-doc",
            status=PipelineStatus.PENDING,
            current_step=0,
            total_steps=14,
            current_step_name="00-ROADMAP",
            started_at="2026-03-24T10:00:00Z",
            completed_at=None,
            cost_usd=0.0,
            triggered_by="priya",
            error_message=None,
            checkpoint_step=None,
        )
        return service

    @pytest.mark.unit
    async def test_trigger_returns_pipeline_run_shape(self, mock_service):
        """Handler should return a dict matching PipelineRun data shape."""
        result = await trigger_pipeline_handler(
            arguments={
                "project_id": "proj-001",
                "pipeline_name": "full-stack-first-14-doc",
                "brief": "Generate docs for Project Alpha",
            },
            service=mock_service,
        )

        assert "run_id" in result
        assert "status" in result
        assert result["status"] == "pending"
        assert result["total_steps"] == 14

    @pytest.mark.unit
    async def test_trigger_validates_required_fields(self, mock_service):
        """Handler should reject requests missing required fields."""
        with pytest.raises(Exception, match="required"):
            await trigger_pipeline_handler(
                arguments={"project_id": "proj-001"},  # missing pipeline_name, brief
                service=mock_service,
            )

    @pytest.mark.unit
    async def test_trigger_validates_project_id_format(self, mock_service):
        """Handler should reject invalid project_id format."""
        with pytest.raises(Exception, match="project_id"):
            await trigger_pipeline_handler(
                arguments={
                    "project_id": "",  # empty
                    "pipeline_name": "full-stack-first-14-doc",
                    "brief": "test",
                },
                service=mock_service,
            )

    @pytest.mark.unit
    async def test_trigger_delegates_to_service(self, mock_service):
        """Handler should call PipelineService.trigger() with correct args."""
        await trigger_pipeline_handler(
            arguments={
                "project_id": "proj-001",
                "pipeline_name": "full-stack-first-14-doc",
                "brief": "test brief",
            },
            service=mock_service,
        )

        mock_service.trigger.assert_called_once_with(
            project_id="proj-001",
            pipeline_name="full-stack-first-14-doc",
            brief="test brief",
            triggered_by=pytest.ANY,  # extracted from MCP auth context
        )

    @pytest.mark.unit
    async def test_trigger_wraps_service_error_as_mcp_error(self, mock_service):
        """Handler should convert service exceptions to MCP error responses."""
        mock_service.trigger.side_effect = ValueError("Invalid pipeline name")

        with pytest.raises(Exception) as exc_info:
            await trigger_pipeline_handler(
                arguments={
                    "project_id": "proj-001",
                    "pipeline_name": "bad-pipeline",
                    "brief": "test",
                },
                service=mock_service,
            )

        # Verify the error is formatted as an MCP-compliant error
        assert "Invalid pipeline name" in str(exc_info.value)
```

### 6.2 Protocol Compliance (MCP Inspector)

MCP Inspector validates that all tool schemas are correctly defined and that server responses follow the MCP protocol specification.

```python
# tests/mcp/test_mcp_protocol.py
import subprocess
import json

import pytest


class TestMcpProtocolCompliance:
    """Verify MCP servers conform to protocol spec using MCP Inspector."""

    SERVERS = [
        ("agentic-sdlc-agents", 3100, 18),
        ("agentic-sdlc-governance", 3101, 10),
        ("agentic-sdlc-knowledge", 3102, 4),
    ]

    @pytest.mark.parametrize("server_name,port,expected_tools", SERVERS)
    @pytest.mark.integration
    async def test_server_lists_correct_tool_count(
        self, server_name, port, expected_tools
    ):
        """Each MCP server should list the expected number of tools."""
        # Use MCP client to send tools/list request
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="python",
            args=["-m", f"src.mcp.servers.{server_name.replace('-', '_')}"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert len(tools.tools) == expected_tools

    @pytest.mark.parametrize("server_name,port,expected_tools", SERVERS)
    @pytest.mark.integration
    async def test_all_tools_have_valid_json_schema(
        self, server_name, port, expected_tools
    ):
        """Every tool should have a valid JSON Schema for inputSchema."""
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        import jsonschema

        server_params = StdioServerParameters(
            command="python",
            args=["-m", f"src.mcp.servers.{server_name.replace('-', '_')}"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()

                for tool in tools.tools:
                    # Validate the tool's inputSchema is valid JSON Schema
                    assert tool.name, "Tool must have a name"
                    assert tool.description, f"Tool {tool.name} must have description"
                    assert tool.inputSchema, f"Tool {tool.name} must have inputSchema"
                    # This will raise if the schema itself is invalid
                    jsonschema.Draft7Validator.check_schema(tool.inputSchema)

    @pytest.mark.integration
    async def test_server_startup_within_5s(self):
        """MCP servers should reach ready state within 5s (Q-003)."""
        import time
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        for server_name, _, _ in self.SERVERS:
            server_params = StdioServerParameters(
                command="python",
                args=["-m", f"src.mcp.servers.{server_name.replace('-', '_')}"],
            )

            start = time.monotonic()
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    elapsed = time.monotonic() - start
                    assert elapsed < 5.0, (
                        f"{server_name} took {elapsed:.1f}s to start (max 5s)"
                    )
```

### 6.3 Auth Enforcement Tests

```python
# tests/mcp/test_mcp_auth.py
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class TestMcpAuth:
    """Verify MCP authentication enforcement (Q-019)."""

    @pytest.mark.integration
    async def test_unauthenticated_request_rejected(self):
        """Requests without API key should receive error code -32001."""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "src.mcp.servers.agentic_sdlc_agents"],
            env={},  # No ANTHROPIC_API_KEY
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                with pytest.raises(Exception) as exc_info:
                    await session.call_tool("list_agents", arguments={})
                assert "-32001" in str(exc_info.value) or "Unauthorized" in str(
                    exc_info.value
                )

    @pytest.mark.integration
    async def test_invalid_api_key_rejected(self):
        """Requests with invalid API key should receive error code -32001."""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "src.mcp.servers.agentic_sdlc_agents"],
            env={"ANTHROPIC_API_KEY": "invalid-key-value"},
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                with pytest.raises(Exception) as exc_info:
                    await session.call_tool("list_agents", arguments={})
                assert "-32001" in str(exc_info.value) or "Unauthorized" in str(
                    exc_info.value
                )

    @pytest.mark.integration
    async def test_project_isolation(self):
        """Client for project P1 must not access project P2 data (Q-021)."""
        # Authenticate as project P1
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "src.mcp.servers.agentic_sdlc_agents"],
            env={"ANTHROPIC_API_KEY": "valid-key-project-1"},
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Attempt to access project P2 data
                with pytest.raises(Exception, match="permission|denied|forbidden"):
                    await session.call_tool(
                        "get_pipeline_status",
                        arguments={"run_id": "run-belonging-to-project-2"},
                    )
```

### 6.4 MCP Integration Test (Full Stack)

```python
# tests/mcp/test_agents_server.py (continued)


class TestTriggerPipelineIntegration:
    """Integration tests: MCP client -> tool handler -> service -> DB."""

    @pytest.mark.integration
    async def test_trigger_pipeline_full_stack(self, db_pool):
        """Full MCP client call should persist a pipeline run to DB."""
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command="python",
            args=["-m", "src.mcp.servers.agentic_sdlc_agents"],
            env={"ANTHROPIC_API_KEY": "test-valid-key", "DATABASE_URL": "..."},
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "trigger_pipeline",
                    arguments={
                        "project_id": "proj-mcp-integ",
                        "pipeline_name": "full-stack-first-14-doc",
                        "brief": "MCP integration test",
                    },
                )

                # Parse the MCP response content
                content = result.content[0].text
                import json
                data = json.loads(content)

                assert "run_id" in data
                assert data["status"] == "pending"
                assert data["total_steps"] == 14

                # Verify it actually persisted to DB
                async with db_pool.acquire() as conn:
                    row = await conn.fetchrow(
                        "SELECT * FROM pipeline_runs WHERE run_id = $1",
                        data["run_id"],
                    )
                    assert row is not None
                    assert row["project_id"] == "proj-mcp-integ"
```

---

## 7. REST API Tests

### 7.1 Route Unit Tests (Mocked Service)

```python
# tests/api/test_pipeline_routes.py
import json
import uuid

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, TestClient
from unittest.mock import AsyncMock

from src.api.routes.pipeline_routes import create_pipeline_routes
from src.models.pipeline import PipelineRun, PipelineStatus


class TestPipelineRoutesUnit:
    """Unit tests for pipeline REST routes with mocked service."""

    @pytest.fixture
    def mock_service(self):
        service = AsyncMock()
        return service

    @pytest.fixture
    async def client(self, mock_service, aiohttp_client):
        """Create a test client with mocked pipeline service."""
        app = web.Application()
        app["pipeline_service"] = mock_service
        create_pipeline_routes(app)
        return await aiohttp_client(app)

    @pytest.mark.unit
    async def test_post_pipelines_returns_201(self, client, mock_service):
        """POST /api/v1/pipelines should return 201 with PipelineRun envelope."""
        mock_service.trigger.return_value = PipelineRun(
            run_id=str(uuid.uuid4()),
            project_id="proj-001",
            pipeline_name="full-stack-first-14-doc",
            status=PipelineStatus.PENDING,
            current_step=0,
            total_steps=14,
            current_step_name="00-ROADMAP",
            started_at="2026-03-24T10:00:00Z",
            completed_at=None,
            cost_usd=0.0,
            triggered_by="test-user",
            error_message=None,
            checkpoint_step=None,
        )

        resp = await client.post(
            "/api/v1/pipelines",
            json={
                "project_id": "proj-001",
                "pipeline_name": "full-stack-first-14-doc",
                "brief": "Test pipeline",
            },
        )

        assert resp.status == 201
        body = await resp.json()
        assert body["ok"] is True
        assert "data" in body
        assert body["data"]["status"] == "pending"
        assert body["data"]["total_steps"] == 14

    @pytest.mark.unit
    async def test_post_pipelines_returns_envelope_format(self, client, mock_service):
        """Response should follow { ok, data, error, meta } envelope."""
        mock_service.trigger.return_value = PipelineRun(
            run_id=str(uuid.uuid4()),
            project_id="proj-001",
            pipeline_name="full-stack-first-14-doc",
            status=PipelineStatus.PENDING,
            current_step=0,
            total_steps=14,
            current_step_name="00-ROADMAP",
            started_at="2026-03-24T10:00:00Z",
            completed_at=None,
            cost_usd=0.0,
            triggered_by="test-user",
            error_message=None,
            checkpoint_step=None,
        )

        resp = await client.post(
            "/api/v1/pipelines",
            json={
                "project_id": "proj-001",
                "pipeline_name": "full-stack-first-14-doc",
                "brief": "Test",
            },
        )

        body = await resp.json()
        assert set(body.keys()) == {"ok", "data", "error", "meta"}
        assert body["error"] is None

    @pytest.mark.unit
    async def test_post_pipelines_400_missing_body(self, client, mock_service):
        """POST /api/v1/pipelines without body should return 400."""
        resp = await client.post("/api/v1/pipelines")
        assert resp.status == 400

    @pytest.mark.unit
    async def test_post_pipelines_400_invalid_json(self, client, mock_service):
        """POST /api/v1/pipelines with invalid JSON should return 400."""
        resp = await client.post(
            "/api/v1/pipelines",
            data=b"not json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status == 400

    @pytest.mark.unit
    async def test_get_pipeline_status(self, client, mock_service):
        """GET /api/v1/pipelines/{run_id} should return pipeline run."""
        run_id = str(uuid.uuid4())
        mock_service.get_status.return_value = PipelineRun(
            run_id=run_id,
            project_id="proj-001",
            pipeline_name="full-stack-first-14-doc",
            status=PipelineStatus.RUNNING,
            current_step=5,
            total_steps=14,
            current_step_name="05-FEATURE-CATALOG",
            started_at="2026-03-24T10:00:00Z",
            completed_at=None,
            cost_usd=8.50,
            triggered_by="test-user",
            error_message=None,
            checkpoint_step=4,
        )

        resp = await client.get(f"/api/v1/pipelines/{run_id}")
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["run_id"] == run_id
        assert body["data"]["status"] == "running"

    @pytest.mark.unit
    async def test_get_pipeline_404_not_found(self, client, mock_service):
        """GET /api/v1/pipelines/{run_id} for missing run should return 404."""
        from src.services.exceptions import NotFoundError
        mock_service.get_status.side_effect = NotFoundError("Pipeline not found")

        resp = await client.get(f"/api/v1/pipelines/{uuid.uuid4()}")
        assert resp.status == 404
        body = await resp.json()
        assert body["ok"] is False
        assert "not found" in body["error"]["message"].lower()

    @pytest.mark.unit
    async def test_post_cancel_pipeline(self, client, mock_service):
        """POST /api/v1/pipelines/{run_id}/cancel should return cancelled run."""
        run_id = str(uuid.uuid4())
        mock_service.cancel.return_value = PipelineRun(
            run_id=run_id,
            project_id="proj-001",
            pipeline_name="full-stack-first-14-doc",
            status=PipelineStatus.CANCELLED,
            current_step=3,
            total_steps=14,
            current_step_name="03-CLAUDE",
            started_at="2026-03-24T10:00:00Z",
            completed_at="2026-03-24T10:05:00Z",
            cost_usd=5.25,
            triggered_by="test-user",
            error_message=None,
            checkpoint_step=2,
        )

        resp = await client.post(f"/api/v1/pipelines/{run_id}/cancel")
        assert resp.status == 200
        body = await resp.json()
        assert body["data"]["status"] == "cancelled"
```

### 7.2 Auth Tests

```python
# tests/api/test_auth_routes.py
import pytest
from aiohttp import web


class TestAuthEnforcement:
    """Verify REST API authentication enforcement (Q-022)."""

    @pytest.mark.unit
    async def test_health_endpoint_no_auth(self, client):
        """GET /health should be accessible without authentication."""
        resp = await client.get("/health")
        assert resp.status == 200

    @pytest.mark.unit
    async def test_all_routes_require_auth(self, client, registered_routes):
        """Every route except /health and /auth/login should require auth."""
        exempt = {"/health", "/auth/login"}

        for route in registered_routes:
            if route.path in exempt:
                continue

            resp = await client.request(
                route.method,
                route.path,
                headers={},  # No auth header
            )
            assert resp.status == 401, (
                f"{route.method} {route.path} should return 401 without auth, "
                f"got {resp.status}"
            )

    @pytest.mark.unit
    async def test_valid_jwt_accepted(self, client, valid_jwt_token):
        """Request with valid JWT should be accepted."""
        resp = await client.get(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )
        assert resp.status == 200

    @pytest.mark.unit
    async def test_valid_api_key_accepted(self, client, valid_api_key):
        """Request with valid API key should be accepted."""
        resp = await client.get(
            "/api/v1/agents",
            headers={"X-API-Key": valid_api_key},
        )
        assert resp.status == 200

    @pytest.mark.unit
    async def test_expired_jwt_rejected(self, client, expired_jwt_token):
        """Request with expired JWT should return 401."""
        resp = await client.get(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {expired_jwt_token}"},
        )
        assert resp.status == 401

    @pytest.mark.unit
    async def test_malformed_jwt_rejected(self, client):
        """Request with malformed JWT should return 401."""
        resp = await client.get(
            "/api/v1/agents",
            headers={"Authorization": "Bearer not-a-real-jwt"},
        )
        assert resp.status == 401
```

### 7.3 REST Integration Test

```python
# tests/api/test_pipeline_routes.py (continued)


class TestPipelineRoutesIntegration:
    """Integration tests: HTTP client -> route -> service -> DB."""

    @pytest.fixture
    async def client(self, db_pool, aiohttp_client):
        """Create a test client with real service wired to test DB."""
        from src.api.app import create_app

        app = create_app(db_pool=db_pool)
        return await aiohttp_client(app)

    @pytest.mark.integration
    async def test_post_and_get_pipeline(self, client):
        """POST to create, then GET to retrieve should return same data."""
        # Create
        create_resp = await client.post(
            "/api/v1/pipelines",
            json={
                "project_id": "proj-api-integ",
                "pipeline_name": "full-stack-first-14-doc",
                "brief": "API integration test",
            },
            headers={"Authorization": "Bearer test-jwt"},
        )
        assert create_resp.status == 201
        create_body = await create_resp.json()
        run_id = create_body["data"]["run_id"]

        # Retrieve
        get_resp = await client.get(
            f"/api/v1/pipelines/{run_id}",
            headers={"Authorization": "Bearer test-jwt"},
        )
        assert get_resp.status == 200
        get_body = await get_resp.json()
        assert get_body["data"]["run_id"] == run_id
        assert get_body["data"]["project_id"] == "proj-api-integ"
```

---

## 8. Dashboard Tests

### 8.1 Component Render Tests

Using Streamlit's `AppTest` framework to verify pages render correctly with mocked REST API responses.

```python
# tests/dashboard/test_fleet_health.py
import pytest
from unittest.mock import patch, AsyncMock
from streamlit.testing.v1 import AppTest


class TestFleetHealthPage:
    """Tests for the Fleet Health dashboard page."""

    @pytest.fixture
    def mock_api_responses(self):
        """Mock REST API responses for Fleet Health page."""
        return {
            "fleet_health": {
                "ok": True,
                "data": {
                    "healthy_agents": 45,
                    "total_agents": 48,
                    "by_phase": {
                        "plan": {"total": 10, "healthy": 10},
                        "design": {"total": 10, "healthy": 9},
                        "build": {"total": 12, "healthy": 11},
                        "verify": {"total": 10, "healthy": 9},
                        "deploy": {"total": 6, "healthy": 6},
                    },
                    "by_status": {
                        "active": 42,
                        "degraded": 3,
                        "offline": 2,
                        "canary": 1,
                    },
                    "circuit_breakers_open": 1,
                    "avg_response_ms": 120,
                    "p95_response_ms": 340,
                    "fleet_cost_today_usd": 12.50,
                    "active_pipelines": 2,
                    "pending_approvals": 1,
                    "last_updated_at": "2026-03-24T10:00:00Z",
                },
                "error": None,
                "meta": {},
            },
            "agents": {
                "ok": True,
                "data": [
                    {
                        "agent_id": f"agent-{i:03d}",
                        "name": f"Agent {i}",
                        "phase": "build",
                        "archetype": "writer",
                        "status": "active",
                        "active_version": "1.0.0",
                        "cost_today_usd": 0.25,
                        "last_invocation_at": "2026-03-24T09:30:00Z",
                        "invocation_count_today": 5,
                    }
                    for i in range(3)
                ],
                "error": None,
                "meta": {},
            },
        }

    @pytest.mark.unit
    def test_fleet_health_renders_summary_cards(self, mock_api_responses):
        """Fleet Health page should render MetricCard components for key stats."""
        with patch("src.dashboard.api_client.get") as mock_get:
            mock_get.side_effect = lambda url: mock_api_responses.get(
                url.split("/")[-1], {}
            )

            at = AppTest.from_file("src/dashboard/pages/fleet_health.py")
            at.run()

            assert not at.exception
            # Check that key metrics are displayed
            rendered_text = str(at)
            assert "45" in rendered_text  # healthy_agents
            assert "48" in rendered_text  # total_agents
            assert "$12.50" in rendered_text or "12.50" in rendered_text  # cost

    @pytest.mark.unit
    def test_fleet_health_renders_agent_grid(self, mock_api_responses):
        """Fleet Health page should render the agent grid with status tiles."""
        with patch("src.dashboard.api_client.get") as mock_get:
            mock_get.return_value = mock_api_responses["agents"]

            at = AppTest.from_file("src/dashboard/pages/fleet_health.py")
            at.run()

            assert not at.exception
            # Agent grid should show agent names
            rendered_text = str(at)
            assert "Agent 0" in rendered_text

    @pytest.mark.unit
    def test_fleet_health_shows_circuit_breaker_warning(self, mock_api_responses):
        """When circuit_breakers_open > 0, a warning should be displayed."""
        with patch("src.dashboard.api_client.get") as mock_get:
            mock_get.return_value = mock_api_responses["fleet_health"]

            at = AppTest.from_file("src/dashboard/pages/fleet_health.py")
            at.run()

            assert not at.exception
            # Should show warning about open circuit breakers
            rendered_text = str(at)
            assert "circuit" in rendered_text.lower() or "breaker" in rendered_text.lower()

    @pytest.mark.unit
    def test_fleet_health_handles_api_error(self):
        """Fleet Health page should show error state when API call fails."""
        with patch("src.dashboard.api_client.get") as mock_get:
            mock_get.side_effect = Exception("API unavailable")

            at = AppTest.from_file("src/dashboard/pages/fleet_health.py")
            at.run()

            assert not at.exception  # Page should not crash
            rendered_text = str(at)
            assert "error" in rendered_text.lower() or "unavailable" in rendered_text.lower()
```

### 8.2 Accessibility Tests

```python
# tests/dashboard/test_accessibility.py
import pytest
from playwright.async_api import async_playwright


DASHBOARD_PAGES = [
    ("/fleet-health", "Fleet Health"),
    ("/cost-monitor", "Cost Monitor"),
    ("/pipeline-runs", "Pipeline Runs"),
    ("/audit-log", "Audit Log"),
    ("/approval-queue", "Approval Queue"),
]


class TestDashboardAccessibility:
    """Automated WCAG 2.1 AA accessibility checks (Q-029 to Q-033)."""

    @pytest.mark.parametrize("path,name", DASHBOARD_PAGES)
    @pytest.mark.integration
    async def test_wcag_aa_compliance(self, path, name, dashboard_url):
        """Each dashboard page should pass axe-core WCAG 2.1 AA checks."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"{dashboard_url}{path}")
            await page.wait_for_load_state("networkidle")

            # Inject axe-core and run accessibility audit
            await page.add_script_tag(
                url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js"
            )
            results = await page.evaluate("axe.run()")

            violations = results.get("violations", [])
            # Filter to WCAG 2.1 AA violations only
            aa_violations = [
                v for v in violations
                if any(
                    "wcag2a" in tag or "wcag2aa" in tag
                    for tag in v.get("tags", [])
                )
            ]

            assert len(aa_violations) == 0, (
                f"{name} page has {len(aa_violations)} WCAG AA violations: "
                f"{[v['id'] for v in aa_violations]}"
            )

            await browser.close()

    @pytest.mark.parametrize("path,name", DASHBOARD_PAGES)
    @pytest.mark.integration
    async def test_keyboard_navigation(self, path, name, dashboard_url):
        """All interactive elements should be reachable via keyboard (Q-030)."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"{dashboard_url}{path}")
            await page.wait_for_load_state("networkidle")

            # Tab through the page and collect focused elements
            focused_elements = []
            for _ in range(50):  # Max 50 tab presses
                await page.keyboard.press("Tab")
                tag = await page.evaluate(
                    "document.activeElement?.tagName?.toLowerCase()"
                )
                if tag == "body":
                    break
                focused_elements.append(tag)

            # At least some interactive elements should be focusable
            interactive_tags = {"a", "button", "input", "select", "textarea"}
            focusable_interactive = [
                el for el in focused_elements if el in interactive_tags
            ]
            assert len(focusable_interactive) > 0, (
                f"{name} page has no keyboard-focusable interactive elements"
            )

            await browser.close()
```

---

## 9. Cross-Interface Tests (Full-Stack-First Unique)

This is the defining test category for Full-Stack-First. These tests verify that MCP and REST return identical data for the same operation, and that multi-step journeys spanning interfaces work end-to-end.

### 9.1 Parity Tests (Q-049, Q-051, Q-053)

```python
# tests/integration/test_parity.py
import json

import pytest

from src.models.pipeline import PipelineRun
from src.models.agent import AgentSummary


class TestInterfaceParity:
    """Verify MCP and REST return same data shapes for same operations (Q-049, Q-051)."""

    @pytest.fixture
    async def mcp_client(self, mcp_session):
        """MCP client connected to agents server."""
        return mcp_session

    @pytest.fixture
    async def api_client(self, aiohttp_client, db_pool):
        """REST API test client."""
        from src.api.app import create_app
        app = create_app(db_pool=db_pool)
        return await aiohttp_client(app)

    @pytest.mark.parity
    async def test_trigger_pipeline_parity(self, mcp_client, api_client):
        """trigger_pipeline MCP tool and POST /api/v1/pipelines should return same shape."""
        input_data = {
            "project_id": "proj-parity-001",
            "pipeline_name": "full-stack-first-14-doc",
            "brief": "Parity test pipeline",
        }

        # Call via MCP
        mcp_response = await mcp_client.call_tool("trigger_pipeline", input_data)
        mcp_result = json.loads(mcp_response.content[0].text)

        # Call via REST
        api_response = await api_client.post(
            "/api/v1/pipelines",
            json=input_data,
            headers={"Authorization": "Bearer test-jwt"},
        )
        api_body = await api_response.json()
        api_result = api_body["data"]

        # Same data shape: identical keys
        assert set(mcp_result.keys()) == set(api_result.keys()), (
            f"Key mismatch: MCP has {set(mcp_result.keys()) - set(api_result.keys())} extra, "
            f"REST has {set(api_result.keys()) - set(mcp_result.keys())} extra"
        )

        # Same value types for each key
        for key in mcp_result:
            mcp_type = type(mcp_result[key]).__name__
            api_type = type(api_result[key]).__name__
            assert mcp_type == api_type, (
                f"Type mismatch for '{key}': MCP={mcp_type}, REST={api_type}"
            )

        # Same status and structure (values may differ since they are separate calls)
        assert mcp_result["status"] == api_result["status"]
        assert mcp_result["total_steps"] == api_result["total_steps"]

    @pytest.mark.parity
    async def test_list_agents_parity(self, mcp_client, api_client, seed_agents):
        """list_agents MCP tool and GET /api/v1/agents should return same shape."""
        # Call via MCP
        mcp_response = await mcp_client.call_tool("list_agents", {})
        mcp_result = json.loads(mcp_response.content[0].text)

        # Call via REST
        api_response = await api_client.get(
            "/api/v1/agents",
            headers={"Authorization": "Bearer test-jwt"},
        )
        api_body = await api_response.json()
        api_result = api_body["data"]

        # Both should return arrays
        assert isinstance(mcp_result, list)
        assert isinstance(api_result, list)

        # Same count
        assert len(mcp_result) == len(api_result)

        # Same keys in each item
        if mcp_result:
            assert set(mcp_result[0].keys()) == set(api_result[0].keys())

    @pytest.mark.parity
    async def test_get_cost_report_parity(self, mcp_client, api_client):
        """get_cost_report MCP tool and GET /api/v1/cost/report should return same shape."""
        params = {"scope": "fleet", "period_days": 7}

        # Call via MCP
        mcp_response = await mcp_client.call_tool("get_cost_report", params)
        mcp_result = json.loads(mcp_response.content[0].text)

        # Call via REST
        api_response = await api_client.get(
            "/api/v1/cost/report",
            params=params,
            headers={"Authorization": "Bearer test-jwt"},
        )
        api_body = await api_response.json()
        api_result = api_body["data"]

        assert set(mcp_result.keys()) == set(api_result.keys())
        assert mcp_result["scope"] == api_result["scope"]
        assert mcp_result["period_days"] == api_result["period_days"]

    @pytest.mark.parity
    async def test_query_audit_events_parity(self, mcp_client, api_client, seed_audit_events):
        """query_audit_events MCP and GET /api/v1/audit/events should match."""
        params = {"severity": "error", "limit": 10}

        mcp_response = await mcp_client.call_tool("query_audit_events", params)
        mcp_result = json.loads(mcp_response.content[0].text)

        api_response = await api_client.get(
            "/api/v1/audit/events",
            params=params,
            headers={"Authorization": "Bearer test-jwt"},
        )
        api_body = await api_response.json()
        api_result = api_body["data"]

        assert isinstance(mcp_result, list)
        assert isinstance(api_result, list)
        if mcp_result:
            assert set(mcp_result[0].keys()) == set(api_result[0].keys())

    @pytest.mark.parity
    async def test_list_pending_approvals_parity(
        self, mcp_client, api_client, seed_approval_requests
    ):
        """list_pending_approvals MCP and GET /api/v1/approvals should match."""
        mcp_response = await mcp_client.call_tool("list_pending_approvals", {})
        mcp_result = json.loads(mcp_response.content[0].text)

        api_response = await api_client.get(
            "/api/v1/approvals?status=pending",
            headers={"Authorization": "Bearer test-jwt"},
        )
        api_body = await api_response.json()
        api_result = api_body["data"]

        assert isinstance(mcp_result, list)
        assert isinstance(api_result, list)
        if mcp_result:
            assert set(mcp_result[0].keys()) == set(api_result[0].keys())
```

### 9.2 Error Code Parity (Q-050)

```python
# tests/integration/test_error_parity.py
import json

import pytest

from src.shared.error_codes import ErrorCode


class TestErrorCodeParity:
    """Verify MCP and REST return consistent error codes for same failures (Q-050)."""

    ERROR_SCENARIOS = [
        ("not_found", "get_pipeline_status", {"run_id": "nonexistent-id"}, "/api/v1/pipelines/nonexistent-id", 404),
        ("validation", "trigger_pipeline", {"project_id": ""}, "/api/v1/pipelines", 400),
        ("conflict", "approve_gate", {"approval_id": "already-decided"}, "/api/v1/approvals/already-decided/approve", 409),
    ]

    @pytest.mark.parity
    @pytest.mark.parametrize("scenario,tool,mcp_args,rest_path,expected_http", ERROR_SCENARIOS)
    async def test_error_code_mapping(
        self, scenario, tool, mcp_args, rest_path, expected_http,
        mcp_client, api_client
    ):
        """Same error should produce mapped MCP error code and HTTP status."""
        # Trigger error via MCP
        try:
            await mcp_client.call_tool(tool, mcp_args)
            pytest.fail(f"Expected MCP error for scenario '{scenario}'")
        except Exception as mcp_error:
            mcp_error_str = str(mcp_error)

        # Trigger same error via REST
        if "trigger" in tool or "approve" in tool or "reject" in tool:
            api_response = await api_client.post(
                rest_path,
                json=mcp_args,
                headers={"Authorization": "Bearer test-jwt"},
            )
        else:
            api_response = await api_client.get(
                rest_path,
                headers={"Authorization": "Bearer test-jwt"},
            )

        assert api_response.status == expected_http
        api_body = await api_response.json()

        # Both should reference the same error code from shared enum
        assert api_body["error"]["code"] in [e.value for e in ErrorCode]
```

### 9.3 Journey Tests

#### Journey 1: Pipeline with Approval Gate (Flagship)

```python
# tests/integration/test_pipeline_approval.py
import json
import asyncio

import pytest


class TestJourney1PipelineApproval:
    """
    Journey 1: Pipeline with Approval Gate

    Priya (MCP) triggers pipeline -> Pipeline pauses at approval gate ->
    Anika (Dashboard/REST) approves -> Pipeline resumes -> Priya checks completion.

    Interactions: I-009, I-001, I-002, I-045, I-046, I-002, I-006
    """

    @pytest.mark.journey
    @pytest.mark.e2e
    async def test_full_pipeline_approval_journey(
        self, mcp_client, api_client, db_pool
    ):
        """End-to-end: MCP trigger -> approval gate -> REST approve -> MCP complete."""

        # Step 1 (Priya/MCP): Validate project input (I-009)
        validate_response = await mcp_client.call_tool(
            "validate_project_input",
            {"project_id": "proj-journey-001", "brief": "Journey test project"},
        )
        validate_result = json.loads(validate_response.content[0].text)
        assert validate_result["valid"] is True

        # Step 2 (Priya/MCP): Trigger pipeline (I-001)
        trigger_response = await mcp_client.call_tool(
            "trigger_pipeline",
            {
                "project_id": "proj-journey-001",
                "pipeline_name": "full-stack-first-14-doc",
                "brief": "Journey test: pipeline with approval gate",
            },
        )
        trigger_result = json.loads(trigger_response.content[0].text)
        run_id = trigger_result["run_id"]
        assert trigger_result["status"] == "pending"

        # Step 3 (Priya/MCP): Poll status until pipeline reaches approval gate (I-002)
        max_polls = 30
        for _ in range(max_polls):
            status_response = await mcp_client.call_tool(
                "get_pipeline_status",
                {"run_id": run_id},
            )
            status_result = json.loads(status_response.content[0].text)

            if status_result["status"] == "paused":
                break
            if status_result["status"] in ("failed", "cancelled"):
                pytest.fail(f"Pipeline entered unexpected state: {status_result['status']}")

            await asyncio.sleep(1)
        else:
            pytest.fail("Pipeline did not reach approval gate within timeout")

        assert status_result["status"] == "paused"

        # Step 4 (System): Verify ApprovalRequest was created
        async with db_pool.acquire() as conn:
            approval = await conn.fetchrow(
                "SELECT * FROM approval_requests WHERE run_id = $1 AND status = 'pending'",
                run_id,
            )
            assert approval is not None
            approval_id = str(approval["approval_id"])

        # Step 5 (Anika/REST): List pending approvals (I-045)
        approvals_resp = await api_client.get(
            "/api/v1/approvals?status=pending",
            headers={"Authorization": "Bearer anika-jwt"},
        )
        assert approvals_resp.status == 200
        approvals_body = await approvals_resp.json()
        pending_ids = [a["approval_id"] for a in approvals_body["data"]]
        assert approval_id in pending_ids

        # Step 6 (Anika/REST): Approve the gate (I-046)
        approve_resp = await api_client.post(
            f"/api/v1/approvals/{approval_id}/approve",
            json={"comment": "Approved by Anika in journey test"},
            headers={"Authorization": "Bearer anika-jwt"},
        )
        assert approve_resp.status == 200
        approve_body = await approve_resp.json()
        assert approve_body["data"]["status"] == "approved"
        assert approve_body["data"]["pipeline_resumed"] is True

        # Step 7 (System): Pipeline auto-resumes
        # Step 8 (Priya/MCP): Poll until completion (I-002)
        for _ in range(60):  # Up to 60s for pipeline completion
            status_response = await mcp_client.call_tool(
                "get_pipeline_status",
                {"run_id": run_id},
            )
            status_result = json.loads(status_response.content[0].text)

            if status_result["status"] == "completed":
                break
            if status_result["status"] == "failed":
                pytest.fail(f"Pipeline failed: {status_result.get('error_message')}")

            await asyncio.sleep(2)
        else:
            pytest.fail("Pipeline did not complete within timeout")

        assert status_result["status"] == "completed"
        assert status_result["cost_usd"] <= 25.00  # Q-060

        # Step 9 (Priya/MCP): Retrieve generated documents (I-006)
        docs_response = await mcp_client.call_tool(
            "get_pipeline_documents",
            {"run_id": run_id},
        )
        docs_result = json.loads(docs_response.content[0].text)
        assert len(docs_result) == 14  # 14 documents
        assert all(doc.get("quality_score") is not None for doc in docs_result)

    @pytest.mark.journey
    @pytest.mark.e2e
    async def test_pipeline_rejection_journey(self, mcp_client, api_client, db_pool):
        """Variant: Pipeline gate rejected, pipeline stays paused."""

        # Trigger pipeline
        trigger_response = await mcp_client.call_tool(
            "trigger_pipeline",
            {
                "project_id": "proj-journey-reject",
                "pipeline_name": "full-stack-first-14-doc",
                "brief": "Journey test: rejection path",
            },
        )
        trigger_result = json.loads(trigger_response.content[0].text)
        run_id = trigger_result["run_id"]

        # Wait for approval gate
        for _ in range(30):
            status_response = await mcp_client.call_tool(
                "get_pipeline_status", {"run_id": run_id}
            )
            status_result = json.loads(status_response.content[0].text)
            if status_result["status"] == "paused":
                break
            await asyncio.sleep(1)

        # Get approval ID
        async with db_pool.acquire() as conn:
            approval = await conn.fetchrow(
                "SELECT approval_id FROM approval_requests WHERE run_id = $1 AND status = 'pending'",
                run_id,
            )
            approval_id = str(approval["approval_id"])

        # Reject the gate (I-047) -- comment is mandatory
        reject_resp = await api_client.post(
            f"/api/v1/approvals/{approval_id}/reject",
            json={"comment": "Quality concerns in journey test"},
            headers={"Authorization": "Bearer anika-jwt"},
        )
        assert reject_resp.status == 200
        reject_body = await reject_resp.json()
        assert reject_body["data"]["status"] == "rejected"
        assert reject_body["data"]["pipeline_resumed"] is False

        # Pipeline should remain paused (not resumed)
        status_response = await mcp_client.call_tool(
            "get_pipeline_status", {"run_id": run_id}
        )
        status_result = json.loads(status_response.content[0].text)
        assert status_result["status"] == "paused"
```

#### Journey 2: Cost Spike Investigation

```python
# tests/integration/test_cost_investigation.py
import json

import pytest


class TestJourney2CostInvestigation:
    """
    Journey 2: Cost Spike Investigation

    System detects anomaly -> David (Dashboard/REST) investigates ->
    Priya (MCP) identifies root cause and adjusts threshold.

    Interactions: I-048, I-040, I-041, I-080, I-021, I-023, I-049
    """

    @pytest.mark.journey
    @pytest.mark.e2e
    async def test_cost_spike_investigation(self, mcp_client, api_client, seed_agents):
        """End-to-end: anomaly detection -> dashboard investigation -> MCP fix."""

        # Step 2 (David/REST): View anomalies on Cost Monitor (I-048)
        anomaly_resp = await api_client.get(
            "/api/v1/cost/anomalies",
            headers={"Authorization": "Bearer david-jwt"},
        )
        assert anomaly_resp.status == 200
        anomaly_body = await anomaly_resp.json()
        anomalies = anomaly_body["data"]
        assert isinstance(anomalies, list)

        # Step 3 (David/REST): View fleet cost report (I-040)
        report_resp = await api_client.get(
            "/api/v1/cost/report?scope=fleet&period_days=7",
            headers={"Authorization": "Bearer david-jwt"},
        )
        assert report_resp.status == 200
        report_body = await report_resp.json()
        assert report_body["data"]["scope"] == "fleet"
        assert "breakdown" in report_body["data"]

        # Step 4 (David/REST): Check budget status (I-041)
        budget_resp = await api_client.get(
            "/api/v1/cost/budget?scope=fleet",
            headers={"Authorization": "Bearer david-jwt"},
        )
        assert budget_resp.status == 200
        budget_body = await budget_resp.json()
        assert "utilization_pct" in budget_body["data"]

        # Step 5 (David/REST): Check fleet health (I-080)
        health_resp = await api_client.get(
            "/api/v1/system/fleet-health",
            headers={"Authorization": "Bearer david-jwt"},
        )
        assert health_resp.status == 200
        health_body = await health_resp.json()
        assert "healthy_agents" in health_body["data"]
        assert "circuit_breakers_open" in health_body["data"]

        # Step 6 (Priya/MCP): Get agent detail for suspect agent (I-021)
        agent_response = await mcp_client.call_tool(
            "get_agent",
            {"agent_id": "agent-000"},
        )
        agent_result = json.loads(agent_response.content[0].text)
        assert "agent_id" in agent_result
        assert "cost_today_usd" in agent_result

        # Step 7 (Priya/MCP): Check agent health (I-023)
        health_response = await mcp_client.call_tool(
            "check_agent_health",
            {"agent_id": "agent-000"},
        )
        health_result = json.loads(health_response.content[0].text)
        assert "healthy" in health_result
        assert "response_time_ms" in health_result

        # Step 8 (Priya/MCP): Set budget threshold (I-049)
        threshold_response = await mcp_client.call_tool(
            "set_budget_threshold",
            {
                "scope": "agent",
                "entity_id": "agent-000",
                "alert_threshold_pct": 70,
            },
        )
        threshold_result = json.loads(threshold_response.content[0].text)
        assert threshold_result["alert_threshold_pct"] == 70
```

#### Journey 3: Agent Canary Deployment

```python
# tests/integration/test_canary_deploy.py
import json

import pytest


class TestJourney3CanaryDeploy:
    """
    Journey 3: Agent Canary Deployment

    Priya (MCP) deploys canary -> Jason (Dashboard) monitors ->
    Priya increases traffic -> Priya promotes.

    Interactions: I-026, I-020, I-080, I-026, I-021, I-027, I-024
    """

    @pytest.mark.journey
    @pytest.mark.e2e
    async def test_canary_deployment_lifecycle(
        self, mcp_client, api_client, seed_agents
    ):
        """End-to-end: set canary -> monitor -> ramp -> promote."""
        agent_id = "agent-000"

        # Step 1 (Priya/MCP): Set canary traffic to 10% (I-026)
        canary_response = await mcp_client.call_tool(
            "set_canary_traffic",
            {"agent_id": agent_id, "canary_traffic_pct": 10},
        )
        canary_result = json.loads(canary_response.content[0].text)
        assert canary_result["canary_traffic_pct"] == 10

        # Step 2 (Jason/REST): View agents filtered by canary status (I-020)
        agents_resp = await api_client.get(
            "/api/v1/agents?status=canary",
            headers={"Authorization": "Bearer jason-jwt"},
        )
        assert agents_resp.status == 200
        agents_body = await agents_resp.json()
        canary_agents = agents_body["data"]
        assert any(a["agent_id"] == agent_id for a in canary_agents)

        # Step 3 (Jason/REST): Check fleet health (I-080)
        health_resp = await api_client.get(
            "/api/v1/system/fleet-health",
            headers={"Authorization": "Bearer jason-jwt"},
        )
        assert health_resp.status == 200

        # Step 4 (Priya/MCP): Increase to 50% (I-026)
        canary_response = await mcp_client.call_tool(
            "set_canary_traffic",
            {"agent_id": agent_id, "canary_traffic_pct": 50},
        )
        canary_result = json.loads(canary_response.content[0].text)
        assert canary_result["canary_traffic_pct"] == 50

        # Step 6 (Priya/MCP): Check maturity (I-027)
        maturity_response = await mcp_client.call_tool(
            "get_agent_maturity",
            {"agent_id": agent_id},
        )
        maturity_result = json.loads(maturity_response.content[0].text)
        assert "confidence_avg" in maturity_result

        # Step 7 (Priya/MCP): Promote canary to active (I-024)
        promote_response = await mcp_client.call_tool(
            "promote_agent_version",
            {"agent_id": agent_id},
        )
        promote_result = json.loads(promote_response.content[0].text)
        assert promote_result["canary_version"] is None  # Canary cleared after promote
        assert promote_result["canary_traffic_pct"] == 0
```

#### Journey 4: Compliance Audit

```python
# tests/integration/test_compliance_audit.py
import json

import pytest


class TestJourney4ComplianceAudit:
    """
    Journey 4: Compliance Audit

    Fatima (Dashboard) reviews audit trail -> exports report ->
    Anika cross-references approvals.

    Interactions: I-043, I-042, I-044, I-082, I-045, I-042
    """

    @pytest.mark.journey
    @pytest.mark.e2e
    async def test_compliance_audit_journey(
        self, api_client, seed_audit_events, seed_approval_requests
    ):
        """End-to-end compliance audit: review -> export -> cross-reference."""

        # Step 1 (Fatima/REST): View audit summary (I-043)
        summary_resp = await api_client.get(
            "/api/v1/audit/summary?period_days=30",
            headers={"Authorization": "Bearer fatima-jwt"},
        )
        assert summary_resp.status == 200
        summary_body = await summary_resp.json()
        assert "total_events" in summary_body["data"]
        assert "by_severity" in summary_body["data"]

        # Step 2 (Fatima/REST): Query error + critical events (I-042)
        events_resp = await api_client.get(
            "/api/v1/audit/events?severity=error&severity=critical&limit=50",
            headers={"Authorization": "Bearer fatima-jwt"},
        )
        assert events_resp.status == 200
        events_body = await events_resp.json()
        events = events_body["data"]
        assert all(
            e["severity"] in ("error", "critical") for e in events
        )

        # Step 3 (Fatima/REST): Export audit report as PDF (I-044)
        export_resp = await api_client.post(
            "/api/v1/audit/export",
            json={"format": "pdf", "period_days": 30},
            headers={"Authorization": "Bearer fatima-jwt"},
        )
        assert export_resp.status == 200
        export_body = await export_resp.json()
        assert "download_url" in export_body["data"]
        assert export_body["data"]["format"] == "pdf"

        # Step 4 (Fatima/REST): Review MCP call history (I-082)
        mcp_calls_resp = await api_client.get(
            "/api/v1/system/mcp-calls?limit=50",
            headers={"Authorization": "Bearer fatima-jwt"},
        )
        assert mcp_calls_resp.status == 200
        mcp_calls_body = await mcp_calls_resp.json()
        assert isinstance(mcp_calls_body["data"], list)

        # Step 5 (Anika/REST): Review past approval decisions (I-045)
        approvals_resp = await api_client.get(
            "/api/v1/approvals?status=approved&status=rejected",
            headers={"Authorization": "Bearer anika-jwt"},
        )
        assert approvals_resp.status == 200

        # Step 6 (Anika/REST): Cross-reference with audit events (I-042)
        approval_events_resp = await api_client.get(
            "/api/v1/audit/events?action=approval.approve&action=approval.reject",
            headers={"Authorization": "Bearer anika-jwt"},
        )
        assert approval_events_resp.status == 200
```

---

## 10. Agent Tests

### 10.1 Golden Test Pattern

Golden tests validate that an agent produces expected output structure and content from known inputs. Each agent has at least 3 golden tests (Q-039).

```python
# tests/agents/test_g1_cost_tracker.py
import json

import pytest

from src.agents.g1_cost_tracker import G1CostTracker


class TestG1CostTrackerGolden:
    """Golden-path tests for G1 Cost Tracker agent."""

    @pytest.fixture
    def agent(self):
        return G1CostTracker()

    @pytest.mark.golden
    async def test_golden_normal_cost_tracking(self, agent):
        """Agent should produce cost summary with breakdown for normal invocation."""
        input_data = {
            "pipeline_run_id": "run-golden-001",
            "project_id": "proj-001",
            "agent_invocations": [
                {"agent_id": "agent-prd-writer", "tokens_in": 500, "tokens_out": 2000, "model": "claude-opus-4-6"},
                {"agent_id": "agent-arch-writer", "tokens_in": 800, "tokens_out": 3000, "model": "claude-opus-4-6"},
            ],
        }

        result = await agent.invoke(input_data)

        # Verify output structure
        assert "total_cost_usd" in result
        assert "breakdown" in result
        assert isinstance(result["breakdown"], list)
        assert len(result["breakdown"]) == 2

        # Verify cost calculation
        assert result["total_cost_usd"] > 0
        assert result["total_cost_usd"] < 25.00  # Q-060 ceiling

        # Verify each breakdown item has required fields
        for item in result["breakdown"]:
            assert "agent_id" in item
            assert "cost_usd" in item
            assert "tokens_in" in item
            assert "tokens_out" in item
            assert item["cost_usd"] > 0

    @pytest.mark.golden
    async def test_golden_budget_warning_at_80pct(self, agent):
        """Agent should emit warning when cost reaches 80% of budget."""
        input_data = {
            "pipeline_run_id": "run-golden-002",
            "project_id": "proj-001",
            "accumulated_cost_usd": 20.00,  # 80% of $25 ceiling
            "agent_invocations": [
                {"agent_id": "agent-test-writer", "tokens_in": 500, "tokens_out": 1000, "model": "claude-opus-4-6"},
            ],
        }

        result = await agent.invoke(input_data)

        assert "warnings" in result
        assert any("budget" in w.lower() for w in result["warnings"])

    @pytest.mark.golden
    async def test_golden_zero_cost_empty_invocations(self, agent):
        """Agent should return zero cost for empty invocation list."""
        input_data = {
            "pipeline_run_id": "run-golden-003",
            "project_id": "proj-001",
            "agent_invocations": [],
        }

        result = await agent.invoke(input_data)

        assert result["total_cost_usd"] == 0.0
        assert result["breakdown"] == []


class TestG1CostTrackerAdversarial:
    """Adversarial tests for G1 Cost Tracker agent."""

    @pytest.fixture
    def agent(self):
        return G1CostTracker()

    @pytest.mark.adversarial
    async def test_adversarial_budget_exhaustion(self, agent):
        """Agent should hard-stop at $25 ceiling and not exceed budget."""
        input_data = {
            "pipeline_run_id": "run-adversarial-001",
            "project_id": "proj-001",
            "accumulated_cost_usd": 24.90,  # Near ceiling
            "agent_invocations": [
                # Massive invocation that would push over $25
                {"agent_id": "agent-runaway", "tokens_in": 50000, "tokens_out": 100000, "model": "claude-opus-4-6"},
            ],
        }

        result = await agent.invoke(input_data)

        # Agent should halt or reject, not exceed ceiling
        assert result.get("hard_stop") is True or result["total_cost_usd"] <= 25.00
        assert "ceiling" in str(result).lower() or "budget" in str(result).lower()

    @pytest.mark.adversarial
    async def test_adversarial_malformed_input(self, agent):
        """Agent should handle malformed input gracefully."""
        with pytest.raises((ValueError, TypeError)):
            await agent.invoke({"garbage": "data", "no_required_fields": True})

    @pytest.mark.adversarial
    async def test_adversarial_negative_token_counts(self, agent):
        """Agent should reject negative token counts."""
        input_data = {
            "pipeline_run_id": "run-adversarial-003",
            "project_id": "proj-001",
            "agent_invocations": [
                {"agent_id": "agent-bad", "tokens_in": -500, "tokens_out": -1000, "model": "claude-opus-4-6"},
            ],
        }

        with pytest.raises(ValueError, match="negative"):
            await agent.invoke(input_data)
```

### 10.2 Agent Coverage Meta-Test

```python
# tests/agents/test_agent_coverage.py
import json
import os
from pathlib import Path

import pytest

AGENTS_TEST_DIR = Path(__file__).parent
MANIFEST_PATH = AGENTS_TEST_DIR / "manifest.json"


class TestAgentCoverageManifest:
    """Meta-test: verify all 48 agents have required test coverage (Q-039)."""

    @pytest.fixture
    def manifest(self):
        with open(MANIFEST_PATH) as f:
            return json.load(f)

    def test_manifest_covers_all_48_agents(self, manifest):
        """Manifest should list all 48 agents."""
        assert len(manifest["agents"]) == 48

    def test_each_agent_has_test_file(self, manifest):
        """Each agent in manifest should have a corresponding test file."""
        for agent in manifest["agents"]:
            test_file = AGENTS_TEST_DIR / f"test_{agent['agent_id'].replace('-', '_')}.py"
            assert test_file.exists(), (
                f"Missing test file for agent '{agent['agent_id']}': {test_file}"
            )

    def test_each_agent_has_minimum_golden_tests(self, manifest):
        """Each agent should have >= 3 golden test cases (Q-039)."""
        for agent in manifest["agents"]:
            assert agent["golden_count"] >= 3, (
                f"Agent '{agent['agent_id']}' has {agent['golden_count']} golden tests "
                f"(minimum 3)"
            )

    def test_each_agent_has_minimum_adversarial_tests(self, manifest):
        """Each agent should have >= 1 adversarial test case (Q-039)."""
        for agent in manifest["agents"]:
            assert agent["adversarial_count"] >= 1, (
                f"Agent '{agent['agent_id']}' has {agent['adversarial_count']} "
                f"adversarial tests (minimum 1)"
            )
```

### 10.3 Quality Rubric Validation

```python
# tests/agents/conftest.py

import pytest


@pytest.fixture
def quality_rubric():
    """Standard quality rubric for agent output validation."""
    return {
        "has_version_header": lambda output: "Version:" in output,
        "has_generation_date": lambda output: "2026-" in output,
        "has_table_of_contents": lambda output: "## Table of Contents" in output or "## Contents" in output,
        "no_placeholder_text": lambda output: "[TODO]" not in output and "[PLACEHOLDER]" not in output,
        "no_empty_sections": lambda output: "\n## " not in output.replace("\n## ", "").split("\n\n\n"),
        "minimum_length": lambda output: len(output) > 500,
    }


def validate_agent_output(output: str, rubric: dict) -> list[str]:
    """Validate agent output against quality rubric. Returns list of failures."""
    failures = []
    for check_name, check_fn in rubric.items():
        if not check_fn(output):
            failures.append(check_name)
    return failures
```

---

## 10A. LLM Provider Tests

### 10A.1 Provider Portability Tests

These tests verify that the same agent produces structurally equivalent output regardless of the underlying LLM provider. The output schema and format must match; content quality may vary.

```python
# tests/providers/test_portability.py

import pytest
from sdk.llm import LLMProvider
from sdk.llm.anthropic_provider import AnthropicProvider
from sdk.llm.openai_provider import OpenAIProvider


@pytest.fixture(params=["anthropic", "openai"])
def provider(request) -> LLMProvider:
    """Parametrize across providers to run same test on each."""
    if request.param == "anthropic":
        return AnthropicProvider()
    return OpenAIProvider()


@pytest.mark.slow
class TestProviderPortability:
    """Run the same agent on different providers, verify output schema matches."""

    async def test_cost_tracker_output_schema(self, provider: LLMProvider):
        """G1-cost-tracker must return valid CostReport shape on any provider."""
        agent = create_agent("G1-cost-tracker", llm=provider)
        result = await agent.execute(golden_input("G1-cost-tracker", "TC-001"))
        assert_schema_valid(result, "CostReport")

    async def test_prd_writer_output_schema(self, provider: LLMProvider):
        """P1-prd-writer must return valid markdown with required sections."""
        agent = create_agent("P1-prd-writer", llm=provider)
        result = await agent.execute(golden_input("P1-prd-writer", "TC-001"))
        assert "## Personas" in result.content
        assert "## User Journeys" in result.content
```

### 10A.2 Provider Failover Tests

These tests simulate provider failures and verify the platform falls back gracefully.

```python
# tests/providers/test_failover.py

import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.medium
class TestProviderFailover:
    """Simulate provider failure, verify fallback behavior."""

    async def test_fallback_on_provider_timeout(self):
        """When primary provider times out, agent should raise ProviderError."""
        provider = create_failing_provider(error="timeout")
        agent = create_agent("G1-cost-tracker", llm=provider)
        with pytest.raises(ProviderError, match="timeout"):
            await agent.execute(golden_input("G1-cost-tracker", "TC-001"))

    async def test_fallback_on_rate_limit(self):
        """When primary provider returns 429, ProviderError includes retry_after."""
        provider = create_failing_provider(error="rate_limit", retry_after=30)
        agent = create_agent("G1-cost-tracker", llm=provider)
        with pytest.raises(ProviderError) as exc_info:
            await agent.execute(golden_input("G1-cost-tracker", "TC-001"))
        assert exc_info.value.retry_after == 30

    async def test_cost_recorded_on_partial_failure(self):
        """If provider fails mid-stream, partial token cost is still recorded."""
        provider = create_failing_provider(error="mid_stream", tokens_before_fail=500)
        agent = create_agent("G1-cost-tracker", llm=provider)
        with pytest.raises(ProviderError):
            await agent.execute(golden_input("G1-cost-tracker", "TC-001"))
        assert agent.last_cost_usd > 0  # partial cost recorded

    async def test_health_check_detects_down_provider(self):
        """ProviderService.check_health() returns healthy=false for down provider."""
        with patch("sdk.llm.anthropic_provider.AnthropicProvider.health_check",
                    new_callable=AsyncMock, return_value=False):
            result = await provider_service.check_health("anthropic")
            assert result.healthy is False
```

### 10A.3 Provider-Specific Unit Tests

Each provider implementation has its own unit test file verifying the `LLMProvider` interface contract.

```python
# tests/sdk/llm/test_anthropic_provider.py
# tests/sdk/llm/test_openai_provider.py
# tests/sdk/llm/test_ollama_provider.py

@pytest.mark.unit
class TestAnthropicProvider:
    """Unit tests for AnthropicProvider."""

    async def test_tier_resolution(self):
        """Tier 'balanced' resolves to 'claude-sonnet-4-6'."""
        provider = AnthropicProvider()
        assert provider.resolve_model("balanced") == "claude-sonnet-4-6"
        assert provider.resolve_model("fast") == "claude-haiku-3"
        assert provider.resolve_model("powerful") == "claude-opus-4-6"

    async def test_cost_calculation(self):
        """Cost per token returns correct Anthropic pricing."""
        provider = AnthropicProvider()
        input_cost, output_cost = provider.cost_per_token("claude-sonnet-4-6")
        assert input_cost > 0
        assert output_cost > input_cost  # output tokens cost more

    async def test_health_check(self):
        """Health check makes a lightweight API call."""
        provider = AnthropicProvider()
        result = await provider.health_check()
        assert isinstance(result, bool)
```

---

## 11. Performance Tests

### 11.1 NFR Mapping

| Test | NFR | Target | Tool | Cadence |
|------|-----|--------|------|---------|
| MCP read tool latency | Q-001 | p95 < 500ms | k6 (200 requests/tool) | Nightly CI |
| MCP write tool latency | Q-002 | p95 < 2s | k6 (100 requests/tool) | Nightly CI |
| MCP server startup | Q-003 | < 5s per server | pytest (timed) | Every PR |
| REST GET latency | Q-004 | p95 < 500ms | k6 (50 concurrent, 60s) | Nightly CI |
| REST POST latency | Q-004 | p95 < 1s | k6 (50 concurrent, 60s) | Nightly CI |
| Dashboard page load | Q-005 | p95 < 2s | Lighthouse CI | Nightly CI |
| Fleet Health page load | Q-006 | p95 < 1s | Lighthouse + Playwright | Nightly CI |
| Service method latency | Q-008 | p95 < 200ms | pytest-benchmark (1000 iter) | Weekly CI |
| Query execution time | Q-009 | p95 < 100ms indexed, < 500ms analytical | EXPLAIN ANALYZE | Every PR |
| Cross-interface round-trip | Q-010 | < 10 min (excl. human time) | pytest e2e | Weekly CI |

### 11.2 MCP Latency Tests

```python
# tests/performance/test_mcp_latency.py
import time
import statistics

import pytest


# MCP read tools (Q-001: p95 < 500ms)
MCP_READ_TOOLS = [
    ("get_pipeline_status", {"run_id": "perf-test-run"}),
    ("list_pipeline_runs", {}),
    ("list_agents", {}),
    ("get_agent", {"agent_id": "agent-000"}),
    ("check_agent_health", {"agent_id": "agent-000"}),
    ("get_cost_report", {"scope": "fleet", "period_days": 7}),
    ("check_budget", {"scope": "fleet"}),
    ("query_audit_events", {"limit": 50}),
    ("get_audit_summary", {"period_days": 30}),
    ("list_pending_approvals", {}),
    ("get_fleet_health", {}),
    ("get_mcp_status", {}),
    ("list_recent_mcp_calls", {"limit": 50}),
    ("search_exceptions", {"query": "test"}),
    ("list_exceptions", {"tier": "universal"}),
]

# MCP write tools (Q-002: p95 < 2s)
MCP_WRITE_TOOLS = [
    ("trigger_pipeline", {"project_id": "proj-perf", "pipeline_name": "full-stack-first-14-doc", "brief": "perf test"}),
    ("approve_gate", {"approval_id": "perf-approval"}),
    ("reject_gate", {"approval_id": "perf-approval", "comment": "perf test"}),
    ("promote_agent_version", {"agent_id": "agent-000"}),
    ("set_canary_traffic", {"agent_id": "agent-000", "canary_traffic_pct": 10}),
    ("set_budget_threshold", {"scope": "fleet", "alert_threshold_pct": 80}),
    ("create_exception", {"title": "perf test", "rule": "test", "description": "test", "tier": "client"}),
]


class TestMcpReadLatency:
    """MCP read tool latency benchmark (Q-001)."""

    @pytest.mark.performance
    @pytest.mark.parametrize("tool_name,args", MCP_READ_TOOLS)
    async def test_read_tool_p95_under_500ms(self, tool_name, args, mcp_client):
        """Each MCP read tool should respond in < 500ms at p95."""
        durations = []
        num_requests = 200

        for _ in range(num_requests):
            start = time.monotonic()
            try:
                await mcp_client.call_tool(tool_name, args)
            except Exception:
                pass  # We measure latency regardless of success
            elapsed_ms = (time.monotonic() - start) * 1000
            durations.append(elapsed_ms)

        durations.sort()
        p95_index = int(0.95 * len(durations))
        p95 = durations[p95_index]

        assert p95 < 500, (
            f"MCP read tool '{tool_name}' p95={p95:.0f}ms (max 500ms). "
            f"Median={statistics.median(durations):.0f}ms"
        )


class TestMcpWriteLatency:
    """MCP write tool latency benchmark (Q-002)."""

    @pytest.mark.performance
    @pytest.mark.parametrize("tool_name,args", MCP_WRITE_TOOLS)
    async def test_write_tool_p95_under_2s(self, tool_name, args, mcp_client):
        """Each MCP write tool should respond in < 2s at p95."""
        durations = []
        num_requests = 100

        for _ in range(num_requests):
            start = time.monotonic()
            try:
                await mcp_client.call_tool(tool_name, args)
            except Exception:
                pass
            elapsed_ms = (time.monotonic() - start) * 1000
            durations.append(elapsed_ms)

        durations.sort()
        p95_index = int(0.95 * len(durations))
        p95 = durations[p95_index]

        assert p95 < 2000, (
            f"MCP write tool '{tool_name}' p95={p95:.0f}ms (max 2000ms). "
            f"Median={statistics.median(durations):.0f}ms"
        )
```

### 11.3 REST API Latency Tests

```python
# tests/performance/test_api_latency.py
import time
import statistics

import httpx
import pytest


class TestRestApiLatency:
    """REST API latency benchmarks (Q-004)."""

    GET_ENDPOINTS = [
        "/api/v1/agents",
        "/api/v1/pipelines",
        "/api/v1/cost/report?scope=fleet&period_days=7",
        "/api/v1/audit/events?limit=50",
        "/api/v1/approvals?status=pending",
        "/api/v1/system/fleet-health",
        "/health",
    ]

    POST_ENDPOINTS = [
        ("/api/v1/pipelines", {"project_id": "proj-perf", "pipeline_name": "full-stack-first-14-doc", "brief": "perf"}),
        ("/api/v1/audit/export", {"format": "csv", "period_days": 30}),
    ]

    @pytest.mark.performance
    @pytest.mark.parametrize("endpoint", GET_ENDPOINTS)
    async def test_get_p95_under_500ms(self, endpoint, base_url, auth_headers):
        """GET endpoints should respond in < 500ms at p95."""
        durations = []
        async with httpx.AsyncClient(base_url=base_url) as client:
            for _ in range(200):
                start = time.monotonic()
                await client.get(endpoint, headers=auth_headers)
                elapsed_ms = (time.monotonic() - start) * 1000
                durations.append(elapsed_ms)

        durations.sort()
        p95 = durations[int(0.95 * len(durations))]

        assert p95 < 500, f"GET {endpoint} p95={p95:.0f}ms (max 500ms)"

    @pytest.mark.performance
    @pytest.mark.parametrize("endpoint,body", POST_ENDPOINTS)
    async def test_post_p95_under_1s(self, endpoint, body, base_url, auth_headers):
        """POST endpoints should respond in < 1s at p95."""
        durations = []
        async with httpx.AsyncClient(base_url=base_url) as client:
            for _ in range(100):
                start = time.monotonic()
                await client.post(endpoint, json=body, headers=auth_headers)
                elapsed_ms = (time.monotonic() - start) * 1000
                durations.append(elapsed_ms)

        durations.sort()
        p95 = durations[int(0.95 * len(durations))]

        assert p95 < 1000, f"POST {endpoint} p95={p95:.0f}ms (max 1000ms)"
```

### 11.4 Dashboard Load Tests

```python
# tests/performance/test_dashboard_load.py
import pytest
from playwright.async_api import async_playwright


DASHBOARD_PAGES = [
    ("/fleet-health", "Fleet Health", 1000),   # Q-006: < 1s
    ("/cost-monitor", "Cost Monitor", 2000),   # Q-005: < 2s
    ("/pipeline-runs", "Pipeline Runs", 2000), # Q-005: < 2s
    ("/audit-log", "Audit Log", 2000),         # Q-005: < 2s
    ("/approval-queue", "Approval Queue", 2000), # Q-005: < 2s
]


class TestDashboardLoadTime:
    """Dashboard page load time benchmarks (Q-005, Q-006)."""

    @pytest.mark.performance
    @pytest.mark.parametrize("path,name,max_ms", DASHBOARD_PAGES)
    async def test_page_load_under_threshold(self, path, name, max_ms, dashboard_url):
        """Each dashboard page should load within its threshold."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            durations = []
            for _ in range(10):
                start = await page.evaluate("performance.now()")
                await page.goto(f"{dashboard_url}{path}")
                await page.wait_for_load_state("networkidle")
                end = await page.evaluate("performance.now()")
                durations.append(end - start)

            import statistics
            durations.sort()
            p95 = durations[int(0.95 * len(durations))]

            assert p95 < max_ms, (
                f"{name} page p95 load time = {p95:.0f}ms (max {max_ms}ms). "
                f"Median = {statistics.median(durations):.0f}ms"
            )

            await browser.close()
```

### 11.5 k6 Load Test Scripts

```javascript
// tests/performance/k6/mcp_read_load.js
import { check } from "k6";
import http from "k6/http";

export const options = {
  scenarios: {
    mcp_read: {
      executor: "constant-arrival-rate",
      rate: 200,
      timeUnit: "1m",
      duration: "2m",
      preAllocatedVUs: 50,
      maxVUs: 100,
    },
  },
  thresholds: {
    "http_req_duration{tool_type:read}": ["p(95)<500"],
  },
};

const MCP_URL = __ENV.MCP_URL || "http://localhost:3100/mcp";
const API_KEY = __ENV.API_KEY || "test-key";

const READ_TOOLS = [
  { name: "list_agents", args: {} },
  { name: "get_fleet_health", args: {} },
  { name: "list_pipeline_runs", args: {} },
  { name: "get_cost_report", args: { scope: "fleet", period_days: 7 } },
  { name: "query_audit_events", args: { limit: 50 } },
];

export default function () {
  const tool = READ_TOOLS[Math.floor(Math.random() * READ_TOOLS.length)];

  const payload = JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: { name: tool.name, arguments: tool.args },
  });

  const res = http.post(MCP_URL, payload, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_KEY}`,
    },
    tags: { tool_type: "read", tool_name: tool.name },
  });

  check(res, {
    "status is 200": (r) => r.status === 200,
    "has result": (r) => JSON.parse(r.body).result !== undefined,
  });
}
```

---

## 12. Coverage Thresholds

Derived from QUALITY (Doc 4) NFRs Q-034 through Q-041.

| Layer | Source Path | Minimum Line | Minimum Branch | NFR | Priority | Tool |
|-------|-----------|-------------|---------------|-----|----------|------|
| Shared Services | `src/services/` | 90% | 85% | Q-034 | P0 | `pytest-cov --cov-fail-under=90` |
| MCP Handlers | `src/mcp/tools/` | 85% | -- | Q-035 | P0 | `pytest-cov --cov-fail-under=85` |
| REST Handlers | `src/api/routes/` | 85% | -- | Q-036 | P0 | `pytest-cov --cov-fail-under=85` |
| Dashboard | `src/dashboard/` | 75% | -- | Q-037 | P1 | `pytest-cov --cov-fail-under=75` |
| Parity | `tests/integration/` | 1 test per journey | -- | Q-038 | P1 | Meta-test assertion |
| Agents | `tests/agents/` | 3 golden + 1 adversarial per agent | -- | Q-039 | P1 | Manifest meta-test |
| Mutation (services) | `src/services/` | 70% killed | -- | Q-040 | P2 | `mutmut` (nightly) |
| Migrations | `src/db/migrations/` | 100% (UP + DOWN) | -- | Q-041 | P1 | `test_migrations.py` |

### Coverage CI Commands

```bash
# Shared services (Q-034)
pytest tests/services/ --cov=src/services --cov-branch --cov-fail-under=90 --cov-report=html

# MCP handlers (Q-035)
pytest tests/mcp/ --cov=src/mcp/tools --cov-fail-under=85 --cov-report=html

# REST handlers (Q-036)
pytest tests/api/ --cov=src/api/routes --cov-fail-under=85 --cov-report=html

# Dashboard (Q-037)
pytest tests/dashboard/ --cov=src/dashboard --cov-fail-under=75 --cov-report=html

# Mutation testing (Q-040, nightly only)
mutmut run --paths-to-mutate=src/services/ --runner="pytest tests/services/"
```

---

## 13. CI Pipeline

### Stage Definition

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  # ═══════════════════════════════════════════════════════
  # Stage 1: Static Analysis (fastest, catches syntax/type errors)
  # ═══════════════════════════════════════════════════════
  stage-1-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install ruff mypy
      - name: Ruff lint
        run: ruff check src/ tests/
      - name: Ruff format check
        run: ruff format --check src/ tests/
      - name: Mypy type check
        run: mypy src/ --strict

  # ═══════════════════════════════════════════════════════
  # Stage 2: Schema + Service Unit Tests (fast, no DB)
  # ═══════════════════════════════════════════════════════
  stage-2-unit:
    needs: stage-1-lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: Schema validation tests
        run: pytest tests/schemas/test_data_shapes.py -m "unit" -v
      - name: Service unit tests (Q-034)
        run: |
          pytest tests/services/ -m "unit" \
            --cov=src/services --cov-branch \
            --cov-fail-under=90 \
            --cov-report=xml:coverage-services.xml
      - name: Provider unit tests
        run: |
          pytest tests/sdk/llm/ -m "unit" -v \
            --cov=src/sdk/llm --cov-branch \
            --cov-fail-under=85 \
            --cov-report=xml:coverage-providers.xml
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-services
          path: coverage-services.xml

  # ═══════════════════════════════════════════════════════
  # Stage 3: Interface Unit Tests (parallel, no DB)
  # ═══════════════════════════════════════════════════════
  stage-3-mcp-unit:
    needs: stage-2-unit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: MCP unit + protocol tests (Q-035)
        run: |
          pytest tests/mcp/ -m "unit" \
            --cov=src/mcp/tools --cov-fail-under=85 \
            --cov-report=xml:coverage-mcp.xml

  stage-3-rest-unit:
    needs: stage-2-unit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: REST unit tests (Q-036)
        run: |
          pytest tests/api/ -m "unit" \
            --cov=src/api/routes --cov-fail-under=85 \
            --cov-report=xml:coverage-rest.xml

  stage-3-dashboard:
    needs: stage-2-unit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: Dashboard component tests (Q-037)
        run: |
          pytest tests/dashboard/ -m "unit" \
            --cov=src/dashboard --cov-fail-under=75 \
            --cov-report=xml:coverage-dashboard.xml

  # ═══════════════════════════════════════════════════════
  # Stage 4: Integration Tests (real DB via testcontainers)
  # ═══════════════════════════════════════════════════════
  stage-4-integration:
    needs: [stage-3-mcp-unit, stage-3-rest-unit, stage-3-dashboard]
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:dind
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: Migration UP + DOWN tests (Q-041)
        run: pytest tests/schemas/test_migrations.py -v
      - name: Service integration tests
        run: pytest tests/services/ -m "integration" -v
      - name: MCP integration tests
        run: pytest tests/mcp/ -m "integration" -v
      - name: REST integration tests
        run: pytest tests/api/ -m "integration" -v

  # ═══════════════════════════════════════════════════════
  # Stage 5: Cross-Interface Tests (parity + journeys)
  # ═══════════════════════════════════════════════════════
  stage-5-cross-interface:
    needs: stage-4-integration
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:dind
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -e ".[test]"
      - name: Parity tests (Q-049, Q-050, Q-051, Q-053)
        run: pytest tests/integration/ -m "parity" -v
      - name: Journey tests (Q-038)
        run: pytest tests/integration/ -m "journey" -v
      - name: Agent coverage meta-test (Q-039)
        run: pytest tests/agents/test_agent_coverage.py -v

  # ═══════════════════════════════════════════════════════
  # Stage 6: Performance Tests (nightly only)
  # ═══════════════════════════════════════════════════════
  stage-6-performance:
    if: github.event_name == 'schedule'
    needs: stage-5-cross-interface
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: grafana/setup-k6-action@v1
      - name: Install dependencies
        run: pip install -e ".[test]" && npx playwright install
      - name: MCP latency tests (Q-001, Q-002)
        run: pytest tests/performance/test_mcp_latency.py -m "performance" -v
      - name: REST latency tests (Q-004)
        run: pytest tests/performance/test_api_latency.py -m "performance" -v
      - name: k6 load tests
        run: |
          k6 run tests/performance/k6/mcp_read_load.js
          k6 run tests/performance/k6/rest_load.js
      - name: Dashboard load tests (Q-005, Q-006)
        run: pytest tests/performance/test_dashboard_load.py -m "performance" -v
      - name: Lighthouse CI
        run: npx lhci autorun --config tests/performance/lighthouse/config.js
```

### Pipeline Visualization

```
PR Opened / Push to main
         │
    ┌────▼────┐
    │ Stage 1 │  Ruff lint + mypy type check (~30s)
    │  Lint   │
    └────┬────┘
         │
    ┌────▼────┐
    │ Stage 2 │  Schema + Service unit tests (~2m)
    │  Unit   │  Coverage gate: services >= 90%
    └────┬────┘
         │
    ┌────┼────────────┬────────────┐
    │    │            │            │
┌───▼──┐ ┌──▼───┐ ┌────▼────┐
│MCP   │ │REST  │ │Dashboard│     Stage 3 (parallel, ~1m each)
│Unit  │ │Unit  │ │Component│     Coverage gates: MCP 85%, REST 85%, Dash 75%
└───┬──┘ └──┬───┘ └────┬────┘
    │       │          │
    └───────┼──────────┘
            │
    ┌───────▼───────┐
    │   Stage 4     │  Integration tests with testcontainers (~5m)
    │ Integration   │  Migrations, service, MCP, REST with real DB
    └───────┬───────┘
            │
    ┌───────▼───────┐
    │   Stage 5     │  Cross-interface parity + journey tests (~3m)
    │   Parity      │  Agent coverage meta-test
    └───────┬───────┘
            │
            │ (nightly schedule only)
    ┌───────▼───────┐
    │   Stage 6     │  Performance: k6, Lighthouse, latency benchmarks (~10m)
    │ Performance   │
    └───────────────┘
```

### Gate Summary

| Stage | Blocks PR Merge | Key Assertions |
|-------|----------------|----------------|
| 1 | Yes | Zero lint errors, zero type errors |
| 2 | Yes | Service coverage >= 90%, all unit tests pass |
| 3 | Yes | MCP coverage >= 85%, REST >= 85%, Dashboard >= 75% |
| 4 | Yes | All migrations UP + DOWN pass, all integration tests pass |
| 5 | Yes | All parity tests pass, all journey tests pass, agent manifest complete |
| 6 | No (nightly) | Performance regressions flagged but do not block merge |

---

## 14. Error Handling and Recovery Strategy

### 14.1 Document Generation Failure

When a pipeline agent fails to produce an acceptable document:

1. **First attempt fails:** System captures the error, logs to `audit_events`, and retries with rubric feedback appended to the prompt.
2. **Second attempt fails:** System retries once more with both the error and rubric feedback.
3. **Third attempt fails:** Pipeline step marked `failed`, pipeline status set to `paused`, `ApprovalRequest` created for human review.

```python
# Test pattern for retry behavior
@pytest.mark.integration
async def test_document_generation_retry_on_failure(service, clean_db):
    """Pipeline should retry failed document generation up to 2 times."""
    # Mock agent to fail on first call, succeed on second
    with patch("src.agents.registry.invoke") as mock_invoke:
        mock_invoke.side_effect = [
            AgentError("Quality score below threshold"),  # Attempt 1
            {"content": "Valid document", "quality_score": 0.85},  # Attempt 2
        ]

        result = await service.execute_step(run_id="test-run", step=6)

        assert result.status == "completed"
        assert mock_invoke.call_count == 2  # Retried once

        # Verify rubric feedback was included in retry prompt
        retry_call = mock_invoke.call_args_list[1]
        assert "rubric" in str(retry_call).lower()
```

### 14.2 Dependency Failure

When an upstream document fails and downstream documents depend on it:

```python
@pytest.mark.integration
async def test_downstream_regeneration_after_upstream_fix(service, clean_db):
    """Fixing an upstream doc should trigger regeneration of all downstream deps."""
    # Step 6 (INTERACTION-MAP) is upstream of steps 7, 8, 9, 10
    result = await service.retry_step(run_id="test-run", step_number=6)

    # Verify downstream steps are marked for re-execution
    steps = await clean_db.fetch(
        """SELECT step_number, status FROM pipeline_steps
           WHERE run_id = $1 AND step_number > 6 ORDER BY step_number""",
        "test-run",
    )
    for step in steps:
        assert step["status"] == "pending", (
            f"Step {step['step_number']} should be reset to pending"
        )
```

### 14.3 Cross-Interface Divergence

When MCP and REST return different data for the same operation:

- **Fix the handler**, not the service. Since both interfaces call the same service method, divergence means a handler is transforming the response differently.
- The parity test suite (Section 9.1) catches this automatically.

### 14.4 Partial Pipeline Resume

```python
@pytest.mark.integration
async def test_pipeline_resume_from_checkpoint(service, clean_db):
    """Resuming a failed pipeline should skip completed steps (Q-018)."""
    # Create a pipeline that failed at step 8
    run_id = await _create_pipeline_failed_at_step(clean_db, step=8)

    result = await service.resume(run_id=run_id)

    # Verify steps 0-7 are NOT re-executed
    steps = await clean_db.fetch(
        """SELECT step_number, status, started_at FROM pipeline_steps
           WHERE run_id = $1 ORDER BY step_number""",
        run_id,
    )
    for step in steps:
        if step["step_number"] < 8:
            assert step["status"] == "completed"
            # started_at should not have been updated
```

---

## 15. Test Data Strategy

### 15.1 Factory Functions

Factory functions produce valid test entities with sensible defaults. Any field can be overridden.

```python
# tests/factories.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any


def create_agent(
    agent_id: str | None = None,
    name: str | None = None,
    phase: str = "build",
    archetype: str = "writer",
    status: str = "active",
    active_version: str = "1.0.0",
    maturity_level: str = "supervised",
    model: str = "claude-opus-4-6",
    **overrides: Any,
) -> dict:
    """Create a valid agent_registry row."""
    return {
        "agent_id": agent_id or f"agent-{uuid.uuid4().hex[:8]}",
        "name": name or f"Test Agent {uuid.uuid4().hex[:6]}",
        "phase": phase,
        "archetype": archetype,
        "status": status,
        "active_version": active_version,
        "canary_version": None,
        "canary_traffic_pct": 0,
        "previous_version": None,
        "maturity_level": maturity_level,
        "model": model,
        "max_tokens": 4096,
        "temperature": 0.7,
        **overrides,
    }


def create_pipeline_run(
    run_id: str | None = None,
    project_id: str | None = None,
    pipeline_name: str = "full-stack-first-14-doc",
    status: str = "pending",
    current_step: int = 0,
    total_steps: int = 14,
    cost_usd: float = 0.0,
    triggered_by: str = "test-user",
    **overrides: Any,
) -> dict:
    """Create a valid pipeline_runs row."""
    now = datetime.now(timezone.utc)
    return {
        "run_id": run_id or str(uuid.uuid4()),
        "project_id": project_id or f"proj-{uuid.uuid4().hex[:8]}",
        "pipeline_name": pipeline_name,
        "status": status,
        "current_step": current_step,
        "total_steps": total_steps,
        "current_step_name": f"{current_step:02d}-DOC",
        "started_at": now,
        "completed_at": now if status in ("completed", "cancelled", "failed") else None,
        "cost_usd": cost_usd,
        "triggered_by": triggered_by,
        "error_message": "Test error" if status == "failed" else None,
        "checkpoint_step": current_step - 1 if current_step > 0 else None,
        **overrides,
    }


def create_audit_event(
    event_id: str | None = None,
    agent_id: str = "agent-000",
    action: str = "agent.invoke",
    severity: str = "info",
    cost_usd: float = 0.05,
    **overrides: Any,
) -> dict:
    """Create a valid audit_events row."""
    now = datetime.now(timezone.utc)
    return {
        "event_id": event_id or str(uuid.uuid4()),
        "timestamp": now,
        "agent_id": agent_id,
        "session_id": str(uuid.uuid4()),
        "project_id": f"proj-{uuid.uuid4().hex[:8]}",
        "action": action,
        "severity": severity,
        "details": "{}",
        "cost_usd": cost_usd,
        "tokens_in": 500,
        "tokens_out": 1000,
        "duration_ms": 200,
        "pii_detected": False,
        **overrides,
    }


def create_approval_request(
    approval_id: str | None = None,
    run_id: str | None = None,
    status: str = "pending",
    risk_level: str = "medium",
    **overrides: Any,
) -> dict:
    """Create a valid approval_requests row."""
    now = datetime.now(timezone.utc)
    return {
        "approval_id": approval_id or str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "run_id": run_id or str(uuid.uuid4()),
        "pipeline_name": "full-stack-first-14-doc",
        "step_number": 6,
        "step_name": "06-INTERACTION-MAP",
        "summary": "Approval needed for INTERACTION-MAP generation",
        "risk_level": risk_level,
        "status": status,
        "requested_at": now,
        "expires_at": now + timedelta(hours=24),
        "decided_at": now if status in ("approved", "rejected") else None,
        "decision_by": "anika" if status in ("approved", "rejected") else None,
        "decision_comment": "Approved" if status == "approved" else None,
        "context": "{}",
        **overrides,
    }


def create_cost_metric(
    agent_id: str = "agent-000",
    cost_usd: float = 0.05,
    **overrides: Any,
) -> dict:
    """Create a valid cost_metrics row."""
    now = datetime.now(timezone.utc)
    return {
        "id": None,  # auto-generated
        "agent_id": agent_id,
        "project_id": f"proj-{uuid.uuid4().hex[:8]}",
        "pipeline_run_id": str(uuid.uuid4()),
        "model": "claude-opus-4-6",
        "input_tokens": 500,
        "output_tokens": 1000,
        "cost_usd": cost_usd,
        "recorded_at": now,
        **overrides,
    }


def create_knowledge_exception(
    title: str = "Test Exception",
    tier: str = "client",
    **overrides: Any,
) -> dict:
    """Create a valid knowledge_exceptions row."""
    return {
        "exception_id": str(uuid.uuid4()),
        "title": title,
        "rule": "test_rule_pattern",
        "description": "Test exception for unit testing",
        "severity": "medium",
        "tier": tier,
        "stack_name": "test-stack" if tier != "universal" else None,
        "client_id": "client-001" if tier == "client" else None,
        "active": True,
        "fire_count": 0,
        "last_fired_at": None,
        "created_at": datetime.now(timezone.utc),
        "created_by": "test-user",
        "tags": ["test", "unit"],
        **overrides,
    }
```

### 15.2 Deterministic Seeding

For reproducible test runs, all random data uses a fixed seed.

```python
# tests/conftest.py (continued)
import random


@pytest.fixture(autouse=True)
def deterministic_seed():
    """Fix random seed for reproducible test data."""
    random.seed(42)
    yield
    # No cleanup needed -- each test gets the same seed
```

### 15.3 Seed Data Volumes

| Table | Seed Count | Purpose |
|-------|-----------|---------|
| `agent_registry` | 48 | Full fleet for list/filter tests |
| `cost_metrics` | 200 | Enough for aggregation + anomaly detection tests |
| `audit_events` | 100 | Enough for filter, summary, and export tests |
| `pipeline_runs` | 10 | Cover all 6 status values + edge cases |
| `pipeline_steps` | 140 | 10 runs x 14 steps each |
| `knowledge_exceptions` | 15 | 5 per tier (client, stack, universal) |
| `session_context` | 5 | Active sessions for pipeline execution tests |
| `approval_requests` | 10 | Cover all 5 status values |
| `pipeline_checkpoints` | 5 | For resume/checkpoint tests |
| `mcp_call_events` | 50 | For MCP monitoring panel tests |

---

## Appendix A: NFR-to-Test Traceability Matrix

| NFR | Test File | Test Class/Method | Stage |
|-----|-----------|-------------------|-------|
| Q-001 | `tests/performance/test_mcp_latency.py` | `TestMcpReadLatency` | 6 |
| Q-002 | `tests/performance/test_mcp_latency.py` | `TestMcpWriteLatency` | 6 |
| Q-003 | `tests/mcp/test_mcp_protocol.py` | `test_server_startup_within_5s` | 4 |
| Q-004 | `tests/performance/test_api_latency.py` | `TestRestApiLatency` | 6 |
| Q-005 | `tests/performance/test_dashboard_load.py` | `TestDashboardLoadTime` | 6 |
| Q-006 | `tests/performance/test_dashboard_load.py` | `test_page_load_under_threshold[fleet-health]` | 6 |
| Q-019 | `tests/mcp/test_mcp_auth.py` | `TestMcpAuth` | 4 |
| Q-020 | `tests/mcp/test_mcp_protocol.py` | `test_all_tools_have_valid_json_schema` | 3 |
| Q-021 | `tests/mcp/test_mcp_auth.py` | `test_project_isolation` | 4 |
| Q-022 | `tests/api/test_auth_routes.py` | `test_all_routes_require_auth` | 3 |
| Q-029 | `tests/dashboard/test_accessibility.py` | `test_wcag_aa_compliance` | 3 |
| Q-030 | `tests/dashboard/test_accessibility.py` | `test_keyboard_navigation` | 3 |
| Q-034 | `tests/services/` (all) | Coverage gate: 90% | 2 |
| Q-035 | `tests/mcp/` (all) | Coverage gate: 85% | 3 |
| Q-036 | `tests/api/` (all) | Coverage gate: 85% | 3 |
| Q-037 | `tests/dashboard/` (all) | Coverage gate: 75% | 3 |
| Q-038 | `tests/integration/` | Journey tests + parity manifest | 5 |
| Q-039 | `tests/agents/test_agent_coverage.py` | `TestAgentCoverageManifest` | 5 |
| Q-040 | (nightly) `mutmut` | 70% mutation kill rate | 6 |
| Q-041 | `tests/schemas/test_migrations.py` | UP + DOWN for all 9 migrations | 4 |
| Q-049 | `tests/integration/test_parity.py` | `TestInterfaceParity` | 5 |
| Q-050 | `tests/integration/test_error_parity.py` | `TestErrorCodeParity` | 5 |
| Q-051 | `tests/integration/test_parity.py` | Shape key equality assertions | 5 |
| Q-052 | `tests/integration/test_data_freshness.py` | Dashboard staleness < 5s | 5 |
| Q-053 | `tests/integration/test_schema_version.py` | Schema version parity | 5 |
| Q-060 | `tests/agents/test_g1_cost_tracker.py` | Cost ceiling assertion | 5 |

---

## Appendix B: Interaction-to-Test Mapping

Every INTERACTION-MAP interaction (I-NNN) must have test coverage in at least two layers: the service layer and at least one interface layer.

| Interaction | Service Test | MCP Test | REST Test | Dashboard Test | Parity Test |
|------------|-------------|----------|-----------|----------------|-------------|
| I-001 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | `test_parity.py::test_trigger_pipeline_parity` |
| I-002 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | Yes |
| I-003 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | Yes |
| I-004 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | Yes |
| I-005 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | Yes |
| I-006 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | Yes |
| I-007 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | Yes |
| I-008 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | Yes |
| I-009 | `test_pipeline_service.py` | `test_agents_server.py` | `test_pipeline_routes.py` | `test_pipeline_runs.py` | Yes |
| I-020 | `test_agent_service.py` | `test_agents_server.py` | `test_agent_routes.py` | `test_fleet_health.py` | `test_parity.py::test_list_agents_parity` |
| I-021 | `test_agent_service.py` | `test_agents_server.py` | `test_agent_routes.py` | `test_fleet_health.py` | Yes |
| I-022 | `test_agent_service.py` | `test_agents_server.py` | `test_agent_routes.py` | N/A (MCP-only) | Yes (MCP+REST) |
| I-023 | `test_agent_service.py` | `test_agents_server.py` | `test_agent_routes.py` | `test_fleet_health.py` | Yes |
| I-024 | `test_agent_service.py` | `test_agents_server.py` | `test_agent_routes.py` | `test_fleet_health.py` | Yes |
| I-025 | `test_agent_service.py` | `test_agents_server.py` | `test_agent_routes.py` | `test_fleet_health.py` | Yes |
| I-026 | `test_agent_service.py` | `test_agents_server.py` | `test_agent_routes.py` | `test_fleet_health.py` | Yes |
| I-027 | `test_agent_service.py` | `test_agents_server.py` | `test_agent_routes.py` | `test_fleet_health.py` | Yes |
| I-040 | `test_cost_service.py` | `test_governance_server.py` | `test_cost_routes.py` | `test_cost_monitor.py` | `test_parity.py::test_get_cost_report_parity` |
| I-041 | `test_cost_service.py` | `test_governance_server.py` | `test_cost_routes.py` | `test_cost_monitor.py` | Yes |
| I-042 | `test_audit_service.py` | `test_governance_server.py` | `test_audit_routes.py` | `test_audit_log.py` | `test_parity.py::test_query_audit_events_parity` |
| I-043 | `test_audit_service.py` | `test_governance_server.py` | `test_audit_routes.py` | `test_audit_log.py` | Yes |
| I-044 | `test_audit_service.py` | `test_governance_server.py` | `test_audit_routes.py` | `test_audit_log.py` | Yes |
| I-045 | `test_approval_service.py` | `test_governance_server.py` | `test_approval_routes.py` | `test_approval_queue.py` | `test_parity.py::test_list_pending_approvals_parity` |
| I-046 | `test_approval_service.py` | `test_governance_server.py` | `test_approval_routes.py` | `test_approval_queue.py` | Yes |
| I-047 | `test_approval_service.py` | `test_governance_server.py` | `test_approval_routes.py` | `test_approval_queue.py` | Yes |
| I-048 | `test_cost_service.py` | `test_governance_server.py` | `test_cost_routes.py` | `test_cost_monitor.py` | Yes |
| I-049 | `test_cost_service.py` | `test_governance_server.py` | `test_cost_routes.py` | `test_cost_monitor.py` | Yes |
| I-060 | `test_knowledge_service.py` | `test_knowledge_server.py` | `test_knowledge_routes.py` | N/A | Yes (MCP+REST) |
| I-061 | `test_knowledge_service.py` | `test_knowledge_server.py` | `test_knowledge_routes.py` | N/A | Yes |
| I-062 | `test_knowledge_service.py` | `test_knowledge_server.py` | `test_knowledge_routes.py` | N/A | Yes |
| I-063 | `test_knowledge_service.py` | `test_knowledge_server.py` | `test_knowledge_routes.py` | N/A | Yes |
| I-080 | `test_health_service.py` | `test_system_tools.py` | `test_system_routes.py` | `test_fleet_health.py` | Yes |
| I-081 | `test_health_service.py` | `test_system_tools.py` | `test_system_routes.py` | `test_fleet_health.py` | Yes |
| I-082 | `test_audit_service.py` | `test_system_tools.py` | `test_system_routes.py` | `test_fleet_health.py` | Yes |

---

*End of document. Generated using Full-Stack-First approach.*
