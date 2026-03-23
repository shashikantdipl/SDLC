# CLAUDE.md — Agentic SDLC Platform

> This file is the single source of truth for "how we build in this repo."
> Read by Claude Code and human developers before any code is written.

---

## 1. Project

| Field          | Value                                                                 |
| -------------- | --------------------------------------------------------------------- |
| Name           | Agentic SDLC Platform                                                 |
| Purpose        | Production-grade AI agent control plane for full software delivery lifecycle automation |
| Tagline        | 48 agents across 7 SDLC phases, orchestrated by spec-first manifests and governed by real-time cost controls. |
| Owner          | Platform Engineering                                                  |
| Version        | 0.1.0                                                                 |
| Repo           | `agentic-sdlc` (main branch, ~800 files)                             |
| Spec Source    | `Requirement/MASTER-BUILD-SPEC.md`                                    |
| Gold Standard  | `agents/govern/G1-cost-tracker/` — copy this structure for every new agent |
| State Tracker  | `state/MANIFEST.md` — updated after every file create/modify          |

---

## 2. Architecture

- **Language:** Python 3.12 with mandatory type hints on all function signatures. Linted by Ruff, type-checked by mypy (strict mode).
- **Agent SDK:** All 48 agents use the Claude Agent SDK (`from claude_agent_sdk import query, ClaudeAgentOptions`). Every agent extends `sdk/base_agent.py::BaseAgent`.
- **Database:** PostgreSQL 15+ as the single operational store (agent_registry, cost_metrics, audit_events, pipeline_runs, session_context, approval_requests, pipeline_checkpoints, knowledge_exceptions). No SQLite anywhere.
- **Runtime:** Fully async via `asyncio`. HTTP server via `aiohttp` on port 8080. Dashboard via Streamlit on port 8501.
- **Config Resolution:** 4-layer merge: archetype YAML -> mixins -> agent manifest.yaml -> client profile YAML. Resolved at runtime by `sdk/manifest_loader.py`.

---

## 3. Repo Structure

