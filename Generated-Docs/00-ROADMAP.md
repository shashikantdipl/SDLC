# ROADMAP.md — Agentic SDLC Platform

**Document:** 0 of 12 (API-First Build Sequence)
**Version:** 1.0.0
**Date:** 2026-03-23
**Status:** ACTIVE
**Owner:** Platform Team (2-3 developers)
**Repository:** `agentic-sdlc` (main branch, ~800 files, v0.1.0)

---

## 1. Current State

### 1.1 What Exists Today

The Agentic SDLC Platform is a production-grade AI agent control plane built on top of the Claude Agent SDK. 48 agents across 7 SDLC phases automate the full software delivery lifecycle. The platform is functional at the individual-agent and single-team level but lacks the infrastructure for multi-agent pipelines and persistent state.

**Verified operational (real API calls, 2026-03-21):**

| Test | Result | Cost |
|------|--------|------|
| G1-cost-tracker single invocation | PASS | $0.006 |
| B1-code-reviewer single invocation | PASS | $0.134 |
| T3-coverage-gate single invocation | PASS | $0.005 |
| OV-D5-governance-gap-auditor single invocation | PASS | $0.832 |
| compliance-audit team (G1+G2+B7+OV-D5) | PASS | $0.920 ($3.00 ceiling respected) |
| All 48 agents dry-run | PASS | $0.00 |
| All 48 manifests schema validation | PASS | $0.00 |
| **Total real API spend to date** | | **$1.30** |

**Implemented SDK modules (6 of 19):**

| Module | File Path | Status |
|--------|-----------|--------|
| BaseAgent / BaseStatefulAgent | `sdk/base_agent.py` | Complete |
| BaseHooks (D08 audit, cost tracking, PII) | `sdk/base_hooks.py` | Complete |
| ManifestLoader (4-layer resolution) | `sdk/manifest_loader.py` | Complete |
| SchemaValidator (JSON Schema 2020-12) | `sdk/schema_validator.py` | Complete |
| Agent manifest schema | `schema/agent-manifest.schema.json` (571 lines) | Complete |
| Output contract schemas | `schema/output-contracts/` (20 schemas) | Complete |

**Other completed artifacts:**

- 7 archetype YAMLs (one per SDLC phase)
- 9 team workflow YAMLs
- SQL migrations 001-004
- 48 agent manifest.yaml files (all pass schema validation)
- 48 agent prompt.md files (many are stubs — see Risk R-04)

### 1.2 What Does Not Exist

**13 SDK modules not yet built:**

| Priority | Module | File Path | Blocks |
|----------|--------|-----------|--------|
| P1-BLOCKING | SessionStore | `sdk/context/session_store.py` | Entire 12-doc pipeline |
| P1-BLOCKING | PostgresCostStore | `sdk/stores/postgres_cost_store.py` | Real budget enforcement |
| P2 | ApprovalStore | `sdk/stores/approval_store.py` | Approval gates |
| P2 | PipelineCheckpoint | `sdk/orchestration/pipeline_checkpoint.py` | Pipeline resume |
| P2 | TokenBucketRateLimiter | `sdk/rate_limiter.py` | Parallel API safety |
| P3 | PipelineRunner | `sdk/orchestration/pipeline_runner.py` | Multi-agent pipelines |
| P3 | TeamOrchestrator | `sdk/orchestration/team_orchestrator.py` | Team workflows |
| P4 | WebhookNotifier | `sdk/notifications/webhook_notifier.py` | External alerts |
| P4 | QualityScorer | `sdk/scoring/quality_scorer.py` | Quality gates |
| P4 | ExceptionPromotionEngine | `sdk/exceptions/promotion_engine.py` | Exception lifecycle |
| P4 | SelfHealPolicy | `sdk/resilience/self_heal_policy.py` | Auto-recovery |
| P4 | HealthServer | `sdk/health/health_server.py` | Liveness/readiness |
| P5 | OtelInstrumentation | `sdk/observability/otel_instrumentation.py` | Distributed tracing |

**9 missing agents:**

