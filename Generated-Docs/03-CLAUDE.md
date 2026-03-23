# CLAUDE.md — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 3 of 14 | Status: Draft

> **Read this file before writing any code.** This is the single source of truth for how we build in this repository. Every contributor — human or AI — must follow these rules without exception. When this file conflicts with other documentation, this file wins.

---

## 1. Project

| Field        | Value                                                                   |
|--------------|-------------------------------------------------------------------------|
| **Name**     | Agentic SDLC Platform                                                   |
| **Purpose**  | Production-grade AI agent control plane for full software delivery lifecycle |
| **Tagline**  | "48 agents, 14 pipelines, 9 teams — governed, audited, cost-tracked"    |
| **Owner**    | Platform Team (2-3 developers)                                          |
| **Version**  | v0.1.0                                                                  |
| **Repo URL** | `agentic-sdlc` (main branch, ~800 files)                               |
| **Approach** | Full-Stack-First with 14+2 documents                                    |

---

## 2. Architecture

- **Python 3.12, Claude Agent SDK** — all agents use `from claude_agent_sdk import query, ClaudeAgentOptions` and extend `sdk/base_agent.py::BaseAgent`.
- **3 MCP Servers** (agents-server :3100, governance-server :3101, knowledge-server :3102) — primary AI interface; stdio transport for Claude Desktop, SSE for programmatic access.
- **aiohttp REST API** (:8080) — programmatic interface and dashboard backend; every MCP tool has a corresponding REST endpoint.
- **Streamlit Dashboard** (:8501) — human operator interface; consumes REST API exclusively, never imports services directly.
- **8 Shared Services** — THE business logic layer. MCP tool handlers and REST route handlers are thin wrappers that call these services. Business logic lives nowhere else.
- **PostgreSQL** (:5432) — persistence with Row-Level Security (RLS) for multi-tenancy; all access via async `asyncpg` through the service layer.
- **External integrations** — Claude API (Anthropic), Slack (notifications), PagerDuty (escalation).
- **SDK foundation** — BaseAgent, BaseHooks, ManifestLoader, SchemaValidator (complete) + 13 modules to build.

---

## 3. Repo Structure

```
agentic-sdlc/
├── mcp-servers/                        # MCP server implementations (3 servers)
│   ├── agents-server/                  # Agent execution + pipeline MCP server (:3100)
│   │   ├── __init__.py
│   │   ├── server.py                   # MCP server entry point (stdio + SSE transport)
│   │   └── tools/                      # Tool handlers (thin wrappers around services)
│   │       ├── __init__.py
│   │       ├── trigger_pipeline.py     # Calls PipelineService.trigger()
│   │       ├── list_agents.py          # Calls AgentService.list()
│   │       ├── invoke_agent.py         # Calls AgentService.invoke()
│   │       ├── get_pipeline_status.py  # Calls PipelineService.status()
│   │       └── agent_health.py         # Calls HealthService.agent_status()
│   ├── governance-server/              # Cost + audit + approval MCP server (:3101)
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── get_cost_report.py      # Calls CostService.get_report()
│   │       ├── check_budget.py         # Calls CostService.check_budget()
│   │       ├── query_audit.py          # Calls AuditService.query_events()
│   │       ├── create_approval.py      # Calls ApprovalService.create()
│   │       ├── approve_request.py      # Calls ApprovalService.approve()
│   │       └── reject_request.py       # Calls ApprovalService.reject()
│   └── knowledge-server/              # Knowledge management MCP server (:3102)
│       ├── __init__.py
│       ├── server.py
│       └── tools/
│           ├── __init__.py
│           ├── search_knowledge.py     # Calls KnowledgeService.search()
│           ├── create_exception.py     # Calls KnowledgeService.create()
│           └── promote_exception.py    # Calls KnowledgeService.promote()
├── api/                                # REST API (aiohttp, wraps shared services)
│   ├── __init__.py
│   ├── app.py                          # aiohttp application factory + startup/shutdown
│   ├── routes/                         # Route handlers (thin wrappers around services)
│   │   ├── __init__.py
│   │   ├── pipelines.py               # /api/v1/pipelines/* -> PipelineService
│   │   ├── agents.py                   # /api/v1/agents/* -> AgentService
│   │   ├── cost.py                     # /api/v1/cost/* -> CostService
│   │   ├── audit.py                    # /api/v1/audit/* -> AuditService
│   │   ├── approvals.py               # /api/v1/approvals/* -> ApprovalService
│   │   ├── knowledge.py               # /api/v1/knowledge/* -> KnowledgeService
│   │   ├── health.py                   # /api/v1/health/* -> HealthService
│   │   └── sessions.py                # /api/v1/sessions/* -> SessionService
│   └── middleware/                     # Auth, CORS, error handling, request logging
│       ├── __init__.py
│       ├── auth.py                     # API key validation middleware
│       ├── cors.py                     # CORS headers middleware
│       ├── error_handler.py            # Uniform error response formatting
│       └── request_logger.py           # structlog request/response logging
├── dashboard/                          # Streamlit operator dashboard
│   ├── app.py                          # Streamlit entry (multipage configuration)
│   ├── config.py                       # API_BASE, refresh intervals, theme settings
│   ├── components/                     # Reusable Streamlit components
│   │   ├── __init__.py
│   │   ├── sidebar.py                  # Navigation + fleet status summary
│   │   ├── metric_card.py             # Styled metric display
│   │   └── status_badge.py            # Agent/pipeline status indicator
│   └── pages/
│       ├── 01_fleet_health.py          # Fleet overview + agent status grid
│       ├── 02_cost_monitor.py          # Budget burn-down + cost alerts
│       ├── 03_pipeline_runs.py         # Pipeline execution history + live status
│       ├── 04_audit_log.py             # Searchable audit event stream
│       └── 05_approval_queue.py        # Pending approvals + approve/reject actions
├── services/                           # SHARED SERVICE LAYER (the core — ALL business logic)
│   ├── __init__.py
│   ├── pipeline_service.py             # trigger, status, list, resume, cancel
│   ├── agent_service.py                # list, get, invoke, health_check
│   ├── cost_service.py                 # get_report, check_budget, record_spend
│   ├── audit_service.py                # query_events, get_summary, record_event
│   ├── approval_service.py             # create, approve, reject, list_pending
│   ├── knowledge_service.py            # search, create, promote, list_exceptions
│   ├── health_service.py               # fleet_health, agent_status, component_status
│   └── session_service.py              # read, write, list, delete session context
├── sdk/                                # Agent SDK (foundation layer)
│   ├── __init__.py
│   ├── base_agent.py                   # COMPLETE — BaseAgent + BaseStatefulAgent
│   ├── base_hooks.py                   # COMPLETE — audit, cost, PII hooks
│   ├── manifest_loader.py              # COMPLETE — 4-layer resolution (agent->archetype->team->global)
│   ├── schema_validator.py             # COMPLETE — JSON Schema 2020-12 validation
│   ├── context/
│   │   ├── __init__.py
│   │   └── session_store.py            # TO BUILD (FIX-01, P1 BLOCKING)
│   ├── stores/
│   │   ├── __init__.py
│   │   └── postgres_cost_store.py      # TO BUILD (FIX-04, P1)
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── pipeline_runner.py          # STUB — wire to PipelineService (P3)
│   │   ├── team_orchestrator.py        # STUB — wire to AgentService (P3)
│   │   ├── approval_store.py           # TO BUILD (FIX-02, P2)
│   │   ├── checkpoint.py              # TO BUILD (FIX-03, P2)
│   │   └── self_heal.py               # TO BUILD (ADD-06, P4)
│   ├── enforcement/
│   │   ├── __init__.py
│   │   └── rate_limiter.py             # TO BUILD (FIX-09, P2)
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── quality_scorer.py           # TO BUILD (ADD-08, P4)
│   └── communication/
│       ├── __init__.py
│       ├── envelope.py                 # STUB — message envelope format
│       └── webhook.py                  # TO BUILD (ADD-01, P4)
├── agents/                             # 48 agent implementations
│   ├── govern/                         # G1-G5 governance agents
│   │   ├── G1-cost-tracker/            # GOLD STANDARD — copy this pattern exactly
│   │   │   ├── manifest.yaml           # Agent manifest (9 anatomy subsystems)
│   │   │   ├── prompt.md               # System prompt (Markdown)
│   │   │   ├── agent.py                # Agent implementation (extends BaseAgent)
│   │   │   ├── hooks.py                # Pre/post hooks (cost, audit, PII)
│   │   │   ├── tools.py                # Tool definitions for the agent
│   │   │   ├── rubric.yaml             # Evaluation rubric (required)
│   │   │   ├── __init__.py
│   │   │   └── tests/                  # Agent-specific tests
│   │   │       ├── test_agent.py
│   │   │       ├── golden/             # At least 3 golden tests (TC-001 through TC-003)
│   │   │       └── adversarial/        # At least 1 adversarial test (ADV-001)
│   │   ├── G2-budget-enforcer/
│   │   ├── G3-audit-logger/
│   │   ├── G4-approval-gate/
│   │   └── G5-compliance-checker/
│   └── claude-cc/                      # All non-governance agents
│       ├── D1-roadmap-generator/       # DESIGN phase
│       ├── D2-prd-generator/
│       ├── D3-feature-extractor/
│       ├── D4-enforcement-scaffolder/
│       ├── D5-architecture-drafter/
│       ├── D6-data-model-designer/
│       ├── D7-api-contract-generator/
│       ├── D8-backlog-builder/
│       ├── D9-design-spec-writer/
│       ├── D10-quality-spec-generator/
│       ├── D11-test-strategy-generator/
│       ├── B1-code-generator/          # BUILD phase
│       ├── B2-test-writer/
│       ├── B3-reviewer/
│       ├── T1-unit-runner/             # TEST phase
│       ├── T2-integration-runner/
│       ├── P1-deployer/                # DEPLOY phase
│       ├── O1-monitor/                 # OPERATE phase
│       └── OV-D1-scope-boundary-auditor/  # OVERSIGHT phase
├── schema/
│   ├── agent-manifest.schema.json      # COMPLETE (571 lines, JSON Schema 2020-12)
│   └── contracts/                      # 20 output contract schemas
│       ├── cost-report.schema.json
│       ├── audit-event.schema.json
│       ├── pipeline-run.schema.json
│       └── ...                         # 17 more contract schemas
├── archetypes/                         # 7 archetype YAMLs (shared agent configurations)
│   ├── ci-gate.yaml
│   ├── reviewer.yaml
│   ├── ops-agent.yaml
│   ├── discovery-agent.yaml
│   ├── co-pilot.yaml
│   ├── orchestrator.yaml
│   └── governance.yaml
├── teams/                              # 9 team workflows + 5 to build
│   ├── design-team.yaml
│   ├── build-team.yaml
│   ├── test-team.yaml
│   ├── deploy-team.yaml
│   ├── governance-team.yaml
│   ├── document-stack.yaml             # 12-doc pipeline definition
│   └── ...
├── migrations/                         # PostgreSQL migrations (sequential, idempotent)
│   ├── 001_create_agents.sql           # EXISTS — agent_registry table
│   ├── 002_create_audit_events.sql     # EXISTS — audit_events table
│   ├── 003_create_cost_metrics.sql     # EXISTS — cost_metrics table
│   ├── 004_create_pipeline_runs.sql    # EXISTS — pipeline_runs table
│   ├── 005_create_knowledge_exceptions.sql  # TO BUILD
│   ├── 006_create_approvals.sql        # TO BUILD
│   ├── 007_create_sessions.sql         # TO BUILD
│   └── 008_create_checkpoints.sql      # TO BUILD
├── knowledge/                          # 3-tier exception knowledge base
│   ├── universal/                      # Cross-project exceptions
│   ├── stack/                          # Stack-specific exceptions (python-fastapi, etc.)
│   └── client/                         # Client-specific exceptions
├── state/
│   └── MANIFEST.md                     # Source of truth for file status (update after every file change)
├── tests/
│   ├── conftest.py                     # Shared fixtures (db, services, test client)
│   ├── services/                       # Shared service tests (MOST tests live here)
│   │   ├── test_pipeline_service.py
│   │   ├── test_agent_service.py
│   │   ├── test_cost_service.py
│   │   ├── test_audit_service.py
│   │   ├── test_approval_service.py
│   │   ├── test_knowledge_service.py
│   │   ├── test_health_service.py
│   │   └── test_session_service.py
│   ├── mcp/                            # MCP tool handler tests
│   │   ├── test_agents_server.py
│   │   ├── test_governance_server.py
│   │   └── test_knowledge_server.py
│   ├── api/                            # REST route handler tests
│   │   ├── test_pipelines_routes.py
│   │   ├── test_agents_routes.py
│   │   ├── test_cost_routes.py
│   │   ├── test_audit_routes.py
│   │   ├── test_approvals_routes.py
│   │   └── test_knowledge_routes.py
│   ├── dashboard/                      # Dashboard component tests
│   ├── integration/                    # Cross-interface parity tests
│   │   └── test_mcp_api_parity.py      # Ensures MCP and REST return identical results
│   ├── golden/                         # Agent golden tests (input -> expected output)
│   └── adversarial/                    # Agent adversarial tests (edge cases, attacks)
├── .claude/                            # Claude Code enforcement configuration
│   ├── settings.json                   # Tool permissions, auto-approve patterns
│   └── rules/                          # Custom rules for Claude Code
├── .env.example                        # Environment variable template (never commit .env)
├── pyproject.toml                      # Project config (ruff, mypy, pytest settings)
├── Makefile                            # Development commands (make dev, make test, etc.)
├── docker-compose.yml                  # Local development stack (PostgreSQL, API, MCP, Dashboard)
└── CLAUDE.md                           # THIS FILE — read before writing any code
```

