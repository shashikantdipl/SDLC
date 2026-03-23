# MASTER BUILD SPECIFICATION
# Agentic SDLC Platform — Complete Context for Claude

**Version:** 3.0 — Consolidated from `agentic-sdlc` analysis + `12-NEXT-PHASE-SPEC.md`
**Date:** 2026-03-21
**Purpose:** Hand this single document to Claude at the start of any new session.
**Scope:** Full platform understanding + 12-document pipeline + all gaps to close.

---

## HOW TO USE THIS DOCUMENT

This document gives Claude complete context to:
1. Understand the full platform architecture and patterns
2. Build the 12-document generation pipeline end-to-end
3. Fix 10 architectural gaps in the existing codebase
4. Add 15 new capabilities
5. Complete all 48 agent implementations

**Read in order:** Section 1 (rules) → Section 2 (architecture) → Section 3 (12-doc pipeline) → Section 4 (agent patterns) → Section 5 (SDK) → Section 6 (gaps to fix) → Section 7 (priority order).

---

## SECTION 1 — MANDATORY RULES (read before writing a single line of code)

1. All agents use `from claude_agent_sdk import query, ClaudeAgentOptions`
2. All agents extend `sdk/base_agent.py::BaseAgent`
3. Every agent manifest has exactly 9 anatomy subsystems
4. Build spec-first: update `manifest.yaml` + `prompt.md` before writing `agent.py`
5. API key only needed to RUN agents, not to write code
6. No placeholder comments — every file is fully implemented or marked `# TODO: <reason>`
7. Update `state/MANIFEST.md` after every file created or modified
8. Commit every 3 files: `git add -p && git commit -m "feat: <what>"`
9. Follow `G1-cost-tracker` as the gold standard for every new agent
10. Every new agent must pass `python -m pytest tests/test_<agent_id>.py -v` before moving on
11. File naming: lowercase-hyphenated (e.g., `my-document.md`), no spaces
12. Agent folders: named by ID (e.g., `G1-cost-tracker`, `OV-D1-scope-boundary-auditor`)
13. Every agent manifest must validate against `schema/agent-manifest.schema.json`

---

## SECTION 2 — PLATFORM ARCHITECTURE

### 2.1 What This Is

The **Agentic SDLC Platform** is a production-grade AI agent control plane. It does not replace the Claude Agent SDK — it is a higher-order orchestration layer on top of it. 48 agents across 7 SDLC phases automate the full software delivery lifecycle.

**Repository:** `agentic-sdlc` (main branch, ~800 files, v0.1.0)

**Three Pillars:**
- **Anatomy** (Spec 1A) — Every agent is a declarative YAML manifest with 9 subsystems
- **Orchestration** (Spec 1B) — 5 levels: Agent Loop → Subagent → Pipeline → Team → Fleet
- **Communication** (Spec 1C) — 7 protocol patterns with typed message envelopes

### 2.2 The 7 SDLC Phases

| Phase | Folder | Purpose | Agent Count |
|-------|--------|---------|-------------|
| **GOVERN** | `agents/govern/` | Cost, audit, lifecycle, orchestration | 4 (target 5) |
| **DESIGN** | `agents/claude-cc/D*/` | Requirements through test strategy | 12 (target 13) |
| **BUILD** | `agents/claude-cc/B*/` | Code generation, review, security | 8 (target 9) |
| **TEST** | `agents/claude-cc/T*/` | Static analysis, test running, coverage | 4 (target 5) |
| **DEPLOY** | `agents/claude-cc/P*/` | Checklist, IaC, release, rollback | 3 (target 5) |
| **OPERATE** | `agents/claude-cc/O*/` | Incident triage, runbook, SLA, alerts | 4 (target 5) |
| **OVERSIGHT** | `agents/claude-cc/OV-*/` | Structural + design audits | 10 (target 10) |

### 2.3 The 9-Subsystem Agent Anatomy

Every `manifest.yaml` must declare all 9 subsystems:

```yaml
identity:
  id: <agent-id>
  name: <display-name>
  version: "1.0.0"
  description: <one sentence>
  owner: platform-team
  phase: <govern|design|build|test|deploy|operate|oversight>
  extends: <archetype-id>          # one of 7 archetypes
  mixins: []                       # optional capabilities
  tags: []

foundation_model:
  model: <claude-haiku-4-5-20251001|claude-sonnet-4-6|claude-opus-4-6>
  temperature: 0.2                 # 0.0 for governance/test/deploy; 0.2 for design/build
  max_tokens: 8192

perception:
  trigger: <cron|api|webhook|event>
  input_schema:
    type: object
    required: [...]
    properties: {...}

memory:
  working: session_context          # reads from SessionStore
  episodic: audit_events_table
  semantic: exception_catalog

planning:
  strategy: <sequential|parallel|cot>
  max_steps: 10
  dry_run_supported: true

tools:
  allowed: [Read, Edit, Bash, Glob, Grep]
  custom: []                        # from tools.py

output:
  schema_ref: schema/contracts/<contract-v1>.json
  channels: [stdout]
  writes_to: <session key name>     # what key it writes to SessionStore

safety:
  autonomy_tier: <T0|T1|T2|T3>     # T0=full-auto, T3=every-action-approved
  max_budget_usd: 0.50
  audit_logging: true
  pii_scanning: true
  hitl:
    enabled: true
    trigger: confidence < 0.7

observability:
  metrics_enabled: true
  log_level: INFO
  alert_rules:
    - condition: cost_usd > 0.40
      action: slack_alert

maturity:
  current_level: apprentice
  max_maturity: expert
  promotion_criteria:
    override_rate_below: 0.05
    confidence_above: 0.85
    consecutive_days: 14

testing:
  golden_tests: tests/golden/
  adversarial_tests: tests/adversarial/
  min_coverage: 0.90

compliance:
  data_inventory:
    reads: [source_code, requirements]
    writes: [audit_trail, cost_records]
  regulations: []
```

### 2.4 The 7 Archetypes

Agents inherit from one archetype. Override only what differs.

| Archetype | Best For | Model | Temperature | Key Traits |
|-----------|----------|-------|-------------|------------|
| `ci-gate` | T3, T1, B8 | haiku | 0.0 | Fast, deterministic, binary pass/fail |
| `reviewer` | B1, B3, B4, OV-* | opus | 0.1 | Deep analysis, high confidence, multi-pass |
| `ops-agent` | O1, O2, O3 | opus | 0.0 | Incident response, sandbox-enabled |
| `discovery-agent` | DS1-DS4 | sonnet | 0.3 | Multi-turn, conversational, exploration |
| `co-pilot` | D1-D11, B2 | opus/sonnet | 0.2 | File-writing, session state, interactive |
| `orchestrator` | G4, OV-U1, team-spawner | sonnet | 0.1 | Spawns subagents, complex routing |
| `governance` | G1, G2, G3 | haiku | 0.0 | Monitoring, audit, cost control |

### 2.5 The 4-Layer Configuration Resolution

