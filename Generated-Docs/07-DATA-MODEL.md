# Data Model — Agentic SDLC Platform

| Field            | Value                                      |
| ---------------- | ------------------------------------------ |
| Document ID      | DM-ASDLC-001                               |
| Version          | 1.0.0                                      |
| Status           | Draft                                      |
| Owner            | Platform Engineering                       |
| Last Updated     | 2026-03-23                                 |
| Database         | PostgreSQL 15+                             |
| ORM              | None (raw SQL via asyncpg)                 |
| Migration Tool   | Plain SQL files (migrations/001_xxx.sql)   |
| Multi-Tenancy    | project_id + client_id columns with RLS    |

---

## 1. Overview

All persistent state for the Agentic SDLC Platform lives in a single PostgreSQL 15+ database. There is no ORM; all queries are raw SQL executed through asyncpg's connection pool. Multi-tenancy is enforced at the database level using Row-Level Security (RLS) policies keyed on `project_id` and `client_id`.

### 1.1 Data Store Inventory

| # | Table                  | Technology   | Purpose                                          | Mutability        | Migration |
|---|------------------------|-------------|--------------------------------------------------|-------------------|-----------|
| 1 | `agent_registry`       | PostgreSQL  | Catalog of all 48 agents with versioning          | Mutable (UPDATE)  | 001       |
| 2 | `cost_metrics`         | PostgreSQL  | Per-invocation API spend tracking                 | Append-only       | 002       |
| 3 | `audit_events`         | PostgreSQL  | Immutable compliance audit trail                  | Immutable         | 003       |
| 4 | `pipeline_runs`        | PostgreSQL  | Top-level pipeline execution records              | Mutable (status)  | 004       |
| 5 | `pipeline_steps`       | PostgreSQL  | Individual step outcomes within a pipeline run    | Mutable (status)  | 004       |
| 6 | `knowledge_exceptions` | PostgreSQL  | Tiered exception rules for knowledge management   | Mutable           | 005       |
| 7 | `session_context`      | PostgreSQL  | Shared key-value state across agents in a session | Mutable (upsert)  | 006       |
| 8 | `approval_requests`    | PostgreSQL  | Human-in-the-loop approval gate records           | Mutable (status)  | 007       |
| 9 | `pipeline_checkpoints` | PostgreSQL  | Resume-from-failure checkpoint snapshots           | Mutable (upsert)  | 008       |

### 1.2 Supplementary Stores (Non-PostgreSQL)

| Store              | Technology  | Purpose                                 | Retention |
|--------------------|------------|------------------------------------------|-----------|
| `reports/{pid}/`   | File system | Generated document artifacts (Markdown)  | Permanent |
| Agent manifests    | YAML files  | Agent configuration (loaded at startup)  | Permanent |
| Session logs       | JSONL files | Structured log output per session        | 90 days   |

---

## 2. Schema DDL

All tables use the `public` schema. Every multi-tenant table includes `project_id` and/or `client_id` columns for RLS enforcement.

### 2.1 agent_registry (Migration 001)

```sql
-- Migration: 001_create_agent_registry.sql
-- Purpose: Catalog of all 48 agents with model configuration and canary versioning.

CREATE TABLE agent_registry (
    id                  VARCHAR(64)     PRIMARY KEY,
    name                VARCHAR(128)    NOT NULL,
    phase               VARCHAR(32)     NOT NULL,
    archetype           VARCHAR(32)     NOT NULL,
    version             VARCHAR(32)     NOT NULL DEFAULT '1.0.0',
    status              VARCHAR(16)     NOT NULL DEFAULT 'active'
                                        CHECK (status IN ('active','inactive','deprecated','canary')),
    model               VARCHAR(64)     NOT NULL DEFAULT 'claude-sonnet-4-20250514',
    temperature         NUMERIC(3,2)    NOT NULL DEFAULT 0.7
                                        CHECK (temperature >= 0.0 AND temperature <= 2.0),
    max_tokens          INTEGER         NOT NULL DEFAULT 4096
                                        CHECK (max_tokens > 0 AND max_tokens <= 200000),

    -- FIX-05: Canary deployment versioning fields
    active_version      VARCHAR(32)     DEFAULT '1.0.0',
    canary_version      VARCHAR(32),
    canary_traffic_pct  NUMERIC(5,2)    DEFAULT 0.00
                                        CHECK (canary_traffic_pct >= 0.00 AND canary_traffic_pct <= 100.00),
    previous_version    VARCHAR(32),

    -- Multi-tenancy (agents are global but can be scoped)
    project_id          VARCHAR(64),
    client_id           VARCHAR(128),

    -- Metadata
    description         TEXT,
    manifest_path       VARCHAR(512),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Phase enum enforcement
COMMENT ON COLUMN agent_registry.phase IS
    'One of: requirements, design, implementation, testing, deployment, monitoring, operations';

COMMENT ON COLUMN agent_registry.archetype IS
    'One of: generator, reviewer, orchestrator, validator, ops';

-- Trigger: auto-update updated_at
CREATE OR REPLACE FUNCTION update_agent_registry_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_agent_registry_updated_at
    BEFORE UPDATE ON agent_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_registry_timestamp();
```

### 2.2 cost_metrics (Migration 002)

```sql
-- Migration: 002_create_cost_metrics.sql
-- Purpose: Per-invocation API spend tracking for cost governance (C3).

CREATE TABLE cost_metrics (
    id              BIGSERIAL       PRIMARY KEY,
    session_id      UUID            NOT NULL,
    agent_id        VARCHAR(64)     NOT NULL REFERENCES agent_registry(id),
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    model           VARCHAR(64)     NOT NULL,
    input_tokens    INTEGER         NOT NULL DEFAULT 0
                                    CHECK (input_tokens >= 0),
    output_tokens   INTEGER         NOT NULL DEFAULT 0
                                    CHECK (output_tokens >= 0),
    cost_usd        NUMERIC(12,6)   NOT NULL DEFAULT 0.000000
                                    CHECK (cost_usd >= 0),
    timestamp       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- Denormalized fields for fast aggregation
    pipeline_name   VARCHAR(128),
    phase           VARCHAR(32)
);

COMMENT ON TABLE cost_metrics IS
    'Append-only ledger of every LLM API call with token counts and USD cost.';
```

### 2.3 audit_events (Migration 003)

```sql
-- Migration: 003_create_audit_events.sql
-- Purpose: Immutable audit trail for compliance (C6). Q-033: No UPDATE/DELETE allowed.

CREATE TABLE audit_events (
    event_id        UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID            NOT NULL,
    correlation_id  UUID,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    agent_id        VARCHAR(64),
    event_type      VARCHAR(64)     NOT NULL,
    severity        VARCHAR(16)     NOT NULL DEFAULT 'INFO'
                                    CHECK (severity IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')),
    timestamp       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    payload         JSONB           NOT NULL DEFAULT '{}'::jsonb,
    environment     VARCHAR(32)     NOT NULL DEFAULT 'production'
                                    CHECK (environment IN ('development','staging','production')),
    source_ip       INET,
    user_agent      VARCHAR(512)
);

COMMENT ON TABLE audit_events IS
    'Immutable 13-field audit trail. Triggers prevent UPDATE and DELETE. Retention: 365 days.';

-- Q-033: Immutability triggers — prevent UPDATE
CREATE OR REPLACE FUNCTION prevent_audit_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'UPDATE on audit_events is forbidden (Q-033 immutability)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_no_update
    BEFORE UPDATE ON audit_events
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_update();

-- Q-033: Immutability triggers — prevent DELETE
CREATE OR REPLACE FUNCTION prevent_audit_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'DELETE on audit_events is forbidden (Q-033 immutability)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_no_delete
    BEFORE DELETE ON audit_events
    FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_delete();
```

### 2.4 pipeline_runs + pipeline_steps (Migration 004)

