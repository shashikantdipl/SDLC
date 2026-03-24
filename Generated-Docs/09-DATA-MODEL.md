# DATA-MODEL — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 9 of 14 | Status: Draft
**Reads from:** INTERACTION-MAP (Doc 6) — all 22 data shapes drive table design. MCP-TOOL-SPEC (Doc 7) and DESIGN-SPEC (Doc 8) — query patterns drive index design.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Data Shape to Table Mapping](#2-data-shape-to-table-mapping)
3. [Schema DDL](#3-schema-ddl)
4. [Indexes](#4-indexes)
5. [Row-Level Security (RLS)](#5-row-level-security-rls)
6. [Query Pattern Registry](#6-query-pattern-registry)
7. [Capacity Estimates](#7-capacity-estimates)
8. [Migration Strategy](#8-migration-strategy)
9. [Supplementary Data Stores](#9-supplementary-data-stores)

---

## 1. Overview

The Agentic SDLC Platform uses PostgreSQL 15+ as its primary operational store. In Full-Stack-First, the data model serves THREE consumers equally through a shared service layer:

1. **MCP tool handlers** — optimized for MCP tool query patterns (list, get, search, filter)
2. **REST API handlers** — optimized for API query patterns (CRUD, pagination, bulk)
3. **Dashboard (via REST API)** — optimized for real-time display queries (list views, filters, sorts, aggregations)

All three consumers call the same shared service methods, which return the canonical data shapes defined in the INTERACTION-MAP (Doc 6). The database schema is designed so that every data shape can be materialized from table rows with minimal joins and no application-level post-processing.

### Data Store Inventory

| Store | Technology | Purpose | Tables | Mutability |
|-------|-----------|---------|--------|------------|
| Primary OLTP | PostgreSQL 15+ | Operational data for all 3 consumers | 10 tables | Read/Write (except audit_events: append-only) |
| File Storage | Local filesystem | Generated documents, exported reports | N/A (directory tree) | Write-once, read-many |
| Configuration | YAML files | Agent manifests, archetypes, team definitions | N/A (file-based) | Read-only at runtime |
| Structured Logs | JSONL files | Audit trail backup, structured log archive | N/A (append-only files) | Append-only |
| In-Memory | Python dict / Token Buckets | Rate limiter state, circuit breaker state | N/A | Ephemeral |

### Table Summary

| # | Table | Migration | Row Growth | Primary Consumer(s) |
|---|-------|-----------|------------|---------------------|
| 1 | `agent_registry` | 001 + 009-ALTER | Slow (48 rows, rarely changes) | Fleet Health page, list_agents MCP |
| 2 | `cost_metrics` | 002 | High (100-500 rows/day) | Cost Monitor page, get_cost_report MCP |
| 3 | `audit_events` | 003 | High (200-1000 rows/day) | Audit Log page, query_audit_events MCP |
| 4 | `pipeline_runs` | 004 | Medium (5-10 rows/day) | Pipeline Runs page, list_pipeline_runs MCP |
| 5 | `pipeline_steps` | 004 | Medium (70-140 rows/day) | Pipeline Run Detail, get_pipeline_status MCP |
| 6 | `knowledge_exceptions` | 005 | Low (10-50 rows/month) | search_exceptions MCP |
| 7 | `session_context` | 006 | High (140-280 rows/day) | Pipeline execution (internal), session store |
| 8 | `approval_requests` | 007 | Low (5-20 rows/day) | Approval Queue page, list_pending_approvals MCP |
| 9 | `pipeline_checkpoints` | 008 | Medium (5-10 rows/day) | Pipeline resume (internal) |
| 10 | `mcp_call_events` | 009 | High (200-1000 rows/day) | MCP Monitoring Panel, list_recent_mcp_calls MCP |

---

## 2. Data Shape to Table Mapping

The INTERACTION-MAP defines 22 data shapes. Each must be producible from one or more database tables. Some shapes are direct row mappings; others are computed aggregations.

| # | INTERACTION-MAP Shape | Primary Table(s) | Computed? | Mapping Notes |
|---|----------------------|-------------------|-----------|---------------|
| 1 | `PipelineRun` | `pipeline_runs` | No | Direct row mapping. `current_step_name` joined from `pipeline_steps`. `checkpoint_step` from `pipeline_checkpoints`. |
| 2 | `PipelineDocument` | File system + `pipeline_steps` | Partial | `content` from filesystem (`reports/{project_id}/{run_id}/`). Metadata (`quality_score`, `token_count`, `agent_id`) from `pipeline_steps`. |
| 3 | `PipelineConfig` | YAML files | Yes | Read from `teams/document-stack.yaml` at runtime. Not stored in DB. Cached in memory. |
| 4 | `ValidationResult` | None (computed) | Yes | Computed in-memory by `PipelineService.validate_input()`. No persistence. |
| 5 | `AgentSummary` | `agent_registry` + `cost_metrics` | Partial | Base fields from `agent_registry`. `cost_today_usd` aggregated from `cost_metrics`. `invocation_count_today` from `cost_metrics` COUNT. |
| 6 | `AgentDetail` | `agent_registry` + YAML + `cost_metrics` | Partial | Extends `AgentSummary`. `manifest` from filesystem YAML. `prompt_preview` from `agents/{id}/prompt.md`. |
| 7 | `AgentHealth` | In-memory + `agent_registry` | Yes | Computed by health check ping. `circuit_breaker_open` from in-memory state. `consecutive_failures` tracked in memory. |
| 8 | `AgentVersion` | `agent_registry` | No | Direct column mapping: `active_version`, `canary_version`, `canary_traffic_pct`, `previous_version`. Timestamps from `updated_at`. |
| 9 | `AgentMaturity` | `agent_registry` + `cost_metrics` + `audit_events` | Yes | `current_level` from `agent_registry.maturity_level`. `override_rate` computed from `audit_events`. `confidence_avg` from recent invocation scores. |
| 10 | `AgentInvocationResult` | `audit_events` + `cost_metrics` | Yes | Composed from audit event of action `agent.invoke` plus associated cost record. |
| 11 | `CostReport` | `cost_metrics` + `agent_registry` | Yes | Aggregated: `SUM(cost_usd)`, `GROUP BY agent_id`, date truncation. `trend_pct` computed by comparing current vs. previous period. |
| 12 | `BudgetStatus` | `cost_metrics` + config (env vars) | Yes | `spent_usd` from `SUM(cost_usd)`. `budget_usd` from env config. `utilization_pct` = spent/budget * 100. |
| 13 | `CostAnomaly` | `cost_metrics` | Yes | Computed by anomaly detection: compare rolling average vs. current window. No dedicated table (computed on-the-fly). |
| 14 | `AuditEvent` | `audit_events` | No | Direct row mapping. All fields stored as columns. `details` is JSONB. |
| 15 | `AuditSummary` | `audit_events` | Yes | Aggregated: `COUNT(*)`, `GROUP BY severity`, `GROUP BY agent_id`, `GROUP BY project_id`, `GROUP BY action`. |
| 16 | `AuditReport` | File system + `audit_events` | Yes | Report metadata generated on export. `download_url` points to `reports/{project_id}/audit/`. Source data from `audit_events`. |
| 17 | `ApprovalRequest` | `approval_requests` | No | Direct row mapping. `context` stored as JSONB. `risk_level` and `project_id` added as columns (extending MASTER-BUILD-SPEC schema). |
| 18 | `ApprovalResult` | `approval_requests` | No | Subset of `approval_requests` columns after decision. `pipeline_resumed` derived from pipeline_runs status change. |
| 19 | `KnowledgeException` | `knowledge_exceptions` | No | Direct row mapping. `tags` stored as `TEXT[]`. |
| 20 | `FleetHealth` | `agent_registry` + `cost_metrics` + `pipeline_runs` + `approval_requests` | Yes | Aggregated across multiple tables. `healthy_agents` from agent_registry WHERE status. `active_pipelines` from pipeline_runs WHERE status. |
| 21 | `McpServerStatus` | In-memory | Yes | Computed from MCP server runtime metrics. Not persisted. Cached with 5s TTL. |
| 22 | `McpCallEvent` | `mcp_call_events` | No | Direct row mapping. New table (migration 009). |

---

## 3. Schema DDL

All DDL is valid, executable PostgreSQL 15+. Tables are presented in migration order.

### Migration 001: agent_registry

```sql
-- Migration 001: Create agent_registry table
-- UP
CREATE TABLE agent_registry (
    id              BIGSERIAL PRIMARY KEY,
    agent_id        VARCHAR(64) NOT NULL UNIQUE,
    name            VARCHAR(256) NOT NULL,
    phase           VARCHAR(32) NOT NULL
                    CHECK (phase IN ('govern', 'design', 'build', 'test', 'deploy', 'operate', 'oversight')),
    archetype       VARCHAR(64) NOT NULL
                    CHECK (archetype IN ('ci-gate', 'reviewer', 'ops-agent', 'discovery-agent', 'co-pilot', 'orchestrator', 'governance')),
    model           VARCHAR(64) NOT NULL DEFAULT 'claude-sonnet-4-6',
    status          VARCHAR(16) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'degraded', 'offline', 'canary')),
    active_version  VARCHAR(32) DEFAULT '1.0.0',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE agent_registry IS 'Registry of all 48 SDLC agents with their configuration and status';

-- DOWN
DROP TABLE IF EXISTS agent_registry;
```

### Migration 002: cost_metrics

```sql
-- Migration 002: Create cost_metrics table
-- UP
CREATE TABLE cost_metrics (
    id              BIGSERIAL PRIMARY KEY,
    agent_id        VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id),
    project_id      VARCHAR(64) NOT NULL,
    session_id      UUID NOT NULL,
    model           VARCHAR(64) NOT NULL,
    input_tokens    INTEGER NOT NULL DEFAULT 0 CHECK (input_tokens >= 0),
    output_tokens   INTEGER NOT NULL DEFAULT 0 CHECK (output_tokens >= 0),
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE cost_metrics IS 'Per-invocation cost tracking for budget enforcement and reporting';

-- DOWN
DROP TABLE IF EXISTS cost_metrics;
```

### Migration 003: audit_events (IMMUTABLE)

```sql
-- Migration 003: Create audit_events table with immutability trigger
-- UP
CREATE TABLE audit_events (
    id              BIGSERIAL PRIMARY KEY,
    event_id        UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    agent_id        VARCHAR(64),
    project_id      VARCHAR(64),
    session_id      UUID NOT NULL,
    action          VARCHAR(128) NOT NULL,
    severity        VARCHAR(16) NOT NULL DEFAULT 'info'
                    CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    message         TEXT,
    details         JSONB DEFAULT '{}',
    pii_detected    BOOLEAN NOT NULL DEFAULT FALSE,
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    tokens_in       INTEGER NOT NULL DEFAULT 0 CHECK (tokens_in >= 0),
    tokens_out      INTEGER NOT NULL DEFAULT 0 CHECK (tokens_out >= 0),
    duration_ms     INTEGER NOT NULL DEFAULT 0 CHECK (duration_ms >= 0),
    source_ip       INET,
    user_id         VARCHAR(128),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Immutability trigger: block UPDATE and DELETE on audit_events
CREATE OR REPLACE FUNCTION audit_events_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_events table is immutable. UPDATE and DELETE operations are prohibited.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_events_no_update
    BEFORE UPDATE ON audit_events
    FOR EACH ROW
    EXECUTE FUNCTION audit_events_immutable();

CREATE TRIGGER trg_audit_events_no_delete
    BEFORE DELETE ON audit_events
    FOR EACH ROW
    EXECUTE FUNCTION audit_events_immutable();

COMMENT ON TABLE audit_events IS 'Immutable audit trail. No UPDATE or DELETE allowed. Append-only.';

-- DOWN
DROP TRIGGER IF EXISTS trg_audit_events_no_delete ON audit_events;
DROP TRIGGER IF EXISTS trg_audit_events_no_update ON audit_events;
DROP FUNCTION IF EXISTS audit_events_immutable();
DROP TABLE IF EXISTS audit_events;
```

### Migration 004: pipeline_runs + pipeline_steps

```sql
-- Migration 004: Create pipeline_runs and pipeline_steps tables
-- UP
CREATE TABLE pipeline_runs (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    project_id      VARCHAR(64) NOT NULL,
    pipeline_name   VARCHAR(128) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed', 'cancelled')),
    current_step    INTEGER NOT NULL DEFAULT 0 CHECK (current_step >= 0),
    total_steps     INTEGER NOT NULL DEFAULT 14 CHECK (total_steps > 0),
    triggered_by    VARCHAR(128) NOT NULL DEFAULT 'system',
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0)
);

CREATE TABLE pipeline_steps (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    step_number     INTEGER NOT NULL CHECK (step_number >= 0),
    step_name       VARCHAR(128) NOT NULL,
    agent_id        VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id),
    status          VARCHAR(16) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    input_key       VARCHAR(128),
    output_key      VARCHAR(128),
    quality_score   NUMERIC(4, 3) CHECK (quality_score >= 0 AND quality_score <= 1),
    token_count     INTEGER DEFAULT 0 CHECK (token_count >= 0),
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    UNIQUE (run_id, step_number)
);

COMMENT ON TABLE pipeline_runs IS 'Top-level pipeline execution records';
COMMENT ON TABLE pipeline_steps IS 'Individual step execution within a pipeline run';

-- DOWN
DROP TABLE IF EXISTS pipeline_steps;
DROP TABLE IF EXISTS pipeline_runs;
```

### Migration 005: knowledge_exceptions

```sql
-- Migration 005: Create knowledge_exceptions table
-- UP
CREATE TABLE knowledge_exceptions (
    exception_id    VARCHAR(64) PRIMARY KEY,
    title           VARCHAR(256) NOT NULL,
    rule            TEXT NOT NULL,
    description     TEXT,
    severity        VARCHAR(16) NOT NULL DEFAULT 'warning'
                    CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    tier            VARCHAR(16) NOT NULL
                    CHECK (tier IN ('universal', 'stack', 'client')),
    stack_name      VARCHAR(128),
    client_id       VARCHAR(128),
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    applies_to_phases TEXT[],
    applies_to_agents TEXT[],
    fire_count      INTEGER NOT NULL DEFAULT 0 CHECK (fire_count >= 0),
    last_fired_at   TIMESTAMPTZ,
    tags            TEXT[] DEFAULT '{}',
    promoted_by     VARCHAR(128),
    promoted_at     TIMESTAMPTZ,
    created_by      VARCHAR(128) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tier-level constraint: client tier requires client_id, stack tier requires stack_name
ALTER TABLE knowledge_exceptions
    ADD CONSTRAINT chk_tier_client CHECK (
        tier != 'client' OR client_id IS NOT NULL
    );

ALTER TABLE knowledge_exceptions
    ADD CONSTRAINT chk_tier_stack CHECK (
        tier != 'stack' OR stack_name IS NOT NULL
    );

COMMENT ON TABLE knowledge_exceptions IS 'Three-tier knowledge exception catalog (universal > stack > client)';

-- DOWN
DROP TABLE IF EXISTS knowledge_exceptions;
```

### Migration 006: session_context (BLOCKING)

```sql
-- Migration 006: Create session_context table
-- BLOCKING: The 12-doc pipeline cannot run without this table.
-- Agents write intermediate outputs to session_context; downstream agents read them.
-- UP
CREATE TABLE session_context (
    id              BIGSERIAL PRIMARY KEY,
    session_id      UUID NOT NULL,
    key             VARCHAR(128) NOT NULL,
    value           JSONB NOT NULL,
    written_by      VARCHAR(64) NOT NULL,
    written_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ttl_seconds     INTEGER NOT NULL DEFAULT 86400 CHECK (ttl_seconds > 0),
    expires_at      TIMESTAMPTZ GENERATED ALWAYS AS (written_at + (ttl_seconds || ' seconds')::INTERVAL) STORED,
    UNIQUE (session_id, key)
);

COMMENT ON TABLE session_context IS 'Session key-value store for inter-agent context passing within pipeline runs';
COMMENT ON COLUMN session_context.ttl_seconds IS 'Time-to-live in seconds. Default 86400 (24 hours). Expired rows cleaned by background job.';

-- DOWN
DROP TABLE IF EXISTS session_context;
```

### Migration 007: approval_requests

```sql
-- Migration 007: Create approval_requests table
-- UP
CREATE TABLE approval_requests (
    approval_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL,
    run_id          UUID REFERENCES pipeline_runs(run_id) ON DELETE SET NULL,
    project_id      VARCHAR(64),
    pipeline_name   VARCHAR(128) NOT NULL,
    step_number     INTEGER NOT NULL CHECK (step_number >= 0),
    step_name       VARCHAR(128) NOT NULL,
    summary         TEXT NOT NULL,
    risk_level      VARCHAR(16) NOT NULL DEFAULT 'medium'
                    CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    status          VARCHAR(16) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'rejected', 'expired', 'escalated')),
    context         JSONB DEFAULT '{}',
    approver_channel VARCHAR(256),
    decision_by     VARCHAR(128),
    decision_comment TEXT,
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ NOT NULL
);

-- Rejection requires a comment
ALTER TABLE approval_requests
    ADD CONSTRAINT chk_rejection_comment CHECK (
        status != 'rejected' OR decision_comment IS NOT NULL
    );

COMMENT ON TABLE approval_requests IS 'Human approval gate requests for pipeline steps';

-- DOWN
DROP TABLE IF EXISTS approval_requests;
```

### Migration 008: pipeline_checkpoints

```sql
-- Migration 008: Create pipeline_checkpoints table
-- UP
CREATE TABLE pipeline_checkpoints (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    session_id      UUID NOT NULL,
    pipeline_name   VARCHAR(128) NOT NULL,
    last_step_number INTEGER NOT NULL CHECK (last_step_number >= 0),
    last_step_name  VARCHAR(128) NOT NULL,
    step_results    JSONB NOT NULL DEFAULT '{}',
    status          VARCHAR(32) NOT NULL DEFAULT 'in_progress'
                    CHECK (status IN ('in_progress', 'paused', 'completed', 'failed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_checkpoints_run ON pipeline_checkpoints(run_id);

COMMENT ON TABLE pipeline_checkpoints IS 'Pipeline execution checkpoints for resume-after-failure';

-- DOWN
DROP INDEX IF EXISTS idx_checkpoints_run;
DROP TABLE IF EXISTS pipeline_checkpoints;
```

### Migration 009: mcp_call_events + agent_registry ALTER

```sql
-- Migration 009: Create mcp_call_events table and extend agent_registry for versioning
-- UP

-- 009a: MCP call event tracking (for MCP Monitoring Panel on Dashboard)
CREATE TABLE mcp_call_events (
    id              BIGSERIAL PRIMARY KEY,
    call_id         UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    server_name     VARCHAR(64) NOT NULL
                    CHECK (server_name IN ('agentic-sdlc-agents', 'agentic-sdlc-governance', 'agentic-sdlc-knowledge')),
    tool_name       VARCHAR(128) NOT NULL,
    caller          VARCHAR(256) NOT NULL,
    project_id      VARCHAR(64),
    duration_ms     INTEGER NOT NULL DEFAULT 0 CHECK (duration_ms >= 0),
    status          VARCHAR(16) NOT NULL DEFAULT 'success'
                    CHECK (status IN ('success', 'error', 'timeout')),
    error_message   TEXT,
    tokens_used     INTEGER NOT NULL DEFAULT 0 CHECK (tokens_used >= 0),
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    called_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE mcp_call_events IS 'MCP tool invocation log for observability and the MCP Monitoring Panel';

-- 009b: Extend agent_registry with versioning and maturity columns
ALTER TABLE agent_registry
    ADD COLUMN IF NOT EXISTS canary_version VARCHAR(32),
    ADD COLUMN IF NOT EXISTS canary_traffic_pct SMALLINT NOT NULL DEFAULT 0
        CHECK (canary_traffic_pct >= 0 AND canary_traffic_pct <= 100),
    ADD COLUMN IF NOT EXISTS previous_version VARCHAR(32),
    ADD COLUMN IF NOT EXISTS maturity_level VARCHAR(32) NOT NULL DEFAULT 'supervised'
        CHECK (maturity_level IN ('supervised', 'assisted', 'autonomous', 'fully_autonomous')),
    ADD COLUMN IF NOT EXISTS promoted_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS rolled_back_at TIMESTAMPTZ;

-- DOWN
ALTER TABLE agent_registry
    DROP COLUMN IF EXISTS canary_version,
    DROP COLUMN IF EXISTS canary_traffic_pct,
    DROP COLUMN IF EXISTS previous_version,
    DROP COLUMN IF EXISTS maturity_level,
    DROP COLUMN IF EXISTS promoted_at,
    DROP COLUMN IF EXISTS rolled_back_at;

DROP TABLE IF EXISTS mcp_call_events;
```

### Complete agent_registry After All Migrations

For reference, the `agent_registry` table after migrations 001 + 009 has these columns:

| Column | Type | Nullable | Default | Source |
|--------|------|----------|---------|--------|
| `id` | BIGSERIAL | NOT NULL | auto | Migration 001 |
| `agent_id` | VARCHAR(64) | NOT NULL | — | Migration 001 |
| `name` | VARCHAR(256) | NOT NULL | — | Migration 001 |
| `phase` | VARCHAR(32) | NOT NULL | — | Migration 001 |
| `archetype` | VARCHAR(64) | NOT NULL | — | Migration 001 |
| `model` | VARCHAR(64) | NOT NULL | `'claude-sonnet-4-6'` | Migration 001 |
| `status` | VARCHAR(16) | NOT NULL | `'active'` | Migration 001 |
| `active_version` | VARCHAR(32) | NULL | `'1.0.0'` | Migration 001 |
| `canary_version` | VARCHAR(32) | NULL | NULL | Migration 009 |
| `canary_traffic_pct` | SMALLINT | NOT NULL | `0` | Migration 009 |
| `previous_version` | VARCHAR(32) | NULL | NULL | Migration 009 |
| `maturity_level` | VARCHAR(32) | NOT NULL | `'supervised'` | Migration 009 |
| `promoted_at` | TIMESTAMPTZ | NULL | NULL | Migration 009 |
| `rolled_back_at` | TIMESTAMPTZ | NULL | NULL | Migration 009 |
| `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | Migration 001 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | Migration 001 |

---

## 4. Indexes

Indexes are organized by consumer to ensure every hot query path is covered. Each index references the specific interaction or dashboard query it accelerates.

### MCP Tool Query Indexes

```sql
-- I-020: list_agents — WHERE phase = $1 AND status = $2 ORDER BY name
CREATE INDEX idx_agents_phase_status
    ON agent_registry(phase, status, name);

-- I-040: get_cost_report — WHERE project_id = $1 AND recorded_at > $2 GROUP BY agent_id
CREATE INDEX idx_cost_project_date
    ON cost_metrics(project_id, recorded_at DESC);

-- I-040: get_cost_report — GROUP BY agent_id for breakdown
CREATE INDEX idx_cost_agent_project
    ON cost_metrics(agent_id, project_id, recorded_at DESC);

-- I-042: query_audit_events — WHERE project_id = $1 AND severity >= $2 AND created_at > $3
CREATE INDEX idx_audit_project_severity
    ON audit_events(project_id, severity, created_at DESC);

-- I-045: list_pending_approvals — WHERE status = 'PENDING' AND project_id = $1
CREATE INDEX idx_approvals_pending
    ON approval_requests(status, project_id, expires_at ASC)
    WHERE status = 'pending';

-- I-003: list_pipeline_runs — WHERE project_id = $1 AND status = $2 ORDER BY started_at DESC
CREATE INDEX idx_pipelines_project_status
    ON pipeline_runs(project_id, status, started_at DESC);

-- I-060: search_exceptions — full-text search on title + rule
CREATE INDEX idx_exceptions_search
    ON knowledge_exceptions
    USING GIN(to_tsvector('english', title || ' ' || rule));

-- I-060: search_exceptions — WHERE tier = $1
CREATE INDEX idx_exceptions_tier
    ON knowledge_exceptions(tier, active)
    WHERE active = TRUE;

-- Session context lookup for pipeline inter-agent context passing
CREATE INDEX idx_session_lookup
    ON session_context(session_id, key);

-- Session context TTL cleanup
CREATE INDEX idx_session_expires
    ON session_context(expires_at)
    WHERE expires_at IS NOT NULL;
```

### Dashboard Query Indexes

```sql
-- Fleet Health page: SELECT * FROM agent_registry WHERE status = 'active' ORDER BY phase, name
CREATE INDEX idx_agents_active
    ON agent_registry(phase, name)
    WHERE status = 'active';

-- Cost Monitor: date_trunc('day', recorded_at) aggregation
CREATE INDEX idx_cost_daily
    ON cost_metrics(project_id, (date_trunc('day', recorded_at)));

-- Audit Log: recent errors and criticals
CREATE INDEX idx_audit_recent_errors
    ON audit_events(created_at DESC)
    WHERE severity IN ('error', 'critical');

-- MCP Monitoring Panel: recent calls ordered by time
CREATE INDEX idx_mcp_calls_recent
    ON mcp_call_events(called_at DESC);

-- MCP Monitoring Panel: filter by server
CREATE INDEX idx_mcp_calls_server
    ON mcp_call_events(server_name, called_at DESC);

-- Approval Queue: history view (non-pending)
CREATE INDEX idx_approvals_history
    ON approval_requests(decided_at DESC)
    WHERE status != 'pending';
```

### Pipeline and Internal Indexes

```sql
-- Pipeline steps: fetch all steps for a run
CREATE INDEX idx_steps_run_id
    ON pipeline_steps(run_id, step_number);

-- Pipeline runs: by run_id for direct lookup
-- (Already covered by UNIQUE constraint on run_id)

-- Pipeline checkpoints: lookup by session
CREATE INDEX idx_checkpoints_session
    ON pipeline_checkpoints(session_id);

-- Audit events: by session_id for session-scoped queries
CREATE INDEX idx_audit_session
    ON audit_events(session_id, created_at DESC);

-- Cost metrics: by session for per-invocation cost lookup
CREATE INDEX idx_cost_session
    ON cost_metrics(session_id);

-- MCP calls: by project_id for project-scoped observability
CREATE INDEX idx_mcp_calls_project
    ON mcp_call_events(project_id, called_at DESC)
    WHERE project_id IS NOT NULL;
```

### Index Summary

| # | Index Name | Table | Columns | Type | Partial? | Primary Consumer |
|---|-----------|-------|---------|------|----------|-----------------|
| 1 | `idx_agents_phase_status` | agent_registry | phase, status, name | B-tree | No | MCP list_agents |
| 2 | `idx_cost_project_date` | cost_metrics | project_id, recorded_at DESC | B-tree | No | MCP get_cost_report |
| 3 | `idx_cost_agent_project` | cost_metrics | agent_id, project_id, recorded_at DESC | B-tree | No | MCP get_cost_report breakdown |
| 4 | `idx_audit_project_severity` | audit_events | project_id, severity, created_at DESC | B-tree | No | MCP query_audit_events |
| 5 | `idx_approvals_pending` | approval_requests | status, project_id, expires_at | B-tree | Yes (pending) | MCP list_pending_approvals |
| 6 | `idx_pipelines_project_status` | pipeline_runs | project_id, status, started_at DESC | B-tree | No | MCP list_pipeline_runs |
| 7 | `idx_exceptions_search` | knowledge_exceptions | title + rule (tsvector) | GIN | No | MCP search_exceptions |
| 8 | `idx_exceptions_tier` | knowledge_exceptions | tier, active | B-tree | Yes (active) | MCP list_exceptions |
| 9 | `idx_session_lookup` | session_context | session_id, key | B-tree | No | Pipeline execution |
| 10 | `idx_session_expires` | session_context | expires_at | B-tree | Yes (non-null) | TTL cleanup job |
| 11 | `idx_agents_active` | agent_registry | phase, name | B-tree | Yes (active) | Dashboard Fleet Health |
| 12 | `idx_cost_daily` | cost_metrics | project_id, date_trunc | B-tree | No | Dashboard Cost Monitor |
| 13 | `idx_audit_recent_errors` | audit_events | created_at DESC | B-tree | Yes (error/critical) | Dashboard Audit Log |
| 14 | `idx_mcp_calls_recent` | mcp_call_events | called_at DESC | B-tree | No | Dashboard MCP Panel |
| 15 | `idx_mcp_calls_server` | mcp_call_events | server_name, called_at DESC | B-tree | No | Dashboard MCP Panel |
| 16 | `idx_approvals_history` | approval_requests | decided_at DESC | B-tree | Yes (non-pending) | Dashboard Approval history |
| 17 | `idx_steps_run_id` | pipeline_steps | run_id, step_number | B-tree | No | Pipeline detail view |
| 18 | `idx_checkpoints_session` | pipeline_checkpoints | session_id | B-tree | No | Pipeline resume |
| 19 | `idx_audit_session` | audit_events | session_id, created_at DESC | B-tree | No | Session-scoped audit |
| 20 | `idx_cost_session` | cost_metrics | session_id | B-tree | No | Per-invocation cost |
| 21 | `idx_mcp_calls_project` | mcp_call_events | project_id, called_at DESC | B-tree | Yes (non-null) | Project MCP observability |

**Total: 21 indexes** (plus unique constraints and primary keys acting as implicit indexes).

---

## 5. Row-Level Security (RLS)

Row-Level Security ensures multi-tenant data isolation. RLS policies are scoped by `project_id` for project-level tables and `session_id` for session-scoped tables. The application sets `app.current_project_id` and `app.current_session_id` via `SET LOCAL` at the start of each transaction.

### RLS Setup

```sql
-- Enable RLS on multi-tenant tables
ALTER TABLE cost_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_call_events ENABLE ROW LEVEL SECURITY;

-- Force RLS for table owners too (defense in depth)
ALTER TABLE cost_metrics FORCE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs FORCE ROW LEVEL SECURITY;
ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;
ALTER TABLE approval_requests FORCE ROW LEVEL SECURITY;
ALTER TABLE session_context FORCE ROW LEVEL SECURITY;
ALTER TABLE mcp_call_events FORCE ROW LEVEL SECURITY;
```

### Project-Scoped Policies

```sql
-- cost_metrics: project_id isolation
CREATE POLICY cost_metrics_project_isolation ON cost_metrics
    USING (project_id = current_setting('app.current_project_id', TRUE))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE));

-- pipeline_runs: project_id isolation
CREATE POLICY pipeline_runs_project_isolation ON pipeline_runs
    USING (project_id = current_setting('app.current_project_id', TRUE))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE));

-- audit_events: project_id isolation (SELECT only — table is immutable)
CREATE POLICY audit_events_project_isolation ON audit_events
    FOR SELECT
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        OR project_id IS NULL  -- system events visible to all
    );

-- audit_events: INSERT policy (anyone can insert, no project_id restriction on write)
CREATE POLICY audit_events_insert ON audit_events
    FOR INSERT
    WITH CHECK (TRUE);

-- approval_requests: project_id isolation
CREATE POLICY approval_requests_project_isolation ON approval_requests
    USING (project_id = current_setting('app.current_project_id', TRUE))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE));

-- mcp_call_events: project_id isolation
CREATE POLICY mcp_call_events_project_isolation ON mcp_call_events
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        OR project_id IS NULL  -- system-level calls visible to all
    )
    WITH CHECK (TRUE);