| ID | Phase | Folder |
|----|-------|--------|
| G5-audit-reporter | GOVERN | `agents/govern/G5-audit-reporter/` |
| T1-static-analyser | TEST | `agents/claude-cc/T1-static-analyser/` |
| P4-rollback-manager | DEPLOY | `agents/claude-cc/P4-rollback-manager/` |
| P5-feature-flag-manager | DEPLOY | `agents/claude-cc/P5-feature-flag-manager/` |
| O5-alert-manager | OPERATE | `agents/claude-cc/O5-alert-manager/` |
| B9-migration-writer | BUILD | `agents/claude-cc/B9-migration-writer/` |
| D12-localisation-planner | DESIGN | `agents/claude-cc/D12-localisation-planner/` |
| OV-P1-performance-auditor | OVERSIGHT | `agents/claude-cc/OV-P1-performance-auditor/` |
| OV-D1-dependency-auditor | OVERSIGHT | `agents/claude-cc/OV-D1-dependency-auditor/` |

**5 missing team pipelines:**

| Pipeline | File Path |
|----------|-----------|
| bug-fix | `workflows/teams/bug-fix.yaml` |
| hotfix | `workflows/teams/hotfix.yaml` |
| security-patch | `workflows/teams/security-patch.yaml` |
| compliance-review | `workflows/teams/compliance-review.yaml` |
| performance-optimization | `workflows/teams/performance-optimization.yaml` |

**4 missing SQL migrations:**

| Migration | Purpose | Blocks |
|-----------|---------|--------|
| 005 | `knowledge_exceptions` table | Exception promotion |
| 006 | `session_context` table | BLOCKING — SessionStore |
| 007 | `approval_requests` table | Approval gates |
| 008 | `pipeline_checkpoints` table | Pipeline resume |

### 1.3 Budget Constraints

| Scope | Default Ceiling |
|-------|----------------|
| Fleet | $50/day |
| Project | $20/day |
| Agent | $5/day |
| Invocation | $0.50 |

Current BudgetCascade uses stub data and fails open. This is a production risk (see R-02).

---

## 2. Document Build Sequence

The platform's documentation follows the API-First 12-document build sequence. Each document is generated by Claude Code using the preceding documents as input. **This roadmap (Doc 0) is the first.**

| Step | Doc # | Document | Input Dependencies | Status | File Path |
|------|-------|----------|-------------------|--------|-----------|
| 1 | **0** | ROADMAP.md | Raw spec (MASTER-BUILD-SPEC.md) | **In Progress** | `Generated-Docs/00-ROADMAP.md` |
| 2 | **1** | PRD.md | Raw spec | Not Started | `Generated-Docs/01-PRD.md` |
| 3 | **2** | ARCH.md | PRD | Not Started | `Generated-Docs/02-ARCH.md` |
| 4 | **3** | CLAUDE.md | ROADMAP + ARCH | Not Started | `Generated-Docs/03-CLAUDE.md` |
| 5 | **4** | QUALITY.md | PRD + ARCH | Not Started | `Generated-Docs/04-QUALITY.md` |
| 6 | **5** | FEATURE-CATALOG.md | PRD + ARCH | Not Started | `Generated-Docs/05-FEATURE-CATALOG.md` |
| 7 | **6** | CLAUDE-ENFORCEMENT.md | CLAUDE + ARCH | Not Started | `Generated-Docs/06-CLAUDE-ENFORCEMENT.md` |
| 8 | **7** | DATA-MODEL.md | ARCH + FEATURE-CATALOG + QUALITY | Not Started | `Generated-Docs/07-DATA-MODEL.md` |
| 9 | **8** | BACKLOG.md | FEATURE-CATALOG + PRD + ARCH + QUALITY | Not Started | `Generated-Docs/08-BACKLOG.md` |
| 10 | **9** | API-CONTRACTS.md | ARCH + DATA-MODEL + PRD | Not Started | `Generated-Docs/09-API-CONTRACTS.md` |
| 11 | **10** | DESIGN-SPEC.md | PRD + API-CONTRACTS + QUALITY | Not Started | `Generated-Docs/10-DESIGN-SPEC.md` |
| 12 | **11** | TESTING.md | ARCH + QUALITY + DATA-MODEL + CLAUDE | Not Started | `Generated-Docs/11-TESTING.md` |

**Critical dependency:** Doc 0 (ROADMAP) is consumed by Doc 3 (CLAUDE). Docs 1 (PRD) and 2 (ARCH) feed into most downstream documents. Any delay in Docs 0-2 cascades to the entire pipeline.

---