```sql
-- Migration: 004_create_pipeline_tables.sql
-- Purpose: Pipeline execution tracking for the 12-doc generation pipeline (C2) and resilience (C8).

CREATE TABLE pipeline_runs (
    run_id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_name   VARCHAR(128)    NOT NULL,
    session_id      UUID            NOT NULL,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    status          VARCHAR(32)     NOT NULL DEFAULT 'pending'
                                    CHECK (status IN ('pending','running','completed','failed','cancelled','paused')),
    started_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    cost_usd        NUMERIC(12,6)   DEFAULT 0.000000,
    step_count      INTEGER         NOT NULL DEFAULT 0
                                    CHECK (step_count >= 0),
    error_message   TEXT,
    config          JSONB           DEFAULT '{}'::jsonb
);

COMMENT ON TABLE pipeline_runs IS
    'Top-level record for each pipeline execution. Links to pipeline_steps via run_id.';

CREATE TABLE pipeline_steps (
    step_id         VARCHAR(64)     NOT NULL,
    run_id          UUID            NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    agent_id        VARCHAR(64)     NOT NULL REFERENCES agent_registry(id),
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    status          VARCHAR(32)     NOT NULL DEFAULT 'pending'
                                    CHECK (status IN ('pending','running','completed','failed','skipped')),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    input_hash      VARCHAR(64),
    output_hash     VARCHAR(64),
    cost_usd        NUMERIC(12,6)   DEFAULT 0.000000,
    error_message   TEXT,
    retry_count     INTEGER         DEFAULT 0,
    PRIMARY KEY (step_id, run_id)
);

COMMENT ON TABLE pipeline_steps IS
    'Individual step within a pipeline run. Each step maps to one agent invocation.';

-- Trigger: auto-update pipeline_runs.cost_usd when steps complete
CREATE OR REPLACE FUNCTION update_pipeline_run_cost()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE pipeline_runs
    SET cost_usd = (
        SELECT COALESCE(SUM(cost_usd), 0)
        FROM pipeline_steps
        WHERE run_id = NEW.run_id
    )
    WHERE run_id = NEW.run_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_step_cost_rollup
    AFTER INSERT OR UPDATE OF cost_usd ON pipeline_steps
    FOR EACH ROW
    EXECUTE FUNCTION update_pipeline_run_cost();
```

### 2.5 knowledge_exceptions (Migration 005)

```sql
-- Migration: 005_create_knowledge_exceptions.sql
-- Purpose: Tiered exception rules for knowledge management (C7, ADD-11).

CREATE TABLE knowledge_exceptions (
    exception_id    VARCHAR(64)     PRIMARY KEY,
    title           VARCHAR(256)    NOT NULL,
    rule            TEXT            NOT NULL,
    severity        VARCHAR(16)     NOT NULL
                                    CHECK (severity IN ('BLOCKER','WARNING','INFO')),
    tier            VARCHAR(16)     NOT NULL
                                    CHECK (tier IN ('universal','stack','client')),
    stack_name      VARCHAR(128),
    client_id       VARCHAR(128),
    project_id      VARCHAR(64),
    active          BOOLEAN         NOT NULL DEFAULT FALSE,
    applies_to_phases TEXT[],
    applies_to_agents TEXT[],
    fire_count      INTEGER         NOT NULL DEFAULT 0
                                    CHECK (fire_count >= 0),
    last_fired_at   TIMESTAMPTZ,
    promoted_by     VARCHAR(128),
    promoted_at     TIMESTAMPTZ,
    created_by      VARCHAR(128)    NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE knowledge_exceptions IS
    'Three-tier exception rules: universal (all projects), stack (tech-specific), client (org-specific).';

-- Constraint: stack_name required when tier = 'stack'
ALTER TABLE knowledge_exceptions
    ADD CONSTRAINT chk_stack_tier_name
    CHECK (tier != 'stack' OR stack_name IS NOT NULL);

-- Constraint: client_id required when tier = 'client'
ALTER TABLE knowledge_exceptions
    ADD CONSTRAINT chk_client_tier_id
    CHECK (tier != 'client' OR client_id IS NOT NULL);

-- Trigger: auto-update updated_at
CREATE OR REPLACE FUNCTION update_knowledge_exceptions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_knowledge_exceptions_updated_at
    BEFORE UPDATE ON knowledge_exceptions
    FOR EACH ROW
    EXECUTE FUNCTION update_knowledge_exceptions_timestamp();
```

### 2.6 session_context (Migration 006)

```sql
-- Migration: 006_create_session_context.sql
-- Purpose: Shared key-value state for agents within a session (C2, FIX-01 BLOCKING).
-- Q-034: Default TTL = 86400 seconds (24 hours).

CREATE TABLE session_context (
    id              BIGSERIAL       PRIMARY KEY,
    session_id      UUID            NOT NULL,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    key             VARCHAR(128)    NOT NULL,
    value           JSONB           NOT NULL,
    written_by      VARCHAR(64)     NOT NULL,
    written_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    ttl_seconds     INTEGER         NOT NULL DEFAULT 86400
                                    CHECK (ttl_seconds > 0 AND ttl_seconds <= 604800),
    version         INTEGER         NOT NULL DEFAULT 1,
    UNIQUE (session_id, key)
);

COMMENT ON TABLE session_context IS
    'Shared state bus for the 12-doc pipeline. Each agent writes its output doc here. TTL default: 24h.';

-- Q-035: Output size enforcement (100KB max)
ALTER TABLE session_context
    ADD CONSTRAINT chk_value_size
    CHECK (pg_column_size(value) <= 102400);

-- Well-known keys written by the 12-doc pipeline agents:
-- requirements_doc  (D1)  — Roadmap phases, milestones, timeline
-- prd_doc           (D2)  — Product vision, user stories, acceptance criteria
-- feature_catalog   (D3)  — Feature list with priority and description
-- enforcement_scaffold (D4) — Linting rules, coding standards config
-- architecture_doc  (D5)  — Component diagram, patterns, tech decisions
-- db_schema         (D6)  — Entity-relationship model, table definitions
-- api_contracts     (D7)  — OpenAPI/GraphQL contracts
-- task_list         (D8)  — Epics, stories, tickets with estimates
-- quality_spec      (D10) — Coverage targets, quality gates
-- test_strategy     (D11) — Test levels, tools, environments
```

### 2.7 approval_requests (Migration 007)

```sql
-- Migration: 007_create_approval_requests.sql
-- Purpose: Human-in-the-loop approval gate workflow (C4, FIX-02).

CREATE TABLE approval_requests (
    approval_id     UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID            NOT NULL,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    pipeline_name   VARCHAR(128)    NOT NULL,
    step_id         VARCHAR(64)     NOT NULL,
    summary         TEXT            NOT NULL,
    status          VARCHAR(16)     NOT NULL DEFAULT 'PENDING'
                                    CHECK (status IN ('PENDING','APPROVED','REJECTED','TIMEOUT')),
    approver_channel VARCHAR(256),
    decision_by     VARCHAR(128),
    decision_comment TEXT,
    requested_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    decided_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ     NOT NULL,
    escalation_sent BOOLEAN         NOT NULL DEFAULT FALSE,
    reminder_count  INTEGER         NOT NULL DEFAULT 0
);

COMMENT ON TABLE approval_requests IS
    'Each row represents a pending or resolved human approval gate in a pipeline.';

-- Constraint: decided_at required when status is not PENDING
ALTER TABLE approval_requests
    ADD CONSTRAINT chk_decision_timestamp
    CHECK (status = 'PENDING' OR decided_at IS NOT NULL);
```

### 2.8 pipeline_checkpoints (Migration 008)

```sql
-- Migration: 008_create_pipeline_checkpoints.sql
-- Purpose: Resume-from-failure checkpoint snapshots for pipeline resilience (C8, FIX-03).

CREATE TABLE pipeline_checkpoints (
    id              BIGSERIAL       PRIMARY KEY,
    session_id      UUID            NOT NULL,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    pipeline_name   VARCHAR(128)    NOT NULL,
    last_step_id    VARCHAR(64)     NOT NULL,
    step_results    JSONB           NOT NULL DEFAULT '{}'::jsonb,
    status          VARCHAR(32)     NOT NULL DEFAULT 'in_progress'
                                    CHECK (status IN ('in_progress','completed','failed','abandoned')),
    retry_count     INTEGER         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE pipeline_checkpoints IS
    'Stores the last successful step and accumulated results for pipeline resume-from-failure.';

-- Trigger: auto-update updated_at
CREATE OR REPLACE FUNCTION update_pipeline_checkpoints_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pipeline_checkpoints_updated_at
    BEFORE UPDATE ON pipeline_checkpoints
    FOR EACH ROW
    EXECUTE FUNCTION update_pipeline_checkpoints_timestamp();
```