```
agentic-sdlc/
├── state/                          # Session continuity between Claude sessions
│   ├── MANIFEST.md                 # Source of truth for all file statuses
│   ├── CONTEXT_DUMP.md             # Current session context snapshot
│   └── decisions.md                # Architecture Decision Log (ADL)
│
├── agents/                         # All 48 agent implementations
│   ├── govern/                     # Governance agents (G1-G5)
│   │   └── G1-cost-tracker/        # GOLD STANDARD — copy this for every agent
│   │       ├── manifest.yaml       # 9 subsystems, validates against schema
│   │       ├── prompt.md           # Role, input, output, reasoning steps, examples
│   │       ├── agent.py            # Extends BaseAgent, implements all modes
│   │       ├── hooks.py            # Extends BaseHooks, pre+post hooks
│   │       ├── tools.py            # TOOL_SCHEMAS + handlers + dispatch_tool()
│   │       ├── rubric.yaml         # 4 quality dimensions, weights sum to 1.0
│   │       ├── __init__.py         # Empty
│   │       ├── requirements.txt    # Agent-specific dependencies
│   │       └── tests/
│   │           ├── golden/         # TC-001.yaml, TC-002.yaml, TC-003.yaml minimum
│   │           └── adversarial/    # ADV-001.yaml minimum
│   └── claude-cc/                  # All non-governance agents
│       ├── D*-*/                   # DESIGN phase (D1-D13, 12-13 agents)
│       ├── B*-*/                   # BUILD phase (B1-B9, 8-9 agents)
│       ├── T*-*/                   # TEST phase (T1-T5, 4-5 agents)
│       ├── P*-*/                   # DEPLOY phase (P1-P5, 3-5 agents)
│       ├── O*-*/                   # OPERATE phase (O1-O5, 4-5 agents)
│       └── OV-*-*/                 # OVERSIGHT phase (OV-D1 to OV-U1, 10 agents)
│
├── sdk/                            # Shared framework (imported by all agents)
│   ├── base_agent.py               # COMPLETE — BaseAgent + BaseStatefulAgent
│   ├── base_hooks.py               # COMPLETE — D08 audit, cost tracking, PII scanning
│   ├── manifest_loader.py          # COMPLETE — 4-layer config resolution
│   ├── schema_validator.py         # COMPLETE — JSON Schema 2020-12 validation
│   ├── client_profile_loader.py    # STUB
│   ├── context/
│   │   ├── session_store.py        # TO BUILD (P1 BLOCKING)
│   │   └── code_snapshot.py        # TO BUILD
│   ├── stores/
│   │   └── postgres_cost_store.py  # TO BUILD (P1)
│   ├── orchestration/
│   │   ├── pipeline_runner.py      # STUB — DAG execution engine
│   │   ├── team_orchestrator.py    # STUB — Complex workflow with parallel/conditional
│   │   ├── approval_store.py       # TO BUILD (P2)
│   │   ├── checkpoint.py           # TO BUILD (P2)
│   │   └── self_heal.py            # TO BUILD (P4)
│   ├── communication/
│   │   ├── envelope.py             # STUB — Typed message envelope
│   │   └── webhook.py              # TO BUILD (P4)
│   ├── enforcement/
│   │   ├── rate_limiter.py         # TO BUILD (P2)
│   │   ├── cost_controller.py      # STUB
│   │   └── circuit_breaker.py      # STUB
│   ├── evaluation/
│   │   └── quality_scorer.py       # TO BUILD (P4)
│   ├── knowledge/
│   │   └── promotion_engine.py     # TO BUILD (P4)
│   └── server/
│       └── health.py               # TO BUILD (P4)
│
├── schema/                         # Validation schemas
│   ├── agent-manifest.schema.json  # COMPLETE (571 lines, JSON Schema 2020-12)
│   └── contracts/                  # 20 output contract schemas (one per agent output type)
│
├── archetypes/                     # 7 archetype YAML definitions
│   ├── ci-gate.yaml
│   ├── reviewer.yaml
│   ├── ops-agent.yaml
│   ├── discovery-agent.yaml
│   ├── co-pilot.yaml
│   ├── orchestrator.yaml
│   └── governance.yaml
│
├── teams/                          # Team workflow definitions (9 exist, 5 to build)
│   └── document-stack.yaml         # 12-doc pipeline definition
│
├── migrations/                     # PostgreSQL DDL
│   ├── 001_agent_registry.sql
│   ├── 002_audit_events.sql
│   ├── 003_cost_metrics.sql
│   ├── 004_pipeline_runs.sql
│   └── 005-008 — TO BUILD          # session_context, approvals, checkpoints, knowledge
│
├── dashboard/                      # Streamlit web UI (TO BUILD)
│   └── app.py
│
├── knowledge/                      # Knowledge base (3-tier)
│   ├── universal/                  # Patterns valid for all projects
│   ├── stack/                      # Stack-specific (python-fastapi, etc.)
│   └── client/                     # Client-specific overrides
│
├── compliance/                     # Compliance templates and reports
├── docs/                           # Human-facing documentation
├── reports/                        # Generated output (reports/{project_id}/)
├── requirements.txt                # Top-level dependencies
└── pyproject.toml                  # Ruff + mypy configuration
```

---

## 4. Language Rules — Python 3.12

### Type Safety (enforced by mypy --strict)

- Add type hints to every function signature, including return types. No exceptions.
- Use `from __future__ import annotations` at the top of every module.
- Never use `# type: ignore` without a trailing explanation: `# type: ignore[arg-type] — third-party stub missing`.
- Use `TypedDict` for structured dictionaries, never bare `dict[str, Any]` for known shapes.

### Imports (enforced by Ruff I001, I002)

- Never use `import *`. Always import specific names.
- Sort imports: stdlib, third-party, local. Ruff auto-sorts on save.
- Use absolute imports for SDK modules: `from sdk.base_agent import BaseAgent`, not relative imports.

### Formatting (enforced by Ruff)

- Line length: 120 characters maximum.
- Indent: 4 spaces. No tabs.
- Trailing commas on multi-line collections and function signatures.
- Single quotes for strings. Double quotes only for docstrings.

### Error Handling