## 3. Delivery Phases

### Phase 0 — Foundation Unblock (Weeks 1-2)

**Goal:** Remove the two P1-BLOCKING dependencies so pipelines can run.

**Entry criteria:**
- MASTER-BUILD-SPEC.md finalized (done)
- All 48 manifests pass schema validation (done)
- PostgreSQL instance available for development

**Exit criteria:**
- `sdk/context/session_store.py` passes 8+ unit tests covering CRUD, TTL expiry, and concurrent access
- `sdk/stores/postgres_cost_store.py` passes 6+ unit tests covering insert, aggregate, budget-check, and fail-closed behavior
- Migration 006 (`session_context`) applied and tested against local PostgreSQL
- Migration 005 (`knowledge_exceptions`) applied
- BudgetCascade switched from stub data to PostgresCostStore with fail-closed semantics
- G1-cost-tracker re-verified with real store (PASS, cost < $0.05)

**Deliverables:**

| Deliverable | File Path | Tests |
|-------------|-----------|-------|
| SessionStore | `sdk/context/session_store.py` | `tests/test_session_store.py` (8 tests) |
| PostgresCostStore | `sdk/stores/postgres_cost_store.py` | `tests/test_postgres_cost_store.py` (6 tests) |
| Migration 005 | `migrations/005_knowledge_exceptions.sql` | Manual apply + verify |
| Migration 006 | `migrations/006_session_context.sql` | Manual apply + verify |
| Updated BudgetCascade | `sdk/budget_cascade.py` (modify existing) | `tests/test_budget_cascade.py` (3 new tests for fail-closed) |

**Dependencies:** None (this is the root).
**Owner:** Developer 1
**Risk buffer:** 2 days

---

### Phase 1 — 12-Document Pipeline Generation (Weeks 2-4)

**Goal:** Generate all 12 SDLC documents in dependency order using Claude Code.

**Entry criteria:**
- Phase 0 complete (SessionStore operational)
- ROADMAP.md (this document) reviewed and approved

**Exit criteria:**
- All 12 documents exist at `Generated-Docs/00-ROADMAP.md` through `Generated-Docs/11-TESTING.md`
- Each document passes internal cross-reference check (no broken doc references)
- BACKLOG.md contains S-NNN stories covering all 10 FIX items and 9 missing agents
- TESTING.md covers all 13 SDK modules

**Deliverables:**

| Deliverable | File Path | Acceptance |
|-------------|-----------|------------|
| ROADMAP.md | `Generated-Docs/00-ROADMAP.md` | This document, reviewed |
| PRD.md | `Generated-Docs/01-PRD.md` | Personas defined, C1-C7 capabilities listed |
| ARCH.md | `Generated-Docs/02-ARCH.md` | All 5 orchestration levels documented |
| CLAUDE.md | `Generated-Docs/03-CLAUDE.md` | Repo structure rules, forbidden patterns |
| QUALITY.md | `Generated-Docs/04-QUALITY.md` | Q-NNN NFRs with measurable thresholds |
| FEATURE-CATALOG.md | `Generated-Docs/05-FEATURE-CATALOG.md` | F-NNN features with dependency graph |
| CLAUDE-ENFORCEMENT.md | `Generated-Docs/06-CLAUDE-ENFORCEMENT.md` | `.claude/` rules generated |
| DATA-MODEL.md | `Generated-Docs/07-DATA-MODEL.md` | All tables including migrations 005-008 |
| BACKLOG.md | `Generated-Docs/08-BACKLOG.md` | S-NNN stories, prioritized |
| API-CONTRACTS.md | `Generated-Docs/09-API-CONTRACTS.md` | All endpoints with request/response schemas |
| DESIGN-SPEC.md | `Generated-Docs/10-DESIGN-SPEC.md` | Streamlit dashboard screens specified |
| TESTING.md | `Generated-Docs/11-TESTING.md` | Test strategy for all 19 SDK modules |

**Dependencies:** Phase 0 (SessionStore needed for pipeline context persistence).
**Owner:** Developer 1 (docs 0-6), Developer 2 (docs 7-11)
**Risk buffer:** 3 days

---

### Phase 2 — P2 SDK Modules + Migrations (Weeks 4-6)

**Goal:** Build the safety infrastructure: approvals, checkpoints, rate limiting.