---

## 3. Indexes

All indexes are listed with the queries they accelerate.

### 3.1 agent_registry Indexes

```sql
-- Lookup agents by phase (e.g., "list all testing-phase agents")
CREATE INDEX idx_agent_registry_phase ON agent_registry(phase);

-- Filter agents by status (e.g., "list all active agents")
CREATE INDEX idx_agent_registry_status ON agent_registry(status);

-- Multi-tenancy: filter agents by project scope
CREATE INDEX idx_agent_registry_project ON agent_registry(project_id)
    WHERE project_id IS NOT NULL;

-- Canary deployments: find agents with active canary traffic
CREATE INDEX idx_agent_registry_canary ON agent_registry(id)
    WHERE canary_version IS NOT NULL AND canary_traffic_pct > 0;
```

### 3.2 cost_metrics Indexes

```sql
-- Dashboard: cost by project over a time range
CREATE INDEX idx_cost_metrics_project_ts ON cost_metrics(project_id, timestamp DESC);

-- Dashboard: cost by agent over a time range
CREATE INDEX idx_cost_metrics_agent_ts ON cost_metrics(agent_id, timestamp DESC);

-- Dashboard: cost by session (drill-down)
CREATE INDEX idx_cost_metrics_session ON cost_metrics(session_id);

-- Aggregation: cost by model type
CREATE INDEX idx_cost_metrics_model ON cost_metrics(model, timestamp DESC);

-- Multi-tenancy: cost by client
CREATE INDEX idx_cost_metrics_client ON cost_metrics(client_id, timestamp DESC)
    WHERE client_id IS NOT NULL;

-- Retention cleanup: delete rows older than 90 days
CREATE INDEX idx_cost_metrics_timestamp ON cost_metrics(timestamp);
```

### 3.3 audit_events Indexes

```sql
-- Compliance queries: events by project in time range
CREATE INDEX idx_audit_events_project_ts ON audit_events(project_id, timestamp DESC);

-- Drill-down: events for a specific session
CREATE INDEX idx_audit_events_session ON audit_events(session_id, timestamp DESC);

-- Filtering: events by type (e.g., 'agent.invoked', 'pipeline.completed')
CREATE INDEX idx_audit_events_type ON audit_events(event_type, timestamp DESC);

-- Filtering: events by severity for alerting
CREATE INDEX idx_audit_events_severity ON audit_events(severity, timestamp DESC)
    WHERE severity IN ('ERROR', 'CRITICAL');

-- Correlation: trace an operation across agents
CREATE INDEX idx_audit_events_correlation ON audit_events(correlation_id)
    WHERE correlation_id IS NOT NULL;

-- Multi-tenancy: events by client
CREATE INDEX idx_audit_events_client ON audit_events(client_id, timestamp DESC)
    WHERE client_id IS NOT NULL;

-- JSONB payload search (GIN index for @> operator)
CREATE INDEX idx_audit_events_payload ON audit_events USING GIN (payload jsonb_path_ops);

-- Retention cleanup: delete rows older than 365 days
CREATE INDEX idx_audit_events_timestamp ON audit_events(timestamp);
```

### 3.4 pipeline_runs Indexes

```sql
-- Dashboard: runs by project ordered by recency
CREATE INDEX idx_pipeline_runs_project_ts ON pipeline_runs(project_id, started_at DESC);

-- Dashboard: runs by status for monitoring
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status, started_at DESC);

-- Lookup: runs for a specific session
CREATE INDEX idx_pipeline_runs_session ON pipeline_runs(session_id);

-- Multi-tenancy: runs by client
CREATE INDEX idx_pipeline_runs_client ON pipeline_runs(client_id, started_at DESC)
    WHERE client_id IS NOT NULL;
```

### 3.5 pipeline_steps Indexes

```sql
-- Step lookup by run (join from pipeline_runs)
CREATE INDEX idx_pipeline_steps_run ON pipeline_steps(run_id);

-- Step lookup by agent (agent performance analysis)
CREATE INDEX idx_pipeline_steps_agent ON pipeline_steps(agent_id, started_at DESC);

-- Multi-tenancy: steps by project
CREATE INDEX idx_pipeline_steps_project ON pipeline_steps(project_id);

-- Failure analysis: find failed steps
CREATE INDEX idx_pipeline_steps_failed ON pipeline_steps(run_id, status)
    WHERE status = 'failed';
```

### 3.6 knowledge_exceptions Indexes

```sql
-- Lookup active exceptions by tier
CREATE INDEX idx_knowledge_exceptions_tier ON knowledge_exceptions(tier, active)
    WHERE active = TRUE;

-- Lookup by severity for blocker checks
CREATE INDEX idx_knowledge_exceptions_severity ON knowledge_exceptions(severity)
    WHERE active = TRUE;

-- Filter by phase applicability (GIN for array containment)
CREATE INDEX idx_knowledge_exceptions_phases ON knowledge_exceptions USING GIN (applies_to_phases);

-- Filter by agent applicability (GIN for array containment)
CREATE INDEX idx_knowledge_exceptions_agents ON knowledge_exceptions USING GIN (applies_to_agents);

-- Multi-tenancy: exceptions by client
CREATE INDEX idx_knowledge_exceptions_client ON knowledge_exceptions(client_id)
    WHERE client_id IS NOT NULL;

-- Multi-tenancy: exceptions by project
CREATE INDEX idx_knowledge_exceptions_project ON knowledge_exceptions(project_id)
    WHERE project_id IS NOT NULL;
```

### 3.7 session_context Indexes

```sql
-- Primary lookup: get a key for a session (covers UNIQUE constraint)
CREATE INDEX idx_session_context_session_id ON session_context(session_id);

-- Key lookup within session (covered by the UNIQUE constraint above, but explicit for clarity)
CREATE INDEX idx_session_context_key ON session_context(session_id, key);

-- Multi-tenancy: context by project
CREATE INDEX idx_session_context_project ON session_context(project_id);

-- TTL cleanup: find expired rows
CREATE INDEX idx_session_context_expiry ON session_context(written_at, ttl_seconds);

-- Writer tracking: who wrote what
CREATE INDEX idx_session_context_writer ON session_context(written_by);
```

### 3.8 approval_requests Indexes

```sql
-- Dashboard: pending approvals for a project
CREATE INDEX idx_approval_requests_project_status ON approval_requests(project_id, status)
    WHERE status = 'PENDING';

-- Timeout checker: find expired pending requests
CREATE INDEX idx_approval_requests_expiry ON approval_requests(expires_at)
    WHERE status = 'PENDING';

-- Session drill-down: approvals for a session
CREATE INDEX idx_approval_requests_session ON approval_requests(session_id);

-- Multi-tenancy: approvals by client
CREATE INDEX idx_approval_requests_client ON approval_requests(client_id)
    WHERE client_id IS NOT NULL;
```

### 3.9 pipeline_checkpoints Indexes

```sql
-- Resume lookup: find the latest checkpoint for a session
CREATE UNIQUE INDEX idx_checkpoints_session ON pipeline_checkpoints(session_id);

-- Multi-tenancy: checkpoints by project
CREATE INDEX idx_checkpoints_project ON pipeline_checkpoints(project_id);

-- Cleanup: find stale in_progress checkpoints
CREATE INDEX idx_checkpoints_status ON pipeline_checkpoints(status, updated_at)
    WHERE status = 'in_progress';
```

---

## 4. Row-Level Security (RLS)

Every table containing `project_id` or `client_id` has RLS enabled. The application sets session variables before each query:

```sql
-- Application connection setup (run per-connection or per-transaction):
SET app.current_project_id = '<project_id>';
SET app.current_client_id  = '<client_id>';
```

### 4.1 RLS Policy Definitions