---

## 4. Language Rules — Python 3.12

These rules are **imperative and enforced**. Violations are caught by CI and must be fixed before merge.

### Type Hints

- Type hints on **ALL** function signatures — parameters and return types. No exceptions.
- Use `from __future__ import annotations` at the top of every module.
- Enforced by `mypy --strict` in CI.
- Prefer `str | None` over `Optional[str]` (Python 3.12 union syntax).
- Use `TypeAlias` for complex types; never inline complex generics more than once.
- Never use `# type: ignore` without a trailing explanation: `# type: ignore[arg-type] -- third-party stub missing`.

### Formatting and Linting

- **Ruff** for both linting and formatting — single tool, no separate flake8/black/isort.
- Line length: **120 characters** maximum.
- Indent: 4 spaces. No tabs.
- Import order: `stdlib` -> `third-party` -> `local` (enforced by ruff isort rules, I001/I002).
- Trailing commas on multi-line collections and function signatures.
- Never use `import *`. Always import specific names.
- Use absolute imports for SDK modules: `from sdk.base_agent import BaseAgent`, not relative imports.
- All ruff rules are configured in `pyproject.toml` under `[tool.ruff]`.

### Async / IO

- **asyncio for ALL I/O operations** — no synchronous database calls, no synchronous HTTP calls.
- Database access: `asyncpg` via SQLAlchemy async engine (`AsyncEngine`).
- HTTP client: `aiohttp.ClientSession` for outbound calls in services/API/MCP code.
- Never use `requests` in service layer or MCP/API code (only allowed in Streamlit dashboard).
- Never use `time.sleep()` — use `asyncio.sleep()` when delay is needed.
- Use `asyncio.gather()` for parallel execution (e.g., parallel pipeline steps).

### Data Validation

- **Pydantic v2** for all request/response models in the service layer.
- All service method inputs and outputs are Pydantic models or primitives — never raw dicts crossing service boundaries.
- Use `model_validator` for cross-field validation, not ad-hoc if-checks.

### Logging

- **structlog** for ALL logging — JSON format in production, console format in development.
- Never use `print()` in any production code path.
- Bind context (agent_id, pipeline_id, request_id) at the start of each operation.
- Log levels: `debug` for internal flow, `info` for business events, `warning` for recoverable issues, `error` for failures, `critical` for system-level failures.
- Every log entry in agent context must include: `agent_id`, `session_id`, `project_id`.

### Error Handling

- Never use bare `except:`. Always catch specific exception types.
- Raise domain-specific exceptions (e.g., `ManifestValidationError`, `BudgetExceededError`), not generic `Exception`.
- Never use `eval()` or `exec()` with untrusted input. Use structured parsing (JSON, YAML loaders).

### Testing

- **pytest** + **pytest-asyncio** for all tests.
- **testcontainers** for PostgreSQL in tests — always test against a real database, never mock the database.
- Never substitute SQLite for PostgreSQL in tests.
- Test files named `test_<module>.py` in the appropriate `tests/` subdirectory.
- Minimum coverage: 80% for services, 70% for MCP/API handlers, 90% for SDK modules.
- Every agent must pass `python -m pytest tests/test_<agent_id>.py -v` before moving to the next agent.
- Minimum 3 golden test cases per agent, minimum 1 adversarial test case per agent.

### Dependencies

- Pin all dependencies in `pyproject.toml` with minimum versions.
- Core: `claude-agent-sdk`, `aiohttp`, `asyncpg`, `sqlalchemy[asyncio]`, `pydantic>=2.0`, `structlog`, `streamlit`, `mcp`.
- Dev: `pytest`, `pytest-asyncio`, `testcontainers[postgres]`, `mypy`, `ruff`, `coverage`.

---

## 5. Implementation Patterns

Every feature in this platform follows these six patterns. The Shared Service pattern is the foundation — all other patterns depend on it.

### Pattern 1: Shared Service (THE CORE PATTERN)

Every feature is implemented as a shared service first. MCP and REST are thin wrappers. The service owns all business logic, validation, authorization, and database access. **If you build nothing else, build the service.**