At runtime, `sdk/manifest_loader.py` resolves config in this order (later layers override earlier):

```
1. archetype YAML (e.g., archetypes/co-pilot.yaml)
        ↓ merge
2. mixins (e.g., d08-audit-logging, cost-tracking)
        ↓ merge
3. agent manifest.yaml (agent-specific overrides)
        ↓ merge
4. client profile YAML (knowledge/client/{client_id}/*.yaml)
        ↓
    Final resolved config → ClaudeAgentOptions
```

### 2.6 The 5 Orchestration Levels

```
L0 — Agent loop (Claude Agent SDK query() — internal)
L1 — Subagent spawn (nested SDK query() for delegation)
L2 — Pipeline (sequential agent chain, sdk/orchestration/pipeline_runner.py)
L3 — Team (complex workflow with parallel/conditional, sdk/orchestration/team_orchestrator.py)
L4 — Fleet (fleet-wide scaling + health, sdk/orchestration/fleet_controller.py)
L5 — Human (escalation, approval gates)
```

### 2.7 The Message Envelope

Every inter-agent message is wrapped in a standard envelope:

```python
{
    "envelope_id": "uuid",
    "correlation_id": "uuid",        # links all messages in one pipeline run
    "session_id": "uuid",
    "project_id": "proj-xxx",
    "from_agent": "D1-roadmap-generator",
    "to_agent": "D2-prd-generator",
    "timestamp": "2026-03-21T10:00:00Z",
    "trust_chain": ["external", "G4-team-orchestrator", "D1-roadmap-generator"],
    "payload": {
        "mode": "generate",
        "data": { ... }              # agent-specific input
    }
}
```

---

## SECTION 3 — THE 12-DOCUMENT PIPELINE

### 3.1 Overview

The `document-stack` team pipeline generates a complete engagement document set from a single brief. It is the highest-value workflow — one trigger produces 12 interconnected deliverables.

**Team YAML:** `teams/document-stack.yaml`
**Cost ceiling:** $25.00 per run
**Context strategy:** accumulate (each agent sees all prior outputs)
**Trigger:** manual

### 3.2 The 12 Documents — Sequence and Dependencies

```
INPUT: Client brief (project name, problem statement, tech stack, constraints)
         │
         ▼
DOC 01 — ROADMAP (D1-roadmap-generator)
         "What are we building and when?"
         Output key: requirements_doc (phases, milestones, timeline)
         │
         ▼
DOC 02 — CLAUDE.md (claude-md-generator)
         "What are the rules for this project?"
         Reads: requirements_doc
         Output: project-specific CLAUDE.md
         │
         ▼
DOC 03 — PRD (D2-prd-generator)
         "What does the product do and why?"
         Reads: requirements_doc
         Output key: prd_doc (vision, user stories, acceptance criteria)
         │
         ▼
DOC 04 — FEATURE CATALOG (D3-feature-extractor)
         "What are all the discrete features?"
         Reads: requirements_doc, prd_doc
         Output key: feature_catalog (features with MoSCoW priority)
         │
         ▼
DOC 05 — BACKLOG (D8-backlog-builder)
         "What are all the tasks in sprint order?"
         Reads: feature_catalog
         Output key: task_list (epics, stories, tickets with estimates)
         │
         ▼
DOC 06 — ARCHITECTURE (D5-architecture-drafter)
         "How is the system structured?"
         Reads: requirements_doc, prd_doc, feature_catalog
         Output key: architecture_doc (components, patterns, decisions)
         │
         ▼
DOC 07 — DATA MODEL (D6-data-model-designer)    ←─┐ parallel
         "What are the database schemas?"           │
         Reads: architecture_doc                    │
         Output key: db_schema                      │
                                                    │
DOC 08 — API CONTRACTS (D7-api-contract-generator) │ parallel
         "What are the REST/GraphQL interfaces?"    │
         Reads: architecture_doc                    │
         Output key: api_contracts                  │
         (D6 and D7 run in parallel)        ────────┘
         │
         ▼
DOC 09 — ENFORCEMENT SCAFFOLD (D4-enforcement-scaffolder)
         "What are the coding rules and linting config?"
         Reads: architecture_doc, feature_catalog
         Output key: enforcement_scaffold
         │
         ▼
DOC 10 — QUALITY SPEC (D10-quality-spec-generator)  ←─┐ parallel
         "What are the quality requirements?"           │
         Reads: requirements_doc, feature_catalog       │
         Output key: quality_spec                       │
                                                        │
DOC 11 — TEST STRATEGY (D11-test-strategy-generator)   │ parallel
         "How will we test everything?"                 │
         Reads: architecture_doc, quality_spec          │
         Output key: test_strategy                      │
         (D10 and D11 run in parallel)         ─────────┘
         │
         ▼
DOC 12 — DESIGN SPEC (D9-design-spec-writer)
         "What is the complete technical specification?"
         Reads: ALL prior outputs
         Output: comprehensive design spec document
         │
         ▼
OUTPUT: 12 deliverable files written to reports/{project_id}/
```

### 3.3 Session Context Keys (Shared State)

All agents in the pipeline read/write via `SessionStore`. Use **exactly** these key names:

| Key | Written By | Read By | Content |
|-----|-----------|---------|---------|
| `requirements_doc` | D1 | D2, D3, D4, D5, D6, D7, D8, D9, D10 | Roadmap phases, milestones, timeline |
| `prd_doc` | D2 | D3, D5, D6, D9, B1 | Product vision, user stories, acceptance criteria |
| `feature_catalog` | D3 | D4, D8, B1, B7 | Feature list with priority and description |
| `task_list` | D8 | B1, T2 | Epics, stories, tickets with estimates |
| `architecture_doc` | D5 | D3, D6, D7, D9, B1 | Component diagram, patterns, tech decisions |
| `db_schema` | D6 | B1, B2 | Entity-relationship model, table definitions |
| `api_contracts` | D7 | B1, B2, T4 | OpenAPI/GraphQL contracts |
| `enforcement_scaffold` | D4 | B1 | Linting rules, coding standards config |
| `quality_spec` | D10 | T2, T3, T4, T5 | Coverage targets, quality gates |
| `test_strategy` | D11 | T2, T3, T4, T5 | Test levels, tools, environments |

### 3.4 Pipeline Execution Rules

1. **Gate logic:** Each step has `gate: pass` — only runs if the previous step succeeded
2. **Context accumulation:** Each agent receives all prior session context keys automatically
3. **Parallel steps:** D6+D7 and D10+D11 run with `asyncio.gather()`, results merged via `union` strategy
4. **Minimum confidence:** If any agent returns `confidence < 0.5`, the pipeline halts and requests human review
5. **Cost tracking:** G1-cost-tracker monitors total spend against the $25.00 ceiling in real-time
6. **Output destination:** All documents written to `reports/{project_id}/`

---

## SECTION 4 — AGENT PATTERNS (How Every Agent Works)

### 4.1 The Gold Standard Agent: G1-cost-tracker

Study this agent before building any other. It demonstrates every correct pattern.