```sql
-- ============================================================
-- agent_registry: project-scoped (global agents have NULL project_id)
-- ============================================================
ALTER TABLE agent_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_registry FORCE ROW LEVEL SECURITY;

CREATE POLICY agent_registry_project_isolation ON agent_registry
    FOR ALL
    USING (
        project_id IS NULL
        OR project_id = current_setting('app.current_project_id', TRUE)
    )
    WITH CHECK (
        project_id IS NULL
        OR project_id = current_setting('app.current_project_id', TRUE)
    );

-- ============================================================
-- cost_metrics: strict project + client isolation
-- ============================================================
ALTER TABLE cost_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_metrics FORCE ROW LEVEL SECURITY;

CREATE POLICY cost_metrics_project_isolation ON cost_metrics
    FOR ALL
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    )
    WITH CHECK (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    );

-- ============================================================
-- audit_events: strict project + client isolation
-- ============================================================
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;

CREATE POLICY audit_events_project_isolation ON audit_events
    FOR ALL
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    )
    WITH CHECK (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    );

-- ============================================================
-- pipeline_runs: project + client isolation
-- ============================================================
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs FORCE ROW LEVEL SECURITY;

CREATE POLICY pipeline_runs_project_isolation ON pipeline_runs
    FOR ALL
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    )
    WITH CHECK (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    );

-- ============================================================
-- pipeline_steps: project + client isolation
-- ============================================================
ALTER TABLE pipeline_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_steps FORCE ROW LEVEL SECURITY;

CREATE POLICY pipeline_steps_project_isolation ON pipeline_steps
    FOR ALL
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    )
    WITH CHECK (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    );

-- ============================================================
-- knowledge_exceptions: tier-aware isolation
-- Universal tier visible to all; stack/client tiers scoped.
-- ============================================================
ALTER TABLE knowledge_exceptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_exceptions FORCE ROW LEVEL SECURITY;

CREATE POLICY knowledge_exceptions_isolation ON knowledge_exceptions
    FOR ALL
    USING (
        tier = 'universal'
        OR (tier = 'stack' AND (
            project_id IS NULL
            OR project_id = current_setting('app.current_project_id', TRUE)
        ))
        OR (tier = 'client' AND (
            client_id = current_setting('app.current_client_id', TRUE)
        ))
    )
    WITH CHECK (
        tier = 'universal'
        OR (tier = 'stack' AND (
            project_id IS NULL
            OR project_id = current_setting('app.current_project_id', TRUE)
        ))
        OR (tier = 'client' AND (
            client_id = current_setting('app.current_client_id', TRUE)
        ))
    );

-- ============================================================
-- session_context: project isolation
-- ============================================================
ALTER TABLE session_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_context FORCE ROW LEVEL SECURITY;

CREATE POLICY session_context_project_isolation ON session_context
    FOR ALL
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    )
    WITH CHECK (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    );

-- ============================================================
-- approval_requests: project + client isolation
-- ============================================================
ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_requests FORCE ROW LEVEL SECURITY;

CREATE POLICY approval_requests_project_isolation ON approval_requests
    FOR ALL
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    )
    WITH CHECK (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    );

-- ============================================================
-- pipeline_checkpoints: project + client isolation
-- ============================================================
ALTER TABLE pipeline_checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_checkpoints FORCE ROW LEVEL SECURITY;

CREATE POLICY pipeline_checkpoints_project_isolation ON pipeline_checkpoints
    FOR ALL
    USING (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    )
    WITH CHECK (
        project_id = current_setting('app.current_project_id', TRUE)
        AND (
            client_id IS NULL
            OR client_id = current_setting('app.current_client_id', TRUE)
        )
    );
```

### 4.2 Superuser Bypass Role

```sql
-- Admin role bypasses RLS for migrations and maintenance
CREATE ROLE asdlc_admin NOLOGIN;
GRANT ALL ON ALL TABLES IN SCHEMA public TO asdlc_admin;
ALTER TABLE agent_registry        OWNER TO asdlc_admin;
ALTER TABLE cost_metrics           OWNER TO asdlc_admin;
ALTER TABLE audit_events           OWNER TO asdlc_admin;
ALTER TABLE pipeline_runs          OWNER TO asdlc_admin;
ALTER TABLE pipeline_steps         OWNER TO asdlc_admin;
ALTER TABLE knowledge_exceptions   OWNER TO asdlc_admin;
ALTER TABLE session_context        OWNER TO asdlc_admin;
ALTER TABLE approval_requests      OWNER TO asdlc_admin;
ALTER TABLE pipeline_checkpoints   OWNER TO asdlc_admin;

-- Application role: RLS enforced
CREATE ROLE asdlc_app LOGIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO asdlc_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO asdlc_app;

-- Read-only role for dashboards
CREATE ROLE asdlc_readonly LOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO asdlc_readonly;
```

---

## 5. Capacity Estimates

Assumptions: 5 concurrent projects, 3 pipeline runs/project/day, 48 agents, 12 steps/pipeline.

| Table                  | Avg Row Size | Initial Rows | Daily Growth | Monthly Growth | 1-Year Projection |
|------------------------|-------------|-------------|-------------|---------------|-------------------|
| `agent_registry`       | 512 B       | 48          | ~1          | ~30           | ~400              |
| `cost_metrics`         | 256 B       | 0           | ~900        | ~27,000       | ~328,500          |
| `audit_events`         | 1 KB        | 0           | ~5,000      | ~150,000      | ~1,825,000        |
| `pipeline_runs`        | 512 B       | 0           | ~15         | ~450          | ~5,475            |
| `pipeline_steps`       | 384 B       | 0           | ~180        | ~5,400        | ~65,700           |
| `knowledge_exceptions` | 1 KB        | 50          | ~2          | ~60           | ~780              |
| `session_context`      | 8 KB        | 0           | ~150        | ~4,500        | ~54,750*          |
| `approval_requests`    | 512 B       | 0           | ~15         | ~450          | ~5,475            |
| `pipeline_checkpoints` | 4 KB        | 0           | ~15         | ~450          | ~5,475*           |

*After retention cleanup (30-day TTL for session_context, 30-day TTL for checkpoints).

### Storage Projections (1 year, before retention cleanup)

| Table              | Row Count   | Estimated Size | After Retention |
|--------------------|-------------|---------------|-----------------|
| `audit_events`     | 1,825,000   | ~1.74 GB      | 1.74 GB (365d)  |
| `cost_metrics`     | 328,500     | ~80 MB        | ~24 MB (90d)    |
| `session_context`  | 54,750      | ~418 MB       | ~35 MB (30d)    |
| `pipeline_steps`   | 65,700      | ~24 MB        | 24 MB (no TTL)  |
| `pipeline_runs`    | 5,475       | ~2.7 MB       | 2.7 MB (no TTL) |
| All others         | ~12,000     | ~10 MB        | ~10 MB          |
| **Total**          |             | **~2.3 GB**   | **~1.84 GB**    |

---

## 6. Migration Strategy

Migrations live in `migrations/` as plain SQL files. Each file contains both the upgrade DDL and a commented-out downgrade section. Migrations are applied in order and tracked in a `schema_migrations` table.

### 6.0 Schema Migrations Tracker

```sql
-- migrations/000_schema_migrations.sql
-- UPGRADE:
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER     PRIMARY KEY,
    name        VARCHAR(256) NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    checksum    VARCHAR(64)
);

-- DOWNGRADE:
-- DROP TABLE IF EXISTS schema_migrations;
```

### 6.1 Migration 001 — agent_registry