```

### Session-Scoped Policies

```sql
-- session_context: session_id isolation
CREATE POLICY session_context_session_isolation ON session_context
    USING (session_id = current_setting('app.current_session_id', TRUE)::UUID)
    WITH CHECK (session_id = current_setting('app.current_session_id', TRUE)::UUID);
```

### Application-Level RLS Usage

```sql
-- At the start of each request, the shared service layer sets the context:
BEGIN;
SET LOCAL app.current_project_id = 'proj_abc123def456';
SET LOCAL app.current_session_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

-- All subsequent queries in this transaction are automatically filtered by RLS.
-- Example: this returns only rows for proj_abc123def456
SELECT * FROM cost_metrics WHERE recorded_at > NOW() - INTERVAL '7 days';

COMMIT;
```

### Superuser Bypass Role

```sql
-- Create a bypass role for administrative operations (migrations, bulk exports)
CREATE ROLE sdlc_admin BYPASSRLS;
-- Application role does NOT bypass RLS
CREATE ROLE sdlc_app NOINHERIT;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO sdlc_app;
```

---

## 6. Query Pattern Registry

Every consumer (MCP tool, REST endpoint, Dashboard screen) maps to a specific query pattern, the index that accelerates it, and estimated row counts.

### Pipeline Operations

| # | Consumer | Operation | Interaction | Query Pattern | Index Used | Est. Rows |
|---|----------|-----------|-------------|---------------|------------|-----------|
| 1 | MCP | `trigger_pipeline` | I-001 | `INSERT INTO pipeline_runs (...) RETURNING *` | PK | 1 |
| 2 | MCP | `get_pipeline_status` | I-002 | `SELECT * FROM pipeline_runs WHERE run_id = $1` | UNIQUE(run_id) | 1 |
| 3 | MCP + Dashboard | `list_pipeline_runs` | I-003 | `SELECT * FROM pipeline_runs WHERE project_id = $1 AND status = $2 ORDER BY started_at DESC LIMIT $3` | idx_pipelines_project_status | 10-50 |
| 4 | MCP | `resume_pipeline` | I-004 | `UPDATE pipeline_runs SET status = 'running' WHERE run_id = $1 AND status = 'paused'` | UNIQUE(run_id) | 1 |
| 5 | MCP | `cancel_pipeline` | I-005 | `UPDATE pipeline_runs SET status = 'cancelled', completed_at = NOW() WHERE run_id = $1` | UNIQUE(run_id) | 1 |
| 6 | MCP + Dashboard | `get_pipeline_documents` | I-006 | `SELECT * FROM pipeline_steps WHERE run_id = $1 AND status = 'completed' ORDER BY step_number` | idx_steps_run_id | 14 |
| 7 | MCP | `retry_pipeline_step` | I-007 | `UPDATE pipeline_steps SET status = 'pending' WHERE run_id = $1 AND step_number = $2` | idx_steps_run_id | 1 |

### Agent Operations

| # | Consumer | Operation | Interaction | Query Pattern | Index Used | Est. Rows |
|---|----------|-----------|-------------|---------------|------------|-----------|
| 8 | MCP + Dashboard | `list_agents` | I-020 | `SELECT * FROM agent_registry WHERE phase = $1 AND status = $2 ORDER BY name` | idx_agents_phase_status | 5-48 |
| 9 | MCP + Dashboard | `get_agent` | I-021 | `SELECT * FROM agent_registry WHERE agent_id = $1` | UNIQUE(agent_id) | 1 |
| 10 | Dashboard | Fleet Health grid | I-020 | `SELECT * FROM agent_registry WHERE status = 'active' ORDER BY phase, name` | idx_agents_active | 48 |
| 11 | MCP | `promote_agent_version` | I-024 | `UPDATE agent_registry SET active_version = canary_version, canary_version = NULL, canary_traffic_pct = 0, promoted_at = NOW() WHERE agent_id = $1` | UNIQUE(agent_id) | 1 |
| 12 | MCP | `rollback_agent_version` | I-025 | `UPDATE agent_registry SET active_version = previous_version, rolled_back_at = NOW() WHERE agent_id = $1` | UNIQUE(agent_id) | 1 |

### Cost and Budget Operations

| # | Consumer | Operation | Interaction | Query Pattern | Index Used | Est. Rows |
|---|----------|-----------|-------------|---------------|------------|-----------|
| 13 | MCP + Dashboard | `get_cost_report` | I-040 | `SELECT agent_id, SUM(cost_usd), COUNT(*) FROM cost_metrics WHERE project_id = $1 AND recorded_at > $2 GROUP BY agent_id` | idx_cost_project_date | 100-5000 agg to 48 |
| 14 | Dashboard | Cost daily chart | I-040 | `SELECT agent_id, SUM(cost_usd), date_trunc('day', recorded_at) AS day FROM cost_metrics WHERE project_id = $1 AND recorded_at > $2 GROUP BY agent_id, day` | idx_cost_daily | 100-5000 agg to ~300 |
| 15 | MCP + Dashboard | `check_budget` | I-041 | `SELECT SUM(cost_usd) FROM cost_metrics WHERE project_id = $1 AND recorded_at > date_trunc('day', NOW())` | idx_cost_project_date | 50-500 agg to 1 |

### Audit Operations

| # | Consumer | Operation | Interaction | Query Pattern | Index Used | Est. Rows |
|---|----------|-----------|-------------|---------------|------------|-----------|
| 16 | MCP + Dashboard | `query_audit_events` | I-042 | `SELECT * FROM audit_events WHERE project_id = $1 AND severity IN ($2) AND created_at > $3 ORDER BY created_at DESC LIMIT $4` | idx_audit_project_severity | 50-100 |
| 17 | Dashboard | Audit recent errors | I-042 | `SELECT * FROM audit_events WHERE severity IN ('error', 'critical') ORDER BY created_at DESC LIMIT 100` | idx_audit_recent_errors | 100 |
| 18 | MCP + Dashboard | `get_audit_summary` | I-043 | `SELECT severity, COUNT(*) FROM audit_events WHERE project_id = $1 AND created_at > $2 GROUP BY severity` | idx_audit_project_severity | 1000-10000 agg to 4 |

### Approval Operations

| # | Consumer | Operation | Interaction | Query Pattern | Index Used | Est. Rows |
|---|----------|-----------|-------------|---------------|------------|-----------|
| 19 | MCP + Dashboard | `list_pending_approvals` | I-045 | `SELECT * FROM approval_requests WHERE status = 'pending' AND project_id = $1 ORDER BY expires_at ASC` | idx_approvals_pending | 0-10 |
| 20 | MCP | `approve_gate` | I-046 | `UPDATE approval_requests SET status = 'approved', decided_at = NOW(), decision_by = $2 WHERE approval_id = $1 AND status = 'pending'` | PK | 1 |
| 21 | MCP | `reject_gate` | I-047 | `UPDATE approval_requests SET status = 'rejected', decided_at = NOW(), decision_by = $2, decision_comment = $3 WHERE approval_id = $1 AND status = 'pending'` | PK | 1 |
| 22 | Dashboard | Approval history | I-045 | `SELECT * FROM approval_requests WHERE status != 'pending' ORDER BY decided_at DESC LIMIT 50` | idx_approvals_history | 50 |

### Knowledge Operations

| # | Consumer | Operation | Interaction | Query Pattern | Index Used | Est. Rows |
|---|----------|-----------|-------------|---------------|------------|-----------|
| 23 | MCP | `search_exceptions` | I-060 | `SELECT * FROM knowledge_exceptions WHERE tier = $1 AND to_tsvector('english', title \|\| ' ' \|\| rule) @@ plainto_tsquery($2)` | idx_exceptions_search + idx_exceptions_tier | 5-20 |
| 24 | MCP | `list_exceptions` | I-063 | `SELECT * FROM knowledge_exceptions WHERE tier = $1 AND active = TRUE ORDER BY fire_count DESC` | idx_exceptions_tier | 10-50 |
| 25 | MCP | `create_exception` | I-061 | `INSERT INTO knowledge_exceptions (...) RETURNING *` | PK | 1 |

### MCP and System Operations

| # | Consumer | Operation | Interaction | Query Pattern | Index Used | Est. Rows |
|---|----------|-----------|-------------|---------------|------------|-----------|
| 26 | Dashboard | MCP call feed | I-082 | `SELECT * FROM mcp_call_events ORDER BY called_at DESC LIMIT 50` | idx_mcp_calls_recent | 50 |
| 27 | Dashboard | MCP calls by server | I-082 | `SELECT * FROM mcp_call_events WHERE server_name = $1 ORDER BY called_at DESC LIMIT 50` | idx_mcp_calls_server | 50 |
| 28 | MCP + Dashboard | Fleet health | I-080 | `SELECT status, COUNT(*) FROM agent_registry GROUP BY status` | idx_agents_phase_status | 48 agg to 4 |
| 29 | Internal | Session read | — | `SELECT value FROM session_context WHERE session_id = $1 AND key = $2` | idx_session_lookup | 1 |
| 30 | Internal | Session write | — | `INSERT INTO session_context (session_id, key, value, written_by) VALUES ($1, $2, $3, $4) ON CONFLICT (session_id, key) DO UPDATE SET value = $3, written_at = NOW()` | UNIQUE(session_id, key) | 1 |

---

## 7. Capacity Estimates

Projections assume a team of 5-8 engineers performing 5-10 pipeline runs per day in steady state, with 48 registered agents.

| Table | Growth Rate | Est. 1yr Rows | Est. Size | Archival Strategy |
|-------|------------|---------------|-----------|-------------------|
| `agent_registry` | ~0 (static 48 rows, occasional updates) | 48 | < 100 KB | No archival needed. Version history in git. |
| `cost_metrics` | 200-500 rows/day | 73K - 182K | 15 - 40 MB | Archive rows older than 90 days to `cost_metrics_archive`. Retain aggregates in materialized view. |
| `audit_events` | 300-1000 rows/day | 110K - 365K | 50 - 200 MB | Archive rows older than 1 year to JSONL files for compliance. Keep 90-day window in main table. |
| `pipeline_runs` | 5-10 rows/day | 1.8K - 3.6K | 1 - 3 MB | Archive completed runs older than 6 months. |
| `pipeline_steps` | 70-140 rows/day (14 per run) | 25K - 51K | 10 - 25 MB | Archive with parent pipeline_runs. |
| `knowledge_exceptions` | 10-50 rows/month | 120 - 600 | < 1 MB | No archival needed. Inactive exceptions soft-deleted (active=false). |
| `session_context` | 140-280 rows/day (auto-expired) | ~10K active (TTL-cleaned) | 5 - 20 MB | Automatic: background job deletes rows where `expires_at < NOW()` every hour. |
| `approval_requests` | 5-20 rows/day | 1.8K - 7.3K | 1 - 5 MB | Archive decided requests older than 1 year. |
| `pipeline_checkpoints` | 5-10 rows/day (one per active run) | ~100 active (cleaned on completion) | < 1 MB | Delete checkpoint when pipeline completes. Keep failed checkpoints for 30 days. |
| `mcp_call_events` | 200-1000 rows/day | 73K - 365K | 30 - 150 MB | Archive rows older than 90 days. Retain hourly aggregates for trending. |

### Total Estimated Storage (1 year)

| Scenario | Active Data | Archived Data | Total |
|----------|------------|---------------|-------|
| Low usage (5 runs/day) | ~120 MB | ~200 MB | ~320 MB |
| High usage (10 runs/day) | ~450 MB | ~600 MB | ~1 GB |

### Archival Implementation

```sql
-- Example: Archive cost_metrics older than 90 days
-- Run as a scheduled job (cron or pg_cron)

