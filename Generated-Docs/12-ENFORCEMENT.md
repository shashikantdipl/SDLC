# CLAUDE-ENFORCEMENT — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 12 of 14 | Status: Draft

---

## Purpose

This document defines the `.claude/` directory structure, rules, and skills that **automatically enforce** the coding standards in CLAUDE.md (Doc 3) and the architectural constraints in ARCH.md (Doc 2). In the Full-Stack-First approach:

- **THE KEY RULE:** All business logic lives in shared services (`services/`). MCP tool handlers, REST route handlers, and Dashboard pages are thin adapters only.
- **THE KEY SKILL:** `/new-interaction` scaffolds all layers at once (service, MCP tool, REST route, Dashboard view, schema, and tests), guaranteeing structural parity from the moment code is created.

### Upstream Dependencies

| Document | What This Doc Reads |
|----------|-------------------|
| CLAUDE.md (Doc 3) | Coding rules, forbidden patterns, repo structure, implementation patterns |
| ARCH.md (Doc 2) | 3 MCP servers, REST API (aiohttp), Dashboard (Streamlit), 8 shared services, PostgreSQL |
| INTERACTION-MAP (Doc 6) | Interaction IDs, data shape names, service method signatures |
| FEATURE-CATALOG (Doc 5) | Feature IDs referenced in rule justifications |

### Downstream Consumers

| Document | What It Reads From Here |
|----------|------------------------|
| TESTING (Doc 13) | Test scaffolding skills, coverage thresholds per layer |
| BACKLOG (Doc 11) | Enforcement setup stories, rule file deliverables |

---

## 1. Directory Structure

```
.claude/
├── settings.json                  # Claude Code configuration
├── rules/
│   ├── 01-python.md               # Python language standards
│   ├── 02-shared-services.md      # THE KEY RULE — business logic isolation
│   ├── 03-mcp-servers.md          # MCP tool handler constraints
│   ├── 04-api-routes.md           # REST route handler constraints
│   ├── 05-dashboard.md            # Streamlit dashboard constraints
│   ├── 06-agents.md               # Agent implementation standards
│   ├── 07-schemas.md              # Schema definition standards
│   ├── 08-migrations.md           # Database migration standards
│   └── 09-tests.md                # Test standards and coverage thresholds
└── skills/
    ├── new-interaction.md          # THE KEY SKILL — full-stack scaffolding
    ├── new-mcp-tool.md             # MCP tool scaffolding
    ├── new-api-route.md            # REST route scaffolding
    ├── new-dashboard-view.md       # Dashboard view scaffolding
    ├── new-agent.md                # Agent scaffolding
    ├── new-test.md                 # Test file scaffolding
    └── new-migration.md            # Database migration scaffolding
```

---

## 2. settings.json

```json
{
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "Bash(python *)",
      "Bash(pytest *)",
      "Bash(ruff *)",
      "Bash(mypy *)",
      "Bash(git *)",
      "Bash(psql *)",
      "Bash(alembic *)"
    ],
    "deny": [
      "Bash(rm -rf /)",
      "Bash(docker rm *)",
      "Bash(DROP DATABASE *)"
    ]
  },
  "rules": [
    ".claude/rules/01-python.md",
    ".claude/rules/02-shared-services.md",
    ".claude/rules/03-mcp-servers.md",
    ".claude/rules/04-api-routes.md",
    ".claude/rules/05-dashboard.md",
    ".claude/rules/06-agents.md",
    ".claude/rules/07-schemas.md",
    ".claude/rules/08-migrations.md",
    ".claude/rules/09-tests.md"
  ],
  "skills": [
    ".claude/skills/new-interaction.md",
    ".claude/skills/new-mcp-tool.md",
    ".claude/skills/new-api-route.md",
    ".claude/skills/new-dashboard-view.md",
    ".claude/skills/new-agent.md",
    ".claude/skills/new-test.md",
    ".claude/skills/new-provider.md",
    ".claude/skills/new-migration.md"
  ],
  "context": {
    "include": [
      "CLAUDE.md",
      "services/**/*.py",
      "schema/**/*.json"
    ]
  }
}
```

---

## 3. Rule Files

### 3.1 `.claude/rules/01-python.md` — Python Language Standards