```sql
-- migrations/001_create_agent_registry.sql
-- UPGRADE:
CREATE TABLE agent_registry (
    id                  VARCHAR(64)     PRIMARY KEY,
    name                VARCHAR(128)    NOT NULL,
    phase               VARCHAR(32)     NOT NULL,
    archetype           VARCHAR(32)     NOT NULL,
    version             VARCHAR(32)     NOT NULL DEFAULT '1.0.0',
    status              VARCHAR(16)     NOT NULL DEFAULT 'active'
                                        CHECK (status IN ('active','inactive','deprecated','canary')),
    model               VARCHAR(64)     NOT NULL DEFAULT 'claude-sonnet-4-20250514',
    temperature         NUMERIC(3,2)    NOT NULL DEFAULT 0.7,
    max_tokens          INTEGER         NOT NULL DEFAULT 4096,
    active_version      VARCHAR(32)     DEFAULT '1.0.0',
    canary_version      VARCHAR(32),
    canary_traffic_pct  NUMERIC(5,2)    DEFAULT 0.00,
    previous_version    VARCHAR(32),
    project_id          VARCHAR(64),
    client_id           VARCHAR(128),
    description         TEXT,
    manifest_path       VARCHAR(512),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_registry_phase ON agent_registry(phase);
CREATE INDEX idx_agent_registry_status ON agent_registry(status);

INSERT INTO schema_migrations (version, name) VALUES (1, '001_create_agent_registry');

-- DOWNGRADE:
-- DROP TABLE IF EXISTS agent_registry CASCADE;
-- DELETE FROM schema_migrations WHERE version = 1;
```

### 6.2 Migration 002 — cost_metrics

```sql
-- migrations/002_create_cost_metrics.sql
-- UPGRADE:
CREATE TABLE cost_metrics (
    id              BIGSERIAL       PRIMARY KEY,
    session_id      UUID            NOT NULL,
    agent_id        VARCHAR(64)     NOT NULL REFERENCES agent_registry(id),
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    model           VARCHAR(64)     NOT NULL,
    input_tokens    INTEGER         NOT NULL DEFAULT 0,
    output_tokens   INTEGER         NOT NULL DEFAULT 0,
    cost_usd        NUMERIC(12,6)   NOT NULL DEFAULT 0.000000,
    timestamp       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    pipeline_name   VARCHAR(128),
    phase           VARCHAR(32)
);

CREATE INDEX idx_cost_metrics_project_ts ON cost_metrics(project_id, timestamp DESC);
CREATE INDEX idx_cost_metrics_agent_ts ON cost_metrics(agent_id, timestamp DESC);
CREATE INDEX idx_cost_metrics_session ON cost_metrics(session_id);
CREATE INDEX idx_cost_metrics_timestamp ON cost_metrics(timestamp);

INSERT INTO schema_migrations (version, name) VALUES (2, '002_create_cost_metrics');

-- DOWNGRADE:
-- DROP TABLE IF EXISTS cost_metrics CASCADE;
-- DELETE FROM schema_migrations WHERE version = 2;
```

### 6.3 Migration 003 — audit_events

```sql
-- migrations/003_create_audit_events.sql
-- UPGRADE:
CREATE TABLE audit_events (
    event_id        UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID            NOT NULL,
    correlation_id  UUID,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    agent_id        VARCHAR(64),
    event_type      VARCHAR(64)     NOT NULL,
    severity        VARCHAR(16)     NOT NULL DEFAULT 'INFO'
                                    CHECK (severity IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')),
    timestamp       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    payload         JSONB           NOT NULL DEFAULT '{}'::jsonb,
    environment     VARCHAR(32)     NOT NULL DEFAULT 'production'
                                    CHECK (environment IN ('development','staging','production')),
    source_ip       INET,
    user_agent      VARCHAR(512)
);

CREATE INDEX idx_audit_events_project_ts ON audit_events(project_id, timestamp DESC);
CREATE INDEX idx_audit_events_session ON audit_events(session_id, timestamp DESC);
CREATE INDEX idx_audit_events_type ON audit_events(event_type, timestamp DESC);
CREATE INDEX idx_audit_events_severity ON audit_events(severity, timestamp DESC)
    WHERE severity IN ('ERROR', 'CRITICAL');
CREATE INDEX idx_audit_events_correlation ON audit_events(correlation_id)
    WHERE correlation_id IS NOT NULL;
CREATE INDEX idx_audit_events_payload ON audit_events USING GIN (payload jsonb_path_ops);
CREATE INDEX idx_audit_events_timestamp ON audit_events(timestamp);

-- Immutability triggers (Q-033)
CREATE OR REPLACE FUNCTION prevent_audit_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'UPDATE on audit_events is forbidden (Q-033)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_no_update
    BEFORE UPDATE ON audit_events FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_update();

CREATE OR REPLACE FUNCTION prevent_audit_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'DELETE on audit_events is forbidden (Q-033)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_no_delete
    BEFORE DELETE ON audit_events FOR EACH ROW
    EXECUTE FUNCTION prevent_audit_delete();

INSERT INTO schema_migrations (version, name) VALUES (3, '003_create_audit_events');

-- DOWNGRADE:
-- DROP TRIGGER IF EXISTS trg_audit_no_delete ON audit_events;
-- DROP TRIGGER IF EXISTS trg_audit_no_update ON audit_events;
-- DROP FUNCTION IF EXISTS prevent_audit_delete();
-- DROP FUNCTION IF EXISTS prevent_audit_update();
-- DROP TABLE IF EXISTS audit_events CASCADE;
-- DELETE FROM schema_migrations WHERE version = 3;
```

### 6.4 Migration 004 — pipeline_runs + pipeline_steps

```sql
-- migrations/004_create_pipeline_tables.sql
-- UPGRADE:
CREATE TABLE pipeline_runs (
    run_id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_name   VARCHAR(128)    NOT NULL,
    session_id      UUID            NOT NULL,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    status          VARCHAR(32)     NOT NULL DEFAULT 'pending'
                                    CHECK (status IN ('pending','running','completed','failed','cancelled','paused')),
    started_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    cost_usd        NUMERIC(12,6)   DEFAULT 0.000000,
    step_count      INTEGER         NOT NULL DEFAULT 0,
    error_message   TEXT,
    config          JSONB           DEFAULT '{}'::jsonb
);

CREATE TABLE pipeline_steps (
    step_id         VARCHAR(64)     NOT NULL,
    run_id          UUID            NOT NULL REFERENCES pipeline_runs(run_id) ON DELETE CASCADE,
    agent_id        VARCHAR(64)     NOT NULL REFERENCES agent_registry(id),
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    status          VARCHAR(32)     NOT NULL DEFAULT 'pending'
                                    CHECK (status IN ('pending','running','completed','failed','skipped')),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    input_hash      VARCHAR(64),
    output_hash     VARCHAR(64),
    cost_usd        NUMERIC(12,6)   DEFAULT 0.000000,
    error_message   TEXT,
    retry_count     INTEGER         DEFAULT 0,
    PRIMARY KEY (step_id, run_id)
);

CREATE INDEX idx_pipeline_runs_project_ts ON pipeline_runs(project_id, started_at DESC);
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status, started_at DESC);
CREATE INDEX idx_pipeline_runs_session ON pipeline_runs(session_id);
CREATE INDEX idx_pipeline_steps_run ON pipeline_steps(run_id);
CREATE INDEX idx_pipeline_steps_agent ON pipeline_steps(agent_id, started_at DESC);

CREATE OR REPLACE FUNCTION update_pipeline_run_cost()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE pipeline_runs
    SET cost_usd = (SELECT COALESCE(SUM(cost_usd), 0) FROM pipeline_steps WHERE run_id = NEW.run_id)
    WHERE run_id = NEW.run_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_step_cost_rollup
    AFTER INSERT OR UPDATE OF cost_usd ON pipeline_steps
    FOR EACH ROW EXECUTE FUNCTION update_pipeline_run_cost();

INSERT INTO schema_migrations (version, name) VALUES (4, '004_create_pipeline_tables');

-- DOWNGRADE:
-- DROP TRIGGER IF EXISTS trg_step_cost_rollup ON pipeline_steps;
-- DROP FUNCTION IF EXISTS update_pipeline_run_cost();
-- DROP TABLE IF EXISTS pipeline_steps CASCADE;
-- DROP TABLE IF EXISTS pipeline_runs CASCADE;
-- DELETE FROM schema_migrations WHERE version = 4;
```

### 6.5 Migration 005 — knowledge_exceptions