-- Step 1: Copy to archive table (same schema, no indexes)
INSERT INTO cost_metrics_archive
SELECT * FROM cost_metrics
WHERE recorded_at < NOW() - INTERVAL '90 days';

-- Step 2: Delete archived rows from main table
DELETE FROM cost_metrics
WHERE recorded_at < NOW() - INTERVAL '90 days';

-- Step 3: Clean up session_context expired rows
DELETE FROM session_context
WHERE expires_at < NOW();

-- Step 4: Clean up completed pipeline checkpoints
DELETE FROM pipeline_checkpoints
WHERE status = 'completed'
  AND updated_at < NOW() - INTERVAL '7 days';
```

---

## 8. Migration Strategy

### Migration File Inventory

| File | Table(s) | Type | Priority | Dependency |
|------|----------|------|----------|------------|
| `001_create_agents.sql` | agent_registry | CREATE | Existing | None |
| `002_create_cost_metrics.sql` | cost_metrics | CREATE | Existing | 001 (FK to agent_registry) |
| `003_create_audit_events.sql` | audit_events | CREATE + TRIGGER | Existing | None |
| `004_create_pipelines.sql` | pipeline_runs, pipeline_steps | CREATE | Existing | 001 (FK to agent_registry) |
| `005_create_knowledge_exceptions.sql` | knowledge_exceptions | CREATE | P1 | None |
| `006_create_session_context.sql` | session_context | CREATE | P1 BLOCKING | None |
| `007_create_approval_requests.sql` | approval_requests | CREATE | P2 | 004 (FK to pipeline_runs) |
| `008_create_pipeline_checkpoints.sql` | pipeline_checkpoints | CREATE | P2 | 004 (FK to pipeline_runs) |
| `009_create_mcp_events_alter_agents.sql` | mcp_call_events + ALTER agent_registry | CREATE + ALTER | P2 | 001 (ALTER agent_registry) |

### Migration Execution Order

```
001 ──┬── 002
      ├── 003 (independent)
      ├── 004 ──┬── 007
      │         └── 008
      └── 009 (ALTER agent_registry)