```markdown
---
description: Python language and tooling standards for all source files
globs: ["**/*.py"]
severity: error
---

# Python Language Standards

## Runtime
- Python 3.12+ required. Use modern syntax: `match` statements, `type` aliases, PEP 695 generics where applicable.
- Target platform: Linux (production), macOS/Windows (development).

## Type Hints
- **Every function** must have complete type annotations on all parameters and the return type.
- Use `from __future__ import annotations` at the top of every module for PEP 604 union syntax (`X | None`).
- Use `typing.Protocol` for structural subtyping instead of ABCs where possible.
- No `Any` unless explicitly justified with a comment explaining why.

## Linting — Ruff
- Configuration lives in `pyproject.toml`.
- Line length: 120.
- Select rules: `["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "SIM"]`.
- All Ruff errors are blocking — code must pass `ruff check .` with zero errors before commit.
- Import sorting: isort-compatible (Ruff `I` rules). Sections: stdlib, third-party, first-party, local.

## Type Checking — mypy
- Strict mode enabled (`--strict`).
- No `type: ignore` without a specific error code (e.g., `# type: ignore[override]`).
- Every module must pass `mypy --strict` independently.

## Logging — structlog
- **FORBIDDEN:** `print()`, `logging.getLogger()`, `logging.info()`, or any stdlib logging usage.
- Use `import structlog; logger = structlog.get_logger()` in every module.
- Log levels: `debug` (development traces), `info` (business events), `warning` (recoverable issues), `error` (failures), `critical` (system down).
- Every log call must include structured context: `logger.info("pipeline_triggered", project_id=project_id, pipeline_name=name)`.

## Async
- All I/O operations must be `async`. No blocking calls in the event loop.
- Use `asyncio` for concurrency. No `threading` or `multiprocessing` for I/O-bound work.
- Use `asyncpg` for database access (never `psycopg2`).
- Use `aiohttp.ClientSession` for HTTP calls (never `requests`).

## Testing
- Framework: `pytest` with `pytest-asyncio`.
- Database tests: `testcontainers` for real PostgreSQL (never mock the database).
- No `unittest.TestCase` — use plain pytest functions and fixtures.

## Forbidden Patterns
- **No bare `except:`** — always catch specific exceptions or use `except Exception:`.
- **No mutable default arguments** — use `None` and assign inside function body.
- **No `global` or `nonlocal`** — use class attributes or return values.
- **No wildcard imports** — `from module import *` is forbidden.
- **No relative imports beyond one level** — use absolute imports for cross-package references.
- **No `time.sleep()`** — use `asyncio.sleep()` in async code or redesign.
```

---

### 3.2 `.claude/rules/02-shared-services.md` — THE KEY RULE

```markdown
---
description: "THE KEY RULE: All business logic MUST live in the shared service layer"
globs: ["services/**/*.py", "mcp-servers/**/*.py", "api/**/*.py", "dashboard/**/*.py"]
severity: error
---

# Shared Service Layer — THE KEY RULE

This is the most important architectural rule in the entire codebase. It enforces the
Full-Stack-First principle: three interface layers (MCP, REST, Dashboard) share one
business logic layer.

## The Rule

**ALL business logic MUST live in `services/` directory.** No exceptions.

## What Each Layer Is Allowed To Do

### services/**/*.py (Shared Services)
- OWNS all business logic, data access, validation, orchestration.
- Every public method: `async`, fully type-hinted, returns a typed dataclass or Pydantic model.
- Receives dependencies via constructor injection (DB pool, other services).
- NEVER imports from `mcp-servers/`, `api/`, or `dashboard/`.
- NEVER accesses `st.` (Streamlit), `aiohttp.web`, or MCP protocol types.
- Services are interface-agnostic — they do not know which layer is calling them.

### mcp-servers/**/tools/*.py (MCP Tool Handlers)
- THIN ADAPTERS ONLY.
- Allowed: parse MCP input, call a service method, format MCP response.
- FORBIDDEN: SQL queries, business logic, data transformation beyond MCP formatting.
- FORBIDDEN: importing from `api/` or `dashboard/`.
- Every handler is one service call (max two for read-then-write patterns).

### api/routes/*.py (REST Route Handlers)
- THIN ADAPTERS ONLY.
- Allowed: parse HTTP request, validate with Pydantic, call a service method, format HTTP response.
- FORBIDDEN: SQL queries, business logic, data transformation beyond HTTP formatting.
- FORBIDDEN: importing from `mcp-servers/` or `dashboard/`.
- Every handler is one service call (max two for read-then-write patterns).

### dashboard/**/*.py (Streamlit Pages/Components)
- PURE PRESENTATION ONLY.
- Allowed: call REST API endpoints, render Streamlit components, manage UI state.
- FORBIDDEN: importing from `services/` directly.
- FORBIDDEN: importing from `mcp-servers/` or `api/`.
- FORBIDDEN: direct database access of any kind.
- ALL data comes from REST API calls to `localhost:8080`.

## Service Class Pattern

Every service MUST follow this pattern:

```python
from __future__ import annotations

import asyncpg
import structlog
from dataclasses import dataclass

logger = structlog.get_logger()


@dataclass(frozen=True)
class PipelineRun:
    """Immutable data shape returned by PipelineService."""
    id: str
    project_id: str
    pipeline_name: str
    status: str
    progress_pct: float
    created_at: str


class PipelineService:
    """Shared service for pipeline operations.

    All pipeline business logic lives here. MCP tool handlers
    and REST route handlers are thin wrappers around these methods.
    """

    def __init__(self, db: asyncpg.Pool, cost_service: CostService) -> None:
        self._db = db
        self._cost = cost_service

    async def trigger(
        self, project_id: str, pipeline_name: str, brief: str
    ) -> PipelineRun:
        """Validate inputs, check budget, create run, start pipeline."""
        # 1. Validate project exists
        # 2. Check budget via cost_service
        # 3. Create pipeline_run record
        # 4. Schedule pipeline execution
        # 5. Return typed result
        ...

    async def get_status(self, run_id: str) -> PipelineRun:
        """Retrieve current status of a pipeline run."""
        ...
```

## Dependency Injection Pattern

Services receive dependencies via constructor, wired at application startup:

```python
# In app startup (api/app.py or mcp-servers/*/server.py):
db_pool = await asyncpg.create_pool(dsn=DATABASE_URL)
cost_service = CostService(db=db_pool)
audit_service = AuditService(db=db_pool)
pipeline_service = PipelineService(db=db_pool, cost_service=cost_service)
```

## Violation Detection

If you see ANY of these patterns, it is a violation:
- `import asyncpg` in a file under `mcp-servers/`, `api/routes/`, or `dashboard/`
- `await db.fetch(` or `await db.execute(` outside `services/`
- Business logic (if/else on domain state, calculations, multi-step orchestration) in a tool handler or route handler
- `from services.` in any file under `dashboard/`
- `import streamlit` in any file under `services/`, `mcp-servers/`, or `api/`

## LLM Provider Abstraction Rule

**Never import `anthropic`, `openai`, or `ollama` directly in agent code.** All LLM calls MUST go through `sdk.llm.LLMProvider`. Only the provider implementations inside `sdk/llm/` are allowed to import provider-specific SDKs.

If you see ANY of these patterns in agent code, it is a violation:
- `import anthropic` or `from anthropic import` in `agents/**/*.py`
- `import openai` or `from openai import` in `agents/**/*.py`
- `import ollama` or `from ollama import` in `agents/**/*.py`
- Direct model ID references (e.g., `"claude-sonnet-4-6"`, `"gpt-4o"`) in agent code — use tier names instead

**Correct pattern:**
```python
from sdk.llm import LLMProvider

class MyAgent(BaseAgent):
    async def execute(self, input: AgentInput) -> AgentOutput:
        response = await self.llm.complete(prompt=..., tier="balanced")
        # self.llm is an LLMProvider injected by BaseAgent
```
```

---

### 3.3 `.claude/rules/03-mcp-servers.md` — MCP Server Standards

```markdown
---
description: MCP tool handler implementation standards
globs: ["mcp-servers/**/*.py"]
severity: error
---

# MCP Server Standards

## Tool Naming
- Tool names use `snake_case`: `verb_noun` format.
- Examples: `trigger_pipeline`, `list_agents`, `get_cost_report`.
- Resource URIs use `protocol://path` format: `agent://fleet/status`, `pipeline://runs/{id}`.

## Input Schema
- Every tool MUST have a `input_schema` dict with valid JSON Schema 2020-12.
- All required fields must be listed in `"required"` array.
- Every field must have a `"description"` string.
- Use `"enum"` for constrained string values.

```python
TOOL_DEFINITION = {
    "name": "trigger_pipeline",
    "description": "Start a 14-doc generation pipeline for a project",
    "input_schema": {
        "type": "object",
        "properties": {
            "project_id": {
                "type": "string",
                "description": "Unique project identifier"
            },
            "pipeline_name": {
                "type": "string",
                "description": "Pipeline template to execute",
                "enum": ["full-14-doc", "design-only", "build-only"]
            },
            "brief": {
                "type": "string",
                "description": "Project brief or requirements summary"
            }
        },
        "required": ["project_id", "pipeline_name", "brief"]
    }
}
```

## Input Validation
- Validate all inputs BEFORE calling the service method.
- Use Pydantic models or manual validation matching the JSON Schema.
- Return structured validation errors, never raw tracebacks.

## Error Handling
- NEVER expose raw exceptions to the caller.
- Return structured error responses with: `error_code`, `message`, `details`.
- Error codes must match the standard error envelope (same codes as REST API).
- Log every error with `structlog` including tool name, inputs (sanitized), and error details.

```python
async def handle_trigger_pipeline(arguments: dict) -> list[TextContent]:
    try:
        # Validate
        project_id = arguments.get("project_id")
        if not project_id:
            return [TextContent(type="text", text=json.dumps({
                "error_code": "VALIDATION_ERROR",
                "message": "project_id is required"
            }))]

        # Call service
        result = await pipeline_service.trigger(
            project_id=project_id,
            pipeline_name=arguments["pipeline_name"],
            brief=arguments["brief"],
        )

        # Format response
        return [TextContent(type="text", text=json.dumps(asdict(result)))]

    except DomainError as e:
        logger.error("tool_error", tool="trigger_pipeline", error=str(e))
        return [TextContent(type="text", text=json.dumps({
            "error_code": e.code,
            "message": str(e)
        }))]
```

## Async Requirements
- Every tool handler is `async`.
- No blocking I/O whatsoever (no `time.sleep`, no synchronous HTTP, no synchronous DB).
- No tool handler should run longer than 30 seconds without reporting progress.
- Long-running operations must return a `run_id` for polling.

## Audit Trail
- Every tool invocation MUST be logged to the audit trail via `AuditService.record_event()`.
- Log: tool name, caller identity, input parameters (sanitized — no secrets), result status, duration.

## Health Check
- Every MCP server MUST expose a `health_check` tool.
- Health check returns: server name, version, uptime, connected services status.

## Server Registration
- Each server registers tools in `server.py` using the MCP SDK `@server.tool()` decorator.
- Tool handlers are in separate files under `tools/` — one file per tool or closely related group.
```

---

### 3.4 `.claude/rules/04-api-routes.md` — REST API Standards

```markdown
---
description: REST API route handler implementation standards
globs: ["api/**/*.py"]
severity: error
---

# REST API Route Standards

## Route Handler Pattern
- Every route handler calls exactly one shared service method (max two for read-then-write).
- No inline business logic. No SQL queries. No direct DB access.
- Every handler is `async`.

```python
from aiohttp import web
from pydantic import BaseModel, ValidationError

class TriggerPipelineRequest(BaseModel):
    project_id: str
    pipeline_name: str
    brief: str

async def trigger_pipeline(request: web.Request) -> web.Response:
    """POST /api/v1/pipelines/trigger"""
    try:
        body = await request.json()
        req = TriggerPipelineRequest(**body)
    except (ValidationError, Exception) as e:
        return error_response(400, "VALIDATION_ERROR", str(e))

    pipeline_service: PipelineService = request.app["pipeline_service"]
    result = await pipeline_service.trigger(
        project_id=req.project_id,
        pipeline_name=req.pipeline_name,
        brief=req.brief,
    )
    return success_response(data=asdict(result), status=201)
```

## Standard Response Envelope
- ALL responses use the same envelope:

```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601",
    "duration_ms": 42
  }
}
```

- Error responses:

```json
{
  "status": "error",
  "error": {
    "code": "BUDGET_EXCEEDED",
    "message": "Project budget limit reached",
    "details": { ... }
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

## Error Codes
- Error codes MUST match between MCP and REST (same code for same error).
- Standard codes: `VALIDATION_ERROR`, `NOT_FOUND`, `UNAUTHORIZED`, `FORBIDDEN`, `BUDGET_EXCEEDED`, `RATE_LIMITED`, `INTERNAL_ERROR`, `CONFLICT`, `TIMEOUT`.

## Authentication
- Dashboard requests: JWT tokens in `Authorization: Bearer <token>` header.
- Programmatic access: API keys in `X-API-Key` header.
- Auth middleware in `api/middleware/auth.py` — routes do not handle auth directly.
- Health check endpoints (`/api/v1/health/*`) are unauthenticated.

## Input Validation
- Use Pydantic models for ALL request body validation.
- Path parameters validated via type annotations in route registration.
- Query parameters validated with default values and type coercion.

## Rate Limiting
- Every response includes rate limit headers:
  - `X-RateLimit-Limit`: max requests per window
  - `X-RateLimit-Remaining`: remaining requests
  - `X-RateLimit-Reset`: window reset timestamp (UTC epoch seconds)
- Rate limiting middleware in `api/middleware/` — routes do not implement rate limiting directly.

## URL Structure
- Base path: `/api/v1/`
- Resource naming: plural nouns (`/pipelines`, `/agents`, `/approvals`).
- Nested resources max 2 levels: `/pipelines/{id}/steps`.
- Actions as sub-resources: `/pipelines/trigger`, `/approvals/{id}/approve`.

## CORS
- CORS middleware allows `localhost:8501` (Dashboard) and configured origins.
- Preflight responses cached for 3600 seconds.
```

---

### 3.5 `.claude/rules/05-dashboard.md` — Streamlit Dashboard Standards

```markdown
---
description: Streamlit dashboard implementation standards
globs: ["dashboard/**/*.py"]
severity: error
---

# Streamlit Dashboard Standards

## Architecture Constraint
- **ALL data MUST come from the REST API** at `localhost:8080`.
- FORBIDDEN: `from services import ...` (never import shared services directly).
- FORBIDDEN: `import asyncpg` or any direct database access.
- FORBIDDEN: `from mcp_servers import ...` or any MCP server imports.
- The dashboard is a pure presentation layer that consumes the REST API.

## Data Fetching Pattern

```python
import requests
import streamlit as st

API_BASE = "http://localhost:8080/api/v1"

def fetch_pipeline_runs(status: str | None = None) -> list[dict]:
    """Fetch pipeline runs from REST API."""
    params = {}
    if status:
        params["status"] = status
    try:
        resp = requests.get(f"{API_BASE}/pipelines", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()["data"]
    except requests.RequestException as e:
        st.error(f"Failed to load pipeline runs: {e}")
        return []
```

## Streamlit Components
- Use only Streamlit native components (`st.dataframe`, `st.metric`, `st.plotly_chart`, etc.).
- Reusable components live in `dashboard/components/`.
- Page files live in `dashboard/pages/` with numeric prefix for ordering.

## Loading States
- Every data fetch MUST show a loading state:

```python
with st.spinner("Loading pipeline runs..."):
    runs = fetch_pipeline_runs()
```

- Use `st.skeleton` (Streamlit 1.31+) for placeholder layouts where available.

## Error States
- Every failed API call MUST show an error message with a retry button:

```python
runs = fetch_pipeline_runs()
if not runs:
    st.warning("No pipeline runs found.")
    if st.button("Retry", key="retry_runs"):
        st.rerun()
```

## Accessibility — WCAG 2.1 AA
- All interactive elements MUST have ARIA labels via Streamlit's `label` parameter.
- Keyboard navigation must work for all actions (approve, reject, trigger, filter).
- Color contrast ratio minimum 4.5:1 for text, 3:1 for large text.
- Never convey information through color alone — always include text labels or icons.
- All images and charts MUST have `alt` text or `st.caption` descriptions.

## Styling
- No inline CSS longer than one property. For multi-property styling:

```python
# WRONG:
st.markdown('<div style="color:red;font-size:20px;margin:10px;padding:5px">text</div>',
            unsafe_allow_html=True)

# RIGHT:
st.markdown("""
<style>
.alert-card { color: red; font-size: 20px; margin: 10px; padding: 5px; }
</style>
<div class="alert-card">text</div>
""", unsafe_allow_html=True)
```

## Auto-Refresh
- Pages with live data use `st.auto_refresh(interval=30)` or `time.sleep` + `st.rerun` loop.
- Refresh interval is configurable via `dashboard/config.py`.
- User can pause auto-refresh with a toggle.

## Session State
- Use `st.session_state` for UI state (filters, selections, pagination).
- Never store business data in session state — always re-fetch from API.
```

---

### 3.6 `.claude/rules/06-agents.md` — Agent Implementation Standards

```markdown
---
description: Agent directory structure and implementation standards
globs: ["agents/**/*"]
severity: error
---

# Agent Implementation Standards

## Directory Structure
Every agent directory MUST contain:

```
agents/<team>/<agent-id>/
├── manifest.yaml       # Agent manifest (REQUIRED — validates against schema)
├── prompt.md           # System prompt (REQUIRED — no stubs)
├── agent.py            # Agent implementation (REQUIRED — extends BaseAgent)
├── hooks.py            # Pre/post hooks (optional but recommended)
├── tools.py            # Tool definitions (optional)
├── rubric.yaml         # Evaluation rubric (REQUIRED)
├── __init__.py         # Package init (REQUIRED)
└── tests/
    ├── test_agent.py           # Unit tests (REQUIRED)
    ├── golden/                 # Golden tests (REQUIRED — minimum 3)
    │   ├── TC-001.yaml
    │   ├── TC-002.yaml
    │   └── TC-003.yaml
    └── adversarial/            # Adversarial tests (REQUIRED — minimum 1)
        └── ADV-001.yaml
```

## manifest.yaml
- MUST validate against `schema/agent-manifest.schema.json` (571-line JSON Schema 2020-12).
- Required fields: `id`, `name`, `version`, `archetype`, `team`, `phase`, `description`.
- Required subsystems: `inputs`, `outputs`, `hooks`, `guardrails`, `cost_profile`.
- The Gold Standard is `agents/govern/G1-cost-tracker/manifest.yaml` — copy that pattern.

## prompt.md
- **No stubs.** Every prompt.md must contain:
  - `# Role` — who the agent is and what it does.
  - `# Input` — what the agent receives (format, schema reference).
  - `# Output` — what the agent produces (format, schema reference).
  - `# Reasoning Steps` — minimum 5 numbered steps the agent follows.
  - `# Constraints` — what the agent must NOT do.
  - `# Examples` — at least 1 input/output example.
- Minimum length: 500 characters (no placeholder prompts).

## agent.py
- MUST extend `sdk.base_agent.BaseAgent` or `sdk.base_agent.BaseStatefulAgent`.
- Constructor receives manifest and dependencies.
- `async def execute(self, input: AgentInput) -> AgentOutput` is the main entry point.
- Must call `self.hooks.pre_execute()` and `self.hooks.post_execute()`.
- Must respect cost budget via `self.cost_profile.check_budget()`.

```python
from sdk.base_agent import BaseAgent, AgentInput, AgentOutput

class CostTrackerAgent(BaseAgent):
    async def execute(self, input: AgentInput) -> AgentOutput:
        await self.hooks.pre_execute(input)
        # ... agent logic ...
        result = AgentOutput(...)
        await self.hooks.post_execute(input, result)
        return result
```

## Testing Requirements
- **3+ golden tests (TC-001 through TC-003+):** known input produces expected output.
- **1+ adversarial test (ADV-001+):** edge cases, malformed input, prompt injection, budget overflow.
- Golden test format:

```yaml
# TC-001.yaml
id: TC-001
name: "Standard cost report generation"
input:
  scope: "fleet"
  period: "2026-03"
expected_output:
  contains: ["total_cost", "breakdown"]
  status: "success"
```

## Manifest Tier Rule

**Agent manifests MUST use `tier` (fast/balanced/powerful), NOT hardcoded model IDs.** The platform resolves tiers to concrete model IDs at invocation time based on the active LLM provider (`LLM_PROVIDER` env var).

If you see ANY of these patterns in `manifest.yaml`, it is a violation:
- `model: claude-sonnet-4-6` or any other hardcoded model ID
- `model: gpt-4o` or any OpenAI model ID
- Any field that pins an agent to a specific provider's model

**Correct pattern:**
```yaml
# In manifest.yaml:
cost_profile:
  tier: balanced          # resolved to claude-sonnet-4-6 (anthropic) or gpt-4o (openai)
  max_tokens: 16000
  temperature: 0.2
```

## Orchestration Levels
- L0 (single agent): standalone execution.
- L1 (chain): sequential agent pipeline.
- L2 (router): dynamic routing to sub-agents.
- L3 (parallel): fan-out execution with merge.
- L4 (autonomous): self-directed with approval gates.
- The orchestration level is declared in `manifest.yaml` and enforced by the runtime.
```

---

### 3.7 `.claude/rules/07-schemas.md` — Schema Standards

```markdown
---
description: Schema definition and data shape standards
globs: ["schema/**/*", "schemas/**/*"]
severity: error
---

# Schema Standards

## JSON Schema Version
- ALL schemas use JSON Schema 2020-12 (`"$schema": "https://json-schema.org/draft/2020-12/schema"`).
- No legacy draft-04 or draft-07 schemas.

## Data Shape Naming
- PascalCase for all data shapes: `PipelineRun`, `CostReport`, `AgentSummary`.
- Names MUST match the INTERACTION-MAP (Doc 6) data shape definitions exactly.
- If INTERACTION-MAP says `PipelineRun`, the schema file is `pipeline-run.schema.json` and the Pydantic model is `class PipelineRun`.

## Single Source of Truth
- Each data shape is defined ONCE in `schema/contracts/`.
- Both MCP tool responses and REST API responses reference the same schema.
- Pydantic models in `services/` or a shared `schemas/` module are generated from or validated against these JSON Schemas.

## Schema File Structure

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://agentic-sdlc.dev/schemas/pipeline-run",
  "title": "PipelineRun",
  "description": "Represents a single pipeline execution run",
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid", "description": "Unique run identifier" },
    "project_id": { "type": "string", "description": "Project this run belongs to" },
    "pipeline_name": { "type": "string", "description": "Pipeline template name" },
    "status": {
      "type": "string",
      "enum": ["pending", "running", "paused", "completed", "failed", "cancelled"],
      "description": "Current run status"
    },
    "progress_pct": { "type": "number", "minimum": 0, "maximum": 100 },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  },
  "required": ["id", "project_id", "pipeline_name", "status", "created_at"],
  "additionalProperties": false
}
```

## Required Fields
- Every schema MUST have: `$schema`, `$id`, `title`, `description`, `type`, `properties`, `required`.
- Every property MUST have a `description`.
- Use `additionalProperties: false` by default (explicit opt-in if needed).

## Enum Values
- All enum values are `snake_case` lowercase strings.
- Status enums include terminal states: `completed`, `failed`, `cancelled`.

## Schema Validation
- All schemas validated at CI time via `schema/agent-manifest.schema.json` validator.
- Service return types must match schema definitions (enforced by mypy + runtime checks).
```