```sql
-- migrations/005_create_knowledge_exceptions.sql
-- UPGRADE:
CREATE TABLE knowledge_exceptions (
    exception_id    VARCHAR(64)     PRIMARY KEY,
    title           VARCHAR(256)    NOT NULL,
    rule            TEXT            NOT NULL,
    severity        VARCHAR(16)     NOT NULL CHECK (severity IN ('BLOCKER','WARNING','INFO')),
    tier            VARCHAR(16)     NOT NULL CHECK (tier IN ('universal','stack','client')),
    stack_name      VARCHAR(128),
    client_id       VARCHAR(128),
    project_id      VARCHAR(64),
    active          BOOLEAN         NOT NULL DEFAULT FALSE,
    applies_to_phases TEXT[],
    applies_to_agents TEXT[],
    fire_count      INTEGER         NOT NULL DEFAULT 0,
    last_fired_at   TIMESTAMPTZ,
    promoted_by     VARCHAR(128),
    promoted_at     TIMESTAMPTZ,
    created_by      VARCHAR(128)    NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

ALTER TABLE knowledge_exceptions
    ADD CONSTRAINT chk_stack_tier_name CHECK (tier != 'stack' OR stack_name IS NOT NULL);
ALTER TABLE knowledge_exceptions
    ADD CONSTRAINT chk_client_tier_id CHECK (tier != 'client' OR client_id IS NOT NULL);

CREATE INDEX idx_knowledge_exceptions_tier ON knowledge_exceptions(tier, active) WHERE active = TRUE;
CREATE INDEX idx_knowledge_exceptions_severity ON knowledge_exceptions(severity) WHERE active = TRUE;
CREATE INDEX idx_knowledge_exceptions_phases ON knowledge_exceptions USING GIN (applies_to_phases);
CREATE INDEX idx_knowledge_exceptions_agents ON knowledge_exceptions USING GIN (applies_to_agents);

CREATE OR REPLACE FUNCTION update_knowledge_exceptions_timestamp()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_knowledge_exceptions_updated_at
    BEFORE UPDATE ON knowledge_exceptions FOR EACH ROW
    EXECUTE FUNCTION update_knowledge_exceptions_timestamp();

INSERT INTO schema_migrations (version, name) VALUES (5, '005_create_knowledge_exceptions');

-- DOWNGRADE:
-- DROP TRIGGER IF EXISTS trg_knowledge_exceptions_updated_at ON knowledge_exceptions;
-- DROP FUNCTION IF EXISTS update_knowledge_exceptions_timestamp();
-- DROP TABLE IF EXISTS knowledge_exceptions CASCADE;
-- DELETE FROM schema_migrations WHERE version = 5;
```

### 6.6 Migration 006 — session_context

```sql
-- migrations/006_create_session_context.sql
-- UPGRADE:
CREATE TABLE session_context (
    id              BIGSERIAL       PRIMARY KEY,
    session_id      UUID            NOT NULL,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    key             VARCHAR(128)    NOT NULL,
    value           JSONB           NOT NULL,
    written_by      VARCHAR(64)     NOT NULL,
    written_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    ttl_seconds     INTEGER         NOT NULL DEFAULT 86400,
    version         INTEGER         NOT NULL DEFAULT 1,
    UNIQUE (session_id, key)
);

ALTER TABLE session_context
    ADD CONSTRAINT chk_value_size CHECK (pg_column_size(value) <= 102400);

CREATE INDEX idx_session_context_session_id ON session_context(session_id);
CREATE INDEX idx_session_context_key ON session_context(session_id, key);
CREATE INDEX idx_session_context_project ON session_context(project_id);
CREATE INDEX idx_session_context_expiry ON session_context(written_at, ttl_seconds);

INSERT INTO schema_migrations (version, name) VALUES (6, '006_create_session_context');

-- DOWNGRADE:
-- DROP TABLE IF EXISTS session_context CASCADE;
-- DELETE FROM schema_migrations WHERE version = 6;
```

### 6.7 Migration 007 — approval_requests

```sql
-- migrations/007_create_approval_requests.sql
-- UPGRADE:
CREATE TABLE approval_requests (
    approval_id     UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID            NOT NULL,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    pipeline_name   VARCHAR(128)    NOT NULL,
    step_id         VARCHAR(64)     NOT NULL,
    summary         TEXT            NOT NULL,
    status          VARCHAR(16)     NOT NULL DEFAULT 'PENDING'
                                    CHECK (status IN ('PENDING','APPROVED','REJECTED','TIMEOUT')),
    approver_channel VARCHAR(256),
    decision_by     VARCHAR(128),
    decision_comment TEXT,
    requested_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    decided_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ     NOT NULL,
    escalation_sent BOOLEAN         NOT NULL DEFAULT FALSE,
    reminder_count  INTEGER         NOT NULL DEFAULT 0
);

ALTER TABLE approval_requests
    ADD CONSTRAINT chk_decision_timestamp CHECK (status = 'PENDING' OR decided_at IS NOT NULL);

CREATE INDEX idx_approval_requests_project_status ON approval_requests(project_id, status)
    WHERE status = 'PENDING';
CREATE INDEX idx_approval_requests_expiry ON approval_requests(expires_at)
    WHERE status = 'PENDING';
CREATE INDEX idx_approval_requests_session ON approval_requests(session_id);

INSERT INTO schema_migrations (version, name) VALUES (7, '007_create_approval_requests');

-- DOWNGRADE:
-- DROP TABLE IF EXISTS approval_requests CASCADE;
-- DELETE FROM schema_migrations WHERE version = 7;
```

### 6.8 Migration 008 — pipeline_checkpoints

```sql
-- migrations/008_create_pipeline_checkpoints.sql
-- UPGRADE:
CREATE TABLE pipeline_checkpoints (
    id              BIGSERIAL       PRIMARY KEY,
    session_id      UUID            NOT NULL,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    pipeline_name   VARCHAR(128)    NOT NULL,
    last_step_id    VARCHAR(64)     NOT NULL,
    step_results    JSONB           NOT NULL DEFAULT '{}'::jsonb,
    status          VARCHAR(32)     NOT NULL DEFAULT 'in_progress'
                                    CHECK (status IN ('in_progress','completed','failed','abandoned')),
    retry_count     INTEGER         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_checkpoints_session ON pipeline_checkpoints(session_id);
CREATE INDEX idx_checkpoints_project ON pipeline_checkpoints(project_id);
CREATE INDEX idx_checkpoints_status ON pipeline_checkpoints(status, updated_at)
    WHERE status = 'in_progress';

CREATE OR REPLACE FUNCTION update_pipeline_checkpoints_timestamp()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pipeline_checkpoints_updated_at
    BEFORE UPDATE ON pipeline_checkpoints FOR EACH ROW
    EXECUTE FUNCTION update_pipeline_checkpoints_timestamp();

INSERT INTO schema_migrations (version, name) VALUES (8, '008_create_pipeline_checkpoints');

-- DOWNGRADE:
-- DROP TRIGGER IF EXISTS trg_pipeline_checkpoints_updated_at ON pipeline_checkpoints;
-- DROP FUNCTION IF EXISTS update_pipeline_checkpoints_timestamp();
-- DROP TABLE IF EXISTS pipeline_checkpoints CASCADE;
-- DELETE FROM schema_migrations WHERE version = 8;
```

### 6.9 Migration 009 — Enable RLS on All Tables