005 (independent)
006 (independent, BLOCKING — run first after 001-004)
```

### Zero-Downtime Deployment Pattern

For ALTER TABLE operations (migration 009), follow this sequence to avoid locking:

```
Phase 1: ADD COLUMN with DEFAULT (no table rewrite in PG 11+)
  ALTER TABLE agent_registry ADD COLUMN IF NOT EXISTS canary_version VARCHAR(32);
  -- This acquires a brief ACCESS EXCLUSIVE lock, then returns immediately.
  -- New rows get the default; existing rows have NULL.

Phase 2: BACKFILL (optional, in batches)
  UPDATE agent_registry SET maturity_level = 'supervised' WHERE maturity_level IS NULL;
  -- Run in batches of 100 if table is large. For 48 rows, single UPDATE is fine.

Phase 3: ADD CONSTRAINT (if needed)
  ALTER TABLE agent_registry ADD CONSTRAINT ... CHECK (...) NOT VALID;
  ALTER TABLE agent_registry VALIDATE CONSTRAINT ...;
  -- NOT VALID + VALIDATE avoids full table lock during validation.
```

### Migration Testing

Each migration includes both UP and DOWN scripts (shown in Section 3 DDL). Testing uses testcontainers:

```python
# Migration test pattern
import testcontainers.postgres