---

### 3.8 `.claude/rules/08-migrations.md` — Database Migration Standards

```markdown
---
description: PostgreSQL migration file standards
globs: ["migrations/**/*.sql"]
severity: error
---

# Database Migration Standards

## File Naming
- Sequential numbering: `001_create_agents.sql`, `002_create_audit_events.sql`.
- Descriptive suffix: `create_`, `add_`, `alter_`, `drop_`, `seed_`.
- Never reuse a migration number. Numbers only go up.

## Structure
- Every migration file MUST contain both UP and DOWN sections:

```sql
-- Migration: 005_create_knowledge_exceptions.sql
-- Created: 2026-03-24
-- Description: Create knowledge_exceptions table for 3-tier exception knowledge base

-- ========== UP ==========

CREATE TABLE IF NOT EXISTS knowledge_exceptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_pattern TEXT NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('client', 'stack', 'universal')),
    description TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    promoted_at TIMESTAMPTZ,
    promoted_by TEXT
);

CREATE INDEX idx_knowledge_exceptions_tier ON knowledge_exceptions(tier);
CREATE INDEX idx_knowledge_exceptions_rule ON knowledge_exceptions(rule_pattern);

-- ========== DOWN ==========

DROP INDEX IF EXISTS idx_knowledge_exceptions_rule;
DROP INDEX IF EXISTS idx_knowledge_exceptions_tier;
DROP TABLE IF EXISTS knowledge_exceptions;
```

## Safety Rules
- **No `DROP TABLE` without explicit approval** — flagged as a blocking review item.
- **All `ALTER TABLE` must be backwards-compatible:**
  - Adding columns: MUST have `DEFAULT` value or be `NULL`able.
  - Renaming columns: FORBIDDEN (add new + migrate + drop old in 3 separate migrations).
  - Changing column types: FORBIDDEN (add new column + migrate + drop old).
  - Dropping columns: Only after verifying no code references remain.
- **No `TRUNCATE`** in migrations — use `DELETE` with `WHERE` clause if needed.
- **Idempotent:** Use `IF NOT EXISTS` for `CREATE`, `IF EXISTS` for `DROP`.

## Row-Level Security
- Every table with tenant data MUST have RLS policies.
- RLS is enabled in the `CREATE TABLE` migration, not as a separate migration.

## Testing
- Every migration MUST be tested with `testcontainers` before merging:
  - Apply UP, verify schema.
  - Apply DOWN, verify clean rollback.
  - Apply UP again, verify idempotency.
- Migration tests live in `tests/migrations/`.

## Indexing
- Every foreign key column MUST have an index.
- Every column used in `WHERE` clauses in service queries SHOULD have an index.
- Partial indexes preferred for status columns: `WHERE status = 'active'`.
```