- Never use bare `except:`. Always catch specific exception types.
- Use `structlog` or `logging` for all log output. Never use `print()`.
- Raise domain-specific exceptions (e.g., `ManifestValidationError`, `BudgetExceededError`), not generic `Exception`.

### Async

- All agent execution is async. Use `async def` for agent methods.
- Never use `time.sleep()` in async code. Use `asyncio.sleep()`.
- Use `asyncio.gather()` for parallel execution (e.g., parallel pipeline steps).

### Testing (enforced by pytest + pytest-asyncio)

- Framework: `pytest` with `pytest-asyncio` for async tests.
- Every agent has a test file: `tests/test_<agent_id>.py`.
- Minimum 3 golden test cases (`tests/golden/TC-001.yaml` through `TC-003.yaml`).
- Minimum 1 adversarial test case (`tests/adversarial/ADV-001.yaml`).
- Minimum coverage target: 90% per agent module.
- Never mock the database engine. Use real PostgreSQL in tests (via test containers or dedicated test DB).
- Never substitute SQLite for PostgreSQL in tests.

### Logging

- Use `structlog` with structured key-value output.
- Every log entry must include: `agent_id`, `session_id`, `project_id`.
- Log levels: DEBUG for internal state, INFO for lifecycle events, WARNING for recoverable issues, ERROR for failures.

---

## 5. Implementation Patterns

### Pattern A: Agent Directory (every agent, no exceptions)

Every agent follows this exact file structure. Copy from `agents/govern/G1-cost-tracker/`.

```
agents/{phase}/{agent-id}/
├── manifest.yaml          # 9 subsystems — validates against schema/agent-manifest.schema.json
├── prompt.md              # Role + input + output + 5 reasoning steps + 2 examples
├── agent.py               # Extends BaseAgent, implements generate/review/fix/score modes
├── hooks.py               # Extends BaseHooks, pre_invoke + post_invoke hooks
├── tools.py               # TOOL_SCHEMAS list + handler functions + dispatch_tool()
├── rubric.yaml            # 4 quality dimensions, float weights summing to 1.0
├── __init__.py            # Empty file (makes directory a Python package)
├── requirements.txt       # Agent-specific pip dependencies (may be empty)
└── tests/
    ├── golden/            # TC-001.yaml, TC-002.yaml, TC-003.yaml (minimum 3)
    └── adversarial/       # ADV-001.yaml (minimum 1)
```

**Build order for a new agent (mandatory):**
1. Write `manifest.yaml` (all 9 subsystems)
2. Validate: `python -m sdk.schema_validator agents/{phase}/{id}/manifest.yaml`
3. Write `prompt.md`
4. Write `agent.py` (extends `BaseAgent`)
5. Write `hooks.py` (extends `BaseHooks`)
6. Write `tools.py` (TOOL_SCHEMAS + dispatch_tool)
7. Write `rubric.yaml`
8. Write test cases in `tests/golden/` and `tests/adversarial/`
9. Run: `python -m pytest tests/test_<agent_id>.py -v`
10. Update `state/MANIFEST.md`

### Pattern B: SDK Module

Every SDK module follows this structure:

```python
"""Module docstring — one sentence purpose."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ModuleConfig:
    """Configuration for this module, loaded from env or manifest."""
    setting_a: str = "default"
    setting_b: int = 100


class ModuleName:
    """Main class — single responsibility."""

    def __init__(self, config: ModuleConfig) -> None:
        self._config = config
        self._logger = logger.bind(module=self.__class__.__name__)

    async def primary_method(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Async method with type hints and structured logging."""
        self._logger.info("method_start", input_keys=list(input_data.keys()))
        # Implementation here — no stubs without # TODO: <reason>
        result: dict[str, Any] = {}
        self._logger.info("method_complete", result_keys=list(result.keys()))
        return result
```

### Pattern C: Agent agent.py Structure