def test_migration_005_up_down():
    """Test knowledge_exceptions migration applies and rolls back cleanly."""
    with PostgresContainer("postgres:15") as pg:
        conn = pg.get_connection()

        # Apply migrations 001-004 (prerequisites)
        apply_migrations(conn, up_to=4)

        # Apply migration 005
        apply_migration(conn, 5, direction="up")
        assert table_exists(conn, "knowledge_exceptions")

        # Insert test data
        conn.execute("""
            INSERT INTO knowledge_exceptions (exception_id, title, rule, severity, tier, created_by)
            VALUES ('exc-001', 'Test', 'test rule', 'low', 'universal', 'test-user')
        """)

        # Rollback migration 005
        apply_migration(conn, 5, direction="down")
        assert not table_exists(conn, "knowledge_exceptions")
```

### Migration Safety Checklist

- [ ] Every migration has both UP and DOWN scripts
- [ ] DOWN scripts drop objects in reverse dependency order
- [ ] No migration modifies existing column types (always add new columns)
- [ ] Indexes created CONCURRENTLY in production (avoids table locks)
- [ ] Foreign keys validated after creation with `NOT VALID` + `VALIDATE`
- [ ] Tested with testcontainers against PostgreSQL 15
- [ ] Migration 006 (session_context) runs before any pipeline execution
- [ ] Migration 009 ALTER uses `ADD COLUMN IF NOT EXISTS` for idempotency

---

## 9. Supplementary Data Stores

### File System: Generated Documents

```
reports/
  {project_id}/
    {run_id}/
      00-ROADMAP.md
      01-PRD.md
      02-ARCH.md
      ...
      13-TESTING.md
    audit/
      audit-report-{timestamp}.pdf
      audit-report-{timestamp}.csv