**Entry criteria:**
- Phase 0 complete (SessionStore and PostgresCostStore operational)
- Migrations 005-006 applied
- DATA-MODEL.md (Doc 7) reviewed (provides schema definitions)

**Exit criteria:**
- ApprovalStore passes 6 tests (create, approve, reject, timeout, query, audit-trail)
- PipelineCheckpoint passes 5 tests (save, load, resume, expire, list)
- TokenBucketRateLimiter passes 5 tests (acquire, exhaust, refill, concurrent, burst)
- Migrations 007 and 008 applied and tested
- Rate limiter integrated into BaseAgent (all 48 agents inherit it)

**Deliverables:**

| Deliverable | File Path | Tests |
|-------------|-----------|-------|
| ApprovalStore | `sdk/stores/approval_store.py` | `tests/test_approval_store.py` (6 tests) |
| PipelineCheckpoint | `sdk/orchestration/pipeline_checkpoint.py` | `tests/test_pipeline_checkpoint.py` (5 tests) |
| TokenBucketRateLimiter | `sdk/rate_limiter.py` | `tests/test_rate_limiter.py` (5 tests) |
| Migration 007 | `migrations/007_approval_requests.sql` | Apply + verify |
| Migration 008 | `migrations/008_pipeline_checkpoints.sql` | Apply + verify |
| BaseAgent rate-limiter integration | `sdk/base_agent.py` (modify) | `tests/test_base_agent.py` (2 new tests) |

**Dependencies:** Phase 0.
**Owner:** Developer 2
**Risk buffer:** 2 days

---

### Phase 3 — Pipeline & Team Orchestration (Weeks 5-7)

**Goal:** Build PipelineRunner and TeamOrchestrator so multi-agent workflows execute end-to-end.

**Entry criteria:**
- Phase 2 complete (checkpoints and approvals operational)
- At least 5 team workflow YAMLs validated against schema
- API-CONTRACTS.md (Doc 9) reviewed

**Exit criteria:**
- PipelineRunner executes a 3-agent sequential pipeline with checkpoint/resume (test)
- PipelineRunner executes a parallel DAG of 3 agents with fan-out/fan-in (FIX-06)
- TeamOrchestrator runs `compliance-audit` team workflow end-to-end with real API calls (cost < $3.00)
- Agent versioning (FIX-05) implemented: `manifest.yaml` version field enforced, version mismatch raises error

**Deliverables:**

| Deliverable | File Path | Tests |
|-------------|-----------|-------|
| PipelineRunner | `sdk/orchestration/pipeline_runner.py` | `tests/test_pipeline_runner.py` (8 tests) |
| TeamOrchestrator | `sdk/orchestration/team_orchestrator.py` | `tests/test_team_orchestrator.py` (6 tests) |
| Parallel DAG executor | `sdk/orchestration/dag_executor.py` | `tests/test_dag_executor.py` (4 tests) |
| Agent version enforcement | `sdk/manifest_loader.py` (modify) | `tests/test_manifest_loader.py` (2 new tests) |
| Input/output validation (FIX-08) | `sdk/base_agent.py` (modify) | `tests/test_base_agent.py` (3 new tests) |

**Dependencies:** Phase 2 (needs checkpoints and approvals).
**Owner:** Developer 1
**Risk buffer:** 3 days

---

### Phase 4 — Missing Agents (Weeks 6-8)

**Goal:** Build all 9 missing agents. Each agent = manifest.yaml + prompt.md + agent.py + test.

**Entry criteria:**
- Phase 0 complete (SessionStore operational)
- FEATURE-CATALOG.md (Doc 5) reviewed (defines F-NNN features per agent)
- BACKLOG.md (Doc 8) reviewed (defines S-NNN stories per agent)

**Exit criteria:**
- All 9 agents pass dry-run
- All 9 agents pass schema validation
- All 9 agents pass `python -m pytest tests/test_<agent_id>.py -v`
- Total agent count: 57 (48 existing + 9 new), all manifests valid
- prompt.md for each new agent is fully implemented (no stubs)

**Deliverables:**

