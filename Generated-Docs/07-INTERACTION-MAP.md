# INTERACTION-MAP — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 07 of 24 | Status: Draft
**Role:** This is the CONTRACT between MCP-TOOL-SPEC (Doc 08) and DESIGN-SPEC (Doc 09). Both docs MUST reference interaction IDs and data shapes defined here.

---

## Table of Contents

1. [Interaction Inventory](#1-interaction-inventory)
2. [Data Shape Definitions](#2-data-shape-definitions)
3. [Cross-Interface Journeys](#3-cross-interface-journeys)
4. [Naming Conventions](#4-naming-conventions)
5. [Parity Matrix](#5-parity-matrix)
6. [Interaction ID Guidelines](#6-interaction-id-guidelines)
7. [Naming Conflict Resolution](#7-naming-conflict-resolution)

---

## Purpose and Scope

In Full-Stack-First, MCP tools and Dashboard screens are designed IN PARALLEL. Without coordination, they diverge. This document prevents that by defining:

- **Interface-agnostic interactions (I-NNN)** -- each one represents a single user intent, regardless of whether it is fulfilled via MCP tool, REST endpoint, or Dashboard widget.
- **Shared data shapes** -- used by BOTH MCP responses and Dashboard renders. A single service call returns the same shape to both interfaces.
- **Cross-interface journeys** -- multi-step workflows where a user starts on one interface and finishes on another.
- **Naming conventions** -- the canonical vocabulary shared across all downstream documents.

### Downstream Contracts

| Consumer Document | What it reads from this doc |
|---|---|
| **MCP-TOOL-SPEC (Doc 08)** | Interaction IDs, MCP tool names, MCP server assignments, input/output data shapes |
| **DESIGN-SPEC (Doc 09)** | Interaction IDs, Dashboard screen mappings, data shapes for rendering, journey wireframes |
| **DATA-MODEL (Doc 10)** | Data shape field definitions as source for DB schema |
| **API-CONTRACTS (Doc 11)** | REST endpoint names derived from interaction IDs, request/response shapes |
| **BACKLOG (Doc 13)** | Interaction IDs as acceptance-criteria anchors for each story |
| **TESTING (Doc 18)** | Interaction IDs as test-case identifiers for parity verification |

---

## 1. Interaction Inventory

**Total interactions: 30** (within target range 25-35)

### I-001 to I-009: Pipeline Operations

| ID | Interaction | Description | MCP Tool | MCP Server | Dashboard Screen | Shared Service | Data Shape(s) | Features |
|------|-------------|-------------|----------|------------|-----------------|----------------|---------------|----------|
| I-001 | Trigger pipeline | Start a 24-doc generation run for a project | `trigger_pipeline` | agents-server | Pipeline Trigger Form (Pipeline Runs page) | `PipelineService.trigger()` | `PipelineRun` | F-001 |
| I-002 | Get pipeline status | Check progress of a running pipeline | `get_pipeline_status` | agents-server | Pipeline Status Card (Pipeline Runs page) | `PipelineService.get_status()` | `PipelineRun` | F-002 |
| I-003 | List pipeline runs | View all pipeline runs with filters (status, project, date) | `list_pipeline_runs` | agents-server | Pipeline Runs Table (Pipeline Runs page) | `PipelineService.list_runs()` | `PipelineRun[]` | F-003 |
| I-004 | Resume pipeline | Resume from checkpoint after failure or pause | `resume_pipeline` | agents-server | Resume Button (Pipeline Runs page) | `PipelineService.resume()` | `PipelineRun` | F-004 |
| I-005 | Cancel pipeline | Stop a running pipeline gracefully | `cancel_pipeline` | agents-server | Cancel Button (Pipeline Runs page) | `PipelineService.cancel()` | `PipelineRun` | F-005 |
| I-006 | Get pipeline documents | Retrieve generated documents from a completed run | `get_pipeline_documents` | agents-server | Document Viewer (Pipeline Runs page) | `PipelineService.get_documents()` | `PipelineDocument[]` | F-002, F-006 |
| I-007 | Retry pipeline step | Re-execute a single failed step within a run | `retry_pipeline_step` | agents-server | Retry Button (Pipeline Runs page) | `PipelineService.retry_step()` | `PipelineRun` | F-004, F-007 |
| I-008 | Get pipeline config | Retrieve pipeline configuration and step definitions | `get_pipeline_config` | agents-server | Config Panel (Pipeline Runs page) | `PipelineService.get_config()` | `PipelineConfig` | F-001 |
| I-009 | Validate project input | Validate project requirements before pipeline run | `validate_project_input` | agents-server | Validation Panel (Pipeline Runs page) | `PipelineService.validate_input()` | `ValidationResult` | F-001 |

### I-020 to I-028: Agent Operations

| ID | Interaction | Description | MCP Tool | MCP Server | Dashboard Screen | Shared Service | Data Shape(s) | Features |
|------|-------------|-------------|----------|------------|-----------------|----------------|---------------|----------|
| I-020 | List agents | View all 48 agents with status, phase, and archetype | `list_agents` | agents-server | Agent Grid (Fleet Health page) | `AgentService.list_agents()` | `AgentSummary[]` | F-008 |
| I-021 | Get agent detail | View single agent config, metrics, and prompt preview | `get_agent` | agents-server | Agent Detail Card (Fleet Health page) | `AgentService.get_agent()` | `AgentDetail` | F-009 |
| I-022 | Invoke agent | Run an agent directly outside a pipeline context | `invoke_agent` | agents-server | -- (MCP-only) | `AgentService.invoke()` | `AgentInvocationResult` | F-010 |
| I-023 | Check agent health | Ping agent health and get response time | `check_agent_health` | agents-server | Health Badge (Fleet Health page) | `AgentService.health_check()` | `AgentHealth` | F-011 |
| I-024 | Promote agent version | Move canary version to active production | `promote_agent_version` | agents-server | Promote Button (Fleet Health page) | `AgentService.promote_version()` | `AgentVersion` | F-012 |
| I-025 | Rollback agent version | Revert to previous known-good version | `rollback_agent_version` | agents-server | Rollback Button (Fleet Health page) | `AgentService.rollback_version()` | `AgentVersion` | F-012 |
| I-026 | Set canary traffic | Adjust canary traffic split percentage | `set_canary_traffic` | agents-server | Canary Slider (Fleet Health page) | `AgentService.set_canary()` | `AgentVersion` | F-012 |
| I-027 | Get agent maturity | View maturity level and promotion eligibility | `get_agent_maturity` | agents-server | Maturity Badge (Fleet Health page) | `AgentService.get_maturity()` | `AgentMaturity` | F-013 |

### I-040 to I-049: Governance Operations (Cost, Audit, Approval)

| ID | Interaction | Description | MCP Tool | MCP Server | Dashboard Screen | Shared Service | Data Shape(s) | Features |
|------|-------------|-------------|----------|------------|-----------------|----------------|---------------|----------|
| I-040 | Get cost report | Cost breakdown by scope (fleet/project/agent) and period | `get_cost_report` | governance-server | Cost Charts (Cost Monitor page) | `CostService.get_report()` | `CostReport` | F-014 |
| I-041 | Check budget | Remaining budget at fleet, project, or agent level | `check_budget` | governance-server | Budget Gauges (Cost Monitor page) | `CostService.check_budget()` | `BudgetStatus` | F-015, F-016 |
| I-042 | Query audit events | Search and filter the audit trail by agent, severity, date | `query_audit_events` | governance-server | Event Table (Audit Log page) | `AuditService.query_events()` | `AuditEvent[]` | F-019 |
| I-043 | Get audit summary | Aggregated audit statistics for a time period | `get_audit_summary` | governance-server | Summary Cards (Audit Log page) | `AuditService.get_summary()` | `AuditSummary` | F-020 |
| I-044 | Export audit report | Generate and download audit report as PDF or CSV | `export_audit_report` | governance-server | Export Button (Audit Log page) | `AuditService.export_report()` | `AuditReport` | F-021 |
| I-045 | List pending approvals | View all approval requests awaiting decision | `list_pending_approvals` | governance-server | Approval Queue Table (Approval Queue page) | `ApprovalService.list_pending()` | `ApprovalRequest[]` | F-024 |
| I-046 | Approve gate | Approve a pipeline gate to allow continuation | `approve_gate` | governance-server | Approve Button (Approval Queue page) | `ApprovalService.approve()` | `ApprovalResult` | F-025 |
| I-047 | Reject gate | Reject a pipeline gate with mandatory comment | `reject_gate` | governance-server | Reject Button + Comment Field (Approval Queue page) | `ApprovalService.reject()` | `ApprovalResult` | F-026 |
| I-048 | Get cost anomalies | View cost spikes, runaway agents, and budget anomalies | `get_cost_anomalies` | governance-server | Anomaly Alerts (Cost Monitor page) | `CostService.get_anomalies()` | `CostAnomaly[]` | F-017 |
| I-049 | Set budget threshold | Configure budget limits and alert thresholds | `set_budget_threshold` | governance-server | Budget Settings (Cost Monitor page) | `CostService.set_threshold()` | `BudgetStatus` | F-016, F-018 |

### I-060 to I-064: Knowledge Operations

| ID | Interaction | Description | MCP Tool | MCP Server | Dashboard Screen | Shared Service | Data Shape(s) | Features |
|------|-------------|-------------|----------|------------|-----------------|----------------|---------------|----------|
| I-060 | Search exceptions | Find knowledge exceptions by keyword or rule pattern | `search_exceptions` | knowledge-server | -- (MCP/REST only) | `KnowledgeService.search()` | `KnowledgeException[]` | F-029 |
| I-061 | Create exception | Add a new exception rule at client tier | `create_exception` | knowledge-server | -- (MCP/REST only) | `KnowledgeService.create()` | `KnowledgeException` | F-030 |
| I-062 | Promote exception | Promote exception from client to stack to universal tier | `promote_exception` | knowledge-server | -- (MCP/REST only) | `KnowledgeService.promote()` | `KnowledgeException` | F-031 |
| I-063 | List exceptions by tier | View all exceptions filtered by tier level | `list_exceptions` | knowledge-server | -- (MCP/REST only; future Dashboard) | `KnowledgeService.list_by_tier()` | `KnowledgeException[]` | F-032, F-033 |

### I-080 to I-084: System and Health Operations

| ID | Interaction | Description | MCP Tool | MCP Server | Dashboard Screen | Shared Service | Data Shape(s) | Features |
|------|-------------|-------------|----------|------------|-----------------|----------------|---------------|----------|
| I-080 | Get fleet health | Overall platform health: agent counts, circuit breakers, avg latency | `get_fleet_health` | agents-server | Health Overview (Fleet Health page) | `HealthService.get_fleet_health()` | `FleetHealth` | F-040, F-041 |
| I-081 | Get MCP server status | MCP server uptime, tool count, and connection metrics | `get_mcp_status` | agents-server | MCP Panel (Fleet Health page) | `HealthService.get_mcp_status()` | `McpServerStatus[]` | F-045, F-034 |
| I-082 | List recent MCP calls | Recent tool invocations by AI clients for observability | `list_recent_mcp_calls` | governance-server | MCP Call Feed (Fleet Health page) | `AuditService.list_mcp_calls()` | `McpCallEvent[]` | F-045, F-022 |
| I-083 | Check LLM provider status | Verify LLM provider health: reachability, latency, model availability | `check_provider_health` | agents-server | Fleet Health page (provider status panel) | `HealthService.check_provider_health()` | `ProviderStatus` | F-057, F-058 |
| I-084 | Switch agent provider | Change an agent's LLM provider override at runtime | `set_agent_provider` | agents-server | Agent Detail panel (provider selector) | `AgentService.set_provider()` | `AgentDetail` | F-057 |

### Interaction Count Summary

| Domain | ID Range | Count |
|--------|----------|-------|
| Pipeline Operations | I-001 to I-009 | 9 |
| Agent Operations | I-020 to I-027 | 8 |
| Governance (Cost, Audit, Approval) | I-040 to I-049 | 10 |
| Knowledge Operations | I-060 to I-063 | 4 |
| System / Health | I-080 to I-084 | 5 |
| **Total** | | **36** |

### Feature Coverage Cross-Reference

Every feature (F-001 to F-056) from FEATURE-CATALOG must be traceable to at least one interaction. Features in infrastructure epics (E-007 MCP Server Infrastructure, E-008 Dashboard UI, E-009 Quality, E-010 Platform Foundation) are cross-cutting and are covered implicitly by the interactions above or by platform-level concerns below.

| Feature Range | Epic | Covered By |
|---|---|---|
| F-001 to F-007 | E-001: Pipeline Execution | I-001 to I-009 |
| F-008 to F-013 | E-002: Agent Management | I-020 to I-027 |
| F-014 to F-018 | E-003: Cost & Budget | I-040, I-041, I-048, I-049 |
| F-019 to F-022 | E-004: Audit & Compliance | I-042, I-043, I-044, I-082 |
| F-023 to F-028 | E-005: Human Approval Gates | I-045, I-046, I-047 (F-023 gate creation is implicit in I-001 pipeline trigger; F-027/F-028 escalation/SLA are sub-behaviors of I-045) |
| F-029 to F-033 | E-006: Knowledge Management | I-060 to I-063 |
| F-034 to F-039 | E-007: MCP Server Infrastructure | I-081 (server status); F-034 to F-039 are infrastructure capabilities consumed by all MCP interactions |
| F-040 to F-045 | E-008: Dashboard / Operator UI | I-080, I-081, I-082 (dashboard pages); F-040 to F-044 are rendered by Dashboard screens mapped in interaction inventory |
| F-046 to F-049 | E-009: Quality & Testing | Cross-cutting; quality metrics surface through I-006 (document quality_score), I-027 (maturity confidence) |
| F-050 to F-058 | E-010: Platform Foundation | Cross-cutting; session management (F-050), config (F-051), logging (F-052), secrets (F-053), rate limiting (F-054), feature flags (F-055), health checks (F-056), LLM provider selection (F-057, I-083, I-084), provider health (F-058, I-083) are infrastructure consumed by all services |

---

## 2. Data Shape Definitions

All data shapes are defined as TypeScript-style interfaces for precision. Every MCP tool response and every Dashboard render MUST use these exact shapes. Service methods return these shapes directly -- no transformation in handlers.

### 2.1 PipelineRun

```typescript
interface PipelineRun {
  run_id: string;                // UUID v4
  project_id: string;            // UUID v4
  pipeline_name: string;         // e.g., "full-stack-first-24-doc"
  status: PipelineStatus;        // "pending" | "running" | "paused" | "completed" | "failed" | "cancelled"
  current_step: number;          // 0-indexed step currently executing
  total_steps: number;           // total steps in pipeline (e.g., 24)
  current_step_name: string;     // e.g., "07-INTERACTION-MAP"
  started_at: string;            // ISO 8601 timestamp
  completed_at: string | null;   // ISO 8601 timestamp, null if not complete
  cost_usd: number;              // cumulative cost so far
  triggered_by: string;          // persona or system identifier
  error_message: string | null;  // null if no error
  checkpoint_step: number | null;// last successful step for resume
}

type PipelineStatus = "pending" | "running" | "paused" | "completed" | "failed" | "cancelled";
```

**Produced by:** I-001 (trigger), I-002 (status), I-004 (resume), I-005 (cancel), I-007 (retry)
**Consumed by:** Pipeline Runs Table, Pipeline Status Card, MCP `get_pipeline_status` response
**Service methods:** `PipelineService.trigger()`, `.get_status()`, `.resume()`, `.cancel()`, `.retry_step()`

### 2.2 PipelineDocument

```typescript
interface PipelineDocument {
  document_id: string;           // UUID v4
  run_id: string;                // references PipelineRun.run_id
  doc_number: number;            // 0-23 in the sequence
  doc_name: string;              // e.g., "INTERACTION-MAP"
  doc_type: string;              // e.g., "markdown"
  content: string;               // full document content (may be truncated in list views)
  generated_at: string;          // ISO 8601 timestamp
  quality_score: number | null;  // 0.0 to 1.0, null if not yet scored
  token_count: number;           // tokens consumed generating this document
  agent_id: string;              // agent that generated this document
}
```

**Produced by:** I-006 (get documents)
**Consumed by:** Document Viewer (Pipeline Runs page), MCP `get_pipeline_documents` response
**Service methods:** `PipelineService.get_documents()`

### 2.3 PipelineConfig

```typescript
interface PipelineConfig {
  pipeline_name: string;         // e.g., "full-stack-first-24-doc"
  approach: string;              // "full-stack-first" | "api-first" | "design-first" | "mcp-first"
  steps: PipelineStep[];         // ordered list of steps
  default_timeout_seconds: number;
  approval_gates: string[];      // step names requiring approval
}

interface PipelineStep {
  step_number: number;
  step_name: string;
  agent_id: string;
  timeout_seconds: number;
  requires_approval: boolean;
  depends_on: number[];          // step_numbers this step depends on
}
```

**Produced by:** I-008 (get config)
**Consumed by:** Config Panel (Pipeline Runs page), MCP `get_pipeline_config` response
**Service methods:** `PipelineService.get_config()`

### 2.4 ValidationResult

```typescript
interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  project_id: string | null;     // assigned project_id if valid
}

interface ValidationError {
  field: string;
  message: string;
  code: string;
}

interface ValidationWarning {
  field: string;
  message: string;
  suggestion: string;
}
```

**Produced by:** I-009 (validate input)
**Consumed by:** Validation Panel (Pipeline Runs page), MCP `validate_project_input` response
**Service methods:** `PipelineService.validate_input()`

### 2.5 AgentSummary

```typescript
interface AgentSummary {
  agent_id: string;              // e.g., "agent-prd-writer"
  name: string;                  // human-readable name
  phase: string;                 // "plan" | "design" | "build" | "verify" | "deploy"
  archetype: string;             // "writer" | "reviewer" | "orchestrator" | "validator"
  status: AgentStatus;           // "active" | "degraded" | "offline" | "canary"
  active_version: string;        // semver, e.g., "1.2.0"
  cost_today_usd: number;        // cost incurred today
  last_invocation_at: string | null; // ISO 8601, null if never invoked
  invocation_count_today: number;
}

type AgentStatus = "active" | "degraded" | "offline" | "canary";
```

**Produced by:** I-020 (list agents)
**Consumed by:** Agent Grid (Fleet Health page), MCP `list_agents` response
**Service methods:** `AgentService.list_agents()`

### 2.6 AgentDetail

```typescript
interface AgentDetail extends AgentSummary {
  manifest: object;              // full agent manifest (YAML parsed to JSON)
  prompt_preview: string;        // first 500 chars of system prompt
  maturity: AgentMaturity;       // nested maturity info
  canary_version: string | null; // null if no canary deployed
  canary_traffic_pct: number;    // 0-100, 0 if no canary
  health: AgentHealth;           // nested health info
  model: string;                 // e.g., "claude-opus-4-6"
  max_tokens: number;
  temperature: number;
  tools: string[];               // list of tool names the agent can invoke
}
```

**Produced by:** I-021 (get agent)
**Consumed by:** Agent Detail Card (Fleet Health page), MCP `get_agent` response
**Service methods:** `AgentService.get_agent()`

### 2.7 AgentHealth

```typescript
interface AgentHealth {
  agent_id: string;
  healthy: boolean;
  last_check_at: string;         // ISO 8601
  response_time_ms: number;
  error_message: string | null;  // null if healthy
  consecutive_failures: number;
  circuit_breaker_open: boolean;
}
```

**Produced by:** I-023 (check health)
**Consumed by:** Health Badge (Fleet Health page), MCP `check_agent_health` response, nested in `AgentDetail`
**Service methods:** `AgentService.health_check()`

### 2.8 AgentVersion

```typescript
interface AgentVersion {
  agent_id: string;
  active_version: string;        // semver
  canary_version: string | null;
  canary_traffic_pct: number;    // 0-100
  previous_version: string | null;
  promoted_at: string | null;    // ISO 8601
  rolled_back_at: string | null; // ISO 8601
}
```

**Produced by:** I-024 (promote), I-025 (rollback), I-026 (set canary)
**Consumed by:** Promote/Rollback Buttons, Canary Slider (Fleet Health page), MCP tool responses
**Service methods:** `AgentService.promote_version()`, `.rollback_version()`, `.set_canary()`

### 2.9 AgentMaturity

```typescript
interface AgentMaturity {
  agent_id: string;
  current_level: MaturityLevel;  // "supervised" | "assisted" | "autonomous" | "fully_autonomous"
  override_rate: number;         // 0.0 to 1.0, percentage of outputs overridden by humans
  confidence_avg: number;        // 0.0 to 1.0, average confidence score
  consecutive_days: number;      // days at current performance threshold
  next_level: MaturityLevel | null; // null if at max level
  promotion_eligible: boolean;   // true if meets threshold for next level
  promotion_criteria: string;    // human-readable criteria description
}

type MaturityLevel = "supervised" | "assisted" | "autonomous" | "fully_autonomous";
```

**Produced by:** I-027 (get maturity)
**Consumed by:** Maturity Badge (Fleet Health page), MCP `get_agent_maturity` response, nested in `AgentDetail`
**Service methods:** `AgentService.get_maturity()`

### 2.10 AgentInvocationResult

```typescript
interface AgentInvocationResult {
  invocation_id: string;         // UUID v4
  agent_id: string;
  mode: string;                  // "direct" | "pipeline"
  status: "success" | "failure" | "timeout";
  confidence: number;            // 0.0 to 1.0
  output: string;                // agent output content
  cost_usd: number;
  duration_ms: number;
  tokens_in: number;
  tokens_out: number;
  model: string;                 // model used for this invocation
  error_message: string | null;
}
```

**Produced by:** I-022 (invoke agent)
**Consumed by:** MCP `invoke_agent` response only (no Dashboard screen)
**Service methods:** `AgentService.invoke()`

### 2.11 CostReport

```typescript
interface CostReport {
  scope: CostScope;             // "fleet" | "project" | "agent"
  entity_id: string | null;     // null for fleet scope
  period_days: number;          // 1, 7, 30, 90
  total_usd: number;
  breakdown: CostBreakdownItem[];
  generated_at: string;          // ISO 8601
  trend_pct: number;            // % change vs previous period, positive = increase
}

interface CostBreakdownItem {
  entity_id: string;
  entity_name: string;
  cost_usd: number;
  invocation_count: number;
  avg_cost_per_invocation: number;
  tokens_total: number;
}

type CostScope = "fleet" | "project" | "agent";
```

**Produced by:** I-040 (get cost report)
**Consumed by:** Cost Charts (Cost Monitor page), MCP `get_cost_report` response
**Service methods:** `CostService.get_report()`

### 2.12 BudgetStatus

```typescript
interface BudgetStatus {
  scope: CostScope;
  entity_id: string;
  budget_usd: number;
  spent_usd: number;
  remaining_usd: number;
  utilization_pct: number;       // 0-100
  at_risk: boolean;              // true if utilization > 80%
  alert_threshold_pct: number;   // configured alert threshold
  projected_overrun_date: string | null; // ISO 8601, null if within budget
}
```

**Produced by:** I-041 (check budget), I-049 (set threshold)
**Consumed by:** Budget Gauges (Cost Monitor page), MCP `check_budget` / `set_budget_threshold` response
**Service methods:** `CostService.check_budget()`, `.set_threshold()`

### 2.13 CostAnomaly

```typescript
interface CostAnomaly {
  anomaly_id: string;            // UUID v4
  entity_id: string;
  entity_type: "agent" | "project" | "pipeline";
  entity_name: string;
  expected_usd: number;          // predicted cost based on historical pattern
  actual_usd: number;
  deviation_pct: number;         // percentage above expected
  detected_at: string;           // ISO 8601
  severity: "low" | "medium" | "high" | "critical";
  acknowledged: boolean;
  acknowledged_by: string | null;
}
```

**Produced by:** I-048 (get cost anomalies)
**Consumed by:** Anomaly Alerts (Cost Monitor page), MCP `get_cost_anomalies` response
**Service methods:** `CostService.get_anomalies()`

### 2.14 AuditEvent

```typescript
interface AuditEvent {
  event_id: string;              // UUID v4
  timestamp: string;             // ISO 8601
  agent_id: string | null;       // null for system events
  session_id: string;
  project_id: string | null;
  action: string;                // e.g., "pipeline.trigger", "agent.invoke", "approval.approve"
  severity: AuditSeverity;
  details: object;               // action-specific payload
  cost_usd: number;
  tokens_in: number;
  tokens_out: number;
  duration_ms: number;
  pii_detected: boolean;
  source_ip: string | null;
  user_id: string | null;
}

type AuditSeverity = "info" | "warning" | "error" | "critical";
```

**Produced by:** I-042 (query audit events)
**Consumed by:** Event Table (Audit Log page), MCP `query_audit_events` response
**Service methods:** `AuditService.query_events()`

### 2.15 AuditSummary

```typescript
interface AuditSummary {
  period: string;                // e.g., "2026-03-24T00:00:00Z/2026-03-24T23:59:59Z"
  total_events: number;
  by_severity: Record<AuditSeverity, number>;  // {"info": 120, "warning": 15, ...}
  by_agent: Record<string, number>;             // {"agent-prd-writer": 45, ...}
  by_project: Record<string, number>;
  by_action: Record<string, number>;
  total_cost_usd: number;
  pii_detections: number;
}
```

**Produced by:** I-043 (get audit summary)
**Consumed by:** Summary Cards (Audit Log page), MCP `get_audit_summary` response
**Service methods:** `AuditService.get_summary()`

### 2.16 AuditReport

```typescript
interface AuditReport {
  report_id: string;             // UUID v4
  format: "pdf" | "csv" | "json";
  period: string;                // ISO 8601 interval
  filters_applied: object;       // filters used to generate
  generated_at: string;          // ISO 8601
  download_url: string;          // presigned URL, expires in 1 hour
  size_bytes: number;
  record_count: number;
}
```

**Produced by:** I-044 (export audit report)
**Consumed by:** Export Button result (Audit Log page), MCP `export_audit_report` response
**Service methods:** `AuditService.export_report()`

### 2.17 ApprovalRequest

```typescript
interface ApprovalRequest {
  approval_id: string;           // UUID v4
  session_id: string;
  run_id: string;                // references PipelineRun.run_id
  pipeline_name: string;
  step_number: number;
  step_name: string;
  summary: string;               // human-readable description of what needs approval
  risk_level: "low" | "medium" | "high" | "critical";
  status: ApprovalStatus;
  requested_at: string;          // ISO 8601
  expires_at: string;            // ISO 8601
  decided_at: string | null;
  decision_by: string | null;    // user who approved/rejected
  decision_comment: string | null;
  context: object;               // step-specific context for reviewer
}

type ApprovalStatus = "pending" | "approved" | "rejected" | "expired" | "escalated";
```

**Produced by:** I-045 (list pending)
**Consumed by:** Approval Queue Table (Approval Queue page), MCP `list_pending_approvals` response
**Service methods:** `ApprovalService.list_pending()`

### 2.18 ApprovalResult

```typescript
interface ApprovalResult {
  approval_id: string;
  status: "approved" | "rejected";
  decided_at: string;            // ISO 8601
  decision_by: string;
  decision_comment: string | null; // required for rejection
  pipeline_resumed: boolean;     // true if pipeline auto-resumed after approval
}
```

**Produced by:** I-046 (approve), I-047 (reject)
**Consumed by:** Approval Queue confirmation (Approval Queue page), MCP `approve_gate` / `reject_gate` response
**Service methods:** `ApprovalService.approve()`, `.reject()`

### 2.19 KnowledgeException

```typescript
interface KnowledgeException {
  exception_id: string;          // UUID v4
  title: string;                 // human-readable title
  rule: string;                  // the exception rule pattern/expression
  description: string;           // detailed explanation
  severity: "low" | "medium" | "high" | "critical";
  tier: KnowledgeTier;
  stack_name: string | null;     // null for universal tier
  client_id: string | null;      // null for stack and universal tiers
  active: boolean;
  fire_count: number;            // times this exception has been matched
  last_fired_at: string | null;  // ISO 8601, null if never fired
  created_at: string;            // ISO 8601
  created_by: string;
  tags: string[];
}

type KnowledgeTier = "client" | "stack" | "universal";
```

**Produced by:** I-060 (search), I-061 (create), I-062 (promote), I-063 (list by tier)
**Consumed by:** MCP tool responses (no Dashboard screen currently)
**Service methods:** `KnowledgeService.search()`, `.create()`, `.promote()`, `.list_by_tier()`

### 2.20 FleetHealth

```typescript
interface FleetHealth {
  healthy_agents: number;
  total_agents: number;
  by_phase: Record<string, { total: number; healthy: number }>;
  by_status: Record<AgentStatus, number>;
  circuit_breakers_open: number;
  avg_response_ms: number;
  p95_response_ms: number;
  fleet_cost_today_usd: number;
  active_pipelines: number;
  pending_approvals: number;
  last_updated_at: string;       // ISO 8601
}
```

**Produced by:** I-080 (get fleet health)
**Consumed by:** Health Overview (Fleet Health page), MCP `get_fleet_health` response
**Service methods:** `HealthService.get_fleet_health()`

### 2.21 McpServerStatus

```typescript
interface McpServerStatus {
  server_name: string;           // "agents-server" | "governance-server" | "knowledge-server"
  healthy: boolean;
  uptime_seconds: number;
  tool_count: number;            // number of tools registered
  active_connections: number;    // current WebSocket/SSE connections
  requests_per_minute: number;   // rolling 5-minute average
  error_rate_pct: number;        // rolling 5-minute error rate
  version: string;               // server version
  last_restart_at: string;       // ISO 8601
}
```

**Produced by:** I-081 (get MCP status)
**Consumed by:** MCP Panel (Fleet Health page), MCP `get_mcp_status` response
**Service methods:** `HealthService.get_mcp_status()`

### 2.22 McpCallEvent

```typescript
interface McpCallEvent {
  call_id: string;               // UUID v4
  timestamp: string;             // ISO 8601
  server_name: string;
  tool_name: string;             // e.g., "trigger_pipeline"
  caller: string;                // AI client identifier or user
  project_id: string | null;
  duration_ms: number;
  status: "success" | "error" | "timeout";
  error_message: string | null;
  tokens_used: number;
  cost_usd: number;
}
```

**Produced by:** I-082 (list recent MCP calls)
**Consumed by:** MCP Call Feed (Fleet Health page), MCP `list_recent_mcp_calls` response
**Service methods:** `AuditService.list_mcp_calls()`

### 2.23 ProviderStatus

```typescript
interface ProviderStatus {
  provider_name: string;         // "anthropic" | "openai" | "ollama"
  healthy: boolean;
  model_count: number;           // number of models available at this provider
  default_tier: string;          // "fast" | "balanced" | "powerful"
  latency_ms: number;            // last health check round-trip latency
  tier_map: Record<string, string>;  // e.g., { "fast": "claude-haiku", "balanced": "claude-sonnet", "powerful": "claude-opus" }
  cost_per_1k_input: number;     // USD per 1K input tokens (0.00 for Ollama)
  cost_per_1k_output: number;    // USD per 1K output tokens (0.00 for Ollama)
  last_checked_at: string;       // ISO 8601
}
```

**Produced by:** I-083 (check LLM provider status)
**Consumed by:** Fleet Health page (provider status panel), MCP `check_provider_health` response
**Service methods:** `HealthService.check_provider_health()`

---

## 3. Cross-Interface Journeys

These journeys describe real multi-step workflows where users move between MCP and Dashboard interfaces. Each step references a specific interaction ID and data shape.

### Journey 1: Pipeline with Approval Gate (Flagship Cross-Interface Journey)

**Personas:** Priya (Platform Eng, MCP primary), Anika (Eng Lead, Dashboard primary)
**Trigger:** Developer needs to generate documentation suite for a new project.

| Step | Persona | Interface | Action | Interaction ID | Data Shape | Notes |
|------|---------|-----------|--------|---------------|------------|-------|
| 1 | Priya | MCP | Validates project requirements | I-009 | `ValidationResult` | Ensures input is well-formed before committing resources |
| 2 | Priya | MCP | Triggers full-stack-first pipeline | I-001 | `PipelineRun` | Returns `run_id`, status = "running" |
| 3 | Priya | MCP | Checks pipeline status periodically | I-002 | `PipelineRun` | Watches `current_step` advance, cost accumulate |
| 4 | System | -- | Pipeline hits approval gate at step 6 | -- | -- | Pipeline status changes to "paused", `ApprovalRequest` created |
| 5 | Anika | Dashboard | Opens Approval Queue page, sees pending approval | I-045 | `ApprovalRequest[]` | Filters by status = "pending", sees risk_level and summary |
| 6 | Anika | Dashboard | Reviews context and approves the gate | I-046 | `ApprovalResult` | Adds comment, `pipeline_resumed` = true |
| 7 | System | -- | Pipeline resumes automatically | -- | `PipelineRun` | Status changes back to "running" |
| 8 | Priya | MCP | Checks pipeline status, sees completion | I-002 | `PipelineRun` | Status = "completed", all 24 docs generated |
| 9 | Priya | MCP | Retrieves generated documents | I-006 | `PipelineDocument[]` | Reviews quality_score for each document |

**Key handoff:** Step 4 to Step 5 is the cross-interface moment. The pipeline pause creates an `ApprovalRequest` that surfaces on Anika's Dashboard. No manual notification is needed -- the Dashboard polls `ApprovalService.list_pending()` every 30 seconds.

### Journey 2: Cost Spike Investigation

**Personas:** David (DevOps, Dashboard primary), Priya (Platform Eng, MCP primary)
**Trigger:** CostService detects anomalous spending pattern.

| Step | Persona | Interface | Action | Interaction ID | Data Shape | Notes |
|------|---------|-----------|--------|---------------|------------|-------|
| 1 | System | -- | Cost anomaly detected by background job | -- | `CostAnomaly` | Severity = "high", Slack alert sent |
| 2 | David | Dashboard | Opens Cost Monitor page, views anomaly alerts | I-048 | `CostAnomaly[]` | Sees deviation_pct and severity for each anomaly |
| 3 | David | Dashboard | Drills into fleet cost report | I-040 | `CostReport` | Scope = "fleet", identifies expensive entity in breakdown |
| 4 | David | Dashboard | Checks budget status for the affected project | I-041 | `BudgetStatus` | Sees utilization_pct > 90%, at_risk = true |
| 5 | David | Dashboard | Checks fleet health to see if agent is degraded | I-080 | `FleetHealth` | Confirms circuit_breakers_open > 0 |
| 6 | Priya | MCP | Gets agent detail for runaway agent | I-021 | `AgentDetail` | Confirms high invocation count and cost |
| 7 | Priya | MCP | Checks agent health | I-023 | `AgentHealth` | May show degraded status or high response times |
| 8 | Priya | MCP | Sets budget threshold to prevent further overrun | I-049 | `BudgetStatus` | Configures lower alert_threshold_pct |

**Key handoff:** Step 5 to Step 6 is the cross-interface moment. David identifies the problem on Dashboard, escalates to Priya who acts via MCP.

### Journey 3: Agent Canary Deployment

**Personas:** Priya (Platform Eng, MCP primary), Jason (Tech Lead, both interfaces)
**Trigger:** New agent version ready for canary testing.

| Step | Persona | Interface | Action | Interaction ID | Data Shape | Notes |
|------|---------|-----------|--------|---------------|------------|-------|
| 1 | Priya | MCP | Sets canary traffic to 10% | I-026 | `AgentVersion` | canary_traffic_pct = 10, canary_version set |
| 2 | Jason | Dashboard | Monitors Fleet Health page for canary agent | I-020 | `AgentSummary[]` | Filters by status = "canary" |
| 3 | Jason | Dashboard | Checks fleet health metrics | I-080 | `FleetHealth` | Watches avg_response_ms, compares before/after |
| 4 | Priya | MCP | Increases canary traffic to 50% | I-026 | `AgentVersion` | canary_traffic_pct = 50 |
| 5 | Jason | Dashboard | Reviews agent detail with expanded canary metrics | I-021 | `AgentDetail` | Checks health, maturity, error rates |
| 6 | Priya | MCP | Gets agent maturity for canary confidence | I-027 | `AgentMaturity` | Confirms confidence_avg is acceptable |
| 7 | Priya | MCP | Promotes canary to active | I-024 | `AgentVersion` | canary_version becomes active_version |

**Key handoff:** Priya acts via MCP (steps 1, 4, 6, 7), Jason monitors via Dashboard (steps 2, 3, 5). The same `AgentVersion` and `AgentDetail` shapes ensure both see consistent data.

### Journey 4: Compliance Audit

**Personas:** Fatima (Compliance Officer, Dashboard primary), Anika (Eng Lead, Dashboard primary)
**Trigger:** Quarterly compliance review requires audit trail examination.

| Step | Persona | Interface | Action | Interaction ID | Data Shape | Notes |
|------|---------|-----------|--------|---------------|------------|-------|
| 1 | Fatima | Dashboard | Opens Audit Log page, views summary cards | I-043 | `AuditSummary` | Reviews total_events, pii_detections, by_severity |
| 2 | Fatima | Dashboard | Queries audit events filtered by severity = "error" + "critical" | I-042 | `AuditEvent[]` | Filters by date range, severity, reviews details |
| 3 | Fatima | Dashboard | Exports audit report as PDF | I-044 | `AuditReport` | Downloads via download_url for compliance records |
| 4 | Fatima | Dashboard | Reviews MCP call history for unusual patterns | I-082 | `McpCallEvent[]` | Checks for unauthorized tool usage or anomalous callers |
| 5 | Anika | Dashboard | Opens Approval Queue to review past decisions | I-045 | `ApprovalRequest[]` | Filters by status != "pending" to see historical decisions |
| 6 | Anika | Dashboard | Cross-references approval decisions with audit events | I-042 | `AuditEvent[]` | Filters by action = "approval.approve" or "approval.reject" |

**Key handoff:** This journey stays within Dashboard but crosses personas. Fatima flags issues in steps 1-4, Anika investigates approval patterns in steps 5-6. Both use the same `AuditEvent` shape, ensuring consistency.

---

## 4. Naming Conventions

### 4.1 Verb Table (CRUD+ Canonical Verbs)

All interactions follow this verb vocabulary. MCP tools use `verb_noun` (snake_case). Dashboard labels use `Verb Noun` (Title Case). Data shapes use `PascalCase`.

| Canonical Verb | MCP Tool Prefix | REST Method | Dashboard Label | Description |
|---------------|-----------------|-------------|-----------------|-------------|
| `trigger` | `trigger_` | POST | Trigger | Initiate a process (pipelines only) |
| `get` | `get_` | GET | View / Get | Retrieve a single resource |
| `list` | `list_` | GET | View All / List | Retrieve multiple resources with optional filters |
| `create` | `create_` | POST | Create / Add | Create a new resource |
| `resume` | `resume_` | POST | Resume | Continue a paused process |
| `cancel` | `cancel_` | POST | Cancel | Stop a running process |
| `retry` | `retry_` | POST | Retry | Re-attempt a failed operation |
| `check` | `check_` | GET | Check | Verify status or health |
| `approve` | `approve_` | POST | Approve | Grant approval for a gate |
| `reject` | `reject_` | POST | Reject | Deny approval for a gate |
| `promote` | `promote_` | POST | Promote | Elevate version or tier |
| `rollback` | `rollback_` | POST | Rollback | Revert to previous version |
| `set` | `set_` | PUT | Set / Configure | Update a configuration value |
| `search` | `search_` | GET | Search | Full-text or filtered search |
| `export` | `export_` | POST | Export / Download | Generate downloadable artifact |
| `validate` | `validate_` | POST | Validate | Check input correctness |
| `invoke` | `invoke_` | POST | -- | Direct agent execution (MCP-only) |

### 4.2 Noun Table

| Canonical Noun | MCP Tool Suffix | Dashboard Label | Data Shape |
|---------------|-----------------|-----------------|------------|
| `pipeline` | `_pipeline` | Pipeline | `PipelineRun` |
| `pipeline_runs` | `_pipeline_runs` | Pipeline Runs | `PipelineRun[]` |
| `pipeline_documents` | `_pipeline_documents` | Documents | `PipelineDocument[]` |
| `pipeline_step` | `_pipeline_step` | Step | (part of `PipelineRun`) |
| `pipeline_config` | `_pipeline_config` | Configuration | `PipelineConfig` |
| `agent` / `agents` | `_agent` / `_agents` | Agent(s) | `AgentSummary` / `AgentDetail` |
| `agent_health` | `_agent_health` | Health | `AgentHealth` |
| `agent_version` | `_agent_version` | Version | `AgentVersion` |
| `agent_maturity` | `_agent_maturity` | Maturity | `AgentMaturity` |
| `cost_report` | `_cost_report` | Cost Report | `CostReport` |
| `budget` | `_budget` | Budget | `BudgetStatus` |
| `cost_anomalies` | `_cost_anomalies` | Anomalies | `CostAnomaly[]` |
| `audit_events` | `_audit_events` | Audit Events | `AuditEvent[]` |
| `audit_summary` | `_audit_summary` | Audit Summary | `AuditSummary` |
| `audit_report` | `_audit_report` | Audit Report | `AuditReport` |
| `pending_approvals` | `_pending_approvals` | Approvals | `ApprovalRequest[]` |
| `gate` | `_gate` | Gate | `ApprovalResult` |
| `exceptions` | `_exceptions` | Exceptions | `KnowledgeException[]` |
| `fleet_health` | `_fleet_health` | Fleet Health | `FleetHealth` |
| `mcp_status` | `_mcp_status` | MCP Status | `McpServerStatus[]` |
| `mcp_calls` | `_recent_mcp_calls` | MCP Calls | `McpCallEvent[]` |

### 4.3 Interface-Specific Conventions

| Convention | MCP Tools | REST Endpoints | Dashboard Widgets | Data Shapes |
|-----------|-----------|----------------|-------------------|-------------|
| **Case** | snake_case | snake_case (URL path) | Title Case | PascalCase |
| **Example** | `get_pipeline_status` | `/api/v1/pipelines/{id}/status` | Pipeline Status Card | `PipelineRun` |
| **Plurals** | Plural for list, singular for get | Plural in path, singular in body | Context-dependent | Append `[]` for arrays |
| **Prefixes** | verb_noun | /api/v1/{noun} | {Noun} {Widget} | None |

---

## 5. Parity Matrix

This matrix ensures compliance with Q-049 (MCP-REST parity) and Q-051 (data shape parity). Every interaction must have both MCP and REST coverage. Dashboard coverage is optional for MCP-primary interactions.

| ID | Interaction | MCP | REST | Dashboard | Justification for Gaps |
|------|-------------|-----|------|-----------|----------------------|
| I-001 | Trigger pipeline | Yes | Yes | Yes | -- |
| I-002 | Get pipeline status | Yes | Yes | Yes | -- |
| I-003 | List pipeline runs | Yes | Yes | Yes | -- |
| I-004 | Resume pipeline | Yes | Yes | Yes | -- |
| I-005 | Cancel pipeline | Yes | Yes | Yes | -- |
| I-006 | Get pipeline documents | Yes | Yes | Yes | -- |
| I-007 | Retry pipeline step | Yes | Yes | Yes | -- |
| I-008 | Get pipeline config | Yes | Yes | Yes | -- |
| I-009 | Validate project input | Yes | Yes | Yes | -- |
| I-020 | List agents | Yes | Yes | Yes | -- |
| I-021 | Get agent detail | Yes | Yes | Yes | -- |
| I-022 | Invoke agent | Yes | Yes | **No** | Direct agent invocation is a developer/MCP workflow. Dashboard users trigger agents through pipelines (I-001), not directly. Adding a Dashboard form would create a dangerous shortcut bypassing pipeline governance. |
| I-023 | Check agent health | Yes | Yes | Yes | -- |
| I-024 | Promote agent version | Yes | Yes | Yes | -- |
| I-025 | Rollback agent version | Yes | Yes | Yes | -- |
| I-026 | Set canary traffic | Yes | Yes | Yes | -- |
| I-027 | Get agent maturity | Yes | Yes | Yes | -- |
| I-040 | Get cost report | Yes | Yes | Yes | -- |
| I-041 | Check budget | Yes | Yes | Yes | -- |
| I-042 | Query audit events | Yes | Yes | Yes | -- |
| I-043 | Get audit summary | Yes | Yes | Yes | -- |
| I-044 | Export audit report | Yes | Yes | Yes | -- |
| I-045 | List pending approvals | Yes | Yes | Yes | -- |
| I-046 | Approve gate | Yes | Yes | Yes | -- |
| I-047 | Reject gate | Yes | Yes | Yes | -- |
| I-048 | Get cost anomalies | Yes | Yes | Yes | -- |
| I-049 | Set budget threshold | Yes | Yes | Yes | -- |
| I-060 | Search exceptions | Yes | Yes | **No** | Knowledge exceptions are used by agents and platform engineers during generation. Dashboard support planned for v2; current users (Priya, Marcus) prefer MCP. |
| I-061 | Create exception | Yes | Yes | **No** | Same as I-060. Exception creation is a developer workflow. |
| I-062 | Promote exception | Yes | Yes | **No** | Same as I-060. Tier promotion requires understanding of exception semantics. |
| I-063 | List exceptions by tier | Yes | Yes | **No** | Same as I-060. Future Dashboard page planned. |
| I-080 | Get fleet health | Yes | Yes | Yes | -- |
| I-081 | Get MCP server status | Yes | Yes | Yes | -- |
| I-082 | List recent MCP calls | Yes | Yes | Yes | -- |
| I-083 | Check LLM provider status | Yes | Yes | Yes | -- |
| I-084 | Switch agent provider | Yes | Yes | Yes | -- |

### Parity Summary

| Metric | Count |
|--------|-------|
| Total interactions | 34 |
| MCP + REST coverage | 34 / 34 (100%) |
| Dashboard coverage | 29 / 34 (85%) |
| Dashboard gaps | 5 (I-022, I-060 to I-063) |
| All gaps justified | Yes |

### Data Shape Parity (Q-051)

Every service method returns the SAME data shape regardless of whether the caller is MCP, REST, or Dashboard. The service layer is the single source of truth:

```
MCP Handler  -->  ServiceMethod()  -->  DataShape
REST Handler -->  ServiceMethod()  -->  DataShape
Dashboard    -->  REST API         -->  DataShape
```

No shape transformation is allowed in MCP handlers or REST handlers. Dashboard reads from REST, which delegates to the same service method.

---

## 6. Interaction ID Guidelines

### 6.1 Format

```
I-{NNN}
```

- **I** prefix is mandatory (distinguishes from F-NNN features, Q-NNN quality requirements, E-NNN epics).
- **NNN** is a zero-padded 3-digit number.
- IDs are assigned in domain-grouped blocks with gaps for future expansion.

### 6.2 Domain Grouping

| Domain | ID Range | Capacity | Used | Available |
|--------|----------|----------|------|-----------|
| Pipeline Operations | I-001 to I-019 | 19 | 9 | 10 |
| Agent Operations | I-020 to I-039 | 20 | 8 | 12 |
| Governance (Cost, Audit, Approval) | I-040 to I-059 | 20 | 10 | 10 |
| Knowledge Operations | I-060 to I-079 | 20 | 4 | 16 |
| System / Health | I-080 to I-099 | 20 | 5 | 15 |

### 6.3 Scope

Each I-NNN represents a **single user intent** that:
- Maps to exactly ONE shared service method call (the primary call; side effects may trigger others)
- Returns exactly ONE data shape (which may be a single object or an array)
- Can be fulfilled by MCP tool, REST endpoint, or Dashboard widget (or any combination)

### 6.4 Granularity Rules

1. **One intent, one interaction.** Do not combine "list and filter" into separate IDs. Filtering is a parameter of the list interaction.
2. **Separate read from write.** `get_pipeline_status` (I-002) is separate from `trigger_pipeline` (I-001) even though both involve pipelines.
3. **Separate approve from reject.** Different business semantics warrant different IDs (I-046 vs I-047), even though both modify the same resource.
4. **Group variants under one ID.** "Get cost report for fleet" and "Get cost report for agent" are the same interaction (I-040) with different `scope` parameter values.

### 6.5 Splitting Rule

Split an existing interaction into two when:
- The service method signatures differ (different input parameters or return types)
- The authorization requirements differ (different roles can perform each)
- The NFR targets differ (one must be faster than the other)

### 6.6 Expected Count

Target range: **25 to 35 interactions**. This platform has 34.

- Fewer than 25 suggests interactions are too coarse (multiple intents crammed into one ID)
- More than 35 suggests interactions are too fine (parameter variations split into separate IDs)

---

## 7. Naming Conflict Resolution

### 7.1 Resolution Rules

**Rule 1: Service method name is canonical.** When MCP tool name and Dashboard label disagree, the shared service method name breaks the tie. Example: if service is `PipelineService.get_status()`, MCP must be `get_pipeline_status` and Dashboard must be "Pipeline Status" -- not "Pipeline Progress" or "Run Status".

**Rule 2: Data shape name wins over display name.** The PascalCase data shape name (e.g., `PipelineRun`) is the authoritative term. Dashboard may display "Pipeline Run" or "Run" but the underlying component prop type must reference `PipelineRun`.

**Rule 3: Interaction ID is the tiebreaker.** If two teams disagree on naming, reference the I-NNN interaction. The name in the Interaction Inventory (Section 1) is authoritative. Changes require a PR to this document.

**Rule 4: No synonyms in code.** If the canonical term is "pipeline", do not use "workflow", "job", or "run" as variable names in code. Use "pipeline" everywhere. The `PipelineRun` shape represents a single execution of a pipeline -- the word "run" in the shape name is part of the compound noun, not a synonym.

### 7.2 Synonym Table

This table maps common alternative terms to their canonical equivalents. All downstream documents, code, and UI copy MUST use the canonical term.

| Canonical Term | Forbidden Synonyms | Context |
|---|---|---|
| **pipeline** | workflow, job, process, flow | The multi-step document generation process |
| **agent** | bot, worker, model, AI, assistant | An LLM-powered component that performs a specific task |
| **invoke** | call, execute, run, fire | Direct agent execution outside pipeline |
| **trigger** | start, launch, kick off, initiate | Starting a pipeline run |
| **approval** | review, sign-off, authorization, gate check | Human decision gate in a pipeline |
| **exception** | rule, pattern, override, deviation | Knowledge base exception entry |
| **maturity** | trust level, autonomy, confidence tier | Agent maturity progression level |
| **canary** | shadow, blue-green, staged, gradual | Traffic-split version testing |
| **anomaly** | spike, outlier, deviation, irregularity | Cost anomaly detection result |
| **fleet** | cluster, farm, pool, swarm | The entire collection of agents |
| **tier** | level, layer, scope (in knowledge context) | Knowledge exception tier (client/stack/universal) |
| **gate** | checkpoint, barrier, hold, pause point | Approval gate in pipeline |

### 7.3 Conflict Escalation Process

1. Developer notices naming inconsistency between MCP tool and Dashboard widget.
2. Developer looks up the interaction ID in this document (Section 1).
3. If the canonical name here matches one side, the other side must be updated.
4. If neither matches, file a PR against this document proposing a resolution. The PR must update:
   - Section 1 (Interaction Inventory)
   - Section 2 (Data Shape, if field names affected)
   - Section 4 (Naming Conventions, if new verb or noun)
   - Section 7 (Synonym Table, if new canonical term)

---

## Appendix A: Quick Reference — Interaction to MCP Tool Mapping

For MCP-TOOL-SPEC (Doc 08) convenience:

```
agents-server tools (18):
  trigger_pipeline        (I-001)
  get_pipeline_status     (I-002)
  list_pipeline_runs      (I-003)
  resume_pipeline         (I-004)
  cancel_pipeline         (I-005)
  get_pipeline_documents  (I-006)
  retry_pipeline_step     (I-007)
  get_pipeline_config     (I-008)
  validate_project_input  (I-009)
  list_agents             (I-020)
  get_agent               (I-021)
  invoke_agent            (I-022)
  check_agent_health      (I-023)
  promote_agent_version   (I-024)
  rollback_agent_version  (I-025)
  set_canary_traffic      (I-026)
  get_agent_maturity      (I-027)
  get_fleet_health        (I-080)
  get_mcp_status          (I-081)
  check_provider_health   (I-083)
  set_agent_provider      (I-084)

governance-server tools (11):
  get_cost_report         (I-040)
  check_budget            (I-041)
  query_audit_events      (I-042)
  get_audit_summary       (I-043)
  export_audit_report     (I-044)
  list_pending_approvals  (I-045)
  approve_gate            (I-046)
  reject_gate             (I-047)
  get_cost_anomalies      (I-048)
  set_budget_threshold    (I-049)
  list_recent_mcp_calls   (I-082)

knowledge-server tools (4):
  search_exceptions       (I-060)
  create_exception        (I-061)
  promote_exception       (I-062)
  list_exceptions         (I-063)
```

## Appendix B: Quick Reference — Interaction to Dashboard Screen Mapping

For DESIGN-SPEC (Doc 09) convenience:

```
Fleet Health page:
  Health Overview        -> I-080 (FleetHealth)
  Agent Grid             -> I-020 (AgentSummary[])
  Agent Detail Card      -> I-021 (AgentDetail)
  Health Badge           -> I-023 (AgentHealth)
  Maturity Badge         -> I-027 (AgentMaturity)
  Promote Button         -> I-024 (AgentVersion)
  Rollback Button        -> I-025 (AgentVersion)
  Canary Slider          -> I-026 (AgentVersion)
  MCP Panel              -> I-081 (McpServerStatus[])
  MCP Call Feed          -> I-082 (McpCallEvent[])
  Provider Status Panel  -> I-083 (ProviderStatus)

Cost Monitor page:
  Cost Charts            -> I-040 (CostReport)
  Budget Gauges          -> I-041 (BudgetStatus)
  Anomaly Alerts         -> I-048 (CostAnomaly[])
  Budget Settings        -> I-049 (BudgetStatus)

Pipeline Runs page:
  Pipeline Trigger Form  -> I-001 (PipelineRun)
  Pipeline Runs Table    -> I-003 (PipelineRun[])
  Pipeline Status Card   -> I-002 (PipelineRun)
  Resume Button          -> I-004 (PipelineRun)
  Cancel Button          -> I-005 (PipelineRun)
  Retry Button           -> I-007 (PipelineRun)
  Document Viewer        -> I-006 (PipelineDocument[])
  Config Panel           -> I-008 (PipelineConfig)
  Validation Panel       -> I-009 (ValidationResult)

Audit Log page:
  Summary Cards          -> I-043 (AuditSummary)
  Event Table            -> I-042 (AuditEvent[])
  Export Button          -> I-044 (AuditReport)

Approval Queue page:
  Approval Queue Table   -> I-045 (ApprovalRequest[])
  Approve Button         -> I-046 (ApprovalResult)
  Reject Button + Comment-> I-047 (ApprovalResult)
```

## Appendix C: NFR Linkage

Each interaction inherits NFR targets from QUALITY (Doc 05):

| Interface | NFR | Target | Applies To |
|-----------|-----|--------|------------|
| MCP | Q-001 | p95 < 500ms | All MCP read interactions (I-002, I-003, I-020, I-021, I-023, I-027, I-040, I-041, I-042, I-043, I-045, I-048, I-060, I-063, I-080, I-081, I-082) |
| MCP | Q-001 | p95 < 2000ms | All MCP write interactions (I-001, I-004, I-005, I-007, I-022, I-024, I-025, I-026, I-046, I-047, I-049, I-061, I-062) |
| REST | Q-004 | p95 < 500ms | All REST endpoints (mirrors MCP targets) |
| Dashboard | Q-005 | Page load p95 < 2s | All 5 Streamlit pages |
| Cross-interface | Q-049 | MCP-REST parity | Every MCP tool has a REST equivalent (verified in Parity Matrix) |
| Cross-interface | Q-050 | Error code consistency | Same error codes returned by MCP and REST for identical failures |
| Cross-interface | Q-051 | Data shape parity | Same service method returns same shape to both MCP and REST |

---

*End of INTERACTION-MAP. This document is the single source of truth for all interaction IDs, data shapes, and cross-interface contracts. MCP-TOOL-SPEC (Doc 08) and DESIGN-SPEC (Doc 09) MUST NOT define new interactions or shapes without updating this document first.*