```

- **Access pattern:** Write-once during pipeline execution, read-many for document retrieval (I-006).
- **Retention:** Permanent for completed pipeline runs. Deleted on pipeline run deletion (manual admin action).
- **Size estimate:** ~500 KB per run (14 documents), ~2.5 GB/year at 10 runs/day.

### YAML Configuration Files

```
agents/
  {agent-id}/
    manifest.yaml          # Agent manifest (9 subsystems)
    prompt.md              # System prompt template
archetypes/
  ci-gate.yaml
  reviewer.yaml
  co-pilot.yaml
  ...
teams/
  document-stack.yaml      # Pipeline definition (PipelineConfig shape source)
knowledge/
  client/{client_id}/
    overrides.yaml         # Client-specific agent overrides
```

- **Access pattern:** Read-only at runtime. `PipelineConfig` shape (I-008) reads from `teams/document-stack.yaml`. `AgentDetail` shape (I-021) reads from `agents/{id}/manifest.yaml`.
- **Mutability:** Changed only through git commits. Never modified by the application at runtime.

### JSONL Structured Logs

```
logs/
  audit-{date}.jsonl       # Daily audit event backup
  mcp-calls-{date}.jsonl   # Daily MCP call backup
  cost-{date}.jsonl        # Daily cost metric backup