```python
# services/pipeline_service.py
from __future__ import annotations

import structlog
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine

from sdk.context.session_store import SessionStore
from sdk.stores.postgres_cost_store import CostStore

logger = structlog.get_logger()


class PipelineRunRequest(BaseModel):
    project_id: str
    pipeline_name: str
    brief: str


class PipelineRun(BaseModel):
    id: str
    project_id: str
    pipeline_name: str
    status: str  # "pending" | "running" | "completed" | "failed" | "cancelled"
    created_at: str
    updated_at: str


class PipelineService:
    """Pipeline orchestration service.

    ALL pipeline business logic lives in this class.
    MCP tool handlers and API route handlers call these methods directly.
    They never implement business logic themselves.
    """

    def __init__(
        self,
        db: AsyncEngine,
        session_store: SessionStore,
        cost_store: CostStore,
    ) -> None:
        self.db = db
        self.session_store = session_store
        self.cost_store = cost_store

    async def trigger(
        self, project_id: str, pipeline_name: str, brief: str
    ) -> PipelineRun:
        """Trigger a new pipeline run.

        Validates budget, creates the run record, and starts execution.
        ALL business logic lives HERE — not in MCP handler, not in API route.
        """
        log = logger.bind(project_id=project_id, pipeline_name=pipeline_name)

        # 1. Check budget before starting
        budget_ok = await self.cost_store.check_budget(project_id, cost=25.0)
        if not budget_ok:
            log.warning("pipeline_budget_exceeded")
            raise BudgetExceededError(project_id)

        # 2. Create pipeline run record
        async with self.db.begin() as conn:
            result = await conn.execute(
                INSERT_PIPELINE_RUN,
                {"project_id": project_id, "name": pipeline_name, "brief": brief},
            )
            run_id = result.scalar_one()

        # 3. Record cost
        await self.cost_store.record_spend(
            project_id=project_id, category="pipeline", amount=25.0
        )

        log.info("pipeline_triggered", run_id=run_id)
        return PipelineRun(
            id=run_id,
            project_id=project_id,
            pipeline_name=pipeline_name,
            status="pending",
            created_at=now_iso(),
            updated_at=now_iso(),
        )

    async def status(self, run_id: str) -> PipelineRun:
        """Get current status of a pipeline run."""
        async with self.db.begin() as conn:
            row = await conn.execute(SELECT_PIPELINE_RUN, {"run_id": run_id})
            data = row.one()
        return PipelineRun(**data._mapping)

    async def list(self, project_id: str) -> list[PipelineRun]:
        """List all pipeline runs for a project."""
        async with self.db.begin() as conn:
            rows = await conn.execute(SELECT_PIPELINE_RUNS, {"project_id": project_id})
        return [PipelineRun(**row._mapping) for row in rows]

    async def resume(self, run_id: str) -> PipelineRun:
        """Resume a paused pipeline run (e.g., after approval)."""
        log = logger.bind(run_id=run_id)
        async with self.db.begin() as conn:
            await conn.execute(
                UPDATE_PIPELINE_STATUS, {"run_id": run_id, "status": "running"}
            )
        log.info("pipeline_resumed")
        return await self.status(run_id)

    async def cancel(self, run_id: str) -> PipelineRun:
        """Cancel a running pipeline."""
        log = logger.bind(run_id=run_id)
        async with self.db.begin() as conn:
            await conn.execute(
                UPDATE_PIPELINE_STATUS, {"run_id": run_id, "status": "cancelled"}
            )
        log.info("pipeline_cancelled")
        return await self.status(run_id)
```

### Pattern 2: MCP Tool Handler (thin wrapper calling service)

MCP tool handlers have **ZERO** business logic. They parse MCP parameters, call the shared service, and format the response for MCP protocol. That is all.

```python
# mcp-servers/agents-server/tools/trigger_pipeline.py
from __future__ import annotations

from mcp.types import Tool, TextContent

from services.pipeline_service import PipelineService


TOOL_DEFINITION = Tool(
    name="trigger_pipeline",
    description="Trigger a new pipeline run for a project",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Project identifier"},
            "pipeline_name": {"type": "string", "description": "Pipeline to trigger"},
            "brief": {"type": "string", "description": "Brief describing what to build"},
        },
        "required": ["project_id", "pipeline_name", "brief"],
    },
)


async def handle_trigger_pipeline(
    params: dict, service: PipelineService
) -> list[TextContent]:
    """MCP tool handler — thin wrapper, ZERO business logic.

    1. Extract params from MCP call
    2. Call shared service
    3. Return MCP-formatted response
    Nothing else.
    """
    result = await service.trigger(
        project_id=params["project_id"],
        pipeline_name=params["pipeline_name"],
        brief=params["brief"],
    )
    return [TextContent(type="text", text=result.model_dump_json())]
```

### Pattern 3: API Route Handler (thin wrapper calling SAME service)

API routes have **ZERO** business logic. They parse the HTTP request, call the **same shared service** as MCP, and format the HTTP response. That is all.

```python
# api/routes/pipelines.py
from __future__ import annotations

from aiohttp import web

from services.pipeline_service import PipelineService


def setup_routes(app: web.Application) -> None:
    app.router.add_post("/api/v1/pipelines", post_pipelines)
    app.router.add_get("/api/v1/pipelines/{run_id}", get_pipeline)
    app.router.add_get("/api/v1/pipelines", list_pipelines)
    app.router.add_post("/api/v1/pipelines/{run_id}/resume", resume_pipeline)
    app.router.add_post("/api/v1/pipelines/{run_id}/cancel", cancel_pipeline)


async def post_pipelines(request: web.Request) -> web.Response:
    """POST /api/v1/pipelines — trigger a new pipeline run.

    API route handler — thin wrapper, ZERO business logic.
    Calls the SAME PipelineService that MCP uses.
    """
    body = await request.json()
    service: PipelineService = request.app["pipeline_service"]
    result = await service.trigger(
        project_id=body["project_id"],
        pipeline_name=body["pipeline_name"],
        brief=body["brief"],
    )
    return web.json_response(
        {"data": result.model_dump(), "status": "ok"},
        status=201,
    )


async def get_pipeline(request: web.Request) -> web.Response:
    """GET /api/v1/pipelines/{run_id} — get pipeline status."""
    run_id = request.match_info["run_id"]
    service: PipelineService = request.app["pipeline_service"]
    result = await service.status(run_id)
    return web.json_response({"data": result.model_dump(), "status": "ok"})


async def list_pipelines(request: web.Request) -> web.Response:
    """GET /api/v1/pipelines — list pipeline runs."""
    project_id = request.query.get("project_id", "")
    service: PipelineService = request.app["pipeline_service"]
    results = await service.list(project_id)
    return web.json_response(
        {"data": [r.model_dump() for r in results], "status": "ok"}
    )


async def resume_pipeline(request: web.Request) -> web.Response:
    """POST /api/v1/pipelines/{run_id}/resume — resume paused pipeline."""
    run_id = request.match_info["run_id"]
    service: PipelineService = request.app["pipeline_service"]
    result = await service.resume(run_id)
    return web.json_response({"data": result.model_dump(), "status": "ok"})


async def cancel_pipeline(request: web.Request) -> web.Response:
    """POST /api/v1/pipelines/{run_id}/cancel — cancel running pipeline."""
    run_id = request.match_info["run_id"]
    service: PipelineService = request.app["pipeline_service"]
    result = await service.cancel(run_id)
    return web.json_response({"data": result.model_dump(), "status": "ok"})
```

### Pattern 4: Dashboard View (consumes REST API only)

Dashboard pages **NEVER** import services directly. They call the REST API over HTTP. This ensures the dashboard can run as a separate process with no shared memory.

```python
# dashboard/pages/03_pipeline_runs.py
from __future__ import annotations

import streamlit as st
import requests
from dashboard.config import API_BASE


st.set_page_config(page_title="Pipeline Runs", page_icon="*")
st.title("Pipeline Runs")

# ---------------------------------------------------------------
# Dashboard calls REST API — NEVER imports service directly
# ---------------------------------------------------------------
response = requests.get(f"{API_BASE}/api/v1/pipelines")
response.raise_for_status()
pipelines = response.json()["data"]

# Display pipeline runs
if pipelines:
    st.dataframe(
        pipelines,
        column_config={
            "id": st.column_config.TextColumn("Run ID"),
            "pipeline_name": st.column_config.TextColumn("Pipeline"),
            "status": st.column_config.TextColumn("Status"),
            "created_at": st.column_config.DatetimeColumn("Started"),
        },
        use_container_width=True,
    )
else:
    st.info("No pipeline runs found.")

# Trigger new pipeline
with st.form("trigger_pipeline"):
    st.subheader("Trigger New Pipeline")
    project_id = st.text_input("Project ID")
    pipeline_name = st.selectbox(
        "Pipeline",
        ["design-build-test", "review-deploy", "full-sdlc", "document-stack"],
    )
    brief = st.text_area("Brief")
    submitted = st.form_submit_button("Trigger")

    if submitted and project_id and brief:
        trigger_resp = requests.post(
            f"{API_BASE}/api/v1/pipelines",
            json={
                "project_id": project_id,
                "pipeline_name": pipeline_name,
                "brief": brief,
            },
        )
        if trigger_resp.ok:
            st.success(f"Pipeline triggered: {trigger_resp.json()['data']['id']}")
            st.rerun()
        else:
            st.error(f"Failed: {trigger_resp.text}")
```

