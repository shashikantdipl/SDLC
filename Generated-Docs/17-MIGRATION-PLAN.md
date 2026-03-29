# MIGRATION-PLAN — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-29
**Document:** 17 of 24 | Status: Draft
**Reads from:** ARCH (Doc 03), DATA-MODEL (Doc 10), API-CONTRACTS (Doc 11), ROADMAP (Doc 01)

---

## Table of Contents

1. [Migration Overview](#1-migration-overview)
2. [Source State Assessment](#2-source-state-assessment)
3. [Target State Definition](#3-target-state-definition)
4. [Phased Migration Approach](#4-phased-migration-approach)
5. [Data Migration](#5-data-migration)
6. [Validation Strategy](#6-validation-strategy)
7. [Cutover Runbook](#7-cutover-runbook)
8. [Rollback Plan](#8-rollback-plan)
9. [Team Training Plan](#9-team-training-plan)
10. [Risk Register](#10-risk-register)
11. [Success Criteria](#11-success-criteria)

---

## 1. Migration Overview

This is a **greenfield migration** — we are not replacing an existing platform. Instead, we are migrating teams from **manual, ad-hoc SDLC documentation processes** to the automated 48-agent pipeline. The migration is phased over 12 weeks to minimize disruption, validate quality, and build team confidence.

### Migration Scope

| Dimension | Source (Manual) | Target (Automated) |
|-----------|-----------------|---------------------|
| Spec authoring | Engineers write specs in Google Docs / Confluence / Notion | `trigger_pipeline` MCP tool or `POST /api/v1/pipelines` generates 24 docs from raw spec |
| Document storage | Scattered across wikis, drives, Slack threads | PostgreSQL (`session_context`, `pipeline_runs`, `pipeline_steps`) + filesystem (`reports/{project_id}/{run_id}/`) |
| Quality review | Manual peer review, inconsistent checklists | Automated quality gates (schema compliance, completeness, faithfulness, consistency scoring) |
| Cost tracking | No visibility into documentation effort | `cost_metrics` table, G1-cost-tracker agent, real-time Cost Monitor dashboard |
| Audit trail | Git blame + meeting notes | `audit_events` table (append-only), G2-audit-trail-validator agent |
| Approval workflow | Slack threads, email chains | `approval_requests` table, Approval Queue dashboard page, `list_pending_approvals` MCP tool |

### Guiding Principles

1. **Run in parallel** — never cut over cold. Old and new processes coexist during Phases 2-3.
2. **Quality parity first** — generated documents must meet or exceed manual document quality before any team switches.
3. **Per-project opt-in** — teams choose when to move each project; no forced migration.
4. **Rollback always available** — manual process remains functional throughout all phases.

---

## 2. Source State Assessment

### 2.1 Document Inventory

Before migration begins, run a source audit to catalog existing project documentation:

| Source Location | Document Types | Est. Volume | Import Complexity |
|----------------|----------------|-------------|-------------------|
| Confluence spaces | PRDs, architecture docs, API specs | 50-200 docs/team | Medium — export as Markdown via Confluence API |
| Google Docs | Requirements briefs, meeting notes, design docs | 100-500 docs/team | Medium — export via Google Drive API |
| Notion databases | Feature specs, sprint backlogs, decision logs | 30-100 pages/team | Low — native Markdown export |
| Slack channels | Decisions, approvals, context threads | N/A (unstructured) | High — manual extraction of key decisions |
| Git repositories | README files, ADRs, inline doc comments | 10-50 docs/repo | Low — already in Markdown |
| Figma / Miro | Design specs, architecture diagrams | 5-20 boards/team | High — manual conversion to text descriptions |

### 2.2 Source Quality Baseline

For each project entering migration, capture baseline metrics:

```
Source Quality Assessment:
  - document_count: <number of existing docs>
  - completeness_score: <% of standard sections present>
  - consistency_score: <% of cross-references that resolve>
  - freshness: <days since last meaningful update>
  - format_variance: <number of distinct templates used>
```

These baselines feed the validation step (Section 6) for quality comparison.

---

## 3. Target State Definition

### 3.1 Target Architecture

The target state is the full Agentic SDLC Platform as defined in ARCH (Doc 03):

- **48 agents** across 7 SDLC phases (GOVERN: G1-G5, DESIGN: D1-D13, BUILD: B1-B9, TEST: T1-T5, DEPLOY: P1-P5, plus PLAN and MONITOR agents)
- **3 MCP servers** (`agentic-sdlc-agents`, `agentic-sdlc-governance`, `agentic-sdlc-knowledge`)
- **REST API** at `localhost:8080/api/v1/`
- **Streamlit Dashboard** at `localhost:8501` (Fleet Health, Cost Monitor, Pipeline Runs, Audit Log, Approval Queue)
- **PostgreSQL 15+** with 10 tables: `agent_registry`, `cost_metrics`, `audit_events`, `pipeline_runs`, `pipeline_steps`, `knowledge_exceptions`, `session_context`, `approval_requests`, `pipeline_checkpoints`, `mcp_call_events`

### 3.2 Target Document Pipeline

Each project produces a 24-document stack via `trigger_pipeline`:

```
raw_spec (input) → G4-team-orchestrator → 24 documents:
  00-BRD → 01-ROADMAP → 02-PRD → 03-ARCH → 04-FEATURE-CATALOG
  → 05-QUALITY → 06-SECURITY-ARCH → 07-INTERACTION-MAP
  → 08-MCP-TOOL-SPEC (parallel) + 09-DESIGN-SPEC (parallel)
  → 10-DATA-MODEL → 11-API-CONTRACTS → 12-USER-STORIES → 13-BACKLOG
  → 14-CLAUDE → 15-ENFORCEMENT → 16-INFRA-DESIGN → 17-MIGRATION-PLAN
  → 18-TESTING → 19-FAULT-TOLERANCE → 20-GUARDRAILS-SPEC
  → 21-COMPLIANCE-MATRIX → 22-AGENT-HANDOFF-PROTOCOL
  → 23-AGENT-INTERACTION-DIAGRAM
```

Quality gates at each step. Cost tracked by G1-cost-tracker. Full audit trail in `audit_events`.

---

## 4. Phased Migration Approach

### Phase 1: Import and Catalog (Weeks 1-2)

**Goal:** Get existing documentation into the platform's `session_context` store without changing any team workflow.

| Step | Action | Owner | Tool/Endpoint | Validation |
|------|--------|-------|---------------|------------|
| 1.1 | Deploy platform in staging environment | DevOps (David) | Docker Compose + PostgreSQL | `GET /api/v1/system/health` returns `200` |
| 1.2 | Run source audit (Section 2.1) for 3 pilot projects | Tech Lead (Jason) | Manual inventory | Inventory spreadsheet complete |
| 1.3 | Export existing docs to Markdown | Engineering team | Confluence/Notion/GDocs export scripts | All docs in `imports/{project_id}/` directory |
| 1.4 | Import as raw_spec input | Platform Engineer (Priya) | `POST /api/v1/pipelines` with `dry_run: true` | `session_context` rows created, no pipeline execution |
| 1.5 | Baseline quality assessment | Quality team | Manual scoring using rubric from QUALITY (Doc 05) | Baseline scores recorded per project |
| 1.6 | Train 3 pilot users on MCP tools | Priya | Training session (see Section 9) | Users can call `trigger_pipeline` and `check_pipeline_status` |

**Exit Criteria:**
- 3 pilot projects imported into `session_context`
- Baseline quality scores recorded for all 3
- 3 users can invoke basic MCP tools
- Platform health checks passing in staging

### Phase 2: Parallel Generation (Weeks 3-4)

**Goal:** Generate documents using the automated pipeline **alongside** the manual process. Compare quality.

| Step | Action | Owner | Tool/Endpoint | Validation |
|------|--------|-------|---------------|------------|
| 2.1 | Trigger pipeline for pilot project 1 | Jason | `trigger_pipeline` MCP tool | `pipeline_runs` record created, status progresses |
| 2.2 | Generate first 6 docs (ROADMAP through INTERACTION-MAP) | G4-team-orchestrator | Automated pipeline | `pipeline_steps` show `completed` for steps 1-6 |
| 2.3 | Run quality comparison (generated vs manual) | Jason + Anika | Manual review + quality scores | Generated doc quality >= 80% of manual baseline |
| 2.4 | Collect feedback, tune agent prompts | Priya | Agent manifest + prompt updates | Feedback log in `audit_events` |
| 2.5 | Generate full 24-doc stack for all 3 pilots | G4-team-orchestrator | `trigger_pipeline` for each project | All 24 docs generated, cost < $25/run |
| 2.6 | Side-by-side review with stakeholders | Jason, Anika, Marcus | Dashboard Pipeline Runs page | Stakeholder sign-off on quality |

**Exit Criteria:**
- 24-doc stack generated for all 3 pilot projects
- Quality score of generated docs >= 85% of manual baseline on all dimensions
- Pipeline cost per run < $25 (verified in Cost Monitor)
- No P0 or P1 issues open from pilot runs
- Stakeholder approval from at least 2 of 3 pilot project owners

### Phase 3: New Projects Automated, In-Flight Manual (Weeks 5-8)

**Goal:** All **new** projects use the automated pipeline. Existing in-flight projects continue manually until natural completion.

| Step | Action | Owner | Tool/Endpoint | Validation |
|------|--------|-------|---------------|------------|
| 3.1 | Deploy platform to production | David | Production deployment runbook | `GET /api/v1/system/health` returns `200` in prod |
| 3.2 | Onboard all teams (training, Section 9) | Priya + Jason | Training sessions + documentation | All team members trained |
| 3.3 | New project intake process updated | Marcus | Process documentation | New projects routed to `trigger_pipeline` |
| 3.4 | Monitor cost and quality dashboards | David + Priya | Cost Monitor + Fleet Health pages | Cost within budget, no quality degradation |
| 3.5 | Weekly migration review meetings | Jason | Status review | Issues tracked, blockers resolved |
| 3.6 | In-flight projects: optional re-generation | Project leads | `trigger_pipeline` with existing specs as input | Opt-in only, quality comparison |

**Exit Criteria:**
- All new projects using automated pipeline for 2+ weeks
- Cost Monitor showing stable cost trends
- Fleet Health showing all agents healthy
- No manual workarounds needed for any new project
- At least 50% of in-flight projects opted into re-generation

### Phase 4: Full Cutover (Weeks 9-12)

**Goal:** All projects on the automated pipeline. Manual process decommissioned as primary workflow.

| Step | Action | Owner | Tool/Endpoint | Validation |
|------|--------|-------|---------------|------------|
| 4.1 | Migrate remaining in-flight projects | Project leads | `trigger_pipeline` with existing specs | All active projects have pipeline runs |
| 4.2 | Archive manual process documentation | Jason | Confluence archive | Manual templates marked as "archived" |
| 4.3 | Set up ongoing monitoring | David | PagerDuty + Slack alerts | Alert routing configured for P0/P1 |
| 4.4 | Compliance audit of migrated data | Fatima | `GET /api/v1/audit/events` + manual review | All `audit_events` present, no data gaps |
| 4.5 | Final quality report | Jason + Priya | Quality comparison dashboard | Generated docs >= 90% quality vs manual baseline |
| 4.6 | Migration retrospective | All | Team meeting | Lessons learned documented |

**Exit Criteria:**
- 100% of active projects on automated pipeline
- Zero projects still using manual-only workflow
- Quality metrics stable for 2+ weeks
- Compliance audit passed
- Retrospective completed

---

## 5. Data Migration

### 5.1 Data Flow

```
Source Documents (Confluence/Notion/GDocs)
    |
    v
Export to Markdown (scripts/export_sources.py)
    |
    v
Normalize to raw_spec format (scripts/normalize_spec.py)
    |
    v
POST /api/v1/pipelines (dry_run: true)
    |
    v
session_context table (project_id, context_type: "imported_spec", context_data: JSONB)
    |
    v
trigger_pipeline (full run) → pipeline_runs + pipeline_steps + reports/
```

### 5.2 Data Mapping

| Source Field | Target Table | Target Column | Transform |
|-------------|-------------|---------------|-----------|
| Document title | `session_context` | `context_data.title` | Normalize to lowercase-hyphenated |
| Document body (Markdown) | `session_context` | `context_data.content` | Strip wiki-specific syntax |
| Author | `session_context` | `context_data.original_author` | Map to platform user ID |
| Last modified date | `session_context` | `context_data.source_modified_at` | ISO 8601 format |
| Source URL | `session_context` | `context_data.source_url` | Preserve original URL |
| Project identifier | `session_context` | `project_id` | Map to `proj-{slug}-{year}` format |
| Document type | `session_context` | `context_type` | Map to: `imported_prd`, `imported_arch`, `imported_design`, `imported_raw_spec` |

### 5.3 Migration Scripts

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `scripts/migration/export_confluence.py` | Export Confluence spaces to Markdown | Confluence space key + API token | `imports/{project_id}/confluence/*.md` |
| `scripts/migration/export_gdocs.py` | Export Google Docs folder to Markdown | Google Drive folder ID + service account | `imports/{project_id}/gdocs/*.md` |
| `scripts/migration/export_notion.py` | Export Notion database to Markdown | Notion database ID + API key | `imports/{project_id}/notion/*.md` |
| `scripts/migration/normalize_spec.py` | Normalize exported docs to raw_spec format | `imports/{project_id}/**/*.md` | `imports/{project_id}/raw_spec.md` |
| `scripts/migration/import_to_platform.py` | Load normalized spec into `session_context` | `imports/{project_id}/raw_spec.md` | `session_context` rows |
| `scripts/migration/validate_import.py` | Verify import completeness | `project_id` | Validation report |

### 5.4 Data Integrity Checks

Run after each import batch:

```sql
-- Verify all imported projects have session_context entries
SELECT project_id, COUNT(*) as context_count
FROM session_context
WHERE context_type LIKE 'imported_%'
GROUP BY project_id;

-- Verify no empty content
SELECT id, project_id, context_type
FROM session_context
WHERE context_data->>'content' IS NULL
   OR LENGTH(context_data->>'content') < 100;

-- Verify no duplicate imports
SELECT project_id, context_type, COUNT(*)
FROM session_context
WHERE context_type LIKE 'imported_%'
GROUP BY project_id, context_type
HAVING COUNT(*) > 1;
```

---

## 6. Validation Strategy

### 6.1 Quality Comparison Framework

For each pilot project, compare generated documents against manual documents across 5 dimensions:

| Dimension | Metric | Measurement Method | Minimum Threshold |
|-----------|--------|-------------------|-------------------|
| Schema compliance | % of required sections present | Automated schema check against doc template | >= 95% |
| Completeness | % of domain concepts covered | Manual spot-check: 20 key concepts per doc | >= 85% |
| Faithfulness | % of claims traceable to input spec | Manual audit: 30 random claims per doc | >= 90% |
| Consistency | % of cross-references that resolve | Automated link checker across 24-doc set | >= 95% |
| Readability | Flesch-Kincaid grade level | Automated readability scorer | Grade 10-14 (technical writing range) |

### 6.2 Validation Process

```
For each pilot project:
  1. Generate 24-doc stack via trigger_pipeline
  2. Retrieve generated docs from reports/{project_id}/{run_id}/
  3. Score each doc on 5 dimensions (automated + manual)
  4. Compare scores against manual baseline (from Section 2.2)
  5. Generate validation report:
     - Per-document scores
     - Per-dimension aggregate scores
     - Delta vs manual baseline
     - Specific examples of quality gaps
  6. If any dimension < threshold:
     - Log issue in audit_events (action: "migration.quality_gap")
     - Create backlog item for agent prompt tuning
     - Re-run pipeline after fix, re-validate
  7. If all dimensions >= threshold:
     - Mark project as "migration_validated" in session_context
     - Record validation in audit_events (action: "migration.validated")
```

### 6.3 Automated Validation Queries

```sql
-- Quality scores per pipeline run (from pipeline_steps)
SELECT
  pr.project_id,
  ps.step_name,
  ps.quality_score,
  ps.token_count,
  ps.cost_usd
FROM pipeline_runs pr
JOIN pipeline_steps ps ON pr.id = ps.run_id
WHERE pr.project_id IN ('proj-pilot-1', 'proj-pilot-2', 'proj-pilot-3')
ORDER BY pr.project_id, ps.step_order;

-- Cost per pilot run
SELECT
  project_id,
  SUM(cost_usd) as total_cost,
  COUNT(*) as step_count
FROM pipeline_runs pr
JOIN pipeline_steps ps ON pr.id = ps.run_id
WHERE pr.project_id LIKE 'proj-pilot-%'
GROUP BY project_id;
```

---

## 7. Cutover Runbook

### 7.1 Pre-Cutover Checklist (Day -7)

| # | Check | Command / Action | Expected Result |
|---|-------|-----------------|-----------------|
| 1 | Platform health | `GET /api/v1/system/health` | All components `healthy` |
| 2 | All agents registered | `GET /api/v1/agents` | 48 agents, all `status: active` |
| 3 | Database migrations applied | Check `schema_migrations` table | All migrations `applied` |
| 4 | Cost tracking operational | `get_cost_report` MCP tool | Returns valid report |
| 5 | Audit logging operational | `GET /api/v1/audit/events?limit=10` | Recent events present |
| 6 | Pilot validation passed | Migration validation report | All pilots >= threshold |
| 7 | Rollback tested | Execute rollback drill (Section 8) | Rollback completes in < 1 hour |
| 8 | Team training completed | Training attendance log | >= 90% team members trained |
| 9 | Monitoring configured | PagerDuty + Slack alerts | Test alert received |
| 10 | Backup verified | PostgreSQL backup + filesystem backup | Backup restoration tested |

### 7.2 Cutover Steps (Day 0)

**Time-boxed: 4-hour window (09:00-13:00 UTC)**

| Time | Step | Action | Duration | Rollback Point |
|------|------|--------|----------|----------------|
| 09:00 | C-1 | Announce migration window to all teams via Slack | 5 min | N/A |
| 09:05 | C-2 | Take final backup of `session_context` table | 10 min | Restore backup |
| 09:15 | C-3 | Run final import batch for any new source docs | 15 min | Skip (run later) |
| 09:30 | C-4 | Update team intake form to route to `trigger_pipeline` | 5 min | Revert form |
| 09:35 | C-5 | Verify first production pipeline run (test project) | 20 min | Rollback to manual |
| 09:55 | C-6 | Check Cost Monitor for cost anomalies | 5 min | Pause if anomaly |
| 10:00 | C-7 | Check Fleet Health — all 48 agents green | 5 min | Investigate, fallback to manual |
| 10:05 | C-8 | Open platform to all teams | 5 min | Restrict access |
| 10:10 | C-9 | Monitor first 3 real project pipeline runs | 60 min | Per-project rollback |
| 11:10 | C-10 | Validate outputs of first 3 runs (spot-check) | 30 min | Flag quality issues |
| 11:40 | C-11 | Review `audit_events` for anomalies | 10 min | Investigate |
| 11:50 | C-12 | Confirm Approval Queue workflow (test approval) | 10 min | Manual approvals |
| 12:00 | C-13 | Send "migration complete" announcement | 5 min | N/A |
| 12:05 | C-14 | Begin 48-hour hypercare period | Ongoing | Full team on standby |

### 7.3 Post-Cutover Monitoring (Days 1-7)

| Metric | Dashboard/Tool | Alert Threshold | Escalation |
|--------|---------------|----------------|------------|
| Pipeline success rate | Pipeline Runs page | < 90% | Page Jason + Priya |
| Average cost per run | Cost Monitor page | > $20 (80% of $25 ceiling) | Alert G1-cost-tracker logs |
| Agent health | Fleet Health page | Any agent `unhealthy` for > 5 min | Page David |
| Quality scores | `pipeline_steps.quality_score` | Any doc < 70% | Alert Jason |
| Error rate | `GET /api/v1/system/health` | > 5% error rate | Page David |
| Audit event volume | Audit Log page | < 50% of expected volume | Investigate logging |

---

## 8. Rollback Plan

### 8.1 Rollback Triggers

| Trigger | Threshold | Decision Maker |
|---------|-----------|----------------|
| Quality degradation | Generated doc quality < 70% on any dimension for 3+ consecutive runs | Jason (Tech Lead) |
| Cost overrun | Pipeline cost > $25 per run for 3+ consecutive runs | Marcus (Delivery Lead) |
| Platform instability | P0 incident unresolved > 2 hours | David (DevOps) |
| Data integrity issue | Missing or corrupted `audit_events` | Fatima (Compliance) |
| Team blockers | > 50% of team unable to complete workflow | Jason (Tech Lead) |

### 8.2 Rollback Procedure

**Estimated rollback time: 30-60 minutes**

| Step | Action | Duration |
|------|--------|----------|
| R-1 | Announce rollback to all teams via Slack | 2 min |
| R-2 | Revert intake form to manual workflow | 5 min |
| R-3 | Cancel any in-progress pipeline runs: `POST /api/v1/pipelines/{run_id}/cancel` for each | 5 min |
| R-4 | Export any generated documents from `reports/` that teams want to keep | 10 min |
| R-5 | Notify teams to resume manual process | 5 min |
| R-6 | Keep platform running in read-only mode for audit trail access | 5 min |
| R-7 | Create incident report with root cause analysis | 30 min |
| R-8 | Schedule re-migration after fixes applied | N/A |

### 8.3 Partial Rollback

Not all failures require full rollback. Per-project rollback is supported:

- **Single project rollback:** Re-route that project's documentation to manual process. Other projects continue on platform.
- **Single phase rollback:** If a specific SDLC phase (e.g., BUILD agents B1-B9) has issues, generate those documents manually while other phases remain automated.
- **Single provider rollback:** If one LLM provider (e.g., OpenAI) is degraded, switch to failover provider (Anthropic or Ollama) via `agent_registry.provider` update.

---

## 9. Team Training Plan

### 9.1 Training Schedule

| Session | Audience | Duration | Timing | Trainer |
|---------|----------|----------|--------|---------|
| T1: Platform Overview | All team members | 90 min | Phase 1, Week 1 | Priya |
| T2: MCP Tools for Power Users | Engineers (Anika, Jason) | 120 min | Phase 1, Week 2 | Priya |
| T3: Dashboard for Managers | Leads (Marcus, Jason) | 60 min | Phase 2, Week 3 | Priya |
| T4: DevOps and Monitoring | Operations (David) | 90 min | Phase 2, Week 4 | Priya + David |
| T5: Compliance and Audit | Compliance (Fatima) | 60 min | Phase 3, Week 5 | Priya + Fatima |
| T6: Advanced: Agent Tuning | Platform engineers | 120 min | Phase 3, Week 6 | Priya |

### 9.2 Training Content

**T1: Platform Overview**
- What the platform does: 48 agents, 7 phases, 24-doc pipeline
- Three interfaces: MCP tools, REST API, Streamlit Dashboard
- Live demo: trigger a pipeline, watch it run, view outputs
- Cost model: $25 ceiling, G1-cost-tracker, Cost Monitor dashboard

**T2: MCP Tools for Power Users**
- Setting up MCP client (Claude Code / Cursor)
- Key tools: `trigger_pipeline`, `check_pipeline_status`, `get_pipeline_outputs`, `get_document`
- Agent interaction: `list_agents`, `query_agent`, `invoke_agent`
- Governance: `get_cost_summary`, `get_audit_log`, `list_pending_approvals`, `approve_gate`
- Hands-on exercise: generate a 24-doc stack from a sample spec

**T3: Dashboard for Managers**
- Fleet Health page: agent status, health indicators
- Cost Monitor page: budget tracking, cost trends, anomaly detection
- Pipeline Runs page: run status, step progress, quality scores
- Approval Queue page: pending approvals, approve/reject workflow
- Audit Log page: event history, filtering, export

**T4: DevOps and Monitoring**
- System health endpoint: `GET /api/v1/system/health`
- PagerDuty integration for P0/P1 alerts
- Log analysis: structured logs in JSONL format
- Database monitoring: connection pool, slow queries
- Agent lifecycle: canary deployments, rollback

**T5: Compliance and Audit**
- Audit trail: `audit_events` table, immutable append-only
- Compliance queries: `GET /api/v1/audit/events` with filters
- Export for audit: `GET /api/v1/audit/export`
- PII handling: data classification, Ollama for confidential data
- Evidence collection for SOC 2 / GDPR

**T6: Advanced: Agent Tuning**
- Agent manifest structure (`manifest.yaml`)
- Prompt engineering for agents (`prompt.md`)
- Quality rubrics (`rubric.yaml`)
- A/B testing with canary deployments
- G3-agent-lifecycle-manager for version management

### 9.3 Training Materials

| Material | Format | Location |
|----------|--------|----------|
| Platform Quick Start Guide | Markdown | `docs/training/quick-start.md` |
| MCP Tool Reference Card | PDF | `docs/training/mcp-reference.pdf` |
| Dashboard Walkthrough Video | MP4 | `docs/training/dashboard-walkthrough.mp4` |
| Sample Raw Spec (for practice) | Markdown | `docs/training/sample-raw-spec.md` |
| FAQ | Markdown | `docs/training/faq.md` |

---

## 10. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R-1 | Generated document quality lower than manual | Medium | High | Phase 2 quality comparison; prompt tuning; threshold gates |
| R-2 | LLM provider outage during cutover | Low | High | Multi-provider support (Anthropic/OpenAI/Ollama); circuit breaker; failover |
| R-3 | Team resistance to automated workflow | Medium | Medium | Early pilot involvement; training; demonstrate time savings |
| R-4 | Cost per pipeline run exceeds $25 ceiling | Low | Medium | G1-cost-tracker hard stop; token budget enforcement; model tier selection |
| R-5 | Data loss during source document export | Low | High | Source docs remain in original systems; export is copy-only |
| R-6 | PII exposure during migration | Low | Critical | PII filtering in guardrails; Ollama for confidential data; pre-import PII scan |
| R-7 | Platform performance degradation under load | Medium | Medium | Load testing in Phase 2; connection pool tuning; rate limiting |
| R-8 | Compliance gap during transition period | Low | High | Audit trail active from Day 1; dual logging (manual + automated) during parallel phase |

---

## 11. Success Criteria

### Phase Completion Gates

| Phase | Gate Criteria | Measured By |
|-------|-------------|-------------|
| Phase 1 | 3 pilot projects imported, 3 users trained, platform healthy | Import validation + training log |
| Phase 2 | Generated doc quality >= 85% of manual baseline | Quality comparison report |
| Phase 3 | All new projects on pipeline for 2+ weeks, no P0/P1 open | Pipeline Runs + incident log |
| Phase 4 | 100% projects migrated, quality >= 90%, compliance audit passed | Final migration report |

### Overall Migration Success

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first document | < 30 seconds (from `trigger_pipeline` to first output) | `pipeline_runs.first_output_at - pipeline_runs.triggered_at` |
| Full pipeline time | < 10 minutes (excluding human approval wait time) | `pipeline_runs.completed_at - pipeline_runs.triggered_at` |
| Cost per run | < $25 | `SUM(cost_metrics.cost_usd) WHERE pipeline_run_id = ?` |
| Document quality | >= 85% average across all dimensions | `pipeline_steps.quality_score` |
| Team adoption | 100% of active projects | Count of projects with `pipeline_runs` records |
| Audit completeness | 100% of pipeline events logged | `audit_events` row count vs expected |

---

*End of MIGRATION-PLAN. This document will be updated as migration progresses through each phase.*