```python
"""<Agent display name> — one sentence description."""

from __future__ import annotations

from claude_agent_sdk import query, ClaudeAgentOptions
from sdk.base_agent import BaseAgent


class <AgentClassName>(BaseAgent):
    """Implements <agent-id> across all execution modes."""

    async def generate(self, input_data: dict) -> dict:
        """Primary generation mode."""
        ...

    async def review(self, input_data: dict) -> dict:
        """Review mode — evaluates existing artifacts."""
        ...

    async def fix(self, input_data: dict) -> dict:
        """Fix mode — applies corrections to flagged issues."""
        ...

    async def score(self, input_data: dict) -> dict:
        """Score mode — returns rubric-based quality score."""
        ...
```

### Pattern D: Manifest 9-Subsystem Template

Every `manifest.yaml` must declare all 9 top-level subsystems. Missing any subsystem causes schema validation failure.

```
identity          — id, name, version, description, owner, phase, extends, mixins, tags
foundation_model  — model, temperature, max_tokens
perception        — trigger, input_schema
memory            — working, episodic, semantic
planning          — strategy, max_steps, dry_run_supported
tools             — allowed, custom
output            — schema_ref, channels, writes_to
safety            — autonomy_tier, max_budget_usd, audit_logging, pii_scanning, hitl
observability     — metrics_enabled, log_level, alert_rules
```

Plus the required `maturity`, `testing`, and `compliance` sections.

---

## 6. Key Reference Tables

### 6.1 Archetypes

| Archetype          | Best For                          | Model         | Temperature | Key Traits                              |
| ------------------ | --------------------------------- | ------------- | ----------- | --------------------------------------- |
| `ci-gate`          | T3, T1, B8                        | haiku         | 0.0         | Fast, deterministic, binary pass/fail   |
| `reviewer`         | B1, B3, B4, OV-*                  | opus          | 0.1         | Deep analysis, high confidence, multi-pass |
| `ops-agent`        | O1, O2, O3                        | opus          | 0.0         | Incident response, sandbox-enabled      |
| `discovery-agent`  | DS1-DS4                           | sonnet        | 0.3         | Multi-turn, conversational, exploration |
| `co-pilot`         | D1-D11, B2                        | opus/sonnet   | 0.2         | File-writing, session state, interactive |
| `orchestrator`     | G4, OV-U1, team-spawner           | sonnet        | 0.1         | Spawns subagents, complex routing       |
| `governance`       | G1, G2, G3                        | haiku         | 0.0         | Monitoring, audit, cost control         |

### 6.2 SDLC Phases

| Phase        | Folder                  | Agent Count (current/target) | Agent ID Prefix |
| ------------ | ----------------------- | ---------------------------- | --------------- |
| GOVERN       | `agents/govern/`        | 4 / 5                        | G1-G5           |
| DESIGN       | `agents/claude-cc/D*/`  | 12 / 13                      | D1-D13          |
| BUILD        | `agents/claude-cc/B*/`  | 8 / 9                        | B1-B9           |
| TEST         | `agents/claude-cc/T*/`  | 4 / 5                        | T1-T5           |
| DEPLOY       | `agents/claude-cc/P*/`  | 3 / 5                        | P1-P5           |
| OPERATE      | `agents/claude-cc/O*/`  | 4 / 5                        | O1-O5           |
| OVERSIGHT    | `agents/claude-cc/OV-*/`| 10 / 10                       | OV-D1 to OV-U1 |

### 6.3 Autonomy Tiers

| Tier | Name              | Approval Required       | Use Case                          |
| ---- | ----------------- | ----------------------- | --------------------------------- |
| T0   | Full Auto         | None                    | Cost tracking, linting, metrics   |
| T1   | Notify            | None, but notifies      | Code generation, doc generation   |
| T2   | Approve on Risk   | If confidence < 0.7     | Architecture decisions, reviews   |
| T3   | Always Approve    | Every action             | Production deploys, rollbacks     |

### 6.4 Environment Variables