```sql
-- migrations/009_enable_rls.sql
-- UPGRADE:

-- agent_registry
ALTER TABLE agent_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_registry FORCE ROW LEVEL SECURITY;
CREATE POLICY agent_registry_project_isolation ON agent_registry FOR ALL
    USING (project_id IS NULL OR project_id = current_setting('app.current_project_id', TRUE))
    WITH CHECK (project_id IS NULL OR project_id = current_setting('app.current_project_id', TRUE));

-- cost_metrics
ALTER TABLE cost_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_metrics FORCE ROW LEVEL SECURITY;
CREATE POLICY cost_metrics_project_isolation ON cost_metrics FOR ALL
    USING (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)));

-- audit_events
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;
CREATE POLICY audit_events_project_isolation ON audit_events FOR ALL
    USING (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)));

-- pipeline_runs
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs FORCE ROW LEVEL SECURITY;
CREATE POLICY pipeline_runs_project_isolation ON pipeline_runs FOR ALL
    USING (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)));

-- pipeline_steps
ALTER TABLE pipeline_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_steps FORCE ROW LEVEL SECURITY;
CREATE POLICY pipeline_steps_project_isolation ON pipeline_steps FOR ALL
    USING (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)));

-- knowledge_exceptions
ALTER TABLE knowledge_exceptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_exceptions FORCE ROW LEVEL SECURITY;
CREATE POLICY knowledge_exceptions_isolation ON knowledge_exceptions FOR ALL
    USING (tier = 'universal'
        OR (tier = 'stack' AND (project_id IS NULL OR project_id = current_setting('app.current_project_id', TRUE)))
        OR (tier = 'client' AND client_id = current_setting('app.current_client_id', TRUE)))
    WITH CHECK (tier = 'universal'
        OR (tier = 'stack' AND (project_id IS NULL OR project_id = current_setting('app.current_project_id', TRUE)))
        OR (tier = 'client' AND client_id = current_setting('app.current_client_id', TRUE)));

-- session_context
ALTER TABLE session_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_context FORCE ROW LEVEL SECURITY;
CREATE POLICY session_context_project_isolation ON session_context FOR ALL
    USING (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)));

-- approval_requests
ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_requests FORCE ROW LEVEL SECURITY;
CREATE POLICY approval_requests_project_isolation ON approval_requests FOR ALL
    USING (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)));

-- pipeline_checkpoints
ALTER TABLE pipeline_checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_checkpoints FORCE ROW LEVEL SECURITY;
CREATE POLICY pipeline_checkpoints_project_isolation ON pipeline_checkpoints FOR ALL
    USING (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)))
    WITH CHECK (project_id = current_setting('app.current_project_id', TRUE)
        AND (client_id IS NULL OR client_id = current_setting('app.current_client_id', TRUE)));

INSERT INTO schema_migrations (version, name) VALUES (9, '009_enable_rls');

-- DOWNGRADE:
-- DROP POLICY IF EXISTS pipeline_checkpoints_project_isolation ON pipeline_checkpoints;
-- DROP POLICY IF EXISTS approval_requests_project_isolation ON approval_requests;
-- DROP POLICY IF EXISTS session_context_project_isolation ON session_context;
-- DROP POLICY IF EXISTS knowledge_exceptions_isolation ON knowledge_exceptions;
-- DROP POLICY IF EXISTS pipeline_steps_project_isolation ON pipeline_steps;
-- DROP POLICY IF EXISTS pipeline_runs_project_isolation ON pipeline_runs;
-- DROP POLICY IF EXISTS audit_events_project_isolation ON audit_events;
-- DROP POLICY IF EXISTS cost_metrics_project_isolation ON cost_metrics;
-- DROP POLICY IF EXISTS agent_registry_project_isolation ON agent_registry;
-- ALTER TABLE pipeline_checkpoints DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE approval_requests DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE session_context DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE knowledge_exceptions DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE pipeline_steps DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE pipeline_runs DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE audit_events DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE cost_metrics DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE agent_registry DISABLE ROW LEVEL SECURITY;
-- DELETE FROM schema_migrations WHERE version = 9;
```

---

## 7. Entity Relationship Diagram

```
 +---------------------+          +---------------------+
 |   agent_registry    |          |    cost_metrics      |
 |---------------------|          |---------------------|
 | PK id           (64)|<----+    | PK id       (BIGSER)|
 |    name             |     |    | FK agent_id     (64)|---+
 |    phase            |     |    |    session_id  (UUID)|   |
 |    archetype        |     |    |    project_id   (64)|   |
 |    version          |     |    |    client_id   (128)|   |
 |    status           |     |    |    model        (64)|   |
 |    model            |     |    |    input_tokens     |   |
 |    temperature      |     |    |    output_tokens    |   |
 |    max_tokens       |     |    |    cost_usd         |   |
 |    active_version   |     |    |    timestamp        |   |
 |    canary_version   |     |    |    pipeline_name    |   |
 |    canary_traffic_% |     |    |    phase            |   |
 |    previous_version |     |    +---------------------+   |
 |    project_id       |     |                              |
 |    client_id        |     +------------------------------+
 |    created_at       |     |
 |    updated_at       |     |
 +---------------------+     |
          ^                  |
          |                  |
          | FK agent_id      | FK agent_id
          |                  |
 +--------+------------+     |    +---------------------+
 |   pipeline_steps    |     |    |   audit_events      |
 |---------------------|     |    |---------------------|
 | PK step_id     (64) |     |    | PK event_id  (UUID) |
 | PK run_id     (UUID)|--+  |    |    session_id (UUID) |
 | FK agent_id     (64)|--+--+    |    correlation_id    |
 |    project_id   (64)|  |       |    project_id   (64) |
 |    client_id   (128)|  |       |    client_id   (128) |
 |    status           |  |       |    agent_id     (64) |
 |    started_at       |  |       |    event_type        |
 |    completed_at     |  |       |    severity          |
 |    input_hash       |  |       |    timestamp         |
 |    output_hash      |  |       |    payload    (JSONB)|
 |    cost_usd         |  |       |    environment       |
 |    error_message    |  |       |    source_ip         |
 |    retry_count      |  |       |    user_agent        |
 +---------------------+  |       +---------------------+
          |                |
          | FK run_id      |
          v                |
 +---------------------+  |       +---------------------+
 |   pipeline_runs     |  |       | knowledge_exceptions|
 |---------------------|  |       |---------------------|
 | PK run_id    (UUID) |<-+       | PK exception_id (64)|
 |    pipeline_name    |          |    title             |
 |    session_id (UUID)|          |    rule              |
 |    project_id   (64)|          |    severity          |
 |    client_id   (128)|          |    tier              |
 |    status           |          |    stack_name        |
 |    started_at       |          |    client_id   (128) |
 |    completed_at     |          |    project_id   (64) |
 |    cost_usd         |          |    active            |
 |    step_count       |          |    applies_to_phases |
 |    error_message    |          |    applies_to_agents |
 |    config    (JSONB)|          |    fire_count        |
 +---------------------+          |    last_fired_at     |
                                  |    promoted_by       |
                                  |    created_by        |
 +---------------------+         +---------------------+
 |  session_context    |
 |---------------------|
 | PK id     (BIGSER)  |         +---------------------+
 |    session_id (UUID)|         | approval_requests   |
 |    project_id   (64)|         |---------------------|
 |    client_id   (128)|         | PK approval_id(UUID)|
 |    key         (128)|         |    session_id (UUID) |
 |    value     (JSONB)|         |    project_id   (64) |
 |    written_by   (64)|         |    client_id   (128) |
 |    written_at       |         |    pipeline_name     |
 |    ttl_seconds      |         |    step_id      (64) |
 |    version          |         |    summary           |
 | UQ(session_id, key) |         |    status            |
 +---------------------+         |    approver_channel  |
                                 |    decision_by       |
                                 |    decision_comment  |
 +---------------------+        |    requested_at      |
 | pipeline_checkpoints|        |    decided_at        |
 |---------------------|        |    expires_at        |
 | PK id     (BIGSER)  |        |    escalation_sent   |
 |    session_id (UUID)|        |    reminder_count    |
 |    project_id   (64)|        +---------------------+
 |    client_id   (128)|
 |    pipeline_name    |
 |    last_step_id (64)|
 |    step_results(JSB)|
 |    status           |
 |    retry_count      |
 |    created_at       |
 |    updated_at       |
 | UQ(session_id)      |
 +---------------------+
```

### Relationship Summary

| Relationship | Type | FK Column | Notes |
|---|---|---|---|
| `cost_metrics` -> `agent_registry` | Many-to-One | `agent_id` | Every cost record links to the agent that incurred it |
| `pipeline_steps` -> `pipeline_runs` | Many-to-One | `run_id` | Steps belong to exactly one pipeline run; CASCADE delete |
| `pipeline_steps` -> `agent_registry` | Many-to-One | `agent_id` | Each step is executed by exactly one agent |
| `session_context` -- `pipeline_runs` | Logical (session_id) | None | Shared session_id links context to the pipeline run |
| `pipeline_checkpoints` -- `pipeline_runs` | Logical (session_id) | None | Checkpoint resumes the pipeline associated with the session |
| `approval_requests` -- `pipeline_steps` | Logical (step_id) | None | Approval gates correspond to specific pipeline steps |
| `audit_events` -- all tables | Logical (session_id, agent_id) | None | Audit events reference agents and sessions but have no FK for immutability |