### Pattern 5: Agent (follow G1-cost-tracker gold standard)

Every agent consists of exactly 7 files + a tests directory. Copy this structure exactly for every new agent.

**Build order (mandatory):**
1. Write `manifest.yaml` (all 9 subsystems)
2. Validate: `python -m sdk.schema_validator agents/{phase}/{id}/manifest.yaml`
3. Write `prompt.md`
4. Write `agent.py` (extends BaseAgent)
5. Write `hooks.py` (extends BaseHooks)
6. Write `tools.py` (TOOL_SCHEMAS + handlers)
7. Write `rubric.yaml`
8. Write tests in `tests/golden/` (min 3) and `tests/adversarial/` (min 1)
9. Run: `python -m pytest tests/test_<agent_id>.py -v` — must pass
10. Update `state/MANIFEST.md`

**manifest.yaml** — Must contain all 9 anatomy subsystems. Must validate against `schema/agent-manifest.schema.json`.

```yaml
# agents/govern/G1-cost-tracker/manifest.yaml
agent:
  id: G1-cost-tracker
  name: Cost Tracker
  version: "1.0.0"
  archetype: enforcer

# Subsystem 1: Identity
identity:
  role: "Cost tracking and budget enforcement agent"
  domain: governance
  team: governance-team
  owner: platform-team
  phase: govern
  tags: [cost, budget, enforcement, governance]

# Subsystem 2: Capabilities
capabilities:
  tools:
    - name: get_cost_report
      description: "Retrieve cost report for a project or agent"
    - name: check_budget
      description: "Check remaining budget for a scope"
    - name: record_spend
      description: "Record token/API spend for an invocation"
  modes: [generate, review, score]

# Subsystem 3: Constraints
constraints:
  max_tokens_per_invocation: 4096
  max_cost_per_invocation: 0.50
  timeout_seconds: 30
  rate_limit: "60/minute"

# Subsystem 4: Knowledge
knowledge:
  context_sources:
    - type: session
      key: "cost_history"
    - type: universal
      path: "knowledge/universal/cost-rules.yaml"

# Subsystem 5: Communication
communication:
  input_contract: "schema/contracts/cost-query.schema.json"
  output_contract: "schema/contracts/cost-report.schema.json"
  escalation:
    - condition: "budget_exceeded"
      target: "G2-budget-enforcer"
      channel: "slack"

# Subsystem 6: Governance
governance:
  audit: true
  cost_tracking: true
  pii_filter: true
  approval_required: false
  autonomy_tier: T0

# Subsystem 7: Evaluation
evaluation:
  rubric: "rubric.yaml"
  golden_tests: 3
  adversarial_tests: 1

# Subsystem 8: Lifecycle
lifecycle:
  status: active
  created: "2026-03-01"
  last_validated: "2026-03-24"

# Subsystem 9: Deployment
deployment:
  mcp_server: governance-server
  rest_endpoint: "/api/v1/cost"
  health_check: "/api/v1/health/agents/G1-cost-tracker"
```

**prompt.md** — System prompt for the agent.

```markdown
# G1-cost-tracker — Cost Tracking Agent

You are G1-cost-tracker, the Cost Tracking agent for the Agentic SDLC Platform.

## Role
Track and report costs for all agent invocations, pipeline runs, and API calls.
Enforce budget limits at fleet, project, and agent scopes.

## Rules
1. Always check budget BEFORE approving any spend.
2. Block on database errors — never fail-open on cost tracking.
3. Report costs in USD with 4 decimal places.
4. Escalate to G2-budget-enforcer when any scope reaches 80% budget.

## Output Format
Always return a CostReport matching schema/contracts/cost-report.schema.json.
```

**agent.py** — Agent implementation.

```python
# agents/govern/G1-cost-tracker/agent.py
from __future__ import annotations

from claude_agent_sdk import query, ClaudeAgentOptions
from sdk.base_agent import BaseAgent
from .hooks import CostTrackerHooks
from .tools import TOOLS


class CostTrackerAgent(BaseAgent):
    """G1-cost-tracker: Cost tracking and budget enforcement."""

    agent_id = "G1-cost-tracker"

    def __init__(self) -> None:
        super().__init__(
            manifest_path="agents/govern/G1-cost-tracker/manifest.yaml",
            hooks=CostTrackerHooks(),
            tools=TOOLS,
        )

    async def invoke(self, input_data: dict) -> dict:
        """Execute cost tracking query."""
        prompt = self.build_prompt(input_data)
        options = ClaudeAgentOptions(
            max_tokens=self.manifest.constraints.max_tokens_per_invocation,
            tools=self.tool_definitions,
        )
        result = await query(prompt=prompt, options=options)
        return self.parse_output(result)
```

**hooks.py** — Pre/post execution hooks.

```python
# agents/govern/G1-cost-tracker/hooks.py
from __future__ import annotations

from sdk.base_hooks import BaseHooks, HookContext
import structlog

logger = structlog.get_logger()


class CostTrackerHooks(BaseHooks):
    """Hooks for G1-cost-tracker agent."""

    async def pre_invoke(self, ctx: HookContext) -> HookContext:
        """Validate budget before invocation."""
        logger.info("cost_tracker_pre_invoke", agent_id="G1-cost-tracker")
        ctx = await self.audit_hook(ctx)
        ctx = await self.cost_check_hook(ctx)
        ctx = await self.pii_filter_hook(ctx)
        return ctx

    async def post_invoke(self, ctx: HookContext) -> HookContext:
        """Record spend after invocation."""
        logger.info("cost_tracker_post_invoke", agent_id="G1-cost-tracker")
        ctx = await self.record_cost_hook(ctx)
        ctx = await self.audit_complete_hook(ctx)
        return ctx
```

**tools.py** — Tool definitions available to the agent.

```python
# agents/govern/G1-cost-tracker/tools.py
from __future__ import annotations

TOOLS = [
    {
        "name": "get_cost_report",
        "description": "Retrieve cost report for a given scope (fleet/project/agent)",
        "input_schema": {
            "type": "object",
            "properties": {
                "scope": {"type": "string", "enum": ["fleet", "project", "agent"]},
                "scope_id": {"type": "string"},
                "period": {"type": "string", "enum": ["day", "week", "month"]},
            },
            "required": ["scope", "scope_id"],
        },
    },
    {
        "name": "check_budget",
        "description": "Check remaining budget for a scope",
        "input_schema": {
            "type": "object",
            "properties": {
                "scope": {"type": "string", "enum": ["fleet", "project", "agent"]},
                "scope_id": {"type": "string"},
            },
            "required": ["scope", "scope_id"],
        },
    },
    {
        "name": "record_spend",
        "description": "Record a cost entry for an agent invocation",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string"},
                "project_id": {"type": "string"},
                "amount_usd": {"type": "number"},
                "token_count": {"type": "integer"},
                "description": {"type": "string"},
            },
            "required": ["agent_id", "project_id", "amount_usd"],
        },
    },
]
```

**rubric.yaml** — Evaluation rubric (required for every agent).

```yaml
# agents/govern/G1-cost-tracker/rubric.yaml
rubric:
  agent_id: G1-cost-tracker
  version: "1.0.0"
  dimensions:
    accuracy:
      weight: 0.30
      criteria:
        - "Cost figures match database records within 0.01 USD"
        - "Budget percentages calculated correctly"
        - "Time period filtering is accurate"
    completeness:
      weight: 0.25
      criteria:
        - "All requested scopes included in report"
        - "Breakdown by agent and pipeline provided"
        - "Trend data included when period > 1 day"
    safety:
      weight: 0.25
      criteria:
        - "Never fails open — blocks on DB error"
        - "Escalates at 80% budget threshold"
        - "No PII in cost report output"
    format:
      weight: 0.20
      criteria:
        - "Output matches cost-report.schema.json"
        - "USD amounts have 4 decimal places"
        - "ISO 8601 timestamps throughout"
```

### Pattern 6: Migration

```sql
-- migrations/005_create_knowledge_exceptions.sql
-- Knowledge exception tables for 3-tier exception system
-- Depends on: 001_create_agents.sql

BEGIN;

CREATE TABLE IF NOT EXISTS knowledge_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tier TEXT NOT NULL CHECK (tier IN ('universal', 'stack', 'client')),
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    resolution TEXT,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    stack TEXT,               -- NULL for universal tier
    client_id TEXT,           -- NULL for universal and stack tiers
    promoted_from UUID REFERENCES knowledge_exceptions(id),
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_knowledge_exceptions_tier ON knowledge_exceptions(tier);
CREATE INDEX idx_knowledge_exceptions_category ON knowledge_exceptions(category);
CREATE INDEX idx_knowledge_exceptions_stack ON knowledge_exceptions(stack) WHERE stack IS NOT NULL;
CREATE INDEX idx_knowledge_exceptions_client ON knowledge_exceptions(client_id) WHERE client_id IS NOT NULL;
CREATE INDEX idx_knowledge_exceptions_severity ON knowledge_exceptions(severity);

-- RLS for multi-tenancy
ALTER TABLE knowledge_exceptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY knowledge_read_policy ON knowledge_exceptions
    FOR SELECT USING (
        tier = 'universal'
        OR (tier = 'stack' AND stack = current_setting('app.current_stack', true))
        OR (tier = 'client' AND client_id = current_setting('app.current_client', true))
    );

COMMIT;
```