| Variable                         | Required | Default            | Purpose                               |
| -------------------------------- | -------- | ------------------ | ------------------------------------- |
| `ANTHROPIC_API_KEY`              | Yes      | —                  | Claude API authentication             |
| `DATABASE_URL`                   | Yes      | —                  | PostgreSQL connection string           |
| `SLACK_WEBHOOK_URL`              | No       | —                  | Slack notification endpoint            |
| `REPORTS_DIR`                    | No       | `reports/`         | Output directory for generated docs    |
| `ENVIRONMENT`                    | No       | `dev`              | Runtime environment (dev/staging/prod) |
| `DRY_RUN`                        | No       | `false`            | Simulate without API calls             |
| `LOG_LEVEL`                      | No       | `INFO`             | structlog level                        |
| `FLEET_DAILY_BUDGET_USD`         | No       | `50`               | Fleet-wide daily spend ceiling         |
| `PROJECT_DAILY_BUDGET_USD`       | No       | `20`               | Per-project daily spend ceiling        |
| `AGENT_DAILY_BUDGET_USD`         | No       | `5`                | Per-agent daily spend ceiling           |
| `INVOCATION_BUDGET_USD`          | No       | `0.50`             | Per-invocation spend ceiling           |
| `ANTHROPIC_REQUESTS_PER_MINUTE`  | No       | `50`               | API rate limit (requests)              |
| `ANTHROPIC_TOKENS_PER_MINUTE`    | No       | `100000`           | API rate limit (tokens)                |
| `DEFAULT_PROJECT_ID`             | No       | `proj-default`     | Default project for multi-project mode |
| `DEFAULT_CLIENT_ID`              | No       | `client-default`   | Default client for profile resolution  |
| `DEFAULT_STACK`                  | No       | `python-fastapi`   | Default tech stack for knowledge base  |

### 6.5 Model Pricing (Claude API)

| Model                          | Input (per 1M tokens) | Output (per 1M tokens) |
| ------------------------------ | --------------------- | ---------------------- |
| claude-haiku-4-5-20251001      | $0.80                 | $4.00                  |
| claude-sonnet-4-6              | $3.00                 | $15.00                 |
| claude-opus-4-6                | $15.00                | $75.00                 |

### 6.6 PostgreSQL Tables

| Table                   | Migration | Purpose                                     |
| ----------------------- | --------- | ------------------------------------------- |
| `agent_registry`        | 001       | Agent metadata, versions, status             |
| `audit_events`          | 002       | Immutable audit trail (append-only)          |
| `cost_metrics`          | 003       | Token usage, USD spend per invocation        |
| `pipeline_runs`         | 004       | Pipeline execution state and history         |
| `session_context`       | 005       | TO BUILD — shared agent session state        |
| `approval_requests`     | 006       | TO BUILD — HITL approval gate records        |
| `pipeline_checkpoints`  | 007       | TO BUILD — checkpoint/resume state           |
| `knowledge_exceptions`  | 008       | TO BUILD — knowledge promotion exceptions    |

---

## 7. Key Commands

### Setup

```bash
# Install all dependencies
pip install -r requirements.txt

# Run database migrations (in order)
psql $DATABASE_URL -f migrations/001_agent_registry.sql
psql $DATABASE_URL -f migrations/002_audit_events.sql
psql $DATABASE_URL -f migrations/003_cost_metrics.sql
psql $DATABASE_URL -f migrations/004_pipeline_runs.sql
```

### Validation

```bash
# Validate a single agent manifest against JSON Schema
python -m sdk.schema_validator agents/{phase}/{agent-id}/manifest.yaml

# Type-check the entire codebase
mypy sdk/ agents/ --strict

# Lint and auto-fix
ruff check sdk/ agents/ --fix
ruff format sdk/ agents/
```

### Testing

```bash
# Test a single agent
python -m pytest tests/test_<agent_id>.py -v

# Test all agents with coverage
python -m pytest tests/ -v --cov=sdk --cov-report=term-missing

# Test with coverage threshold (90% minimum)
python -m pytest tests/ -v --cov=sdk --cov-fail-under=90
```

### Running Agents

```bash
# Dry run (no API key needed, no Claude calls)
python -m agents.{phase}.{agent-id}.agent --dry-run

# Live run (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-... python -m agents.govern.G1-cost-tracker.agent
```

### Dashboard

```bash
# Start the Streamlit dashboard (port 8501)
streamlit run dashboard/app.py
```

### Git Workflow