**File structure:**
```
agents/govern/G1-cost-tracker/
├── manifest.yaml          # 9 subsystems, all fields populated
├── prompt.md              # role, input, output, reasoning, examples
├── agent.py               # extends BaseAgent, implements all modes
├── hooks.py               # extends BaseHooks, pre+post hooks
├── tools.py               # TOOL_SCHEMAS + handlers + dispatch_tool()
├── rubric.yaml            # quality scoring on 4 dimensions
├── __init__.py            # empty
├── requirements.txt       # agent-specific deps
└── tests/
    ├── golden/
    │   ├── TC-001.yaml    # normal path: standard daily cost report
    │   ├── TC-002.yaml    # edge case: multiple projects, partial data
    │   └── TC-003.yaml    # minimal input: only today's data, no history
    └── adversarial/
        ├── ADV-001.yaml   # malformed input: missing required fields
        └── ADV-002.yaml   # attack: inject cost figures to exceed budget
```

### 4.2 agent.py Pattern

```python
from sdk.base_agent import BaseAgent
from sdk.communication.envelope import create_envelope

class CostTrackerAgent(BaseAgent):
    """G1 — monitors daily spend across all agents."""

    AGENT_ID = "G1-cost-tracker"
    MANIFEST_PATH = "agents/govern/G1-cost-tracker/manifest.yaml"

    async def run(self, envelope: dict, **kwargs) -> dict:
        """Main entry point. Always receives a message envelope."""
        # 1. Validate input (base class handles schema validation)
        mode = envelope["payload"]["mode"]

        # 2. Dispatch to mode handler
        if mode == "daily_report":
            return await self._daily_report(envelope)
        elif mode == "alert_check":
            return await self._alert_check(envelope)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    async def _daily_report(self, envelope: dict) -> dict:
        # 3. Read from session context if needed
        project_id = envelope["project_id"]

        # 4. Call Claude via base class (handles rate limiting, audit, cost tracking)
        result = await self.query(
            system_prompt=self._load_prompt(),    # loads prompt.md
            user_message=self._format_input(envelope),
            tools=self._get_tool_schemas()        # from tools.py
        )

        # 5. Write output to session store
        await self.session_store.write(
            session_id=envelope["session_id"],
            key="cost_report",
            value=result,
            agent_id=self.AGENT_ID
        )

        # 6. Return wrapped in output envelope
        return create_envelope(
            from_agent=self.AGENT_ID,
            to_agent=envelope["from_agent"],
            data=result,
            correlation_id=envelope["correlation_id"]
        )
```

### 4.3 hooks.py Pattern

```python
from sdk.base_hooks import BaseHooks

class CostTrackerHooks(BaseHooks):
    """Pre and post hooks for G1-cost-tracker."""

    def pre_tool_use(self, tool_name: str, tool_input: dict) -> dict:
        """Runs before every tool call. Can modify or block."""
        # Always call super() first — handles audit trail + PII scan
        tool_input = super().pre_tool_use(tool_name, tool_input)

        # Agent-specific: block Bash tool for governance agents
        if tool_name == "Bash" and self.manifest.get("safety", {}).get("autonomy_tier") == "T0":
            raise PermissionError("Bash tool not allowed for T0 agents")

        return tool_input

    def post_tool_use(self, tool_name: str, tool_input: dict, tool_output: dict) -> dict:
        """Runs after every tool call. Can modify output."""
        # Always call super() first — records cost, updates audit trail
        tool_output = super().post_tool_use(tool_name, tool_input, tool_output)

        # Agent-specific: log cost tool calls
        if tool_name == "get_cost_metrics":
            self._log_metric("cost_query", {"tool": tool_name})

        return tool_output
```

### 4.4 tools.py Pattern

```python
from typing import Any

# Schema defines the tool for Claude to call
TOOL_SCHEMAS = [
    {
        "name": "get_cost_metrics",
        "description": "Retrieve cost metrics for a project or agent from the cost store.",
        "input_schema": {
            "type": "object",
            "required": ["scope", "period_days"],
            "properties": {
                "scope": {
                    "type": "string",
                    "enum": ["fleet", "project", "agent"],
                    "description": "Scope of cost query"
                },
                "period_days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 90,
                    "description": "Number of days to look back"
                },
                "agent_id": {
                    "type": "string",
                    "description": "Required when scope=agent"
                }
            }
        }
    }
]

def handle_get_cost_metrics(tool_input: dict) -> dict:
    """Handler for get_cost_metrics tool."""
    scope = tool_input["scope"]
    period_days = tool_input["period_days"]
    # Real implementation queries PostgresCostStore
    return {
        "scope": scope,
        "period_days": period_days,
        "total_usd": 0.00,
        "breakdown": []
    }

def dispatch_tool(tool_name: str, tool_input: dict) -> Any:
    """Routes tool calls to their handlers. Called by BaseAgent."""
    if tool_name == "get_cost_metrics":
        return handle_get_cost_metrics(tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")
```

### 4.5 prompt.md Pattern (Mandatory Structure)

Every `prompt.md` must follow this structure exactly:

```markdown
# [Agent Name] — System Prompt

## Role
You are [agent name], a specialist agent in the [phase] phase of the SDLC platform.
Your single responsibility is: [one sentence — no more].

## What You Receive
You receive a JSON envelope with:
- `mode`: one of [list all modes this agent handles]
- `[field_name]`: [description of each input field]

## What You Must Produce
You must always return a JSON envelope containing:
- `[output_field]`: [description, format, constraints]
- `confidence`: float 0.0-1.0 reflecting how complete and correct your output is

## Step-by-Step Reasoning Process
1. [first thing to do — concrete, not vague]
2. [second thing to do]
3. [...]
(minimum 5 steps, maximum 10)

## Quality Standards
- [concrete measurable standard — e.g., "Every feature in feature_catalog must have a MoSCoW priority"]
- [concrete measurable standard — e.g., "Confidence >= 0.85 only if all required fields are populated"]

## Examples

### Good Output
[concrete example of correct output as JSON]

### Bad Output (do not produce this)
[concrete example of what to avoid, with explanation of why it's wrong]

## Exception Rules
[injected automatically by exception_loader — do not write manually here]
```

### 4.6 rubric.yaml Pattern (Required for Every Agent)

```yaml
rubric_id: <agent-id>-quality
dimensions:
  completeness:
    weight: 0.30
    criteria: "[specific: what fields/sections must be present]"
  accuracy:
    weight: 0.40
    criteria: "[specific: what makes content correct for this agent]"
  format_compliance:
    weight: 0.15
    criteria: "[specific: naming, structure, schema conformance]"
  exception_compliance:
    weight: 0.15
    criteria: "[specific: which exception rules must be followed]"
```

### 4.7 Test Case Patterns

**Golden test (tests/golden/TC-001.yaml):**
```yaml
test_id: TC-G1-001
description: "Standard daily cost report — 3 agents, normal spend"
priority: P0
input:
  envelope:
    session_id: "test-session-001"
    project_id: "proj-test"
    payload:
      mode: daily_report
      data:
        date: "2026-03-21"
expected_output:
  status: success
  confidence_min: 0.85
  fields_present: [total_usd, breakdown, alerts]
  no_fields: [error]
```