```

- **Access pattern:** Append-only during operation. Read for compliance audits and disaster recovery.
- **Rotation:** Daily rotation. Compressed after 7 days. Retained for 3 years (compliance).
- **Format:** One JSON object per line, matching the database row schema plus a `_backed_up_at` timestamp.

### In-Memory State

| Store | Data | TTL | Eviction | Persistence |
|-------|------|-----|----------|-------------|
| Rate Limiter Token Buckets | Per-agent request counts | Rolling 60s window | Automatic (time-based) | None (rebuilt on restart) |
| Circuit Breaker State | Per-agent failure counts | Reset after success | Manual (health check) | None (all circuits closed on restart) |
| MCP Server Status Cache | Server health metrics | 5s TTL | Time-based refresh | None (re-polled on restart) |
| Fleet Health Cache | Aggregated fleet metrics | 10s TTL | Time-based refresh | None (re-computed on restart) |
| Agent Health Cache | Per-agent health check results | 30s TTL | Time-based refresh | None (re-checked on restart) |

---

## Appendix A: Entity-Relationship Summary

```
agent_registry (48 rows)
  ├── 1:N → cost_metrics (via agent_id)
  ├── 1:N → pipeline_steps (via agent_id)
  └── 1:N → audit_events (via agent_id, nullable)