| Agent | Files | Tests |
|-------|-------|-------|
| G5-audit-reporter | `agents/govern/G5-audit-reporter/{manifest.yaml,prompt.md,agent.py}` | `tests/test_g5_audit_reporter.py` |
| T1-static-analyser | `agents/claude-cc/T1-static-analyser/{manifest.yaml,prompt.md,agent.py}` | `tests/test_t1_static_analyser.py` |
| P4-rollback-manager | `agents/claude-cc/P4-rollback-manager/{manifest.yaml,prompt.md,agent.py}` | `tests/test_p4_rollback_manager.py` |
| P5-feature-flag-manager | `agents/claude-cc/P5-feature-flag-manager/{manifest.yaml,prompt.md,agent.py}` | `tests/test_p5_feature_flag_manager.py` |
| O5-alert-manager | `agents/claude-cc/O5-alert-manager/{manifest.yaml,prompt.md,agent.py}` | `tests/test_o5_alert_manager.py` |
| B9-migration-writer | `agents/claude-cc/B9-migration-writer/{manifest.yaml,prompt.md,agent.py}` | `tests/test_b9_migration_writer.py` |
| D12-localisation-planner | `agents/claude-cc/D12-localisation-planner/{manifest.yaml,prompt.md,agent.py}` | `tests/test_d12_localisation_planner.py` |
| OV-P1-performance-auditor | `agents/claude-cc/OV-P1-performance-auditor/{manifest.yaml,prompt.md,agent.py}` | `tests/test_ov_p1_performance_auditor.py` |
| OV-D1-dependency-auditor | `agents/claude-cc/OV-D1-dependency-auditor/{manifest.yaml,prompt.md,agent.py}` | `tests/test_ov_d1_dependency_auditor.py` |

**Dependencies:** Phase 0. Can run in parallel with Phase 2 and Phase 3.
**Owner:** Developer 2 (GOVERN, TEST, DEPLOY agents), Developer 1 (BUILD, DESIGN, OPERATE, OVERSIGHT agents)
**Risk buffer:** 3 days

---

### Phase 5 — Missing Team Pipelines + Prompt Completion (Weeks 7-9)

**Goal:** Build 5 missing team pipelines. Complete all stub prompt.md files across existing 48 agents.

**Entry criteria:**
- Phase 3 complete (PipelineRunner and TeamOrchestrator operational)
- Phase 4 complete (all 57 agents available)

**Exit criteria:**
- All 5 new team pipelines execute dry-run successfully
- At least 2 team pipelines execute with real API calls (cost < $5.00 each)
- Zero stub prompt.md files remain in the repository (FIX-10)
- All 14 team workflows (9 existing + 5 new) pass schema validation

**Deliverables:**

| Pipeline | File Path | Agents Involved |
|----------|-----------|----------------|
| bug-fix | `workflows/teams/bug-fix.yaml` | B1, B2, T2, T3 |
| hotfix | `workflows/teams/hotfix.yaml` | B1, P3, P4, T3 |
| security-patch | `workflows/teams/security-patch.yaml` | B7, B1, T2, P3 |
| compliance-review | `workflows/teams/compliance-review.yaml` | G2, G5, OV-D5, B7 |
| performance-optimization | `workflows/teams/performance-optimization.yaml` | OV-P1, B1, T3, P3 |
| Completed prompt.md files | `agents/**/prompt.md` (all 57) | N/A |

**Dependencies:** Phase 3, Phase 4.
**Owner:** Developer 1 (pipelines), Developer 2 (prompt completion)
**Risk buffer:** 2 days

---

### Phase 6 — P4 SDK Modules: Resilience & Observability (Weeks 8-10)

**Goal:** Build the operational infrastructure: notifications, scoring, self-healing, health checks.

**Entry criteria:**
- Phase 3 complete (PipelineRunner operational)
- QUALITY.md (Doc 4) reviewed (defines Q-NNN thresholds for scoring)

**Exit criteria:**
- WebhookNotifier sends test payload to a mock endpoint (test)
- QualityScorer scores a sample agent output against 3 Q-NNN criteria (test)
- ExceptionPromotionEngine promotes an exception through the full lifecycle (test)
- SelfHealPolicy retries a failed agent invocation with backoff (test)
- HealthServer responds to `/healthz` and `/readyz` (test)
- Streamlit dashboard (`dashboard/app.py`) displays cost, health, and pipeline status (FIX-07)

**Deliverables:**