---

### 3.9 `.claude/rules/09-tests.md` — Test Standards

```markdown
---
description: Test file structure, coverage thresholds, and testing patterns
globs: ["tests/**/*.py"]
severity: error
---

# Test Standards

## File Mirroring
- Test files mirror source structure:
  - `services/pipeline_service.py` -> `tests/services/test_pipeline_service.py`
  - `mcp-servers/agents-server/tools/trigger_pipeline.py` -> `tests/mcp/test_trigger_pipeline.py`
  - `api/routes/pipelines.py` -> `tests/api/test_pipelines.py`
  - `dashboard/pages/01_fleet_health.py` -> `tests/dashboard/test_fleet_health.py`

## Coverage Thresholds (Enforced in CI)

| Layer | Minimum Coverage | Rationale |
|-------|-----------------|-----------|
| `services/` | 90% | Core business logic — highest value |
| `mcp-servers/` | 85% | Thin adapters but critical interface |
| `api/routes/` | 85% | Thin adapters but critical interface |
| `dashboard/` | 75% | UI layer — harder to test comprehensively |
| `sdk/` | 90% | Foundation layer — must be rock solid |
| `agents/` | 80% | Agent logic + golden/adversarial tests |
| **Overall** | **85%** | Project-wide minimum |

## Database Testing
- **ALWAYS use real PostgreSQL via `testcontainers`.** Never mock the database.
- Shared fixture in `tests/conftest.py`:

```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as pg:
        yield pg

@pytest.fixture
async def db_pool(postgres):
    pool = await asyncpg.create_pool(dsn=postgres.get_connection_url())
    # Run migrations
    await run_migrations(pool)
    yield pool
    await pool.close()
```

## Parity Tests
- For every interaction in the INTERACTION-MAP (Doc 6), there MUST be a parity test.
- Parity tests verify: calling the same service method through MCP and REST produces identical results.
- Parity tests live in `tests/integration/test_mcp_api_parity.py`.

```python
async def test_trigger_pipeline_parity(mcp_client, rest_client, db_pool):
    """I-001: MCP and REST trigger_pipeline return identical PipelineRun."""
    # MCP path
    mcp_result = await mcp_client.call_tool("trigger_pipeline", {
        "project_id": "test-project",
        "pipeline_name": "full-14-doc",
        "brief": "Test brief"
    })

    # REST path
    rest_result = await rest_client.post("/api/v1/pipelines/trigger", json={
        "project_id": "test-project",
        "pipeline_name": "full-14-doc",
        "brief": "Test brief"
    })

    # Compare (ignoring IDs and timestamps)
    assert_shapes_equal(mcp_result, rest_result["data"],
                        ignore=["id", "created_at"])
```

## Test Naming
- Test functions: `test_<method>_<scenario>` — e.g., `test_trigger_pipeline_success`, `test_trigger_pipeline_budget_exceeded`.
- Test classes (optional grouping): `class TestPipelineService:`.

## Fixtures
- Shared fixtures in `tests/conftest.py`: `db_pool`, `pipeline_service`, `cost_service`, etc.
- Module-specific fixtures in module-level `conftest.py` files.
- No fixture should mutate shared state without cleanup.

## Async Tests
- Use `@pytest.mark.asyncio` for all async tests.
- Configure in `pyproject.toml`: `asyncio_mode = "auto"`.

## Forbidden Test Patterns
- **No `unittest.mock.patch` on database calls** — use real DB via testcontainers.
- **No `sleep()` in tests** — use async patterns or event-driven waits.
- **No test ordering dependencies** — every test must run independently.
- **No hardcoded ports** — use dynamic port allocation from testcontainers.
```

---

## 4. Skill Files

### 4.1 `.claude/skills/new-interaction.md` — THE KEY SKILL

```markdown
---
name: new-interaction
description: "THE KEY SKILL: Scaffold a complete full-stack interaction across all layers"
usage: "/new-interaction <domain> <name>"
example: "/new-interaction pipeline trigger"
---

# /new-interaction — Full-Stack Scaffolding

## Purpose
Creates ALL files needed for a new interaction across every layer simultaneously,
guaranteeing structural parity from creation. This is the primary way to add new
functionality to the Agentic SDLC Platform.

## Usage
```
/new-interaction <domain> <name>
```

## Arguments
- `<domain>`: The business domain (e.g., `pipeline`, `agent`, `cost`, `audit`, `approval`, `knowledge`, `health`, `session`).
- `<name>`: The action name (e.g., `trigger`, `list`, `approve`, `search`).

## Example
```
/new-interaction pipeline trigger
```

## Files Created (9 files)

### 1. `services/<domain>_service.py` — Service Method

Add method to existing service class (or create new class if first method for domain):

```python
# services/pipeline_service.py

async def trigger(
    self,
    project_id: str,
    pipeline_name: str,
    brief: str,
) -> PipelineRun:
    """Trigger a new pipeline run.

    Steps:
    1. Validate project_id exists in database
    2. Check budget via CostService
    3. Create pipeline_run record with status='pending'
    4. Schedule pipeline execution via background worker
    5. Record audit event
    6. Return PipelineRun data shape

    Raises:
        NotFoundError: project_id does not exist
        BudgetExceededError: project has exceeded budget limit
    """
    ...
```

### 2. `mcp-servers/<server>/tools/<name>.py` — MCP Tool Handler

```python
# mcp-servers/agents-server/tools/trigger_pipeline.py
from __future__ import annotations

import json
from dataclasses import asdict

import structlog
from mcp.types import TextContent

logger = structlog.get_logger()

TOOL_DEFINITION = {
    "name": "trigger_pipeline",
    "description": "Start a 14-doc generation pipeline for a project",
    "input_schema": {
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "Unique project identifier"},
            "pipeline_name": {"type": "string", "description": "Pipeline template name"},
            "brief": {"type": "string", "description": "Project brief"},
        },
        "required": ["project_id", "pipeline_name", "brief"],
    },
}


async def handle(arguments: dict, pipeline_service: PipelineService) -> list[TextContent]:
    """MCP tool handler — thin adapter over PipelineService.trigger()."""
    logger.info("mcp_tool_called", tool="trigger_pipeline", project_id=arguments.get("project_id"))

    project_id = arguments.get("project_id", "")
    pipeline_name = arguments.get("pipeline_name", "")
    brief = arguments.get("brief", "")

    if not all([project_id, pipeline_name, brief]):
        return [TextContent(type="text", text=json.dumps({
            "error_code": "VALIDATION_ERROR",
            "message": "project_id, pipeline_name, and brief are required",
        }))]

    try:
        result = await pipeline_service.trigger(
            project_id=project_id,
            pipeline_name=pipeline_name,
            brief=brief,
        )
        return [TextContent(type="text", text=json.dumps(asdict(result)))]
    except Exception as e:
        logger.error("mcp_tool_error", tool="trigger_pipeline", error=str(e))
        return [TextContent(type="text", text=json.dumps({
            "error_code": getattr(e, "code", "INTERNAL_ERROR"),
            "message": str(e),
        }))]
```

### 3. `api/routes/<domain>.py` — REST Route Handler

```python
# api/routes/pipelines.py
from __future__ import annotations

from aiohttp import web
from dataclasses import asdict
from pydantic import BaseModel

from api.middleware.response import success_response, error_response


class TriggerPipelineRequest(BaseModel):
    project_id: str
    pipeline_name: str
    brief: str


async def trigger_pipeline(request: web.Request) -> web.Response:
    """POST /api/v1/pipelines/trigger"""
    try:
        body = await request.json()
        req = TriggerPipelineRequest(**body)
    except Exception as e:
        return error_response(400, "VALIDATION_ERROR", str(e))

    pipeline_service = request.app["pipeline_service"]
    try:
        result = await pipeline_service.trigger(
            project_id=req.project_id,
            pipeline_name=req.pipeline_name,
            brief=req.brief,
        )
        return success_response(data=asdict(result), status=201)
    except Exception as e:
        return error_response(
            getattr(e, "status_code", 500),
            getattr(e, "code", "INTERNAL_ERROR"),
            str(e),
        )
```

### 4. `dashboard/views/<domain>.py` — Streamlit Component

```python
# dashboard/views/pipeline_trigger.py
from __future__ import annotations

import requests
import streamlit as st

from dashboard.config import API_BASE


