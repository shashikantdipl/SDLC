# FAULT-TOLERANCE — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-29
**Document:** 21 (Extended) | Status: Draft
**Reads from:** ARCH (Doc 2), DATA-MODEL (Doc 9), API-CONTRACTS (Doc 10), QUALITY (Doc 4)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Layer 1 — Application Faults](#2-layer-1--application-faults)
3. [Layer 2 — Functional Faults](#3-layer-2--functional-faults)
4. [Layer 3 — Database Faults](#4-layer-3--database-faults)
5. [Layer 4 — Session Faults](#5-layer-4--session-faults)
6. [Layer 5 — Cross-Cutting Faults](#6-layer-5--cross-cutting-faults)
7. [On-Call Procedures](#7-on-call-procedures)
8. [Summary Statistics](#8-summary-statistics)

---

## 1. Overview

The Agentic SDLC Platform operates 48 agents across 7 SDLC phases, communicating with 3 external LLM providers (Anthropic, OpenAI, Ollama) and storing state in PostgreSQL 15+. This document defines fault tolerance strategies across 5 layers, ensuring the platform degrades gracefully rather than failing catastrophically.

### Design Principles

1. **Detect fast** — health checks, circuit breakers, and anomaly detection surface faults within seconds.
2. **Isolate immediately** — faults in one agent, provider, or pipeline run must not cascade.
3. **Recover automatically** — P0 and P1 faults have automated recovery paths. Human intervention is the last resort.
4. **Audit everything** — every fault detection, recovery action, and escalation is logged in `audit_events`.
5. **Budget-aware recovery** — recovery actions (retries, failovers) are subject to cost governance by G1-cost-tracker.

### Priority Definitions

| Priority | Description | RTO Target | Escalation |
|----------|-------------|------------|------------|
| P0 | Platform unavailable or data integrity at risk | < 60 seconds | Immediate page to on-call + incident commander |
| P1 | Major feature degraded, workaround available | < 5 minutes | Page on-call within 5 minutes |
| P2 | Minor degradation, user impact limited | < 15 minutes | Alert to Slack channel, next-business-day fix |

---

## 2. Layer 1 — Application Faults

### APP-001 | P0 | MCP Server Crash

| Field | Value |
|-------|-------|
| **Fault ID** | APP-001 |
| **Priority** | P0 |
| **Component** | MCP servers (`agentic-sdlc-agents`, `agentic-sdlc-governance`, `agentic-sdlc-knowledge`) |
| **Detection** | Health check (`GET /api/v1/system/health`) fails 3 consecutive times (10s interval) |
| **Trigger** | Unhandled exception, OOM kill, or process exit |
| **Recovery** | Container orchestrator restarts the crashed MCP server container |
| **RTO** | 30 seconds |
| **Impact** | MCP tool calls fail during restart window; REST API and Dashboard unaffected (separate process) |
| **Audit** | `audit_events` entry: `action: "fault.app_001"`, `severity: "critical"`, `details: { server, restart_count, downtime_ms }` |

**Recovery sequence:**
```
1. Health check probe fails (T+0s)
2. Second probe fails (T+10s)
3. Third probe fails (T+20s) → trigger restart
4. Container orchestrator kills old process
5. New container starts, loads agent manifests from YAML
6. Health check passes (T+30s)
7. In-flight MCP calls receive error → client retries
8. Log to audit_events with action "fault.app_001.recovered"
```

**Post-incident:** If restart count > 3 in 10 minutes, escalate to P0 incident. Check `mcp_call_events` for the failing request pattern.

---

### APP-002 | P1 | LLM Provider Timeout

| Field | Value |
|-------|-------|
| **Fault ID** | APP-002 |
| **Priority** | P1 |
| **Component** | LLM Provider Adapter (shared service layer) |
| **Detection** | LLM API response time > 30 seconds |
| **Trigger** | Provider latency spike, network congestion, model overload |
| **Recovery** | Circuit breaker opens → failover to secondary provider |
| **RTO** | 5 seconds |
| **Impact** | Current agent call delayed; pipeline step may use fallback provider at different cost |
| **Audit** | `audit_events` entry: `action: "fault.app_002"`, `details: { provider, latency_ms, failover_provider }` |

**Circuit breaker configuration:**
```yaml
circuit_breaker:
  provider_timeout:
    threshold: 30s          # Single call timeout
    failure_count: 3        # Opens after 3 timeouts
    half_open_after: 60s    # Test one call after 60s
    reset_after: 300s       # Full reset after 5 min of success
```

**Failover order:**
| Primary Provider | Secondary | Tertiary |
|-----------------|-----------|----------|
| Anthropic (Claude) | OpenAI (GPT-4) | Ollama (local, no cost) |
| OpenAI (GPT-4) | Anthropic (Claude) | Ollama (local, no cost) |
| Ollama (local) | Anthropic (Claude) | OpenAI (GPT-4) |

**Cost implication:** Failover to a different provider is logged in `cost_metrics` with the actual provider used. G1-cost-tracker tracks cross-provider spend.

---

### APP-003 | P1 | LLM Provider Outage

| Field | Value |
|-------|-------|
| **Fault ID** | APP-003 |
| **Priority** | P1 |
| **Component** | LLM Provider Adapter |
| **Detection** | 5 consecutive HTTP 503 responses from provider API |
| **Trigger** | Provider-wide outage, rate limiting, account suspension |
| **Recovery** | Mark provider as `unhealthy` in `agent_registry` → route all traffic to fallback provider |
| **RTO** | 10 seconds |
| **Impact** | All agents using that provider switch to fallback; cost profile may change |
| **Audit** | `audit_events` entry: `action: "fault.app_003"`, `severity: "high"`, `details: { provider, error_codes, failover_provider }` |

**Recovery sequence:**
```
1. 5th consecutive 503 received (T+0s)
2. Provider health monitor marks provider "unhealthy"
3. UPDATE agent_registry SET provider_status = 'unhealthy'
   WHERE provider = '{affected_provider}'
4. All new agent invocations route to fallback provider (T+5s)
5. In-flight calls: timeout → retry on fallback (T+10s)
6. Background health probe pings provider every 60s
7. On 3 consecutive 200s: mark provider "healthy", resume traffic
8. Log recovery to audit_events with action "fault.app_003.recovered"
```

---

### APP-004 | P2 | Dashboard WebSocket Disconnect

| Field | Value |
|-------|-------|
| **Fault ID** | APP-004 |
| **Priority** | P2 |
| **Component** | Streamlit Dashboard (port 8501) |
| **Detection** | WebSocket `onclose` event fired |
| **Trigger** | Network blip, server restart, idle timeout |
| **Recovery** | Client-side exponential backoff reconnection |
| **RTO** | 3 seconds (typical), 30 seconds (worst case) |
| **Impact** | Dashboard shows stale data until reconnected; no data loss |
| **Audit** | Client-side log only (no server-side `audit_events` for transient disconnects) |

**Reconnection strategy:**
```
Attempt 1: wait 1s → reconnect
Attempt 2: wait 2s → reconnect
Attempt 3: wait 4s → reconnect
Attempt 4: wait 8s → reconnect
Attempt 5: wait 16s → reconnect (show "Reconnecting..." banner)
Attempt 6+: wait 30s → reconnect (show "Connection lost. Retrying...")
Max attempts: 20 (then show "Please refresh the page")
```

---

### APP-005 | P2 | REST API 5xx Spike

| Field | Value |
|-------|-------|
| **Fault ID** | APP-005 |
| **Priority** | P2 |
| **Component** | REST API (aiohttp, port 8080) |
| **Detection** | Error rate > 5% over 60-second sliding window |
| **Trigger** | Downstream failure, resource exhaustion, bug in handler |
| **Recovery** | Load shedding (reject lowest-priority requests with 503) + alert |
| **RTO** | 15 seconds |
| **Impact** | Some API calls rejected; Dashboard shows partial data; MCP tools unaffected (separate path) |
| **Audit** | `audit_events` entry: `action: "fault.app_005"`, `details: { error_rate, shed_count, duration_s }` |

**Load shedding priority (lowest shed first):**
1. `GET /api/v1/audit/export` (bulk export — defer)
2. `GET /api/v1/cost/forecast` (nice-to-have — defer)
3. `GET /api/v1/agents` (fleet listing — degrade to cached)
4. `POST /api/v1/pipelines` (pipeline trigger — never shed)
5. `POST /api/v1/approvals/{id}/approve` (approval action — never shed)

---

## 3. Layer 2 — Functional Faults

### FUNC-001 | P0 | Pipeline Step Quality Gate Failure

| Field | Value |
|-------|-------|
| **Fault ID** | FUNC-001 |
| **Priority** | P0 |
| **Component** | G4-team-orchestrator, pipeline execution engine |
| **Detection** | `pipeline_steps.quality_score` < minimum threshold (default: 70%) |
| **Trigger** | Agent produces low-quality output (hallucination, incomplete, off-topic) |
| **Recovery** | Retry with quality feedback injected into prompt (max 2 retries) → escalate to human |
| **RTO** | 60-120 seconds per retry |
| **Impact** | Pipeline paused at failing step; downstream steps blocked |
| **Audit** | `audit_events` entries for each retry: `action: "pipeline.quality_gate_fail"`, `details: { step, score, threshold, retry_count }` |

**Recovery sequence:**
```
1. Agent completes step, output scored (T+0s)
2. Score < threshold → log to audit_events
3. RETRY 1: Re-invoke agent with feedback:
   "Previous output scored {score}%. Issues: {quality_issues}.
    Improve: {specific_guidance}"
4. Score check on retry output
5. If still < threshold → RETRY 2 with stronger guidance
6. If retry 2 fails:
   a. Pipeline status → "awaiting_human_review"
   b. Create approval_request:
      INSERT INTO approval_requests (pipeline_run_id, step_name,
        request_type, details)
      VALUES (?, ?, 'quality_escalation', ?)
   c. Notify via Slack + Dashboard Approval Queue
   d. Human reviews, edits, approves → pipeline resumes
7. Cost of retries tracked in cost_metrics (G1-cost-tracker)
```

---

### FUNC-002 | P1 | Pipeline Cost Ceiling Breach

| Field | Value |
|-------|-------|
| **Fault ID** | FUNC-002 |
| **Priority** | P1 |
| **Component** | G1-cost-tracker agent |
| **Detection** | `SUM(cost_metrics.cost_usd) WHERE pipeline_run_id = ?` > $45.00 (pipeline hard ceiling) |
| **Trigger** | Excessive retries, expensive model usage, prompt bloat |
| **Recovery** | Halt pipeline immediately → notify stakeholders → human decision |
| **RTO** | Immediate halt (< 1 second) |
| **Impact** | Pipeline stops; partially generated documents preserved in `reports/` |
| **Audit** | `audit_events` entry: `action: "cost.ceiling_breach"`, `severity: "high"`, `details: { run_id, total_cost, ceiling, step_costs }` |

**Human decision options:**
1. **Resume with budget increase** — Update ceiling, resume pipeline via `POST /api/v1/pipelines/{run_id}/resume`
2. **Resume with cheaper model** — Switch remaining steps to Ollama (free), resume
3. **Cancel pipeline** — `POST /api/v1/pipelines/{run_id}/cancel`, preserve partial output
4. **Restart from checkpoint** — Resume from `pipeline_checkpoints` with adjusted configuration

**Cost thresholds:**
| Threshold | Action |
|-----------|--------|
| $20.00 (80% of $25 standard) | Warning in Cost Monitor dashboard |
| $25.00 (standard ceiling) | Alert to pipeline owner |
| $35.00 (140% of standard) | Alert to tech lead + delivery lead |
| $45.00 (hard ceiling) | **Halt pipeline** (this fault) |

---

### FUNC-003 | P1 | Agent Hallucination Detected

| Field | Value |
|-------|-------|
| **Fault ID** | FUNC-003 |
| **Priority** | P1 |
| **Component** | Output guardrail layer (all agents) |
| **Detection** | Hallucination detector: output references entities not present in input data |
| **Trigger** | Agent fabricates feature IDs (F-NNN), agent names, API endpoints, or table names not in source spec |
| **Recovery** | Discard output → retry with grounding instruction → if 2nd fail → quarantine agent |
| **RTO** | 30-60 seconds per retry |
| **Impact** | Pipeline step delayed; quarantined agent requires manual review before re-enabling |
| **Audit** | `audit_events` entry: `action: "guardrail.hallucination"`, `details: { agent_id, hallucinated_entities, input_hash }` |

**Quarantine process:**
```sql
-- Quarantine the agent
UPDATE agent_registry
SET status = 'quarantined',
    quarantine_reason = 'hallucination_detected',
    quarantined_at = NOW()
WHERE agent_id = '{agent_id}';

-- Log quarantine event
INSERT INTO audit_events (action, agent_id, severity, details)
VALUES ('agent.quarantined', '{agent_id}', 'high',
  '{"reason": "hallucination", "consecutive_failures": 2}');
```

**Unquarantine:** Requires manual review by tech lead (Jason) via `POST /api/v1/agents/{id}/unquarantine` or Approval Queue.

---

### FUNC-004 | P2 | PII Detected in Agent Output

| Field | Value |
|-------|-------|
| **Fault ID** | FUNC-004 |
| **Priority** | P2 |
| **Component** | Output guardrail layer (PII scanner) |
| **Detection** | Regex + NER scan detects PII patterns (SSN, email, phone, credit card) in agent output |
| **Trigger** | Agent leaks PII from input context into generated document |
| **Recovery** | Redact PII in output → log → alert security team → output delivered with redactions |
| **RTO** | < 5 seconds (inline redaction) |
| **Impact** | Generated document has `[REDACTED]` placeholders; human review may be needed |
| **Audit** | `audit_events` entry: `action: "guardrail.pii_detected"`, `severity: "high"`, `details: { agent_id, pii_types, redaction_count }` |

**PII patterns scanned:**
| PII Type | Pattern | Redaction |
|----------|---------|-----------|
| Email | `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}\b` | `[EMAIL-REDACTED]` |
| Phone | `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b` | `[PHONE-REDACTED]` |
| SSN | `\b\d{3}-\d{2}-\d{4}\b` | `[SSN-REDACTED]` |
| Credit Card | `\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b` | `[CC-REDACTED]` |
| IP Address | `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b` | `[IP-REDACTED]` |

---

### FUNC-005 | P1 | Agent Budget Exceeded

| Field | Value |
|-------|-------|
| **Fault ID** | FUNC-005 |
| **Priority** | P1 |
| **Component** | G1-cost-tracker agent, per-agent budget enforcement |
| **Detection** | Single agent call cost > $0.50 threshold |
| **Trigger** | Excessive token usage (long input context, verbose output), expensive model tier |
| **Recovery** | Terminate LLM call immediately → log cost → alert |
| **RTO** | < 2 seconds |
| **Impact** | Agent call produces no output; pipeline step must retry (with token limit reduced) |
| **Audit** | `audit_events` entry: `action: "cost.agent_budget_exceeded"`, `details: { agent_id, cost_usd, token_count, model }` |

**Budget enforcement checkpoints:**
```
1. Pre-call: Estimate cost from input token count + model pricing
   - If estimated_cost > $0.40 (80% of limit): warn, proceed
   - If estimated_cost > $0.50: reject call, log, alert
2. Mid-call: Monitor streaming token count
   - If running_cost > $0.50: abort stream, log partial cost
3. Post-call: Record actual cost in cost_metrics
   - INSERT INTO cost_metrics (agent_id, cost_usd, token_count, model, provider)
```

---

## 4. Layer 3 — Database Faults

### DB-001 | P0 | Primary Database Failure

| Field | Value |
|-------|-------|
| **Fault ID** | DB-001 |
| **Priority** | P0 |
| **Component** | PostgreSQL 15+ primary instance |
| **Detection** | Connection refused or query timeout > 10 seconds on 3 consecutive attempts |
| **Trigger** | Disk full, OOM, hardware failure, corrupted WAL |
| **Recovery** | Automatic failover to read replica (promoted to primary) |
| **RTO** | 60 seconds |
| **Impact** | All writes blocked during failover; reads may serve stale data for up to 10s (replication lag) |
| **Audit** | Post-recovery: `audit_events` entry: `action: "fault.db_001"`, `details: { downtime_s, replication_lag_s, data_loss: false }` |

**Recovery sequence:**
```
1. Health check detects primary unreachable (T+0s)
2. Connection pool returns errors for all queries
3. Retry 2 more times (T+10s, T+20s)
4. After 3rd failure: initiate failover (T+30s)
5. Promote read replica to primary
6. Update connection string in application config
7. Application reconnects to new primary (T+50s)
8. Verify data integrity: compare last known WAL position
9. Health check passes (T+60s)
10. Alert on-call: "DB failover completed"
11. Provision new replica from new primary (background, 30-60 min)
```

**Critical tables to verify after failover:**
- `audit_events` — append-only, verify no gaps in `id` sequence
- `pipeline_runs` — verify no runs stuck in `running` state
- `cost_metrics` — reconcile against `audit_events` totals

---

### DB-002 | P1 | Connection Pool Exhaustion

| Field | Value |
|-------|-------|
| **Fault ID** | DB-002 |
| **Priority** | P1 |
| **Component** | PostgreSQL connection pool (asyncpg) |
| **Detection** | Active connections > 90% of `max_pool_size` (default: 20) |
| **Trigger** | Connection leak, long-running queries, traffic spike |
| **Recovery** | Load shed low-priority queries → alert → investigate |
| **RTO** | 5 seconds |
| **Impact** | New queries queued or rejected; in-flight queries unaffected |
| **Audit** | `audit_events` entry: `action: "fault.db_002"`, `details: { active_connections, max_pool_size, queued_queries }` |

**Pool configuration:**
```yaml
database:
  pool:
    min_size: 5
    max_size: 20
    max_queries: 50000     # Per connection before recycle
    max_inactive_time: 300  # Seconds before idle connection closed
    command_timeout: 30     # Query timeout in seconds
```

**Load shedding order (shed first):**
1. `GET /api/v1/audit/export` (bulk reads)
2. `GET /api/v1/cost/forecast` (complex aggregation)
3. Agent health checks (use cached result)
4. Pipeline execution queries (never shed)

---

### DB-003 | P1 | Migration Failure

| Field | Value |
|-------|-------|
| **Fault ID** | DB-003 |
| **Priority** | P1 |
| **Component** | Database migration system (Alembic) |
| **Detection** | Migration script returns non-zero exit code |
| **Trigger** | Schema conflict, constraint violation, disk space, timeout |
| **Recovery** | Automatic rollback of failed migration → alert |
| **RTO** | 10 minutes |
| **Impact** | Schema stays at previous version; new features requiring the migration are unavailable |
| **Audit** | `audit_events` entry: `action: "fault.db_003"`, `details: { migration_id, error, rolled_back: true }` |

**Migration safety rules:**
1. All migrations run in a transaction (atomic apply/rollback)
2. Every migration has a corresponding down migration
3. Migrations tested against a copy of production schema before deploy
4. Maximum migration duration: 5 minutes (timeout kill)
5. No `DROP TABLE` or `DROP COLUMN` without 2-version deprecation period

---

### DB-004 | P2 | Slow Query Detected

| Field | Value |
|-------|-------|
| **Fault ID** | DB-004 |
| **Priority** | P2 |
| **Component** | PostgreSQL query engine |
| **Detection** | Query execution time > 2 seconds (logged by `pg_stat_statements`) |
| **Trigger** | Missing index, table bloat, complex join, large result set |
| **Recovery** | Log query + execution plan → add to optimization queue |
| **RTO** | N/A (no immediate recovery; query completes, just slow) |
| **Impact** | Individual request slow; no system-wide impact unless widespread |
| **Audit** | `audit_events` entry: `action: "fault.db_004"`, `severity: "low"`, `details: { query_hash, duration_ms, table }` |

**Known slow query patterns and mitigations:**

| Query Pattern | Table | Expected Duration | Mitigation |
|---------------|-------|-------------------|------------|
| `SELECT * FROM audit_events WHERE project_id = ? ORDER BY created_at DESC` | `audit_events` | < 500ms | Index: `idx_audit_events_project_created` |
| `SELECT SUM(cost_usd) FROM cost_metrics WHERE agent_id = ? AND created_at > ?` | `cost_metrics` | < 300ms | Index: `idx_cost_metrics_agent_created` |
| `SELECT * FROM pipeline_steps WHERE run_id = ? ORDER BY step_order` | `pipeline_steps` | < 200ms | Index: `idx_pipeline_steps_run_order` |
| Audit export with date range | `audit_events` | < 5s (bulk) | Pagination, streaming response |

---

## 5. Layer 4 — Session Faults

### SESS-001 | P1 | API Key Revoked Mid-Pipeline

| Field | Value |
|-------|-------|
| **Fault ID** | SESS-001 |
| **Priority** | P1 |
| **Component** | LLM Provider Adapter, API key management |
| **Detection** | HTTP 401 or 403 from LLM provider API |
| **Trigger** | API key rotated, expired, or manually revoked while pipeline is running |
| **Recovery** | Pause pipeline → attempt re-authentication with backup key → resume |
| **RTO** | Immediate pause; resume depends on key availability |
| **Impact** | Pipeline paused; no data loss (checkpoint preserved in `pipeline_checkpoints`) |
| **Audit** | `audit_events` entry: `action: "fault.sess_001"`, `details: { provider, pipeline_run_id, step_name }` |

**Recovery sequence:**
```
1. Agent call returns 401/403 (T+0s)
2. Pipeline engine pauses run:
   UPDATE pipeline_runs SET status = 'paused',
     pause_reason = 'auth_failure'
   WHERE id = '{run_id}'
3. Save checkpoint:
   INSERT INTO pipeline_checkpoints (run_id, step_name, context_snapshot)
   VALUES ('{run_id}', '{current_step}', '{serialized_context}')
4. Attempt re-auth with backup API key (if configured)
5. If backup key works: resume pipeline from checkpoint
6. If no backup key: alert team, await manual key update
7. After key updated: POST /api/v1/pipelines/{run_id}/resume
```

---

### SESS-002 | P2 | Session Context Corruption

| Field | Value |
|-------|-------|
| **Fault ID** | SESS-002 |
| **Priority** | P2 |
| **Component** | `session_context` table (JSONB `context_data` column) |
| **Detection** | Checksum mismatch on `session_context.context_data` read |
| **Trigger** | Partial write, concurrent update conflict, bit rot |
| **Recovery** | Rebuild context from `audit_events` trail |
| **RTO** | 5-30 seconds depending on context size |
| **Impact** | Pipeline step may need to re-read context; no pipeline restart needed |
| **Audit** | `audit_events` entry: `action: "fault.sess_002"`, `details: { session_id, expected_checksum, actual_checksum }` |

**Rebuild process:**
```sql
-- Find all audit events for this session to rebuild context
SELECT action, details, created_at
FROM audit_events
WHERE project_id = '{project_id}'
  AND session_id = '{session_id}'
ORDER BY created_at ASC;

-- Replay events to reconstruct session_context.context_data
-- (Handled by SessionService.rebuild_from_audit())
```

---

### SESS-003 | P2 | Dashboard Session Timeout

| Field | Value |
|-------|-------|
| **Fault ID** | SESS-003 |
| **Priority** | P2 |
| **Component** | Streamlit Dashboard session management |
| **Detection** | Session token expired (default: 30 min inactivity) |
| **Trigger** | User idle timeout, browser tab backgrounded |
| **Recovery** | Preserve unsaved state in browser localStorage → re-authenticate → restore state |
| **RTO** | 5 seconds (re-auth) + 2 seconds (state restore) |
| **Impact** | User sees login prompt; after login, returns to previous view with filters preserved |
| **Audit** | `audit_events` entry: `action: "session.timeout"`, `severity: "info"`, `details: { user, page, idle_duration_s }` |

**State preservation:**
```javascript
// Preserved in localStorage before session expires:
{
  "current_page": "pipeline_runs",
  "filters": { "status": "running", "project_id": "proj-acme-2026" },
  "scroll_position": 450,
  "expanded_rows": ["run-abc-123"],
  "unsaved_approval_comments": "Looks good, minor formatting issue on section 3"
}
```

---

## 6. Layer 5 — Cross-Cutting Faults

### CROSS-001 | P1 | Audit Logging Pipeline Down

| Field | Value |
|-------|-------|
| **Fault ID** | CROSS-001 |
| **Priority** | P1 |
| **Component** | Audit event writer (writes to `audit_events` table) |
| **Detection** | `INSERT INTO audit_events` fails or times out |
| **Trigger** | Database connection issue, `audit_events` table lock, disk full |
| **Recovery** | Buffer events in memory (ring buffer) → flush when connection recovers |
| **RTO** | Immediate (buffering); flush within 60 seconds of recovery |
| **Impact** | Audit events delayed but not lost (up to buffer limit) |
| **Audit** | Self-referential: first event after recovery includes `buffer_flush_count` |

**Buffer configuration:**
```yaml
audit:
  buffer:
    max_events: 1000       # Maximum events in memory buffer
    flush_interval: 5s     # Attempt flush every 5 seconds
    overflow_action: drop_oldest  # If buffer full, drop oldest events
    overflow_alert: true   # Alert if buffer reaches 80% capacity
```

**Overflow scenario:** If buffer reaches 1000 events (approximately 5 minutes of heavy activity), oldest events are dropped. This triggers a P0 alert because audit completeness is compromised.

```
Buffer at 800/1000 → alert: "Audit buffer 80% full, DB write failing"
Buffer at 1000/1000 → P0 alert: "Audit events being dropped, DB write critical"
```

---

### CROSS-002 | P2 | Nightly Reconciliation Failure

| Field | Value |
|-------|-------|
| **Fault ID** | CROSS-002 |
| **Priority** | P2 |
| **Component** | Nightly reconciliation job (cron) |
| **Detection** | Reconciliation query detects mismatch |
| **Trigger** | `cost_metrics` totals do not match `audit_events` cost entries |
| **Recovery** | Log discrepancy → generate reconciliation report → alert finance/compliance |
| **RTO** | N/A (batch job, not real-time) |
| **Impact** | Cost reports may be inaccurate; compliance risk |
| **Audit** | `audit_events` entry: `action: "reconciliation.mismatch"`, `details: { cost_metrics_total, audit_events_total, delta_usd }` |

**Reconciliation queries:**
```sql
-- Compare cost_metrics total vs audit_events cost entries
WITH cost_total AS (
  SELECT SUM(cost_usd) as metrics_total
  FROM cost_metrics
  WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
    AND created_at < CURRENT_DATE
),
audit_total AS (
  SELECT SUM((details->>'cost_usd')::decimal) as audit_total
  FROM audit_events
  WHERE action LIKE 'agent.invoke%'
    AND created_at >= CURRENT_DATE - INTERVAL '1 day'
    AND created_at < CURRENT_DATE
)
SELECT
  ct.metrics_total,
  at.audit_total,
  ABS(ct.metrics_total - at.audit_total) as delta,
  CASE
    WHEN ABS(ct.metrics_total - at.audit_total) > 0.01 THEN 'MISMATCH'
    ELSE 'OK'
  END as status
FROM cost_total ct, audit_total at;
```

**Acceptable delta:** $0.01 (rounding). Any delta > $0.01 triggers investigation.

---

### CROSS-003 | P1 | Multi-Tenant Data Leak Detection

| Field | Value |
|-------|-------|
| **Fault ID** | CROSS-003 |
| **Priority** | P1 |
| **Component** | Row-Level Security (RLS) on all tables, query interceptor |
| **Detection** | Query interceptor detects query without `project_id` filter on tenant-scoped tables |
| **Trigger** | Bug in service layer, missing RLS policy, direct SQL without tenant context |
| **Recovery** | Reject query → log → alert security team |
| **RTO** | < 1 second (query rejected before execution) |
| **Impact** | Query fails; no data leaked |
| **Audit** | `audit_events` entry: `action: "security.tenant_isolation_violation"`, `severity: "critical"`, `details: { query_hash, table, caller }` |

**Tenant-scoped tables (RLS enforced):**
| Table | Tenant Column | RLS Policy |
|-------|--------------|------------|
| `pipeline_runs` | `project_id` | `current_setting('app.project_id') = project_id` |
| `pipeline_steps` | via `pipeline_runs.project_id` | Join-based RLS |
| `cost_metrics` | `project_id` | `current_setting('app.project_id') = project_id` |
| `audit_events` | `project_id` | `current_setting('app.project_id') = project_id` |
| `session_context` | `project_id` | `current_setting('app.project_id') = project_id` |
| `approval_requests` | `project_id` | `current_setting('app.project_id') = project_id` |
| `pipeline_checkpoints` | via `pipeline_runs.project_id` | Join-based RLS |

**Exempt tables (global scope):**
- `agent_registry` — shared across all projects
- `knowledge_exceptions` — shared knowledge base
- `mcp_call_events` — operational monitoring (no tenant data)

---

## 7. On-Call Procedures

### 7.1 P0 Incident Response

**Response time:** Acknowledge within 5 minutes. Begin remediation within 15 minutes.

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | PagerDuty alert fires | Automated | T+0 |
| 2 | On-call acknowledges alert | On-call engineer | T+5 min |
| 3 | Open incident channel in Slack (`#incident-{id}`) | On-call engineer | T+6 min |
| 4 | Check `GET /api/v1/system/health` for component status | On-call engineer | T+7 min |
| 5 | Check `audit_events` for recent fault entries | On-call engineer | T+8 min |
| 6 | Identify fault ID from this document, follow recovery sequence | On-call engineer | T+10 min |
| 7 | Execute recovery | On-call engineer | T+15 min |
| 8 | Verify recovery via health check | On-call engineer | T+RTO |
| 9 | Post incident update to Slack channel | On-call engineer | T+RTO+5 min |
| 10 | Create post-incident review ticket | On-call engineer | T+RTO+30 min |

**P0 Scenarios requiring this procedure:**
- APP-001: MCP Server Crash
- FUNC-001: Pipeline Step Quality Gate Failure
- DB-001: Primary Database Failure

### 7.2 P1 Incident Response

**Response time:** Acknowledge within 15 minutes. Begin remediation within 30 minutes.

| Step | Action | Owner | Time |
|------|--------|-------|------|
| 1 | PagerDuty alert fires (low urgency) or Slack alert | Automated | T+0 |
| 2 | On-call acknowledges | On-call engineer | T+15 min |
| 3 | Assess impact: check Fleet Health + Cost Monitor dashboards | On-call engineer | T+20 min |
| 4 | Identify fault ID, follow recovery sequence | On-call engineer | T+25 min |
| 5 | Execute recovery | On-call engineer | T+30 min |
| 6 | Verify recovery | On-call engineer | T+RTO |
| 7 | Document in incident log | On-call engineer | Next business day |

**P1 Scenarios requiring this procedure:**
- APP-002: LLM Provider Timeout
- APP-003: LLM Provider Outage
- FUNC-002: Pipeline Cost Ceiling Breach
- FUNC-003: Agent Hallucination Detected
- FUNC-005: Agent Budget Exceeded
- DB-002: Connection Pool Exhaustion
- DB-003: Migration Failure
- SESS-001: API Key Revoked Mid-Pipeline
- CROSS-001: Audit Logging Pipeline Down
- CROSS-003: Multi-Tenant Data Leak Detection

### 7.3 Escalation Matrix

| Escalation Level | Trigger | Who | Contact Method |
|-----------------|---------|-----|----------------|
| L1 | Any P0 or P1 alert | On-call engineer (rotating) | PagerDuty |
| L2 | P0 unresolved > 30 min | Tech Lead (Jason) | PagerDuty + phone |
| L3 | P0 unresolved > 1 hour | Platform Engineer (Priya) + DevOps (David) | PagerDuty + phone |
| L4 | Data breach or compliance issue | Compliance Officer (Fatima) | PagerDuty + phone + email |
| L5 | Platform-wide outage > 2 hours | Engineering Director | Phone |

---

## 8. Summary Statistics

### Fault Inventory

| Layer | P0 | P1 | P2 | Total |
|-------|----|----|-----|-------|
| Layer 1 — Application | 1 | 2 | 2 | 5 |
| Layer 2 — Functional | 1 | 3 | 1 | 5 |
| Layer 3 — Database | 1 | 2 | 1 | 4 |
| Layer 4 — Session | 0 | 1 | 2 | 3 |
| Layer 5 — Cross-Cutting | 0 | 2 | 1 | 3 |
| **Total** | **3** | **10** | **7** | **20** |

### RTO Summary

| Priority | Fault Count | RTO Range | Automated Recovery |
|----------|-------------|-----------|--------------------|
| P0 | 3 | 30s - 120s | Yes (all 3) |
| P1 | 10 | 2s - 10 min | Yes (8 of 10); 2 require human decision |
| P2 | 7 | 3s - 30s | Yes (all 7) |

### Recovery Dependencies

| Fault | Depends On |
|-------|-----------|
| APP-001 | Container orchestrator (Docker/K8s) |
| APP-002, APP-003 | At least 2 of 3 LLM providers operational |
| FUNC-001 | G1-cost-tracker budget available for retries |
| FUNC-002 | Human decision maker available |
| DB-001 | Read replica configured and in sync |
| CROSS-001 | Memory available for 1000-event buffer |
| CROSS-003 | RLS policies applied on all tenant-scoped tables |

### Monitoring Endpoints

| Endpoint | Checks | Frequency |
|----------|--------|-----------|
| `GET /api/v1/system/health` | All components, DB connectivity, provider status | Every 10s |
| `GET /api/v1/system/health/db` | PostgreSQL connection, replication lag | Every 30s |
| `GET /api/v1/system/health/providers` | LLM provider latency and error rates | Every 30s |
| `GET /api/v1/system/health/agents` | Agent registry status, circuit breaker state | Every 60s |

---

*End of FAULT-TOLERANCE. This document is a living specification — new fault scenarios are added as the platform evolves. Review quarterly.*