```bash
# Commit every 3 files (mandatory cadence)
git add -p && git commit -m "feat: <what was added>"

# After every file create/modify, update state
# Edit state/MANIFEST.md to reflect new file status
```

---

## 8. Pipelines / Workflows

### 8.1 The 12-Document Pipeline

The highest-value workflow. One client brief produces 12 interconnected deliverables.

```
Client Brief
  |
  v
D1-roadmap-generator --------> requirements_doc
  |
  v
claude-md-generator ----------> project CLAUDE.md
  |
  v
D2-prd-generator -------------> prd_doc
  |
  v
D3-feature-extractor ---------> feature_catalog
  |
  v
D8-backlog-builder -----------> task_list
  |
  v
D5-architecture-drafter ------> architecture_doc
  |
  +--[ parallel ]---+
  |                  |
  v                  v
D6-data-model       D7-api-contract
  |                  |
  v                  v
db_schema           api_contracts
  |                  |
  +--------+---------+
           |
           v
D4-enforcement-scaffolder ----> enforcement_scaffold
  |
  +--[ parallel ]---+
  |                  |
  v                  v
D10-quality-spec    D11-test-strategy
  |                  |
  v                  v
quality_spec        test_strategy
  |                  |
  +--------+---------+
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
- Parallel execution: D6+D7 and D10+D11 run via `asyncio.gather()`, results merged by `union` strategy

### 8.2 Agent Execution Lifecycle

```
Trigger (cron | api | webhook | event)
  |
  v
manifest_loader.py: resolve config (archetype -> mixins -> manifest -> client profile)
  |
  v
BaseHooks.pre_invoke(): cost check, PII scan, audit log start
  |
  v
BaseAgent.run(): load prompt.md -> build ClaudeAgentOptions -> query()
  |
  v
[Claude Agent SDK loop: reasoning + tool use]
  |
  v
BaseHooks.post_invoke(): cost record, audit log close, quality score
  |
  v
Output -> SessionStore (writes_to key) + stdout/webhook/channel
```

### 8.3 Orchestration Levels

```
L0 — Agent Loop        Claude Agent SDK query() — internal reasoning + tool use
L1 — Subagent Spawn    Nested query() calls for delegation
L2 — Pipeline          Sequential agent chain (pipeline_runner.py)
L3 — Team              Parallel/conditional workflow (team_orchestrator.py)
L4 — Fleet             Fleet-wide scaling and health (fleet_controller.py)
L5 — Human             Escalation and approval gates (approval_store.py)
```

### 8.4 CI/CD (Target)

```
git push -> GitHub Actions
  |
  +--> ruff check + ruff format --check
  +--> mypy --strict
  +--> pytest tests/ -v --cov-fail-under=90
  +--> python -m sdk.schema_validator agents/**/manifest.yaml
  |
  v
All pass -> merge allowed
```

---

## 9. Cost / Budget

### 9.1 Budget Tiers (4-Level Hierarchy)

| Level        | Variable                    | Default  | Scope                        |
| ------------ | --------------------------- | -------- | ---------------------------- |
| Fleet        | `FLEET_DAILY_BUDGET_USD`    | $50.00   | All agents, all projects     |
| Project      | `PROJECT_DAILY_BUDGET_USD`  | $20.00   | Single project, all agents   |
| Agent        | `AGENT_DAILY_BUDGET_USD`    | $5.00    | Single agent, all invocations |
| Invocation   | `INVOCATION_BUDGET_USD`     | $0.50    | Single agent run              |

### 9.2 Cost Calculation Formula

```
invocation_cost_usd = (input_tokens / 1_000_000 * model_input_price)
                    + (output_tokens / 1_000_000 * model_output_price)
```

### 9.3 Cost Tracking Flow

```
Every agent invocation:
  1. BaseHooks.pre_invoke() checks: remaining budget >= estimated cost
  2. If budget exceeded -> reject invocation, log to audit_events, alert via Slack
  3. Claude Agent SDK query() executes
  4. BaseHooks.post_invoke() records actual cost to cost_metrics table
  5. G1-cost-tracker aggregates daily/weekly/monthly reports