| Deliverable | File Path | Tests |
|-------------|-----------|-------|
| WebhookNotifier | `sdk/notifications/webhook_notifier.py` | `tests/test_webhook_notifier.py` (3 tests) |
| QualityScorer | `sdk/scoring/quality_scorer.py` | `tests/test_quality_scorer.py` (4 tests) |
| ExceptionPromotionEngine | `sdk/exceptions/promotion_engine.py` | `tests/test_promotion_engine.py` (4 tests) |
| SelfHealPolicy | `sdk/resilience/self_heal_policy.py` | `tests/test_self_heal_policy.py` (4 tests) |
| HealthServer | `sdk/health/health_server.py` | `tests/test_health_server.py` (3 tests) |
| Observability dashboard | `dashboard/app.py` | Manual verification |

**Dependencies:** Phase 3.
**Owner:** Developer 2
**Risk buffer:** 2 days

---

### Phase 7 — Integration Testing & P5 Observability (Weeks 10-12)

**Goal:** Full end-to-end integration tests. OTel instrumentation. Production readiness.

**Entry criteria:**
- All prior phases complete
- All 57 agents pass dry-run
- All 14 team workflows pass schema validation
- All 19 SDK modules pass unit tests

**Exit criteria:**
- OtelInstrumentation emits spans for agent invocations, pipeline steps, and team workflows (test)
- End-to-end test: `compliance-audit` team runs against live codebase, produces report, cost < $3.00
- End-to-end test: `bug-fix` pipeline runs with mocked bug input, produces fix PR, cost < $5.00
- End-to-end test: 5 agents run in parallel DAG, respecting rate limits and budget ceilings
- All 10 FIX items verified closed
- `state/MANIFEST.md` fully up to date
- TESTING.md (Doc 11) acceptance criteria all pass

**Deliverables:**

| Deliverable | File Path | Tests |
|-------------|-----------|-------|
| OtelInstrumentation | `sdk/observability/otel_instrumentation.py` | `tests/test_otel_instrumentation.py` (5 tests) |
| E2E: compliance-audit | `tests/e2e/test_compliance_audit_team.py` | 1 test |
| E2E: bug-fix pipeline | `tests/e2e/test_bug_fix_pipeline.py` | 1 test |
| E2E: parallel DAG | `tests/e2e/test_parallel_dag.py` | 1 test |
| E2E: budget enforcement | `tests/e2e/test_budget_enforcement.py` | 1 test |
| Updated MANIFEST.md | `state/MANIFEST.md` | Cross-reference check |

**Dependencies:** All previous phases.
**Owner:** Both developers
**Risk buffer:** 3 days

---

## 4. Milestones

| ID | Milestone | Target Week | Owner | Definition of Done |
|----|-----------|-------------|-------|-------------------|
| M-01 | SessionStore unblocked | Week 2 | Dev 1 | `sdk/context/session_store.py` passes 8 unit tests, migration 006 applied |
| M-02 | Real cost enforcement | Week 2 | Dev 1 | PostgresCostStore operational, BudgetCascade fail-closed, G1 re-verified |
| M-03 | 12-document pipeline complete | Week 4 | Dev 1 + Dev 2 | All 12 docs exist at `Generated-Docs/`, cross-references valid |
| M-04 | Safety infrastructure | Week 6 | Dev 2 | ApprovalStore + PipelineCheckpoint + RateLimiter all pass tests |
| M-05 | Multi-agent orchestration | Week 7 | Dev 1 | PipelineRunner executes sequential + parallel DAG; TeamOrchestrator runs compliance-audit |
| M-06 | 57-agent fleet | Week 8 | Both | All 57 agents dry-run PASS, schema-valid, tested |
| M-07 | All team pipelines | Week 9 | Dev 1 | 14 team workflows validated, 2 tested with real API calls |
| M-08 | Zero stub prompts | Week 9 | Dev 2 | `grep -r "TODO" agents/**/prompt.md` returns 0 results |
| M-09 | Operational readiness | Week 10 | Dev 2 | Dashboard, health checks, webhook notifications, self-healing all operational |
| M-10 | All FIX items closed | Week 11 | Both | FIX-01 through FIX-10 verified with specific test for each |
| M-11 | E2E integration pass | Week 12 | Both | 4 E2E tests pass, total cost < $15.00, no budget ceiling violations |
| M-12 | v0.2.0 release | Week 12 | Both | Tag `v0.2.0`, CHANGELOG.md updated, all 19 SDK modules operational |