---

## 8. Data Retention Policies

### 8.1 Retention Schedule

| Table                  | Retention Period | NFR Reference | Cleanup Strategy             |
|------------------------|-----------------|--------------|-------------------------------|
| `audit_events`         | 365 days        | Q-036        | Partition by month, drop old  |
| `cost_metrics`         | 90 days         | Q-036        | Cron DELETE by timestamp      |
| `session_context`      | 30 days         | Q-036        | TTL-based expiry + cron sweep |
| `pipeline_runs`        | 180 days        | --           | Cron DELETE by started_at     |
| `pipeline_steps`       | 180 days        | --           | CASCADE from pipeline_runs    |
| `pipeline_checkpoints` | 30 days         | --           | Cron DELETE by updated_at     |
| `approval_requests`    | 90 days         | --           | Cron DELETE by requested_at   |
| `knowledge_exceptions` | No expiry       | --           | Manual deactivation only      |
| `agent_registry`       | No expiry       | --           | Soft-delete via status field  |

### 8.2 Automated Cleanup SQL

These queries should be executed by a scheduled job (e.g., `pg_cron` or external cron) daily at 02:00 UTC.

```sql
-- =================================================================
-- RETENTION JOB: Run daily at 02:00 UTC
-- =================================================================

-- 1. Session context: Delete rows past their TTL (Q-034)
DELETE FROM session_context
WHERE written_at + (ttl_seconds || ' seconds')::INTERVAL < NOW();

-- 2. Cost metrics: Delete rows older than 90 days (Q-036)
DELETE FROM cost_metrics
WHERE timestamp < NOW() - INTERVAL '90 days';

-- 3. Approval requests: Delete rows older than 90 days
DELETE FROM approval_requests
WHERE requested_at < NOW() - INTERVAL '90 days';

-- 4. Pipeline checkpoints: Delete rows older than 30 days
DELETE FROM pipeline_checkpoints
WHERE updated_at < NOW() - INTERVAL '30 days';

-- 5. Pipeline runs + steps: Delete runs older than 180 days (steps cascade)
DELETE FROM pipeline_runs
WHERE started_at < NOW() - INTERVAL '180 days';

-- 6. Audit events: handled via partitioning (see below)
```

### 8.3 Audit Events Partitioning Strategy

Because audit_events is immutable and high-volume, it should use PostgreSQL native range partitioning by month. This allows dropping entire partitions instead of row-by-row DELETE, which is far more efficient and avoids triggering the DELETE-prevention trigger.

```sql
-- Convert audit_events to partitioned table (one-time migration)
-- Note: This requires recreating the table. Plan for a maintenance window.

CREATE TABLE audit_events_partitioned (
    event_id        UUID            NOT NULL DEFAULT gen_random_uuid(),
    session_id      UUID            NOT NULL,
    correlation_id  UUID,
    project_id      VARCHAR(64)     NOT NULL,
    client_id       VARCHAR(128),
    agent_id        VARCHAR(64),
    event_type      VARCHAR(64)     NOT NULL,
    severity        VARCHAR(16)     NOT NULL DEFAULT 'INFO',
    timestamp       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    payload         JSONB           NOT NULL DEFAULT '{}'::jsonb,
    environment     VARCHAR(32)     NOT NULL DEFAULT 'production',
    source_ip       INET,
    user_agent      VARCHAR(512),
    PRIMARY KEY (event_id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions (example for 2026)
CREATE TABLE audit_events_2026_01 PARTITION OF audit_events_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE audit_events_2026_02 PARTITION OF audit_events_partitioned
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE audit_events_2026_03 PARTITION OF audit_events_partitioned
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
-- ... continue for each month

-- Retention: drop partitions older than 365 days
-- Example: on 2027-04-01, drop the March 2026 partition:
-- DROP TABLE audit_events_2026_03;

-- Auto-create next month's partition (run monthly via cron):
-- CREATE TABLE audit_events_YYYY_MM PARTITION OF audit_events_partitioned
--     FOR VALUES FROM ('YYYY-MM-01') TO ('YYYY-{MM+1}-01');
```

### 8.4 Backup and Recovery (RPO Targets)

| Table            | RPO Target | Strategy                                           |
|------------------|-----------|-----------------------------------------------------|
| `audit_events`   | RPO = 0   | Synchronous replication to standby (Q-010)          |
| `session_context`| RPO < 1m  | Asynchronous streaming replication (Q-010)          |
| All other tables | RPO < 5m  | Asynchronous streaming replication + daily pg_dump  |

```sql
-- Verify replication status (run on primary)
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state
FROM pg_stat_replication;
```

---

## Appendix A: Session Context Key Reference

Complete list of well-known keys written by the 12-document generation pipeline agents.

| Key                    | Written By | Agent ID | Content Description                          | Avg Size |
|------------------------|-----------|----------|----------------------------------------------|----------|
| `requirements_doc`     | D1        | doc-01   | Roadmap phases, milestones, timeline          | 15 KB    |
| `prd_doc`              | D2        | doc-02   | Product vision, user stories, criteria        | 25 KB    |
| `feature_catalog`      | D3        | doc-03   | Feature list with priority and description    | 30 KB    |
| `enforcement_scaffold` | D4        | doc-04   | Linting rules, coding standards config        | 10 KB    |
| `architecture_doc`     | D5        | doc-05   | Component diagram, patterns, tech decisions   | 40 KB    |
| `db_schema`            | D6        | doc-06   | Entity-relationship model, table definitions  | 20 KB    |
| `api_contracts`        | D7        | doc-07   | OpenAPI/GraphQL contracts                     | 35 KB    |
| `task_list`            | D8        | doc-08   | Epics, stories, tickets with estimates        | 50 KB    |
| `quality_spec`         | D10       | doc-10   | Coverage targets, quality gates               | 15 KB    |
| `test_strategy`        | D11       | doc-11   | Test levels, tools, environments              | 20 KB    |

---

## Appendix B: Common Queries

### B.1 Get all session context for a pipeline run

```sql
SELECT sc.key, sc.value, sc.written_by, sc.written_at
FROM session_context sc
WHERE sc.session_id = $1
  AND sc.written_at + (sc.ttl_seconds || ' seconds')::INTERVAL > NOW()
ORDER BY sc.written_at;
```

### B.2 Calculate total cost for a project in a date range

```sql
SELECT
    agent_id,
    model,
    COUNT(*) AS invocations,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens,
    SUM(cost_usd) AS total_cost
FROM cost_metrics
WHERE project_id = $1
  AND timestamp BETWEEN $2 AND $3
GROUP BY agent_id, model
ORDER BY total_cost DESC;
```

### B.3 Find pending approvals about to expire

```sql
SELECT
    approval_id,
    pipeline_name,
    step_id,
    summary,
    expires_at,
    expires_at - NOW() AS time_remaining
FROM approval_requests
WHERE status = 'PENDING'
  AND expires_at < NOW() + INTERVAL '1 hour'
ORDER BY expires_at;
```

### B.4 Resume a pipeline from its checkpoint

```sql
SELECT
    pc.last_step_id,
    pc.step_results,
    pc.retry_count,
    pr.pipeline_name,
    pr.config
FROM pipeline_checkpoints pc
JOIN pipeline_runs pr ON pr.session_id = pc.session_id
WHERE pc.session_id = $1
  AND pc.status = 'in_progress';
```

### B.5 List active blocker exceptions for a phase

```sql
SELECT exception_id, title, rule, tier
FROM knowledge_exceptions
WHERE active = TRUE
  AND severity = 'BLOCKER'
  AND $1 = ANY(applies_to_phases)
ORDER BY tier, title;
```

### B.6 Agent fleet health summary

```sql
SELECT
    ar.phase,
    ar.status,
    COUNT(*) AS agent_count,
    COUNT(*) FILTER (WHERE ar.canary_version IS NOT NULL) AS canary_count
FROM agent_registry ar
GROUP BY ar.phase, ar.status
ORDER BY ar.phase;
```