```

### 9.4 Budget Alert Rules

| Condition                              | Action                              |
| -------------------------------------- | ----------------------------------- |
| Invocation cost > 80% of budget        | `slack_alert` warning               |
| Invocation cost > budget               | Reject invocation                   |
| Agent daily spend > 80% of daily cap   | `slack_alert` warning               |
| Agent daily spend > daily cap          | Halt agent for remainder of day     |
| Fleet daily spend > 80% of fleet cap   | `slack_alert` + page on-call        |
| Fleet daily spend > fleet cap          | Halt all non-critical agents        |

### 9.5 12-Document Pipeline Cost Estimate

| Agent                      | Model   | Est. Tokens (in+out) | Est. Cost |
| -------------------------- | ------- | --------------------- | --------- |
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
| **Total**                  |         |                       | **~$7.55** |

Pipeline ceiling: $25.00 (provides 3x headroom for retries and re-runs).

---

## 10. Forbidden Patterns

These patterns are never acceptable in this codebase. Every item is specific and greppable.

### Code Quality

| Forbidden                                          | Use Instead                                          |
| -------------------------------------------------- | ---------------------------------------------------- |
| `print(`                                           | `structlog.get_logger()` or `logging.getLogger()`    |
| `import *`                                         | Explicit named imports                                |
| `except:`  (bare)                                  | `except SpecificException:`                          |
| `# type: ignore` without explanation               | `# type: ignore[code] -- reason`                     |
| `time.sleep(` in async code                        | `await asyncio.sleep(`                               |
| Mutable default arguments (`def f(x=[])`)          | `def f(x: list | None = None):`                      |
| `# TODO` without reason                            | `# TODO: <specific reason and ticket/priority>`      |
| Placeholder/stub code without `# TODO: <reason>`   | Fully implement or mark with explicit TODO            |

### Security

| Forbidden                                          | Use Instead                                          |
| -------------------------------------------------- | ---------------------------------------------------- |
| Hardcoded API keys, passwords, connection strings  | Environment variables via `os.environ`                |
| Credentials in source code or committed files      | `.env` file (gitignored) or secrets manager           |
| `eval(` or `exec(` with untrusted input            | Structured parsing (JSON, YAML loaders)              |

### Database

| Forbidden                                          | Use Instead                                          |
| -------------------------------------------------- | ---------------------------------------------------- |
| SQLite as PostgreSQL substitute (including tests)  | Real PostgreSQL instance (test containers or test DB) |
| Mocking the database engine in tests               | Integration tests against real PostgreSQL             |
| Raw SQL string concatenation                       | Parameterized queries                                |

### Architecture

| Forbidden                                          | Use Instead                                          |
| -------------------------------------------------- | ---------------------------------------------------- |
| Agent that does not extend `BaseAgent`             | `from sdk.base_agent import BaseAgent`               |
| Agent without all 9 manifest subsystems            | Full manifest per `schema/agent-manifest.schema.json` |
| Skipping manifest validation before writing code   | `python -m sdk.schema_validator` first               |
| Agent without minimum 3 golden + 1 adversarial test| Write tests before marking agent complete            |
| Direct `query()` call without going through BaseAgent | All SDK calls route through BaseAgent.run()        |
| File names with spaces or camelCase                | `lowercase-hyphenated.ext`                           |
| Agent folder names not matching agent ID           | Folder name === `identity.id` from manifest          |

### Process

| Forbidden                                          | Use Instead                                          |
| -------------------------------------------------- | ---------------------------------------------------- |
| Writing `agent.py` before `manifest.yaml`          | Spec-first: manifest -> prompt -> agent              |
| Committing without updating `state/MANIFEST.md`    | Update MANIFEST.md after every file change            |
| Committing more than 3 files without a commit      | `git add -p && git commit` every 3 files             |
| Skipping tests before declaring agent complete     | `python -m pytest tests/test_<agent_id>.py -v`       |

---

## Appendix: Session Context Keys (12-Doc Pipeline)

These are the exact key names used in `SessionStore`. Use them verbatim.

| Key                      | Written By | Read By                                  |
| ------------------------ | ---------- | ---------------------------------------- |
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