**Adversarial test (tests/adversarial/ADV-001.yaml):**
```yaml
test_id: ADV-G1-001
description: "Malformed input — missing required date field"
attack_type: missing_required_field
input:
  envelope:
    session_id: "test-session-adv"
    project_id: "proj-test"
    payload:
      mode: daily_report
      data: {}                        # missing date
expected_behavior:
  must_not_crash: true
  must_return_error: true
  error_message_contains: "date"
  must_not_expose: [api_key, database_url, internal_paths]
```

---

## SECTION 5 — SDK ARCHITECTURE

### 5.1 What Exists and Is Complete

| Module | Path | Status | Purpose |
|--------|------|--------|---------|
| `BaseAgent` | `sdk/base_agent.py` | COMPLETE | Stateless invocation, manifest loading, hook wiring, retry |
| `BaseStatefulAgent` | `sdk/base_agent.py` | COMPLETE | Multi-turn sessions via ClaudeSDKClient |
| `BaseHooks` | `sdk/base_hooks.py` | COMPLETE | D08 audit (13-field JSONL), cost tracking, PII detection, budget enforcement |
| `ManifestLoader` | `sdk/manifest_loader.py` | COMPLETE | 4-layer resolution, archetype→mixins→manifest→client |
| `SchemaValidator` | `sdk/schema_validator.py` | COMPLETE | JSON Schema 2020-12 validation for manifests + contracts |
| `ClientProfileLoader` | `sdk/client_profile_loader.py` | STUB | Loads per-client YAML rules (structure exists, zero profiles) |

### 5.2 What Needs to Be Built (Priority Order)

| Module | Path | Priority | Depends On |
|--------|------|----------|-----------|
| `SessionStore` | `sdk/context/session_store.py` | P1 — BLOCKING | PostgreSQL migration 006 |
| `PostgresCostStore` | `sdk/stores/postgres_cost_store.py` | P1 — BLOCKING | PostgreSQL cost_metrics table |
| `ApprovalStore` | `sdk/orchestration/approval_store.py` | P2 | PostgreSQL migration 007 |
| `PipelineCheckpoint` | `sdk/orchestration/checkpoint.py` | P2 | PostgreSQL migration 008 |
| `TokenBucketRateLimiter` | `sdk/enforcement/rate_limiter.py` | P2 | None |
| `PipelineRunner` | `sdk/orchestration/pipeline_runner.py` | P3 | SessionStore, ApprovalStore, Checkpoint |
| `TeamOrchestrator` | `sdk/orchestration/team_orchestrator.py` | P3 | PipelineRunner |
| `WebhookNotifier` | `sdk/communication/webhook.py` | P4 | None |
| `QualityScorer` | `sdk/evaluation/quality_scorer.py` | P4 | rubric.yaml per agent |
| `ExceptionPromotionEngine` | `sdk/knowledge/promotion_engine.py` | P4 | knowledge_exceptions table |
| `SelfHealPolicy` | `sdk/orchestration/self_heal.py` | P4 | PipelineRunner |
| `HealthServer` | `sdk/server/health.py` | P4 | aiohttp |
| `OtelInstrumentation` | `sdk/observability/otel.py` | P5 | opentelemetry-sdk |

### 5.3 Database Schema (PostgreSQL)

The platform uses PostgreSQL as its operational store. Five migrations exist or are needed:

**Migration 001–004 (existing):**
- `001_create_agents.sql` — `agent_registry` table
- `002_create_cost_metrics.sql` — `cost_metrics` table
- `003_create_audit_events.sql` — `audit_events` table (immutable, triggers on UPDATE/DELETE)
- `004_create_pipelines.sql` — `pipeline_runs` + `pipeline_steps` tables