---

## 6. Key Reference Tables

### 6.1 MCP Server Inventory

| Server              | Port | Transport    | Tool Count | Service Dependencies                                    |
|---------------------|------|-------------|------------|----------------------------------------------------------|
| agents-server       | 3100 | stdio + SSE | 5          | PipelineService, AgentService, HealthService             |
| governance-server   | 3101 | stdio + SSE | 6          | CostService, AuditService, ApprovalService               |
| knowledge-server    | 3102 | stdio + SSE | 3          | KnowledgeService                                         |

### 6.2 Dashboard View Inventory

| Page                   | File                        | REST Endpoints Consumed                                          |
|------------------------|-----------------------------|------------------------------------------------------------------|
| Fleet Health           | `01_fleet_health.py`        | `GET /api/v1/health/fleet`, `GET /api/v1/agents`                |
| Cost Monitor           | `02_cost_monitor.py`        | `GET /api/v1/cost/report`, `GET /api/v1/cost/budget`            |
| Pipeline Runs          | `03_pipeline_runs.py`       | `GET /api/v1/pipelines`, `POST /api/v1/pipelines`               |
| Audit Log              | `04_audit_log.py`           | `GET /api/v1/audit/events`, `GET /api/v1/audit/summary`         |
| Approval Queue         | `05_approval_queue.py`      | `GET /api/v1/approvals/pending`, `POST /api/v1/approvals/{id}/*`|

### 6.3 Shared Service Inventory

| Service            | File                      | Method Count | Methods                                   | Primary Consumers                           |
|--------------------|---------------------------|--------------|--------------------------------------------|---------------------------------------------|
| PipelineService    | `pipeline_service.py`     | 5            | trigger, status, list, resume, cancel      | agents-server, API /pipelines, Dashboard    |
| AgentService       | `agent_service.py`        | 4            | list, get, invoke, health_check            | agents-server, API /agents, Dashboard       |
| CostService        | `cost_service.py`         | 3            | get_report, check_budget, record_spend     | governance-server, API /cost, Dashboard     |
| AuditService       | `audit_service.py`        | 3            | query_events, get_summary, record_event    | governance-server, API /audit, Dashboard    |
| ApprovalService    | `approval_service.py`     | 4            | create, approve, reject, list_pending      | governance-server, API /approvals, Dashboard|
| KnowledgeService   | `knowledge_service.py`    | 4            | search, create, promote, list_exceptions   | knowledge-server, API /knowledge            |
| HealthService      | `health_service.py`       | 3            | fleet_health, agent_status, component_status| agents-server, API /health, Dashboard      |
| SessionService     | `session_service.py`      | 4            | read, write, list, delete                  | Internal (SDK, pipeline runner)             |

### 6.4 REST API Endpoint Inventory

| Method | Endpoint                                       | Service             | Route File             |
|--------|-------------------------------------------------|---------------------|------------------------|
| POST   | `/api/v1/pipelines`                             | PipelineService     | `routes/pipelines.py`  |
| GET    | `/api/v1/pipelines`                             | PipelineService     | `routes/pipelines.py`  |
| GET    | `/api/v1/pipelines/{id}`                        | PipelineService     | `routes/pipelines.py`  |
| POST   | `/api/v1/pipelines/{id}/resume`                 | PipelineService     | `routes/pipelines.py`  |
| POST   | `/api/v1/pipelines/{id}/cancel`                 | PipelineService     | `routes/pipelines.py`  |
| GET    | `/api/v1/agents`                                | AgentService        | `routes/agents.py`     |
| GET    | `/api/v1/agents/{id}`                           | AgentService        | `routes/agents.py`     |
| POST   | `/api/v1/agents/{id}/invoke`                    | AgentService        | `routes/agents.py`     |
| GET    | `/api/v1/agents/{id}/health`                    | AgentService        | `routes/agents.py`     |
| GET    | `/api/v1/cost/report`                           | CostService         | `routes/cost.py`       |
| GET    | `/api/v1/cost/budget`                           | CostService         | `routes/cost.py`       |
| POST   | `/api/v1/cost/spend`                            | CostService         | `routes/cost.py`       |
| GET    | `/api/v1/audit/events`                          | AuditService        | `routes/audit.py`      |
| GET    | `/api/v1/audit/summary`                         | AuditService        | `routes/audit.py`      |
| POST   | `/api/v1/approvals`                             | ApprovalService     | `routes/approvals.py`  |
| GET    | `/api/v1/approvals/pending`                     | ApprovalService     | `routes/approvals.py`  |
| POST   | `/api/v1/approvals/{id}/approve`                | ApprovalService     | `routes/approvals.py`  |
| POST   | `/api/v1/approvals/{id}/reject`                 | ApprovalService     | `routes/approvals.py`  |
| GET    | `/api/v1/knowledge/search`                      | KnowledgeService    | `routes/knowledge.py`  |
| POST   | `/api/v1/knowledge/exceptions`                  | KnowledgeService    | `routes/knowledge.py`  |
| POST   | `/api/v1/knowledge/exceptions/{id}/promote`     | KnowledgeService    | `routes/knowledge.py`  |
| GET    | `/api/v1/health/fleet`                          | HealthService       | `routes/health.py`     |
| GET    | `/api/v1/health/agents/{id}`                    | HealthService       | `routes/health.py`     |

### 6.5 Archetypes

| Archetype          | Best For                          | Model         | Temperature | Key Traits                              |
|--------------------|-----------------------------------|---------------|-------------|------------------------------------------|
| `ci-gate`          | T3, T1, B8                        | haiku         | 0.0         | Fast, deterministic, binary pass/fail    |
| `reviewer`         | B1, B3, B4, OV-*                  | opus          | 0.1         | Deep analysis, high confidence           |
| `ops-agent`        | O1, O2, O3                        | opus          | 0.0         | Incident response, sandbox-enabled       |
| `discovery-agent`  | DS1-DS4                           | sonnet        | 0.3         | Multi-turn, conversational, exploration  |
| `co-pilot`         | D1-D11, B2                        | opus/sonnet   | 0.2         | File-writing, session state, interactive |
| `orchestrator`     | G4, OV-U1, team-spawner           | sonnet        | 0.1         | Spawns subagents, complex routing        |
| `governance`       | G1, G2, G3                        | haiku         | 0.0         | Monitoring, audit, cost control          |

### 6.6 Autonomy Tiers

| Tier | Name              | Approval Required       | Use Case                          |
|------|-------------------|-------------------------|-----------------------------------|
| T0   | Full Auto         | None                    | Cost tracking, linting, metrics   |
| T1   | Notify            | None, but notifies      | Code generation, doc generation   |
| T2   | Approve on Risk   | If confidence < 0.7     | Architecture decisions, reviews   |
| T3   | Always Approve    | Every action            | Production deploys, rollbacks     |

### 6.7 PostgreSQL Tables

| Table                   | Migration | Status    | Purpose                                     |
|-------------------------|-----------|-----------|----------------------------------------------|
| `agent_registry`        | 001       | EXISTS    | Agent metadata, versions, status             |
| `audit_events`          | 002       | EXISTS    | Immutable audit trail (append-only)          |
| `cost_metrics`          | 003       | EXISTS    | Token usage, USD spend per invocation        |
| `pipeline_runs`         | 004       | EXISTS    | Pipeline execution state and history         |
| `knowledge_exceptions`  | 005       | TO BUILD  | Knowledge promotion exceptions               |
| `approval_requests`     | 006       | TO BUILD  | HITL approval gate records                   |
| `session_context`       | 007       | TO BUILD  | Shared agent session state                   |
| `pipeline_checkpoints`  | 008       | TO BUILD  | Checkpoint/resume state                      |

### 6.8 Environment Variables