---

## 5. Open Decisions

| ID | Question | Options | Who Decides | Blocks |
|----|----------|---------|-------------|--------|
| OD-01 | PostgreSQL hosting for production | (A) Self-hosted on VM, (B) Managed service (e.g., Neon, Supabase, RDS), (C) SQLite for dev + Postgres for prod | Platform Lead | Phase 0 — SessionStore needs a connection string |
| OD-02 | Rate limiting strategy for parallel agents | (A) Global token bucket shared across all agents, (B) Per-agent token buckets, (C) Per-phase token buckets | Platform Lead | Phase 2 — TokenBucketRateLimiter design |
| OD-03 | Approval gate UX | (A) CLI prompt, (B) Streamlit modal, (C) Slack webhook with button, (D) All three | Platform Lead + Dev Team | Phase 2 — ApprovalStore notification mechanism |
| OD-04 | OTel backend for traces | (A) Jaeger (self-hosted), (B) Grafana Tempo, (C) Console exporter only for v0.2.0 | Platform Lead | Phase 7 — OtelInstrumentation exporter config |
| OD-05 | Dashboard auth | (A) No auth (dev only), (B) Basic auth, (C) OAuth via provider | Platform Lead | Phase 6 — HealthServer and dashboard deployment |
| OD-06 | Parallel DAG execution model | (A) asyncio.gather with semaphore, (B) Task queue (e.g., Celery), (C) Custom DAG scheduler | Dev 1 | Phase 3 — dag_executor.py design |
| OD-07 | Exception promotion thresholds | (A) Fixed counts (3 occurrences = promote), (B) Configurable per-agent, (C) ML-based anomaly detection | Dev 2 | Phase 6 — ExceptionPromotionEngine policy |
| OD-08 | Missing agent model selection | (A) All new agents use claude-haiku-4-5 (cheapest), (B) Match archetype defaults, (C) Let each agent's manifest define it | Dev Team | Phase 4 — manifest.yaml for 9 new agents |

---

## 6. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-01 | SessionStore implementation takes longer than 2 weeks, blocking entire pipeline | Medium | **Critical** | Start Phase 0 immediately. Fallback: in-memory dict with file-backed persistence as temporary shim. |
| R-02 | BudgetCascade fail-open allows runaway API costs | High | **High** | FIX-04 is P1-BLOCKING. Until PostgresCostStore is live, enforce a hard $5/session kill switch in BaseHooks. |
| R-03 | Parallel agent API calls hit Anthropic rate limits | Medium | **High** | TokenBucketRateLimiter (Phase 2) is the fix. Interim: limit concurrency to 2 agents via asyncio.Semaphore in BaseAgent. |
| R-04 | Many prompt.md files are stubs; agents produce low-quality output | **High** | Medium | Phase 5 addresses this (FIX-10). Until then, prioritize prompts for agents used in team workflows (G1, G2, B1, B7, T3, OV-D5). |
| R-05 | 12-document generation pipeline produces inconsistent cross-references | Medium | Medium | Each document generation step must validate references to prior documents. Build a `scripts/validate_doc_refs.py` script in Phase 1. |
| R-06 | Team of 2-3 developers is insufficient for 12-week timeline | Medium | **High** | Phases 2-4 are designed for parallel execution by 2 developers. If team shrinks to 1, cut Phase 6 P4 modules to post-v0.2.0. |
| R-07 | PostgreSQL schema migrations conflict or fail on apply | Low | Medium | Test all migrations against a clean database in CI. Maintain `migrations/rollback/` scripts for each migration. |
| R-08 | Claude Agent SDK breaking changes in upstream releases | Low | **High** | Pin SDK version in `pyproject.toml`. Monitor SDK changelog. Keep a `sdk/compat.py` shim layer for version-specific behavior. |
| R-09 | E2E tests are flaky due to LLM nondeterminism | **High** | Medium | Use `temperature: 0.0` for test invocations. Assert on output schema compliance, not exact string matches. Allow 3 retries in E2E test harness. |
| R-10 | Total API cost for testing exceeds budget during development | Medium | Medium | Track cumulative cost in `state/cost_ledger.json`. Set a hard development budget of $50 total for all E2E testing. Use dry-run mode for all non-E2E tests. |

---

## 7. Timeline Visualization

