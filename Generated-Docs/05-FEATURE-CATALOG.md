# FEATURE-CATALOG — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 5 of 14 | Status: Draft

---

## Table of Contents

1. [Overview](#overview)
2. [Feature Schema](#feature-schema)
3. [E-001: Pipeline Execution](#e-001-pipeline-execution)
4. [E-002: Agent Management](#e-002-agent-management)
5. [E-003: Cost & Budget](#e-003-cost--budget)
6. [E-004: Audit & Compliance](#e-004-audit--compliance)
7. [E-005: Human Approval Gates](#e-005-human-approval-gates)
8. [E-006: Knowledge Management](#e-006-knowledge-management)
9. [E-007: MCP Server Infrastructure](#e-007-mcp-server-infrastructure)
10. [E-008: Dashboard / Operator UI](#e-008-dashboard--operator-ui)
11. [E-009: Quality & Testing](#e-009-quality--testing)
12. [E-010: Platform Foundation](#e-010-platform-foundation)
13. [Summary Table](#summary-table)
14. [Statistics](#statistics)

---

## Overview

This document decomposes the 12 PRD capabilities (C1-C12) into 56 discrete, implementable features. Each feature declares:

- **Which interfaces expose it** (MCP, REST, Dashboard)
- **Which shared service implements it** (business logic never lives in handlers)
- **Which MCP server hosts its tool** (agents-server, governance-server, knowledge-server)
- **Traceability** back to PRD capabilities and forward to backlog stories

### Full-Stack-First Principle

Every feature that is exposed via MCP is also exposed via REST (interface parity, Q-049). Business logic resides exclusively in shared services; MCP tool handlers and REST route handlers are thin wrappers that delegate to the same service method.

---

## Feature Schema

Every feature in this catalog conforms to the following schema:

```json
{
  "id": "F-NNN",
  "name": "Short name",
  "description": "One sentence describing what this feature does",
  "capability": "C1-C12 reference",
  "epic": "E-NNN",
  "priority": "must|should|could|wont",
  "story_points": "1|2|3|5|8|13",
  "mcp_server": "agents-server|governance-server|knowledge-server|none",
  "dashboard_view": "Fleet Health|Cost Monitor|Pipeline Runs|Audit Log|Approval Queue|none",
  "shared_service": "PipelineService|AgentService|CostService|AuditService|ApprovalService|KnowledgeService|HealthService|SessionService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-NNN"],
  "acceptance_criteria": ["Testable statement 1", "Testable statement 2"]
}
```

---

## E-001: Pipeline Execution

**Capabilities:** C2 (12-Document Generation Pipeline), C8 (Pipeline Resilience)
**Priority tier:** must
**Feature count:** 7

### F-001: Trigger Pipeline

```json
{
  "id": "F-001",
  "name": "Trigger Pipeline",
  "description": "Accept a project brief and initiate the 12-document generation pipeline, returning a run_id for tracking",
  "capability": "C2",
  "epic": "E-001",
  "priority": "must",
  "story_points": 8,
  "mcp_server": "agents-server",
  "dashboard_view": "Pipeline Runs",
  "shared_service": "PipelineService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": [],
  "acceptance_criteria": [
    "POST /api/v1/pipelines with a valid brief returns 201 with run_id",
    "MCP tool trigger_pipeline returns run_id within 2 seconds",
    "Dashboard 'New Run' button submits brief and navigates to run detail",
    "Invalid brief (empty or >50KB) returns 422 with validation error",
    "Pipeline run record is persisted in pipeline_runs table with status 'pending'"
  ]
}
```

### F-002: Get Pipeline Status

```json
{
  "id": "F-002",
  "name": "Get Pipeline Status",
  "description": "Retrieve the current status, progress percentage, completed phases, and active agents for a given pipeline run",
  "capability": "C2",
  "epic": "E-001",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "agents-server",
  "dashboard_view": "Pipeline Runs",
  "shared_service": "PipelineService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-001"],
  "acceptance_criteria": [
    "GET /api/v1/pipelines/{run_id} returns status, progress_pct, phases_completed, active_agents",
    "MCP tool get_pipeline_status returns identical data shape",
    "Response latency is under 200ms for any run_id",
    "Non-existent run_id returns 404 with descriptive message",
    "Dashboard Pipeline Runs page polls status every 5 seconds for active runs"
  ]
}
```

### F-003: List Pipeline Runs

```json
{
  "id": "F-003",
  "name": "List Pipeline Runs",
  "description": "Return a paginated list of pipeline runs filtered by status, project, or date range",
  "capability": "C2",
  "epic": "E-001",
  "priority": "must",
  "story_points": 3,
  "mcp_server": "agents-server",
  "dashboard_view": "Pipeline Runs",
  "shared_service": "PipelineService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-001"],
  "acceptance_criteria": [
    "GET /api/v1/pipelines returns paginated list with limit/offset parameters",
    "Filtering by status (pending, running, completed, failed) returns correct subset",
    "Filtering by project_id returns only runs for that project",
    "Default sort is created_at descending",
    "MCP tool list_pipeline_runs supports the same filter parameters"
  ]
}
```

### F-004: Resume Pipeline from Checkpoint

```json
{
  "id": "F-004",
  "name": "Resume Pipeline from Checkpoint",
  "description": "Resume a failed or paused pipeline run from its last successful checkpoint, skipping completed phases",
  "capability": "C8",
  "epic": "E-001",
  "priority": "must",
  "story_points": 8,
  "mcp_server": "agents-server",
  "dashboard_view": "none",
  "shared_service": "PipelineService",
  "interfaces": ["mcp", "rest"],
  "depends_on": ["F-001", "F-002"],
  "acceptance_criteria": [
    "POST /api/v1/pipelines/{run_id}/resume restarts from last checkpoint",
    "Previously completed phases are not re-executed",
    "Checkpoint data (intermediate outputs) is loaded from checkpoint store",
    "Run that is already in 'running' state returns 409 Conflict",
    "Run that completed successfully returns 400 Bad Request",
    "Audit event is emitted with type 'pipeline.resumed'"
  ]
}
```

### F-005: Cancel Pipeline

```json
{
  "id": "F-005",
  "name": "Cancel Pipeline",
  "description": "Cancel a running pipeline, terminating active agent invocations and recording partial outputs",
  "capability": "C2",
  "epic": "E-001",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "agents-server",
  "dashboard_view": "none",
  "shared_service": "PipelineService",
  "interfaces": ["mcp", "rest"],
  "depends_on": ["F-001"],
  "acceptance_criteria": [
    "POST /api/v1/pipelines/{run_id}/cancel sets status to 'cancelled'",
    "Active agent invocations receive cancellation signal within 5 seconds",
    "Partial outputs generated before cancellation are preserved",
    "Cancelling an already-completed run returns 400",
    "Cost accrued up to cancellation point is recorded"
  ]
}
```

### F-006: Pipeline Parallel DAG Execution

```json
{
  "id": "F-006",
  "name": "Pipeline Parallel DAG Execution",
  "description": "Execute pipeline phases as a directed acyclic graph, running independent phases in parallel to minimize total duration",
  "capability": "C8",
  "epic": "E-001",
  "priority": "must",
  "story_points": 13,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "PipelineService",
  "interfaces": [],
  "depends_on": ["F-001"],
  "acceptance_criteria": [
    "Independent phases (e.g., ARCH and QUALITY) execute concurrently",
    "Phase with unmet dependencies waits until all predecessors complete",
    "Total pipeline duration is less than sequential sum when parallelism is possible",
    "DAG cycle detection raises ConfigurationError at startup",
    "Maximum concurrency is configurable via MAX_PARALLEL_PHASES (default 3)"
  ]
}
```

### F-007: Pipeline Self-Healing on Test Failure

```json
{
  "id": "F-007",
  "name": "Pipeline Self-Healing on Test Failure",
  "description": "Automatically retry a failed agent invocation with enriched context from the failure, up to a configurable retry limit",
  "capability": "C8",
  "epic": "E-001",
  "priority": "must",
  "story_points": 8,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "PipelineService",
  "interfaces": [],
  "depends_on": ["F-001", "F-046"],
  "acceptance_criteria": [
    "Failed agent invocation is retried with failure context appended to prompt",
    "Maximum retries configurable via AGENT_MAX_RETRIES (default 2)",
    "Each retry is logged as a separate audit event with retry_count",
    "If all retries fail, pipeline transitions to 'failed' state with aggregated errors",
    "Self-healing does not exceed per-agent budget allocation"
  ]
}
```

---

## E-002: Agent Management

**Capabilities:** C1 (Agent Orchestration), C9 (Agent Lifecycle)
**Priority tier:** should
**Feature count:** 6

### F-008: List Agents with Status

```json
{
  "id": "F-008",
  "name": "List Agents with Status",
  "description": "Return the full agent registry with each agent's current status, maturity level, and active invocation count",
  "capability": "C1",
  "epic": "E-002",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "agents-server",
  "dashboard_view": "Fleet Health",
  "shared_service": "AgentService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": [],
  "acceptance_criteria": [
    "GET /api/v1/agents returns list of all 48 agents with status fields",
    "Each agent includes: agent_id, name, phase, status, maturity, active_invocations",
    "Filtering by phase (1-7) returns correct subset",
    "MCP tool list_agents returns identical data shape",
    "Dashboard Fleet Health page renders agent cards grouped by phase"
  ]
}
```

### F-009: Get Agent Detail

```json
{
  "id": "F-009",
  "name": "Get Agent Detail",
  "description": "Retrieve full agent configuration including model, temperature, system prompt hash, version slots, and performance metrics",
  "capability": "C1",
  "epic": "E-002",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "agents-server",
  "dashboard_view": "Fleet Health",
  "shared_service": "AgentService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-008"],
  "acceptance_criteria": [
    "GET /api/v1/agents/{agent_id} returns full agent configuration",
    "Response includes version_slots (canary, stable, previous)",
    "Response includes performance metrics (avg_latency, success_rate, avg_quality_score)",
    "Non-existent agent_id returns 404",
    "MCP tool get_agent_detail returns identical data shape"
  ]
}
```

### F-010: Invoke Agent Directly

```json
{
  "id": "F-010",
  "name": "Invoke Agent Directly",
  "description": "Invoke a single agent outside the pipeline context, passing input and receiving structured output with cost tracking",
  "capability": "C1",
  "epic": "E-002",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "agents-server",
  "dashboard_view": "none",
  "shared_service": "AgentService",
  "interfaces": ["mcp", "rest"],
  "depends_on": ["F-008", "F-016"],
  "acceptance_criteria": [
    "POST /api/v1/agents/{agent_id}/invoke accepts input payload and returns structured output",
    "Invocation respects agent's configured model, temperature, and system prompt",
    "Cost is tracked via CostService.record_spend for the invocation",
    "Invocation timeout is enforced (default 120s, configurable per agent)",
    "Rate limiting is applied per agent_id",
    "Audit event is emitted with type 'agent.invoked'"
  ]
}
```

### F-011: Agent Health Check

```json
{
  "id": "F-011",
  "name": "Agent Health Check",
  "description": "Run a lightweight probe against an agent to verify it can accept invocations and respond within SLA",
  "capability": "C1",
  "epic": "E-002",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "agents-server",
  "dashboard_view": "Fleet Health",
  "shared_service": "HealthService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-008"],
  "acceptance_criteria": [
    "GET /api/v1/agents/{agent_id}/health returns healthy/degraded/unhealthy status",
    "Health check completes within 10 seconds",
    "Degraded status is returned if latency exceeds 2x SLA threshold",
    "Unhealthy status is returned if agent fails to respond",
    "Dashboard Fleet Health page displays color-coded health indicators"
  ]
}
```

### F-012: Agent Version Management

```json
{
  "id": "F-012",
  "name": "Agent Version Management",
  "description": "Manage agent version slots (canary, stable, previous) with promote, rollback, and canary traffic splitting",
  "capability": "C9",
  "epic": "E-002",
  "priority": "should",
  "story_points": 8,
  "mcp_server": "agents-server",
  "dashboard_view": "Fleet Health",
  "shared_service": "AgentService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-008", "F-009"],
  "acceptance_criteria": [
    "POST /api/v1/agents/{agent_id}/versions/canary deploys new version to canary slot",
    "POST /api/v1/agents/{agent_id}/versions/promote moves canary to stable, stable to previous",
    "POST /api/v1/agents/{agent_id}/versions/rollback swaps stable with previous",
    "Canary traffic percentage is configurable (default 10%)",
    "Version promotion requires minimum 10 successful canary invocations",
    "Dashboard shows version slot status with one-click promote/rollback"
  ]
}
```

### F-013: Agent Maturity Progression Tracking

```json
{
  "id": "F-013",
  "name": "Agent Maturity Progression Tracking",
  "description": "Track and display each agent's maturity level (bootstrap, validated, production, optimized) with progression criteria",
  "capability": "C9",
  "epic": "E-002",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "Fleet Health",
  "shared_service": "AgentService",
  "interfaces": ["rest", "dashboard"],
  "depends_on": ["F-008", "F-046"],
  "acceptance_criteria": [
    "GET /api/v1/agents/{agent_id}/maturity returns current level and progression criteria",
    "Maturity levels: bootstrap -> validated -> production -> optimized",
    "Progression from bootstrap to validated requires 90% quality score on golden tests",
    "Progression from validated to production requires 100 successful invocations",
    "Dashboard Fleet Health page shows maturity badge per agent"
  ]
}
```

---

## E-003: Cost & Budget

**Capabilities:** C3 (Cost Control & Governance)
**Priority tier:** must
**Feature count:** 5

### F-014: Get Cost Report

```json
{
  "id": "F-014",
  "name": "Get Cost Report",
  "description": "Generate a cost report aggregated by fleet, project, agent, or time period with breakdown by model and token type",
  "capability": "C3",
  "epic": "E-003",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "governance-server",
  "dashboard_view": "Cost Monitor",
  "shared_service": "CostService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-016"],
  "acceptance_criteria": [
    "GET /api/v1/costs/report returns cost data aggregated by requested dimension",
    "Supports aggregation by: fleet, project, agent, invocation",
    "Supports time range filtering (start_date, end_date)",
    "Breakdown includes input_tokens, output_tokens, model, cost_usd",
    "MCP tool get_cost_report returns identical data shape",
    "Dashboard Cost Monitor page renders interactive cost chart"
  ]
}
```

### F-015: Check Budget Remaining

```json
{
  "id": "F-015",
  "name": "Check Budget Remaining",
  "description": "Return the remaining budget for a given scope (fleet, project, or agent) with percentage consumed and projected exhaustion time",
  "capability": "C3",
  "epic": "E-003",
  "priority": "must",
  "story_points": 3,
  "mcp_server": "governance-server",
  "dashboard_view": "Cost Monitor",
  "shared_service": "CostService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-016", "F-018"],
  "acceptance_criteria": [
    "GET /api/v1/costs/budget?scope=project&id={project_id} returns budget_total, budget_spent, budget_remaining",
    "Response includes percentage_consumed and projected_exhaustion_time",
    "Fleet-level budget defaults to $25 ceiling per pipeline run",
    "MCP tool check_budget returns identical data shape",
    "Dashboard Cost Monitor page shows budget gauge with color thresholds (green <60%, yellow <80%, red >=80%)"
  ]
}
```

### F-016: Record Spend Event

```json
{
  "id": "F-016",
  "name": "Record Spend Event",
  "description": "Record a cost event from an agent invocation including model, tokens, and computed cost, persisted to cost_events table",
  "capability": "C3",
  "epic": "E-003",
  "priority": "must",
  "story_points": 3,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "CostService",
  "interfaces": [],
  "depends_on": [],
  "acceptance_criteria": [
    "CostService.record_spend persists event with agent_id, model, input_tokens, output_tokens, cost_usd",
    "Cost is computed using model-specific pricing table",
    "Event includes timestamp, run_id, and project_id for aggregation",
    "Concurrent writes do not cause lost updates (row-level locking or serializable isolation)",
    "Event is written within 100ms of invocation completion"
  ]
}
```

### F-017: Cost Anomaly Detection and Alert

```json
{
  "id": "F-017",
  "name": "Cost Anomaly Detection and Alert",
  "description": "Detect cost anomalies when an agent or pipeline exceeds 2x its rolling average spend and emit alerts",
  "capability": "C3",
  "epic": "E-003",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "Cost Monitor",
  "shared_service": "CostService",
  "interfaces": ["dashboard"],
  "depends_on": ["F-016"],
  "acceptance_criteria": [
    "Anomaly is detected when spend exceeds 2x the 7-day rolling average for the scope",
    "Alert is emitted as a structured log event with severity 'warning'",
    "Dashboard Cost Monitor page displays anomaly banner with details",
    "Anomaly detection runs after each spend event (not batch)",
    "False positive rate is below 5% over a 30-day window"
  ]
}
```

### F-018: Budget Tier Enforcement

```json
{
  "id": "F-018",
  "name": "Budget Tier Enforcement",
  "description": "Enforce budget limits at fleet, project, and agent tiers, blocking invocations that would exceed the budget",
  "capability": "C3",
  "epic": "E-003",
  "priority": "must",
  "story_points": 8,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "CostService",
  "interfaces": [],
  "depends_on": ["F-016"],
  "acceptance_criteria": [
    "Agent invocation is blocked with BudgetExceededError if it would exceed agent-level budget",
    "Pipeline run is blocked if it would exceed project-level budget",
    "Fleet-level $25 ceiling is enforced per pipeline run",
    "Budget check latency is under 50ms (cached in Redis or memory)",
    "Blocked invocation emits audit event with type 'budget.exceeded'",
    "Budget limits are configurable per project via project_config table"
  ]
}
```

---

## E-004: Audit & Compliance

**Capabilities:** C6 (Observability & Audit)
**Priority tier:** should
**Feature count:** 4

### F-019: Query Audit Events

```json
{
  "id": "F-019",
  "name": "Query Audit Events",
  "description": "Query the immutable audit_events table with filters for event type, agent, time range, and severity",
  "capability": "C6",
  "epic": "E-004",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "governance-server",
  "dashboard_view": "Audit Log",
  "shared_service": "AuditService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": [],
  "acceptance_criteria": [
    "GET /api/v1/audit/events returns paginated audit events (default limit 50)",
    "Supports filtering by: event_type, agent_id, run_id, severity, time_range",
    "Events include all 13 JSONL fields as defined in the observability spec",
    "MCP tool query_audit_events returns identical data shape",
    "Response time under 500ms for queries spanning up to 7 days",
    "Dashboard Audit Log page renders events in sortable, filterable table"
  ]
}
```

### F-020: Get Audit Summary

```json
{
  "id": "F-020",
  "name": "Get Audit Summary",
  "description": "Return an aggregated audit summary with event counts by type, severity distribution, and top agents by event volume",
  "capability": "C6",
  "epic": "E-004",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "governance-server",
  "dashboard_view": "Audit Log",
  "shared_service": "AuditService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-019"],
  "acceptance_criteria": [
    "GET /api/v1/audit/summary returns event_count_by_type, severity_distribution, top_agents",
    "Supports time range parameter (default: last 24 hours)",
    "MCP tool get_audit_summary returns identical data shape",
    "Dashboard Audit Log page renders summary cards at top of page",
    "Computation completes within 1 second for up to 100K events"
  ]
}
```

### F-021: Export Audit Report

```json
{
  "id": "F-021",
  "name": "Export Audit Report",
  "description": "Export filtered audit events as a downloadable CSV or JSONL file for compliance reporting",
  "capability": "C6",
  "epic": "E-004",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "none",
  "dashboard_view": "Audit Log",
  "shared_service": "AuditService",
  "interfaces": ["rest", "dashboard"],
  "depends_on": ["F-019"],
  "acceptance_criteria": [
    "GET /api/v1/audit/export?format=csv returns CSV with all 13 audit fields",
    "GET /api/v1/audit/export?format=jsonl returns JSONL with one event per line",
    "Export respects the same filters as query_audit_events",
    "Export of 10K events completes within 10 seconds",
    "Dashboard Audit Log page has 'Export' button that downloads the file"
  ]
}
```

### F-022: PII Detection in Outputs

```json
{
  "id": "F-022",
  "name": "PII Detection in Outputs",
  "description": "Scan agent outputs for personally identifiable information (PII) patterns and flag or redact before storage",
  "capability": "C6",
  "epic": "E-004",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "AuditService",
  "interfaces": [],
  "depends_on": [],
  "acceptance_criteria": [
    "PII scanner detects: email addresses, phone numbers, SSNs, credit card numbers",
    "Detection runs on every agent output before persistence",
    "Detected PII is flagged in audit event with pii_detected=true",
    "Optional redaction mode replaces PII with [REDACTED] tokens",
    "False negative rate below 2% on standard PII test corpus",
    "Scanning adds less than 50ms latency per output"
  ]
}
```

---

## E-005: Human Approval Gates

**Capabilities:** C4 (Human-in-the-Loop)
**Priority tier:** must
**Feature count:** 6

### F-023: Create Approval Request

```json
{
  "id": "F-023",
  "name": "Create Approval Request",
  "description": "Create a pending approval request when a pipeline reaches a gate that requires human review based on autonomy tier",
  "capability": "C4",
  "epic": "E-005",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "ApprovalService",
  "interfaces": [],
  "depends_on": ["F-001"],
  "acceptance_criteria": [
    "Approval request is created with: run_id, phase, agent_id, gate_type, context_summary",
    "Request is persisted in approval_requests table with status 'pending'",
    "Pipeline execution pauses at the gate until approval is granted or timeout occurs",
    "Autonomy tier T0 (full human review) creates approval for every phase output",
    "Autonomy tier T3 (full autonomy) skips approval gate creation",
    "Audit event is emitted with type 'approval.requested'"
  ]
}
```

### F-024: List Pending Approvals

```json
{
  "id": "F-024",
  "name": "List Pending Approvals",
  "description": "Return all pending approval requests with filtering by project, phase, and age",
  "capability": "C4",
  "epic": "E-005",
  "priority": "must",
  "story_points": 3,
  "mcp_server": "governance-server",
  "dashboard_view": "Approval Queue",
  "shared_service": "ApprovalService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-023"],
  "acceptance_criteria": [
    "GET /api/v1/approvals?status=pending returns paginated list of pending approvals",
    "Each approval includes: approval_id, run_id, phase, gate_type, created_at, context_summary",
    "Filtering by project_id and phase is supported",
    "Results are sorted by created_at ascending (oldest first)",
    "MCP tool list_pending_approvals returns identical data shape",
    "Dashboard Approval Queue page auto-refreshes every 10 seconds"
  ]
}
```

### F-025: Approve Gate

```json
{
  "id": "F-025",
  "name": "Approve Gate",
  "description": "Approve a pending approval request, unblocking the pipeline to proceed to the next phase",
  "capability": "C4",
  "epic": "E-005",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "governance-server",
  "dashboard_view": "Approval Queue",
  "shared_service": "ApprovalService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-023", "F-024"],
  "acceptance_criteria": [
    "POST /api/v1/approvals/{approval_id}/approve sets status to 'approved'",
    "Pipeline run resumes within 5 seconds of approval",
    "Approver identity is recorded (user_id or api_key_id)",
    "Already-approved or already-rejected request returns 409 Conflict",
    "Audit event is emitted with type 'approval.approved'",
    "Dashboard Approval Queue page has 'Approve' button per pending item"
  ]
}
```

### F-026: Reject Gate with Comment

```json
{
  "id": "F-026",
  "name": "Reject Gate with Comment",
  "description": "Reject a pending approval request with a mandatory comment explaining the rejection reason",
  "capability": "C4",
  "epic": "E-005",
  "priority": "must",
  "story_points": 3,
  "mcp_server": "governance-server",
  "dashboard_view": "Approval Queue",
  "shared_service": "ApprovalService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-023", "F-024"],
  "acceptance_criteria": [
    "POST /api/v1/approvals/{approval_id}/reject requires a non-empty comment field",
    "Rejection sets approval status to 'rejected' and pipeline run to 'blocked'",
    "Rejection comment is persisted and visible in audit trail",
    "Missing or empty comment returns 422 Unprocessable Entity",
    "Audit event is emitted with type 'approval.rejected'",
    "Dashboard Approval Queue page has 'Reject' button with comment textarea"
  ]
}
```

### F-027: Approval Timeout and Escalation

```json
{
  "id": "F-027",
  "name": "Approval Timeout and Escalation",
  "description": "Automatically escalate approval requests that exceed the configured timeout, notifying escalation contacts",
  "capability": "C4",
  "epic": "E-005",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "ApprovalService",
  "interfaces": [],
  "depends_on": ["F-023"],
  "acceptance_criteria": [
    "Approval request exceeding timeout (default 30 minutes) is escalated",
    "Escalation sends notification to configured escalation contacts",
    "Timeout duration is configurable per gate_type in project configuration",
    "Escalated approval changes status to 'escalated' (still pending decision)",
    "After second timeout (2x original), pipeline is auto-rejected with timeout reason",
    "Audit event is emitted with type 'approval.escalated'"
  ]
}
```

### F-028: Slack Notification on Approval Needed

```json
{
  "id": "F-028",
  "name": "Slack Notification on Approval Needed",
  "description": "Send a Slack notification to the configured channel when a new approval request is created, with approve/reject action buttons",
  "capability": "C4",
  "epic": "E-005",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "ApprovalService",
  "interfaces": [],
  "depends_on": ["F-023"],
  "acceptance_criteria": [
    "Slack message is sent within 10 seconds of approval request creation",
    "Message includes: run_id, phase, gate_type, context_summary, and deep link to dashboard",
    "Slack channel is configurable per project via SLACK_CHANNEL_ID",
    "Slack integration gracefully degrades if webhook fails (logs warning, does not block pipeline)",
    "Message includes interactive approve/reject buttons (Slack Block Kit)",
    "Slack action triggers the same ApprovalService.approve/reject methods"
  ]
}
```

---

## E-006: Knowledge Management

**Capabilities:** C7 (Knowledge Management)
**Priority tier:** should
**Feature count:** 5

### F-029: Search Exceptions

```json
{
  "id": "F-029",
  "name": "Search Exceptions",
  "description": "Search the knowledge base for exceptions matching a query string, filtered by tier and category",
  "capability": "C7",
  "epic": "E-006",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "knowledge-server",
  "dashboard_view": "none",
  "shared_service": "KnowledgeService",
  "interfaces": ["mcp", "rest"],
  "depends_on": [],
  "acceptance_criteria": [
    "GET /api/v1/knowledge/exceptions/search?q={query} returns ranked matches",
    "Supports filtering by tier (client, stack, universal) and category",
    "Results include: exception_id, title, description, tier, relevance_score",
    "MCP tool search_exceptions returns identical data shape",
    "Search latency under 200ms for up to 10K exceptions",
    "Empty query returns 422 with descriptive error"
  ]
}
```

### F-030: Create Exception

```json
{
  "id": "F-030",
  "name": "Create Exception",
  "description": "Create a new knowledge base exception from a pipeline failure or manual submission, stored at the client tier by default",
  "capability": "C7",
  "epic": "E-006",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "knowledge-server",
  "dashboard_view": "none",
  "shared_service": "KnowledgeService",
  "interfaces": ["mcp", "rest"],
  "depends_on": [],
  "acceptance_criteria": [
    "POST /api/v1/knowledge/exceptions creates exception with title, description, category, resolution",
    "New exceptions default to 'client' tier",
    "Exception is persisted in knowledge_exceptions table",
    "Duplicate detection warns if similar exception exists (>80% similarity)",
    "MCP tool create_exception returns created exception with id",
    "Audit event is emitted with type 'knowledge.exception_created'"
  ]
}
```

### F-031: Promote Exception

```json
{
  "id": "F-031",
  "name": "Promote Exception",
  "description": "Promote an exception from client tier to stack tier, or from stack tier to universal tier, after validation",
  "capability": "C7",
  "epic": "E-006",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "knowledge-server",
  "dashboard_view": "none",
  "shared_service": "KnowledgeService",
  "interfaces": ["mcp", "rest"],
  "depends_on": ["F-030"],
  "acceptance_criteria": [
    "POST /api/v1/knowledge/exceptions/{id}/promote moves exception to next tier",
    "Promotion from client to stack requires minimum 3 occurrences across projects",
    "Promotion from stack to universal requires validation by operator",
    "Attempting to promote a universal exception returns 400",
    "MCP tool promote_exception returns updated exception",
    "Audit event is emitted with type 'knowledge.exception_promoted'"
  ]
}
```

### F-032: List Exceptions by Tier

```json
{
  "id": "F-032",
  "name": "List Exceptions by Tier",
  "description": "Return paginated list of exceptions filtered by knowledge tier with sorting by recency or frequency",
  "capability": "C7",
  "epic": "E-006",
  "priority": "should",
  "story_points": 2,
  "mcp_server": "knowledge-server",
  "dashboard_view": "Fleet Health",
  "shared_service": "KnowledgeService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-030"],
  "acceptance_criteria": [
    "GET /api/v1/knowledge/exceptions?tier=stack returns paginated exceptions for that tier",
    "Supports sorting by: created_at, occurrence_count, last_seen_at",
    "MCP tool list_exceptions returns identical data shape",
    "Dashboard Fleet Health page shows exception count badges per tier",
    "Pagination via limit/offset with default limit of 50"
  ]
}
```

### F-033: Exception Auto-Injection into Prompts

```json
{
  "id": "F-033",
  "name": "Exception Auto-Injection into Prompts",
  "description": "Automatically inject relevant exceptions from the knowledge base into agent prompts before invocation to prevent known failures",
  "capability": "C7",
  "epic": "E-006",
  "priority": "should",
  "story_points": 8,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "KnowledgeService",
  "interfaces": [],
  "depends_on": ["F-029", "F-010"],
  "acceptance_criteria": [
    "Before each agent invocation, relevant exceptions are retrieved and appended to system prompt",
    "Relevance matching uses agent phase, category, and input content",
    "Maximum of 5 exceptions injected per invocation to limit token usage",
    "Injected exceptions add less than 500 tokens to the prompt",
    "Exception injection is logged in audit event with injected exception IDs",
    "Injection can be disabled per agent via agent configuration"
  ]
}
```

---

## E-007: MCP Server Infrastructure

**Capabilities:** C11 (MCP Server Exposure)
**Priority tier:** must
**Feature count:** 6

### F-034: MCP Agents-Server with Tool Registry

```json
{
  "id": "F-034",
  "name": "MCP Agents-Server with Tool Registry",
  "description": "Run the agents-server MCP server exposing pipeline and agent tools via the Model Context Protocol",
  "capability": "C11",
  "epic": "E-007",
  "priority": "must",
  "story_points": 8,
  "mcp_server": "agents-server",
  "dashboard_view": "none",
  "shared_service": "PipelineService",
  "interfaces": ["mcp"],
  "depends_on": ["F-001", "F-008"],
  "acceptance_criteria": [
    "Server starts on configured port and responds to MCP initialize handshake",
    "tools/list returns all registered agent and pipeline tools with JSON Schema",
    "tools/call dispatches to correct shared service method",
    "Server handles concurrent connections from multiple MCP clients",
    "Tool execution timeout is enforced (default 120s)",
    "Server logs all tool calls with structured logging"
  ]
}
```

### F-035: MCP Governance-Server with Tool Registry

```json
{
  "id": "F-035",
  "name": "MCP Governance-Server with Tool Registry",
  "description": "Run the governance-server MCP server exposing cost, audit, and approval tools via the Model Context Protocol",
  "capability": "C11",
  "epic": "E-007",
  "priority": "must",
  "story_points": 8,
  "mcp_server": "governance-server",
  "dashboard_view": "none",
  "shared_service": "CostService",
  "interfaces": ["mcp"],
  "depends_on": ["F-014", "F-019", "F-024"],
  "acceptance_criteria": [
    "Server starts on configured port and responds to MCP initialize handshake",
    "tools/list returns all governance tools (cost, audit, approval) with JSON Schema",
    "tools/call dispatches to correct shared service method",
    "Server handles concurrent connections from multiple MCP clients",
    "All tool calls are audit-logged",
    "Budget enforcement is applied before cost-related tool execution"
  ]
}
```

### F-036: MCP Knowledge-Server with Tool Registry

```json
{
  "id": "F-036",
  "name": "MCP Knowledge-Server with Tool Registry",
  "description": "Run the knowledge-server MCP server exposing exception search, creation, and promotion tools via the Model Context Protocol",
  "capability": "C11",
  "epic": "E-007",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "knowledge-server",
  "dashboard_view": "none",
  "shared_service": "KnowledgeService",
  "interfaces": ["mcp"],
  "depends_on": ["F-029", "F-030"],
  "acceptance_criteria": [
    "Server starts on configured port and responds to MCP initialize handshake",
    "tools/list returns all knowledge tools with JSON Schema",
    "tools/call dispatches to KnowledgeService methods",
    "Server handles concurrent connections from multiple MCP clients",
    "All tool calls are audit-logged",
    "Search results are ranked by relevance score"
  ]
}
```

### F-037: MCP Authentication

```json
{
  "id": "F-037",
  "name": "MCP Authentication",
  "description": "Authenticate MCP client connections using API keys validated against a secure key store",
  "capability": "C11",
  "epic": "E-007",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "agents-server",
  "dashboard_view": "none",
  "shared_service": "SessionService",
  "interfaces": ["mcp"],
  "depends_on": ["F-034", "F-035", "F-036"],
  "acceptance_criteria": [
    "MCP connection without valid API key is rejected with authentication error",
    "API keys are stored hashed (SHA-256) in api_keys table",
    "Each API key is scoped to specific MCP servers (agents, governance, knowledge)",
    "Key rotation is supported without downtime (old key valid for 24h grace period)",
    "Failed authentication attempts are logged as audit events",
    "Rate limiting is applied per API key (default 100 requests/minute)"
  ]
}
```

### F-038: MCP Resource Exposure

```json
{
  "id": "F-038",
  "name": "MCP Resource Exposure",
  "description": "Expose agent manifests and prompt templates as MCP resources that clients can read and subscribe to",
  "capability": "C11",
  "epic": "E-007",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "agents-server",
  "dashboard_view": "none",
  "shared_service": "AgentService",
  "interfaces": ["mcp"],
  "depends_on": ["F-034"],
  "acceptance_criteria": [
    "resources/list returns available resources (agent manifests, prompt templates)",
    "resources/read returns the content of a specific resource by URI",
    "Agent manifest resource includes: agent_id, name, phase, model, capabilities",
    "Resource URIs follow pattern: sdlc://agents/{agent_id}/manifest",
    "Resources are cached with 5-minute TTL",
    "Resource updates trigger notifications to subscribed clients"
  ]
}
```

### F-039: MCP Prompt Templates

```json
{
  "id": "F-039",
  "name": "MCP Prompt Templates",
  "description": "Expose pre-built prompt templates (generate-docs, review-code) via MCP prompts/list and prompts/get",
  "capability": "C11",
  "epic": "E-007",
  "priority": "must",
  "story_points": 3,
  "mcp_server": "agents-server",
  "dashboard_view": "none",
  "shared_service": "AgentService",
  "interfaces": ["mcp"],
  "depends_on": ["F-034"],
  "acceptance_criteria": [
    "prompts/list returns available prompt templates with descriptions",
    "prompts/get returns parameterized prompt with argument schema",
    "generate-docs prompt accepts project_brief and returns structured pipeline trigger",
    "review-code prompt accepts code_snippet and returns review request",
    "Prompt templates are versioned and can be updated without server restart",
    "Each prompt template includes usage examples in its description"
  ]
}
```

---

## E-008: Dashboard / Operator UI

**Capabilities:** C12 (Dashboard / Operator UI)
**Priority tier:** must
**Feature count:** 6

### F-040: Fleet Health Page

```json
{
  "id": "F-040",
  "name": "Fleet Health Page",
  "description": "Streamlit dashboard page displaying real-time health status of all 48 agents grouped by phase with health indicators",
  "capability": "C12",
  "epic": "E-008",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "Fleet Health",
  "shared_service": "HealthService",
  "interfaces": ["dashboard"],
  "depends_on": ["F-008", "F-011"],
  "acceptance_criteria": [
    "Page displays all 48 agents organized by 7 phases",
    "Each agent card shows: name, status, maturity, health indicator (green/yellow/red)",
    "Page auto-refreshes every 30 seconds",
    "Clicking an agent card navigates to agent detail view",
    "Page loads in under 3 seconds",
    "Phase groups are collapsible"
  ]
}
```

### F-041: Cost Monitor Page

```json
{
  "id": "F-041",
  "name": "Cost Monitor Page",
  "description": "Streamlit dashboard page showing real-time cost tracking with budget gauges, trend charts, and anomaly alerts",
  "capability": "C12",
  "epic": "E-008",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "Cost Monitor",
  "shared_service": "CostService",
  "interfaces": ["dashboard"],
  "depends_on": ["F-014", "F-015", "F-017"],
  "acceptance_criteria": [
    "Page displays fleet-level budget gauge with percentage consumed",
    "Cost trend chart shows daily spend for the last 30 days",
    "Top 10 agents by cost are displayed in a ranked bar chart",
    "Anomaly alerts are shown as dismissible warning banners",
    "Page supports filtering by project and date range",
    "Budget threshold colors: green (<60%), yellow (60-80%), red (>80%)"
  ]
}
```

### F-042: Pipeline Runs Page

```json
{
  "id": "F-042",
  "name": "Pipeline Runs Page",
  "description": "Streamlit dashboard page listing all pipeline runs with status, progress bars, and drill-down to phase details",
  "capability": "C12",
  "epic": "E-008",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "Pipeline Runs",
  "shared_service": "PipelineService",
  "interfaces": ["dashboard"],
  "depends_on": ["F-002", "F-003"],
  "acceptance_criteria": [
    "Page displays pipeline runs in a table with: run_id, project, status, progress, created_at",
    "Active runs show animated progress bars",
    "Clicking a run row expands to show phase-by-phase details",
    "Status filter dropdown (all, pending, running, completed, failed, cancelled)",
    "New Run button opens a brief submission form",
    "Page auto-refreshes every 5 seconds for active runs"
  ]
}
```

### F-043: Audit Log Page

```json
{
  "id": "F-043",
  "name": "Audit Log Page",
  "description": "Streamlit dashboard page showing the immutable audit event stream with filtering, search, and export capabilities",
  "capability": "C12",
  "epic": "E-008",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "Audit Log",
  "shared_service": "AuditService",
  "interfaces": ["dashboard"],
  "depends_on": ["F-019", "F-020", "F-021"],
  "acceptance_criteria": [
    "Page displays audit events in a scrollable table with all 13 JSONL fields",
    "Summary cards at top show: total events, events by severity, events by type",
    "Filter panel supports: event_type, agent_id, severity, date range",
    "Full-text search across event descriptions",
    "Export button downloads filtered results as CSV or JSONL",
    "Page loads last 100 events by default with infinite scroll"
  ]
}
```

### F-044: Approval Queue Page

```json
{
  "id": "F-044",
  "name": "Approval Queue Page",
  "description": "Streamlit dashboard page displaying pending approval requests with approve/reject actions and context preview",
  "capability": "C12",
  "epic": "E-008",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "Approval Queue",
  "shared_service": "ApprovalService",
  "interfaces": ["dashboard"],
  "depends_on": ["F-024", "F-025", "F-026"],
  "acceptance_criteria": [
    "Page displays pending approvals sorted by age (oldest first)",
    "Each approval card shows: run_id, phase, gate_type, age, context_summary",
    "Approve button immediately approves and removes from queue",
    "Reject button opens comment dialog, requires non-empty comment",
    "Escalated approvals are highlighted with warning indicator",
    "Page auto-refreshes every 10 seconds",
    "Badge in navigation shows count of pending approvals"
  ]
}
```

### F-045: MCP Monitoring Panel

```json
{
  "id": "F-045",
  "name": "MCP Monitoring Panel",
  "description": "Dashboard panel showing connected MCP clients, recent tool calls, and server health across all three MCP servers",
  "capability": "C12",
  "epic": "E-008",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "Fleet Health",
  "shared_service": "HealthService",
  "interfaces": ["dashboard"],
  "depends_on": ["F-034", "F-035", "F-036"],
  "acceptance_criteria": [
    "Panel shows three server cards (agents, governance, knowledge) with up/down status",
    "Each server card displays: connected clients count, requests/min, error rate",
    "Recent tool calls table shows last 20 calls with: tool_name, client_id, latency, status",
    "Server health check runs every 15 seconds",
    "Panel is accessible from Fleet Health page",
    "Down server triggers visual alert (red indicator + notification)"
  ]
}
```

---

## E-009: Quality & Testing

**Capabilities:** C5 (Quality Assurance)
**Priority tier:** should
**Feature count:** 4

### F-046: Quality Scoring per Agent Output

```json
{
  "id": "F-046",
  "name": "Quality Scoring per Agent Output",
  "description": "Compute an aggregate quality score (0-100) for each agent output based on configurable rubric dimensions",
  "capability": "C5",
  "epic": "E-009",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "AgentService",
  "interfaces": [],
  "depends_on": ["F-047"],
  "acceptance_criteria": [
    "Every agent invocation output receives a quality score between 0 and 100",
    "Score is computed as weighted average of rubric dimension scores",
    "Score is persisted in invocation_results table alongside the output",
    "Scoring completes within 5 seconds of output generation",
    "Score below 70 triggers a warning in structured logs",
    "Score below 50 triggers self-healing retry (F-007)"
  ]
}
```

### F-047: Rubric-Based Evaluation

```json
{
  "id": "F-047",
  "name": "Rubric-Based Evaluation",
  "description": "Evaluate agent outputs against multi-dimensional rubrics specific to each agent phase and document type",
  "capability": "C5",
  "epic": "E-009",
  "priority": "should",
  "story_points": 8,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "AgentService",
  "interfaces": [],
  "depends_on": [],
  "acceptance_criteria": [
    "Each agent has a configured rubric with 3-7 dimensions",
    "Dimensions include: completeness, accuracy, formatting, consistency, traceability",
    "Each dimension is scored 0-100 with configurable weight",
    "Rubric definitions are stored in agent configuration (not hardcoded)",
    "Rubric evaluation uses a dedicated evaluator prompt (separate Claude call)",
    "Evaluation cost is tracked as a separate cost event"
  ]
}
```

### F-048: Golden Test Execution

```json
{
  "id": "F-048",
  "name": "Golden Test Execution",
  "description": "Execute golden tests (known-good input/output pairs) against agents to verify baseline quality on every version change",
  "capability": "C5",
  "epic": "E-009",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "AgentService",
  "interfaces": [],
  "depends_on": ["F-046", "F-012"],
  "acceptance_criteria": [
    "Each agent has at least 3 golden test cases stored in golden_tests table",
    "Golden tests are executed automatically on agent version promotion",
    "Test passes if output quality score meets 90% threshold",
    "All golden test results are persisted with: agent_id, version, score, pass/fail",
    "Failed golden tests block version promotion (F-012)",
    "Golden test execution cost is capped at $1 per agent per run"
  ]
}
```

### F-049: Adversarial Test Execution

```json
{
  "id": "F-049",
  "name": "Adversarial Test Execution",
  "description": "Execute adversarial tests (edge cases, malformed inputs, prompt injection attempts) to verify agent robustness",
  "capability": "C5",
  "epic": "E-009",
  "priority": "should",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "AgentService",
  "interfaces": [],
  "depends_on": ["F-046"],
  "acceptance_criteria": [
    "Each agent has at least 2 adversarial test cases",
    "Adversarial tests include: empty input, oversized input, prompt injection, conflicting instructions",
    "Agent must handle adversarial input gracefully (no crash, no PII leak, no prompt leak)",
    "Test results are persisted with: agent_id, test_type, outcome, details",
    "Adversarial test suite runs weekly on all production agents",
    "New adversarial patterns from the exception flywheel are automatically added"
  ]
}
```

---

## E-010: Platform Foundation

**Capabilities:** C10 (Multi-Project Isolation), cross-cutting
**Priority tier:** mixed (must/should/could)
**Feature count:** 7

### F-050: Session Context Store

```json
{
  "id": "F-050",
  "name": "Session Context Store",
  "description": "Provide a key-value session store for pipeline runs to share context between agents within the same run",
  "capability": "C10",
  "epic": "E-010",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "SessionService",
  "interfaces": [],
  "depends_on": [],
  "acceptance_criteria": [
    "SessionService.set(run_id, key, value) persists context in session_store table",
    "SessionService.get(run_id, key) retrieves stored value",
    "SessionService.list(run_id) returns all keys for a run",
    "Session data is isolated by run_id (no cross-run leakage)",
    "Read/write latency under 50ms",
    "Session data is automatically cleaned up 30 days after run completion"
  ]
}
```

### F-051: Multi-Project Namespace Isolation

```json
{
  "id": "F-051",
  "name": "Multi-Project Namespace Isolation",
  "description": "Enforce data isolation between projects using namespace prefixes on all database queries and storage paths",
  "capability": "C10",
  "epic": "E-010",
  "priority": "must",
  "story_points": 8,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "SessionService",
  "interfaces": [],
  "depends_on": [],
  "acceptance_criteria": [
    "All database queries include project_id filter (enforced at service layer)",
    "Pipeline runs, cost events, audit events, and approvals are scoped to project_id",
    "Cross-project data access returns empty results (not an error)",
    "Project-specific budget limits are enforced independently",
    "Client-tier knowledge exceptions are scoped to their originating project",
    "API requests without project_id default to the configured default project"
  ]
}
```

### F-052: Rate Limiting for LLM Provider API Calls

```json
{
  "id": "F-052",
  "name": "Rate Limiting for LLM Provider API Calls",
  "description": "Enforce configurable rate limits on Claude API calls to prevent quota exhaustion and ensure fair usage across agents",
  "capability": "C10",
  "epic": "E-010",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "AgentService",
  "interfaces": [],
  "depends_on": [],
  "acceptance_criteria": [
    "Rate limiter enforces requests/minute limit per agent (default 30 RPM)",
    "Rate limiter enforces tokens/minute limit per agent (default 100K TPM)",
    "Exceeded rate limit queues the request with exponential backoff",
    "Fleet-wide rate limit prevents total API usage from exceeding Anthropic tier limits",
    "Rate limit state is stored in-memory with Redis fallback for multi-process",
    "Rate limit metrics are exposed via structured logging"
  ]
}
```

### F-053: Database Migrations

```json
{
  "id": "F-053",
  "name": "Database Migrations",
  "description": "Manage PostgreSQL schema migrations (005-008) for new tables and indexes required by the platform",
  "capability": "C10",
  "epic": "E-010",
  "priority": "must",
  "story_points": 5,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "SessionService",
  "interfaces": [],
  "depends_on": [],
  "acceptance_criteria": [
    "Migration 005: Create knowledge_exceptions table with tier, category, and full-text search index",
    "Migration 006: Create api_keys table with hashed key, scopes, and expiration",
    "Migration 007: Add project_id column to pipeline_runs, cost_events, audit_events tables",
    "Migration 008: Create golden_tests and adversarial_tests tables",
    "All migrations are idempotent (safe to re-run)",
    "Migrations run via 'python -m alembic upgrade head' or equivalent",
    "Rollback scripts exist for each migration"
  ]
}
```

### F-054: Health Endpoint and Readiness Probe

```json
{
  "id": "F-054",
  "name": "Health Endpoint and Readiness Probe",
  "description": "Expose HTTP health and readiness endpoints for container orchestration and monitoring systems",
  "capability": "C10",
  "epic": "E-010",
  "priority": "must",
  "story_points": 2,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "HealthService",
  "interfaces": ["rest"],
  "depends_on": [],
  "acceptance_criteria": [
    "GET /health returns 200 with {status: 'healthy'} when service is running",
    "GET /ready returns 200 only when database connection and Claude API are reachable",
    "GET /ready returns 503 with details when any dependency is unreachable",
    "Health check response time under 100ms",
    "Readiness check caches dependency status for 10 seconds to prevent thundering herd"
  ]
}
```

### F-055: Structured Logging

```json
{
  "id": "F-055",
  "name": "Structured Logging",
  "description": "Emit all application logs as structured JSON via structlog with consistent fields for correlation and analysis",
  "capability": "C10",
  "epic": "E-010",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "HealthService",
  "interfaces": [],
  "depends_on": [],
  "acceptance_criteria": [
    "All log entries are JSON-formatted with: timestamp, level, message, module, correlation_id",
    "Pipeline run operations include run_id in log context",
    "Agent invocations include agent_id and invocation_id in log context",
    "Log level is configurable via LOG_LEVEL environment variable",
    "Sensitive fields (API keys, tokens) are redacted in logs",
    "Logs are written to stdout for container log collection"
  ]
}
```

### F-056: CI/CD Pipeline

```json
{
  "id": "F-056",
  "name": "CI/CD Pipeline",
  "description": "GitHub Actions workflow for linting, testing, building, and deploying the platform with quality gates",
  "capability": "C10",
  "epic": "E-010",
  "priority": "could",
  "story_points": 8,
  "mcp_server": "none",
  "dashboard_view": "none",
  "shared_service": "HealthService",
  "interfaces": [],
  "depends_on": ["F-048", "F-049"],
  "acceptance_criteria": [
    "CI pipeline runs on every pull request to main branch",
    "Pipeline stages: lint (ruff), type-check (mypy), unit tests, integration tests",
    "Quality gate: 90% code coverage required for merge",
    "Quality gate: all golden tests must pass",
    "CD pipeline deploys to staging on merge to main",
    "CD pipeline deploys to production on manual approval",
    "Pipeline completes within 10 minutes for a typical PR"
  ]
}
```

### F-057: LLM Provider Selection

```json
{
  "id": "F-057",
  "name": "LLM Provider Selection",
  "description": "Configure which LLM provider an agent uses via manifest tier (fast/balanced/powerful) or LLM_PROVIDER env var. Supports Anthropic, OpenAI, and Ollama via sdk/llm/ abstraction.",
  "capability": "C1",
  "epic": "E-010",
  "priority": "must",
  "story_points": 8,
  "mcp_server": "agents-server",
  "dashboard_view": "Fleet Health page (provider status), Agent Detail panel (provider override)",
  "shared_service": "HealthService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-011"],
  "acceptance_criteria": [
    "Agents use tier-based model selection (fast/balanced/powerful) instead of hardcoded model names",
    "LLM_PROVIDER env var switches all agents to specified provider (anthropic, openai, ollama)",
    "Per-agent provider: override in manifest.yaml overrides global LLM_PROVIDER",
    "sdk/llm/factory.py creates correct provider instance from env or manifest config",
    "Cost calculation is provider-aware (Anthropic pricing, OpenAI pricing, Ollama = $0.00)",
    "Switching provider does not require any agent code changes"
  ]
}
```

### F-058: Provider Health Check

```json
{
  "id": "F-058",
  "name": "Provider Health Check",
  "description": "Verify LLM provider is reachable and responding within acceptable latency. Reports provider status in fleet health.",
  "capability": "C1",
  "epic": "E-010",
  "priority": "should",
  "story_points": 3,
  "mcp_server": "agents-server",
  "dashboard_view": "Fleet Health page (provider status panel)",
  "shared_service": "HealthService",
  "interfaces": ["mcp", "rest", "dashboard"],
  "depends_on": ["F-057"],
  "acceptance_criteria": [
    "Health check endpoint pings each configured LLM provider with a minimal prompt",
    "Returns provider_name, healthy (bool), latency_ms, model_count, default_tier",
    "Unhealthy provider triggers circuit breaker preventing agent invocations on that provider",
    "Provider health is included in fleet health dashboard",
    "Health check completes within 5 seconds per provider"
  ]
}
```

---

## Summary Table

| ID | Name | Priority | Epic | Interfaces | Shared Service | Story Points |
|----|------|----------|------|------------|---------------|-------------|
| F-001 | Trigger Pipeline | must | E-001 | mcp, rest, dashboard | PipelineService | 8 |
| F-002 | Get Pipeline Status | must | E-001 | mcp, rest, dashboard | PipelineService | 5 |
| F-003 | List Pipeline Runs | must | E-001 | mcp, rest, dashboard | PipelineService | 3 |
| F-004 | Resume Pipeline from Checkpoint | must | E-001 | mcp, rest | PipelineService | 8 |
| F-005 | Cancel Pipeline | must | E-001 | mcp, rest | PipelineService | 5 |
| F-006 | Pipeline Parallel DAG Execution | must | E-001 | (service-only) | PipelineService | 13 |
| F-007 | Pipeline Self-Healing on Test Failure | must | E-001 | (service-only) | PipelineService | 8 |
| F-008 | List Agents with Status | should | E-002 | mcp, rest, dashboard | AgentService | 3 |
| F-009 | Get Agent Detail | should | E-002 | mcp, rest, dashboard | AgentService | 3 |
| F-010 | Invoke Agent Directly | should | E-002 | mcp, rest | AgentService | 5 |
| F-011 | Agent Health Check | should | E-002 | mcp, rest, dashboard | HealthService | 3 |
| F-012 | Agent Version Management | should | E-002 | mcp, rest, dashboard | AgentService | 8 |
| F-013 | Agent Maturity Progression Tracking | should | E-002 | rest, dashboard | AgentService | 5 |
| F-014 | Get Cost Report | must | E-003 | mcp, rest, dashboard | CostService | 5 |
| F-015 | Check Budget Remaining | must | E-003 | mcp, rest, dashboard | CostService | 3 |
| F-016 | Record Spend Event | must | E-003 | (service-only) | CostService | 3 |
| F-017 | Cost Anomaly Detection and Alert | must | E-003 | dashboard | CostService | 5 |
| F-018 | Budget Tier Enforcement | must | E-003 | (service-only) | CostService | 8 |
| F-019 | Query Audit Events | should | E-004 | mcp, rest, dashboard | AuditService | 5 |
| F-020 | Get Audit Summary | should | E-004 | mcp, rest, dashboard | AuditService | 3 |
| F-021 | Export Audit Report | should | E-004 | rest, dashboard | AuditService | 3 |
| F-022 | PII Detection in Outputs | should | E-004 | (service-only) | AuditService | 5 |
| F-023 | Create Approval Request | must | E-005 | (service-only) | ApprovalService | 5 |
| F-024 | List Pending Approvals | must | E-005 | mcp, rest, dashboard | ApprovalService | 3 |
| F-025 | Approve Gate | must | E-005 | mcp, rest, dashboard | ApprovalService | 5 |
| F-026 | Reject Gate with Comment | must | E-005 | mcp, rest, dashboard | ApprovalService | 3 |
| F-027 | Approval Timeout and Escalation | must | E-005 | (service-only) | ApprovalService | 5 |
| F-028 | Slack Notification on Approval Needed | must | E-005 | (service-only) | ApprovalService | 5 |
| F-029 | Search Exceptions | should | E-006 | mcp, rest | KnowledgeService | 5 |
| F-030 | Create Exception | should | E-006 | mcp, rest | KnowledgeService | 3 |
| F-031 | Promote Exception | should | E-006 | mcp, rest | KnowledgeService | 5 |
| F-032 | List Exceptions by Tier | should | E-006 | mcp, rest, dashboard | KnowledgeService | 2 |
| F-033 | Exception Auto-Injection into Prompts | should | E-006 | (service-only) | KnowledgeService | 8 |
| F-034 | MCP Agents-Server with Tool Registry | must | E-007 | mcp | PipelineService | 8 |
| F-035 | MCP Governance-Server with Tool Registry | must | E-007 | mcp | CostService | 8 |
| F-036 | MCP Knowledge-Server with Tool Registry | must | E-007 | mcp | KnowledgeService | 5 |
| F-037 | MCP Authentication | must | E-007 | mcp | SessionService | 5 |
| F-038 | MCP Resource Exposure | must | E-007 | mcp | AgentService | 5 |
| F-039 | MCP Prompt Templates | must | E-007 | mcp | AgentService | 3 |
| F-040 | Fleet Health Page | must | E-008 | dashboard | HealthService | 5 |
| F-041 | Cost Monitor Page | must | E-008 | dashboard | CostService | 5 |
| F-042 | Pipeline Runs Page | must | E-008 | dashboard | PipelineService | 5 |
| F-043 | Audit Log Page | must | E-008 | dashboard | AuditService | 5 |
| F-044 | Approval Queue Page | must | E-008 | dashboard | ApprovalService | 5 |
| F-045 | MCP Monitoring Panel | must | E-008 | dashboard | HealthService | 5 |
| F-046 | Quality Scoring per Agent Output | should | E-009 | (service-only) | AgentService | 5 |
| F-047 | Rubric-Based Evaluation | should | E-009 | (service-only) | AgentService | 8 |
| F-048 | Golden Test Execution | should | E-009 | (service-only) | AgentService | 5 |
| F-049 | Adversarial Test Execution | should | E-009 | (service-only) | AgentService | 5 |
| F-050 | Session Context Store | should | E-010 | (service-only) | SessionService | 3 |
| F-051 | Multi-Project Namespace Isolation | must | E-010 | (service-only) | SessionService | 8 |
| F-052 | Rate Limiting for LLM Provider API Calls | must | E-010 | (service-only) | AgentService | 5 |
| F-053 | Database Migrations | must | E-010 | (service-only) | SessionService | 5 |
| F-054 | Health Endpoint and Readiness Probe | must | E-010 | rest | HealthService | 2 |
| F-055 | Structured Logging | should | E-010 | (cross-cutting) | HealthService | 3 |
| F-056 | CI/CD Pipeline | could | E-010 | (cross-cutting) | HealthService | 8 |
| F-057 | LLM Provider Selection | must | E-010 | mcp, rest, dashboard | HealthService | 8 |
| F-058 | Provider Health Check | should | E-010 | mcp, rest, dashboard | HealthService | 3 |

---

## Statistics

### Total Features
**58 features** across 10 epics

### By Priority

| Priority | Count | Percentage |
|----------|-------|------------|
| must     | 36    | 64.3%      |
| should   | 19    | 33.9%      |
| could    | 1     | 1.8%       |
| wont     | 0     | 0.0%       |
| **Total** | **56** | **100%** |

### By Interface

| Interface | Feature Count | Percentage of Total |
|-----------|--------------|---------------------|
| MCP       | 24           | 42.9%               |
| REST      | 25           | 44.6%               |
| Dashboard | 25           | 44.6%               |
| Service-only | 17        | 30.4%               |
| Cross-cutting | 2        | 3.6%                |

> Note: Features may expose multiple interfaces, so percentages sum to >100%.

### By Epic

| Epic | Name | Feature Count | Story Points |
|------|------|--------------|-------------|
| E-001 | Pipeline Execution | 7 | 50 |
| E-002 | Agent Management | 6 | 27 |
| E-003 | Cost & Budget | 5 | 24 |
| E-004 | Audit & Compliance | 4 | 16 |
| E-005 | Human Approval Gates | 6 | 26 |
| E-006 | Knowledge Management | 5 | 23 |
| E-007 | MCP Server Infrastructure | 6 | 34 |
| E-008 | Dashboard / Operator UI | 6 | 30 |
| E-009 | Quality & Testing | 4 | 23 |
| E-010 | Platform Foundation | 7 | 34 |
| **Total** | | **56** | **287** |

### By Shared Service

| Shared Service | Feature Count |
|---------------|--------------|
| PipelineService | 10 |
| AgentService | 13 |
| CostService | 7 |
| AuditService | 5 |
| ApprovalService | 7 |
| KnowledgeService | 6 |
| HealthService | 6 |
| SessionService | 5 |

> Note: Some features reference multiple services; primary service is counted.

### Total Story Points
**287 story points**

### Interface Parity Check (Q-049)
All features exposed via MCP are also exposed via REST: **PASS**
- 24 MCP features, all have corresponding REST endpoints (except MCP-infrastructure features F-034 through F-039 which are MCP-protocol-specific)

---

## Traceability Matrix

| Capability | Features | Count |
|-----------|---------|-------|
| C1: Agent Orchestration | F-008, F-009, F-010, F-011 | 4 |
| C2: 12-Document Generation Pipeline | F-001, F-002, F-003, F-005 | 4 |
| C3: Cost Control & Governance | F-014, F-015, F-016, F-017, F-018 | 5 |
| C4: Human-in-the-Loop | F-023, F-024, F-025, F-026, F-027, F-028 | 6 |
| C5: Quality Assurance | F-046, F-047, F-048, F-049 | 4 |
| C6: Observability & Audit | F-019, F-020, F-021, F-022 | 4 |
| C7: Knowledge Management | F-029, F-030, F-031, F-032, F-033 | 5 |
| C8: Pipeline Resilience | F-004, F-006, F-007 | 3 |
| C9: Agent Lifecycle | F-012, F-013 | 2 |
| C10: Multi-Project Isolation | F-050, F-051, F-052, F-053, F-054, F-055, F-056, F-057, F-058 | 9 |
| C11: MCP Server Exposure | F-034, F-035, F-036, F-037, F-038, F-039 | 6 |
| C12: Dashboard / Operator UI | F-040, F-041, F-042, F-043, F-044, F-045 | 6 |

All 12 PRD capabilities are covered. **Total: 56 features mapping to 12 capabilities.**

---

*End of Feature Catalog*