def render_trigger_form() -> None:
    """Streamlit component for triggering a pipeline."""
    st.subheader("Trigger Pipeline")

    with st.form("trigger_pipeline_form"):
        project_id = st.text_input("Project ID", help="Unique project identifier")
        pipeline_name = st.selectbox(
            "Pipeline",
            options=["full-14-doc", "design-only", "build-only"],
            help="Pipeline template to execute",
        )
        brief = st.text_area("Project Brief", help="Requirements summary")
        submitted = st.form_submit_button("Trigger Pipeline")

    if submitted:
        if not all([project_id, brief]):
            st.error("Project ID and Brief are required.")
            return

        with st.spinner("Starting pipeline..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/pipelines/trigger",
                    json={
                        "project_id": project_id,
                        "pipeline_name": pipeline_name,
                        "brief": brief,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()["data"]
                st.success(f"Pipeline started: {data['id']}")
            except requests.RequestException as e:
                st.error(f"Failed to trigger pipeline: {e}")
                if st.button("Retry", key="retry_trigger"):
                    st.rerun()
```

### 5. `schemas/<name>.py` — Pydantic Data Shape

```python
# schemas/pipeline_run.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PipelineRun:
    """Data shape for pipeline run — shared across MCP and REST.

    Matches: schema/contracts/pipeline-run.schema.json
    Interaction-MAP: I-001 through I-009
    """
    id: str
    project_id: str
    pipeline_name: str
    status: str  # pending | running | paused | completed | failed | cancelled
    progress_pct: float
    created_at: datetime
    updated_at: datetime | None = None
    brief: str | None = None
    error_message: str | None = None
```

### 6. `tests/services/test_<domain>_service.py` — Service Unit Tests

```python
# tests/services/test_pipeline_service.py
from __future__ import annotations

import pytest
from services.pipeline_service import PipelineService


@pytest.mark.asyncio
async def test_trigger_success(db_pool, cost_service):
    """I-001: Trigger pipeline creates run with pending status."""
    service = PipelineService(db=db_pool, cost_service=cost_service)
    result = await service.trigger(
        project_id="test-project",
        pipeline_name="full-14-doc",
        brief="Test brief for golden path",
    )
    assert result.status == "pending"
    assert result.project_id == "test-project"
    assert result.pipeline_name == "full-14-doc"
    assert result.progress_pct == 0.0


@pytest.mark.asyncio
async def test_trigger_budget_exceeded(db_pool, cost_service_over_budget):
    """I-001: Trigger pipeline raises BudgetExceededError when over limit."""
    service = PipelineService(db=db_pool, cost_service=cost_service_over_budget)
    with pytest.raises(BudgetExceededError):
        await service.trigger(
            project_id="expensive-project",
            pipeline_name="full-14-doc",
            brief="Test brief",
        )


@pytest.mark.asyncio
async def test_trigger_invalid_project(db_pool, cost_service):
    """I-001: Trigger pipeline raises NotFoundError for unknown project."""
    service = PipelineService(db=db_pool, cost_service=cost_service)
    with pytest.raises(NotFoundError):
        await service.trigger(
            project_id="nonexistent",
            pipeline_name="full-14-doc",
            brief="Test brief",
        )
```

### 7. `tests/mcp/test_<name>.py` — MCP Tool Handler Tests

```python
# tests/mcp/test_trigger_pipeline.py
from __future__ import annotations

import json
import pytest


@pytest.mark.asyncio
async def test_mcp_trigger_pipeline_success(mcp_client):
    """I-001: MCP trigger_pipeline returns PipelineRun."""
    result = await mcp_client.call_tool("trigger_pipeline", {
        "project_id": "test-project",
        "pipeline_name": "full-14-doc",
        "brief": "MCP test brief",
    })
    data = json.loads(result[0].text)
    assert "id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_mcp_trigger_pipeline_validation_error(mcp_client):
    """I-001: MCP trigger_pipeline returns VALIDATION_ERROR for missing fields."""
    result = await mcp_client.call_tool("trigger_pipeline", {})
    data = json.loads(result[0].text)
    assert data["error_code"] == "VALIDATION_ERROR"
```

### 8. `tests/api/test_<domain>.py` — REST Route Handler Tests

```python
# tests/api/test_pipelines.py
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_rest_trigger_pipeline_success(rest_client):
    """I-001: POST /api/v1/pipelines/trigger returns 201 with PipelineRun."""
    resp = await rest_client.post("/api/v1/pipelines/trigger", json={
        "project_id": "test-project",
        "pipeline_name": "full-14-doc",
        "brief": "REST test brief",
    })
    assert resp.status == 201
    data = (await resp.json())["data"]
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_rest_trigger_pipeline_validation_error(rest_client):
    """I-001: POST /api/v1/pipelines/trigger returns 400 for invalid body."""
    resp = await rest_client.post("/api/v1/pipelines/trigger", json={})
    assert resp.status == 400
    error = (await resp.json())["error"]
    assert error["code"] == "VALIDATION_ERROR"
```

### 9. `tests/integration/test_<name>_fullstack.py` — Parity + Cross-Interface Tests

```python
# tests/integration/test_trigger_pipeline_fullstack.py
from __future__ import annotations

import json
import pytest


@pytest.mark.asyncio
async def test_trigger_pipeline_parity(mcp_client, rest_client):
    """I-001 PARITY: MCP and REST trigger_pipeline produce same data shape."""
    mcp_result = await mcp_client.call_tool("trigger_pipeline", {
        "project_id": "parity-project",
        "pipeline_name": "full-14-doc",
        "brief": "Parity test",
    })
    mcp_data = json.loads(mcp_result[0].text)

    rest_resp = await rest_client.post("/api/v1/pipelines/trigger", json={
        "project_id": "parity-project",
        "pipeline_name": "full-14-doc",
        "brief": "Parity test",
    })
    rest_data = (await rest_resp.json())["data"]

    # Same fields present
    assert set(mcp_data.keys()) == set(rest_data.keys())
    # Same status
    assert mcp_data["status"] == rest_data["status"]
    # Same project
    assert mcp_data["project_id"] == rest_data["project_id"]


@pytest.mark.asyncio
async def test_trigger_then_status_cross_interface(mcp_client, rest_client):
    """I-001 + I-002 CROSS: Trigger via MCP, check status via REST."""
    # Trigger via MCP
    mcp_result = await mcp_client.call_tool("trigger_pipeline", {
        "project_id": "cross-project",
        "pipeline_name": "full-14-doc",
        "brief": "Cross-interface test",
    })
    run_id = json.loads(mcp_result[0].text)["id"]

    # Check status via REST
    rest_resp = await rest_client.get(f"/api/v1/pipelines/{run_id}")
    assert rest_resp.status == 200
    rest_data = (await rest_resp.json())["data"]
    assert rest_data["id"] == run_id
```

## Checklist After Running

After `/new-interaction` completes, verify:

- [ ] Service method added with full type hints and docstring
- [ ] MCP tool handler is a thin adapter (no business logic)
- [ ] REST route handler is a thin adapter (no business logic)
- [ ] Dashboard component fetches via REST API only
- [ ] Pydantic data shape matches INTERACTION-MAP definition
- [ ] Service test covers success + at least 2 error paths
- [ ] MCP test covers success + validation error
- [ ] REST test covers success + validation error
- [ ] Parity test verifies MCP and REST return same shape
- [ ] Cross-interface test verifies operation works across layers
```

---

### 4.2 `.claude/skills/new-mcp-tool.md` — MCP Tool Scaffolding

```markdown
---
name: new-mcp-tool
description: "Scaffold a new MCP tool handler with schema and test"
usage: "/new-mcp-tool <server> <tool_name>"
example: "/new-mcp-tool agents-server get_pipeline_documents"
---

# /new-mcp-tool — MCP Tool Scaffolding

## Usage
```
/new-mcp-tool <server> <tool_name>
```

## Arguments
- `<server>`: One of `agents-server`, `governance-server`, `knowledge-server`.
- `<tool_name>`: Tool name in `snake_case` (`verb_noun` format).

## Files Created (3 files)

### 1. `mcp-servers/<server>/tools/<tool_name>.py`

```python
from __future__ import annotations

import json
from dataclasses import asdict

import structlog
from mcp.types import TextContent

logger = structlog.get_logger()

TOOL_DEFINITION = {
    "name": "<tool_name>",
    "description": "TODO: Describe what this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            # TODO: Define input properties with descriptions
        },
        "required": [],
    },
}


async def handle(arguments: dict, service: object) -> list[TextContent]:
    """MCP tool handler — thin adapter over shared service method.

    Rules:
    - Validate inputs
    - Call ONE service method
    - Format response as JSON TextContent
    - Log to audit trail
    - Never contain business logic
    """
    logger.info("mcp_tool_called", tool="<tool_name>")

    # TODO: Validate inputs
    # TODO: Call service method
    # TODO: Return formatted result

    try:
        result = await service.method(...)
        return [TextContent(type="text", text=json.dumps(asdict(result)))]
    except Exception as e:
        logger.error("mcp_tool_error", tool="<tool_name>", error=str(e))
        return [TextContent(type="text", text=json.dumps({
            "error_code": getattr(e, "code", "INTERNAL_ERROR"),
            "message": str(e),
        }))]
```

### 2. `schema/contracts/<tool_name>.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://agentic-sdlc.dev/schemas/<tool_name>",
  "title": "TODO: PascalCase name",
  "description": "TODO: Describe this data shape",
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

### 3. `tests/mcp/test_<tool_name>.py`

```python
from __future__ import annotations

import json
import pytest


@pytest.mark.asyncio
async def test_<tool_name>_success(mcp_client):
    """TODO: Interaction ID reference."""
    result = await mcp_client.call_tool("<tool_name>", {
        # TODO: valid inputs
    })
    data = json.loads(result[0].text)
    assert "error_code" not in data


@pytest.mark.asyncio
async def test_<tool_name>_validation_error(mcp_client):
    """<tool_name> returns error for missing required fields."""
    result = await mcp_client.call_tool("<tool_name>", {})
    data = json.loads(result[0].text)
    assert data["error_code"] == "VALIDATION_ERROR"
```

## Registration Reminder
After creating the tool, register it in `mcp-servers/<server>/server.py`:

```python
from tools.<tool_name> import TOOL_DEFINITION, handle as handle_<tool_name>

@server.tool()
async def <tool_name>(arguments: dict) -> list[TextContent]:
    return await handle_<tool_name>(arguments, service=app_service)
```
```

---

### 4.3 `.claude/skills/new-api-route.md` — REST Route Scaffolding

```markdown
---
name: new-api-route
description: "Scaffold a new REST API route with validation and test"
usage: "/new-api-route <method> <path> <domain>"
example: "/new-api-route POST /api/v1/pipelines/trigger pipeline"
---

# /new-api-route — REST Route Scaffolding

## Usage
```
/new-api-route <method> <path> <domain>
```

