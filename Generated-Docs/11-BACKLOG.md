# BACKLOG — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 11 of 14 | Status: Draft

---

## Table of Contents

1. [Overview](#1-overview)
2. [Sprint Summary](#2-sprint-summary)
3. [Story Schema](#3-story-schema)
4. [Sprint 0: Infrastructure](#4-sprint-0-infrastructure)
5. [Sprint 1: Core Shared Services](#5-sprint-1-core-shared-services)
6. [Sprint 2: Safety + Approval Services](#6-sprint-2-safety--approval-services)
7. [Sprint 3: MCP Servers + REST API](#7-sprint-3-mcp-servers--rest-api)
8. [Sprint 4: REST API + Dashboard Foundation](#8-sprint-4-rest-api--dashboard-foundation)
9. [Sprint 5: Dashboard Pages](#9-sprint-5-dashboard-pages)
10. [Sprint 6: Cross-Interface Integration](#10-sprint-6-cross-interface-integration)
11. [Sprint 7: Advanced Features](#11-sprint-7-advanced-features)
12. [Sprint 8: Polish + Hardening](#12-sprint-8-polish--hardening)
13. [Story Dependency Graph](#13-story-dependency-graph)
14. [Traceability Matrix](#14-traceability-matrix)
15. [Velocity and Capacity](#15-velocity-and-capacity)

---

## 1. Overview

This backlog decomposes the Agentic SDLC Platform into 77 implementable user stories across 8 sprints (16 weeks). Every story traces back to a feature (F-NNN) from the FEATURE-CATALOG (Doc 5), an interaction (I-NNN) from the INTERACTION-MAP (Doc 6), and forwards to MCP tools from MCP-TOOL-SPEC (Doc 7) and dashboard screens from DESIGN-SPEC (Doc 8).

### Full-Stack-First Sprint Priority

The sprint sequence follows Full-Stack-First layering:

1. **Sprints 0-2:** Foundation and shared services (database, business logic)
2. **Sprint 3:** MCP tools + REST endpoints (interface layer)
3. **Sprints 4-5:** Dashboard views (operator UI)
4. **Sprint 6:** Cross-interface integration and parity verification
5. **Sprints 7-8:** Advanced features, polish, and hardening

### Key Inputs

| Source Document | Items Referenced |
|---|---|
| FEATURE-CATALOG (Doc 5) | 56 features (F-001 to F-056) across 10 epics |
| INTERACTION-MAP (Doc 6) | 34 interactions (I-001 to I-082) with shared data shapes |
| MCP-TOOL-SPEC (Doc 7) | 35 MCP tools across 3 servers + system tools |
| DESIGN-SPEC (Doc 8) | 23 dashboard screens across 6 pages |
| QUALITY (Doc 4) | 64 NFRs (Q-001 to Q-064) |
| DATA-MODEL (Doc 9) | 10 tables, migrations 001-009 |

---

## 2. Sprint Summary

| Sprint | Theme | Stories | Points | Cumulative Points |
|--------|-------|---------|--------|-------------------|
| Sprint 0 | Infrastructure | 8 | 23 | 23 |
| Sprint 1 | Core Shared Services | 11 | 44 | 67 |
| Sprint 2 | Safety + Approval Services | 11 | 39 | 106 |
| Sprint 3 | MCP Servers + REST API | 11 | 45 | 151 |
| Sprint 4 | REST API + Dashboard Foundation | 10 | 43 | 194 |
| Sprint 5 | Dashboard Pages | 5 | 34 | 228 |
| Sprint 6 | Cross-Interface Integration | 7 | 41 | 269 |
| Sprint 7 | Advanced Features | 7 | 41 | 310 |
| Sprint 8 | Polish + Hardening | 7 | 41 | 351 |
| **Total** | | **77** | **351** | |

---

## 3. Story Schema

Every story in this backlog conforms to the following structure:

```yaml
id: S-NNN
title: What is being built
feature: F-NNN           # Reference to FEATURE-CATALOG
sprint: N                # Target sprint (0-8)
story_points: N          # Fibonacci: 1, 2, 3, 5, 8, 13
layer: service | mcp | rest | dashboard | integration | infrastructure
interaction_ids: [I-NNN] # References to INTERACTION-MAP
mcp_tools: [tool_names]  # MCP tools from MCP-TOOL-SPEC
dashboard_screens: []    # Screen names from DESIGN-SPEC
shared_service: Name     # Shared service that implements logic
acceptance_criteria:      # Given/When/Then format
depends_on: [S-NNN]      # Story dependencies
definition_of_done:       # Checkable completion statements
```

---

## 4. Sprint 0: Infrastructure

**Theme:** Database, project scaffolding, and security foundations
**Capacity:** 23 points | 2 weeks
**Goal:** All database tables exist, RLS policies enforced, CI pipeline green

---

### S-001: PostgreSQL Setup and Core Migrations (001-004)

```yaml
id: S-001
title: PostgreSQL setup with core migrations 001-004 (projects, pipeline_runs, pipeline_steps, agent_registry)
feature: F-050, F-051
sprint: 0
story_points: 3
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: DatabaseService
acceptance_criteria:
  - Given a fresh PostgreSQL 15+ instance
    When migrations 001-004 are applied via Alembic
    Then tables projects, pipeline_runs, pipeline_steps, and agent_registry exist with correct schemas
  - Given the migrations have been applied
    When a SELECT on each table is executed
    Then all columns match the DATA-MODEL specification (Doc 9)
  - Given the agent_registry table exists
    When the seed script runs
    Then 48 agent records are inserted across 7 SDLC phases
depends_on: []
definition_of_done:
  - [ ] Alembic migrations 001-004 pass on clean database
  - [ ] Schema matches DATA-MODEL exactly
  - [ ] Seed data for 48 agents loads without error
  - [ ] Rollback (downgrade) tested for each migration
  - [ ] CI runs migrations in GitHub Actions
```

---

### S-002: Migration 005 — knowledge_exceptions Table

```yaml
id: S-002
title: Migration 005 — knowledge_exceptions table for tiered exception storage
feature: F-029, F-030
sprint: 0
story_points: 2
layer: infrastructure
interaction_ids: [I-060, I-061]
mcp_tools: []
dashboard_screens: []
shared_service: KnowledgeService
acceptance_criteria:
  - Given migrations 001-004 have been applied
    When migration 005 runs
    Then the knowledge_exceptions table exists with columns: id, rule_pattern, exception_text, tier (client/stack/universal), project_id, created_by, created_at, promoted_at, promoted_by
  - Given the knowledge_exceptions table exists
    When an exception is inserted with tier='client'
    Then the row is persisted and retrievable by project_id
  - Given the table has a unique constraint on (rule_pattern, project_id, tier)
    When a duplicate is inserted
    Then a constraint violation error is raised
depends_on: [S-001]
definition_of_done:
  - [ ] Migration 005 applies cleanly after 001-004
  - [ ] Unique constraint on (rule_pattern, project_id, tier) verified
  - [ ] Rollback drops the table cleanly
  - [ ] Index on (project_id, tier) exists for query performance
```

---

### S-003: Migration 006 — session_context Table (BLOCKING)

```yaml
id: S-003
title: Migration 006 — session_context table for cross-request state management
feature: F-050
sprint: 0
story_points: 3
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: SessionService
acceptance_criteria:
  - Given migrations 001-005 have been applied
    When migration 006 runs
    Then the session_context table exists with columns: session_id (UUID PK), project_id (FK), context_data (JSONB), created_at, updated_at, expires_at, interface_origin (mcp/rest/dashboard)
  - Given the session_context table exists
    When a session is created with interface_origin='mcp'
    Then it is retrievable by session_id and includes project_id context
  - Given a session has expired (expires_at < now())
    When a cleanup job runs
    Then expired sessions are soft-deleted
depends_on: [S-001]
definition_of_done:
  - [ ] Migration 006 applies cleanly
  - [ ] JSONB context_data supports arbitrary key-value pairs
  - [ ] TTL index or cleanup function for expired sessions exists
  - [ ] Rollback tested
  - [ ] BLOCKING: All shared services in Sprint 1 depend on this table
```

---

### S-004: Migration 007 — approval_requests Table

```yaml
id: S-004
title: Migration 007 — approval_requests table for human gate management
feature: F-023, F-024
sprint: 0
story_points: 2
layer: infrastructure
interaction_ids: [I-045, I-046, I-047]
mcp_tools: []
dashboard_screens: []
shared_service: ApprovalService
acceptance_criteria:
  - Given migrations 001-006 have been applied
    When migration 007 runs
    Then the approval_requests table exists with columns: request_id (UUID PK), run_id (FK to pipeline_runs), step_name, gate_type (quality/architecture/deployment), status (pending/approved/rejected/escalated), requested_at, decided_at, decided_by, comment, sla_deadline
  - Given a pipeline run triggers a quality gate
    When an approval request is created
    Then it is persisted with status='pending' and sla_deadline set per gate_type
  - Given an approval request exists
    When it is approved with a comment
    Then status changes to 'approved', decided_at is set, and comment is stored
depends_on: [S-001]
definition_of_done:
  - [ ] Migration 007 applies cleanly
  - [ ] Foreign key to pipeline_runs enforced
  - [ ] Index on (status, sla_deadline) for pending query performance
  - [ ] Rollback tested
```

---

### S-005: Migration 008 — pipeline_checkpoints Table

```yaml
id: S-005
title: Migration 008 — pipeline_checkpoints table for resume-from-failure support
feature: F-004
sprint: 0
story_points: 2
layer: infrastructure
interaction_ids: [I-004, I-007]
mcp_tools: []
dashboard_screens: []
shared_service: PipelineService
acceptance_criteria:
  - Given migrations 001-007 have been applied
    When migration 008 runs
    Then the pipeline_checkpoints table exists with columns: checkpoint_id (UUID PK), run_id (FK), step_index, step_name, state (JSONB), output_artifact_path, created_at
  - Given a pipeline step completes successfully
    When a checkpoint is saved
    Then the step state and output path are persisted
  - Given a pipeline has failed at step 7
    When resume is requested
    Then checkpoints for steps 0-6 are retrievable to skip re-execution
depends_on: [S-001]
definition_of_done:
  - [ ] Migration 008 applies cleanly
  - [ ] Foreign key to pipeline_runs enforced
  - [ ] JSONB state column stores intermediate outputs
  - [ ] Index on (run_id, step_index) for sequential lookup
  - [ ] Rollback tested
```

---

### S-006: Migration 009 — mcp_call_events + agent_registry ALTER

```yaml
id: S-006
title: Migration 009 — mcp_call_events table and agent_registry version columns
feature: F-022, F-012
sprint: 0
story_points: 3
layer: infrastructure
interaction_ids: [I-082, I-024, I-025, I-026]
mcp_tools: []
dashboard_screens: []
shared_service: AuditService, AgentService
acceptance_criteria:
  - Given migrations 001-008 have been applied
    When migration 009 runs
    Then mcp_call_events table exists with columns: event_id (UUID PK), tool_name, server_name, client_id, project_id, input_hash, duration_ms, status (success/error), error_message, created_at
  - Given migration 009 has run
    Then agent_registry table has new columns: active_version, canary_version, canary_traffic_pct (default 0), promoted_at, rollback_version
  - Given an MCP tool is invoked
    When the call completes
    Then an mcp_call_events record can be inserted with all fields
depends_on: [S-001]
definition_of_done:
  - [ ] Migration 009 applies cleanly
  - [ ] mcp_call_events has index on (server_name, created_at) for feed queries
  - [ ] agent_registry ALTER adds version columns without data loss
  - [ ] Rollback removes new table and columns cleanly
```

---

### S-007: Project Scaffolding

```yaml
id: S-007
title: Project scaffolding — pyproject.toml, directory structure, CI pipeline, dev tooling
feature: F-056
sprint: 0
story_points: 5
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: N/A
acceptance_criteria:
  - Given a new developer clones the repository
    When they run `pip install -e ".[dev]"`
    Then all dependencies install and the project is importable
  - Given the project structure
    Then directories exist: src/services/, src/mcp_servers/, src/rest_api/, src/dashboard/, tests/, migrations/
  - Given a push to any branch
    When GitHub Actions runs
    Then lint (ruff), type check (mypy), and unit tests (pytest) execute in under 5 minutes
  - Given the CI pipeline
    Then code coverage threshold is set at 80% (Q-034)
depends_on: []
definition_of_done:
  - [ ] pyproject.toml with all dependencies and dev extras
  - [ ] Directory structure matches architecture document
  - [ ] GitHub Actions workflow (.github/workflows/ci.yml) runs on push
  - [ ] Pre-commit hooks configured (ruff, mypy, black)
  - [ ] .env.example with all required environment variables
  - [ ] Docker Compose for local PostgreSQL
```

---

### S-008: Row-Level Security Policies on All Multi-Tenant Tables

```yaml
id: S-008
title: RLS policies on all multi-tenant tables for tenant isolation
feature: F-051
sprint: 0
story_points: 3
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: DatabaseService
acceptance_criteria:
  - Given tables with project_id columns (pipeline_runs, pipeline_steps, knowledge_exceptions, session_context, approval_requests, pipeline_checkpoints)
    When RLS is enabled
    Then queries from a connection with SET app.current_project_id only return rows matching that project_id
  - Given an authenticated request for project A
    When it queries pipeline_runs
    Then it cannot see pipeline runs belonging to project B
  - Given the superuser role
    When queries are executed
    Then RLS policies are bypassed for admin operations
depends_on: [S-001, S-002, S-003, S-004, S-005, S-006]
definition_of_done:
  - [ ] RLS policies created for all 6 multi-tenant tables
  - [ ] Integration test verifies cross-tenant isolation
  - [ ] Superuser bypass documented and tested
  - [ ] Performance test confirms < 5% overhead from RLS
```

---

## 5. Sprint 1: Core Shared Services

**Theme:** Business logic layer — the services that MCP, REST, and Dashboard all delegate to
**Capacity:** 44 points | 2 weeks
**Goal:** All core services implemented and unit tested; no interface layer yet

---

### S-009: SessionService — Read, Write, List Session Context

```yaml
id: S-009
title: SessionService implementation — read, write, list session context for cross-request state
feature: F-050
sprint: 1
story_points: 8
layer: service
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: SessionService
acceptance_criteria:
  - Given a new MCP conversation begins
    When SessionService.create() is called with project_id and interface_origin
    Then a session_context row is created with a UUID session_id and default 30-minute TTL
  - Given an active session
    When SessionService.read(session_id) is called
    Then the session context_data JSONB is returned with all stored key-value pairs
  - Given an active session
    When SessionService.write(session_id, key, value) is called
    Then the context_data JSONB is updated and updated_at is refreshed
  - Given a project_id
    When SessionService.list(project_id) is called
    Then all active (non-expired) sessions for that project are returned
  - Given a session has expired
    When SessionService.read() is called
    Then a SessionExpiredError is raised
depends_on: [S-003, S-007]
definition_of_done:
  - [ ] SessionService class in src/services/session_service.py
  - [ ] Unit tests with 90%+ coverage
  - [ ] Session cleanup background task implemented
  - [ ] Async database operations via asyncpg
  - [ ] Type hints and docstrings on all public methods
```

---

### S-010: PipelineService.trigger() — Start a Pipeline Run

```yaml
id: S-010
title: PipelineService.trigger() — accept project brief and start pipeline execution
feature: F-001
sprint: 1
story_points: 5
layer: service
interaction_ids: [I-001]
mcp_tools: [trigger_pipeline]
dashboard_screens: [Pipeline Trigger Form]
shared_service: PipelineService
acceptance_criteria:
  - Given a valid project brief (non-empty, <= 50KB)
    When PipelineService.trigger(project_id, brief, config) is called
    Then a pipeline_runs row is created with status='pending' and a UUID run_id is returned
  - Given a valid trigger
    When the pipeline starts
    Then pipeline_steps rows are created for all 14 document phases
  - Given an invalid brief (empty or > 50KB)
    When PipelineService.trigger() is called
    Then a ValidationError is raised with a descriptive message
  - Given a successful trigger
    When the run is created
    Then an audit event 'pipeline.triggered' is emitted via AuditService
  - Given the trigger completes
    Then the response conforms to the PipelineRun data shape (INTERACTION-MAP Doc 6)
depends_on: [S-001, S-007]
definition_of_done:
  - [ ] PipelineService class in src/services/pipeline_service.py
  - [ ] trigger() method with input validation
  - [ ] Audit event emission
  - [ ] Unit tests for valid/invalid inputs
  - [ ] Returns PipelineRun data shape
```

---

### S-011: PipelineService.get_status() — Pipeline Run Status

```yaml
id: S-011
title: PipelineService.get_status() — retrieve current pipeline run status and progress
feature: F-002
sprint: 1
story_points: 3
layer: service
interaction_ids: [I-002]
mcp_tools: [get_pipeline_status]
dashboard_screens: [Pipeline Status Card]
shared_service: PipelineService
acceptance_criteria:
  - Given a valid run_id
    When PipelineService.get_status(run_id) is called
    Then a PipelineRun shape is returned with status, progress_pct, current_step, active_agents
  - Given a non-existent run_id
    When get_status() is called
    Then a NotFoundError is raised
  - Given a running pipeline
    When get_status() is called
    Then progress_pct reflects (completed_steps / total_steps) * 100
  - Given any call
    Then response latency is under 200ms (Q-001)
depends_on: [S-010]
definition_of_done:
  - [ ] get_status() method on PipelineService
  - [ ] Returns PipelineRun data shape from INTERACTION-MAP
  - [ ] NotFoundError for invalid run_id
  - [ ] Unit tests covering all pipeline statuses
```

---

### S-012: PipelineService.list_runs() — Paginated Pipeline Runs

```yaml
id: S-012
title: PipelineService.list_runs() — paginated list with filters (status, project, date)
feature: F-003
sprint: 1
story_points: 3
layer: service
interaction_ids: [I-003]
mcp_tools: [list_pipeline_runs]
dashboard_screens: [Pipeline Runs Table]
shared_service: PipelineService
acceptance_criteria:
  - Given pipeline runs exist
    When PipelineService.list_runs(limit=20, offset=0) is called
    Then a paginated list of PipelineRun shapes is returned, sorted by created_at descending
  - Given runs with mixed statuses
    When list_runs(status='running') is called
    Then only running pipelines are returned
  - Given a project_id filter
    When list_runs(project_id=X) is called
    Then only runs for project X are returned (RLS enforced)
  - Given valid filters
    Then response includes total_count for pagination metadata
depends_on: [S-010]
definition_of_done:
  - [ ] list_runs() method with limit, offset, status, project_id, date_from, date_to parameters
  - [ ] Pagination metadata (total_count, has_more)
  - [ ] Unit tests for each filter combination
  - [ ] SQL query uses indexes for performance
```

---

### S-013: AgentService.list_agents() — Agent Registry Query

```yaml
id: S-013
title: AgentService.list_agents() — return all 48 agents with status, phase, and archetype
feature: F-008
sprint: 1
story_points: 3
layer: service
interaction_ids: [I-020]
mcp_tools: [list_agents]
dashboard_screens: [Agent Grid]
shared_service: AgentService
acceptance_criteria:
  - Given the agent_registry is seeded with 48 agents
    When AgentService.list_agents() is called
    Then all 48 agents are returned as AgentSummary[] data shape
  - Given a phase filter
    When list_agents(phase=3) is called
    Then only agents in SDLC phase 3 are returned
  - Given any call
    Then each agent includes: agent_id, name, phase, archetype, status, maturity, active_invocations
  - Given the response
    Then agents are grouped by phase (1-7) in the returned list
depends_on: [S-001, S-007]
definition_of_done:
  - [ ] AgentService class in src/services/agent_service.py
  - [ ] list_agents() with optional phase filter
  - [ ] Returns AgentSummary[] from INTERACTION-MAP
  - [ ] Unit tests with mocked database
```

---

### S-014: AgentService.get_agent() — Single Agent Detail

```yaml
id: S-014
title: AgentService.get_agent() — retrieve full agent config, metrics, and prompt preview
feature: F-009
sprint: 1
story_points: 3
layer: service
interaction_ids: [I-021]
mcp_tools: [get_agent]
dashboard_screens: [Agent Detail Panel]
shared_service: AgentService
acceptance_criteria:
  - Given a valid agent_id
    When AgentService.get_agent(agent_id) is called
    Then an AgentDetail shape is returned with config, metrics, version slots, and prompt hash
  - Given a non-existent agent_id
    When get_agent() is called
    Then a NotFoundError is raised
  - Given a valid agent
    Then the response includes: model, temperature, system_prompt_hash, active_version, canary_version, performance_metrics
depends_on: [S-013]
definition_of_done:
  - [ ] get_agent() method on AgentService
  - [ ] Returns AgentDetail data shape
  - [ ] Includes version management fields from migration 009
  - [ ] Unit tests for found/not-found cases
```

---

### S-015: CostService.get_report() — Cost Breakdown Report

```yaml
id: S-015
title: CostService.get_report() — cost breakdown by scope (fleet/project/agent) and period
feature: F-014
sprint: 1
story_points: 5
layer: service
interaction_ids: [I-040]
mcp_tools: [get_cost_report]
dashboard_screens: [Cost Charts]
shared_service: CostService
acceptance_criteria:
  - Given cost records exist
    When CostService.get_report(scope='fleet', period='7d') is called
    Then a CostReport shape is returned with total_cost, breakdown_by_agent, breakdown_by_phase, daily_series
  - Given scope='project' and a project_id
    When get_report() is called
    Then only costs for that project are included
  - Given scope='agent' and an agent_id
    When get_report() is called
    Then cost data for that specific agent is returned with per-invocation detail
  - Given a period parameter
    Then supported values are: 1d, 7d, 30d, 90d, custom (with date_from/date_to)
depends_on: [S-001, S-007]
definition_of_done:
  - [ ] CostService class in src/services/cost_service.py
  - [ ] get_report() with scope, period, project_id, agent_id parameters
  - [ ] Returns CostReport data shape from INTERACTION-MAP
  - [ ] Aggregation queries optimized with indexes
  - [ ] Unit tests for each scope level
```

---

### S-016: CostService.check_budget() — Budget Status Check

```yaml
id: S-016
title: CostService.check_budget() — remaining budget at fleet, project, or agent level
feature: F-015
sprint: 1
story_points: 3
layer: service
interaction_ids: [I-041]
mcp_tools: [check_budget]
dashboard_screens: [Budget Gauges]
shared_service: CostService
acceptance_criteria:
  - Given a budget is configured for a project
    When CostService.check_budget(scope='project', project_id=X) is called
    Then a BudgetStatus shape is returned with budget_limit, spent, remaining, utilization_pct
  - Given utilization exceeds 80%
    Then the response includes warning=true
  - Given utilization exceeds 100%
    Then the response includes exceeded=true and remaining is negative
  - Given no budget is configured
    Then the response returns budget_limit=null with a note "No budget configured"
depends_on: [S-015]
definition_of_done:
  - [ ] check_budget() method on CostService
  - [ ] Returns BudgetStatus data shape
  - [ ] Warning thresholds configurable (default 80%)
  - [ ] Unit tests for under/warning/exceeded scenarios
```

---

### S-017: CostService.record_spend() — Record Agent Cost

```yaml
id: S-017
title: CostService.record_spend() — record token usage and cost for an agent invocation
feature: F-016
sprint: 1
story_points: 3
layer: service
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: CostService
acceptance_criteria:
  - Given an agent invocation completes
    When CostService.record_spend(agent_id, run_id, input_tokens, output_tokens, model, cost_usd) is called
    Then a cost record is persisted with all fields and a created_at timestamp
  - Given a cost record is created
    Then it is immediately reflected in subsequent get_report() and check_budget() calls
  - Given the budget is already exceeded
    When record_spend() is called
    Then the spend is still recorded but a BudgetExceededWarning is returned
  - Given invalid inputs (negative tokens or cost)
    Then a ValidationError is raised
depends_on: [S-015]
definition_of_done:
  - [ ] record_spend() method on CostService
  - [ ] Atomic write with budget check
  - [ ] Unit tests for valid/invalid/exceeded cases
  - [ ] Idempotency key to prevent double-recording
```

---

### S-018: AuditService.query_events() — Audit Trail Search

```yaml
id: S-018
title: AuditService.query_events() — search and filter audit trail by agent, severity, date
feature: F-019
sprint: 1
story_points: 5
layer: service
interaction_ids: [I-042]
mcp_tools: [query_audit_events]
dashboard_screens: [Event Table]
shared_service: AuditService
acceptance_criteria:
  - Given audit events exist
    When AuditService.query_events(limit=50, offset=0) is called
    Then a paginated list of AuditEvent[] is returned sorted by timestamp descending
  - Given a severity filter
    When query_events(severity='error') is called
    Then only error-level events are returned
  - Given an agent_id filter
    When query_events(agent_id=X) is called
    Then only events from agent X are returned
  - Given a date range filter
    When query_events(date_from=A, date_to=B) is called
    Then only events within the range are returned
  - Given the response
    Then each event includes: event_id, event_type, agent_id, severity, message, metadata (JSONB), created_at
depends_on: [S-001, S-007]
definition_of_done:
  - [ ] AuditService class in src/services/audit_service.py
  - [ ] query_events() with pagination and filters
  - [ ] Returns AuditEvent[] data shape from INTERACTION-MAP
  - [ ] Composite index on (severity, created_at) for filter performance
  - [ ] Unit tests for each filter parameter
```

---

### S-019: AuditService.get_summary() — Aggregated Audit Statistics

```yaml
id: S-019
title: AuditService.get_summary() — aggregated audit statistics for a time period
feature: F-020
sprint: 1
story_points: 3
layer: service
interaction_ids: [I-043]
mcp_tools: [get_audit_summary]
dashboard_screens: [Summary Cards]
shared_service: AuditService
acceptance_criteria:
  - Given audit events exist for the past 7 days
    When AuditService.get_summary(period='7d') is called
    Then an AuditSummary shape is returned with total_events, by_severity (info/warn/error/critical), by_event_type, by_agent
  - Given a project_id filter
    When get_summary(project_id=X) is called
    Then only events for that project are aggregated
  - Given no events exist for the period
    Then all counts are 0 and the response is still valid
depends_on: [S-018]
definition_of_done:
  - [ ] get_summary() method on AuditService
  - [ ] Returns AuditSummary data shape
  - [ ] Aggregation query with GROUP BY
  - [ ] Unit tests with sample data
```

---

## 6. Sprint 2: Safety + Approval Services

**Theme:** Approval gates, knowledge management, health monitoring, and rate limiting
**Capacity:** 39 points | 2 weeks
**Goal:** All shared services complete; ready for interface layer in Sprint 3

---

### S-020: ApprovalService.create_request() — Create Approval Gate

```yaml
id: S-020
title: ApprovalService.create_request() — create a human approval gate for a pipeline step
feature: F-023
sprint: 2
story_points: 5
layer: service
interaction_ids: [I-045]
mcp_tools: [list_pending_approvals]
dashboard_screens: [Approval Queue Table]
shared_service: ApprovalService
acceptance_criteria:
  - Given a pipeline step requires human approval
    When ApprovalService.create_request(run_id, step_name, gate_type) is called
    Then an approval_requests row is created with status='pending' and sla_deadline computed from gate_type
  - Given gate_type='quality'
    Then sla_deadline is set to 4 hours from creation
  - Given gate_type='architecture'
    Then sla_deadline is set to 8 hours from creation
  - Given gate_type='deployment'
    Then sla_deadline is set to 2 hours from creation
  - Given the request is created
    Then an audit event 'approval.requested' is emitted
  - Given the pipeline run does not exist
    Then a NotFoundError is raised
depends_on: [S-001, S-004, S-010]
definition_of_done:
  - [ ] ApprovalService class in src/services/approval_service.py
  - [ ] create_request() with SLA deadline computation
  - [ ] Audit event emission on creation
  - [ ] Unit tests for each gate_type
  - [ ] Foreign key validation against pipeline_runs
```

---

### S-021: ApprovalService.list_pending() — Pending Approval Queue

```yaml
id: S-021
title: ApprovalService.list_pending() — list all pending approval requests
feature: F-024
sprint: 2
story_points: 3
layer: service
interaction_ids: [I-045]
mcp_tools: [list_pending_approvals]
dashboard_screens: [Approval Queue Table]
shared_service: ApprovalService
acceptance_criteria:
  - Given pending approval requests exist
    When ApprovalService.list_pending() is called
    Then all requests with status='pending' are returned sorted by sla_deadline ascending (most urgent first)
  - Given a project_id filter
    When list_pending(project_id=X) is called
    Then only approvals for project X's pipelines are returned
  - Given each approval request
    Then it includes: request_id, run_id, step_name, gate_type, status, requested_at, sla_deadline, time_remaining
  - Given an approval is past its SLA deadline
    Then time_remaining is negative and is_overdue=true
depends_on: [S-020]
definition_of_done:
  - [ ] list_pending() method on ApprovalService
  - [ ] Returns ApprovalRequest[] data shape
  - [ ] SLA time_remaining calculated dynamically
  - [ ] Unit tests with overdue and non-overdue scenarios
```

---

### S-022: ApprovalService.approve() — Approve a Gate

```yaml
id: S-022
title: ApprovalService.approve() — approve a pipeline gate to allow continuation
feature: F-025
sprint: 2
story_points: 3
layer: service
interaction_ids: [I-046]
mcp_tools: [approve_gate]
dashboard_screens: [Approve Button]
shared_service: ApprovalService
acceptance_criteria:
  - Given a pending approval request
    When ApprovalService.approve(request_id, decided_by, comment) is called
    Then status changes to 'approved', decided_at is set, decided_by and comment are stored
  - Given the approval is processed
    Then an audit event 'approval.approved' is emitted with the decision metadata
  - Given the approval is processed
    Then the associated pipeline run is notified to resume (via PipelineService.resume())
  - Given the request is not in 'pending' status
    Then a ConflictError is raised ("Approval already decided")
  - Given the request_id does not exist
    Then a NotFoundError is raised
depends_on: [S-020]
definition_of_done:
  - [ ] approve() method on ApprovalService
  - [ ] Status transition validation (only pending -> approved)
  - [ ] Audit event emission
  - [ ] Pipeline resume notification
  - [ ] Unit tests for approve/conflict/not-found
```

---

### S-023: ApprovalService.reject() — Reject a Gate

```yaml
id: S-023
title: ApprovalService.reject() — reject a pipeline gate with mandatory comment
feature: F-026
sprint: 2
story_points: 3
layer: service
interaction_ids: [I-047]
mcp_tools: [reject_gate]
dashboard_screens: [Reject Button + Comment Field]
shared_service: ApprovalService
acceptance_criteria:
  - Given a pending approval request
    When ApprovalService.reject(request_id, decided_by, comment) is called
    Then status changes to 'rejected', decided_at is set, and comment is stored
  - Given the rejection
    Then comment is mandatory — empty comment raises ValidationError
  - Given the rejection is processed
    Then an audit event 'approval.rejected' is emitted
  - Given the rejection is processed
    Then the associated pipeline run transitions to 'failed' with rejection reason
  - Given the request is not in 'pending' status
    Then a ConflictError is raised
depends_on: [S-020]
definition_of_done:
  - [ ] reject() method on ApprovalService
  - [ ] Mandatory comment validation
  - [ ] Pipeline failure notification
  - [ ] Audit event emission
  - [ ] Unit tests for reject/conflict/missing-comment
```

---

### S-024: PipelineService.resume() — Resume from Checkpoint

```yaml
id: S-024
title: PipelineService.resume() — resume a failed or paused pipeline from last checkpoint
feature: F-004
sprint: 2
story_points: 5
layer: service
interaction_ids: [I-004]
mcp_tools: [resume_pipeline]
dashboard_screens: [Resume Button]
shared_service: PipelineService
acceptance_criteria:
  - Given a pipeline run in 'failed' or 'paused' status
    When PipelineService.resume(run_id) is called
    Then the pipeline restarts from the last successful checkpoint
  - Given checkpoints exist for steps 0-5
    When resume is called
    Then steps 0-5 are skipped and execution begins at step 6
  - Given a pipeline in 'running' status
    When resume() is called
    Then a ConflictError is raised ("Pipeline is already running")
  - Given a pipeline in 'completed' status
    When resume() is called
    Then a ValidationError is raised ("Cannot resume a completed pipeline")
  - Given a successful resume
    Then an audit event 'pipeline.resumed' is emitted with checkpoint context
depends_on: [S-010, S-005]
definition_of_done:
  - [ ] resume() method on PipelineService
  - [ ] Checkpoint loading from pipeline_checkpoints table
  - [ ] Status validation (only failed/paused allowed)
  - [ ] Audit event emission
  - [ ] Unit tests for resume/conflict/invalid-status
```

---

### S-025: PipelineService.cancel() — Cancel Running Pipeline

```yaml
id: S-025
title: PipelineService.cancel() — stop a running pipeline gracefully
feature: F-005
sprint: 2
story_points: 2
layer: service
interaction_ids: [I-005]
mcp_tools: [cancel_pipeline]
dashboard_screens: [Cancel Button]
shared_service: PipelineService
acceptance_criteria:
  - Given a pipeline in 'running' or 'pending' status
    When PipelineService.cancel(run_id) is called
    Then status transitions to 'cancelled' and active agents receive cancellation signal
  - Given active agent invocations
    Then they are terminated within 5 seconds of cancellation
  - Given partial outputs exist before cancellation
    Then they are preserved in pipeline_checkpoints
  - Given a pipeline in 'completed' or 'cancelled' status
    When cancel() is called
    Then a ValidationError is raised
  - Given a successful cancellation
    Then an audit event 'pipeline.cancelled' is emitted and cost accrued is recorded
depends_on: [S-010]
definition_of_done:
  - [ ] cancel() method on PipelineService
  - [ ] Agent cancellation signal propagation
  - [ ] Partial output preservation
  - [ ] Audit event emission
  - [ ] Unit tests for cancel/invalid-status
```

---

### S-026: KnowledgeService.search() — Search Knowledge Exceptions

```yaml
id: S-026
title: KnowledgeService.search() — find knowledge exceptions by keyword or rule pattern
feature: F-029
sprint: 2
story_points: 3
layer: service
interaction_ids: [I-060]
mcp_tools: [search_exceptions]
dashboard_screens: []
shared_service: KnowledgeService
acceptance_criteria:
  - Given knowledge exceptions exist
    When KnowledgeService.search(query='typescript', project_id=X) is called
    Then exceptions matching the keyword in rule_pattern or exception_text are returned
  - Given a tier filter
    When search(tier='universal') is called
    Then only universal-tier exceptions are returned
  - Given the search
    Then results are ranked by relevance (keyword match score)
  - Given no matches
    Then an empty list is returned
  - Given the response
    Then each result includes: id, rule_pattern, exception_text, tier, created_at, match_score
depends_on: [S-002, S-007]
definition_of_done:
  - [ ] KnowledgeService class in src/services/knowledge_service.py
  - [ ] search() with keyword, project_id, tier parameters
  - [ ] PostgreSQL full-text search or trigram matching
  - [ ] Returns KnowledgeException[] data shape
  - [ ] Unit tests for match/no-match/tier-filter
```

---

### S-027: KnowledgeService.create_exception() — Add Exception Rule

```yaml
id: S-027
title: KnowledgeService.create_exception() — add a new exception rule at client tier
feature: F-030
sprint: 2
story_points: 3
layer: service
interaction_ids: [I-061]
mcp_tools: [create_exception]
dashboard_screens: []
shared_service: KnowledgeService
acceptance_criteria:
  - Given valid exception data
    When KnowledgeService.create_exception(rule_pattern, exception_text, project_id, created_by) is called
    Then a knowledge_exceptions row is created with tier='client'
  - Given the creation
    Then the new exception is immediately searchable via search()
  - Given a duplicate rule_pattern for the same project and tier
    When create_exception() is called
    Then a ConflictError is raised ("Exception already exists for this pattern")
  - Given an empty rule_pattern or exception_text
    Then a ValidationError is raised
  - Given a successful creation
    Then an audit event 'knowledge.exception_created' is emitted
depends_on: [S-026]
definition_of_done:
  - [ ] create_exception() method on KnowledgeService
  - [ ] Unique constraint enforcement
  - [ ] Audit event emission
  - [ ] Input validation
  - [ ] Unit tests for create/duplicate/invalid
```

---

### S-028: KnowledgeService.promote() — Promote Exception Tier

```yaml
id: S-028
title: KnowledgeService.promote() — promote exception from client to stack to universal tier
feature: F-031
sprint: 2
story_points: 3
layer: service
interaction_ids: [I-062]
mcp_tools: [promote_exception]
dashboard_screens: []
shared_service: KnowledgeService
acceptance_criteria:
  - Given a client-tier exception
    When KnowledgeService.promote(exception_id) is called
    Then tier changes from 'client' to 'stack' and promoted_at/promoted_by are set
  - Given a stack-tier exception
    When promote() is called
    Then tier changes from 'stack' to 'universal'
  - Given a universal-tier exception
    When promote() is called
    Then a ValidationError is raised ("Already at highest tier")
  - Given a successful promotion
    Then an audit event 'knowledge.exception_promoted' is emitted with old_tier and new_tier
depends_on: [S-027]
definition_of_done:
  - [ ] promote() method on KnowledgeService
  - [ ] Tier transition validation (client -> stack -> universal)
  - [ ] promoted_at and promoted_by tracking
  - [ ] Audit event emission
  - [ ] Unit tests for each tier transition
```

---

### S-029: HealthService.get_fleet_health() — Platform Health Overview

```yaml
id: S-029
title: HealthService.get_fleet_health() — overall platform health with agent counts and circuit breakers
feature: F-054
sprint: 2
story_points: 3
layer: service
interaction_ids: [I-080]
mcp_tools: [get_fleet_health]
dashboard_screens: [Health Overview]
shared_service: HealthService
acceptance_criteria:
  - Given the platform is operational
    When HealthService.get_fleet_health() is called
    Then a FleetHealth shape is returned with total_agents, healthy_count, degraded_count, offline_count, avg_latency_ms, circuit_breakers_open
  - Given all 48 agents are healthy
    Then healthy_count=48, degraded_count=0, offline_count=0
  - Given 3 agents have open circuit breakers
    Then circuit_breakers_open=3 and those agents are in degraded_count
  - Given the fleet health
    Then the response includes a health_status enum: 'healthy' (all green), 'degraded' (any degraded), 'critical' (>20% offline)
depends_on: [S-013, S-007]
definition_of_done:
  - [ ] HealthService class in src/services/health_service.py
  - [ ] get_fleet_health() with aggregated agent status
  - [ ] Returns FleetHealth data shape from INTERACTION-MAP
  - [ ] Circuit breaker state tracking
  - [ ] Unit tests for healthy/degraded/critical scenarios
```

---

### S-030: RateLimiter Implementation

```yaml
id: S-030
title: RateLimiter — token bucket rate limiting for MCP and REST interfaces
feature: F-052
sprint: 2
story_points: 5
layer: service
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: RateLimiter
acceptance_criteria:
  - Given the rate limiter is configured with 100 requests/minute per client
    When a client makes 100 requests within 60 seconds
    Then all 100 succeed
  - Given the rate limit is exhausted
    When the 101st request arrives
    Then a RateLimitExceededError is raised with retry_after_seconds
  - Given MCP and REST interfaces
    Then both use the same RateLimiter instance with shared counters per client_id
  - Given the rate limiter
    Then it uses a token bucket algorithm with configurable burst (default 10) and refill rate
  - Given a rate-limited request
    Then the response includes headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
depends_on: [S-007]
definition_of_done:
  - [ ] RateLimiter class in src/services/rate_limiter.py
  - [ ] Token bucket algorithm with configurable rate/burst
  - [ ] Redis-backed for multi-process consistency (or in-memory for single-process)
  - [ ] Middleware integration points for MCP and REST
  - [ ] Unit tests for within-limit/exceeded/burst scenarios
```

---

## 7. Sprint 3: MCP Servers + REST API

**Theme:** Interface layer — expose all shared services via MCP tools and begin REST API
**Capacity:** 45 points | 2 weeks
**Goal:** All 35 MCP tools operational, MCP authentication in place

---

### S-031: MCP agents-server Scaffold (stdio transport)

```yaml
id: S-031
title: MCP agents-server scaffold — stdio transport, tool registration, error handling
feature: F-034
sprint: 3
story_points: 5
layer: mcp
interaction_ids: [I-001, I-002, I-003, I-020, I-021]
mcp_tools: []
dashboard_screens: []
shared_service: N/A
acceptance_criteria:
  - Given the agents-server is started
    When an MCP initialize handshake is sent via stdio
    Then the server responds with capabilities including tools, resources, and prompts
  - Given the server is running
    When tools/list is called
    Then all 18 agent+pipeline tools are listed with correct schemas
  - Given any tool call
    Then errors are caught and returned as MCP error responses (not process crashes)
  - Given the server startup
    Then it reaches ready state within 5 seconds (Q-003)
  - Given the server
    Then it logs all tool invocations to structlog with correlation IDs
depends_on: [S-010, S-013, S-007]
definition_of_done:
  - [ ] src/mcp_servers/agents/server.py with MCP SDK integration
  - [ ] stdio transport working
  - [ ] Tool registration for all 18 tools (stubs for unimplemented)
  - [ ] Error handling middleware
  - [ ] Integration test: initialize -> tools/list -> tool call
```

---

### S-032: MCP Pipeline Tools — trigger, get_status, list_runs

```yaml
id: S-032
title: MCP tools — trigger_pipeline, get_pipeline_status, list_pipeline_runs
feature: F-001, F-002, F-003
sprint: 3
story_points: 5
layer: mcp
interaction_ids: [I-001, I-002, I-003]
mcp_tools: [trigger_pipeline, get_pipeline_status, list_pipeline_runs]
dashboard_screens: []
shared_service: PipelineService
acceptance_criteria:
  - Given the MCP agents-server is running
    When trigger_pipeline is called with a valid project brief
    Then PipelineService.trigger() is invoked and the PipelineRun shape is returned
  - Given a running pipeline
    When get_pipeline_status is called with a run_id
    Then PipelineService.get_status() is invoked and the response matches the INTERACTION-MAP data shape exactly
  - Given pipeline runs exist
    When list_pipeline_runs is called with filters
    Then PipelineService.list_runs() is invoked with matching parameters
  - Given any MCP tool handler
    Then it is a thin wrapper — no business logic, only service delegation
  - Given an MCP read tool
    Then response time is under 500ms (Q-001)
depends_on: [S-031, S-010, S-011, S-012]
definition_of_done:
  - [ ] Three tool handlers in agents-server
  - [ ] Each delegates to PipelineService methods
  - [ ] Input schema validation per MCP-TOOL-SPEC
  - [ ] Integration tests for each tool
  - [ ] Response shapes match INTERACTION-MAP exactly
```

---

### S-033: MCP Agent Tools — list, get, invoke, health

```yaml
id: S-033
title: MCP tools — list_agents, get_agent, invoke_agent, check_agent_health
feature: F-008, F-009, F-010, F-011
sprint: 3
story_points: 5
layer: mcp
interaction_ids: [I-020, I-021, I-022, I-023]
mcp_tools: [list_agents, get_agent, invoke_agent, check_agent_health]
dashboard_screens: []
shared_service: AgentService
acceptance_criteria:
  - Given the agents-server is running
    When list_agents is called
    Then AgentService.list_agents() is invoked and AgentSummary[] is returned
  - Given a valid agent_id
    When get_agent is called
    Then AgentService.get_agent() is invoked and AgentDetail is returned
  - Given a valid agent_id and input
    When invoke_agent is called
    Then AgentService.invoke() executes the agent outside pipeline context and returns AgentInvocationResult
  - Given an agent_id
    When check_agent_health is called
    Then AgentService.health_check() pings the agent and returns AgentHealth with response_time_ms
depends_on: [S-031, S-013, S-014]
definition_of_done:
  - [ ] Four tool handlers in agents-server
  - [ ] Each delegates to AgentService methods
  - [ ] invoke_agent includes cost tracking via CostService.record_spend()
  - [ ] Integration tests for each tool
```

---

### S-034: MCP governance-server Scaffold

```yaml
id: S-034
title: MCP governance-server scaffold — stdio transport for cost, audit, and approval tools
feature: F-035
sprint: 3
story_points: 3
layer: mcp
interaction_ids: [I-040, I-042, I-045]
mcp_tools: []
dashboard_screens: []
shared_service: N/A
acceptance_criteria:
  - Given the governance-server is started
    When an MCP initialize handshake is sent
    Then the server responds with capabilities listing 10 tools
  - Given the server
    Then it reaches ready state within 5 seconds (Q-003)
  - Given any tool call
    Then errors are wrapped in MCP error responses
  - Given the server
    Then it runs on port 3101 in production (streamable-http)
depends_on: [S-015, S-018, S-020, S-007]
definition_of_done:
  - [ ] src/mcp_servers/governance/server.py with MCP SDK integration
  - [ ] stdio transport working
  - [ ] Tool registration for all 10 tools
  - [ ] Error handling middleware
  - [ ] Integration test: initialize -> tools/list
```

---

### S-035: MCP Governance Tools — cost + audit

```yaml
id: S-035
title: MCP tools — get_cost_report, check_budget, query_audit_events, get_audit_summary
feature: F-014, F-015, F-019, F-020
sprint: 3
story_points: 5
layer: mcp
interaction_ids: [I-040, I-041, I-042, I-043]
mcp_tools: [get_cost_report, check_budget, query_audit_events, get_audit_summary]
dashboard_screens: []
shared_service: CostService, AuditService
acceptance_criteria:
  - Given the governance-server is running
    When get_cost_report is called with scope and period
    Then CostService.get_report() is invoked and CostReport shape is returned
  - Given a check_budget call
    Then CostService.check_budget() is invoked and BudgetStatus is returned
  - Given a query_audit_events call with filters
    Then AuditService.query_events() is invoked with matching parameters
  - Given a get_audit_summary call
    Then AuditService.get_summary() is invoked and AuditSummary is returned
  - Given all tools
    Then response shapes match INTERACTION-MAP data shapes exactly
depends_on: [S-034, S-015, S-016, S-018, S-019]
definition_of_done:
  - [ ] Four tool handlers in governance-server
  - [ ] Each delegates to respective service methods
  - [ ] Input schema validation per MCP-TOOL-SPEC
  - [ ] Integration tests for each tool
```

---

### S-036: MCP Approval Tools — list, approve, reject

```yaml
id: S-036
title: MCP tools — list_pending_approvals, approve_gate, reject_gate
feature: F-024, F-025, F-026
sprint: 3
story_points: 5
layer: mcp
interaction_ids: [I-045, I-046, I-047]
mcp_tools: [list_pending_approvals, approve_gate, reject_gate]
dashboard_screens: []
shared_service: ApprovalService
acceptance_criteria:
  - Given the governance-server is running
    When list_pending_approvals is called
    Then ApprovalService.list_pending() is invoked and ApprovalRequest[] is returned
  - Given a pending approval
    When approve_gate is called with request_id and comment
    Then ApprovalService.approve() is invoked and ApprovalResult is returned
  - Given a pending approval
    When reject_gate is called with request_id and mandatory comment
    Then ApprovalService.reject() is invoked and ApprovalResult is returned
  - Given reject_gate without a comment
    Then a validation error is returned
depends_on: [S-034, S-020, S-021, S-022, S-023]
definition_of_done:
  - [ ] Three tool handlers in governance-server
  - [ ] Mandatory comment validation for reject_gate
  - [ ] Integration tests for approve/reject flows
  - [ ] Response shapes match INTERACTION-MAP
```

---

### S-037: MCP knowledge-server Scaffold

```yaml
id: S-037
title: MCP knowledge-server scaffold — stdio transport for exception knowledge base tools
feature: F-036
sprint: 3
story_points: 3
layer: mcp
interaction_ids: [I-060, I-061, I-062, I-063]
mcp_tools: []
dashboard_screens: []
shared_service: N/A
acceptance_criteria:
  - Given the knowledge-server is started
    When an MCP initialize handshake is sent
    Then the server responds with capabilities listing 4 tools
  - Given the server
    Then it reaches ready state within 5 seconds (Q-003)
  - Given any tool call
    Then errors are wrapped in MCP error responses
  - Given the server
    Then it runs on port 3102 in production (streamable-http)
depends_on: [S-026, S-007]
definition_of_done:
  - [ ] src/mcp_servers/knowledge/server.py with MCP SDK integration
  - [ ] stdio transport working
  - [ ] Tool registration for all 4 tools
  - [ ] Error handling middleware
  - [ ] Integration test: initialize -> tools/list
```

---

### S-038: MCP Knowledge Tools — search, create, promote, list

```yaml
id: S-038
title: MCP tools — search_exceptions, create_exception, promote_exception, list_exceptions
feature: F-029, F-030, F-031, F-032
sprint: 3
story_points: 5
layer: mcp
interaction_ids: [I-060, I-061, I-062, I-063]
mcp_tools: [search_exceptions, create_exception, promote_exception, list_exceptions]
dashboard_screens: []
shared_service: KnowledgeService
acceptance_criteria:
  - Given the knowledge-server is running
    When search_exceptions is called with a query
    Then KnowledgeService.search() is invoked and KnowledgeException[] is returned
  - Given create_exception is called with valid data
    Then KnowledgeService.create_exception() is invoked and a new KnowledgeException is returned
  - Given promote_exception is called with an exception_id
    Then KnowledgeService.promote() is invoked and the updated KnowledgeException is returned
  - Given list_exceptions is called with a tier filter
    Then KnowledgeService.list_by_tier() is invoked and KnowledgeException[] is returned
depends_on: [S-037, S-026, S-027, S-028]
definition_of_done:
  - [ ] Four tool handlers in knowledge-server
  - [ ] Each delegates to KnowledgeService methods
  - [ ] Input schema validation per MCP-TOOL-SPEC
  - [ ] Integration tests for each tool
```

---

### S-039: MCP Authentication (API Key)

```yaml
id: S-039
title: MCP authentication — API key validation for all three MCP servers
feature: F-037
sprint: 3
story_points: 3
layer: mcp
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: AuthService
acceptance_criteria:
  - Given an MCP client connects with a valid ANTHROPIC_API_KEY
    When any tool is called
    Then the request is authorized and processed normally
  - Given an MCP client connects without an API key
    When any tool is called
    Then an MCP error response is returned with code -32001 ("Unauthorized")
  - Given an MCP client connects with an invalid API key
    When any tool is called
    Then an MCP error response is returned with code -32001
  - Given authentication
    Then the client_id is extracted from the API key and used for rate limiting and audit trails
  - Given the authentication middleware
    Then it applies to all three servers (agents, governance, knowledge)
depends_on: [S-031, S-034, S-037]
definition_of_done:
  - [ ] Auth middleware in src/mcp_servers/auth.py
  - [ ] API key validation against allowed keys store
  - [ ] client_id extraction for downstream use
  - [ ] Applied to all three MCP servers
  - [ ] Integration tests for valid/invalid/missing keys
```

---

### S-040: MCP Resources (Agent Manifests, Prompts)

```yaml
id: S-040
title: MCP resources — agent manifests and system prompt templates as MCP resources
feature: F-038
sprint: 3
story_points: 3
layer: mcp
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: AgentService
acceptance_criteria:
  - Given the agents-server is running
    When resources/list is called
    Then 4 resources are listed: agent-manifest://{agent_id}, pipeline-config://{pipeline_name}, system-prompt://{agent_id}, cost-report://{scope}
  - Given a valid agent_id
    When resources/read is called for agent-manifest://{agent_id}
    Then the agent's full manifest YAML is returned
  - Given a valid agent_id
    When resources/read is called for system-prompt://{agent_id}
    Then the agent's current system prompt template is returned
  - Given resources
    Then they support subscriptions for real-time updates when agent config changes
depends_on: [S-031, S-013, S-014]
definition_of_done:
  - [ ] Resource handlers in agents-server
  - [ ] 4 resource types registered
  - [ ] Resource subscription support
  - [ ] Integration tests for list/read
```

---

### S-041: MCP Prompt Templates

```yaml
id: S-041
title: MCP prompt templates — generate-docs, review-code, and other reusable prompts
feature: F-039
sprint: 3
story_points: 3
layer: mcp
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: N/A
acceptance_criteria:
  - Given the agents-server is running
    When prompts/list is called
    Then prompt templates are listed: generate-docs, review-code
  - Given the governance-server is running
    When prompts/list is called
    Then prompt templates are listed: audit-investigation, cost-analysis
  - Given a prompt template
    When prompts/get is called with arguments
    Then the template is rendered with the provided arguments and returned as MCP messages
  - Given each prompt template
    Then it includes: name, description, required arguments, optional arguments
depends_on: [S-031, S-034]
definition_of_done:
  - [ ] Prompt handlers in agents-server and governance-server
  - [ ] 6 prompt templates total (matching MCP-TOOL-SPEC)
  - [ ] Argument validation and rendering
  - [ ] Integration tests for list/get with arguments
```

---

## 8. Sprint 4: REST API + Dashboard Foundation

**Theme:** REST endpoints for all services and dashboard scaffolding
**Capacity:** 43 points | 2 weeks
**Goal:** Full REST API operational, dashboard scaffold with Fleet Health page

---

### S-042: REST API Scaffold (aiohttp, Middleware)

```yaml
id: S-042
title: REST API scaffold — aiohttp server on port 8080 with auth, CORS, logging, error handling middleware
feature: F-051
sprint: 4
story_points: 5
layer: rest
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: N/A
acceptance_criteria:
  - Given the REST API server starts
    When a GET /api/v1/health is sent
    Then a 200 response is returned with server status
  - Given the server
    Then it runs on port 8080 with aiohttp
  - Given middleware stack
    Then requests pass through: CORS -> Auth -> RateLimit -> Logging -> Handler -> ErrorHandler
  - Given any request
    Then a correlation_id (X-Request-ID) is generated and propagated to all service calls
  - Given an unauthenticated request to a protected route
    Then a 401 response is returned
  - Given all responses
    Then they include standard headers: X-Request-ID, X-RateLimit-*, Content-Type
depends_on: [S-007, S-030]
definition_of_done:
  - [ ] src/rest_api/app.py with aiohttp application factory
  - [ ] Middleware chain: CORS, auth, rate limit, logging, error handling
  - [ ] Health endpoint working
  - [ ] Correlation ID propagation
  - [ ] Integration test for middleware chain
```

---

### S-043: REST Pipeline Routes (All 9 Endpoints)

```yaml
id: S-043
title: REST pipeline routes — CRUD + control endpoints for pipeline operations
feature: F-001, F-002, F-003, F-004, F-005
sprint: 4
story_points: 5
layer: rest
interaction_ids: [I-001, I-002, I-003, I-004, I-005, I-006, I-007, I-008, I-009]
mcp_tools: []
dashboard_screens: []
shared_service: PipelineService
acceptance_criteria:
  - Given the REST API is running
    When POST /api/v1/pipelines is called with a valid brief
    Then PipelineService.trigger() is invoked and 201 is returned with PipelineRun
  - Given GET /api/v1/pipelines
    Then PipelineService.list_runs() is invoked with query parameters and 200 is returned
  - Given GET /api/v1/pipelines/{run_id}
    Then PipelineService.get_status() is invoked and 200 is returned with PipelineRun
  - Given POST /api/v1/pipelines/{run_id}/resume
    Then PipelineService.resume() is invoked and 200 is returned
  - Given POST /api/v1/pipelines/{run_id}/cancel
    Then PipelineService.cancel() is invoked and 200 is returned
  - Given GET /api/v1/pipelines/{run_id}/documents
    Then PipelineService.get_documents() is invoked and 200 is returned
  - Given POST /api/v1/pipelines/{run_id}/steps/{step}/retry
    Then PipelineService.retry_step() is invoked and 200 is returned
  - Given GET /api/v1/pipelines/{run_id}/config
    Then PipelineService.get_config() is invoked and 200 is returned
  - Given POST /api/v1/pipelines/validate
    Then PipelineService.validate_input() is invoked and 200 is returned
  - Given all route handlers
    Then they are thin wrappers — no business logic, only service delegation (same as MCP tools)
depends_on: [S-042, S-010, S-011, S-012, S-024, S-025]
definition_of_done:
  - [ ] src/rest_api/routes/pipelines.py with 9 endpoint handlers
  - [ ] Each delegates to PipelineService methods
  - [ ] OpenAPI schema annotations for all endpoints
  - [ ] Integration tests for each endpoint (happy path + error cases)
  - [ ] Response shapes identical to MCP tool responses (parity, Q-049)
```

---

### S-044: REST Agent Routes (All 8 Endpoints)

```yaml
id: S-044
title: REST agent routes — list, get, invoke, health, version management endpoints
feature: F-008, F-009, F-010, F-011, F-012, F-013
sprint: 4
story_points: 5
layer: rest
interaction_ids: [I-020, I-021, I-022, I-023, I-024, I-025, I-026, I-027]
mcp_tools: []
dashboard_screens: []
shared_service: AgentService
acceptance_criteria:
  - Given GET /api/v1/agents
    Then AgentService.list_agents() is invoked and 200 is returned with AgentSummary[]
  - Given GET /api/v1/agents/{agent_id}
    Then AgentService.get_agent() is invoked and 200 is returned with AgentDetail
  - Given POST /api/v1/agents/{agent_id}/invoke
    Then AgentService.invoke() is invoked and 200 is returned with AgentInvocationResult
  - Given GET /api/v1/agents/{agent_id}/health
    Then AgentService.health_check() is invoked and 200 is returned with AgentHealth
  - Given POST /api/v1/agents/{agent_id}/promote
    Then AgentService.promote_version() is invoked
  - Given POST /api/v1/agents/{agent_id}/rollback
    Then AgentService.rollback_version() is invoked
  - Given PUT /api/v1/agents/{agent_id}/canary
    Then AgentService.set_canary() is invoked
  - Given GET /api/v1/agents/{agent_id}/maturity
    Then AgentService.get_maturity() is invoked
depends_on: [S-042, S-013, S-014]
definition_of_done:
  - [ ] src/rest_api/routes/agents.py with 8 endpoint handlers
  - [ ] OpenAPI schema annotations
  - [ ] Integration tests for each endpoint
  - [ ] Response parity with MCP agent tools (Q-049)
```

---

### S-045: REST Cost + Budget Routes

```yaml
id: S-045
title: REST cost and budget routes — report, budget check, anomalies, thresholds
feature: F-014, F-015, F-016, F-017, F-018
sprint: 4
story_points: 3
layer: rest
interaction_ids: [I-040, I-041, I-048, I-049]
mcp_tools: []
dashboard_screens: []
shared_service: CostService
acceptance_criteria:
  - Given GET /api/v1/costs/report?scope=fleet&period=7d
    Then CostService.get_report() is invoked and 200 is returned with CostReport
  - Given GET /api/v1/costs/budget?scope=project&project_id=X
    Then CostService.check_budget() is invoked and 200 is returned with BudgetStatus
  - Given GET /api/v1/costs/anomalies
    Then CostService.get_anomalies() is invoked and 200 is returned
  - Given PUT /api/v1/costs/thresholds
    Then CostService.set_threshold() is invoked and 200 is returned
depends_on: [S-042, S-015, S-016]
definition_of_done:
  - [ ] src/rest_api/routes/costs.py with 4 endpoint handlers
  - [ ] OpenAPI schema annotations
  - [ ] Integration tests
  - [ ] Response parity with MCP governance tools
```

---

### S-046: REST Audit Routes

```yaml
id: S-046
title: REST audit routes — query events, get summary, export report
feature: F-019, F-020, F-021
sprint: 4
story_points: 3
layer: rest
interaction_ids: [I-042, I-043, I-044]
mcp_tools: []
dashboard_screens: []
shared_service: AuditService
acceptance_criteria:
  - Given GET /api/v1/audit/events with filter query params
    Then AuditService.query_events() is invoked and 200 is returned with AuditEvent[]
  - Given GET /api/v1/audit/summary?period=7d
    Then AuditService.get_summary() is invoked and 200 is returned with AuditSummary
  - Given POST /api/v1/audit/export?format=csv
    Then AuditService.export_report() is invoked and the report is returned as a downloadable file
  - Given format=pdf
    Then a PDF audit report is generated and returned
depends_on: [S-042, S-018, S-019]
definition_of_done:
  - [ ] src/rest_api/routes/audit.py with 3 endpoint handlers
  - [ ] CSV and PDF export support
  - [ ] OpenAPI schema annotations
  - [ ] Integration tests
```

---

### S-047: REST Approval Routes

```yaml
id: S-047
title: REST approval routes — list pending, approve, reject
feature: F-024, F-025, F-026
sprint: 4
story_points: 3
layer: rest
interaction_ids: [I-045, I-046, I-047]
mcp_tools: []
dashboard_screens: []
shared_service: ApprovalService
acceptance_criteria:
  - Given GET /api/v1/approvals?status=pending
    Then ApprovalService.list_pending() is invoked and 200 is returned with ApprovalRequest[]
  - Given POST /api/v1/approvals/{request_id}/approve
    Then ApprovalService.approve() is invoked and 200 is returned with ApprovalResult
  - Given POST /api/v1/approvals/{request_id}/reject with mandatory comment
    Then ApprovalService.reject() is invoked and 200 is returned with ApprovalResult
  - Given a reject without comment
    Then 422 is returned with validation error
depends_on: [S-042, S-020, S-021, S-022, S-023]
definition_of_done:
  - [ ] src/rest_api/routes/approvals.py with 3 endpoint handlers
  - [ ] Mandatory comment validation for reject
  - [ ] OpenAPI schema annotations
  - [ ] Integration tests
```

---

### S-048: REST Knowledge Routes

```yaml
id: S-048
title: REST knowledge routes — search, create, promote, list exceptions
feature: F-029, F-030, F-031, F-032
sprint: 4
story_points: 3
layer: rest
interaction_ids: [I-060, I-061, I-062, I-063]
mcp_tools: []
dashboard_screens: []
shared_service: KnowledgeService
acceptance_criteria:
  - Given GET /api/v1/knowledge/exceptions?q=typescript&tier=universal
    Then KnowledgeService.search() is invoked and 200 is returned with KnowledgeException[]
  - Given POST /api/v1/knowledge/exceptions
    Then KnowledgeService.create_exception() is invoked and 201 is returned
  - Given POST /api/v1/knowledge/exceptions/{id}/promote
    Then KnowledgeService.promote() is invoked and 200 is returned
  - Given GET /api/v1/knowledge/exceptions?tier=stack
    Then KnowledgeService.list_by_tier() is invoked and 200 is returned
depends_on: [S-042, S-026, S-027, S-028]
definition_of_done:
  - [ ] src/rest_api/routes/knowledge.py with 4 endpoint handlers
  - [ ] OpenAPI schema annotations
  - [ ] Integration tests
  - [ ] Response parity with MCP knowledge tools
```

---

### S-049: REST System Routes + Auth Routes

```yaml
id: S-049
title: REST system routes (health, MCP status, MCP calls) and auth routes (login, token refresh)
feature: F-054, F-045, F-022
sprint: 4
story_points: 3
layer: rest
interaction_ids: [I-080, I-081, I-082]
mcp_tools: []
dashboard_screens: []
shared_service: HealthService, AuditService
acceptance_criteria:
  - Given GET /api/v1/system/health
    Then HealthService.get_fleet_health() is invoked and 200 is returned with FleetHealth
  - Given GET /api/v1/system/mcp/status
    Then HealthService.get_mcp_status() is invoked and 200 is returned with McpServerStatus[]
  - Given GET /api/v1/system/mcp/calls?limit=50
    Then AuditService.list_mcp_calls() is invoked and 200 is returned with McpCallEvent[]
  - Given POST /api/v1/auth/login with valid credentials
    Then a JWT token is returned
  - Given POST /api/v1/auth/refresh with a valid refresh token
    Then a new access token is returned
depends_on: [S-042, S-029]
definition_of_done:
  - [ ] src/rest_api/routes/system.py and src/rest_api/routes/auth.py
  - [ ] JWT token generation and validation
  - [ ] OpenAPI schema annotations
  - [ ] Integration tests for health, MCP status, auth flow
```

---

### S-050: Dashboard Scaffold (Streamlit, Navigation, Auth)

```yaml
id: S-050
title: Dashboard scaffold — Streamlit app with navigation sidebar, auth, and shared components
feature: F-040
sprint: 4
story_points: 5
layer: dashboard
interaction_ids: []
mcp_tools: []
dashboard_screens: [Navigation Sidebar, Login Page]
shared_service: N/A
acceptance_criteria:
  - Given a user navigates to the dashboard URL
    When they are not authenticated
    Then the login page is shown
  - Given a valid login
    When authentication succeeds
    Then the sidebar navigation appears with pages: Fleet Health, Cost Monitor, Pipeline Runs, Audit Log, Approval Queue
  - Given the navigation sidebar
    Then each page link shows an icon and label, with active page highlighted
  - Given the dashboard scaffold
    Then shared components are available: MetricCard, StatusBadge, DataTable, LoadingSkeleton, ErrorBanner
  - Given any page load
    Then skeleton loading states appear within 200ms while data fetches
  - Given the dashboard
    Then it calls REST API endpoints (not shared services directly) for all data
depends_on: [S-042, S-007]
definition_of_done:
  - [ ] src/dashboard/app.py with Streamlit multipage app
  - [ ] Login page with session token management
  - [ ] Navigation sidebar with 5 page links
  - [ ] Shared component library in src/dashboard/components/
  - [ ] Custom CSS for consistent styling
  - [ ] Page load under 2s (Q-005)
```

---

### S-051: Dashboard Fleet Health Page

```yaml
id: S-051
title: Dashboard Fleet Health page — agent grid, health badges, MCP monitoring panel
feature: F-040
sprint: 4
story_points: 8
layer: dashboard
interaction_ids: [I-020, I-021, I-023, I-080, I-081, I-082]
mcp_tools: []
dashboard_screens: [Fleet Health Overview, Agent Grid, Agent Detail Panel, Health Badges, MCP Monitoring Panel]
shared_service: HealthService, AgentService
acceptance_criteria:
  - Given a user navigates to Fleet Health
    When the page loads
    Then a summary bar shows: total agents, healthy, degraded, offline counts as MetricCards
  - Given the summary bar
    When agents are in different states
    Then MetricCards use color-coded StatusBadges (green/yellow/red)
  - Given the agent grid
    Then all 48 agents are displayed as cards grouped by SDLC phase (1-7)
  - Given an agent card
    When clicked
    Then an Agent Detail Panel slides in showing: config, metrics, version slots, prompt hash
  - Given each agent card
    Then a health badge shows the agent's current health status
  - Given the MCP Monitoring Panel
    Then it shows: connected MCP clients, recent tool invocations feed, server status for all 3 servers
  - Given the page
    Then it loads within 1 second (Q-006) using cached summary data
depends_on: [S-050, S-049]
definition_of_done:
  - [ ] src/dashboard/pages/fleet_health.py
  - [ ] Agent grid with phase grouping
  - [ ] Agent detail slide-in panel
  - [ ] Health badges with color coding
  - [ ] MCP monitoring panel with call feed
  - [ ] Page load < 1s from cached data (Q-006)
  - [ ] WCAG 2.1 AA compliance (Q-029)
```

---

## 9. Sprint 5: Dashboard Pages

**Theme:** Remaining dashboard pages — Cost, Pipeline, Audit, Approval, MCP
**Capacity:** 34 points | 2 weeks
**Goal:** All 6 dashboard pages complete and functional

---

### S-052: Dashboard Cost Monitor Page

```yaml
id: S-052
title: Dashboard Cost Monitor page — cost charts, budget gauges, anomaly alerts
feature: F-041
sprint: 5
story_points: 8
layer: dashboard
interaction_ids: [I-040, I-041, I-048, I-049]
mcp_tools: []
dashboard_screens: [Cost Charts, Budget Gauges, Anomaly Alerts, Budget Settings]
shared_service: CostService
acceptance_criteria:
  - Given a user navigates to Cost Monitor
    When the page loads
    Then a summary bar shows: total spend, budget utilization %, active anomalies count
  - Given the Cost Charts section
    Then Plotly charts display: daily spend trend (line), spend by phase (bar), spend by agent (treemap)
  - Given the Budget Gauges section
    Then circular gauges show fleet/project budget utilization with color: green (<60%), yellow (60-80%), red (>80%)
  - Given a gauge shows red
    When clicked
    Then it drills down to show which agents are driving the overspend
  - Given the Anomaly Alerts section
    Then active cost anomalies are listed with: agent, spike amount, detected_at, investigation link
  - Given the Budget Settings section
    Then fleet and project budget limits can be configured via form inputs
  - Given period selector (1d/7d/30d/90d)
    When changed
    Then all charts and gauges update to reflect the selected period
depends_on: [S-050, S-045]
definition_of_done:
  - [ ] src/dashboard/pages/cost_monitor.py
  - [ ] Plotly charts: line, bar, treemap
  - [ ] Budget gauge components
  - [ ] Anomaly alert list with investigation links
  - [ ] Budget settings form
  - [ ] Period selector with reactive updates
  - [ ] Page load < 2s (Q-005)
```

---

### S-053: Dashboard Pipeline Runs Page

```yaml
id: S-053
title: Dashboard Pipeline Runs page — trigger form, runs table, run detail with step progress
feature: F-042
sprint: 5
story_points: 8
layer: dashboard
interaction_ids: [I-001, I-002, I-003, I-004, I-005, I-006, I-007, I-008, I-009]
mcp_tools: []
dashboard_screens: [Pipeline Trigger Form, Pipeline Runs Table, Pipeline Status Card, Document Viewer, Config Panel]
shared_service: PipelineService
acceptance_criteria:
  - Given a user navigates to Pipeline Runs
    When the page loads
    Then a summary bar shows: active runs, completed today, failed today, avg duration
  - Given the Pipeline Trigger Form
    When a user enters a project brief and clicks "Start Run"
    Then POST /api/v1/pipelines is called and the user navigates to the run detail view
  - Given the Pipeline Runs Table
    Then all runs are listed with: run_id, project, status badge, progress %, started_at, duration
  - Given status filter tabs (All/Running/Completed/Failed)
    When a tab is selected
    Then the table filters to show only matching runs
  - Given a run row is clicked
    Then a run detail view shows: step-by-step progress, current step highlighted, resume/cancel buttons for eligible runs
  - Given a completed run
    When "View Documents" is clicked
    Then generated documents are shown in a Document Viewer panel
  - Given running pipelines
    Then the page polls for status updates every 5 seconds via REST API
depends_on: [S-050, S-043]
definition_of_done:
  - [ ] src/dashboard/pages/pipeline_runs.py
  - [ ] Trigger form with brief input and validation
  - [ ] Runs table with status badges and filters
  - [ ] Run detail view with step progress visualization
  - [ ] Document viewer panel
  - [ ] Resume/cancel action buttons
  - [ ] Auto-polling for active runs
  - [ ] Page load < 2s (Q-005)
```

---

### S-054: Dashboard Audit Log Page

```yaml
id: S-054
title: Dashboard Audit Log page — events table, summary cards, export functionality
feature: F-043
sprint: 5
story_points: 5
layer: dashboard
interaction_ids: [I-042, I-043, I-044]
mcp_tools: []
dashboard_screens: [Event Table, Summary Cards, Export Button]
shared_service: AuditService
acceptance_criteria:
  - Given a user navigates to Audit Log
    When the page loads
    Then summary cards show: total events, errors, warnings, info for the selected period
  - Given the Event Table
    Then events are listed with: timestamp, event_type, agent, severity badge, message (truncated)
  - Given the Event Table
    Then it supports filtering by: severity, agent, event_type, date range
  - Given a table row
    When clicked
    Then the full event detail is shown in an expandable section with metadata JSONB
  - Given the Export Button
    When "Export CSV" is clicked
    Then a CSV file of the filtered events is downloaded
  - Given the Export Button
    When "Export PDF" is clicked
    Then a formatted PDF audit report is downloaded
  - Given the page
    Then pagination supports 50/100/200 rows per page
depends_on: [S-050, S-046]
definition_of_done:
  - [ ] src/dashboard/pages/audit_log.py
  - [ ] Summary cards with period selector
  - [ ] Event table with filters and expandable rows
  - [ ] CSV and PDF export functionality
  - [ ] Pagination controls
  - [ ] Page load < 2s (Q-005)
```

---

### S-055: Dashboard Approval Queue Page

```yaml
id: S-055
title: Dashboard Approval Queue page — pending list, approve/reject with comment, SLA countdown
feature: F-044
sprint: 5
story_points: 8
layer: dashboard
interaction_ids: [I-045, I-046, I-047]
mcp_tools: []
dashboard_screens: [Approval Queue Table, Approve Button, Reject Button + Comment Field]
shared_service: ApprovalService
acceptance_criteria:
  - Given a user navigates to Approval Queue
    When the page loads
    Then a summary bar shows: pending count, overdue count, approved today, rejected today
  - Given the Approval Queue Table
    Then pending approvals are listed with: pipeline name, step, gate_type badge, requested_at, SLA countdown timer, requested_by
  - Given an overdue approval
    Then the SLA countdown shows negative time in red with a warning icon
  - Given an approval row is selected
    Then the full pipeline context is shown: run status, completed steps, requesting agent, step outputs
  - Given the Approve button
    When clicked with an optional comment
    Then POST /api/v1/approvals/{id}/approve is called and the approval is removed from the pending list
  - Given the Reject button
    When clicked
    Then a comment field is required before submission
  - Given an empty reject comment
    Then the submit button is disabled with a tooltip "Comment required for rejection"
  - Given the page
    Then it polls for new approvals every 10 seconds
depends_on: [S-050, S-047]
definition_of_done:
  - [ ] src/dashboard/pages/approval_queue.py
  - [ ] Pending list with SLA countdown timers
  - [ ] Pipeline context detail panel
  - [ ] Approve action with optional comment
  - [ ] Reject action with mandatory comment
  - [ ] Auto-polling for new approvals
  - [ ] Page load < 2s (Q-005)
```

---

### S-056: Dashboard MCP Monitoring Panel (Standalone)

```yaml
id: S-056
title: Dashboard MCP Monitoring Panel — connected clients, tool call feed, server health
feature: F-045
sprint: 5
story_points: 5
layer: dashboard
interaction_ids: [I-081, I-082]
mcp_tools: []
dashboard_screens: [MCP Panel, MCP Call Feed]
shared_service: HealthService, AuditService
acceptance_criteria:
  - Given the MCP Monitoring Panel (embedded in Fleet Health, also standalone)
    When rendered
    Then it shows: server status for agents (3100), governance (3101), knowledge (3102) with uptime and tool counts
  - Given the connected clients section
    Then it shows: client_id, connected_since, tools_called_count, last_tool_called
  - Given the MCP Call Feed
    Then recent tool invocations are listed: timestamp, tool_name, server, client_id, duration_ms, status badge
  - Given the call feed
    Then it auto-refreshes every 5 seconds with new calls appearing at the top
  - Given a call feed entry
    When clicked
    Then the full call detail is shown: input parameters (hashed), output summary, error message if failed
depends_on: [S-051, S-049]
definition_of_done:
  - [ ] MCP monitoring panel component in src/dashboard/components/mcp_panel.py
  - [ ] Server health status indicators
  - [ ] Connected clients list
  - [ ] Real-time call feed
  - [ ] Call detail expansion
```

---

## 10. Sprint 6: Cross-Interface Integration

**Theme:** Interface parity verification and cross-interface journey testing
**Capacity:** 41 points | 2 weeks
**Goal:** MCP, REST, and Dashboard are provably consistent; real-time channels operational

---

### S-057: Interface Parity Tests (MCP vs REST for All 34 Interactions)

```yaml
id: S-057
title: Parity tests — verify MCP and REST return identical responses for all 34 interactions
feature: F-049
sprint: 6
story_points: 8
layer: integration
interaction_ids: [I-001 through I-082]
mcp_tools: [all 35 tools]
dashboard_screens: []
shared_service: All services
acceptance_criteria:
  - Given each of the 34 interactions in the INTERACTION-MAP
    When the interaction is triggered via MCP tool AND via REST endpoint
    Then the response data shapes are identical (field names, types, nesting)
  - Given trigger_pipeline via MCP and POST /api/v1/pipelines via REST
    When both return a PipelineRun
    Then every field matches (run_id format, status values, step structure)
  - Given list_agents via MCP and GET /api/v1/agents via REST
    When both return AgentSummary[]
    Then the array contents are identical when called at the same point in time
  - Given any write operation via MCP
    When the same operation is queried via REST
    Then the state change is immediately visible (Q-049: interface parity)
  - Given the full test suite
    Then parity is verified for: field names (Q-049), error codes (Q-051), pagination (Q-053)
depends_on: [S-032, S-033, S-035, S-036, S-038, S-043, S-044, S-045, S-046, S-047, S-048]
definition_of_done:
  - [ ] tests/integration/test_parity.py with 34 test cases
  - [ ] Each test calls MCP and REST for the same interaction and asserts shape equality
  - [ ] Error code parity tests (MCP error codes map to HTTP status codes)
  - [ ] Pagination parity tests (limit/offset produce same results)
  - [ ] CI runs parity tests on every PR
```

---

### S-058: Cross-Interface Journey — Pipeline with Approval Gate

```yaml
id: S-058
title: Journey test — pipeline triggered via MCP, approval via Dashboard, result via REST
feature: F-001, F-023, F-025
sprint: 6
story_points: 5
layer: integration
interaction_ids: [I-001, I-045, I-046, I-002]
mcp_tools: [trigger_pipeline, list_pending_approvals, approve_gate, get_pipeline_status]
dashboard_screens: [Approval Queue Table, Pipeline Status Card]
shared_service: PipelineService, ApprovalService
acceptance_criteria:
  - Given Priya triggers a pipeline via MCP (trigger_pipeline)
    When the pipeline reaches a quality gate
    Then an approval request appears in the Approval Queue dashboard page
  - Given Anika views the Approval Queue on the dashboard
    Then she sees the full pipeline context: run_id, step, requesting agent, outputs so far
  - Given Anika approves the gate via the Dashboard Approve button
    When the approval is processed
    Then the pipeline resumes and Priya can see the updated status via MCP (get_pipeline_status)
  - Given the full journey
    Then all state changes are reflected consistently across MCP, REST, and Dashboard within 2 seconds
  - Given the journey audit trail
    Then events show: triggered_by=mcp, approved_by=dashboard with correct user attribution
depends_on: [S-057]
definition_of_done:
  - [ ] tests/integration/test_journey_pipeline_approval.py
  - [ ] End-to-end test covering MCP trigger -> Dashboard approval -> MCP status check
  - [ ] Timing assertions (state visible within 2s)
  - [ ] Audit trail verification
```

---

### S-059: Cross-Interface Journey — Cost Spike Investigation

```yaml
id: S-059
title: Journey test — cost anomaly detected, investigated via Dashboard, resolved via MCP
feature: F-017, F-014
sprint: 6
story_points: 5
layer: integration
interaction_ids: [I-048, I-040, I-025]
mcp_tools: [get_cost_anomalies, get_cost_report, rollback_agent_version]
dashboard_screens: [Anomaly Alerts, Cost Charts, Agent Detail Panel]
shared_service: CostService, AgentService
acceptance_criteria:
  - Given a cost anomaly is detected for agent X
    When David views the Cost Monitor dashboard
    Then the anomaly appears in the Anomaly Alerts section with agent name and spike amount
  - Given David clicks the investigation link
    Then the Cost Charts drill down to show agent X's cost trend
  - Given David determines the cause is a bad agent version
    When Jason rollbacks the agent via MCP (rollback_agent_version)
    Then the agent version reverts and the anomaly is flagged as "mitigated"
  - Given the full journey
    Then the dashboard reflects the rollback within 2 seconds of the MCP action
depends_on: [S-057]
definition_of_done:
  - [ ] tests/integration/test_journey_cost_investigation.py
  - [ ] End-to-end test covering anomaly detection -> Dashboard investigation -> MCP rollback
  - [ ] Cross-interface state consistency assertions
```

---

### S-060: Cross-Interface Journey — Canary Deployment

```yaml
id: S-060
title: Journey test — canary deployment promoted via MCP, monitored via Dashboard
feature: F-012
sprint: 6
story_points: 5
layer: integration
interaction_ids: [I-026, I-023, I-024]
mcp_tools: [set_canary_traffic, check_agent_health, promote_agent_version]
dashboard_screens: [Agent Detail Panel, Health Badges, Version Management]
shared_service: AgentService
acceptance_criteria:
  - Given a new agent version is deployed as canary
    When Jason sets canary traffic to 10% via MCP (set_canary_traffic)
    Then the Dashboard Fleet Health page shows the canary badge on the agent
  - Given canary traffic is active
    When David monitors health via Dashboard Health Badges
    Then canary and production health metrics are shown side by side
  - Given canary metrics are healthy after monitoring period
    When Jason promotes the version via MCP (promote_agent_version)
    Then the Dashboard updates to show the new active version and canary is cleared
  - Given the full journey
    Then version history is preserved and auditable
depends_on: [S-057]
definition_of_done:
  - [ ] tests/integration/test_journey_canary_deployment.py
  - [ ] End-to-end test covering set canary -> monitor -> promote
  - [ ] Dashboard state reflects MCP changes within 2 seconds
```

---

### S-061: Cross-Interface Journey — Compliance Audit Export

```yaml
id: S-061
title: Journey test — audit events queried via MCP, exported via Dashboard for compliance
feature: F-021, F-019
sprint: 6
story_points: 5
layer: integration
interaction_ids: [I-042, I-043, I-044]
mcp_tools: [query_audit_events, get_audit_summary]
dashboard_screens: [Event Table, Summary Cards, Export Button]
shared_service: AuditService
acceptance_criteria:
  - Given Fatima queries audit events for the past 30 days via MCP (query_audit_events)
    Then she receives the same events that appear on the Dashboard Audit Log page
  - Given Fatima views the Dashboard Audit Log
    When she applies the same filters (severity=error, period=30d)
    Then the results match the MCP query exactly (parity)
  - Given Fatima clicks "Export PDF" on the Dashboard
    Then a formatted audit report is generated with: summary statistics, event timeline, severity distribution
  - Given the exported report
    Then it includes a compliance attestation section with generation timestamp and filter criteria
depends_on: [S-057]
definition_of_done:
  - [ ] tests/integration/test_journey_compliance_export.py
  - [ ] Parity assertion between MCP query and Dashboard display
  - [ ] PDF export verification
  - [ ] Compliance attestation section in report
```

---

### S-062: WebSocket Channels (Pipeline Progress, MCP Feed, Approvals)

```yaml
id: S-062
title: WebSocket channels for real-time updates — pipeline progress, MCP call feed, approval notifications
feature: F-040, F-044, F-045
sprint: 6
story_points: 8
layer: integration
interaction_ids: [I-002, I-045, I-082]
mcp_tools: []
dashboard_screens: [Pipeline Status Card, Approval Queue Table, MCP Call Feed]
shared_service: N/A
acceptance_criteria:
  - Given a WebSocket connection to /ws/pipelines/{run_id}
    When a pipeline step completes
    Then a status update is pushed to connected clients within 500ms
  - Given a WebSocket connection to /ws/approvals
    When a new approval request is created
    Then a notification is pushed to connected clients
  - Given a WebSocket connection to /ws/mcp/calls
    When an MCP tool is invoked
    Then the call event is pushed to the live feed
  - Given the dashboard
    Then it connects to WebSocket channels for real-time updates instead of polling
  - Given a WebSocket disconnection
    Then the dashboard falls back to polling and shows a "Reconnecting..." indicator
depends_on: [S-051, S-053, S-055, S-056]
definition_of_done:
  - [ ] WebSocket server alongside REST API on port 8080
  - [ ] Three channels: pipeline progress, approvals, MCP calls
  - [ ] Dashboard updated to use WebSocket with polling fallback
  - [ ] Connection management (heartbeat, reconnect)
  - [ ] Integration tests for publish/subscribe
```

---

### S-063: Slack Notification Integration

```yaml
id: S-063
title: Slack notifications — approval gates, cost alerts, pipeline failures
feature: F-044, F-017
sprint: 6
story_points: 5
layer: integration
interaction_ids: [I-045, I-048]
mcp_tools: []
dashboard_screens: []
shared_service: NotificationService
acceptance_criteria:
  - Given an approval request is created
    When the SLA deadline is within 1 hour
    Then a Slack notification is sent to the configured approval channel with: run_id, step, gate_type, SLA countdown, deep link to Dashboard
  - Given a cost anomaly is detected
    Then a Slack alert is sent to the cost monitoring channel with: agent, amount, threshold, deep link to Cost Monitor
  - Given a pipeline fails after all retries
    Then a Slack notification is sent with: run_id, failed step, error summary, deep link to Pipeline Runs
  - Given Slack integration is disabled (no webhook URL configured)
    Then notifications are silently skipped without errors
  - Given Slack is unreachable
    Then the failure is logged but does not block the triggering operation
depends_on: [S-020, S-015]
definition_of_done:
  - [ ] NotificationService class in src/services/notification_service.py
  - [ ] Slack webhook integration with rich message formatting
  - [ ] Deep link generation to Dashboard pages
  - [ ] Graceful degradation when Slack is unavailable
  - [ ] Unit tests with mocked Slack webhook
```

---

## 11. Sprint 7: Advanced Features

**Theme:** Advanced pipeline execution, agent versioning, quality scoring
**Capacity:** 41 points | 2 weeks
**Goal:** DAG execution, self-healing, version management, and knowledge injection

---

### S-064: Agent Version Management (Promote/Rollback/Canary)

```yaml
id: S-064
title: Agent version management — promote, rollback, canary traffic split implementation
feature: F-012
sprint: 7
story_points: 8
layer: service
interaction_ids: [I-024, I-025, I-026]
mcp_tools: [promote_agent_version, rollback_agent_version, set_canary_traffic]
dashboard_screens: [Version Management]
shared_service: AgentService
acceptance_criteria:
  - Given an agent with active_version=v1 and canary_version=v2
    When AgentService.set_canary(agent_id, traffic_pct=10) is called
    Then 10% of invocations route to v2 and 90% to v1
  - Given canary traffic is set to 10%
    When AgentService.promote_version(agent_id) is called
    Then active_version becomes v2, canary_version is cleared, canary_traffic_pct=0
  - Given an active_version=v2 with rollback_version=v1
    When AgentService.rollback_version(agent_id) is called
    Then active_version reverts to v1 and an audit event is emitted
  - Given traffic splitting
    Then the routing decision is recorded per invocation for A/B analysis
  - Given any version change
    Then an audit event is emitted with: old_version, new_version, action (promote/rollback/canary)
depends_on: [S-013, S-014, S-006]
definition_of_done:
  - [ ] promote_version(), rollback_version(), set_canary() methods on AgentService
  - [ ] Traffic splitting logic with random routing
  - [ ] Audit event emission for all version changes
  - [ ] Unit tests for promote/rollback/canary/edge cases
  - [ ] Integration tests with MCP and REST
```

---

### S-065: Pipeline Parallel DAG Execution

```yaml
id: S-065
title: Pipeline DAG execution — independent phases run in parallel with dependency resolution
feature: F-006
sprint: 7
story_points: 8
layer: service
interaction_ids: [I-001]
mcp_tools: [trigger_pipeline]
dashboard_screens: [Pipeline Status Card]
shared_service: PipelineService
acceptance_criteria:
  - Given a pipeline with phases: ROADMAP (independent), PRD (depends on ROADMAP), ARCH + QUALITY (independent of each other, depend on PRD)
    When the pipeline executes
    Then ARCH and QUALITY run concurrently after PRD completes
  - Given MAX_PARALLEL_PHASES=3
    When 4 independent phases are eligible
    Then at most 3 execute concurrently and the 4th waits
  - Given a pipeline DAG with a cycle (A -> B -> A)
    When the pipeline is validated at startup
    Then a ConfigurationError is raised
  - Given parallel execution
    Then total duration is less than sequential sum when parallelism is possible
  - Given the DAG execution
    Then each phase completion triggers dependency resolution and starts newly eligible phases
depends_on: [S-010, S-024]
definition_of_done:
  - [ ] DAG executor in src/services/pipeline_dag.py
  - [ ] Topological sort with cycle detection
  - [ ] Concurrent phase execution with configurable max parallelism
  - [ ] Phase completion triggers dependency resolution
  - [ ] Unit tests with various DAG shapes (linear, diamond, wide)
```

---

### S-066: Pipeline Self-Healing on Test Failure

```yaml
id: S-066
title: Pipeline self-healing — auto-retry failed agents with enriched context from failure
feature: F-007
sprint: 7
story_points: 5
layer: service
interaction_ids: [I-007]
mcp_tools: [retry_pipeline_step]
dashboard_screens: []
shared_service: PipelineService
acceptance_criteria:
  - Given an agent invocation fails during a pipeline step
    When auto-retry is enabled (default)
    Then the agent is re-invoked with the failure message and stack trace appended to the prompt
  - Given AGENT_MAX_RETRIES=2 (configurable)
    When a step fails
    Then it is retried up to 2 times with progressively enriched context
  - Given each retry attempt
    Then a separate audit event is emitted with retry_count and failure reason
  - Given all retries are exhausted
    Then the pipeline transitions to 'failed' with an aggregated error containing all retry attempts
  - Given self-healing is active
    Then per-agent budget is checked before each retry; budget exceeded skips retry and fails
depends_on: [S-010, S-017]
definition_of_done:
  - [ ] Self-healing retry logic in PipelineService
  - [ ] Context enrichment with failure details
  - [ ] Budget guard per retry
  - [ ] Audit events for each retry attempt
  - [ ] Unit tests for: success on retry 1, success on retry 2, all retries fail, budget exceeded
```

---

### S-067: Pipeline Checkpoint/Resume

```yaml
id: S-067
title: Pipeline checkpoint — save intermediate state after each step for resume-from-failure
feature: F-004
sprint: 7
story_points: 5
layer: service
interaction_ids: [I-004]
mcp_tools: [resume_pipeline]
dashboard_screens: [Resume Button]
shared_service: PipelineService
acceptance_criteria:
  - Given a pipeline step completes successfully
    When the step finalizes
    Then a checkpoint record is saved with: step_index, step_name, output state (JSONB), artifact path
  - Given a pipeline fails at step 7
    When PipelineService.resume() is called
    Then checkpoints for steps 0-6 are loaded and execution begins at step 7
  - Given checkpoint data
    Then it includes sufficient state to recreate the step's output without re-executing
  - Given checkpoint storage
    Then artifacts are stored on disk (or S3) and referenced by path in the checkpoint record
  - Given old checkpoints (> 30 days)
    Then a cleanup job deletes them to prevent storage bloat
depends_on: [S-005, S-024]
definition_of_done:
  - [ ] Checkpoint save logic after each successful step
  - [ ] Checkpoint load logic for resume
  - [ ] Artifact storage (local filesystem or S3-compatible)
  - [ ] Cleanup job for old checkpoints
  - [ ] Unit tests for save/load/resume/cleanup
```

---

### S-068: Quality Scoring per Agent Output

```yaml
id: S-068
title: Quality scoring — automated quality assessment for each agent-generated document
feature: F-046, F-047
sprint: 7
story_points: 5
layer: service
interaction_ids: [I-006]
mcp_tools: [get_pipeline_documents]
dashboard_screens: [Document Viewer]
shared_service: QualityService
acceptance_criteria:
  - Given an agent produces a document during a pipeline run
    When the document is finalized
    Then QualityService.score(document) is called and a quality_score (0-100) is computed
  - Given the quality scoring
    Then it evaluates: completeness (required sections present), consistency (cross-document references valid), format compliance (markdown structure), content depth (word count thresholds)
  - Given a quality score below the configured threshold (default 70)
    Then the pipeline step is flagged and self-healing retry is triggered
  - Given quality scores
    Then they are stored on the pipeline_steps record and visible via get_pipeline_documents
  - Given quality metrics
    Then they are aggregated by agent for maturity scoring (F-013)
depends_on: [S-010]
definition_of_done:
  - [ ] QualityService class in src/services/quality_service.py
  - [ ] Scoring algorithm with configurable weights
  - [ ] Integration with pipeline step finalization
  - [ ] Score persistence on pipeline_steps
  - [ ] Unit tests with sample documents at various quality levels
```

---

### S-069: Exception Auto-Injection into Prompts

```yaml
id: S-069
title: Exception auto-injection — automatically inject relevant knowledge exceptions into agent prompts
feature: F-033
sprint: 7
story_points: 5
layer: service
interaction_ids: [I-060, I-063]
mcp_tools: [search_exceptions, list_exceptions]
dashboard_screens: []
shared_service: KnowledgeService, AgentService
acceptance_criteria:
  - Given an agent is about to be invoked for a pipeline step
    When the prompt is being constructed
    Then KnowledgeService.search() is called with the step context to find relevant exceptions
  - Given matching exceptions exist
    Then they are injected into the agent's prompt as an "Exceptions" section with: rule_pattern, exception_text, tier
  - Given tier priority
    Then universal exceptions are injected first, then stack, then client
  - Given the injection
    Then a maximum of 10 exceptions are injected to avoid prompt bloat
  - Given no matching exceptions
    Then the agent prompt is unmodified
depends_on: [S-026, S-010]
definition_of_done:
  - [ ] Exception injection logic in AgentService.invoke()
  - [ ] KnowledgeService.search() integration with step context
  - [ ] Tier-priority ordering
  - [ ] Max injection limit (configurable, default 10)
  - [ ] Unit tests for: matching/no-matching/tier-ordering/limit
```

---

### S-070: Cost Anomaly Detection + Alerting

```yaml
id: S-070
title: Cost anomaly detection — identify cost spikes and trigger alerts
feature: F-017
sprint: 7
story_points: 5
layer: service
interaction_ids: [I-048]
mcp_tools: [get_cost_anomalies]
dashboard_screens: [Anomaly Alerts]
shared_service: CostService
acceptance_criteria:
  - Given historical cost data for an agent
    When the agent's cost for the current period exceeds 2x the rolling average
    Then a CostAnomaly record is created with: agent_id, expected_cost, actual_cost, spike_factor
  - Given anomaly detection
    Then it runs on every record_spend() call (inline) and as a periodic background check (every 15 minutes)
  - Given an anomaly is detected
    Then NotificationService is called to send Slack alerts
  - Given get_cost_anomalies is called
    Then all active (unresolved) anomalies are returned sorted by spike_factor descending
  - Given an anomaly
    When the underlying cause is resolved (agent rollback, budget adjustment)
    Then the anomaly can be marked as 'mitigated' with a resolution note
depends_on: [S-017, S-063]
definition_of_done:
  - [ ] Anomaly detection algorithm (rolling average + threshold)
  - [ ] Inline detection on record_spend()
  - [ ] Background periodic detection job
  - [ ] Notification integration
  - [ ] Unit tests for: spike detection, no-spike, mitigation
```

---

## 12. Sprint 8: Polish + Hardening

**Theme:** Observability, performance, security, CI/CD, and documentation
**Capacity:** 41 points | 2 weeks
**Goal:** Production-ready platform with full observability and security hardening

---

### S-071: Structured Logging (structlog JSON)

```yaml
id: S-071
title: Structured logging — structlog JSON output across all layers with correlation IDs
feature: F-055
sprint: 8
story_points: 5
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: All services
acceptance_criteria:
  - Given any service method call
    When a log is emitted
    Then it is in JSON format via structlog with fields: timestamp, level, message, service, correlation_id, project_id
  - Given an MCP tool call
    Then the log includes: tool_name, server_name, client_id, duration_ms
  - Given a REST API request
    Then the log includes: method, path, status_code, duration_ms, request_id
  - Given a correlation_id
    Then it propagates from the entry point (MCP or REST) through service calls to database queries
  - Given log output
    Then it is parseable by ELK/Loki for centralized log aggregation
depends_on: [S-007]
definition_of_done:
  - [ ] structlog configuration in src/logging.py
  - [ ] JSON processor chain: add timestamp, correlation_id, service context
  - [ ] Integration with all services, MCP servers, and REST API
  - [ ] Correlation ID propagation via contextvars
  - [ ] Unit test verifying log output format
```

---

### S-072: OpenTelemetry Instrumentation

```yaml
id: S-072
title: OpenTelemetry tracing — trace ID propagation across MCP -> service -> database
feature: F-055
sprint: 8
story_points: 8
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: All services
acceptance_criteria:
  - Given an MCP tool call
    When it triggers service methods which query the database
    Then a single trace spans all three layers with parent-child relationships
  - Given a REST API request
    Then the same trace spans API -> service -> database
  - Given the dashboard fetches data via REST
    Then the trace includes the dashboard request as the root span
  - Given OpenTelemetry export
    Then traces are exportable to Jaeger (default) or any OTLP-compatible backend
  - Given instrumentation
    Then it adds < 5% overhead to request latency (measured via benchmark)
  - Given each span
    Then it includes: service.name, operation, duration, status, error (if any)
depends_on: [S-007]
definition_of_done:
  - [ ] OpenTelemetry SDK configuration in src/telemetry.py
  - [ ] Auto-instrumentation for asyncpg, aiohttp
  - [ ] Manual spans for MCP tool handlers
  - [ ] Trace ID in structured log output
  - [ ] Benchmark test confirming < 5% overhead
```

---

### S-073: Performance Testing

```yaml
id: S-073
title: Performance testing — MCP latency, REST API latency, Dashboard page load
feature: F-049
sprint: 8
story_points: 5
layer: integration
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: All services
acceptance_criteria:
  - Given MCP read tools
    When a 200-request load test runs
    Then p95 response time is under 500ms (Q-001)
  - Given MCP write tools
    When a 100-request load test runs
    Then p95 response time is under 2s (Q-002)
  - Given REST API endpoints
    When a k6 load test with 50 concurrent users runs for 60 seconds
    Then GET p95 < 500ms and POST p95 < 1s (Q-004)
  - Given Dashboard pages
    When Lighthouse tests run
    Then page load p95 < 2s (Q-005) and Fleet Health < 1s (Q-006)
  - Given MCP server startup
    Then each server reaches ready state within 5 seconds (Q-003)
depends_on: [S-032, S-043, S-051]
definition_of_done:
  - [ ] MCP load test scripts (pytest-benchmark)
  - [ ] REST API load test scripts (k6)
  - [ ] Dashboard page load tests
  - [ ] Performance baseline established and documented
  - [ ] CI runs performance tests and fails on threshold breach
```

---

### S-074: Security Hardening

```yaml
id: S-074
title: Security hardening — PII detection, input validation, CSRF protection, secrets management
feature: F-053
sprint: 8
story_points: 5
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: All services
acceptance_criteria:
  - Given user input to any MCP tool or REST endpoint
    When the input is processed
    Then it is validated against schema constraints (type, length, pattern) before reaching service layer
  - Given agent-generated output
    When it is stored or displayed
    Then PII patterns (email, phone, SSN) are detected and flagged (Q-027)
  - Given the Dashboard
    Then CSRF tokens are included in all state-changing forms
  - Given secret management
    Then all secrets (API keys, DB credentials) are loaded from environment variables or a secrets manager, never hardcoded (Q-019)
  - Given SQL queries
    Then all use parameterized statements — no string concatenation (Q-020)
  - Given authentication tokens
    Then JWTs expire after 1 hour with refresh tokens valid for 7 days (Q-024)
depends_on: [S-039, S-042]
definition_of_done:
  - [ ] Input validation middleware for REST and MCP
  - [ ] PII detection utility
  - [ ] CSRF protection in Dashboard
  - [ ] Security audit checklist against Q-019 through Q-028
  - [ ] Penetration test plan documented
```

---

### S-075: CI/CD Pipeline (GitHub Actions)

```yaml
id: S-075
title: CI/CD pipeline — lint, test, build, deploy via GitHub Actions
feature: F-056
sprint: 8
story_points: 8
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: N/A
acceptance_criteria:
  - Given a push to any branch
    When GitHub Actions runs
    Then the pipeline executes: lint (ruff) -> type check (mypy) -> unit tests -> integration tests -> parity tests -> performance tests
  - Given all checks pass on a PR
    When the PR is merged to main
    Then a deployment pipeline runs: build Docker images -> push to registry -> deploy to staging
  - Given the staging deployment
    Then smoke tests run against the staging environment
  - Given a manual approval on staging
    Then production deployment proceeds with zero-downtime rolling update
  - Given the CI pipeline
    Then total time for push checks is under 10 minutes
  - Given code coverage
    Then the pipeline fails if coverage drops below 80% (Q-034)
depends_on: [S-007]
definition_of_done:
  - [ ] .github/workflows/ci.yml with full pipeline
  - [ ] .github/workflows/deploy.yml with staging + production
  - [ ] Docker build for all services (MCP servers, REST API, Dashboard)
  - [ ] Smoke test script for staging
  - [ ] Coverage gate at 80%
  - [ ] Pipeline duration under 10 minutes
```

---

### S-076: Documentation (API, MCP, Dashboard User Guide)

```yaml
id: S-076
title: Documentation — OpenAPI spec, MCP tool reference, Dashboard user guide
feature: F-056
sprint: 8
story_points: 5
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: N/A
acceptance_criteria:
  - Given the REST API
    Then an OpenAPI 3.1 specification is generated from route annotations and served at /api/v1/docs
  - Given the MCP tools
    Then a reference document is generated listing all 35 tools with: name, description, input schema, output schema, examples
  - Given the Dashboard
    Then a user guide is written covering: login, each page's purpose and workflow, keyboard shortcuts
  - Given the documentation
    Then it is versioned alongside the codebase and updated on each release
  - Given API examples
    Then curl commands are provided for every REST endpoint and MCP tool call examples are provided
depends_on: [S-043, S-044, S-041, S-050]
definition_of_done:
  - [ ] OpenAPI spec auto-generated and served at /api/v1/docs
  - [ ] MCP tool reference with examples
  - [ ] Dashboard user guide with screenshots
  - [ ] All docs versioned in repository
```

---

### S-078: Implement LLM Provider Abstraction (sdk/llm/)

```yaml
id: S-078
title: Implement LLM provider abstraction layer with pluggable providers
feature: F-050
sprint: 0
story_points: 8
layer: infrastructure
interaction_ids: []
mcp_tools: []
dashboard_screens: []
shared_service: ProviderService
acceptance_criteria:
  - Given the sdk/llm/ module
    When a new LLMProvider implementation is registered
    Then it conforms to the LLMProvider interface (complete, chat, stream methods)
  - Given AnthropicProvider, OpenAIProvider, and OllamaProvider
    When each is instantiated with valid credentials
    Then each can complete a basic prompt and return a well-formed response
  - Given BaseAgent
    When it invokes an LLM call
    Then it uses LLMProvider (no direct anthropic/openai/ollama import)
  - Given an agent manifest with tier: fast|balanced|powerful
    When the agent is invoked
    Then the tier resolves to the correct model ID for the configured provider
  - Given LLM_PROVIDER=anthropic in .env
    When the platform starts
    Then AnthropicProvider is the default provider
  - Given cost calculation
    When a provider-aware invocation completes
    Then cost is calculated using the correct provider's pricing table
depends_on: [S-007]
definition_of_done:
  - [ ] sdk/llm/__init__.py with LLMProvider Protocol
  - [ ] sdk/llm/anthropic_provider.py — AnthropicProvider
  - [ ] sdk/llm/openai_provider.py — OpenAIProvider
  - [ ] sdk/llm/ollama_provider.py — OllamaProvider
  - [ ] sdk/llm/registry.py — provider registry and tier-to-model resolution
  - [ ] BaseAgent updated to use LLMProvider (no direct SDK imports)
  - [ ] Agent manifests use tier (fast/balanced/powerful) not model IDs
  - [ ] Unit tests for all three providers
  - [ ] .env.example updated with LLM_PROVIDER variable
```

---

### S-079: Provider Health Check Endpoint

```yaml
id: S-079
title: REST endpoint for LLM provider health checks
feature: F-050
sprint: 4
story_points: 3
layer: rest
interaction_ids: []
mcp_tools: []
dashboard_screens: [S-001]
shared_service: ProviderService
acceptance_criteria:
  - Given GET /api/v1/system/providers
    When called with valid auth
    Then returns list of all configured providers with health status and tier mappings
  - Given GET /api/v1/system/providers/{name}/health
    When called with a valid provider name
    Then returns detailed health info including latency, error rate, and rate limits
  - Given GET /api/v1/system/providers/{name}/health
    When called with an unknown provider name
    Then returns 404 PROVIDER_NOT_FOUND
  - Given the Fleet Health page (S-001)
    When rendered
    Then the LLM Provider Status sub-section displays data from these endpoints
depends_on: [S-078, S-029]
definition_of_done:
  - [ ] GET /api/v1/system/providers endpoint implemented
  - [ ] GET /api/v1/system/providers/{name}/health endpoint implemented
  - [ ] ProviderService with list_providers() and check_health() methods
  - [ ] Unit tests for both endpoints
  - [ ] Dashboard S-001 updated to consume provider health data
```

---

### S-080: Provider Column in cost_metrics for Per-Provider Cost Tracking

```yaml
id: S-080
title: Add provider column to cost_metrics and agent_registry for per-provider cost tracking
feature: F-014
sprint: 1
story_points: 2
layer: infrastructure
interaction_ids: [I-040]
mcp_tools: [get_cost_report]
dashboard_screens: [S-010]
shared_service: CostService
acceptance_criteria:
  - Given cost_metrics table
    When a cost record is inserted
    Then the provider column stores which LLM provider was used (e.g., "anthropic", "openai")
  - Given agent_registry table
    When an agent is registered
    Then the llm_provider column stores the agent's configured provider
  - Given mcp_call_events table
    When an MCP call is logged
    Then the provider column records which provider handled the call
  - Given the cost report endpoint (GET /api/v1/cost/report)
    When called
    Then the response includes a by_provider breakdown
  - Given the idx_cost_provider index
    When querying costs by provider
    Then the query uses the index and returns results efficiently
depends_on: [S-001, S-078]
definition_of_done:
  - [ ] Migration: ALTER cost_metrics ADD COLUMN provider VARCHAR(32) DEFAULT 'anthropic'
  - [ ] Migration: ALTER agent_registry ADD COLUMN llm_provider VARCHAR(32) DEFAULT 'anthropic'
  - [ ] Migration: ALTER mcp_call_events ADD COLUMN provider VARCHAR(32)
  - [ ] Index: CREATE INDEX idx_cost_provider ON cost_metrics(provider, recorded_at DESC)
  - [ ] CostService.get_report() updated with by_provider breakdown
  - [ ] Unit tests for provider-aware cost aggregation
```

---

### S-077: Agent Golden + Adversarial Test Suite

```yaml
id: S-077
title: Agent test suite — golden path tests and adversarial inputs for all 48 agents
feature: F-048, F-049
sprint: 8
story_points: 5
layer: integration
interaction_ids: [I-022]
mcp_tools: [invoke_agent]
dashboard_screens: []
shared_service: AgentService, QualityService
acceptance_criteria:
  - Given each of the 48 agents
    When invoked with a golden input (known-good test case)
    Then the output meets the quality threshold (score >= 70) and matches expected structure
  - Given each agent
    When invoked with adversarial inputs (empty, oversized, malicious, off-topic)
    Then the agent handles gracefully: returns error or asks for clarification, does not crash or produce unsafe output
  - Given golden tests
    Then each agent has at least 2 golden test cases with expected output patterns
  - Given adversarial tests
    Then each agent has at least 3 adversarial inputs: empty, prompt injection, off-topic
  - Given the test suite
    Then it runs in CI and reports per-agent pass rates
depends_on: [S-033, S-068]
definition_of_done:
  - [ ] tests/agents/golden/ with golden test cases for all 48 agents
  - [ ] tests/agents/adversarial/ with adversarial inputs
  - [ ] Quality score assertion on golden outputs
  - [ ] Graceful handling assertion on adversarial inputs
  - [ ] CI integration with per-agent reporting
```

---

## 13. Story Dependency Graph

```
Sprint 0: Infrastructure
  S-007 (scaffolding) ─────────────────────────────────┐
  S-001 (core migrations) ──┬──┬──┬──┬──┐              │
                            │  │  │  │  │              │
  S-002 (knowledge_excep) ──┘  │  │  │  │              │
  S-003 (session_context) ─────┘  │  │  │              │
  S-004 (approval_req) ──────────┘  │  │              │
  S-005 (checkpoints) ─────────────┘  │              │
  S-006 (mcp_events) ────────────────┘              │
  S-008 (RLS) ← depends on all S-001 through S-006  │
                                                      │
Sprint 1: Core Shared Services                        │
  S-009 (SessionService) ← S-003, S-007 ─────────────┘
  S-010 (Pipeline.trigger) ← S-001, S-007
  S-011 (Pipeline.status) ← S-010
  S-012 (Pipeline.list) ← S-010
  S-013 (Agent.list) ← S-001, S-007
  S-014 (Agent.get) ← S-013
  S-015 (Cost.report) ← S-001, S-007
  S-016 (Cost.budget) ← S-015
  S-017 (Cost.record) ← S-015
  S-018 (Audit.query) ← S-001, S-007
  S-019 (Audit.summary) ← S-018

Sprint 2: Safety + Approval Services
  S-020 (Approval.create) ← S-001, S-004, S-010
  S-021 (Approval.list) ← S-020
  S-022 (Approval.approve) ← S-020
  S-023 (Approval.reject) ← S-020
  S-024 (Pipeline.resume) ← S-010, S-005
  S-025 (Pipeline.cancel) ← S-010
  S-026 (Knowledge.search) ← S-002, S-007
  S-027 (Knowledge.create) ← S-026
  S-028 (Knowledge.promote) ← S-027
  S-029 (Health.fleet) ← S-013, S-007
  S-030 (RateLimiter) ← S-007

Sprint 3: MCP Servers + REST API
  S-031 (agents-server) ← S-010, S-013, S-007
  S-032 (MCP pipeline tools) ← S-031, S-010, S-011, S-012
  S-033 (MCP agent tools) ← S-031, S-013, S-014
  S-034 (governance-server) ← S-015, S-018, S-020, S-007
  S-035 (MCP cost+audit tools) ← S-034, S-015, S-016, S-018, S-019
  S-036 (MCP approval tools) ← S-034, S-020, S-021, S-022, S-023
  S-037 (knowledge-server) ← S-026, S-007
  S-038 (MCP knowledge tools) ← S-037, S-026, S-027, S-028
  S-039 (MCP auth) ← S-031, S-034, S-037
  S-040 (MCP resources) ← S-031, S-013, S-014
  S-041 (MCP prompts) ← S-031, S-034

Sprint 4: REST API + Dashboard Foundation
  S-042 (REST scaffold) ← S-007, S-030
  S-043 (REST pipelines) ← S-042, S-010-S-012, S-024, S-025
  S-044 (REST agents) ← S-042, S-013, S-014
  S-045 (REST costs) ← S-042, S-015, S-016
  S-046 (REST audit) ← S-042, S-018, S-019
  S-047 (REST approvals) ← S-042, S-020-S-023
  S-048 (REST knowledge) ← S-042, S-026-S-028
  S-049 (REST system) ← S-042, S-029
  S-050 (Dashboard scaffold) ← S-042, S-007
  S-051 (Fleet Health page) ← S-050, S-049

Sprint 5: Dashboard Pages
  S-052 (Cost Monitor) ← S-050, S-045
  S-053 (Pipeline Runs) ← S-050, S-043
  S-054 (Audit Log) ← S-050, S-046
  S-055 (Approval Queue) ← S-050, S-047
  S-056 (MCP Panel) ← S-051, S-049

Sprint 6: Cross-Interface Integration
  S-057 (Parity tests) ← S-032-S-038, S-043-S-048
  S-058 (Journey: Pipeline+Approval) ← S-057
  S-059 (Journey: Cost Spike) ← S-057
  S-060 (Journey: Canary) ← S-057
  S-061 (Journey: Compliance) ← S-057
  S-062 (WebSocket) ← S-051, S-053, S-055, S-056
  S-063 (Slack) ← S-020, S-015

Sprint 7: Advanced Features
  S-064 (Agent versions) ← S-013, S-014, S-006
  S-065 (DAG execution) ← S-010, S-024
  S-066 (Self-healing) ← S-010, S-017
  S-067 (Checkpoints) ← S-005, S-024
  S-068 (Quality scoring) ← S-010
  S-069 (Exception injection) ← S-026, S-010
  S-070 (Cost anomalies) ← S-017, S-063

Sprint 8: Polish + Hardening
  S-071 (Logging) ← S-007
  S-072 (OpenTelemetry) ← S-007
  S-073 (Performance tests) ← S-032, S-043, S-051
  S-074 (Security) ← S-039, S-042
  S-075 (CI/CD) ← S-007
  S-076 (Documentation) ← S-043, S-044, S-041, S-050
  S-077 (Agent tests) ← S-033, S-068
```

---

## 14. Traceability Matrix

### Feature to Story Mapping

| Feature | Name | Story(s) | Sprint |
|---------|------|----------|--------|
| F-001 | Trigger Pipeline | S-010, S-032, S-043 | 1, 3, 4 |
| F-002 | Get Pipeline Status | S-011, S-032, S-043 | 1, 3, 4 |
| F-003 | List Pipeline Runs | S-012, S-032, S-043 | 1, 3, 4 |
| F-004 | Resume Pipeline | S-024, S-067, S-043 | 2, 7, 4 |
| F-005 | Cancel Pipeline | S-025, S-043 | 2, 4 |
| F-006 | Pipeline DAG Execution | S-065 | 7 |
| F-007 | Pipeline Self-Healing | S-066 | 7 |
| F-008 | List Agents | S-013, S-033, S-044 | 1, 3, 4 |
| F-009 | Get Agent Detail | S-014, S-033, S-044 | 1, 3, 4 |
| F-010 | Invoke Agent | S-033, S-044 | 3, 4 |
| F-011 | Check Agent Health | S-033, S-044 | 3, 4 |
| F-012 | Agent Version Management | S-064, S-044 | 7, 4 |
| F-013 | Agent Maturity | S-044 | 4 |
| F-014 | Get Cost Report | S-015, S-035, S-045 | 1, 3, 4 |
| F-015 | Check Budget | S-016, S-035, S-045 | 1, 3, 4 |
| F-016 | Record Spend | S-017 | 1 |
| F-017 | Cost Anomaly Detection | S-070 | 7 |
| F-018 | Set Budget Threshold | S-045 | 4 |
| F-019 | Query Audit Events | S-018, S-035, S-046 | 1, 3, 4 |
| F-020 | Get Audit Summary | S-019, S-035, S-046 | 1, 3, 4 |
| F-021 | Export Audit Report | S-046 | 4 |
| F-022 | MCP Call Events | S-006, S-049 | 0, 4 |
| F-023 | Create Approval Request | S-020 | 2 |
| F-024 | List Pending Approvals | S-021, S-036, S-047 | 2, 3, 4 |
| F-025 | Approve Gate | S-022, S-036, S-047 | 2, 3, 4 |
| F-026 | Reject Gate | S-023, S-036, S-047 | 2, 3, 4 |
| F-027 | Approval Escalation | S-020 (sub-behavior) | 2 |
| F-028 | Approval SLA | S-020, S-021 | 2 |
| F-029 | Search Exceptions | S-026, S-038, S-048 | 2, 3, 4 |
| F-030 | Create Exception | S-027, S-038, S-048 | 2, 3, 4 |
| F-031 | Promote Exception | S-028, S-038, S-048 | 2, 3, 4 |
| F-032 | List Exceptions | S-038, S-048 | 3, 4 |
| F-033 | Exception Auto-Injection | S-069 | 7 |
| F-034 | MCP agents-server | S-031 | 3 |
| F-035 | MCP governance-server | S-034 | 3 |
| F-036 | MCP knowledge-server | S-037 | 3 |
| F-037 | MCP Authentication | S-039 | 3 |
| F-038 | MCP Resources | S-040 | 3 |
| F-039 | MCP Prompts | S-041 | 3 |
| F-040 | Dashboard Fleet Health | S-051 | 4 |
| F-041 | Dashboard Cost Monitor | S-052 | 5 |
| F-042 | Dashboard Pipeline Runs | S-053 | 5 |
| F-043 | Dashboard Audit Log | S-054 | 5 |
| F-044 | Dashboard Approval Queue | S-055 | 5 |
| F-045 | Dashboard MCP Panel | S-056 | 5 |
| F-046 | Quality Scoring | S-068 | 7 |
| F-047 | Quality Thresholds | S-068 | 7 |
| F-048 | Golden Test Suite | S-077 | 8 |
| F-049 | Interface Parity | S-057 | 6 |
| F-050 | Session Management | S-009 | 1 |
| F-051 | Configuration | S-008, S-042 | 0, 4 |
| F-052 | Rate Limiting | S-030 | 2 |
| F-053 | Secrets Management | S-074 | 8 |
| F-054 | Fleet Health Check | S-029, S-049 | 2, 4 |
| F-055 | Structured Logging | S-071, S-072 | 8 |
| F-056 | CI/CD | S-007, S-075 | 0, 8 |

### Capability to Feature to Story Mapping

| Capability | Features | Stories |
|------------|----------|---------|
| C1: Agent Orchestration | F-008 to F-013 | S-013, S-014, S-033, S-044, S-064 |
| C2: Pipeline Generation | F-001 to F-003, F-005 | S-010, S-011, S-012, S-025, S-032, S-043 |
| C3: Human Approval Gates | F-023 to F-028 | S-020 to S-023, S-036, S-047, S-055 |
| C4: Cost Governance | F-014 to F-018 | S-015 to S-017, S-035, S-045, S-052, S-070 |
| C5: Audit Trail | F-019 to F-022 | S-018, S-019, S-035, S-046, S-054 |
| C6: Knowledge Management | F-029 to F-033 | S-026 to S-028, S-038, S-048, S-069 |
| C7: MCP Infrastructure | F-034 to F-039 | S-031, S-034, S-037, S-039, S-040, S-041 |
| C8: Pipeline Resilience | F-004, F-006, F-007 | S-024, S-065, S-066, S-067 |
| C9: Agent Lifecycle | F-012, F-013 | S-064, S-044 |
| C10: Quality & Testing | F-046 to F-049 | S-068, S-057, S-077 |
| C11: Dashboard | F-040 to F-045 | S-050 to S-056 |
| C12: Platform Foundation | F-050 to F-056 | S-007 to S-009, S-030, S-071 to S-075 |

### Interaction to Story Mapping

| Interaction | Description | Stories |
|-------------|-------------|---------|
| I-001 | Trigger pipeline | S-010, S-032, S-043, S-053 |
| I-002 | Get pipeline status | S-011, S-032, S-043, S-053 |
| I-003 | List pipeline runs | S-012, S-032, S-043, S-053 |
| I-004 | Resume pipeline | S-024, S-043, S-067 |
| I-005 | Cancel pipeline | S-025, S-043 |
| I-006 | Get pipeline documents | S-043, S-068 |
| I-007 | Retry pipeline step | S-043, S-066 |
| I-008 | Get pipeline config | S-043 |
| I-009 | Validate project input | S-043 |
| I-020 | List agents | S-013, S-033, S-044, S-051 |
| I-021 | Get agent detail | S-014, S-033, S-044, S-051 |
| I-022 | Invoke agent | S-033, S-044, S-077 |
| I-023 | Check agent health | S-033, S-044, S-051 |
| I-024 | Promote agent version | S-064, S-044 |
| I-025 | Rollback agent version | S-064, S-044 |
| I-026 | Set canary traffic | S-064, S-044 |
| I-027 | Get agent maturity | S-044 |
| I-040 | Get cost report | S-015, S-035, S-045, S-052 |
| I-041 | Check budget | S-016, S-035, S-045, S-052 |
| I-042 | Query audit events | S-018, S-035, S-046, S-054 |
| I-043 | Get audit summary | S-019, S-035, S-046, S-054 |
| I-044 | Export audit report | S-046, S-054 |
| I-045 | List pending approvals | S-021, S-036, S-047, S-055 |
| I-046 | Approve gate | S-022, S-036, S-047, S-055 |
| I-047 | Reject gate | S-023, S-036, S-047, S-055 |
| I-048 | Get cost anomalies | S-045, S-052, S-070 |
| I-049 | Set budget threshold | S-045, S-052 |
| I-060 | Search exceptions | S-026, S-038, S-048, S-069 |
| I-061 | Create exception | S-027, S-038, S-048 |
| I-062 | Promote exception | S-028, S-038, S-048 |
| I-063 | List exceptions | S-038, S-048, S-069 |
| I-080 | Get fleet health | S-029, S-049, S-051 |
| I-081 | Get MCP server status | S-049, S-051, S-056 |
| I-082 | List recent MCP calls | S-049, S-051, S-056 |

---

## 15. Velocity and Capacity

### Team Configuration

| Role | Count | Points/Sprint |
|------|-------|---------------|
| Full-stack developer | 2 | 20 each |
| **Total capacity** | | **40 pts/sprint** |

### Sprint Velocity Plan

| Sprint | Planned Points | Capacity | Buffer | Risk |
|--------|---------------|----------|--------|------|
| 0 | 23 | 40 | 17 (ramp-up) | Low — greenfield setup |
| 1 | 44 | 40 | -4 (slight over) | Medium — service complexity |
| 2 | 39 | 40 | 1 | Low |
| 3 | 45 | 40 | -5 (slight over) | Medium — MCP SDK learning curve |
| 4 | 43 | 40 | -3 (slight over) | Medium — REST + Dashboard parallel |
| 5 | 34 | 40 | 6 | Low — dashboard-only sprint |
| 6 | 41 | 40 | -1 | Low — mostly testing |
| 7 | 41 | 40 | -1 | High — complex service logic |
| 8 | 41 | 40 | -1 | Medium — hardening can be descoped |
| **Total** | **351** | **360** | **9** | |

### Mitigation for Over-Capacity Sprints

- **Sprint 1 (+4):** S-017 (record_spend, 3 pts) can slip to Sprint 2 if needed
- **Sprint 3 (+5):** S-041 (MCP prompts, 3 pts) can slip to Sprint 4
- **Sprint 4 (+3):** Offset by Sprint 5 having 6-point buffer
- **Sprint 7 (+1):** S-069 (exception injection, 5 pts) can be descoped to Sprint 8

### Timeline Summary

| Milestone | Sprint | Week | Date (est.) |
|-----------|--------|------|-------------|
| Database + scaffolding complete | 0 | 2 | 2026-04-07 |
| All shared services operational | 1-2 | 6 | 2026-05-05 |
| MCP + REST interfaces live | 3-4 | 10 | 2026-06-02 |
| Dashboard complete | 5 | 12 | 2026-06-16 |
| Cross-interface integration verified | 6 | 14 | 2026-06-30 |
| Advanced features complete | 7 | 16 | 2026-07-14 |
| Production-ready | 8 | 18 | 2026-07-28 |

---

## Appendix: NFR Coverage

| NFR | Description | Story(s) |
|-----|-------------|----------|
| Q-001 | MCP read < 500ms p95 | S-073 |
| Q-002 | MCP write < 2s p95 | S-073 |
| Q-003 | MCP server startup < 5s | S-031, S-034, S-037, S-073 |
| Q-004 | REST API < 500ms/1s p95 | S-073 |
| Q-005 | Dashboard page load < 2s p95 | S-051 through S-056, S-073 |
| Q-006 | Fleet Health page < 1s | S-051, S-073 |
| Q-019 | No hardcoded secrets | S-074 |
| Q-020 | Parameterized SQL | S-074 |
| Q-024 | JWT token expiry | S-074 |
| Q-027 | PII detection | S-074 |
| Q-029 | WCAG 2.1 AA | S-050 through S-056 |
| Q-030 | Keyboard navigation | S-050 through S-056 |
| Q-031 | Screen reader support | S-050 through S-056 |
| Q-034 | Code coverage >= 80% | S-075 |
| Q-049 | Interface parity (fields) | S-057 |
| Q-051 | Interface parity (errors) | S-057 |
| Q-053 | Interface parity (pagination) | S-057 |

---

*End of BACKLOG document.*
*Generated using Full-Stack-First approach — every story traces to Feature -> Capability -> Interaction.*