pipeline_runs
  ├── 1:N → pipeline_steps (via run_id, CASCADE)
  ├── 1:N → pipeline_checkpoints (via run_id, CASCADE)
  └── 1:N → approval_requests (via run_id, SET NULL)

session_context (standalone, keyed by session_id + key)
knowledge_exceptions (standalone, keyed by exception_id)
mcp_call_events (standalone, keyed by call_id)
```

## Appendix B: Data Shape Completeness Verification

All 22 INTERACTION-MAP data shapes are accounted for:

| # | Shape | Storage | Verified |
|---|-------|---------|----------|
| 1 | PipelineRun | pipeline_runs table | Yes |
| 2 | PipelineDocument | pipeline_steps + filesystem | Yes |
| 3 | PipelineConfig | YAML files (in-memory cache) | Yes |
| 4 | ValidationResult | Computed in-memory (no persistence) | Yes |
| 5 | AgentSummary | agent_registry + cost_metrics aggregation | Yes |
| 6 | AgentDetail | agent_registry + YAML + cost_metrics | Yes |
| 7 | AgentHealth | In-memory health check state | Yes |
| 8 | AgentVersion | agent_registry columns (migration 009) | Yes |
| 9 | AgentMaturity | agent_registry + computed metrics | Yes |
| 10 | AgentInvocationResult | audit_events + cost_metrics | Yes |
| 11 | CostReport | cost_metrics aggregation | Yes |
| 12 | BudgetStatus | cost_metrics + env config | Yes |
| 13 | CostAnomaly | cost_metrics (computed on-the-fly) | Yes |
| 14 | AuditEvent | audit_events table | Yes |
| 15 | AuditSummary | audit_events aggregation | Yes |
| 16 | AuditReport | audit_events + filesystem | Yes |
| 17 | ApprovalRequest | approval_requests table | Yes |
| 18 | ApprovalResult | approval_requests table (subset) | Yes |
| 19 | KnowledgeException | knowledge_exceptions table | Yes |
| 20 | FleetHealth | Multi-table aggregation | Yes |
| 21 | McpServerStatus | In-memory (no persistence) | Yes |
| 22 | McpCallEvent | mcp_call_events table | Yes |