```
Week    1    2    3    4    5    6    7    8    9   10   11   12
        |    |    |    |    |    |    |    |    |    |    |    |
Phase 0 [====|====]                                             SessionStore + CostStore
        M-01 M-02
             |
Phase 1      [====|====|====]                                   12-Document Pipeline
                       M-03
                  |
Phase 2           [====|====|====]                              Approvals + Checkpoints + RateLimiter
                            M-04
                  |
Phase 4           [====|====|====|====]                         9 Missing Agents (parallel with P2/P3)
                                 M-06
                       |
Phase 3                [====|====|====]                         PipelineRunner + TeamOrchestrator
                                 M-05
                                 |
Phase 5                          [====|====|====]               Team Pipelines + Prompt Completion
                                      M-07 M-08
                            |
Phase 6                     [====|====|====|====]               Resilience + Observability
                                           M-09
                                           |
Phase 7                                    [====|====|====]     Integration + OTel + Release
                                                 M-10 M-11
                                                       M-12
                                                        |
                                                     v0.2.0

LEGEND:
[====] = 1 week of work
M-XX   = Milestone (see Section 4)
|      = Dependency arrow (phase below depends on phase above)

PARALLEL TRACKS:
  Track A (Dev 1): Phase 0 -> Phase 1 (docs 0-6) -> Phase 3 -> Phase 5 (pipelines) -> Phase 7
  Track B (Dev 2): Phase 1 (docs 7-11) -> Phase 2 -> Phase 4 -> Phase 5 (prompts) -> Phase 6 -> Phase 7

CRITICAL PATH: Phase 0 -> Phase 2 -> Phase 3 -> Phase 5 -> Phase 7
  Any delay on this path delays v0.2.0.
```

---

## 8. FIX Item Traceability

Every FIX item from the MASTER-BUILD-SPEC maps to a specific phase and deliverable:

| FIX ID | Description | Phase | Deliverable | Verification |
|--------|-------------|-------|-------------|--------------|
| FIX-01 | SessionStore (BLOCKING) | Phase 0 | `sdk/context/session_store.py` | 8 unit tests pass |
| FIX-02 | Approval gates | Phase 2 | `sdk/stores/approval_store.py` | 6 unit tests pass |
| FIX-03 | Pipeline checkpoint | Phase 2 | `sdk/orchestration/pipeline_checkpoint.py` | 5 unit tests pass |
| FIX-04 | Real cost store | Phase 0 | `sdk/stores/postgres_cost_store.py` | 6 unit tests pass, BudgetCascade fail-closed |
| FIX-05 | Agent versioning | Phase 3 | `sdk/manifest_loader.py` (modify) | 2 unit tests pass |
| FIX-06 | Parallel DAG | Phase 3 | `sdk/orchestration/dag_executor.py` | 4 unit tests pass |
| FIX-07 | Observability dashboard | Phase 6 | `dashboard/app.py` | Manual: cost + health + pipeline views |
| FIX-08 | Input/output validation | Phase 3 | `sdk/base_agent.py` (modify) | 3 unit tests pass |
| FIX-09 | Rate limiter | Phase 2 | `sdk/rate_limiter.py` | 5 unit tests pass |
| FIX-10 | Complete all prompts | Phase 5 | `agents/**/prompt.md` (all 57) | Zero stubs remain |

---

## 9. Success Criteria for v0.2.0

The release is ready when ALL of these are true:

1. **57 agents** — all dry-run PASS, all schema-valid, all tested
2. **19 SDK modules** — all pass unit tests (total: ~95 tests)
3. **14 team workflows** — all schema-valid, 2+ tested with real API calls
4. **4 E2E tests** — all pass, total cost < $15.00
5. **12 documents** — all generated, cross-references valid
6. **10 FIX items** — all verified closed per traceability table above
7. **8 migrations** — all applied, rollback scripts exist
8. **0 stub prompt.md files** — every agent has a production-grade prompt
9. **Budget enforcement** — fail-closed, tested under load (5 parallel agents)
10. **Dashboard** — Streamlit app shows cost, health, pipeline status in real time

---

*This document is the entry point for all downstream development. When in doubt, refer to `Requirement/MASTER-BUILD-SPEC.md` for architectural details and `Generated-Docs/08-BACKLOG.md` (once generated) for individual work items.*
