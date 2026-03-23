# ROADMAP.md — Agentic SDLC Platform

> **v1.0 | Full-Stack-First | 2026-03-24**
>
> **Approach:** Full-Stack-First (14+2 documents). AI interfaces (MCP tools) and human interfaces (dashboard screens) designed in parallel from a shared INTERACTION-MAP, backed by a unified backend.
>
> **Repository:** `agentic-sdlc` (main branch, ~800 files, v0.1.0)
>
> **Team:** Platform team (2-3 developers)

---

## Table of Contents

1. [Current State](#1-current-state)
2. [Document Build Sequence](#2-document-build-sequence)
3. [Delivery Phases](#3-delivery-phases)
4. [Milestones](#4-milestones)
5. [Open Decisions](#5-open-decisions)
6. [Risk Register](#6-risk-register)
7. [Timeline Visualization](#7-timeline-visualization)
8. [Document Versioning & Regeneration Policy](#8-document-versioning--regeneration-policy)

---

## 1. Current State

**Assessment date:** 2026-03-21 (verified real API calls)

### 1.1 What Exists and Works

| Component | Status | File Path / Evidence |
|-----------|--------|----------------------|
| BaseAgent / BaseStatefulAgent | DONE | `sdk/base_agent.py` |
| BaseHooks (D08 audit, cost tracking, PII detection) | DONE | `sdk/base_hooks.py` |
| ManifestLoader (4-layer resolution) | DONE | `sdk/manifest_loader.py` |
| SchemaValidator (JSON Schema 2020-12) | DONE | `sdk/schema_validator.py` |
| Agent manifest schema (571 lines) | DONE | `schema/agent-manifest.schema.json` |
| Output contract schemas | DONE | `schema/output-contracts/` (20 schemas) |
| Archetype YAMLs | DONE | 7 archetypes (one per SDLC phase) |
| Team workflow YAMLs | DONE | 9 workflows defined |
| SQL migrations 001-004 | DONE | `migrations/001-004` |
| 48 agent manifests | DONE | All pass schema validation |
| 48 agent dry-runs | DONE | All pass with stub data |

### 1.2 Verified API Call Results

| Test | Result | Cost |
|------|--------|------|
| G1-cost-tracker | PASS | $0.006 |
| B1-code-reviewer | PASS | $0.134 |
| T3-coverage-gate | PASS | $0.005 |
| OV-D5-governance-gap-auditor | PASS | $0.832 |
| compliance-audit team (G1+G2+B7+OV-D5) | PASS | $0.920 ($3.00 ceiling) |
| **Total real API spend** | **PASS** | **$1.30** |

### 1.3 What Does Not Exist

| Gap ID | Component | Severity | Blocker? |
|--------|-----------|----------|----------|
| FIX-01 | SessionStore | CRITICAL | YES — blocks the entire pipeline |
| FIX-02 | ApprovalStore / approval gates | HIGH | No |
| FIX-03 | PipelineCheckpoint | HIGH | No |
| FIX-04 | PostgresCostStore (real, not stub) | HIGH | No |
| FIX-05 | Agent versioning | MEDIUM | No |
| FIX-06 | Parallel DAG execution | MEDIUM | No |
| FIX-07 | Dashboard (Streamlit) | MEDIUM | No |
| FIX-08 | Input/Output validation | HIGH | No |
| FIX-09 | TokenBucketRateLimiter | HIGH | No |
| FIX-10 | Complete all prompt.md files | HIGH | No |

### 1.4 Numeric Summary

| Metric | Value |
|--------|-------|
| Agents defined (manifests) | 48 |
| Agents with real implementations | 0 (all dry-run stubs) |
| Agents missing entirely | 9 |
| Team pipelines defined | 9 |
| Team pipelines missing | 5 |
| SQL migrations landed | 4 |
| SQL migrations needed | 4 more (005-008) |
| SDLC phases covered | 7 of 7 |
| Prompt files that are stubs | ~40 (estimated) |
| SDK modules complete | 6 of 19 |
| SDK modules not built | 13 |
| Budget: Fleet/day | $50.00 |
| Budget: Total test spend to date | $1.30 |

### 1.5 Agent Roster by Phase

| Phase | Folder | Current Agents | Missing Agents | Current Count | Target Count |
|-------|--------|---------------|----------------|---------------|--------------|
| GOVERN | `agents/govern/` | G1-G4 | G5-audit-reporter | 4 | 5 |
| DESIGN | `agents/claude-cc/D*/` | D1-D11 | D12-localisation-planner | 12 | 13 |
| BUILD | `agents/claude-cc/B*/` | B1-B8 | B9-migration-writer | 8 | 9 |
| TEST | `agents/claude-cc/T*/` | T2-T5 | T1-static-analyser | 4 | 5 |
| DEPLOY | `agents/claude-cc/P*/` | P1-P3 | P4-rollback-manager, P5-feature-flag-manager | 3 | 5 |
| OPERATE | `agents/claude-cc/O*/` | O1-O4 | O5-alert-manager | 4 | 5 |
| OVERSIGHT | `agents/claude-cc/OV-*/` | 8 existing | OV-P1-performance-auditor, OV-D1-dependency-auditor | 8 | 10 |
| **Total** | | | **9 missing** | **43** | **52** |

> Note: The spec states 48 current agents across 7 phases, targeting 52 total (48 + 9 new - 5 overlap adjustments). Agent IDs in the OVERSIGHT phase may need reconciliation in PRD.

### 1.6 Budget Constraints

| Scope | Default Ceiling |
|-------|----------------|
| Fleet | $50/day |
| Project | $20/day |
| Agent | $5/day |
| Invocation | $0.50 |
| Pipeline run | $25/run |

Current BudgetCascade uses stub data and fails open. This is a production safety risk (see R-02 in Risk Register).

---

## 2. Document Build Sequence

The Full-Stack-First approach produces **14 core documents + 2 protocol documents**. The key differentiator from API-First or Design-First is that the **INTERACTION-MAP (Doc 6)** serves as the single coordination document from which both **MCP-TOOL-SPEC (Doc 7)** and **DESIGN-SPEC (Doc 8)** are derived in parallel. This ensures AI interfaces and human interfaces share the same interaction model.

### 2.1 Complete Build Sequence

| Step | Doc # | Document | File Path | Inputs | Parallel With | Status |
|------|-------|----------|-----------|--------|---------------|--------|
| 1 | 0 | **ROADMAP** | `Generated-Docs/00-ROADMAP.md` | Raw spec | Step 2 | **THIS DOC** |
| 2 | 1 | **PRD** | `Generated-Docs/01-PRD.md` | Raw spec | Step 1 | NOT STARTED |
| 3 | 2 | **ARCH** | `Generated-Docs/02-ARCH.md` | PRD | — | NOT STARTED |
| 4 | 3 | **CLAUDE** | `Generated-Docs/03-CLAUDE.md` | ROADMAP + ARCH | — | NOT STARTED |
| 5 | 4 | **QUALITY** | `Generated-Docs/04-QUALITY.md` | PRD + ARCH | Steps 4, 6 | NOT STARTED |
| 6 | 5 | **FEATURE-CATALOG** | `Generated-Docs/05-FEATURE-CATALOG.md` | PRD + ARCH | Steps 4, 5 | NOT STARTED |
| 7 | 6 | **INTERACTION-MAP** | `Generated-Docs/06-INTERACTION-MAP.md` | PRD + ARCH + FEATURES + QUALITY | — | NOT STARTED |
| 8 | 7 | **MCP-TOOL-SPEC** | `Generated-Docs/07-MCP-TOOL-SPEC.md` | INTERACTION-MAP + ARCH + FEATURES + QUALITY | **Step 9** | NOT STARTED |
| 9 | 8 | **DESIGN-SPEC** | `Generated-Docs/08-DESIGN-SPEC.md` | INTERACTION-MAP + PRD + QUALITY + FEATURES | **Step 8** | NOT STARTED |
| 10 | 9 | **DATA-MODEL** | `Generated-Docs/09-DATA-MODEL.md` | ARCH + FEATURES + QUALITY + MCP-TOOL-SPEC + DESIGN-SPEC + INTERACTION-MAP | — | NOT STARTED |
| 11 | 10 | **API-CONTRACTS** | `Generated-Docs/10-API-CONTRACTS.md` | ARCH + DATA-MODEL + PRD + MCP-TOOL-SPEC + DESIGN-SPEC + INTERACTION-MAP | — | NOT STARTED |
| 12 | 11 | **BACKLOG** | `Generated-Docs/11-BACKLOG.md` | All above | — | NOT STARTED |
| 13 | 12 | **ENFORCEMENT** | `Generated-Docs/12-ENFORCEMENT.md` | CLAUDE + ARCH | Steps 12, 14 | NOT STARTED |
| 14 | 13 | **TESTING** | `Generated-Docs/13-TESTING.md` | ARCH + QUALITY + DATA-MODEL + CLAUDE + MCP-TOOL-SPEC + DESIGN-SPEC + INTERACTION-MAP | Steps 12, 13 | NOT STARTED |
| +1 | 14 | **AGENT-HANDOFF-PROTOCOL** | `Generated-Docs/14-AGENT-HANDOFF-PROTOCOL.md` | Build Sequence + ARCH + CLAUDE + QUALITY | — | NOT STARTED |
| +2 | 15 | **AGENT-INTERACTION-DIAGRAM** | `Generated-Docs/15-AGENT-INTERACTION-DIAGRAM.md` | AGENT-HANDOFF-PROTOCOL | — | NOT STARTED |

### 2.2 Document Dependency Graph

```
                              Raw Spec (MASTER-BUILD-SPEC.md)
                                    |
                    +---------------+---------------+
                    |                               |
              [0] ROADMAP                     [1] PRD
                    |                               |
                    +---------------+---------------+
                                    |
                              [2] ARCH
                                    |
                    +---------------+---------------+
                    |               |               |
              [3] CLAUDE      [4] QUALITY    [5] FEATURE-CATALOG
                    |               |               |
                    |               +-------+-------+
                    |                       |
                    |           [6] INTERACTION-MAP     <--- KEY COORDINATION DOC
                    |                       |
                    |           +-----------+-----------+
                    |           |                       |
                    |   [7] MCP-TOOL-SPEC     [8] DESIGN-SPEC     <--- PARALLEL SPRINT
                    |           |                       |
                    |           +-----------+-----------+
                    |                       |
                    |              [9] DATA-MODEL
                    |                       |
                    |             [10] API-CONTRACTS
                    |                       |
                    +----------+   [11] BACKLOG
                    |          |            |
              [12] ENFORCEMENT |   [13] TESTING        <--- PARALLEL
                    |          |            |
                    +----------+------------+
                               |
                  [14] AGENT-HANDOFF-PROTOCOL
                               |
                  [15] AGENT-INTERACTION-DIAGRAM
```

### 2.3 Why INTERACTION-MAP Is the Key Document

The INTERACTION-MAP (Doc 6) defines every touchpoint in the system:
- **Agent-to-Agent** interactions (48 agents, 7 protocol patterns)
- **Agent-to-Human** interactions (dashboard screens, approval flows)
- **Agent-to-MCP** interactions (tool invocations, typed envelopes)
- **Human-to-System** interactions (dashboard CRUD, monitoring)

Both MCP-TOOL-SPEC (the AI interface) and DESIGN-SPEC (the human interface) derive their scope directly from this map. By designing them in parallel from the same source, we guarantee:
1. No interaction is served by only one interface
2. The backend (DATA-MODEL, API-CONTRACTS) can serve both without duplication
3. Conflicts between AI and human paths are caught at design time, not implementation time

---

## 3. Delivery Phases

Each phase is under 3 weeks. Entry and exit criteria are testable. Every deliverable has a specific file path.

### Phase 0: Foundation Documents (Week 1)

**Duration:** 5 days (1 week)
**Goal:** Produce ROADMAP + PRD + ARCH + CLAUDE — the specification foundation.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| Raw spec exists (`Requirement/MASTER-BUILD-SPEC.md`) | ROADMAP, PRD, ARCH, CLAUDE.md all committed to `Generated-Docs/` |
| Repository access confirmed for all team members | All four docs pass peer review (no open TBDs in PRD functional requirements) |
| Team capacity confirmed (2-3 devs available) | ARCH defines all 5 orchestration levels with component diagrams |

**Deliverables:**

| Day | Activity | Output File | Acceptance |
|-----|----------|-------------|------------|
| D1 | Generate ROADMAP + PRD in parallel (Steps 1-2) | `Generated-Docs/00-ROADMAP.md` | This document, reviewed |
| D1 | Generate PRD in parallel with ROADMAP | `Generated-Docs/01-PRD.md` | Personas defined, all 48 agents categorized, 9 missing agents specified |
| D3 | Generate ARCH (depends on PRD) | `Generated-Docs/02-ARCH.md` | All 5 orchestration levels documented, 7 protocol patterns defined |
| D4 | Generate CLAUDE (depends on ROADMAP + ARCH) | `Generated-Docs/03-CLAUDE.md` | Repo structure rules, forbidden patterns, agent conventions |
| D5 | Peer review all 4 documents | Review comments resolved | Zero open TBDs across all docs |

---

### Phase 1: Quality + Features + Interaction Map (Week 2)

**Duration:** 5 days (1 week)
**Goal:** Define quality gates, catalog all features, and produce the INTERACTION-MAP — the central coordination document that enables the parallel MCP + Design sprint in Phase 2.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| ARCH reviewed and stable (no open TBDs) | QUALITY, FEATURE-CATALOG, INTERACTION-MAP committed |
| PRD functional requirements locked | INTERACTION-MAP covers all 48 agents, all dashboard screens, all MCP tool touchpoints |
| CLAUDE.md committed | Every feature in FEATURE-CATALOG has a corresponding quality gate in QUALITY |

**Deliverables:**

| Day | Activity | Output File | Acceptance |
|-----|----------|-------------|------------|
| D1-D2 | Generate QUALITY + FEATURE-CATALOG in parallel (Steps 5-6) | `Generated-Docs/04-QUALITY.md` | Q-NNN NFRs with measurable thresholds for every agent category |
| D1-D2 | (parallel) | `Generated-Docs/05-FEATURE-CATALOG.md` | F-NNN features for all 48+9 agents, dependency graph, priority assignment |
| D3-D5 | Generate INTERACTION-MAP (Step 7, depends on all above) | `Generated-Docs/06-INTERACTION-MAP.md` | Every agent touchpoint identified; every dashboard screen mapped; every MCP tool touchpoint cataloged; zero orphan interactions |

---

### Phase 2: Parallel MCP + Design Sprint (Week 3)

**Duration:** 5 days (1 week)
**Goal:** Design AI interfaces (MCP tools) and human interfaces (dashboard) simultaneously from the shared INTERACTION-MAP. This is the defining sprint of the Full-Stack-First approach.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| INTERACTION-MAP reviewed and frozen | MCP-TOOL-SPEC and DESIGN-SPEC both committed |
| QUALITY gates defined for every feature | Every INTERACTION-MAP touchpoint covered by either MCP tool or dashboard screen (or both) |
| FEATURE-CATALOG complete with all 48+9 agents | No orphan touchpoints — every interaction has both AI and human access path |

**Deliverables (built in parallel — Steps 8 and 9):**

| Day | Activity | Output File | Acceptance |
|-----|----------|-------------|------------|
| D1-D5 | Generate MCP-TOOL-SPEC (AI interface, Step 8) | `Generated-Docs/07-MCP-TOOL-SPEC.md` | Every MCP tool has typed input/output schemas; tool-to-agent mapping complete; references INTERACTION-MAP touchpoint IDs |
| D1-D5 | Generate DESIGN-SPEC (human interface, Step 9) | `Generated-Docs/08-DESIGN-SPEC.md` | Every Streamlit screen wireframed; screen-to-agent mapping complete; references INTERACTION-MAP touchpoint IDs |

**Coordination Protocol for Parallel Sprint:**
1. Both documents MUST reference INTERACTION-MAP touchpoint IDs for traceability
2. Daily 15-minute sync between MCP and Design authors to surface conflicts
3. Any conflict (e.g., MCP tool and dashboard screen assume different data shapes) triggers an immediate review before either document advances
4. Shared decisions logged in `Generated-Docs/phase2-sync-log.md`

---

### Phase 3: Data + API Layer (Week 4-5)

**Duration:** 10 days (2 weeks)
**Goal:** Define the unified data model and API contracts that serve both MCP tools and dashboard screens.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| MCP-TOOL-SPEC and DESIGN-SPEC both frozen | DATA-MODEL covers every entity from both specs |
| No unresolved conflicts from Phase 2 sync | API-CONTRACTS expose every operation needed by MCP tools AND dashboard |
| INTERACTION-MAP touchpoints fully covered | Migrations 005-008 SQL defined in DATA-MODEL |
|  | Every API endpoint traceable to an INTERACTION-MAP touchpoint |

**Deliverables:**

| Day | Activity | Output File | Acceptance |
|-----|----------|-------------|------------|
| D1-D5 | Generate DATA-MODEL (Step 10) | `Generated-Docs/09-DATA-MODEL.md` | All tables defined; migrations 005-008 SQL included; entity-relationship diagram; covers MCP + Design entities |
| D6-D10 | Generate API-CONTRACTS (Step 11) | `Generated-Docs/10-API-CONTRACTS.md` | REST + WebSocket endpoints; request/response schemas; MCP tool endpoints; dashboard endpoints; auth model |

**Key DATA-MODEL deliverables within the document:**
- `migrations/005_knowledge_exceptions.sql` — knowledge store exceptions table
- `migrations/006_session_context.sql` — BLOCKING: enables SessionStore (FIX-01)
- `migrations/007_approval_requests.sql` — approval gate persistence
- `migrations/008_pipeline_checkpoints.sql` — pipeline pause/resume state

---

### Phase 4: Backlog + Governance (Week 6)

**Duration:** 5 days (1 week)
**Goal:** Produce the actionable backlog, enforcement rules, and testing strategy. Steps 12-14 overlap.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| All 10 upstream documents committed (Docs 0-10) | BACKLOG has every work item with priority, estimate, and agent assignment |
| DATA-MODEL and API-CONTRACTS reviewed | ENFORCEMENT rules are machine-checkable (can be validated by CI) |
| No open decisions with severity BLOCKING | TESTING strategy covers unit, integration, contract, and E2E layers |

**Deliverables (partially parallel — Steps 12, 13, 14):**

| Day | Activity | Output File | Acceptance |
|-----|----------|-------------|------------|
| D1-D3 | Generate BACKLOG (Step 12) | `Generated-Docs/11-BACKLOG.md` | S-NNN stories for all FIX items, all 9 missing agents, all 5 missing pipelines; prioritized P1-P5 |
| D2-D4 | Generate ENFORCEMENT (Step 13, parallel with BACKLOG tail + TESTING) | `Generated-Docs/12-ENFORCEMENT.md` | Rules derived from CLAUDE + ARCH; `.claude/` enforcement config generated |
| D2-D5 | Generate TESTING (Step 14, parallel with ENFORCEMENT) | `Generated-Docs/13-TESTING.md` | Test strategy for all SDK modules; contract tests for MCP tools; E2E test plan for team pipelines |

---

### Phase 5: Agent Protocol Documents (Week 7)

**Duration:** 5 days (1 week)
**Goal:** Define agent handoff protocol and produce the interaction diagram. Complete the 14+2 document set.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| BACKLOG, ENFORCEMENT, TESTING all committed | AGENT-HANDOFF-PROTOCOL covers all 7 SDLC phases and all 5 orchestration levels |
| ARCH orchestration model stable | AGENT-INTERACTION-DIAGRAM renders all 48 agents and 14 team pipelines |
| CLAUDE.md agent conventions locked | Protocol validated against compliance-audit team flow |
|  | **All 16 documents committed** — documentation phase complete |

**Deliverables:**

| Day | Activity | Output File | Acceptance |
|-----|----------|-------------|------------|
| D1-D3 | Generate AGENT-HANDOFF-PROTOCOL (Step +1) | `Generated-Docs/14-AGENT-HANDOFF-PROTOCOL.md` | Typed message envelopes for all 7 protocol patterns; handoff sequences for all team workflows; error recovery paths |
| D4-D5 | Generate AGENT-INTERACTION-DIAGRAM (Step +2) | `Generated-Docs/15-AGENT-INTERACTION-DIAGRAM.md` | Visual diagram (Mermaid or ASCII) of all agents; swimlanes by SDLC phase; pipeline flows marked |

---

### Phase 6: FIX-01 SessionStore + P1 Blockers (Week 8-9)

**Duration:** 10 days (2 weeks)
**Goal:** Resolve FIX-01 (SessionStore) and all P1 blocking items. First code phase.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| All 16 documents committed and reviewed | SessionStore passes integration tests (8+ tests) |
| DATA-MODEL migration 006 SQL defined | PostgresCostStore replaces stub; BudgetCascade is fail-closed |
| API-CONTRACTS for session endpoints defined | Input/Output validation active on all 48 agents |
| TESTING strategy defines session test plan | Migrations 005-006 applied to dev database |

**Deliverables:**

| Item | File Path | Tests |
|------|-----------|-------|
| SessionStore | `sdk/context/session_store.py` | `tests/test_session_store.py` (8 tests: CRUD, TTL, concurrent) |
| PostgresCostStore | `sdk/stores/postgres_cost_store.py` | `tests/test_postgres_cost_store.py` (6 tests: insert, aggregate, budget-check, fail-closed) |
| Input/Output validation | `sdk/validation.py` | `tests/test_validation.py` (5 tests) |
| Migration 005 | `migrations/005_knowledge_exceptions.sql` | Apply + verify |
| Migration 006 | `migrations/006_session_context.sql` | Apply + verify |
| Updated BudgetCascade | `sdk/budget_cascade.py` (modify) | `tests/test_budget_cascade.py` (3 new fail-closed tests) |

---

### Phase 7: P2 Infrastructure (Week 10-11)

**Duration:** 10 days (2 weeks)
**Goal:** Build ApprovalStore, PipelineCheckpoint, rate limiter, CI/CD pipeline.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| SessionStore deployed and stable (FIX-01 closed) | ApprovalStore passes approval flow tests |
| Migrations 005-006 applied | PipelineCheckpoint supports save/load/resume/expire |
| BudgetCascade fail-closed verified | TokenBucketRateLimiter enforces budget hierarchy |
|  | CI/CD pipeline runs all tests on push |

**Deliverables:**

| Item | File Path | Tests |
|------|-----------|-------|
| ApprovalStore | `sdk/stores/approval_store.py` | `tests/test_approval_store.py` (6 tests) |
| PipelineCheckpoint | `sdk/orchestration/pipeline_checkpoint.py` | `tests/test_pipeline_checkpoint.py` (5 tests) |
| TokenBucketRateLimiter | `sdk/rate_limiter.py` | `tests/test_rate_limiter.py` (5 tests) |
| Migration 007 | `migrations/007_approval_requests.sql` | Apply + verify |
| Migration 008 | `migrations/008_pipeline_checkpoints.sql` | Apply + verify |
| CI/CD pipeline | `.github/workflows/ci.yml` | Push triggers lint + test + schema-validate |

---

### Phase 8: Agent Implementations — Batch 1 (Week 12-14)

**Duration:** 15 days (3 weeks)
**Goal:** Implement GOVERN + DESIGN + BUILD agents with real prompts. Create 3 new agents (G5, D12, B9).

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| All P1+P2 infrastructure merged and green | 27 agents pass real API calls (not dry-run) |
| Rate limiter active on BaseAgent | Cost per agent invocation under individual budget ceiling ($5/day) |
| AGENT-HANDOFF-PROTOCOL defines message contracts | All 27 prompt.md files are production-grade (zero stubs) |

**Agent Breakdown:**

| Phase | Agents | Count | New? |
|-------|--------|-------|------|
| GOVERN | G1-G5 | 5 | G5-audit-reporter (new) |
| DESIGN | D1-D13 | 13 | D12-localisation-planner (new) |
| BUILD | B1-B9 | 9 | B9-migration-writer (new) |
| **Subtotal** | | **27** | **3 new** |

**Per-agent deliverable set:**

For each agent `{ID}`:
- `agents/{path}/{ID}/manifest.yaml` — validated against schema
- `agents/{path}/{ID}/prompt.md` — production-grade, no stubs
- `agents/{path}/{ID}/agent.py` — real implementation
- `tests/test_{id}.py` — unit tests + dry-run + real API call test

---

### Phase 9: Agent Implementations — Batch 2 + Teams (Week 15-17)

**Duration:** 15 days (3 weeks)
**Goal:** Implement TEST + DEPLOY + OPERATE + OVERSIGHT agents. Create 6 new agents. Build 5 missing team pipelines.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| Batch 1 agents stable (27 green) | All 48 agents pass real API calls |
| PipelineRunner operational | All 14 team pipelines execute successfully |
| TeamOrchestrator merged | compliance-audit team real run cost under $3.00 |
|  | All 9 missing agents created and passing |

**Agent Breakdown:**

| Phase | Agents | Count | New? |
|-------|--------|-------|------|
| TEST | T1-T5 | 5 | T1-static-analyser (new) |
| DEPLOY | P1-P5 | 5 | P4-rollback-manager, P5-feature-flag-manager (new) |
| OPERATE | O1-O5 | 5 | O5-alert-manager (new) |
| OVERSIGHT | OV-D1 through OV-P1 | 10 | OV-P1-performance-auditor, OV-D1-dependency-auditor (new) |
| **Subtotal** | | **25** | **6 new** |

**Missing Team Pipelines:**

| Pipeline | File Path | Key Agents |
|----------|-----------|------------|
| bug-fix | `workflows/teams/bug-fix.yaml` | B1, B2, T2, T3 |
| hotfix | `workflows/teams/hotfix.yaml` | B1, P3, P4, T3 |
| security-patch | `workflows/teams/security-patch.yaml` | B7, B1, T2, P3 |
| compliance-review | `workflows/teams/compliance-review.yaml` | G2, G5, OV-D5, B7 |
| performance-optimization | `workflows/teams/performance-optimization.yaml` | OV-P1, B1, T3, P3 |

---

### Phase 10: Dashboard + Observability + Release (Week 18-19)

**Duration:** 10 days (2 weeks)
**Goal:** Streamlit dashboard, OTel instrumentation, REST API, WebSocket, CLI. Ship v1.0.

| Entry Criteria | Exit Criteria |
|---------------|---------------|
| All 48 agents passing real API calls | Dashboard shows live agent status, cost tracking, pipeline views |
| DESIGN-SPEC dashboard wireframes stable | OTel traces emitted for every agent invocation |
| API-CONTRACTS endpoints defined | REST API serves all MCP tool and dashboard data |
| MCP-TOOL-SPEC tool definitions stable | CLI tool executes basic agent and pipeline commands |
|  | All 10 FIX items verified closed |

**Deliverables:**

| Item | File Path | Tests |
|------|-----------|-------|
| Streamlit dashboard | `dashboard/app.py` | Manual: cost, health, pipeline views render |
| REST API routes | `api/routes/` | `tests/test_api_routes.py` |
| WebSocket events | `api/ws/` | `tests/test_ws.py` |
| OTel instrumentation | `sdk/observability/otel_instrumentation.py` | `tests/test_otel.py` |
| CLI tool | `cli/agentic.py` | `tests/test_cli.py` |
| Multi-env config | `config/` | `tests/test_config.py` |
| mTLS (if OD-08 = v1.0) | `sdk/security/mtls.py` | `tests/test_mtls.py` |

---

## 4. Milestones

| ID | Milestone | Target Week | Done Definition (binary) |
|----|-----------|-------------|--------------------------|
| G1 | Foundation documents complete | W1 | `Generated-Docs/00-ROADMAP.md` through `Generated-Docs/03-CLAUDE.md` committed and peer-reviewed; zero open TBDs |
| G2 | INTERACTION-MAP signed off | W2 | `Generated-Docs/06-INTERACTION-MAP.md` committed; covers all 48 agents, all dashboard screens, all MCP tool touchpoints |
| G3 | Parallel MCP + Design sprint complete | W3 | `Generated-Docs/07-MCP-TOOL-SPEC.md` and `Generated-Docs/08-DESIGN-SPEC.md` committed; every INTERACTION-MAP touchpoint has coverage |
| G4 | Data + API layer complete | W5 | `Generated-Docs/09-DATA-MODEL.md` and `Generated-Docs/10-API-CONTRACTS.md` committed; migrations 005-008 SQL defined |
| G5 | All 16 documents committed | W7 | All files `Generated-Docs/00-ROADMAP.md` through `Generated-Docs/15-AGENT-INTERACTION-DIAGRAM.md` exist; no unresolved TBDs |
| G6 | FIX-01 SessionStore resolved | W9 | `sdk/context/session_store.py` passes 8+ integration tests; migration 006 applied to dev DB |
| G7 | All P1 blockers resolved | W9 | FIX-01, FIX-04, FIX-08 all closed; CI green on all affected modules |
| G8 | All P2 items resolved | W11 | FIX-02, FIX-03, FIX-09 closed; CI/CD pipeline operational; migrations 007-008 applied |
| G9 | First 27 agents live | W14 | GOVERN + DESIGN + BUILD agents pass real API calls; cost under budget per agent |
| G10 | All 48 agents live | W17 | Every agent passes real API call; all 14 team pipelines execute successfully |
| G11 | All 9 missing agents created | W17 | G5, T1, P4, P5, O5, B9, D12, OV-P1, OV-D1 all pass schema validation + real API |
| G12 | Dashboard v1 shipped | W19 | Streamlit app shows live agent status, cost dashboard, pipeline view; accessible at configured URL |
| G13 | All FIX items closed | W19 | FIX-01 through FIX-10 each have a passing test that proves the fix |
| G14 | Platform v1.0 release | W20 | Git tag `v1.0.0`; all milestones G1-G13 verified; CHANGELOG.md updated |

---

## 5. Open Decisions

| ID | Question | Options | Who Decides | What It Blocks | Decide By |
|----|----------|---------|-------------|----------------|-----------|
| OD-01 | **SessionStore backend: PostgreSQL or Redis?** | (A) PostgreSQL — consistent with existing migrations, single DB to manage. (B) Redis — faster TTL-based expiry, purpose-built for sessions. (C) PostgreSQL primary + Redis cache layer. | Platform lead | FIX-01, Phase 6, migration 006 schema, everything downstream | W1 |
| OD-02 | **Dashboard framework: keep Streamlit or move to FastAPI+React?** | (A) Streamlit — faster to ship, already in tech stack spec. (B) FastAPI+React — better WebSocket support, richer UX. (C) Streamlit for v1.0, plan migration for v2.0. | Platform lead | Phase 10, DESIGN-SPEC scope, dashboard component architecture | W3 |
| OD-03 | **Rate limiter scope: per-agent or cascading?** | (A) Per-agent token buckets only. (B) Per-pipeline only. (C) Cascading: fleet -> project -> pipeline -> agent (matches budget hierarchy). | Platform team | FIX-09, TokenBucketRateLimiter design, parallel agent execution safety | W2 |
| OD-04 | **Agent versioning strategy** | (A) Semver in manifest.yaml `version` field. (B) Git tag-based (`agent/{id}/v{semver}`). (C) Both — manifest declares intent, git tag enforces immutability. | Platform team | FIX-05, agent hot-reload, manifest schema update | W4 |
| OD-05 | **BudgetCascade fail behavior** | (A) Fail-closed: reject invocation when cost store unavailable. (B) Fail-open with alert (current — dangerous). (C) Fail-closed with 60-second grace period + alert. | Platform lead | FIX-04, production safety, every agent invocation | W1 |
| OD-06 | **Multi-environment config strategy** | (A) `.env` files per environment. (B) HashiCorp Vault / SOPS encrypted configs. (C) Environment variables + Kubernetes ConfigMaps. | Platform team | Phase 10, deployment pipeline, secret management | W6 |
| OD-07 | **MCP tool granularity** | (A) 1:1 — one MCP tool per agent (48 tools). (B) 7 phase-level tools with sub-commands. (C) Hybrid — phase-level tools + key individual agents exposed directly. | Platform team | MCP-TOOL-SPEC (Doc 7), API surface area, client complexity | W2 |
| OD-08 | **mTLS requirement timeline** | (A) Required from v1.0 for all inter-service communication. (B) Optional in v1.0, required in v1.1. (C) Only for external-facing endpoints, not agent-to-SDK internal calls. | Platform lead | ARCH security model, Phase 10 deployment, certificate management | W3 |
| OD-09 | **Parallel DAG execution model** | (A) `asyncio.gather` with semaphore (simplest). (B) Task queue (Celery/Dramatiq). (C) Custom DAG scheduler with topological sort. | Platform team | FIX-06, PipelineRunner design, scalability model | W4 |
| OD-10 | **Missing agent model selection** | (A) All 9 new agents use `claude-haiku-4-5` (cheapest). (B) Match the archetype default model for each phase. (C) Let each agent manifest define its own model. | Platform team | Phase 8-9, cost projections, manifest schema | W7 |

---

## 6. Risk Register

| ID | Risk | Prob. | Impact | Mitigation |
|----|------|-------|--------|------------|
| R-01 | **SessionStore delay blocks entire pipeline.** FIX-01 is the single critical-path blocker. Any slip cascades to all code phases. | HIGH | CRITICAL | Decide OD-01 in W1. Start SessionStore spike during Phase 0 document writing. Pre-author migration 006 SQL. Have in-memory fallback shim ready as escape hatch (not production, but unblocks dev). |
| R-02 | **BudgetCascade fail-open allows runaway API costs.** Current stub data means budget enforcement is theater. An agent retry loop could burn the entire fleet budget in minutes. | HIGH | HIGH | Decide OD-05 in W1. Implement hard $0.50/invocation circuit breaker in BaseHooks immediately (before Phase 6). Track cumulative spend in `state/cost_ledger.json`. |
| R-03 | **~40 stub prompt.md files mask agent quality.** Agents pass dry-run with stubs but will produce garbage with real API calls. Fixing 40 prompts is significant work not visible in infrastructure phases. | HIGH | MEDIUM | Prompt authoring is an explicit deliverable in Phases 8-9. No agent marked "live" until its prompt is peer-reviewed. Add prompt quality gate to ENFORCEMENT.md (Doc 12). |
| R-04 | **Parallel MCP + Design sprint produces irreconcilable conflicts.** Steps 8-9 run simultaneously; if MCP-TOOL-SPEC and DESIGN-SPEC assume different data models or interaction patterns, rework is expensive. | MEDIUM | HIGH | INTERACTION-MAP (Doc 6) is the binding contract. Both specs reference its touchpoint IDs. Daily sync during Week 3. Any conflict immediately escalated — neither doc advances until resolved. |
| R-05 | **2-3 person team is undersized.** 48 agents x (prompt + impl + tests) = ~96 person-days for agents alone. Plus 16 documents, 13 SDK modules, 5 pipelines, migrations, dashboard. | HIGH | HIGH | Phases 8-9 are the largest. Use agent archetypes to template common patterns (7 archetypes cover 48 agents). Consider contractor for prompt authoring. Accept that timeline may stretch by 2-3 weeks. |
| R-06 | **No rate limiting during parallel agent calls.** Without FIX-09, team pipelines running 4+ agents will hit Anthropic API rate limits or blow budget. | MEDIUM | HIGH | Implement `asyncio.Semaphore(2)` in BaseAgent as interim guard before Phase 7. FIX-09 (TokenBucketRateLimiter) provides the real fix. Never run parallel agents in production without rate limiter. |
| R-07 | **Document regeneration cascade invalidates downstream work.** Changing ARCH after DATA-MODEL is written could invalidate 8+ documents. | LOW | HIGH | Freeze ARCH after Phase 1. Freeze INTERACTION-MAP before Phase 2 starts. Freeze DATA-MODEL after Phase 3. Change request process (Section 8) for any post-freeze modification. |
| R-08 | **Claude API cost overrun during 48-agent implementation.** At $0.134/call (B1) with hundreds of test iterations per agent, Phases 8-9 could cost $200-500 in API calls. | MEDIUM | MEDIUM | Use dry-run mode for development iterations. Real API calls only for acceptance tests. Track daily spend. Alert at 80% of $50/day fleet ceiling. Budget $500 for entire Phase 8-9 testing. |
| R-09 | **9 missing agents have undefined requirements.** Names exist but no functional spec, no prompt strategy, no expected output schema. | MEDIUM | MEDIUM | PRD (Doc 1) MUST define functional requirements for all 9 new agents. FEATURE-CATALOG (Doc 5) MUST include them. Do not defer specification to implementation phase. |
| R-10 | **Claude Agent SDK upstream breaking changes.** The SDK is pre-1.0; breaking changes between minor versions could invalidate BaseAgent patterns. | LOW | HIGH | Pin SDK version in `pyproject.toml`. Maintain `sdk/compat.py` abstraction layer. Monitor SDK changelog weekly. |
| R-11 | **INTERACTION-MAP quality determines everything downstream.** If Doc 6 has gaps, both MCP-TOOL-SPEC and DESIGN-SPEC inherit those gaps, and they propagate through DATA-MODEL and API-CONTRACTS. | MEDIUM | CRITICAL | Allocate 3 full days for INTERACTION-MAP (D3-D5 of Phase 1). Require sign-off from all team members. Run a "touchpoint audit": for every agent, confirm there is an AI path AND a human path. |
| R-12 | **E2E tests are flaky due to LLM nondeterminism.** Agent outputs vary between invocations even with identical inputs. Tests that assert exact outputs will fail intermittently. | HIGH | MEDIUM | Use `temperature: 0.0` for all test invocations. Assert on output schema compliance and structural properties, not exact strings. Allow 3 retries in E2E test harness. |

---

## 7. Timeline Visualization

```
WEEK   1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18   19   20
       |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |
       +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
       |         DOCUMENTATION PHASES              |              IMPLEMENTATION PHASES               |
       +----+----+----+----+----+----+----+---------+----+----+----+----+----+----+----+----+----+----+

P0     [=====]                                      Foundation: ROADMAP + PRD + ARCH + CLAUDE
       G1
            |
P1          [=====]                                 QUALITY + FEATURES + INTERACTION-MAP
            G2
                 |
P2               [=====]                            PARALLEL MCP + DESIGN SPRINT
                 |     |                            +-- MCP-TOOL-SPEC ----+
                 |     |                            +-- DESIGN-SPEC ------+  <--- FROM SHARED
                 G3    |                                                      INTERACTION-MAP
                       |
P3                     [===========]                DATA-MODEL + API-CONTRACTS
                              G4
                              |
P4                            [=====]               BACKLOG + ENFORCEMENT + TESTING (parallel)
                              |     |
P5                            |     [=====]         AGENT-HANDOFF-PROTOCOL + INTERACTION-DIAGRAM
                              |     G5
                              |     |
                              |     +--- ALL 16 DOCUMENTS COMMITTED ---
                              |                     |
P6                            |                     [===========]       SessionStore + P1 blockers
                              |                            G6 G7
                              |                            |
P7                            |                            [===========]  P2: Approvals + Checkpoint + Rate Limiter
                              |                                   G8
                              |                                   |
P8                            |                                   [================]  Agents Batch 1 (GOVERN+DESIGN+BUILD)
                              |                                               G9
                              |                                               |
P9                            |                                               [================]  Agents Batch 2 + Teams
                              |                                                          G10 G11
                              |                                                          |
P10                           |                                                          [===========]  Dashboard + OTel
                              |                                                                 G12 G13
                              |                                                                      |
                              |                                                                     G14
                              |                                                                   v1.0.0
                              |
LEGEND:
  [=====]  = Phase duration (each = spans the weeks shown)
  G{N}     = Milestone (see Section 4)
  P{N}     = Phase number (see Section 3)

CRITICAL PATH:
  P0 -> P1 -> P2 -> P3 -> P4/P5 -> P6 -> P7 -> P8 -> P9 -> P10

PARALLEL TRACKS (2-3 developers):
  Track A: P0(docs) -> P1(INTERACTION-MAP) -> P2(MCP-TOOL-SPEC) -> P3(DATA-MODEL) -> P6(SessionStore) -> P8(agents)
  Track B: P0(docs) -> P1(QUALITY)         -> P2(DESIGN-SPEC)   -> P3(API-CONTRACTS) -> P7(infra)     -> P9(agents)

KEY PARALLEL SPRINTS:
  Week 2:  QUALITY + FEATURE-CATALOG (Steps 5-6)
  Week 3:  MCP-TOOL-SPEC + DESIGN-SPEC (Steps 8-9)  <--- FULL-STACK-FIRST SIGNATURE
  Week 6:  BACKLOG + ENFORCEMENT + TESTING (Steps 12-14)
```

### Simplified Gantt

```
Phase                        W1  W2  W3  W4  W5  W6  W7  W8  W9  W10 W11 W12 W13 W14 W15 W16 W17 W18 W19 W20
P0  Foundation Docs          ===
P1  Quality+Features+IntMap      ===
P2  MCP+Design (PARALLEL)           ===
P3  Data+API                             === ===
P4  Backlog+Enforcement+Test                     ===
P5  Agent Protocols                                  ===
                             --- DOCS COMPLETE (G5) ---+
P6  SessionStore+P1                                      === ===
P7  P2 Infrastructure                                           === ===
P8  Agents Batch 1                                                      === === ===
P9  Agents Batch 2 + Teams                                                          === === ===
P10 Dashboard+OTel+Release                                                                      === ===
                                                                                                     ^
                                                                                                  v1.0.0
```

---

## 8. Document Versioning & Regeneration Policy

### 8.1 Version Format

All documents follow this header format:

```
v{MAJOR}.{MINOR} | Full-Stack-First | {YYYY-MM-DD}
```

- **MAJOR** increments on structural changes: new sections added, sections removed, scope changed.
- **MINOR** increments on content updates within existing structure.
- Example: `v1.0 | Full-Stack-First | 2026-03-24` (this document).

Every document includes a changelog table at the bottom:

```markdown
## Changelog
| Version | Date | Author | Change |
|---------|------|--------|--------|
| v1.0 | 2026-03-24 | Platform team | Initial generation |
```

### 8.2 Regeneration Cascade

When a document changes, all downstream documents must be reviewed and potentially regenerated. The cascade follows the dependency graph in Section 2.2.

| If This Doc Changes... | Then Review/Regenerate These Docs... |
|------------------------|--------------------------------------|
| **[0] ROADMAP** | [3] CLAUDE |
| **[1] PRD** | [2] ARCH, [4] QUALITY, [5] FEATURE-CATALOG, [6] INTERACTION-MAP, [8] DESIGN-SPEC, [10] API-CONTRACTS, [11] BACKLOG |
| **[2] ARCH** | [3] CLAUDE, [4] QUALITY, [5] FEATURE-CATALOG, [6] INTERACTION-MAP, [7] MCP-TOOL-SPEC, [9] DATA-MODEL, [10] API-CONTRACTS, [12] ENFORCEMENT, [13] TESTING, [14] AGENT-HANDOFF-PROTOCOL |
| **[3] CLAUDE** | [12] ENFORCEMENT, [13] TESTING, [14] AGENT-HANDOFF-PROTOCOL |
| **[4] QUALITY** | [6] INTERACTION-MAP, [7] MCP-TOOL-SPEC, [8] DESIGN-SPEC, [9] DATA-MODEL, [13] TESTING |
| **[5] FEATURE-CATALOG** | [6] INTERACTION-MAP, [7] MCP-TOOL-SPEC, [8] DESIGN-SPEC, [9] DATA-MODEL |
| **[6] INTERACTION-MAP** | [7] MCP-TOOL-SPEC, [8] DESIGN-SPEC, [9] DATA-MODEL, [10] API-CONTRACTS, [13] TESTING |
| **[7] MCP-TOOL-SPEC** | [9] DATA-MODEL, [10] API-CONTRACTS, [13] TESTING |
| **[8] DESIGN-SPEC** | [9] DATA-MODEL, [10] API-CONTRACTS, [13] TESTING |
| **[9] DATA-MODEL** | [10] API-CONTRACTS, [13] TESTING |
| **[10] API-CONTRACTS** | [11] BACKLOG |
| **[14] AGENT-HANDOFF-PROTOCOL** | [15] AGENT-INTERACTION-DIAGRAM |

**Key insight:** Changing ARCH (Doc 2) triggers the largest cascade — 10 downstream documents. This is why ARCH freezes early.

### 8.3 Freeze Rules

Documents freeze at specific milestones. Post-freeze changes require the formal change request process.

| Document | Freeze Point | Unfreeze Requires |
|----------|-------------|-------------------|
| [0] ROADMAP | End of Phase 0 (G1) | Change Request approved by platform lead |
| [1] PRD | End of Phase 0 (G1) | Change Request approved by platform lead |
| [2] ARCH | End of Phase 1 (G2) | Change Request approved by platform lead + impact analysis |
| [3] CLAUDE | End of Phase 1 (G2) | Change Request approved by platform lead |
| [4] QUALITY | Start of Phase 2 (before G3) | Change Request + INTERACTION-MAP impact review |
| [5] FEATURE-CATALOG | Start of Phase 2 (before G3) | Change Request + INTERACTION-MAP impact review |
| [6] INTERACTION-MAP | Start of Phase 2 (before G3) | Synchronous review by both MCP and Design authors; both must approve |
| [7] MCP-TOOL-SPEC | End of Phase 2 (G3) | Change Request + DATA-MODEL impact analysis |
| [8] DESIGN-SPEC | End of Phase 2 (G3) | Change Request + DATA-MODEL impact analysis |
| [9] DATA-MODEL | End of Phase 3 (G4) | Change Request + migration compatibility proof |
| [10] API-CONTRACTS | End of Phase 3 (G4) | Change Request + backward compatibility proof |
| [11-15] All remaining | G5 milestone (W7) | Formal change request process only |

**Hard freeze:** After G5 (all 16 docs committed, W7), no document changes without a formal Change Request.

### 8.4 Change Request Format

Post-freeze changes to any document must be submitted as a Change Request file.

**File path:** `Generated-Docs/change-requests/CR-{NNN}-{short-name}.md`

**Template:**

```markdown
# CR-{NNN}: {Title}

- **Date:** {YYYY-MM-DD}
- **Author:** {name}
- **Document(s) affected:** {doc number and name}
- **Severity:** PATCH | MINOR | MAJOR
- **Status:** PROPOSED | APPROVED | REJECTED | APPLIED

## What Changed
{Specific description of the change — quote old text and new text}

## Why
{Business or technical justification — what breaks without this change}

## Regeneration Impact
{List every downstream document from Section 8.2 that needs review}
| Document | Impact | Action Required |
|----------|--------|-----------------|
| {doc} | {what changes} | Review / Regenerate / No impact |

## Backward Compatibility
{Does this break any existing implementation code? If yes, migration plan.}

## Approval
- [ ] Platform lead sign-off
- [ ] Affected document author(s) sign-off
- [ ] Downstream document owners notified
```

### 8.5 Document Storage Layout

```
Generated-Docs/
  00-ROADMAP.md
  01-PRD.md
  02-ARCH.md
  03-CLAUDE.md
  04-QUALITY.md
  05-FEATURE-CATALOG.md
  06-INTERACTION-MAP.md
  07-MCP-TOOL-SPEC.md
  08-DESIGN-SPEC.md
  09-DATA-MODEL.md
  10-API-CONTRACTS.md
  11-BACKLOG.md
  12-ENFORCEMENT.md
  13-TESTING.md
  14-AGENT-HANDOFF-PROTOCOL.md
  15-AGENT-INTERACTION-DIAGRAM.md
  change-requests/
    CR-001-example.md
  archive/
    00-ROADMAP-v0.9.md
  .build-state.json
```

### 8.6 Build State Tracking

A machine-readable file tracks document generation state for tooling and automation.

**File:** `Generated-Docs/.build-state.json`

```json
{
  "approach": "full-stack-first",
  "total_documents": 16,
  "generated_at": "2026-03-24",
  "documents": [
    {
      "number": 0,
      "name": "ROADMAP",
      "file": "00-ROADMAP.md",
      "version": "1.0",
      "status": "GENERATED",
      "frozen": false,
      "freeze_at": "G1",
      "last_modified": "2026-03-24",
      "depends_on": [],
      "depended_by": [3]
    },
    {
      "number": 1,
      "name": "PRD",
      "file": "01-PRD.md",
      "version": null,
      "status": "NOT_STARTED",
      "frozen": false,
      "freeze_at": "G1",
      "last_modified": null,
      "depends_on": [],
      "depended_by": [2, 4, 5, 6, 8, 10, 11]
    },
    {
      "number": 6,
      "name": "INTERACTION-MAP",
      "file": "06-INTERACTION-MAP.md",
      "version": null,
      "status": "NOT_STARTED",
      "frozen": false,
      "freeze_at": "G3-start",
      "last_modified": null,
      "depends_on": [1, 2, 4, 5],
      "depended_by": [7, 8, 9, 10, 13],
      "notes": "KEY COORDINATION DOCUMENT — enables parallel MCP+Design sprint"
    }
  ]
}
```

> Note: Only 3 entries shown for illustration. The full file will contain all 16 documents.

---

## Appendix A: FIX Item Traceability

Every FIX item maps to a specific delivery phase and has a binary verification criterion.

| FIX ID | Description | Phase | Deliverable File | Verification |
|--------|-------------|-------|-----------------|--------------|
| FIX-01 | SessionStore (BLOCKING) | Phase 6 | `sdk/context/session_store.py` | 8 integration tests pass; migration 006 applied |
| FIX-02 | Approval gates | Phase 7 | `sdk/stores/approval_store.py` | 6 unit tests pass (create, approve, reject, timeout, query, audit-trail) |
| FIX-03 | Pipeline checkpoint | Phase 7 | `sdk/orchestration/pipeline_checkpoint.py` | 5 unit tests pass (save, load, resume, expire, list) |
| FIX-04 | Real cost store | Phase 6 | `sdk/stores/postgres_cost_store.py` | 6 unit tests pass; BudgetCascade fail-closed verified |
| FIX-05 | Agent versioning | Phase 8 | `sdk/manifest_loader.py` (modify) | Version mismatch raises `VersionConflictError`; 2 tests pass |
| FIX-06 | Parallel DAG | Phase 9 | `sdk/orchestration/dag_executor.py` | 3-agent fan-out/fan-in test passes; respects rate limiter |
| FIX-07 | Dashboard | Phase 10 | `dashboard/app.py` | Renders cost, health, pipeline views with live data |
| FIX-08 | I/O validation | Phase 6 | `sdk/validation.py` | Invalid input rejected with `ValidationError`; 5 tests pass |
| FIX-09 | Rate limiter | Phase 7 | `sdk/rate_limiter.py` | 5 tests pass (acquire, exhaust, refill, concurrent, burst) |
| FIX-10 | Complete all prompts | Phase 8-9 | `agents/**/prompt.md` | `grep -r "TODO\|STUB\|placeholder" agents/**/prompt.md` returns 0 results |

## Appendix B: Migration Sequence

| Migration | File | Purpose | Depends On | Resolves |
|-----------|------|---------|------------|----------|
| 005 | `migrations/005_knowledge_exceptions.sql` | Knowledge store exceptions table | Migrations 001-004 | — |
| 006 | `migrations/006_session_context.sql` | Session context storage | Migration 005 | FIX-01 (BLOCKING) |
| 007 | `migrations/007_approval_requests.sql` | Approval gate persistence | Migration 006 | FIX-02 |
| 008 | `migrations/008_pipeline_checkpoints.sql` | Pipeline pause/resume state | Migration 006 | FIX-03 |

## Appendix C: Success Criteria for v1.0.0

The release is ready when ALL of these are true:

1. **48 agents live** — all pass real API calls (not dry-run), all schema-valid
2. **9 new agents created** — G5, T1, P4, P5, O5, B9, D12, OV-P1, OV-D1 all operational
3. **14 team pipelines** — all execute successfully, compliance-audit team under $3.00
4. **16 documents** — all committed, all cross-references valid, all frozen
5. **13 SDK modules** — all pass unit tests
6. **10 FIX items** — all verified closed per Appendix A
7. **8 migrations** — all applied, rollback scripts exist for each
8. **0 stub prompt.md files** — every agent has a production-grade prompt
9. **Budget enforcement** — fail-closed, tested with 5 parallel agents under load
10. **Dashboard** — Streamlit app shows cost, health, pipeline status in real time
11. **MCP tools** — all tools defined in MCP-TOOL-SPEC are callable
12. **Observability** — OTel traces emitted for every agent invocation

---

## Changelog

| Version | Date | Author | Change |
|---------|------|--------|--------|
| v0.9 | 2026-03-23 | Platform team | Initial generation (API-First, 12-doc sequence) |
| v1.0 | 2026-03-24 | Platform team | Rewritten for Full-Stack-First approach (14+2 docs); added INTERACTION-MAP as key coordination doc; added parallel MCP+Design sprint; added AGENT-HANDOFF-PROTOCOL and AGENT-INTERACTION-DIAGRAM; expanded timeline to 20 weeks |