## Arguments
- `<method>`: HTTP method (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
- `<path>`: Full route path (e.g., `/api/v1/pipelines/trigger`).
- `<domain>`: Service domain (e.g., `pipeline`, `agent`, `cost`).

## Files Created (2 files)

### 1. `api/routes/<domain>.py` (add handler to existing file or create new)

```python
from __future__ import annotations

from aiohttp import web
from dataclasses import asdict
from pydantic import BaseModel

from api.middleware.response import success_response, error_response


class <Action><Domain>Request(BaseModel):
    """Request validation model.

    Fields match schema/contracts/<domain>.schema.json input.
    """
    # TODO: Define request fields with types and validation


async def <action>_<domain>(request: web.Request) -> web.Response:
    """<METHOD> <path>

    Thin adapter: validates input, calls <Domain>Service.<action>(), formats response.
    """
    try:
        # Parse and validate input
        body = await request.json()
        req = <Action><Domain>Request(**body)
    except Exception as e:
        return error_response(400, "VALIDATION_ERROR", str(e))

    # Call shared service
    service = request.app["<domain>_service"]
    try:
        result = await service.<action>(...)
        return success_response(data=asdict(result))
    except Exception as e:
        return error_response(
            getattr(e, "status_code", 500),
            getattr(e, "code", "INTERNAL_ERROR"),
            str(e),
        )
```

### 2. `tests/api/test_<domain>.py` (add test to existing file or create new)

```python
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_<action>_<domain>_success(rest_client):
    """<METHOD> <path> returns expected status with valid input."""
    resp = await rest_client.<method_lower>("<path>", json={
        # TODO: valid request body
    })
    assert resp.status == 200  # or 201 for POST
    data = (await resp.json())["data"]
    # TODO: assert expected fields


@pytest.mark.asyncio
async def test_<action>_<domain>_validation_error(rest_client):
    """<METHOD> <path> returns 400 for invalid input."""
    resp = await rest_client.<method_lower>("<path>", json={})
    assert resp.status == 400
```

## Route Registration Reminder
Add the route in `api/app.py`:

```python
from api.routes.<domain> import <action>_<domain>

app.router.add_route("<METHOD>", "<path>", <action>_<domain>)
```
```

---

### 4.4 `.claude/skills/new-dashboard-view.md` — Dashboard View Scaffolding

```markdown
---
name: new-dashboard-view
description: "Scaffold a new Streamlit dashboard page or component"
usage: "/new-dashboard-view <type> <name>"
example: "/new-dashboard-view page fleet_health"
---

# /new-dashboard-view — Dashboard View Scaffolding

## Usage
```
/new-dashboard-view <type> <name>
```

## Arguments
- `<type>`: `page` (full page in `pages/`) or `component` (reusable in `components/`).
- `<name>`: View name in `snake_case`.

## Files Created

### For `page` type (2 files):

#### 1. `dashboard/pages/<NN>_<name>.py`

```python
"""<Name> — Dashboard Page

Data source: REST API at {API_BASE}
FORBIDDEN: Direct service imports, direct DB access.
"""
from __future__ import annotations

import requests
import streamlit as st

from dashboard.config import API_BASE

st.set_page_config(page_title="<Name>", page_icon="TODO", layout="wide")
st.title("<Name>")


# --- Data Fetching (REST API only) ---

def fetch_data() -> list[dict]:
    """Fetch data from REST API."""
    try:
        resp = requests.get(f"{API_BASE}/TODO", timeout=10)
        resp.raise_for_status()
        return resp.json()["data"]
    except requests.RequestException as e:
        st.error(f"Failed to load data: {e}")
        return []


# --- Page Layout ---

with st.spinner("Loading..."):
    data = fetch_data()

if not data:
    st.warning("No data available.")
    if st.button("Retry", key="retry_<name>"):
        st.rerun()
else:
    # TODO: Render data using Streamlit components
    st.dataframe(data)
```

#### 2. `tests/dashboard/test_<name>.py`

```python
from __future__ import annotations

from unittest.mock import patch
import pytest


def test_<name>_renders_with_data():
    """Page renders data table when API returns results."""
    with patch("dashboard.pages.<NN>_<name>.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": [{"id": "1"}]}
        # TODO: Use streamlit testing utilities
        # from streamlit.testing.v1 import AppTest
        # at = AppTest.from_file("dashboard/pages/<NN>_<name>.py")
        # at.run()
        # assert not at.exception


def test_<name>_shows_error_on_api_failure():
    """Page shows error message when API call fails."""
    with patch("dashboard.pages.<NN>_<name>.requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        # TODO: Verify error state renders
```

### For `component` type (1 file):

#### 1. `dashboard/components/<name>.py`

```python
"""<Name> — Reusable Streamlit Component

Usage:
    from dashboard.components.<name> import render_<name>
    render_<name>(data=...)
"""
from __future__ import annotations

import streamlit as st


def render_<name>(data: dict) -> None:
    """Render <name> component.

    Args:
        data: Data dict from REST API response.
    """
    # TODO: Implement Streamlit component
    st.write(data)
```

## Accessibility Checklist
After creating the view, verify:
- [ ] All inputs have `label` and `help` parameters
- [ ] All buttons have descriptive labels (not just "Submit")
- [ ] Color is not the sole indicator of state
- [ ] Loading spinners have descriptive text
- [ ] Error states have retry buttons
```

---

### 4.5 `.claude/skills/new-agent.md` — Agent Scaffolding

```markdown
---
name: new-agent
description: "Scaffold a complete agent directory with manifest, prompt, implementation, and tests"
usage: "/new-agent <team> <agent-id> <name>"
example: "/new-agent govern G6-dependency-checker dependency-checker"
---

# /new-agent — Agent Scaffolding

## Usage
```
/new-agent <team> <agent-id> <name>
```

## Arguments
- `<team>`: Team directory (`govern`, `claude-cc`).
- `<agent-id>`: Agent identifier (e.g., `G6-dependency-checker`, `B4-formatter`).
- `<name>`: Human-readable name (e.g., `dependency-checker`).

## Files Created (9 files)

### 1. `agents/<team>/<agent-id>/manifest.yaml`

```yaml
# Agent Manifest — validates against schema/agent-manifest.schema.json
id: "<agent-id>"
name: "<name>"
version: "0.1.0"
archetype: "TODO"  # ci-gate | reviewer | ops-agent | discovery-agent | co-pilot | orchestrator | governance
team: "<team>"
phase: "TODO"      # design | build | test | deploy | operate | govern | oversight
description: "TODO: What this agent does in one sentence."

inputs:
  - name: "TODO"
    type: "TODO"
    description: "TODO"

outputs:
  - name: "TODO"
    type: "TODO"
    schema: "TODO.schema.json"

hooks:
  pre_execute:
    - audit_log
    - budget_check
  post_execute:
    - audit_log
    - cost_record

guardrails:
  max_tokens: 4096
  max_cost_per_run: 0.50
  timeout_seconds: 120
  require_approval: false

cost_profile:
  model: "claude-sonnet-4-20250514"
  estimated_tokens_per_run: 2000
  max_budget_per_day: 5.00
```

### 2. `agents/<team>/<agent-id>/prompt.md`

```markdown
# Role
You are the <name> agent. TODO: Describe what this agent does.

# Input
TODO: What the agent receives. Include format and schema reference.

# Output
TODO: What the agent produces. Include format and schema reference.

# Reasoning Steps
1. TODO: First reasoning step
2. TODO: Second reasoning step
3. TODO: Third reasoning step
4. TODO: Fourth reasoning step
5. TODO: Fifth reasoning step

# Constraints
- TODO: What the agent must NOT do
- Never exceed budget without approval
- Always log actions to audit trail

# Examples

## Example 1
**Input:**
TODO: Example input

**Output:**
TODO: Example output
```

### 3. `agents/<team>/<agent-id>/agent.py`

```python
from __future__ import annotations

import structlog
from sdk.base_agent import BaseAgent, AgentInput, AgentOutput

logger = structlog.get_logger()


class <ClassName>Agent(BaseAgent):
    """<name> agent implementation.

    Extends BaseAgent with domain-specific execution logic.
    """

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Main execution entry point."""
        await self.hooks.pre_execute(input)
        logger.info("agent_executing", agent_id=self.manifest.id)

        # TODO: Implement agent logic
        # 1. Parse input
        # 2. Process according to reasoning steps in prompt.md
        # 3. Build output

        result = AgentOutput(
            agent_id=self.manifest.id,
            status="success",
            data={},  # TODO: populated result
        )

        await self.hooks.post_execute(input, result)
        return result
```

### 4. `agents/<team>/<agent-id>/hooks.py`

```python
from __future__ import annotations

from sdk.base_hooks import BaseHooks


class <ClassName>Hooks(BaseHooks):
    """Hooks for <name> agent — audit, cost, PII checks."""
    pass  # Inherits standard hooks; override if agent needs custom behavior
```

### 5. `agents/<team>/<agent-id>/tools.py`

```python
from __future__ import annotations

TOOLS: list[dict] = [
    # TODO: Define tools this agent can use (if any)
]
```

### 6. `agents/<team>/<agent-id>/rubric.yaml`

```yaml
id: "<agent-id>-rubric"
agent: "<agent-id>"
criteria:
  - name: "correctness"
    weight: 0.4
    description: "Output matches expected result for given input"
  - name: "completeness"
    weight: 0.3
    description: "All required fields are present and populated"
  - name: "efficiency"
    weight: 0.2
    description: "Token usage within expected range"
  - name: "safety"
    weight: 0.1
    description: "No PII leakage, no budget violation, proper audit logging"
```

### 7. `agents/<team>/<agent-id>/__init__.py`

```python
from .<agent_module> import <ClassName>Agent

__all__ = ["<ClassName>Agent"]
```

### 8. `agents/<team>/<agent-id>/tests/golden/TC-001.yaml` (+ TC-002, TC-003)

```yaml
id: TC-001
name: "Standard <name> golden path"
input:
  # TODO: Standard input scenario
expected_output:
  status: "success"
  contains:
    # TODO: Expected output fields
```

### 9. `agents/<team>/<agent-id>/tests/adversarial/ADV-001.yaml`

```yaml
id: ADV-001
name: "Malformed input handling"
input:
  # TODO: Invalid, malformed, or adversarial input
expected_behavior:
  status: "error"
  error_code: "VALIDATION_ERROR"
  must_not_contain:
    - "stack trace"
    - "internal error"
```
```

---

### 4.6 `.claude/skills/new-test.md` — Test File Scaffolding

```markdown
---
name: new-test
description: "Scaffold a test file with standard fixtures and patterns"
usage: "/new-test <layer> <module>"
example: "/new-test services pipeline_service"
---

# /new-test — Test File Scaffolding

## Usage
```
/new-test <layer> <module>
```

## Arguments
- `<layer>`: One of `services`, `mcp`, `api`, `dashboard`, `integration`.
- `<module>`: Module name to test (e.g., `pipeline_service`, `trigger_pipeline`).

## Files Created (1 file)

### `tests/<layer>/test_<module>.py`

```python
"""Tests for <layer>/<module>.

Coverage target: {threshold}% (see 09-tests.md rule).
Database: Real PostgreSQL via testcontainers (never mock DB).
"""
from __future__ import annotations

import pytest


# --- Fixtures ---

@pytest.fixture
async def service(db_pool):
    """Create service instance with real DB pool."""
    # TODO: Instantiate the service under test
    ...


# --- Success Cases ---

@pytest.mark.asyncio
async def test_<method>_success(service):
    """TODO: Interaction ID. Happy path with valid input."""
    result = await service.<method>(...)
    assert result is not None
    # TODO: Assert expected shape and values


# --- Error Cases ---

@pytest.mark.asyncio
async def test_<method>_not_found(service):
    """TODO: Interaction ID. Returns error for nonexistent resource."""
    with pytest.raises(NotFoundError):
        await service.<method>(id="nonexistent")


@pytest.mark.asyncio
async def test_<method>_validation_error(service):
    """TODO: Interaction ID. Returns error for invalid input."""
    with pytest.raises((ValueError, ValidationError)):
        await service.<method>(invalid_param="bad")


# --- Edge Cases ---

@pytest.mark.asyncio
async def test_<method>_empty_result(service):
    """Returns empty collection for no matching records."""
    result = await service.<method>(filter="nonexistent")
    assert result == [] or result is not None
```

## Layer-Specific Templates

### services (90% coverage target)
- Test every public method: success, not-found, validation-error, edge-case.
- Use real DB pool from `conftest.py`.
- Test service-to-service interactions (e.g., PipelineService calls CostService).

### mcp (85% coverage target)
- Test tool handler via MCP client fixture.
- Test: success response, validation error, domain error, timeout.
- Verify response is valid JSON with expected schema.

### api (85% coverage target)
- Test via aiohttp test client fixture.
- Test: success status code, error status codes, response envelope format.
- Test auth: valid token, invalid token, missing token.

### dashboard (75% coverage target)
- Mock `requests.get/post` (REST API calls only).
- Verify component renders without exceptions.
- Test error state rendering.

### integration (no threshold — quality over quantity)
- Parity tests: MCP vs REST same result.
- Cross-interface: action on one interface, verify on another.
- Full journey: multi-step workflow across interfaces.
```

---

### 4.7 `.claude/skills/new-provider.md` — LLM Provider Scaffolding

```markdown
---
name: new-provider
description: "Scaffold a new LLM provider implementation in sdk/llm/"
usage: "/new-provider <provider_name>"
example: "/new-provider bedrock"
---

# /new-provider — LLM Provider Scaffolding

## Usage
```
/new-provider <provider_name>
```

## Arguments
- `<provider_name>`: Provider identifier in lowercase (e.g., `bedrock`, `gemini`, `together`).

## Files Created (3 files)

### 1. `sdk/llm/<provider_name>_provider.py`

```python
"""LLM Provider implementation for <provider_name>."""
from __future__ import annotations

from sdk.llm import LLMProvider, LLMResponse, CompletionRequest


class <ProviderName>Provider(LLMProvider):
    """<ProviderName> LLM provider.

    Implements the LLMProvider interface for <provider_name>.
    """

    TIER_MAP: dict[str, str] = {
        "fast": "TODO-fast-model-id",
        "balanced": "TODO-balanced-model-id",
        "powerful": "TODO-powerful-model-id",
    }

    def __init__(self, api_key: str | None = None) -> None:
        # TODO: Initialize provider SDK client
        ...

    async def complete(self, request: CompletionRequest) -> LLMResponse:
        model = self.TIER_MAP[request.tier]
        # TODO: Implement completion using provider SDK
        ...

    async def health_check(self) -> bool:
        # TODO: Implement health check (lightweight API call)
        ...

    def cost_per_token(self, model: str) -> tuple[float, float]:
        # TODO: Return (input_cost_per_token, output_cost_per_token)
        ...
```

### 2. `tests/sdk/llm/test_<provider_name>_provider.py`

Unit tests for the new provider — tests the LLMProvider interface contract.

### 3. Update `sdk/llm/registry.py`

Register the new provider in the provider registry.

## Post-Creation Checklist
- [ ] Fill in TIER_MAP with real model IDs
- [ ] Implement complete(), health_check(), cost_per_token()
- [ ] Add provider-specific environment variables to .env.example
- [ ] Run: `pytest tests/sdk/llm/test_<provider_name>_provider.py -v`
- [ ] Add provider to the documentation (10-API-CONTRACTS provider list response)
```

---

### 4.8 `.claude/skills/new-migration.md` — Migration Scaffolding

```markdown
---
name: new-migration
description: "Scaffold a new PostgreSQL migration with UP and DOWN sections"
usage: "/new-migration <action> <table>"
example: "/new-migration create approvals"
---

# /new-migration — Database Migration Scaffolding

## Usage
```
/new-migration <action> <table>
```

## Arguments
- `<action>`: `create`, `add_column`, `add_index`, `alter`, `seed`.
- `<table>`: Table name (e.g., `approvals`, `knowledge_exceptions`).

## Process

1. Determine next migration number by reading existing files in `migrations/`.
2. Generate migration file with both UP and DOWN sections.
3. Generate test file for the migration.

## Files Created (2 files)

### 1. `migrations/<NNN>_<action>_<table>.sql`

#### For `create` action:

```sql
-- Migration: <NNN>_create_<table>.sql
-- Created: <date>
-- Description: Create <table> table

-- ========== UP ==========

CREATE TABLE IF NOT EXISTS <table> (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- TODO: Define columns
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_<table>_created_at ON <table>(created_at);

-- Row-Level Security
ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;

-- TODO: Define RLS policies
-- CREATE POLICY <table>_tenant_isolation ON <table>
--     USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- ========== DOWN ==========

DROP TABLE IF EXISTS <table>;
```

#### For `add_column` action:

```sql
-- Migration: <NNN>_add_<column>_to_<table>.sql
-- Created: <date>
-- Description: Add <column> column to <table>

-- ========== UP ==========

ALTER TABLE <table> ADD COLUMN IF NOT EXISTS <column> <type> DEFAULT <default>;

-- ========== DOWN ==========

ALTER TABLE <table> DROP COLUMN IF EXISTS <column>;
```

### 2. `tests/migrations/test_<NNN>_<action>_<table>.py`

```python
"""Migration test: <NNN>_<action>_<table>.sql

Verifies:
1. UP applies cleanly
2. DOWN rolls back cleanly
3. UP is idempotent (apply twice without error)
"""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_migration_up(db_pool):
    """Apply UP migration and verify schema."""
    await apply_migration(db_pool, "<NNN>_<action>_<table>.sql", direction="up")
    # Verify table/column exists
    result = await db_pool.fetchval(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '<table>')"
    )
    assert result is True


@pytest.mark.asyncio
async def test_migration_down(db_pool):
    """Apply UP then DOWN and verify clean rollback."""
    await apply_migration(db_pool, "<NNN>_<action>_<table>.sql", direction="up")
    await apply_migration(db_pool, "<NNN>_<action>_<table>.sql", direction="down")
    result = await db_pool.fetchval(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '<table>')"
    )
    assert result is False


@pytest.mark.asyncio
async def test_migration_idempotent(db_pool):
    """Apply UP twice without error (IF NOT EXISTS)."""
    await apply_migration(db_pool, "<NNN>_<action>_<table>.sql", direction="up")
    await apply_migration(db_pool, "<NNN>_<action>_<table>.sql", direction="up")
    # Should not raise
```

## Safety Checks
Before generating a migration, the skill verifies:
- [ ] Migration number is sequential (no gaps, no duplicates)
- [ ] Table name uses `snake_case`
- [ ] `CREATE TABLE` uses `IF NOT EXISTS`
- [ ] `DROP TABLE` (in DOWN) uses `IF EXISTS`
- [ ] `ALTER TABLE ADD COLUMN` has `DEFAULT` or is `NULL`able
- [ ] No `DROP TABLE` in UP section (flags for manual review)
```

---

## 5. Enforcement Summary Matrix

| # | Rule | File | Scope (Globs) | Enforced By | Severity | Key Constraint |
|---|------|------|---------------|-------------|----------|----------------|
| R-01 | Python 3.12+ required | `01-python.md` | `**/*.py` | Claude Code + CI | error | All source files |
| R-02 | Type hints on all functions | `01-python.md` | `**/*.py` | mypy --strict | error | No untyped functions |
| R-03 | Ruff linting (zero errors) | `01-python.md` | `**/*.py` | ruff check + CI | error | Line 120, selected rules |
| R-04 | structlog only (no print/logging) | `01-python.md` | `**/*.py` | Claude Code + Grep CI | error | Forbidden: print(), logging.* |
| R-05 | Async for all I/O | `01-python.md` | `**/*.py` | Claude Code review | error | No blocking calls |
| R-06 | No bare except | `01-python.md` | `**/*.py` | Ruff B001 | error | Catch specific exceptions |
| R-07 | No mutable default args | `01-python.md` | `**/*.py` | Ruff B006 | error | Use None + assign |
| R-08 | **Business logic in services only** | `02-shared-services.md` | `services/**`, `mcp-servers/**`, `api/**`, `dashboard/**` | Claude Code + PR review | **error** | **THE KEY RULE** |
| R-09 | MCP handlers are thin adapters | `02-shared-services.md` | `mcp-servers/**/*.py` | Claude Code + PR review | error | No SQL, no business logic |
| R-10 | REST handlers are thin adapters | `02-shared-services.md` | `api/**/*.py` | Claude Code + PR review | error | No SQL, no business logic |
| R-11 | Dashboard uses REST API only | `02-shared-services.md` | `dashboard/**/*.py` | Claude Code + import check | error | No service/DB imports |
| R-12 | Services are interface-agnostic | `02-shared-services.md` | `services/**/*.py` | Claude Code + import check | error | No MCP/API/Dashboard imports |
| R-13 | Dependency injection via constructor | `02-shared-services.md` | `services/**/*.py` | Claude Code review | error | No global state |
| R-14 | Tool has JSON Schema input_schema | `03-mcp-servers.md` | `mcp-servers/**/*.py` | Claude Code + runtime | error | Every tool validated |
| R-15 | Tool validates inputs before processing | `03-mcp-servers.md` | `mcp-servers/**/*.py` | Claude Code review | error | No raw passthrough |
| R-16 | Structured error responses | `03-mcp-servers.md` | `mcp-servers/**/*.py` | Claude Code + tests | error | No raw exceptions |
| R-17 | Async tool handlers | `03-mcp-servers.md` | `mcp-servers/**/*.py` | mypy + runtime | error | All handlers async |
| R-18 | Audit trail logging | `03-mcp-servers.md` | `mcp-servers/**/*.py` | Claude Code review | error | Every tool call logged |
| R-19 | Health check per server | `03-mcp-servers.md` | `mcp-servers/*/server.py` | CI check | error | 3 servers, 3 health tools |
| R-20 | snake_case verb_noun tool names | `03-mcp-servers.md` | `mcp-servers/**/*.py` | Claude Code review | warning | Naming convention |
| R-21 | Standard response envelope | `04-api-routes.md` | `api/**/*.py` | Claude Code + tests | error | All responses wrapped |
| R-22 | JWT auth for dashboard | `04-api-routes.md` | `api/middleware/auth.py` | CI + integration tests | error | Bearer token required |
| R-23 | API key for programmatic | `04-api-routes.md` | `api/middleware/auth.py` | CI + integration tests | error | X-API-Key header |
| R-24 | Pydantic input validation | `04-api-routes.md` | `api/routes/*.py` | Claude Code + tests | error | All request bodies validated |
| R-25 | Error codes match MCP codes | `04-api-routes.md` | `api/**/*.py` | Parity tests | error | Same codes across interfaces |
| R-26 | Rate limit headers | `04-api-routes.md` | `api/**/*.py` | Integration tests | error | Every response has headers |
| R-27 | All data via REST API | `05-dashboard.md` | `dashboard/**/*.py` | Claude Code + import check | error | No direct service/DB |
| R-28 | WCAG 2.1 AA compliance | `05-dashboard.md` | `dashboard/**/*.py` | Claude Code + manual review | error | ARIA labels, contrast, keyboard |
| R-29 | Loading states for async data | `05-dashboard.md` | `dashboard/**/*.py` | Claude Code review | warning | st.spinner on every fetch |
| R-30 | Error states with retry | `05-dashboard.md` | `dashboard/**/*.py` | Claude Code review | warning | Retry button on every error |
| R-31 | No long inline CSS | `05-dashboard.md` | `dashboard/**/*.py` | Claude Code review | warning | Use st.markdown classes |
| R-32 | Agent directory completeness | `06-agents.md` | `agents/**/*` | CI directory check | error | 7 required files |
| R-33 | manifest.yaml validates | `06-agents.md` | `agents/*/manifest.yaml` | schema_validator.py | error | Against agent-manifest.schema.json |
| R-34 | Extends BaseAgent | `06-agents.md` | `agents/*/agent.py` | Claude Code + mypy | error | No standalone agents |
| R-35 | 3+ golden tests | `06-agents.md` | `agents/*/tests/golden/` | CI check | error | TC-001 through TC-003 minimum |
| R-36 | 1+ adversarial test | `06-agents.md` | `agents/*/tests/adversarial/` | CI check | error | ADV-001 minimum |
| R-37 | No stub prompts | `06-agents.md` | `agents/*/prompt.md` | CI length check | error | Min 500 chars, 5 reasoning steps |
| R-38 | JSON Schema 2020-12 | `07-schemas.md` | `schema/**/*` | schema validator | error | No legacy drafts |
| R-39 | PascalCase data shape names | `07-schemas.md` | `schema/**/*` | Claude Code review | error | Match INTERACTION-MAP |
| R-40 | Single source of truth | `07-schemas.md` | `schema/**/*` | Claude Code + PR review | error | One definition per shape |
| R-41 | UP and DOWN in every migration | `08-migrations.md` | `migrations/**/*.sql` | CI check | error | Both sections required |
| R-42 | No DROP TABLE without approval | `08-migrations.md` | `migrations/**/*.sql` | CI + PR review gate | error | Flags for manual review |
| R-43 | Backwards-compatible ALTER TABLE | `08-migrations.md` | `migrations/**/*.sql` | Claude Code review | error | Default or nullable columns |
| R-44 | testcontainers migration tests | `08-migrations.md` | `tests/migrations/*.py` | CI | error | UP, DOWN, idempotency |
| R-45 | Test file mirrors source | `09-tests.md` | `tests/**/*.py` | Claude Code review | warning | Matching directory structure |
| R-46 | Services 90%+ coverage | `09-tests.md` | `tests/services/*.py` | CI coverage gate | error | Highest priority |
| R-47 | MCP handlers 85%+ coverage | `09-tests.md` | `tests/mcp/*.py` | CI coverage gate | error | Critical interface |
| R-48 | REST handlers 85%+ coverage | `09-tests.md` | `tests/api/*.py` | CI coverage gate | error | Critical interface |
| R-49 | Dashboard 75%+ coverage | `09-tests.md` | `tests/dashboard/*.py` | CI coverage gate | warning | UI layer tolerance |
| R-50 | Real PostgreSQL (no mock DB) | `09-tests.md` | `tests/**/*.py` | Claude Code + CI | error | testcontainers required |
| R-51 | Parity tests for interactions | `09-tests.md` | `tests/integration/*.py` | CI + INTERACTION-MAP check | error | MCP vs REST identical |
| R-52 | No unittest.mock.patch on DB | `09-tests.md` | `tests/**/*.py` | Claude Code review | error | Use real DB |

---

## 6. CI Integration

The rules defined above integrate into CI/CD through these gates:

```yaml
# .github/workflows/enforce.yml (conceptual)
jobs:
  lint:
    steps:
      - run: ruff check . --config pyproject.toml    # R-03, R-06, R-07
      - run: mypy --strict .                          # R-02, R-17

  architecture:
    steps:
      - name: Check shared-service isolation           # R-08 through R-13
        run: |
          # Verify no asyncpg imports outside services/
          ! grep -r "import asyncpg" mcp-servers/ api/ dashboard/
          # Verify no service imports in dashboard/
          ! grep -r "from services" dashboard/
          # Verify no streamlit imports in services/
          ! grep -r "import streamlit" services/ mcp-servers/ api/

  tests:
    steps:
      - run: pytest tests/ --cov --cov-report=xml     # R-46 through R-51
      - name: Coverage gates
        run: |
          coverage report --fail-under=85              # Overall
          # Per-module gates checked in coverage config

  schemas:
    steps:
      - name: Validate JSON Schemas                    # R-38, R-39, R-40
        run: python -m schema.validate_all

  migrations:
    steps:
      - name: Migration safety check                   # R-41, R-42, R-43
        run: |
          # Check for DROP TABLE without approval flag
          python scripts/check_migrations.py

  agents:
    steps:
      - name: Agent directory completeness             # R-32 through R-37
        run: python scripts/check_agent_directories.py
```

---

### 3.10 `.claude/rules/10-prompt-versioning.md` — Prompt Versioning

```markdown
---
description: Prompt versioning and quality gate enforcement for agent prompts
globs: ["agents/**/prompt.md"]
severity: error
---

# Prompt Versioning

## Rules
- Every prompt.md change requires version bump in accompanying manifest.yaml
- SemVer: MAJOR (output schema change), MINOR (instruction refinement), PATCH (typo/formatting)
- Before merging prompt changes: run golden tests, compare quality scores vs previous version
- Quality regression > 5% blocks merge — requires G3-agent-lifecycle-manager review
- Production deployments pin to specific model version via LLM_MODEL_OVERRIDE env var
- No prompt changes without corresponding test updates
```

### 3.11 `.claude/rules/11-api-governance.md` — API Governance

```markdown
---
description: API and MCP tool governance standards
globs: ["api/**/*.py", "mcp/**/*.py"]
severity: error
---

# API Governance

## Rules
- All REST endpoints use the standard envelope: `{"data": ..., "meta": {...}, "errors": [...]}`
- All MCP tools follow naming: `{verb}_{noun}` (e.g., trigger_pipeline, get_cost_report)
- API versioning in URL path: `/api/v1/` — increment major version on breaking changes
- Deprecation policy: 2-sprint minimum warning before removing any endpoint or MCP tool
- New endpoints require: OpenAPI spec entry + integration test + MCP parity check (if applicable)
- Rate limits defined per endpoint — enforced by middleware, not ad-hoc
```

---

## 7. Rule Priority and Conflict Resolution

When rules conflict, priority is (highest first):

1. **02-shared-services.md** (THE KEY RULE) — architectural isolation is non-negotiable.
2. **01-python.md** — language standards apply universally.
3. **Layer-specific rules** (03 through 05) — apply within their glob scope.
4. **06-agents.md** — agent standards.
5. **07-schemas.md, 08-migrations.md** — data layer standards.
6. **09-tests.md** — test standards.

If a test requirement from `09-tests.md` conflicts with an architectural constraint from `02-shared-services.md`, the architectural constraint wins. For example: "never mock DB" in tests does NOT override "dashboard never imports services" — dashboard tests mock REST API calls, not DB calls.

---

## Appendix A: Quick Reference Card

```
ADDING A NEW FEATURE?
  -> /new-interaction <domain> <name>     # Creates all 9 files

ADDING JUST AN MCP TOOL?
  -> /new-mcp-tool <server> <tool_name>   # Creates 3 files

ADDING JUST A REST ROUTE?
  -> /new-api-route <method> <path> <domain>  # Creates 2 files

ADDING A DASHBOARD PAGE?
  -> /new-dashboard-view page <name>       # Creates 2 files

ADDING AN AGENT?
  -> /new-agent <team> <agent-id> <name>   # Creates 9 files

ADDING TESTS?
  -> /new-test <layer> <module>            # Creates 1 file

ADDING A MIGRATION?
  -> /new-migration <action> <table>       # Creates 2 files
```

**Remember:** THE KEY RULE is that all business logic lives in `services/`. If you are writing an `if` statement that checks domain state, it belongs in a service method, not in a tool handler, route handler, or dashboard page.
