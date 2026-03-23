# 06 — Claude Enforcement Layer Specification

> Agentic SDLC Platform — `.claude/` directory structure, rules, skills, and hooks
> Version: 1.0.0 | Status: Canonical | Last updated: 2026-03-23

---

## Table of Contents

1. [Overview](#1-overview)
2. [Directory Layout](#2-directory-layout)
3. [settings.json — Hooks Configuration](#3-settingsjson--hooks-configuration)
4. [Rule Files](#4-rule-files)
   - 4.1 [python.md](#41-clauderulespythonmd)
   - 4.2 [agents.md](#42-clauderulesagentsmd)
   - 4.3 [sdk.md](#43-clauderulessdkmd)
   - 4.4 [schemas.md](#44-clauderulesschemasmd)
   - 4.5 [migrations.md](#45-clauderulesmigrationsmd)
   - 4.6 [tests.md](#46-clauderulestestsmd)
5. [Skill Files](#5-skill-files)
   - 5.1 [new-agent.md](#51-claudeskillsnew-agentmd)
   - 5.2 [new-test.md](#52-claudeskillsnew-testmd)
   - 5.3 [new-migration.md](#53-claudeskillsnew-migrationmd)
   - 5.4 [validate-agent.md](#54-claudeskillsvalidate-agentmd)
6. [Enforcement Summary Matrix](#6-enforcement-summary-matrix)

---

## 1. Overview

The `.claude/` enforcement layer ensures that every code change authored or assisted by Claude Code conforms to the Agentic SDLC Platform standards. It operates at three levels:

| Level | Mechanism | Trigger |
|-------|-----------|---------|
| **Passive** | Rule files (`rules/*.md`) | Activated by glob patterns on every file touched |
| **Active** | Skill files (`skills/*.md`) | Invoked explicitly via `/slash-command` |
| **Gating** | Hooks in `settings.json` | Run automatically on pre-commit and pre-push |

All three levels work together: rules tell Claude *what* to enforce, skills tell Claude *how* to scaffold, and hooks *block* non-conforming code from entering the repository.

---

## 2. Directory Layout

```
.claude/
  settings.json                  # Hook definitions (pre-commit, pre-push)
  rules/
    python.md                    # Activates on **/*.py
    agents.md                    # Activates on agents/**/*
    sdk.md                       # Activates on sdk/**/*.py
    schemas.md                   # Activates on schema/**/*
    migrations.md                # Activates on migrations/**/*.sql
    tests.md                     # Activates on **/tests/**/*
  skills/
    new-agent.md                 # /new-agent <phase> <agent-id>
    new-test.md                  # /new-test <agent-id> <test-type> <test-id>
    new-migration.md             # /new-migration <NNN> <description>
    validate-agent.md            # /validate-agent <agent-id>
```

---

## 3. settings.json — Hooks Configuration

**File: `.claude/settings.json`**

```json
{
  "$schema": "https://claude.ai/schemas/claude-settings.json",
  "project": "agentic-sdlc",
  "description": "Agentic SDLC Platform — enforcement hooks and permissions",

  "hooks": {
    "pre-commit": [
      {
        "name": "ruff-check",
        "command": "python -m ruff check --config pyproject.toml .",
        "description": "Lint all Python files with Ruff (E, F, W, I, UP, S, B, A, COM, C4, DTZ, ISC, PIE, T20, RSE, RET, SIM, TCH, ERA, PL, TRY, RUF)",
        "fail_on_error": true
      },
      {
        "name": "ruff-format-check",
        "command": "python -m ruff format --check --config pyproject.toml .",
        "description": "Verify Ruff formatting (line-length=120, target-version=py312)",
        "fail_on_error": true
      },
      {
        "name": "mypy-strict",
        "command": "python -m mypy --strict --python-version 3.12 --config-file pyproject.toml .",
        "description": "Run mypy in strict mode — all functions must have type hints",
        "fail_on_error": true
      },
      {
        "name": "manifest-validation",
        "command": "python -m scripts.validate_manifests --schema schema/agent-manifest.schema.json --agents-dir agents/",
        "description": "Validate every agent manifest.yaml against the canonical JSON schema",
        "fail_on_error": true
      },
      {
        "name": "forbidden-pattern-scan",
        "command": "python -m scripts.forbidden_patterns --config .claude/forbidden-patterns.yaml .",
        "description": "Grep for forbidden patterns: print(, import *, bare except:, time.sleep, hardcoded secrets, sqlite in tests",
        "fail_on_error": true
      },
      {
        "name": "secret-scan",
        "command": "python -m scripts.secret_scan --patterns 'sk-ant-,postgresql://,AKIA,ghp_,ghu_' .",
        "description": "Block hardcoded API keys, connection strings, and AWS credentials",
        "fail_on_error": true
      }
    ],

    "pre-push": [
      {
        "name": "pytest-full",
        "command": "python -m pytest tests/ agents/*/tests/ --asyncio-mode=auto -x -q --tb=short",
        "description": "Run all tests (unit + agent golden/adversarial) before push",
        "fail_on_error": true,
        "timeout_seconds": 300
      },
      {
        "name": "coverage-check",
        "command": "python -m pytest tests/ agents/*/tests/ --asyncio-mode=auto --cov=sdk --cov=orchestration --cov=api --cov-report=term-missing --cov-fail-under=80",
        "description": "Enforce minimum coverage: 90% SDK, 85% orchestration, 80% API",
        "fail_on_error": true,
        "timeout_seconds": 300
      },
      {
        "name": "rubric-integrity",
        "command": "python -m scripts.validate_rubrics --agents-dir agents/",
        "description": "Verify every rubric.yaml has 4 dimensions summing to 1.0",
        "fail_on_error": true
      }
    ]
  },

  "permissions": {
    "allow_shell": true,
    "allow_file_write": true,
    "allow_file_read": true,
    "restricted_paths": [
      ".env",
      ".env.*",
      "secrets/",
      "*.pem",
      "*.key"
    ]
  },

  "context": {
    "always_include": [
      "CLAUDE.md",
      "pyproject.toml"
    ]
  }
}
```

---

## 4. Rule Files

Each rule file is automatically activated when Claude touches files matching the specified glob pattern. Rules are enforced passively — Claude reads them before generating or modifying code and must comply with every item.

---

### 4.1 `.claude/rules/python.md`

**File: `.claude/rules/python.md`**

```markdown
---
activates_on: "**/*.py"
priority: 100
---

# Python Rules — Agentic SDLC Platform

These rules apply to EVERY Python file in the repository. Violations are blocking.

## Language & Runtime

- Python 3.12 ONLY. No TypeScript, Go, or any other language.
- All agent code MUST be async: use `async def`, `await`, and `asyncio`.
- Framework: `aiohttp` for HTTP servers/clients, `Streamlit` for dashboards.

## Type Hints (mypy --strict)

- Every function MUST have full type annotations on all parameters and return type.
- Every variable where the type is not obvious from assignment MUST be annotated.
- No `# type: ignore` without an inline explanation in parentheses:
  - FORBIDDEN: `x = foo()  # type: ignore`
  - ALLOWED: `x = foo()  # type: ignore[override] (parent class uses Any)`
- Use `from __future__ import annotations` at the top of every module.

## Linting (Ruff)

- Line length: 120 characters maximum.
- Target version: py312.
- Enabled rule sets: E, F, W, I, UP, S, B, A, COM, C4, DTZ, ISC, PIE, T20, RSE, RET, SIM, TCH, ERA, PL, TRY, RUF.
- All Ruff violations are blocking — fix them, do not suppress.

## Import Ordering

- Imports are sorted by Ruff (isort rules I001, I002).
- Order: stdlib -> third-party -> local.
- NEVER use `import *` — always import specific names.
- Group imports with a single blank line between each group.

## Logging

- NEVER use `print()`. Use `structlog` for all logging.
  - `import structlog` then `logger = structlog.get_logger()`.
  - Use `logger.info()`, `logger.warning()`, `logger.error()`, `logger.debug()`.

## Error Handling

- NEVER use bare `except:` — always catch a specific exception type.
  - FORBIDDEN: `except:`
  - FORBIDDEN: `except Exception:`  (too broad unless re-raised)
  - ALLOWED: `except ValueError as e:`
  - ALLOWED: `except (TimeoutError, ConnectionError) as e:`
- If you must catch `Exception`, you MUST re-raise or log with `logger.exception()`.

## Async Discipline

- NEVER use `time.sleep()` in async code — use `await asyncio.sleep()`.
- NEVER use synchronous I/O (open, requests) in async functions — use `aiofiles`, `aiohttp`.
- All database calls MUST be async (asyncpg, not psycopg2).

## Forbidden Patterns

The following patterns are greppable and will be caught by the pre-commit hook:

| Pattern | Reason | Replacement |
|---------|--------|-------------|
| `print(` | No print statements | `structlog.get_logger()` |
| `import *` | No wildcard imports | Explicit named imports |
| `except:` | No bare except | `except SpecificError:` |
| `time.sleep` | Blocking in async | `await asyncio.sleep()` |
| `# type: ignore` (no comment) | Unexplained suppression | Add parenthetical reason |
| `sk-ant-` | Hardcoded Anthropic key | Environment variable / secrets manager |
| `postgresql://` | Hardcoded connection string | Environment variable / secrets manager |
| `TODO` (no parenthetical) | Unexplained TODO | `TODO(reason)` or `TODO(author): explanation` |

## Mutable Defaults

- NEVER use mutable default arguments in function signatures.
  - FORBIDDEN: `def foo(items: list[str] = []):`
  - ALLOWED: `def foo(items: list[str] | None = None):`

## Database

- PostgreSQL ONLY. No SQLite, no MongoDB, no DynamoDB.
- Use asyncpg for async database access.
- All multi-tenant tables MUST have Row-Level Security (RLS) policies.
- Connection strings come from environment variables, never hardcoded.

## Security

- No hardcoded API keys, passwords, tokens, or connection strings.
- TLS 1.2+ for all external connections.
- No secrets in agent output — PII scan is enforced.
```

---

### 4.2 `.claude/rules/agents.md`

**File: `.claude/rules/agents.md`**

```markdown
---
activates_on: "agents/**/*"
priority: 90
---

# Agent Rules — Agentic SDLC Platform

These rules apply to ALL files under the `agents/` directory.

## Agent Directory Structure

Every agent MUST have the following directory structure. No exceptions.

```
agents/<agent-id>/
  manifest.yaml        # Agent manifest — validates against schema
  prompt.md            # System prompt for the agent
  agent.py             # Agent implementation (extends BaseAgent)
  hooks.py             # Lifecycle hooks (pre_run, post_run, on_error)
  tools.py             # Agent-specific tool definitions
  rubric.yaml          # Evaluation rubric (4 dimensions, sum to 1.0)
  tests/
    test_<agent-id>.py          # Unit + integration tests
    golden/                     # Golden test fixtures (minimum 3)
      golden-001.yaml
      golden-002.yaml
      golden-003.yaml
    adversarial/                # Adversarial test fixtures (minimum 1)
      adversarial-001.yaml
```

## Agent Naming

- Agent folder name MUST match the agent ID: `<phase-prefix><number>-<kebab-name>`.
  - Examples: `G1-cost-tracker`, `P2-test-writer`, `D3-api-builder`.
- Phase prefixes: G (Governance), P (Planning), D (Development), Q (Quality), R (Release), O (Ops).
- Test file name: `test_<agent_id_with_underscores>.py` (e.g., `test_G1_cost_tracker.py`).

## Spec-First Development

- ALWAYS create `manifest.yaml` + `prompt.md` BEFORE writing `agent.py`.
- The manifest is the contract. The implementation follows the contract.
- Refer to `G1-cost-tracker` as the gold-standard reference agent.

## Agent Base Class

- Every agent MUST extend `BaseAgent` from `sdk/base_agent.py`.
- Every agent MUST import: `from claude_agent_sdk import query, ClaudeAgentOptions`.
- The `run()` method MUST be `async def run(self, ...) -> AgentResult:`.
- NEVER instantiate agents directly — use the agent registry.

## Manifest Requirements

- Every `manifest.yaml` MUST validate against `schema/agent-manifest.schema.json`.
- Every manifest MUST have exactly 9 subsystems:
  1. `identity` — agent ID, name, version, phase
  2. `triggers` — what events activate this agent
  3. `inputs` — required input schema
  4. `outputs` — output schema and artifacts
  5. `dependencies` — upstream/downstream agent references
  6. `resources` — compute, memory, token budget
  7. `security` — permissions, RLS scope, secret references
  8. `observability` — metrics, logs, traces configuration
  9. `lifecycle` — hooks, retry policy, timeout
- Missing or extra subsystems are a blocking violation.

## Rubric Requirements

- Every `rubric.yaml` MUST have exactly 4 evaluation dimensions.
- The weights of all 4 dimensions MUST sum to exactly 1.0.
- Each dimension MUST have: `name`, `weight` (float), `description`, `scoring` (1-5 scale criteria).
- Standard dimensions (customize per agent):
  - `correctness` — Does the output match the spec?
  - `completeness` — Are all required artifacts produced?
  - `quality` — Code quality, formatting, best practices.
  - `safety` — Security, no PII leaks, no secrets exposed.

## Hooks (hooks.py)

- Every `hooks.py` MUST implement at minimum:
  - `async def pre_run(context: AgentContext) -> AgentContext:`
  - `async def post_run(context: AgentContext, result: AgentResult) -> AgentResult:`
  - `async def on_error(context: AgentContext, error: Exception) -> ErrorAction:`
- Hooks MUST NOT swallow exceptions silently. Log with structlog and re-raise or return an ErrorAction.

## Tools (tools.py)

- Every tool function MUST have a docstring describing its purpose, parameters, and return value.
- Tools MUST be async.
- Tools MUST validate their inputs before execution.
- Tools MUST NOT access secrets directly — use the secrets manager via `context.secrets`.

## Prompt (prompt.md)

- The system prompt MUST include:
  - Role definition (who is this agent?).
  - Input/output contract (what does it receive and produce?).
  - Constraints and guardrails.
  - Examples (at least one positive, one negative).
- NEVER include hardcoded keys, URLs, or PII in prompts.
```

---

### 4.3 `.claude/rules/sdk.md`

**File: `.claude/rules/sdk.md`**

```markdown
---
activates_on: "sdk/**/*.py"
priority: 95
---

# SDK Rules — Agentic SDLC Platform

These rules apply to ALL Python files under the `sdk/` directory. The SDK is the shared
foundation that every agent depends on. Changes here have the highest blast radius.

## Coverage Requirement

- SDK modules MUST maintain 90% test coverage minimum.
- Every public function and class MUST have at least one unit test.
- Every error path MUST have at least one test that triggers it.

## BaseAgent Contract

- `sdk/base_agent.py` defines `BaseAgent`. ALL agents extend this class.
- The BaseAgent interface is:

```python
class BaseAgent(ABC):
    async def run(self, context: AgentContext) -> AgentResult: ...
    async def validate_inputs(self, inputs: dict[str, Any]) -> ValidationResult: ...
    async def validate_outputs(self, result: AgentResult) -> ValidationResult: ...
    def get_manifest(self) -> AgentManifest: ...
```

- NEVER modify the `BaseAgent` interface without updating ALL agents that extend it.
- NEVER remove a method from `BaseAgent` — only add new optional methods with defaults.

## ClaudeAgentSDK Exports

- The `claude_agent_sdk` package MUST export at minimum:
  - `query` — the function to call the Claude API.
  - `ClaudeAgentOptions` — configuration for API calls.
  - `BaseAgent` — the base class for agents.
  - `AgentContext` — runtime context passed to agents.
  - `AgentResult` — the return type from agent runs.
- All public exports MUST be listed in `__all__` in `__init__.py`.

## Async Patterns

- All SDK public functions MUST be async.
- Use `asyncio.TaskGroup` (Python 3.11+) for concurrent operations, not `gather`.
- All database access MUST go through `sdk/db.py` — no direct asyncpg calls from agents.
- Connection pooling is mandatory — use `asyncpg.create_pool()`.

## Error Hierarchy

- All SDK exceptions MUST extend `sdk.exceptions.SDLCError`.
- Exception hierarchy:
  - `SDLCError` (base)
    - `AgentError` — agent runtime failures
    - `ValidationError` — input/output validation failures
    - `ManifestError` — manifest parsing/validation failures
    - `SecretError` — secret access failures
    - `DatabaseError` — database operation failures
- NEVER raise bare `Exception` or `RuntimeError` from SDK code.

## Observability

- All SDK functions MUST use `structlog` for logging.
- All SDK functions that perform I/O MUST emit OpenTelemetry spans.
- Use `sdk/telemetry.py` for span creation — do not create spans directly.
- Every span MUST include: `agent_id`, `operation`, `duration_ms`.

## Versioning

- SDK follows semver. Breaking changes require a major version bump.
- The SDK version is defined in `sdk/__init__.py` as `__version__`.
- NEVER introduce a breaking change without a migration guide.

## Immutability of Core Interfaces

- `AgentContext`, `AgentResult`, `AgentManifest` MUST be dataclasses or Pydantic models.
- These types MUST be immutable (frozen=True for dataclasses, `model_config = ConfigDict(frozen=True)` for Pydantic).
- NEVER use mutable state on these core types.
```

---

### 4.4 `.claude/rules/schemas.md`

**File: `.claude/rules/schemas.md`**

```markdown
---
activates_on: "schema/**/*"
priority: 85
---

# Schema Rules — Agentic SDLC Platform

These rules apply to ALL files under the `schema/` directory.

## Canonical Schema

- `schema/agent-manifest.schema.json` is the single source of truth for agent manifests.
- EVERY `manifest.yaml` in `agents/*/` MUST validate against this schema.
- The schema MUST enforce exactly 9 required top-level subsystems:
  `identity`, `triggers`, `inputs`, `outputs`, `dependencies`, `resources`, `security`, `observability`, `lifecycle`.

## Schema Modification Protocol

- NEVER remove a required field from the schema — this is a breaking change.
- Adding a new optional field is non-breaking and allowed.
- Adding a new required field requires:
  1. A migration script to update all existing manifests.
  2. An update to the gold-standard agent (G1-cost-tracker).
  3. A version bump in the schema's `$id` or `version` field.
- Schema changes MUST be reviewed and tested against ALL existing agent manifests before merge.

## Schema File Naming

- JSON Schema files: `<subject>.schema.json` (e.g., `agent-manifest.schema.json`).
- YAML schema overlays: `<subject>.schema.yaml` — NEVER use YAML as the canonical schema format.
- Filename must be lowercase-hyphenated.

## Validation Rules

- All `enum` fields in the schema MUST have explicit allowed values — no open-ended strings for structured fields.
- All `string` fields that represent identifiers MUST have a `pattern` constraint (regex).
- Agent ID pattern: `^[A-Z][0-9]+-[a-z0-9-]+$` (e.g., `G1-cost-tracker`).
- Version fields MUST follow semver pattern: `^\d+\.\d+\.\d+$`.

## Schema Testing

- Every schema MUST have a corresponding test file: `tests/test_schema_<name>.py`.
- Tests MUST include:
  - At least 3 valid manifests that pass validation.
  - At least 3 invalid manifests that fail validation (missing fields, wrong types, extra subsystems).
  - Edge cases: empty strings, null values, boundary values.

## Documentation

- Every schema property MUST have a `description` field explaining its purpose.
- Every schema MUST have a top-level `title` and `description`.
- Complex types MUST have `examples` in the schema.
```

---

### 4.5 `.claude/rules/migrations.md`

**File: `.claude/rules/migrations.md`**

```markdown
---
activates_on: "migrations/**/*.sql"
priority: 80
---

# Migration Rules — Agentic SDLC Platform

These rules apply to ALL SQL migration files under `migrations/`.

## File Naming

- Migration files MUST be named: `NNN_description.sql` where NNN is a zero-padded 3-digit sequence number.
  - Examples: `001_create_agents_table.sql`, `042_add_cost_tracking_index.sql`.
- Description MUST be lowercase, underscore-separated, and descriptive of the change.
- Sequence numbers MUST be strictly monotonically increasing — no gaps, no duplicates.

## Database Engine

- PostgreSQL ONLY. No SQLite, no MySQL, no MongoDB.
- Use PostgreSQL-specific features freely: JSONB, arrays, CTEs, window functions, RLS.
- Target PostgreSQL 15+ — use modern syntax.

## Migration Structure

Every migration file MUST follow this structure:

```sql
-- Migration: NNN_description
-- Created: YYYY-MM-DD
-- Author: <agent-id or human>
-- Description: <what this migration does and why>

BEGIN;

-- === UP Migration ===

<DDL statements here>

-- === RLS Policies ===

<RLS policies for any new tables>

COMMIT;
```

## Row-Level Security (RLS)

- EVERY table that stores tenant-scoped data MUST have RLS enabled:
  ```sql
  ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;
  ```
- EVERY RLS-enabled table MUST have at least one policy:
  ```sql
  CREATE POLICY <policy_name> ON <table>
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
  ```
- RLS policies MUST cover SELECT, INSERT, UPDATE, and DELETE.
- NEVER create a table with a `tenant_id` column without enabling RLS.

## Safety Rules

- NEVER use `DROP TABLE` without `IF EXISTS`.
- NEVER use `DELETE FROM <table>` without a `WHERE` clause in a migration.
- NEVER use `TRUNCATE` in a migration — it bypasses RLS.
- ALL DDL operations MUST be wrapped in a transaction (`BEGIN; ... COMMIT;`).
- Add `IF NOT EXISTS` to `CREATE TABLE` and `CREATE INDEX` statements.
- Use `ADD COLUMN IF NOT EXISTS` for column additions.

## Index Requirements

- Every foreign key column MUST have an index.
- Every column used in a `WHERE` clause frequently MUST have an index.
- Use `CREATE INDEX CONCURRENTLY` for indexes on large tables (add a comment if non-concurrent is intentional).
- Name indexes: `idx_<table>_<column(s)>`.

## Rollback

- Every migration SHOULD have a corresponding rollback comment or script.
- If a migration is not safely reversible, it MUST include a comment: `-- IRREVERSIBLE: <reason>`.
```

---

### 4.6 `.claude/rules/tests.md`

**File: `.claude/rules/tests.md`**

```markdown
---
activates_on: "**/tests/**/*"
priority: 90
---

# Testing Rules — Agentic SDLC Platform

These rules apply to ALL test files anywhere in the repository.

## Framework

- Use `pytest` with `pytest-asyncio` for all tests.
- Async test mode: `asyncio_mode = "auto"` in `pyproject.toml`.
- Every async test function MUST be `async def test_*():` (the auto mode handles the rest).

## Coverage Thresholds

| Module | Minimum Coverage |
|--------|-----------------|
| `sdk/` | 90% |
| `orchestration/` | 85% |
| `api/` | 80% |
| `agents/*/` | Per-agent rubric |

## Test File Naming

- Test files: `test_<module_name>.py` (e.g., `test_base_agent.py`).
- Agent test files: `test_<agent_id_underscored>.py` (e.g., `test_G1_cost_tracker.py`).
- Fixture files: `conftest.py` in each test directory.

## Database in Tests

- NEVER use SQLite in tests. NEVER mock the database with in-memory SQLite.
  - FORBIDDEN: `sqlite` anywhere in test files.
  - FORBIDDEN: `mock.patch("...database` — do not mock database calls.
- Use `testcontainers` to spin up a real PostgreSQL instance for integration tests:
  ```python
  from testcontainers.postgres import PostgresContainer
  ```
- Unit tests that need DB fixtures MUST use `testcontainers` or a shared test PostgreSQL.

## Agent Test Requirements

Every agent MUST have:

- **3+ golden tests**: Known-good input/output pairs in `tests/golden/golden-NNN.yaml`.
- **1+ adversarial test**: Edge cases, malicious inputs, boundary conditions in `tests/adversarial/adversarial-NNN.yaml`.

### Golden Test YAML Format

```yaml
id: golden-001
agent_id: G1-cost-tracker
description: "Standard cost tracking for a 3-agent pipeline"
input:
  pipeline_id: "pipe-001"
  agents: ["G1-cost-tracker", "P1-backlog-writer", "D1-code-builder"]
  budget_usd: 10.00
expected_output:
  status: "completed"
  total_cost_usd: 3.47
  per_agent_costs:
    G1-cost-tracker: 0.82
    P1-backlog-writer: 1.15
    D1-code-builder: 1.50
  under_budget: true
assertions:
  - "result.status == 'completed'"
  - "result.total_cost_usd < input.budget_usd"
  - "len(result.per_agent_costs) == len(input.agents)"
```

### Adversarial Test YAML Format

```yaml
id: adversarial-001
agent_id: G1-cost-tracker
description: "Negative budget should be rejected"
input:
  pipeline_id: "pipe-evil"
  agents: ["G1-cost-tracker"]
  budget_usd: -5.00
expected_behavior: "reject"
expected_error: "ValidationError"
assertions:
  - "error.type == 'ValidationError'"
  - "'budget' in error.message.lower()"
```

## Test Patterns

- Use `pytest.fixture` for reusable setup — not test class inheritance.
- Use `pytest.mark.parametrize` for testing multiple inputs against the same logic.
- Group related tests in classes: `class TestCostTracker:`.
- Use descriptive test names: `test_rejects_negative_budget`, not `test_1`.

## Forbidden in Tests

| Pattern | Reason | Replacement |
|---------|--------|-------------|
| `sqlite` | No SQLite in tests | `testcontainers.postgres` |
| `mock.patch("...database` | No mocking the DB | Real PostgreSQL via testcontainers |
| `print(` | No print in tests | `structlog` or `pytest` captured output |
| `time.sleep` | No blocking sleep | `await asyncio.sleep()` or `pytest-timeout` |
| `assert True` | Meaningless assertion | Assert specific values |
| `# noqa` in tests | No lint suppression in tests | Fix the lint violation |

## Fixtures (conftest.py)

- Every test directory MUST have a `conftest.py`.
- Standard fixtures to provide:
  - `db_pool` — asyncpg connection pool to test PostgreSQL.
  - `agent_context` — pre-configured `AgentContext` for agent tests.
  - `sample_manifest` — a valid `AgentManifest` loaded from fixtures.
- Fixtures MUST clean up after themselves (use `yield` + teardown).
```

---

## 5. Skill Files

Skills are invoked explicitly by the developer via `/slash-command`. Each skill provides a step-by-step scaffolding procedure that Claude follows exactly.

---

### 5.1 `.claude/skills/new-agent.md`

**File: `.claude/skills/new-agent.md`**

```markdown
---
skill: new-agent
usage: "/new-agent <phase> <agent-id>"
description: "Scaffold a complete agent directory with all required files and tests"
---

# Skill: /new-agent

## Usage

```
/new-agent <phase> <agent-id>
```

**Parameters:**
- `<phase>` — One of: G (Governance), P (Planning), D (Development), Q (Quality), R (Release), O (Ops)
- `<agent-id>` — Full agent ID in format `<Phase><N>-<kebab-name>` (e.g., `G1-cost-tracker`)

**Example:**
```
/new-agent D D3-api-builder
```

## Procedure

When this skill is invoked, follow these steps IN ORDER:

### Step 1: Validate Arguments

1. Verify `<phase>` is one of: G, P, D, Q, R, O.
2. Verify `<agent-id>` matches pattern `^[A-Z][0-9]+-[a-z0-9-]+$`.
3. Verify the phase prefix in `<agent-id>` matches `<phase>`.
4. Verify `agents/<agent-id>/` does NOT already exist.
5. If any check fails, report the error and STOP.

### Step 2: Create manifest.yaml (FIRST — spec-first)

Create `agents/<agent-id>/manifest.yaml` with ALL 9 required subsystems:

```yaml
# Agent Manifest: <agent-id>
# Generated: <current-date>
# Schema: schema/agent-manifest.schema.json

identity:
  id: "<agent-id>"
  name: "<Human Readable Name>"
  version: "0.1.0"
  phase: "<phase-full-name>"
  description: "<One-line description>"

triggers:
  events:
    - type: "manual"
      description: "Triggered manually or by orchestrator"
  schedule: null

inputs:
  schema:
    type: object
    required: []
    properties: {}

outputs:
  schema:
    type: object
    required: []
    properties: {}
  artifacts: []

dependencies:
  upstream: []
  downstream: []

resources:
  max_tokens: 4096
  max_duration_seconds: 120
  compute: "standard"

security:
  permissions: []
  rls_scope: "tenant"
  secrets: []

observability:
  metrics:
    - name: "<agent-id>_runs_total"
      type: "counter"
    - name: "<agent-id>_duration_seconds"
      type: "histogram"
  log_level: "info"
  trace_sampling_rate: 1.0

lifecycle:
  hooks:
    pre_run: true
    post_run: true
    on_error: true
  retry:
    max_attempts: 3
    backoff: "exponential"
    initial_delay_seconds: 1
  timeout_seconds: 120
```

### Step 3: Create prompt.md (SECOND — spec-first)

Create `agents/<agent-id>/prompt.md`:

```markdown
# System Prompt: <agent-id>

## Role
You are <agent-name>, a <phase> agent in the Agentic SDLC Platform.

## Responsibility
<Describe what this agent does in 2-3 sentences.>

## Input Contract
You will receive:
- <List input fields from manifest>

## Output Contract
You must produce:
- <List output fields from manifest>

## Constraints
- You MUST complete within <timeout> seconds.
- You MUST NOT exceed <max_tokens> tokens.
- You MUST NOT expose secrets or PII in your output.

## Examples

### Positive Example
<Provide a realistic positive example>

### Negative Example
<Provide a realistic negative example — what NOT to do>
```

### Step 4: Create agent.py

Create `agents/<agent-id>/agent.py`:

```python
"""Agent implementation for <agent-id>."""

from __future__ import annotations

from typing import Any

import structlog
from claude_agent_sdk import ClaudeAgentOptions, query

from sdk.base_agent import BaseAgent
from sdk.types import AgentContext, AgentResult, ValidationResult

logger = structlog.get_logger()


class <AgentClassName>(BaseAgent):
    """<One-line description of the agent>."""

    async def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent's primary task."""
        logger.info("<agent-id>.run.start", agent_id=context.agent_id)

        # Validate inputs
        validation = await self.validate_inputs(context.inputs)
        if not validation.is_valid:
            logger.error("<agent-id>.run.invalid_inputs", errors=validation.errors)
            return AgentResult(
                agent_id=context.agent_id,
                status="failed",
                errors=validation.errors,
            )

        # TODO(<agent-id>): Implement agent logic
        result = AgentResult(
            agent_id=context.agent_id,
            status="completed",
            outputs={},
        )

        logger.info("<agent-id>.run.complete", agent_id=context.agent_id)
        return result

    async def validate_inputs(self, inputs: dict[str, Any]) -> ValidationResult:
        """Validate agent inputs against the manifest schema."""
        # TODO(<agent-id>): Implement input validation
        return ValidationResult(is_valid=True, errors=[])

    async def validate_outputs(self, result: AgentResult) -> ValidationResult:
        """Validate agent outputs against the manifest schema."""
        # TODO(<agent-id>): Implement output validation
        return ValidationResult(is_valid=True, errors=[])
```

### Step 5: Create hooks.py

Create `agents/<agent-id>/hooks.py`:

```python
"""Lifecycle hooks for <agent-id>."""

from __future__ import annotations

import structlog

from sdk.types import AgentContext, AgentResult, ErrorAction

logger = structlog.get_logger()


async def pre_run(context: AgentContext) -> AgentContext:
    """Execute before the agent runs. Validate preconditions."""
    logger.info("<agent-id>.hooks.pre_run", agent_id=context.agent_id)
    return context


async def post_run(context: AgentContext, result: AgentResult) -> AgentResult:
    """Execute after the agent completes. Post-process results."""
    logger.info(
        "<agent-id>.hooks.post_run",
        agent_id=context.agent_id,
        status=result.status,
    )
    return result


async def on_error(context: AgentContext, error: Exception) -> ErrorAction:
    """Handle agent errors. Decide whether to retry or abort."""
    logger.exception(
        "<agent-id>.hooks.on_error",
        agent_id=context.agent_id,
        error=str(error),
    )
    return ErrorAction.RETRY
```

### Step 6: Create tools.py

Create `agents/<agent-id>/tools.py`:

```python
"""Tool definitions for <agent-id>."""

from __future__ import annotations

from typing import Any

import structlog

from sdk.types import AgentContext

logger = structlog.get_logger()


async def example_tool(context: AgentContext, param: str) -> dict[str, Any]:
    """Example tool — replace with actual tool implementations.

    Args:
        context: The agent runtime context.
        param: Description of the parameter.

    Returns:
        A dictionary containing the tool result.
    """
    # TODO(<agent-id>): Implement actual tools
    logger.info("<agent-id>.tools.example_tool", param=param)
    return {"status": "ok", "result": param}
```

### Step 7: Create rubric.yaml

Create `agents/<agent-id>/rubric.yaml`:

```yaml
# Evaluation Rubric: <agent-id>
# Dimensions MUST sum to 1.0

dimensions:
  - name: correctness
    weight: 0.35
    description: "Does the output match the expected result?"
    scoring:
      5: "Perfect match to expected output"
      4: "Minor deviations, all key fields correct"
      3: "Mostly correct, some fields missing or wrong"
      2: "Significant errors in output"
      1: "Completely wrong or no output"

  - name: completeness
    weight: 0.25
    description: "Are all required artifacts and fields produced?"
    scoring:
      5: "All artifacts present and fully populated"
      4: "All required artifacts present, optional ones missing"
      3: "Most artifacts present, some required ones missing"
      2: "Many required artifacts missing"
      1: "No artifacts produced"

  - name: quality
    weight: 0.25
    description: "Code quality, formatting, and adherence to standards"
    scoring:
      5: "Exemplary code quality, no lint issues"
      4: "Good quality, minor style issues"
      3: "Acceptable quality, some issues"
      2: "Poor quality, multiple violations"
      1: "Unacceptable quality"

  - name: safety
    weight: 0.15
    description: "No secrets exposed, no PII leaked, security rules followed"
    scoring:
      5: "Perfect security compliance"
      4: "Minor security warnings, no actual exposures"
      3: "Some security concerns, no critical issues"
      2: "Security violations detected"
      1: "Critical security breach (secrets/PII exposed)"
```

### Step 8: Create test scaffolding

Create the following test files:

**`agents/<agent-id>/tests/__init__.py`** — empty file.

**`agents/<agent-id>/tests/conftest.py`**:

```python
"""Test fixtures for <agent-id>."""

from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from testcontainers.postgres import PostgresContainer

from sdk.types import AgentContext


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    """Spin up a PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:15") as pg:
        yield pg


@pytest.fixture
def agent_context() -> AgentContext:
    """Create a test AgentContext."""
    return AgentContext(
        agent_id="<agent-id>",
        tenant_id="test-tenant-001",
        inputs={},
        secrets=AsyncMock(),
    )
```

**`agents/<agent-id>/tests/test_<agent_id_underscored>.py`**:

```python
"""Tests for <agent-id>."""

from __future__ import annotations

import pytest

from agents.<agent_id_dotted>.agent import <AgentClassName>
from sdk.types import AgentContext


class Test<AgentClassName>:
    """Test suite for <AgentClassName>."""

    async def test_run_completes_successfully(
        self, agent_context: AgentContext
    ) -> None:
        """Test that the agent runs and returns a completed result."""
        agent = <AgentClassName>()
        result = await agent.run(agent_context)
        assert result.status == "completed"

    async def test_validate_inputs_accepts_valid_input(
        self, agent_context: AgentContext
    ) -> None:
        """Test that valid inputs pass validation."""
        agent = <AgentClassName>()
        validation = await agent.validate_inputs(agent_context.inputs)
        assert validation.is_valid

    async def test_validate_inputs_rejects_invalid_input(
        self, agent_context: AgentContext
    ) -> None:
        """Test that invalid inputs are rejected."""
        agent = <AgentClassName>()
        # TODO(<agent-id>): Add invalid input fixture
        validation = await agent.validate_inputs({})
        assert validation.is_valid  # Update after implementing validation
```

### Step 9: Create golden and adversarial test fixtures

**`agents/<agent-id>/tests/golden/golden-001.yaml`**:
```yaml
id: golden-001
agent_id: "<agent-id>"
description: "Basic successful execution"
input: {}
expected_output:
  status: "completed"
assertions:
  - "result.status == 'completed'"
```

**`agents/<agent-id>/tests/golden/golden-002.yaml`**:
```yaml
id: golden-002
agent_id: "<agent-id>"
description: "Execution with full input parameters"
input: {}
expected_output:
  status: "completed"
assertions:
  - "result.status == 'completed'"
```

**`agents/<agent-id>/tests/golden/golden-003.yaml`**:
```yaml
id: golden-003
agent_id: "<agent-id>"
description: "Edge case — minimal valid input"
input: {}
expected_output:
  status: "completed"
assertions:
  - "result.status == 'completed'"
```

**`agents/<agent-id>/tests/adversarial/adversarial-001.yaml`**:
```yaml
id: adversarial-001
agent_id: "<agent-id>"
description: "Malformed input should be rejected gracefully"
input:
  __inject__: "'; DROP TABLE agents; --"
expected_behavior: "reject"
expected_error: "ValidationError"
assertions:
  - "error.type == 'ValidationError'"
```

### Step 10: Validate

After creating all files, run:
1. `python -m scripts.validate_manifests --schema schema/agent-manifest.schema.json --agent agents/<agent-id>/manifest.yaml`
2. `python -m ruff check agents/<agent-id>/`
3. `python -m mypy --strict agents/<agent-id>/`

Report the results. If any check fails, fix the issue before finishing.
```

---

### 5.2 `.claude/skills/new-test.md`

**File: `.claude/skills/new-test.md`**

```markdown
---
skill: new-test
usage: "/new-test <agent-id> <test-type> <test-id>"
description: "Create a golden or adversarial test YAML fixture for an agent"
---

# Skill: /new-test

## Usage

```
/new-test <agent-id> <test-type> <test-id>
```

**Parameters:**
- `<agent-id>` — Full agent ID (e.g., `G1-cost-tracker`)
- `<test-type>` — One of: `golden`, `adversarial`
- `<test-id>` — Test ID (e.g., `golden-004`, `adversarial-002`)

**Example:**
```
/new-test G1-cost-tracker golden golden-004
```

## Procedure

### Step 1: Validate Arguments

1. Verify `agents/<agent-id>/` exists.
2. Verify `<test-type>` is either `golden` or `adversarial`.
3. Verify `<test-id>` follows the pattern `<test-type>-NNN`.
4. Verify the target file does NOT already exist.
5. If any check fails, report the error and STOP.

### Step 2: Read Agent Context

1. Read `agents/<agent-id>/manifest.yaml` to understand the input/output schemas.
2. Read `agents/<agent-id>/prompt.md` to understand the agent's purpose.
3. Read existing test fixtures in `agents/<agent-id>/tests/<test-type>/` for consistency.

### Step 3: Create Test Fixture

**For golden tests** — create `agents/<agent-id>/tests/golden/<test-id>.yaml`:

```yaml
id: "<test-id>"
agent_id: "<agent-id>"
description: "<Describe what this test validates>"
input:
  # Populate with realistic values from the manifest input schema
  <field>: <value>
expected_output:
  status: "completed"
  # Populate with expected values from the manifest output schema
  <field>: <value>
assertions:
  - "result.status == 'completed'"
  # Add specific assertions that validate correctness
  - "<assertion-expression>"
tags:
  - "golden"
  - "<relevant-tag>"
```

**For adversarial tests** — create `agents/<agent-id>/tests/adversarial/<test-id>.yaml`:

```yaml
id: "<test-id>"
agent_id: "<agent-id>"
description: "<Describe the attack vector or edge case>"
input:
  # Populate with adversarial/malicious/edge-case values
  <field>: <malicious-value>
expected_behavior: "reject"  # or "degrade-gracefully"
expected_error: "<ExpectedExceptionType>"
assertions:
  - "error.type == '<ExpectedExceptionType>'"
  - "<additional-assertion>"
tags:
  - "adversarial"
  - "<attack-category>"  # e.g., "injection", "overflow", "pii", "auth-bypass"
```

### Step 4: Update Test Runner

Check if `agents/<agent-id>/tests/test_<agent_id_underscored>.py` has a test method
that loads and runs fixtures from the `<test-type>/` directory. If not, add one:

```python
@pytest.mark.parametrize(
    "fixture_path",
    sorted(Path(f"agents/<agent-id>/tests/<test-type>/").glob("*.yaml")),
    ids=lambda p: p.stem,
)
async def test_<test-type>_fixtures(
    self, agent_context: AgentContext, fixture_path: Path
) -> None:
    """Run <test-type> test fixtures."""
    fixture = yaml.safe_load(fixture_path.read_text())
    agent_context.inputs = fixture["input"]
    agent = <AgentClassName>()
    result = await agent.run(agent_context)
    for assertion in fixture["assertions"]:
        assert eval(assertion, {"result": result, "input": fixture["input"]})
```

### Step 5: Validate

1. Verify the YAML is valid: `python -c "import yaml; yaml.safe_load(open('<path>'))"`.
2. Report success and show the created file path.
```

---

### 5.3 `.claude/skills/new-migration.md`

**File: `.claude/skills/new-migration.md`**

```markdown
---
skill: new-migration
usage: "/new-migration <NNN> <description>"
description: "Create a SQL migration file following the project conventions"
---

# Skill: /new-migration

## Usage

```
/new-migration <NNN> <description>
```

**Parameters:**
- `<NNN>` — 3-digit zero-padded sequence number (e.g., `001`, `042`)
- `<description>` — Lowercase underscore-separated description (e.g., `create_agents_table`)

**Example:**
```
/new-migration 015 add_cost_tracking_columns
```

## Procedure

### Step 1: Validate Arguments

1. Verify `<NNN>` is a 3-digit zero-padded number (000-999).
2. Verify `<description>` is lowercase with underscores only (pattern: `^[a-z][a-z0-9_]+$`).
3. Verify `migrations/<NNN>_<description>.sql` does NOT already exist.
4. List existing migrations and verify `<NNN>` is the next sequence number (no gaps, no duplicates).
5. If any check fails, report the error and STOP.

### Step 2: Determine Migration Type

Ask the user or infer from the description:
- `create_*` — New table creation
- `add_*` — Add columns or constraints
- `drop_*` — Remove columns or constraints (dangerous — confirm)
- `alter_*` — Modify existing structures
- `create_*_index` — Index creation
- `seed_*` — Data seeding

### Step 3: Create Migration File

Create `migrations/<NNN>_<description>.sql`:

```sql
-- Migration: <NNN>_<description>
-- Created: <current-date>
-- Author: claude-agent
-- Description: <Human-readable description of what this migration does>

BEGIN;

-- === UP Migration ===

-- <For CREATE TABLE migrations>
CREATE TABLE IF NOT EXISTS <table_name> (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- TODO(migration-<NNN>): Add domain-specific columns
    CONSTRAINT <table_name>_tenant_fk FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_<table_name>_tenant_id ON <table_name>(tenant_id);

-- Row-Level Security
ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;

CREATE POLICY <table_name>_tenant_isolation ON <table_name>
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Updated-at trigger
CREATE OR REPLACE FUNCTION update_<table_name>_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_<table_name>_updated_at
    BEFORE UPDATE ON <table_name>
    FOR EACH ROW
    EXECUTE FUNCTION update_<table_name>_updated_at();

COMMIT;
```

### Step 4: Create Corresponding Test

Create or update `tests/test_migration_<NNN>.py`:

```python
"""Tests for migration <NNN>_<description>."""

from __future__ import annotations

import pytest
from testcontainers.postgres import PostgresContainer


class TestMigration<NNN>:
    """Verify migration <NNN> applies and rolls back cleanly."""

    async def test_migration_applies(self, postgres_container: PostgresContainer) -> None:
        """Test that the migration applies without errors."""
        # Run migration against test DB
        ...

    async def test_rls_policy_exists(self, postgres_container: PostgresContainer) -> None:
        """Test that RLS is enabled on new tables."""
        ...

    async def test_tenant_isolation(self, postgres_container: PostgresContainer) -> None:
        """Test that tenant A cannot see tenant B data."""
        ...
```

### Step 5: Validate

1. Check SQL syntax (if `sqlfluff` is available, run it).
2. Verify the file follows the naming convention.
3. Report success and show the created file path.
```

---

### 5.4 `.claude/skills/validate-agent.md`

**File: `.claude/skills/validate-agent.md`**

```markdown
---
skill: validate-agent
usage: "/validate-agent <agent-id>"
description: "Run the complete validation checklist against an agent"
---

# Skill: /validate-agent

## Usage

```
/validate-agent <agent-id>
```

**Parameters:**
- `<agent-id>` — Full agent ID (e.g., `G1-cost-tracker`)

**Example:**
```
/validate-agent G1-cost-tracker
```

## Procedure

Run every check below. Track results as PASS/FAIL/WARN. Report a summary at the end.

### Check 1: Directory Structure

Verify ALL of the following files exist in `agents/<agent-id>/`:

| # | File | Required |
|---|------|----------|
| 1 | `manifest.yaml` | YES |
| 2 | `prompt.md` | YES |
| 3 | `agent.py` | YES |
| 4 | `hooks.py` | YES |
| 5 | `tools.py` | YES |
| 6 | `rubric.yaml` | YES |
| 7 | `tests/test_<agent_id>.py` | YES |
| 8 | `tests/conftest.py` | YES |
| 9 | `tests/golden/` (3+ files) | YES |
| 10 | `tests/adversarial/` (1+ files) | YES |

- FAIL if any required file is missing.
- WARN if `tests/__init__.py` is missing.

### Check 2: Manifest Validation

1. Load `agents/<agent-id>/manifest.yaml`.
2. Validate against `schema/agent-manifest.schema.json`.
3. Verify exactly 9 subsystems are present: `identity`, `triggers`, `inputs`, `outputs`, `dependencies`, `resources`, `security`, `observability`, `lifecycle`.
4. Verify `identity.id` matches the folder name `<agent-id>`.
5. Verify `identity.version` follows semver.

- FAIL if schema validation fails.
- FAIL if subsystem count is not exactly 9.
- FAIL if identity.id does not match folder name.

### Check 3: Rubric Validation

1. Load `agents/<agent-id>/rubric.yaml`.
2. Verify exactly 4 dimensions exist.
3. Verify all weights sum to exactly 1.0 (with float tolerance of 0.001).
4. Verify each dimension has: `name`, `weight`, `description`, `scoring`.
5. Verify scoring has keys 1 through 5.

- FAIL if dimension count is not 4.
- FAIL if weights do not sum to 1.0.
- FAIL if any dimension is missing required fields.

### Check 4: Python Linting

Run and report results for:

```bash
python -m ruff check agents/<agent-id>/ --config pyproject.toml
python -m ruff format --check agents/<agent-id>/ --config pyproject.toml
```

- FAIL if any Ruff error.
- Report the specific violations.

### Check 5: Type Checking

Run and report results for:

```bash
python -m mypy --strict agents/<agent-id>/ --config-file pyproject.toml
```

- FAIL if any mypy error.
- Report the specific violations.

### Check 6: Agent Class Validation

Read `agents/<agent-id>/agent.py` and verify:

1. Contains `from claude_agent_sdk import query, ClaudeAgentOptions`.
2. Agent class extends `BaseAgent`.
3. Has `async def run(self, context: AgentContext) -> AgentResult:`.
4. Has `async def validate_inputs(...)`.
5. Has `async def validate_outputs(...)`.
6. Uses `structlog` for logging (no `print()`).
7. No bare `except:`.
8. No `time.sleep`.
9. Has `from __future__ import annotations`.

- FAIL for each missing requirement.

### Check 7: Hooks Validation

Read `agents/<agent-id>/hooks.py` and verify:

1. Has `async def pre_run(context: AgentContext) -> AgentContext:`.
2. Has `async def post_run(context: AgentContext, result: AgentResult) -> AgentResult:`.
3. Has `async def on_error(context: AgentContext, error: Exception) -> ErrorAction:`.
4. Uses `structlog` for logging.

- FAIL for each missing hook function.

### Check 8: Forbidden Patterns

Scan ALL files in `agents/<agent-id>/` for forbidden patterns:

| Pattern | Scope | Severity |
|---------|-------|----------|
| `print(` | `*.py` | FAIL |
| `import *` | `*.py` | FAIL |
| `except:` (bare) | `*.py` | FAIL |
| `time.sleep` | `*.py` | FAIL |
| `# type: ignore` (no comment) | `*.py` | FAIL |
| `sk-ant-` | `*` | FAIL |
| `postgresql://` | `*` | FAIL |
| `sqlite` | `tests/*` | FAIL |
| `mock.patch("...database` | `tests/*` | FAIL |
| `TODO` (no parenthetical) | `*` | WARN |

### Check 9: Test Coverage

1. Count golden test files in `tests/golden/`. FAIL if fewer than 3.
2. Count adversarial test files in `tests/adversarial/`. FAIL if fewer than 1.
3. If possible, run: `python -m pytest agents/<agent-id>/tests/ --asyncio-mode=auto -q`.
4. Report pass/fail count.

### Check 10: Prompt Validation

Read `agents/<agent-id>/prompt.md` and verify:

1. Contains a "Role" section.
2. Contains an "Input Contract" or "Inputs" section.
3. Contains an "Output Contract" or "Outputs" section.
4. Contains a "Constraints" section.
5. Contains at least one example.
6. Does NOT contain hardcoded API keys or URLs with credentials.

- WARN for each missing section.
- FAIL if secrets are found in the prompt.

### Summary Report

Print a formatted summary:

```
=== Agent Validation Report: <agent-id> ===

Check 1: Directory Structure  .... PASS
Check 2: Manifest Validation  .... PASS
Check 3: Rubric Validation    .... PASS
Check 4: Python Linting       .... FAIL (3 violations)
Check 5: Type Checking        .... PASS
Check 6: Agent Class          .... PASS
Check 7: Hooks                .... PASS
Check 8: Forbidden Patterns   .... WARN (1 TODO without reason)
Check 9: Test Coverage        .... PASS (3 golden, 1 adversarial)
Check 10: Prompt              .... PASS

Result: 8 PASS | 1 FAIL | 1 WARN
Status: NOT READY (fix FAIL items before merge)
```

If all checks PASS (WARNs are acceptable):
```
Status: READY FOR MERGE
```
```

---

## 6. Enforcement Summary Matrix

This matrix shows which enforcement mechanism catches which rule category:

| Rule Category | Rule File | Hook (pre-commit) | Hook (pre-push) | Skill |
|--------------|-----------|-------------------|-----------------|-------|
| Type hints | `python.md` | `mypy-strict` | -- | `/validate-agent` |
| Ruff linting | `python.md` | `ruff-check` | -- | `/validate-agent` |
| Ruff formatting | `python.md` | `ruff-format-check` | -- | -- |
| Import ordering | `python.md` | `ruff-check` (I001/I002) | -- | -- |
| No print() | `python.md`, `tests.md` | `forbidden-pattern-scan` | -- | `/validate-agent` |
| No bare except | `python.md` | `forbidden-pattern-scan` | -- | `/validate-agent` |
| No time.sleep | `python.md` | `forbidden-pattern-scan` | -- | `/validate-agent` |
| Async discipline | `python.md`, `sdk.md` | `mypy-strict` | -- | `/validate-agent` |
| Secret scanning | `python.md` | `secret-scan` | -- | `/validate-agent` |
| Manifest schema | `agents.md`, `schemas.md` | `manifest-validation` | -- | `/validate-agent` |
| 9 subsystems | `agents.md` | `manifest-validation` | -- | `/validate-agent`, `/new-agent` |
| Rubric weights | `agents.md` | -- | `rubric-integrity` | `/validate-agent` |
| BaseAgent extension | `agents.md`, `sdk.md` | `mypy-strict` | -- | `/validate-agent`, `/new-agent` |
| Agent directory structure | `agents.md` | -- | -- | `/new-agent`, `/validate-agent` |
| Golden tests (3+) | `tests.md` | -- | `pytest-full` | `/new-test`, `/validate-agent` |
| Adversarial tests (1+) | `tests.md` | -- | `pytest-full` | `/new-test`, `/validate-agent` |
| No SQLite in tests | `tests.md` | `forbidden-pattern-scan` | -- | `/validate-agent` |
| No DB mocking | `tests.md` | `forbidden-pattern-scan` | -- | `/validate-agent` |
| Coverage thresholds | `tests.md` | -- | `coverage-check` | -- |
| Migration naming | `migrations.md` | -- | -- | `/new-migration` |
| RLS on all tables | `migrations.md` | -- | -- | `/new-migration`, `/validate-agent` |
| SQL transactions | `migrations.md` | -- | -- | `/new-migration` |
| Schema immutability | `schemas.md` | -- | -- | -- |
| SDK interface stability | `sdk.md` | `mypy-strict` | `pytest-full` | -- |

### Coverage by Stage

| Stage | Mechanisms Active | What Gets Caught |
|-------|------------------|-----------------|
| **Authoring** | Rule files (passive) | Claude reads rules before writing code — prevents violations at generation time |
| **Pre-commit** | 6 hooks | Linting, type-checking, manifest validation, forbidden patterns, secret scanning |
| **Pre-push** | 3 hooks | Full test suite, coverage thresholds, rubric integrity |
| **On-demand** | 4 skills | Agent scaffolding, test creation, migration creation, full validation checklist |

---

*End of document. This specification defines the complete `.claude/` enforcement layer for the Agentic SDLC Platform.*