**Migration 005 (ADD-11 — must build):**
```sql
CREATE TABLE knowledge_exceptions (
    exception_id    VARCHAR(64) PRIMARY KEY,
    title           VARCHAR(256) NOT NULL,
    rule            TEXT NOT NULL,
    severity        VARCHAR(16) NOT NULL CHECK (severity IN ('BLOCKER','WARNING','INFO')),
    tier            VARCHAR(16) NOT NULL CHECK (tier IN ('universal','stack','client')),
    stack_name      VARCHAR(128),
    client_id       VARCHAR(128),
    active          BOOLEAN DEFAULT FALSE,
    applies_to_phases TEXT[],
    applies_to_agents TEXT[],
    fire_count      INTEGER DEFAULT 0,
    last_fired_at   TIMESTAMPTZ,
    promoted_by     VARCHAR(128),
    promoted_at     TIMESTAMPTZ,
    created_by      VARCHAR(128) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**Migration 006 (FIX-01 — BLOCKING for 12-doc pipeline):**
```sql
CREATE TABLE session_context (
    id          BIGSERIAL PRIMARY KEY,
    session_id  UUID NOT NULL,
    key         VARCHAR(128) NOT NULL,
    value       JSONB NOT NULL,
    written_by  VARCHAR(64) NOT NULL,
    written_at  TIMESTAMPTZ DEFAULT NOW(),
    ttl_seconds INTEGER DEFAULT 86400,
    UNIQUE (session_id, key)
);
CREATE INDEX idx_session_context_session_id ON session_context(session_id);
CREATE INDEX idx_session_context_key ON session_context(session_id, key);
```

**Migration 007 (FIX-02 — for human approval gates):**
```sql
CREATE TABLE approval_requests (
    approval_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL,
    pipeline_name   VARCHAR(128) NOT NULL,
    step_id         VARCHAR(64) NOT NULL,
    summary         TEXT NOT NULL,
    status          VARCHAR(16) DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING','APPROVED','REJECTED','TIMEOUT')),
    approver_channel VARCHAR(256),
    decision_by     VARCHAR(128),
    decision_comment TEXT,
    requested_at    TIMESTAMPTZ DEFAULT NOW(),
    decided_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ NOT NULL
);
```

**Migration 008 (FIX-03 — for pipeline checkpoint/resume):**
```sql
CREATE TABLE pipeline_checkpoints (
    id              BIGSERIAL PRIMARY KEY,
    session_id      UUID NOT NULL,
    pipeline_name   VARCHAR(128) NOT NULL,
    last_step_id    VARCHAR(64) NOT NULL,
    step_results    JSONB NOT NULL,
    status          VARCHAR(32) DEFAULT 'in_progress',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_checkpoints_session ON pipeline_checkpoints(session_id);
```

### 5.4 Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@host:5432/sdlc_engine

# Optional (have defaults)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
REPORTS_DIR=reports/
ENVIRONMENT=dev|staging|prod
DRY_RUN=false
LOG_LEVEL=INFO

# Budget (defaults in budget.py)
FLEET_DAILY_BUDGET_USD=50.00
PROJECT_DAILY_BUDGET_USD=20.00
AGENT_DAILY_BUDGET_USD=5.00
INVOCATION_BUDGET_USD=0.50

# Rate limits
ANTHROPIC_REQUESTS_PER_MINUTE=50
ANTHROPIC_TOKENS_PER_MINUTE=100000

# Multi-project
DEFAULT_PROJECT_ID=proj-default
DEFAULT_CLIENT_ID=client-default
DEFAULT_STACK=python-fastapi
```

---

## SECTION 6 — COMPLETE GAP LIST

### 6.1 FIX-01: Session Store (BLOCKING — 12-doc pipeline cannot run without this)

**Problem:** Agents start from zero on every invocation. D2-prd-generator cannot read D1's roadmap output.

**Build:** `sdk/context/session_store.py`

```python
class SessionStore:
    async def write(self, session_id: str, key: str, value: Any, agent_id: str) -> None: ...
    async def read(self, session_id: str, key: str) -> Optional[Any]: ...
    async def read_all(self, session_id: str) -> dict[str, Any]: ...
    async def list_keys(self, session_id: str) -> list[str]: ...
    async def delete(self, session_id: str, key: str) -> None: ...
```

**Wire into BaseAgent:** Every agent gets `self.session_store` injected automatically by `BaseAgent.__init__()`.

---

### 6.2 FIX-02: Human-in-the-Loop Approval Gates

**Problem:** Pipelines run fully automated with no way to pause for human review.

**Build:** Add `human_approval` gate type to `sdk/orchestration/pipeline.py` + `sdk/orchestration/approval_store.py`

**Gate types (update enum):**
```python
GATE_ALWAYS = "always"
GATE_PASS = "pass"
GATE_NO_BLOCKERS = "no_blockers"
GATE_HUMAN = "human_approval"    # NEW
```

**Pipeline behavior for `gate: human_approval`:**
1. Post summary to Slack with Approve/Reject buttons
2. Poll `approval_store.check_approval()` every 30s
3. APPROVED → continue; REJECTED → halt with reason; TIMEOUT → escalate

**Usage in team YAML:**
```yaml
steps:
  - id: step-02-architecture
    agent: D5-architecture-drafter
    gate: human_approval
    approval:
      channel: "#engineering-leads"
      timeout_seconds: 7200
      message: "Architecture designed. Review before proceeding to data model."
```

---

### 6.3 FIX-03: Pipeline Checkpoint + Resume

**Problem:** If step 7 fails in an 11-step pipeline, all prior work is lost — must restart from step 1.

**Build:** `sdk/orchestration/checkpoint.py`

```python
class PipelineCheckpoint:
    async def save(self, session_id: str, step_id: str, result: dict) -> None: ...
    async def load(self, session_id: str) -> Optional[dict]: ...
    async def clear(self, session_id: str) -> None: ...
```

**Pipeline change:** After each step succeeds, call `checkpoint.save()`. On `execute()`, check for checkpoint and skip completed steps.

**Step-level retry in team YAML:**
```yaml
steps:
  - id: step-05-test-runner
    agent: T2-test-runner
    gate: pass
    retry:
      max_attempts: 3
      delay_seconds: 30
      resume_on_failure: true
```

---

### 6.4 FIX-04: Real Cost Store (Fail-Safe)

**Problem:** `BudgetCascade` uses stub data. If DB is down, agents run unchecked (fail-open = dangerous).

**Build:** `sdk/stores/postgres_cost_store.py`

```python
class PostgresCostStore:
    def __init__(self, dsn: str, fail_safe: bool = True):
        # fail_safe=True: if DB unreachable, return float("inf") → agent blocked
        # fail_safe=False: if DB unreachable, return 0.0 → agent allowed (UNSAFE)
        ...

    async def get_fleet_daily_spend(self) -> float: ...
    async def get_project_daily_spend(self, project_id: str) -> float: ...
    async def get_agent_daily_spend(self, agent_id: str) -> float: ...
    async def record_spend(self, session_id: str, agent_id: str, cost_usd: float, tokens: dict) -> None: ...
```

**Default:** `fail_safe=True` — always block on DB error. Never fail-open in production.

---

### 6.5 FIX-05: Agent Versioning and Safe Rollout

**Problem:** Deploying a new agent version immediately affects all pipelines with no rollback.

**Build:** Version slots in `agent_registry` + G3 controls active slot.

**DB change:**
```sql
ALTER TABLE agent_registry ADD COLUMN active_version VARCHAR(32) DEFAULT '1.0.0';
ALTER TABLE agent_registry ADD COLUMN canary_version VARCHAR(32);
ALTER TABLE agent_registry ADD COLUMN canary_traffic_pct SMALLINT DEFAULT 0;
ALTER TABLE agent_registry ADD COLUMN previous_version VARCHAR(32);
```

**G3 commands:**
```python
await g3.promote_canary(agent_id="B1-code-generator")
await g3.rollback(agent_id="B1-code-generator")
await g3.set_canary(agent_id="B1-code-generator", version="2.0.0", traffic_pct=10)
```

---

### 6.6 FIX-06: Parallel Pipeline DAG

**Problem:** D5/D6/D7/D8/D9 run sequentially even though D6, D7, D8, D9 only depend on D5, not each other. Runtime could be cut from ~24 min to ~8 min.

**Build:** Dependency graph in team YAML + DAG executor using `asyncio.gather()`.

**Team YAML change:**
```yaml
steps:
  - id: step-01-requirements
    agent: D1-roadmap-generator
    depends_on: []

  - id: step-02-architecture
    agent: D5-architecture-drafter
    depends_on: [step-01-requirements]

  # These all depend on architecture but NOT on each other → parallel
  - id: step-03-data-model
    agent: D6-data-model-designer
    depends_on: [step-02-architecture]

  - id: step-04-api
    agent: D7-api-contract-generator
    depends_on: [step-02-architecture]
```

---

### 6.7 FIX-07: Observability Dashboard

**Problem:** Cost data and audit events exist in DB but are invisible without writing SQL.

**Build:** `dashboard/app.py` using Streamlit.

**Pages:**
1. `01_fleet_health.py` — agent status grid, circuit breaker states
2. `02_cost_monitor.py` — daily/weekly/monthly spend by agent/project/model
3. `03_pipeline_runs.py` — recent runs, step-by-step status, duration
4. `04_audit_log.py` — filterable audit events (severity/agent/project)
5. `05_approval_queue.py` — pending approvals with Approve/Reject buttons

---

### 6.8 FIX-08: Input/Output Validation

**Problem:** `BaseAgent._validate_input()` and `_validate_output()` are stubs. Agents silently accept malformed envelopes.

**Build:** Wire JSON Schema validation in `sdk/base_agent.py`:

```python
def _validate_input(self, envelope: dict) -> None:
    input_schema = self._manifest.get("perception", {}).get("input_schema")
    if input_schema:
        jsonschema.validate(envelope["payload"]["data"], input_schema)

def _validate_output(self, result: dict) -> None:
    schema_ref = self._manifest.get("output", {}).get("schema_ref")
    if schema_ref:
        schema = self._load_schema(schema_ref)
        jsonschema.validate(result, schema)
```

**Every agent manifest must define `input_schema` in the `perception` section.**

---

### 6.9 FIX-09: API Rate Limiter

**Problem:** Parallel agents call Claude API simultaneously. Hitting rate limits fails all concurrent agents at once.

**Build:** `sdk/enforcement/rate_limiter.py`

```python
class TokenBucketRateLimiter:
    def __init__(self, requests_per_minute: int = 50, tokens_per_minute: int = 100_000): ...
    async def acquire(self, estimated_tokens: int = 1000) -> None: ...
    async def release(self, actual_tokens_used: int) -> None: ...
```

**Wire into `BaseAgent._query()`:** Every Claude API call goes through `rate_limiter.acquire()` first.

---

### 6.10 FIX-10: Complete All 48 Prompt Files

**Problem:** Many `prompt.md` files are stubs. The system prompt is the single most important factor in output quality.

**Action:** Every `prompt.md` must follow the mandatory structure in Section 4.5. Zero stubs allowed.

---

### 6.11 ADD-10: 5 Missing Team Pipelines

Create these team YAML files following the same structure as `feature-development.yaml`:

| File | Steps | Purpose |
|------|-------|---------|
| `teams/bug-fix.yaml` | B1 → B3 → T2 → T3 → P2 → P3 | Fix a reported bug end-to-end |
| `teams/hotfix.yaml` | B1 → B3 → T2 → P2 → P3 | Emergency fix, minimal gates |
| `teams/security-patch.yaml` | B3 → B4 → T4 → P1 → P2 → P3 | CVE remediation |
| `teams/compliance-review.yaml` | OV-C1 → OV-S1 → G2 → D8 | Compliance audit |
| `teams/performance-optimization.yaml` | T5 → B5 → T5 → O4 | Profile → refactor → verify |

---

### 6.12 ADD-12: 9 Missing Agents (to reach 48)

| Agent ID | Phase | Archetype | Purpose |
|----------|-------|-----------|---------|
| `G5-audit-reporter` | govern | governance | Weekly/monthly compliance audit reports |
| `T1-static-analyser` | test | ci-gate | Run mypy, bandit, semgrep before test runner |
| `P4-rollback-manager` | deploy | ops-agent | Execute deployment rollback on smoke test failure |
| `P5-feature-flag-manager` | deploy | ops-agent | Manage feature flag toggles (LaunchDarkly) |
| `O5-alert-manager` | operate | ops-agent | Manage PagerDuty/OpsGenie alert routing |
| `B9-migration-writer` | build | co-pilot | Generate DB migration files from D6 schema changes |
| `D12-localisation-planner` | design | co-pilot | Plan i18n/l10n requirements, locale files |
| `OV-P1-performance-auditor` | oversight | reviewer | Audit historical performance test results |
| `OV-D1-dependency-auditor` | oversight | reviewer | Dependency health, license compliance, CVE |

Each must have the full standard file set (see Section 4.1) + at least 3 golden test cases.

---

### 6.13 ADD-01: Webhook Callback System

**Build:** `sdk/communication/webhook.py`

```python
class WebhookNotifier:
    async def notify(self, callback_url: str, session_id: str,
                     pipeline_result: PipelineResult, secret: Optional[str] = None) -> bool: ...
```

---

### 6.14 ADD-06: Self-Healing Pipeline

**Build:** `sdk/orchestration/self_heal.py`

Policies:
- `test_failure` → T2 fails → invoke B7-test-writer → retry T2 (max 2 attempts)
- `lint_failure` → B8 fails → invoke B5-refactor-assistant → retry B8 (max 1 attempt)

---

### 6.15 ADD-08: Quality Scoring

**Build:** `sdk/evaluation/quality_scorer.py`

```python
@dataclass
class QualityScore:
    completeness: float     # 0.0-1.0
    accuracy: float         # 0.0-1.0
    format_compliance: float
    exception_compliance: float
    overall: float          # weighted average from rubric.yaml
```

---

## SECTION 7 — BUILD PRIORITY ORDER

Work in this exact order. Do not start the next item until the current one passes all tests.

### Priority 1 — Foundation (blocks everything)
1. `sdk/context/session_store.py` + migration 006 (FIX-01)
2. `sdk/stores/postgres_cost_store.py` (FIX-04)
3. Input/output validation in `BaseAgent` (FIX-08)
4. Migration 005 `knowledge_exceptions` table (ADD-11)

### Priority 2 — Safety and Control
5. Human approval gates + `ApprovalStore` + migration 007 (FIX-02)
6. Pipeline checkpoint + resume + migration 008 (FIX-03)
7. Rate limiter `TokenBucketRateLimiter` (FIX-09)
8. CI/CD deploy workflow `.github/workflows/deploy.yml` (ADD-13)

### Priority 3 — Agent Implementation (follow this order exactly)
9. G1-cost-tracker — complete agent.py + hooks.py (currently partial, use as gold standard)
10. G2-policy-enforcer (depends on audit_events)
11. G3-agent-lifecycle-manager (depends on agent_registry + versioning)
12. G4-team-orchestrator (depends on pipeline + router)
13. Design agents: D1 → D2 → D3 → D4 → D5 → D6 → D7 → D8 → D9 → D10 → D11 → claude-md-generator
14. Build agents: B1 → B2 → B3 → B4 → B5 → B6 → B7 → B8 → B9
15. Test agents: T1 → T2 → T3 → T4 → T5
16. Deploy agents: P1 → P2 → P3 → P4 → P5
17. Operate agents: O1 → O2 → O3 → O4 → O5
18. Oversight agents: OV-S1 → OV-C1 → OV-U1 → OV-Q1 → OV-P1 → OV-D1

### Priority 4 — Enhancements
19. Agent versioning (FIX-05)
20. Parallel pipeline DAG (FIX-06)
21. Streamlit dashboard (FIX-07)
22. Cost anomaly detection for G1 (ADD-09)
23. Multi-project namespace isolation (ADD-05)
24. Self-healing pipeline (ADD-06)
25. Quality scoring + rubric.yaml per agent (ADD-08)
26. 5 missing team pipelines (ADD-10)
27. 9 missing agents to reach 48 (ADD-12)
28. Streaming output (ADD-07)

### Priority 5 — Enterprise Grade
29. Response cache for reproducibility (3.2)
30. Security: mTLS + network policy + HMAC signing (3.5)
31. OpenTelemetry distributed tracing (3.6)
32. Graceful degradation + fallback agents (3.7)
33. Multi-environment config (dev/staging/prod) (3.8)
34. REST API + CLI + WebSocket (3.10)

---

## SECTION 8 — DEFINITION OF DONE

### An agent is NOT done until ALL of these pass:

```
[ ] manifest.yaml validates: python -m sdk.schema_validator agents/{phase}/{id}/manifest.yaml
[ ] prompt.md is complete — role, input, output, reasoning steps (≥5), examples — NO STUBS
[ ] agent.py implements ALL modes listed in manifest
[ ] hooks.py registers at least one pre_tool_use and one post_tool_use hook
[ ] tools.py has TOOL_SCHEMAS + handlers + dispatch_tool() for all listed tools
[ ] rubric.yaml exists with all 4 scoring dimensions and correct weights
[ ] At least 3 golden test cases in tests/golden/TC-XXX.yaml
[ ] At least 1 adversarial test case in tests/adversarial/ADV-XXX.yaml
[ ] pytest tests/test_{agent_id}.py passes with >= 90% coverage
[ ] MANIFEST.md updated with status: done
[ ] git commit created
```

### A pipeline is NOT done until:

```
[ ] All agents in the pipeline individually pass the agent checklist above
[ ] End-to-end pipeline test passes: pytest tests/test_pipeline_{name}.py
[ ] Pipeline completes in < 30 minutes (wall clock for 12-doc pipeline: < 60 min)
[ ] All human approval gates tested (both approve AND reject paths)
[ ] Checkpoint resume tested (kill at step 6, restart, verify steps 1-5 skipped)
[ ] Rollback tested (pipeline halted, all artifacts cleaned up)
[ ] Cost stays within ceiling ($25.00 for document-stack)
```

---

## SECTION 9 — COMPLETE AGENT INVENTORY (48 Agents)

### GOVERN Phase (4 current, target 5)

| ID | Name | Model | Archetype | Status | Key Output |
|----|------|-------|-----------|--------|-----------|
| G1-cost-tracker | Cost Tracker | haiku | governance | VERIFIED ($0.006) | Daily cost report, budget alerts |
| G2-audit-trail-validator | Audit Trail Validator | haiku | governance | VERIFIED (team) | Audit compliance report |
| G3-agent-lifecycle-manager | Agent Lifecycle Manager | haiku | governance | dry-run | Agent health, version management |
| G4-team-orchestrator | Team Orchestrator | sonnet | orchestrator | dry-run | Pipeline dispatch, team coordination |
| **G5-audit-reporter** | **Audit Reporter** | **haiku** | **governance** | **TO BUILD** | **Weekly compliance summary** |

### DESIGN Phase (12 current, target 13)

| ID | Name | Model | Session Key Written | Status |
|----|------|-------|---------------------|--------|
| D1-roadmap-generator | Roadmap Generator | opus | `requirements_doc` | dry-run |
| D2-prd-generator | PRD Generator | opus | `prd_doc` | dry-run |
| D3-feature-extractor | Feature Extractor | opus | `feature_catalog` | dry-run |
| D4-enforcement-scaffolder | Enforcement Scaffolder | sonnet | `enforcement_scaffold` | dry-run |
| D5-architecture-drafter | Architecture Drafter | opus | `architecture_doc` | dry-run |
| D6-data-model-designer | Data Model Designer | opus | `db_schema` | dry-run |
| D7-api-contract-generator | API Contract Generator | sonnet | `api_contracts` | dry-run |
| D8-backlog-builder | Backlog Builder | sonnet | `task_list` | dry-run |
| D9-design-spec-writer | Design Spec Writer | opus | `design_spec` | dry-run |
| D10-quality-spec-generator | Quality Spec Generator | sonnet | `quality_spec` | dry-run |
| D11-test-strategy-generator | Test Strategy Generator | sonnet | `test_strategy` | dry-run |
| claude-md-generator | CLAUDE.md Generator | sonnet | — | dry-run |
| **D12-localisation-planner** | **Localisation Planner** | **sonnet** | **`l10n_plan`** | **TO BUILD** |

### BUILD Phase (8 current, target 9)

| ID | Name | Model | Archetype | Status |
|----|------|-------|-----------|--------|
| B1-code-reviewer | Code Reviewer | opus | reviewer | VERIFIED ($0.134) |
| B2-test-writer | Test Writer | sonnet | co-pilot | dry-run |
| B3-security-auditor | Security Auditor | opus | reviewer | VERIFIED (team) |
| B4-performance-analyzer | Performance Analyzer | sonnet | reviewer | dry-run |
| B5-refactor-assistant | Refactor Assistant | sonnet | co-pilot | dry-run |
| B6-doc-generator | Doc Generator | sonnet | co-pilot | dry-run |
| B7-dependency-auditor | Dependency Auditor | haiku | reviewer | VERIFIED (team) |
| B8-build-validator | Build Validator | haiku | ci-gate | dry-run |
| **B9-migration-writer** | **Migration Writer** | **sonnet** | **co-pilot** | **TO BUILD** |

### TEST Phase (4 current, target 5)

| ID | Name | Model | Archetype | Status |
|----|------|-------|-----------|--------|
| T2-acceptance-validator | Acceptance Validator | sonnet | ci-gate | dry-run |
| T3-coverage-gate | Coverage Gate | haiku | ci-gate | VERIFIED ($0.005) |
| T4-integration-test-runner | Integration Test Runner | haiku | ci-gate | dry-run |
| T5-performance-test-runner | Performance Test Runner | sonnet | ci-gate | dry-run |
| **T1-static-analyser** | **Static Analyser** | **haiku** | **ci-gate** | **TO BUILD** |

### DEPLOY Phase (3 current, target 5)

| ID | Name | Model | Archetype | Status |
|----|------|-------|-----------|--------|
| P1-deploy-checklist | Deploy Checklist | haiku | ci-gate | dry-run |
| P2-cdk-iac-reviewer | CDK/IaC Reviewer | opus | reviewer | dry-run |
| P3-release-notes | Release Notes | sonnet | reviewer | dry-run |
| **P4-rollback-manager** | **Rollback Manager** | **sonnet** | **ops-agent** | **TO BUILD** |
| **P5-feature-flag-manager** | **Feature Flag Manager** | **sonnet** | **ops-agent** | **TO BUILD** |

### OPERATE Phase (4 current, target 5)

| ID | Name | Model | Archetype | Status |
|----|------|-------|-----------|--------|
| O1-incident-triage | Incident Triage | opus | ops-agent | dry-run |
| O2-runbook-executor | Runbook Executor | sonnet | ops-agent | dry-run |
| O3-oncall-summarizer | On-Call Summarizer | haiku | ops-agent | dry-run |
| O4-sla-monitor | SLA Monitor | haiku | ops-agent | dry-run |
| **O5-alert-manager** | **Alert Manager** | **haiku** | **ops-agent** | **TO BUILD** |

### OVERSIGHT Phase (10 current)

| ID | Name | Model | Archetype | Status |
|----|------|-------|-----------|--------|
| OV-S1-spec-structure-linter | Spec Structure Linter | haiku | reviewer | dry-run |
| OV-S2-catalog-alignment-checker | Catalog Alignment Checker | haiku | reviewer | dry-run |
| OV-S3-docs-cross-ref-auditor | Docs Cross-Ref Auditor | haiku | reviewer | dry-run |
| OV-S4-agent-code-reviewer | Agent Code Reviewer | opus | reviewer | dry-run |
| OV-D1-scope-boundary-auditor | Scope Boundary Auditor | opus | reviewer | dry-run |
| OV-D2-tier-model-challenger | Tier Model Challenger | opus | reviewer | dry-run |
| OV-D3-rules-enforceability | Rules Enforceability | sonnet | reviewer | dry-run |
| OV-D4-assumption-stress-tester | Assumption Stress Tester | opus | reviewer | dry-run |
| OV-D5-governance-gap-auditor | Governance Gap Auditor | opus | reviewer | VERIFIED ($0.832) |
| OV-U1-ui-review-panel | UI Review Panel | sonnet | orchestrator | dry-run |

---

## SECTION 10 — FOLDER STRUCTURE REFERENCE

```
agentic-sdlc/
├── state/                     # Session continuity
│   ├── MANIFEST.md            # Source of truth for all file status
│   ├── CONTEXT_DUMP.md        # Current session context
│   └── decisions.md           # Architecture decision log
│
├── agents/
│   ├── govern/                # G1-G5
│   └── claude-cc/             # All other phases (D*, B*, T*, P*, O*, OV-*)
│       └── {AGENT-ID}/
│           ├── manifest.yaml
│           ├── prompt.md
│           ├── agent.py
│           ├── hooks.py
│           ├── tools.py
│           ├── rubric.yaml     # REQUIRED — quality scoring
│           ├── __init__.py
│           ├── requirements.txt
│           └── tests/
│               ├── golden/     # TC-XXX.yaml (≥3 per agent)
│               └── adversarial/ # ADV-XXX.yaml (≥1 per agent)
│
├── sdk/
│   ├── base_agent.py          # COMPLETE
│   ├── base_hooks.py          # COMPLETE
│   ├── manifest_loader.py     # COMPLETE
│   ├── schema_validator.py    # COMPLETE
│   ├── context/
│   │   ├── session_store.py   # TO BUILD (FIX-01, BLOCKING)
│   │   └── code_snapshot.py   # TO BUILD (ADD-02)
│   ├── stores/
│   │   └── postgres_cost_store.py  # TO BUILD (FIX-04)
│   ├── orchestration/
│   │   ├── pipeline_runner.py      # STUB → wire (P3)
│   │   ├── team_orchestrator.py    # STUB → wire (P3)
│   │   ├── approval_store.py       # TO BUILD (FIX-02)
│   │   ├── checkpoint.py           # TO BUILD (FIX-03)
│   │   └── self_heal.py            # TO BUILD (ADD-06)
│   ├── communication/
│   │   ├── envelope.py        # STUB → wire
│   │   └── webhook.py         # TO BUILD (ADD-01)
│   ├── enforcement/
│   │   ├── rate_limiter.py    # TO BUILD (FIX-09)
│   │   ├── cost_controller.py # STUB → wire
│   │   └── circuit_breaker.py # STUB → wire
│   ├── evaluation/
│   │   └── quality_scorer.py  # TO BUILD (ADD-08)
│   ├── knowledge/
│   │   └── promotion_engine.py # TO BUILD (ADD-04)
│   └── server/
│       └── health.py          # TO BUILD (ADD-03)
│
├── schema/
│   ├── agent-manifest.schema.json  # COMPLETE (571 lines)
│   └── contracts/             # 20 output contract schemas (COMPLETE)
│
├── archetypes/                # 7 archetype YAMLs (COMPLETE)
├── teams/                     # 9 team workflow YAMLs (COMPLETE + 5 TO BUILD)
├── migrations/                # SQL migrations 001-008 (001-004 exist, 005-008 to build)
├── dashboard/                 # Streamlit app (TO BUILD)
├── knowledge/
│   ├── universal/             # Universal exception rules (EMPTY — to populate)
│   ├── stack/                 # Stack-specific rules (EMPTY)
│   └── client/                # Client-specific rules (EMPTY)
├── compliance/                # AI Act, SOC2, DPA (stubs)
├── docs/                      # Platform guides (stubs)
└── MASTER-BUILD-SPEC.md       # THIS FILE
```

---

## SECTION 11 — VERIFIED BASELINE

What has been proven to work with real API calls (as of 2026-03-21):

| What | Result | Cost | Notes |
|------|--------|------|-------|
| G1-cost-tracker | PASS | $0.006 | Daily cost report generated |
| B1-code-reviewer | PASS | $0.134 | Reviewed sdk/base_hooks.py, found real issues |
| T3-coverage-gate | PASS | ~$0.005 | CI gate pattern confirmed |
| OV-D5-governance-gap-auditor | PASS | $0.832 | Gap analysis on full repo |
| compliance-audit team (G1+G2+B7+OV-D5) | PASS | $0.92 | 4 agents, $3.00 ceiling respected |
| All 48 agents dry-run | PASS | ~$0 | Cost estimation mode |
| All 48 manifests schema validation | PASS | — | Against agent-manifest.schema.json |

**Total real API spend to date:** $1.30

---

## APPENDIX A — Standard File Template Checklist

When creating a new agent, verify each file:

```
agents/{phase}/{agent-id}/
├── manifest.yaml          ← 9 subsystems, all fields, validates against schema
├── prompt.md              ← role, input, output, 5+ reasoning steps, examples
├── agent.py               ← extends BaseAgent, implements ALL modes from manifest
├── hooks.py               ← extends BaseHooks, has pre_tool_use + post_tool_use
├── tools.py               ← TOOL_SCHEMAS list + handlers + dispatch_tool()
├── rubric.yaml            ← 4 dimensions, weights sum to 1.0
├── __init__.py            ← empty file
├── requirements.txt       ← agent-specific Python deps only
└── tests/
    ├── golden/
    │   ├── TC-001.yaml    ← normal/happy path
    │   ├── TC-002.yaml    ← edge case (empty input, max values, etc.)
    │   └── TC-003.yaml    ← minimal valid input
    └── adversarial/
        └── ADV-001.yaml   ← malformed input, must not crash or expose internals
```

---

## APPENDIX B — The Exception Flywheel

The platform improves itself through structured exception capture:

```
Agent produces unexpected output
          ↓
Human overrides / corrects
          ↓
Exception captured as YAML in knowledge/client/{client_id}/
          ↓
Exception fires 5+ times in 7 days
          ↓
ExceptionPromotionEngine proposes promotion
          ↓
Human approves → moves to knowledge/stack/{stack}/  (if stack-specific)
                        or knowledge/universal/       (if universal)
          ↓
Exception auto-injected into all agent prompts via exception_loader
          ↓
Override rate drops → agent matures from apprentice → professional → expert
```

**Exception YAML format:**
```yaml
exception_id: EX-U-001
title: "Never expose secrets in output"
rule: "Output must never contain API keys, passwords, tokens, or connection strings. Redact with [REDACTED]."
severity: BLOCKER
tier: universal
applies_to_phases: null   # all phases
applies_to_agents: null   # all agents
```

---

*End of Master Build Specification. Every item above has a clear owner, a specific file to create, and a specific priority. Build in the order defined in Section 7.*