| Variable                         | Required | Default            | Purpose                               |
|----------------------------------|----------|--------------------|---------------------------------------|
| `ANTHROPIC_API_KEY`              | Yes*     | --                 | Claude API authentication (* only to RUN agents) |
| `DATABASE_URL`                   | Yes      | --                 | PostgreSQL connection string (asyncpg) |
| `SLACK_WEBHOOK_URL`              | No       | --                 | Slack notification endpoint            |
| `PAGERDUTY_INTEGRATION_KEY`      | No       | --                 | PagerDuty escalation integration       |
| `API_HOST`                       | No       | `0.0.0.0`         | REST API bind host                     |
| `API_PORT`                       | No       | `8080`             | REST API port                          |
| `MCP_AGENTS_PORT`                | No       | `3100`             | MCP agents-server port (SSE mode)      |
| `MCP_GOVERNANCE_PORT`            | No       | `3101`             | MCP governance-server port (SSE mode)  |
| `MCP_KNOWLEDGE_PORT`             | No       | `3102`             | MCP knowledge-server port (SSE mode)   |
| `DASHBOARD_PORT`                 | No       | `8501`             | Streamlit dashboard port               |
| `API_BASE`                       | No       | `http://localhost:8080` | Dashboard -> REST API base URL    |
| `BUDGET_FLEET_DAILY`             | No       | `50.00`            | Fleet-wide daily spend ceiling (USD)   |
| `BUDGET_PROJECT_DAILY`           | No       | `20.00`            | Per-project daily spend ceiling (USD)  |
| `BUDGET_AGENT_DAILY`             | No       | `5.00`             | Per-agent daily spend ceiling (USD)    |
| `BUDGET_INVOCATION_MAX`          | No       | `0.50`             | Per-invocation spend ceiling (USD)     |
| `BUDGET_PIPELINE_MAX`            | No       | `25.00`            | Per-pipeline-run spend ceiling (USD)   |
| `LOG_LEVEL`                      | No       | `INFO`             | structlog log level                    |
| `LOG_FORMAT`                     | No       | `json`             | "json" for production, "console" for dev |
| `ENVIRONMENT`                    | No       | `dev`              | Runtime environment (dev/staging/prod) |

---

## 7. Key Commands

```bash
# ============================================================
# FULL STACK — Start everything
# ============================================================
make dev                                    # Start MCP + API + Dashboard + PostgreSQL (docker-compose)
make down                                   # Stop all services

# ============================================================
# INDIVIDUAL SERVICES
# ============================================================
python -m mcp_servers.agents                # MCP agents-server (stdio transport)
python -m mcp_servers.governance            # MCP governance-server (stdio transport)
python -m mcp_servers.knowledge             # MCP knowledge-server (stdio transport)
python -m api.app                           # REST API (port 8080)
streamlit run dashboard/app.py              # Dashboard (port 8501)

# ============================================================
# DATABASE
# ============================================================
make db-up                                  # Start PostgreSQL only
make db-migrate                             # Run all pending migrations
make db-reset                               # Drop + recreate + migrate (DESTRUCTIVE)
psql -h localhost -p 5432 -U agentic -d agentic_sdlc   # Direct DB access

# ============================================================
# TESTING — Run in this order for fastest feedback
# ============================================================
pytest tests/services/ -v                   # 1. Shared service tests (run FIRST — core logic)
pytest tests/mcp/ -v                        # 2. MCP tool handler tests
pytest tests/api/ -v                        # 3. REST API route tests
pytest tests/dashboard/ -v                  # 4. Dashboard component tests
pytest tests/integration/ -v                # 5. Cross-interface parity tests
pytest tests/ -v                            # ALL tests

# Single test file
pytest tests/services/test_cost_service.py -v
pytest tests/services/test_pipeline_service.py::test_trigger_checks_budget -v

# Test with coverage
pytest tests/ -v --cov=services --cov=sdk --cov-report=term-missing
pytest tests/ -v --cov=services --cov-fail-under=80

# ============================================================
# AGENT TESTING
# ============================================================
pytest tests/test_G1-cost-tracker.py -v                     # Single agent test suite
pytest tests/golden/ -v                                      # All golden tests
pytest tests/adversarial/ -v                                 # All adversarial tests
python -m sdk.schema_validator agents/govern/G1-cost-tracker/manifest.yaml  # Validate manifest

# ============================================================
# CODE QUALITY
# ============================================================
ruff check .                                # Lint all files
ruff format .                               # Format all files
ruff check --fix .                          # Auto-fix linting issues
mypy --strict services/ sdk/ api/ mcp-servers/   # Type checking (strict)

# ============================================================
# MCP DEVELOPMENT
# ============================================================
mcp dev mcp-servers/agents-server/server.py     # MCP Inspector for agents-server
mcp dev mcp-servers/governance-server/server.py # MCP Inspector for governance-server
mcp dev mcp-servers/knowledge-server/server.py  # MCP Inspector for knowledge-server

# ============================================================
# AGENT DRY RUN (no API key needed)
# ============================================================
python -m agents.govern.G1-cost-tracker.agent --dry-run

# ============================================================
# GIT WORKFLOW (commit every 3 files)
# ============================================================
git add -p && git commit -m "feat: <what you built>"
git add -p && git commit -m "fix: <what you fixed>"
git add -p && git commit -m "test: <what you tested>"
```

---

## 8. Pipelines / Workflows

### Flow 1: MCP (AI Client Interface)

```
AI Client (Claude Desktop / IDE)
    |
    v
MCP Server (stdio/SSE transport)
    |  Parse tool call, extract parameters
    v
Tool Handler (thin wrapper — ZERO logic)
    |  Call shared service method
    v
Shared Service (ALL business logic)
    |  Validate -> Execute -> Audit -> Cost-track
    v
PostgreSQL (asyncpg)
    |
    v
Response flows back:  DB -> Service -> Tool Handler -> MCP Server -> AI Client
```

### Flow 2: REST API (Programmatic Interface)

```
HTTP Client (curl / SDK / Dashboard)
    |
    v
aiohttp Middleware (auth -> CORS -> logging)
    |
    v
Route Handler (thin wrapper — ZERO logic)
    |  Call shared service method (SAME service as MCP)
    v
Shared Service (ALL business logic)
    |  Validate -> Execute -> Audit -> Cost-track
    v
PostgreSQL (asyncpg)
    |
    v
Response flows back:  DB -> Service -> Route Handler -> Middleware -> HTTP Response
```

### Flow 3: Dashboard (Human Operator Interface)

```
Browser (Human Operator)
    |
    v
Streamlit Dashboard (port 8501)
    |  HTTP request to REST API (requests library)
    v
REST API (port 8080)
    |  Route handler -> Shared service (same flow as Flow 2)
    v
Shared Service -> PostgreSQL
    |
    v
Response flows back:  DB -> Service -> API -> HTTP -> Streamlit -> Browser render
```

### Flow 4: Cross-Interface (MCP trigger, Dashboard observe)

```
AI Client                          Human Operator
    |                                    |
    v                                    |
MCP: trigger_pipeline()                  |
    |                                    |
    v                                    |
PipelineService.trigger()                |
    |                                    |
    v                                    |
PostgreSQL (run record created)          |
    |                                    |
    |    +-------------------------------+
    |    |  (Dashboard polls every 5s)
    |    v
    |  REST API: GET /api/v1/pipelines
    |    |
    |    v
    |  PipelineService.list()
    |    |
    |    v
    |  PostgreSQL (reads same record)
    |    |
    |    v
    |  Dashboard renders pipeline status
    |
    v
MCP returns run_id to AI Client
```

### Flow 5: Agent Invocation Pipeline

```
Pipeline triggered (via MCP or REST)
    |
    v
PipelineService.trigger()
    |  Create run record, check budget
    v
PipelineRunner.execute()
    |  Load pipeline YAML, resolve agent sequence
    v
For each agent in pipeline:
    +-- AgentService.invoke(agent_id, input)
    |      |
    |      v
    |  BaseAgent.invoke()
    |      |
    |      +-- pre_invoke hooks (audit, cost-check, PII)
    |      +-- claude_agent_sdk.query() <-- API key needed HERE
    |      +-- post_invoke hooks (record cost, audit complete)
    |      +-- Return validated output (against contract schema)
    |
    +-- Check: approval required?
    |      YES -> ApprovalService.create() -> PAUSE pipeline
    |      NO  -> Continue to next agent
    |
    +-- Feed output as input to next agent
         |
         v
Pipeline complete -> PipelineService.update(status="completed")
```

### Flow 6: 12-Document Pipeline

```
Client Brief
  |
  v
D1-roadmap-generator ---------> requirements_doc
  |
  v
claude-md-generator -----------> project CLAUDE.md
  |
  v
D2-prd-generator --------------> prd_doc
  |
  v
D3-feature-extractor ----------> feature_catalog
  |
  v
D8-backlog-builder ------------> task_list
  |
  v
D5-architecture-drafter -------> architecture_doc
  |
  +--[ parallel ]---------+
  |                        |
  v                        v
D6-data-model-designer   D7-api-contract-generator
  |                        |
  v                        v
db_schema                api_contracts
  |                        |
  +----------+-------------+
             |
             v
D4-enforcement-scaffolder ----> enforcement_scaffold
  |
  +--[ parallel ]---------+
  |                        |
  v                        v
D10-quality-spec         D11-test-strategy
  |                        |
  v                        v
quality_spec             test_strategy
  |                        |
  +----------+-------------+
             |
             v
D9-design-spec-writer --------> design_spec (reads ALL prior outputs)
  |
  v
reports/{project_id}/           # 12 deliverable files
```

**Pipeline rules:**
- Team YAML: `teams/document-stack.yaml`
- Cost ceiling: $25.00 per full run
- Context strategy: accumulate (each agent sees all prior session keys)
- Gate logic: each step requires `pass` from the previous step
- Confidence halt: if any agent returns `confidence < 0.5`, pipeline halts for human review
- Parallel execution: D6+D7 and D10+D11 run via `asyncio.gather()`

---

## 9. Cost / Budget

### 9.1 Budget Limits

| Scope       | Limit       | Enforcement Point      | On Exceed                               |
|-------------|-------------|------------------------|-----------------------------------------|
| Fleet       | $50/day     | CostService            | Block ALL new invocations fleet-wide    |
| Project     | $20/day     | CostService            | Block new invocations for that project  |
| Agent       | $5/day      | CostService            | Block that agent, escalate to G2        |
| Invocation  | $0.50/call  | BaseAgent pre_invoke   | Reject invocation immediately           |
| Pipeline    | $25/run     | PipelineService        | Block pipeline trigger                  |

### 9.2 Cost Tracking Rules

1. **Every agent invocation** records cost via `CostService.record_spend()` in the `post_invoke` hook.
2. **Every pipeline trigger** checks budget via `CostService.check_budget()` before starting.
3. **Budget checks are pre-emptive**: check BEFORE executing, not after.
4. **Fail-safe on DB error**: If the cost database is unreachable, **BLOCK** the operation. Never fail-open. Never allow untracked spend.
5. **Escalation at 80%**: When any scope reaches 80% of its budget, `G1-cost-tracker` escalates to `G2-budget-enforcer` via Slack.
6. **Cost precision**: All amounts stored and reported in USD with 4 decimal places.
7. **Daily reset**: Budget counters reset at 00:00 UTC daily. Historical data retained indefinitely.

### 9.3 Cost Calculation Formula

```
invocation_cost_usd = (input_tokens / 1_000_000 * model_input_price)
                    + (output_tokens / 1_000_000 * model_output_price)
```

### 9.4 Model Pricing (Claude API)

| Model                          | Input (per 1M tokens) | Output (per 1M tokens) |
|--------------------------------|-----------------------|------------------------|
| claude-haiku-4-5-20251001      | $0.80                 | $4.00                  |
| claude-sonnet-4-6              | $3.00                 | $15.00                 |
| claude-opus-4-6                | $15.00                | $75.00                 |

### 9.5 Budget Alert Rules

| Condition                              | Action                              |
|----------------------------------------|-------------------------------------|
| Invocation cost > 80% of budget        | `slack_alert` warning               |
| Invocation cost > budget               | Reject invocation                   |
| Agent daily spend > 80% of daily cap   | `slack_alert` warning               |
| Agent daily spend > daily cap          | Halt agent for remainder of day     |
| Fleet daily spend > 80% of fleet cap   | `slack_alert` + page on-call        |
| Fleet daily spend > fleet cap          | Halt all non-critical agents        |

### 9.6 12-Document Pipeline Cost Estimate

| Agent                      | Model   | Est. Tokens (in+out) | Est. Cost |
|----------------------------|---------|-----------------------|-----------|
| D1-roadmap-generator       | sonnet  | ~15K                  | ~$0.27    |
| claude-md-generator        | sonnet  | ~12K                  | ~$0.22    |
| D2-prd-generator           | sonnet  | ~20K                  | ~$0.36    |
| D3-feature-extractor       | sonnet  | ~15K                  | ~$0.27    |
| D8-backlog-builder         | sonnet  | ~18K                  | ~$0.32    |
| D5-architecture-drafter    | opus    | ~25K                  | ~$2.25    |
| D6-data-model-designer     | sonnet  | ~15K                  | ~$0.27    |
| D7-api-contract-generator  | sonnet  | ~15K                  | ~$0.27    |
| D4-enforcement-scaffolder  | sonnet  | ~10K                  | ~$0.18    |
| D10-quality-spec-generator | sonnet  | ~12K                  | ~$0.22    |
| D11-test-strategy-generator| sonnet  | ~12K                  | ~$0.22    |
| D9-design-spec-writer      | opus    | ~30K                  | ~$2.70    |
| **Total**                  |         |                       | **~$7.55**|

Pipeline ceiling: $25.00 (provides 3x headroom for retries and re-runs).

---

## 10. Forbidden Patterns

These patterns are **strictly prohibited**. Claude Code and all contributors must reject code that violates these rules. Each pattern is specific and greppable.

### Architecture Violations (F1-F6)

| #  | Forbidden Pattern                                                  | Required Instead                                                           |
|----|--------------------------------------------------------------------|----------------------------------------------------------------------------|
| F1 | Business logic in MCP tool handlers                                | All logic in `services/` — MCP handler calls service method only           |
| F2 | Business logic in API route handlers                               | All logic in `services/` — route handler calls service method only         |
| F3 | Direct database access from dashboard                              | Dashboard calls REST API via HTTP; never imports services or DB            |
| F4 | MCP tool without corresponding REST endpoint                       | Every MCP tool MUST have a matching REST endpoint for parity               |
| F5 | REST endpoint without corresponding MCP tool (for data operations) | Data operations must be accessible from both interfaces                    |
| F6 | Dashboard page that imports from `services/`                       | Dashboard imports only `requests` and `streamlit`                          |

### Code Quality Violations (F7-F14)

| #   | Forbidden Pattern                          | Required Instead                                                    |
|-----|--------------------------------------------|---------------------------------------------------------------------|
| F7  | `print()` in production code               | Use `structlog` — `logger.info()`, `logger.error()`, etc.           |
| F8  | Blocking I/O in async context              | Use `await` — `asyncpg`, `aiohttp.ClientSession`, `asyncio.sleep`  |
| F9  | Sync database calls (`psycopg2`, `sqlite`) | Use `asyncpg` via `sqlalchemy[asyncio]` `AsyncEngine`              |
| F10 | Hardcoded API keys or connection strings   | Use environment variables via `.env` (loaded by `python-dotenv`)    |
| F11 | `# placeholder` or empty function bodies   | Fully implemented OR marked `# TODO(ticket-id): <specific reason>` |
| F12 | Stubs without tracking ticket              | Every `# TODO` must reference a ticket ID (e.g., `FIX-01`, `ADD-06`)|
| F13 | Bare `except:` without specific type       | `except SpecificException:` always                                  |
| F14 | `import *` anywhere                        | Explicit named imports only                                         |

### Agent Violations (F15-F22)

| #   | Forbidden Pattern                                 | Required Instead                                                         |
|-----|---------------------------------------------------|--------------------------------------------------------------------------|
| F15 | Agent without all 9 manifest subsystems            | Every manifest.yaml must have: identity, capabilities, constraints, knowledge, communication, governance, evaluation, lifecycle, deployment |
| F16 | Agent without `rubric.yaml`                        | Every agent folder must contain a rubric.yaml with evaluation dimensions |
| F17 | Agent without at least 3 golden tests              | Every agent must have 3+ golden tests in `tests/golden/`                 |
| F18 | Agent manifest that fails schema validation        | Must pass `python -m sdk.schema_validator <manifest.yaml>`               |
| F19 | Agent that does not extend `BaseAgent`             | All agents use `from sdk.base_agent import BaseAgent` and extend it      |
| F20 | Agent that does not use Claude Agent SDK properly  | All agents use `from claude_agent_sdk import query, ClaudeAgentOptions`  |
| F21 | Writing `agent.py` before `manifest.yaml`          | Build spec-first: update manifest.yaml + prompt.md BEFORE agent.py      |
| F22 | Agent folder not named by agent ID                 | Folder name = agent ID: `G1-cost-tracker`, `OV-D1-scope-boundary-auditor` |

### Process Violations (F23-F28)

| #   | Forbidden Pattern                              | Required Instead                                                      |
|-----|-------------------------------------------------|-----------------------------------------------------------------------|
| F23 | Skipping `state/MANIFEST.md` update            | Update MANIFEST.md after every file created or modified               |
| F24 | Committing more than 3 files without commit    | `git add -p && git commit -m "feat: <what>"` every 3 files           |
| F25 | Moving to next agent before tests pass         | Must pass `pytest tests/test_<agent_id>.py -v` first                 |
| F26 | File names with spaces or camelCase            | Lowercase-hyphenated: `my-document.md`, `cost-service.py`            |
| F27 | Mocking the database engine in tests           | Use real PostgreSQL via testcontainers                                |
| F28 | Substituting SQLite for PostgreSQL in tests    | Use `testcontainers[postgres]` for real PostgreSQL                   |

---

## 11. Mandatory Build Rules (MASTER-BUILD-SPEC Section 1)

These 13 rules are non-negotiable. Every contributor — human or AI — must follow them without exception.

| #  | Rule                                                                                                    |
|----|---------------------------------------------------------------------------------------------------------|
| 1  | All agents use `from claude_agent_sdk import query, ClaudeAgentOptions`.                                |
| 2  | All agents extend `sdk/base_agent.py::BaseAgent`.                                                       |
| 3  | Every agent manifest has exactly 9 anatomy subsystems.                                                  |
| 4  | Build spec-first: update `manifest.yaml` + `prompt.md` before writing `agent.py`.                      |
| 5  | API key only needed to RUN agents, not to write code. All code must be writable without an API key.     |
| 6  | No placeholder comments — fully implemented or marked `# TODO(ticket-id): <reason>`.                   |
| 7  | Update `state/MANIFEST.md` after every file created or modified.                                        |
| 8  | Commit every 3 files: `git add -p && git commit -m "feat: <what>"`.                                    |
| 9  | Follow `G1-cost-tracker` as the gold standard for every new agent. Copy its structure exactly.           |
| 10 | Every new agent must pass `python -m pytest tests/test_<agent_id>.py -v` before moving on.              |
| 11 | File naming: lowercase-hyphenated (e.g., `my-document.md`), no spaces, no camelCase.                   |
| 12 | Agent folders: named by ID (e.g., `G1-cost-tracker`, `OV-D1-scope-boundary-auditor`).                  |
| 13 | Every agent manifest must validate against `schema/agent-manifest.schema.json`.                         |

---

## 12. Adding a Feature: Step-by-Step Checklist

When adding a new feature that spans all three interfaces, follow this exact sequence. A developer reading this section can add a feature across ALL 3 interfaces without asking questions.

### Step 1: Shared Service (do this first — it IS the feature)

```bash
# 1. Create Pydantic models for input/output
# 2. Implement the service class with full business logic
# 3. Write tests FIRST (TDD encouraged)
# File: services/<feature>_service.py
# Test: tests/services/test_<feature>_service.py
pytest tests/services/test_<feature>_service.py -v  # Must pass before proceeding
```

### Step 2: Database Migration (if the feature needs persistence)

```bash
# File: migrations/<next_number>_create_<table>.sql
# Follow Pattern 6 (BEGIN/COMMIT, CREATE TABLE, CREATE INDEX, RLS policy)
make db-migrate  # Apply migration
```

### Step 3: MCP Tool Handler (expose to AI clients)

```bash
# 1. Create tool handler that calls service method (ZERO business logic)
# 2. Define TOOL_DEFINITION with inputSchema
# 3. Register tool in the appropriate MCP server's server.py
# 4. Write MCP tool test
# File: mcp-servers/<server>/tools/<tool_name>.py
# Test: tests/mcp/test_<server>.py
pytest tests/mcp/test_<server>.py -v  # Must pass before proceeding
```

### Step 4: REST API Route (expose to HTTP clients + dashboard)

```bash
# 1. Create route handler that calls SAME service method (ZERO business logic)
# 2. Register routes in api/routes/<feature>.py + api/routes/__init__.py
# 3. Write API route test
# File: api/routes/<feature>.py
# Test: tests/api/test_<feature>_routes.py
pytest tests/api/test_<feature>_routes.py -v  # Must pass before proceeding
```

### Step 5: Dashboard Page (if user-facing)

```bash
# 1. Create Streamlit page that calls REST API (NEVER import services)
# 2. Add to dashboard/pages/ with correct numeric prefix
# File: dashboard/pages/<NN>_<feature>.py
# Test: tests/dashboard/test_<feature>.py
```

### Step 6: Parity Test (verify MCP and REST match)

```bash
# Verify MCP and REST return identical results for the same input
# Add test case to: tests/integration/test_mcp_api_parity.py
pytest tests/integration/test_mcp_api_parity.py -v  # Must pass
```

### Step 7: Update State + Commit

```bash
# Update state/MANIFEST.md with all new/modified files
# Commit every 3 files:
git add -p && git commit -m "feat: add <feature> across all interfaces"
```

---

## 13. Testing Strategy

### Test Pyramid

```
         /  Adversarial  \              <-- Fewest (attack vectors, edge cases)
        / Golden (Agent)   \            <-- Per-agent input -> expected output
       / Integration (Parity) \         <-- MCP <-> REST return identical results
      / API Route Tests         \       <-- HTTP request -> response validation
     / MCP Tool Handler Tests     \     <-- Tool call -> response validation
    / Shared Service Tests (MOST)   \   <-- Core business logic, real PostgreSQL
```

### Test Execution Order (fastest feedback first)

1. `pytest tests/services/ -v` — Service tests catch logic bugs immediately.
2. `pytest tests/mcp/ -v` — MCP handler tests catch integration issues.
3. `pytest tests/api/ -v` — API route tests catch HTTP layer issues.
4. `pytest tests/integration/ -v` — Parity tests catch interface drift.
5. `pytest tests/golden/ -v` — Golden tests validate agent behavior.
6. `pytest tests/adversarial/ -v` — Adversarial tests catch safety issues.

### Shared Test Fixtures

```python
# tests/conftest.py
from __future__ import annotations

from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer

from services.pipeline_service import PipelineService
from services.cost_service import CostService
from services.audit_service import AuditService
from sdk.context.session_store import SessionStore
from sdk.stores.postgres_cost_store import CostStore


@pytest.fixture(scope="session")
def postgres():
    """Real PostgreSQL via testcontainers — never mock the database."""
    with PostgresContainer("postgres:16") as pg:
        yield pg


@pytest_asyncio.fixture
async def db_engine(postgres) -> AsyncEngine:
    """Async SQLAlchemy engine connected to test PostgreSQL."""
    url = postgres.get_connection_url().replace("psycopg2", "asyncpg")
    engine = create_async_engine(url)
    # Run all migrations in order
    async with engine.begin() as conn:
        for migration in sorted(Path("migrations").glob("*.sql")):
            await conn.execute(text(migration.read_text()))
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_store(db_engine: AsyncEngine) -> SessionStore:
    """SessionStore wired to test database."""
    return SessionStore(db=db_engine)


@pytest_asyncio.fixture
async def cost_store(db_engine: AsyncEngine) -> CostStore:
    """CostStore wired to test database."""
    return CostStore(db=db_engine)


@pytest_asyncio.fixture
async def pipeline_service(
    db_engine: AsyncEngine,
    session_store: SessionStore,
    cost_store: CostStore,
) -> PipelineService:
    """PipelineService wired to test database."""
    return PipelineService(
        db=db_engine,
        session_store=session_store,
        cost_store=cost_store,
    )


@pytest_asyncio.fixture
async def cost_service(db_engine: AsyncEngine) -> CostService:
    """CostService wired to test database."""
    return CostService(db=db_engine)


@pytest_asyncio.fixture
async def audit_service(db_engine: AsyncEngine) -> AuditService:
    """AuditService wired to test database."""
    return AuditService(db=db_engine)
```

### Coverage Targets

| Layer            | Target | Enforced By                              |
|------------------|--------|------------------------------------------|
| SDK modules      | 90%    | `pytest --cov=sdk --cov-fail-under=90`   |
| Shared services  | 80%    | `pytest --cov=services --cov-fail-under=80` |
| MCP handlers     | 70%    | `pytest --cov=mcp_servers --cov-fail-under=70` |
| API routes       | 70%    | `pytest --cov=api --cov-fail-under=70`   |
| Per-agent module | 90%    | Agent-level CI check                      |

---

## 14. Session Context Keys (12-Doc Pipeline)

These are the exact key names used in `SessionStore`. Use them verbatim in agent code.

| Key                      | Written By | Read By                                  |
|--------------------------|------------|------------------------------------------|
| `requirements_doc`       | D1         | D2, D3, D4, D5, D6, D7, D8, D9, D10     |
| `prd_doc`                | D2         | D3, D5, D6, D9, B1                       |
| `feature_catalog`        | D3         | D4, D8, B1, B7                           |
| `task_list`              | D8         | B1, T2                                   |
| `architecture_doc`       | D5         | D3, D6, D7, D9, B1                       |
| `db_schema`              | D6         | B1, B2                                   |
| `api_contracts`          | D7         | B1, B2, T4                               |
| `enforcement_scaffold`   | D4         | B1                                       |
| `quality_spec`           | D10        | T2, T3, T4, T5                           |
| `test_strategy`          | D11        | T2, T3, T4, T5                           |
| `design_spec`            | D9         | B1, B2, B3                               |
| `project_claude_md`      | claude-md  | All agents (project-level CLAUDE.md)      |

---

## 15. CI/CD Pipeline (Target)

```
git push -> GitHub Actions
  |
  +--> ruff check . && ruff format --check .
  +--> mypy --strict services/ sdk/ api/ mcp-servers/
  +--> pytest tests/services/ -v --cov=services --cov-fail-under=80
  +--> pytest tests/mcp/ tests/api/ -v
  +--> pytest tests/integration/ -v
  +--> python -m sdk.schema_validator agents/**/manifest.yaml
  |
  v
All pass -> merge allowed
```

---

*End of CLAUDE.md. This document is the single source of truth for how we build in this repository. When in doubt, refer to this file. When this file conflicts with other documentation, this file wins.*
