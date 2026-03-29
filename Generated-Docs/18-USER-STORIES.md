# USER-STORIES — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-29
**Document:** 18 of 16 | Status: Draft

---

## Table of Contents

1. [Overview](#1-overview)
2. [Epic Summary Table](#2-epic-summary-table)
3. [Human Stories — Pipeline Execution](#3-human-stories--pipeline-execution)
4. [Human Stories — Agent Management](#4-human-stories--agent-management)
5. [Human Stories — Cost and Budget](#5-human-stories--cost-and-budget)
6. [Human Stories — Audit and Compliance](#6-human-stories--audit-and-compliance)
7. [Human Stories — Approval Gates](#7-human-stories--approval-gates)
8. [Human Stories — Knowledge Management](#8-human-stories--knowledge-management)
9. [Human Stories — MCP Interface](#9-human-stories--mcp-interface)
10. [Human Stories — Dashboard](#10-human-stories--dashboard)
11. [System Stories](#11-system-stories)
12. [Parking Lot](#12-parking-lot)
13. [Glossary](#13-glossary)

---

## 1. Overview

This document captures all user stories for the Agentic SDLC Platform, organized by epic. Stories are written from the perspective of five personas defined in the PRD (Doc 01):

| Persona | Role | Primary Interface |
|---|---|---|
| **Priya Sharma** | Platform Engineer | MCP via Claude Code |
| **Marcus Chen** | Delivery Lead | MCP via Claude Code |
| **Anika Patel** | Engineering Lead | Streamlit Dashboard |
| **David Okonkwo** | DevOps Engineer | Streamlit Dashboard |
| **Fatima Al-Rashidi** | Compliance Officer | Streamlit Dashboard |

Additionally, **System Stories** describe automated behaviors performed by agents and platform services, with System Acceptance Criteria (SACs) referencing specific API endpoints, database tables, and data model entities.

### Story Format

```
US-{CATEGORY}-{NNN}: As {persona}, I want to {action} so that {outcome}.

Acceptance Criteria:
- AC-1: ...
- AC-2: ...

Priority: must | should | could
Story Points: 1 | 2 | 3 | 5 | 8 | 13
Epic: E-{NNN}
Features: F-{NNN}, F-{NNN}
```

---

## 2. Epic Summary Table

| Epic | Name | Story Count | Must | Should | Could | Total SP |
|---|---|---|---|---|---|---|
| E-001 | Pipeline Execution | 7 | 5 | 2 | 0 | 34 |
| E-002 | Agent Management | 6 | 4 | 1 | 1 | 26 |
| E-003 | Cost and Budget | 5 | 4 | 1 | 0 | 21 |
| E-004 | Audit and Compliance | 4 | 3 | 1 | 0 | 16 |
| E-005 | Human Approval Gates | 4 | 3 | 1 | 0 | 18 |
| E-006 | Knowledge Management | 3 | 1 | 2 | 0 | 10 |
| E-007 | MCP Server Infrastructure | 4 | 3 | 1 | 0 | 13 |
| E-008 | Dashboard / Operator UI | 5 | 4 | 1 | 0 | 21 |
| E-009 | Quality and Testing | 3 | 2 | 1 | 0 | 11 |
| E-010 | Platform Foundation | 4 | 3 | 1 | 0 | 15 |
| **Total** | | **45** | **32** | **12** | **1** | **185** |

---

## 3. Human Stories — Pipeline Execution

### US-PIPE-001: Trigger Full Document Pipeline

**As** Marcus (Delivery Lead), **I want to** trigger a 24-document generation pipeline from a project brief **so that** all SDLC specifications are generated automatically without me writing each document by hand.

**Acceptance Criteria:**
- AC-1: Marcus invokes `trigger_pipeline` MCP tool with a `project_brief` parameter and receives a `run_id` within 5 seconds
- AC-2: Pipeline creates a `pipeline_runs` record with `status = 'running'` and `document_count = 24`
- AC-3: Pipeline creates 24 `pipeline_steps` records, one per document, with ordered `step_number`
- AC-4: All 24 documents are generated and stored in `reports/{project_id}/{run_id}/`
- AC-5: Pipeline completes in < 30 minutes with total cost < $45 USD

**Priority:** must | **Story Points:** 8 | **Epic:** E-001 | **Features:** F-001

---

### US-PIPE-002: Monitor Pipeline Progress

**As** Marcus (Delivery Lead), **I want to** check pipeline status while it runs **so that** I know which documents are complete, which are in progress, and which are pending without leaving my editor.

**Acceptance Criteria:**
- AC-1: `check_pipeline_status` MCP tool returns current status, completed steps, active step, and pending steps
- AC-2: Status includes per-step `quality_score`, `token_count`, and `cost_usd`
- AC-3: Response latency < 500ms (read operation)

**Priority:** must | **Story Points:** 3 | **Epic:** E-001 | **Features:** F-002

---

### US-PIPE-003: Resume Failed Pipeline

**As** Priya (Platform Engineer), **I want to** resume a failed pipeline from its last checkpoint **so that** I do not re-generate documents that already passed quality gates, saving time and cost.

**Acceptance Criteria:**
- AC-1: `resume_pipeline` MCP tool accepts a `run_id` and resumes from the last successful `pipeline_checkpoints` entry
- AC-2: Already-completed steps are skipped; their outputs are preserved
- AC-3: Cost tracking continues from the accumulated total (no double-counting)
- AC-4: Resumed run uses the same `run_id` with `status` updated from `failed` to `running`

**Priority:** must | **Story Points:** 5 | **Epic:** E-001 | **Features:** F-005

---

### US-PIPE-004: Re-generate Single Document

**As** Marcus (Delivery Lead), **I want to** re-generate a single document within a completed pipeline run **so that** when requirements change I only pay for regenerating the affected document, not the entire stack.

**Acceptance Criteria:**
- AC-1: `regenerate_document` MCP tool accepts `run_id` and `document_type` parameters
- AC-2: Only the specified document is regenerated; all other documents remain unchanged
- AC-3: New `pipeline_steps` record created for the regeneration with updated `quality_score`
- AC-4: Cost tracked separately as a supplemental cost on the original `pipeline_runs` record

**Priority:** should | **Story Points:** 5 | **Epic:** E-001 | **Features:** F-003

---

### US-PIPE-005: View Pipeline Run History

**As** Anika (Engineering Lead), **I want to** see a list of all pipeline runs with their status, cost, and document count **so that** I can track team productivity and identify quality trends.

**Acceptance Criteria:**
- AC-1: Pipeline Runs dashboard page displays paginated list from `pipeline_runs` table
- AC-2: Each row shows: `run_id`, `project_id`, `status`, `triggered_at`, `completed_at`, `document_count`, `total_cost_usd`
- AC-3: Sortable by date, status, and cost
- AC-4: Filterable by `project_id` and `status`
- AC-5: Page loads in < 2 seconds

**Priority:** must | **Story Points:** 5 | **Epic:** E-001 | **Features:** F-002

---

### US-PIPE-006: View Pipeline Run Detail

**As** Anika (Engineering Lead), **I want to** drill into a pipeline run to see per-step details **so that** I can understand which agents produced which documents and at what quality level.

**Acceptance Criteria:**
- AC-1: Pipeline Run Detail view shows all `pipeline_steps` for a given `run_id`
- AC-2: Each step displays: `step_number`, `document_type`, `agent_id`, `status`, `quality_score`, `token_count`, `cost_usd`, `duration_ms`
- AC-3: Failed steps show error details from `pipeline_steps.error_message`
- AC-4: Links to download generated document from file system

**Priority:** must | **Story Points:** 5 | **Epic:** E-001 | **Features:** F-002

---

### US-PIPE-007: Cancel Running Pipeline

**As** Priya (Platform Engineer), **I want to** cancel a running pipeline **so that** I can stop cost accumulation when I realize the input brief was wrong.

**Acceptance Criteria:**
- AC-1: `cancel_pipeline` MCP tool sets `pipeline_runs.status = 'cancelled'`
- AC-2: Currently executing agent is sent a cancellation signal within 5 seconds
- AC-3: Partially generated documents are preserved with status `partial`
- AC-4: Final cost recorded reflects only completed work

**Priority:** should | **Story Points:** 3 | **Epic:** E-001 | **Features:** F-004

---

## 4. Human Stories — Agent Management

### US-AGENT-001: Promote Agent Maturity Tier

**As** Anika (Engineering Lead), **I want to** promote an agent from apprentice (T0) to journeyman (T1) based on its performance metrics **so that** trusted agents can operate with less human oversight.

**Acceptance Criteria:**
- AC-1: Promotion action available on Agent Detail page in Dashboard
- AC-2: Promotion requires: minimum 50 invocations, quality score average > 0.8, override rate < 10%
- AC-3: Promotion updates `agent_registry.maturity_level` and creates an `audit_events` record with action `agent.promote`
- AC-4: Only users with `reviewer` or `admin` role can promote

**Priority:** must | **Story Points:** 5 | **Epic:** E-002 | **Features:** F-012

---

### US-AGENT-002: View Agent Fleet Health

**As** David (DevOps Engineer), **I want to** see the health status of all 48 agents on a single page **so that** I can quickly identify agents that are down, degraded, or consuming excessive resources.

**Acceptance Criteria:**
- AC-1: Fleet Health Overview dashboard page displays all 48 agents from `agent_registry`
- AC-2: Each agent shows: name, phase, status (healthy/degraded/down), maturity tier, cost today, invocation count today
- AC-3: Color-coded status indicators (green/yellow/red)
- AC-4: Page loads in < 1 second (M3)
- AC-5: Auto-refresh every 30 seconds

**Priority:** must | **Story Points:** 5 | **Epic:** E-002 | **Features:** F-008, F-009

---

### US-AGENT-003: Deploy Agent Canary Version

**As** Priya (Platform Engineer), **I want to** deploy a canary version of an agent with configurable traffic split **so that** I can test new agent versions on a subset of pipeline runs before full rollout.

**Acceptance Criteria:**
- AC-1: `deploy_canary` MCP tool updates `agent_registry.canary_version` and `canary_traffic_pct`
- AC-2: Traffic split configurable (default 10%, max 50%)
- AC-3: Canary metrics tracked separately in `cost_metrics` and `audit_events`
- AC-4: Promote canary to active via `promote_canary` MCP tool
- AC-5: Rollback canary via `rollback_canary` MCP tool (sets `canary_version = null`)

**Priority:** must | **Story Points:** 5 | **Epic:** E-002 | **Features:** F-013

---

### US-AGENT-004: View Agent Detail

**As** Priya (Platform Engineer), **I want to** view detailed information about a specific agent including its manifest, version history, and performance metrics **so that** I can diagnose issues and plan upgrades.

**Acceptance Criteria:**
- AC-1: `query_agent` MCP tool returns full `AgentDetail` data shape
- AC-2: Response includes: manifest content, prompt preview, active version, canary version, maturity tier, cost metrics, invocation history
- AC-3: Dashboard Agent Detail page displays the same information visually
- AC-4: Response latency < 500ms for MCP; page load < 2s for Dashboard

**Priority:** must | **Story Points:** 3 | **Epic:** E-002 | **Features:** F-010

---

### US-AGENT-005: Search Agents by Phase or Status

**As** David (DevOps Engineer), **I want to** filter the agent fleet by SDLC phase (GOVERN, DESIGN, BUILD, etc.) or by status (healthy, degraded, down) **so that** I can focus on the agents relevant to my current task.

**Acceptance Criteria:**
- AC-1: `list_agents` MCP tool accepts optional `phase` and `status` filter parameters
- AC-2: Dashboard Fleet Health page has filter dropdowns for phase and status
- AC-3: Results update within 500ms of filter change

**Priority:** should | **Story Points:** 2 | **Epic:** E-002 | **Features:** F-008

---

### US-AGENT-006: Decommission Agent

**As** Priya (Platform Engineer), **I want to** decommission an agent that is no longer needed **so that** it stops receiving pipeline assignments and its resources are reclaimed.

**Acceptance Criteria:**
- AC-1: Decommission action sets `agent_registry.status = 'decommissioned'`
- AC-2: Decommissioned agents excluded from pipeline assignment
- AC-3: Historical data (cost_metrics, audit_events) preserved for decommissioned agents
- AC-4: Audit event recorded with action `agent.decommission`

**Priority:** could | **Story Points:** 3 | **Epic:** E-002 | **Features:** F-014

---

## 5. Human Stories — Cost and Budget

### US-COST-001: View Real-Time Cost Burn-Down

**As** Marcus (Delivery Lead), **I want to** see real-time cost burn-down for an active pipeline run **so that** I can stop runaway agents before they exhaust the budget.

**Acceptance Criteria:**
- AC-1: `check_cost` MCP tool returns current total cost, per-agent cost breakdown, and remaining budget for a `run_id`
- AC-2: Cost data updated within 2 seconds of each LLM API call
- AC-3: Dashboard Cost Monitor page shows burn-down chart for active runs
- AC-4: Budget utilization displayed as percentage with color coding (green < 70%, yellow 70-90%, red > 90%)

**Priority:** must | **Story Points:** 5 | **Epic:** E-003 | **Features:** F-016, F-017

---

### US-COST-002: Set Budget Ceiling per Project

**As** Anika (Engineering Lead), **I want to** configure a cost budget ceiling per project **so that** no single project can consume more than its allocated LLM budget.

**Acceptance Criteria:**
- AC-1: Budget ceiling configurable via Dashboard or REST API per `project_id`
- AC-2: G1-cost-tracker enforces hard-stop when project budget is reached
- AC-3: All agents in the project halt execution when ceiling is hit
- AC-4: Alert sent to Slack and displayed on Dashboard

**Priority:** must | **Story Points:** 3 | **Epic:** E-003 | **Features:** F-018

---

### US-COST-003: View Cost Report by Time Period

**As** Fatima (Compliance Officer), **I want to** generate a cost report for a specified time period grouped by agent, project, and provider **so that** I can audit LLM spend for governance reviews.

**Acceptance Criteria:**
- AC-1: `get_cost_report` MCP tool accepts `start_date`, `end_date`, and `group_by` parameters
- AC-2: Report aggregates `cost_metrics` by requested grouping
- AC-3: Dashboard Cost Monitor page offers date range picker and group-by selector
- AC-4: Report exportable as CSV from Dashboard
- AC-5: Cost accuracy within 2% of actual provider billing (M7)

**Priority:** must | **Story Points:** 5 | **Epic:** E-003 | **Features:** F-019

---

### US-COST-004: Detect Cost Anomalies

**As** David (DevOps Engineer), **I want to** be alerted when an agent's cost deviates significantly from its historical average **so that** I can investigate potential token loops or misconfigured prompts.

**Acceptance Criteria:**
- AC-1: Anomaly detection compares rolling 7-day average against current window per agent
- AC-2: Alert fires when cost exceeds 2x the rolling average
- AC-3: Alert sent to Slack and displayed as warning on Fleet Health page
- AC-4: `CostAnomaly` data shape computed on-the-fly from `cost_metrics`

**Priority:** must | **Story Points:** 5 | **Epic:** E-003 | **Features:** F-020

---

### US-COST-005: View Provider Cost Comparison

**As** Priya (Platform Engineer), **I want to** compare cost-per-token and latency across LLM providers (Anthropic, OpenAI, Ollama) **so that** I can optimize provider selection for each agent.

**Acceptance Criteria:**
- AC-1: Cost Monitor dashboard tab shows per-provider breakdown of cost, token count, and average latency
- AC-2: Data sourced from `cost_metrics` grouped by `provider` field
- AC-3: Comparison table updated daily

**Priority:** should | **Story Points:** 3 | **Epic:** E-003 | **Features:** F-021

---

## 6. Human Stories — Audit and Compliance

### US-AUDIT-001: Query Audit Trail

**As** Fatima (Compliance Officer), **I want to** query the audit trail by agent, date range, action type, and severity **so that** I can investigate specific events without reading code or querying databases directly.

**Acceptance Criteria:**
- AC-1: `query_audit_events` MCP tool accepts filters: `agent_id`, `start_date`, `end_date`, `action`, `severity`, `project_id`
- AC-2: Dashboard Audit Log page provides the same filter capabilities with a search interface
- AC-3: Results paginated (50 per page) and sortable by timestamp
- AC-4: Each audit event displays all 13 fields defined in the data model

**Priority:** must | **Story Points:** 5 | **Epic:** E-004 | **Features:** F-022

---

### US-AUDIT-002: Generate Compliance Report

**As** Fatima (Compliance Officer), **I want to** generate an audit-ready compliance report in under 10 minutes **so that** I can present it at the monthly governance board review without manual data assembly.

**Acceptance Criteria:**
- AC-1: Dashboard "Generate Report" button produces a formatted compliance report
- AC-2: Report includes: agent invocation summary, cost summary, approval gate statistics, PII scan results, anomaly incidents
- AC-3: Report generation completes in < 10 minutes
- AC-4: Report exportable as PDF and CSV
- AC-5: Report data sourced from `audit_events`, `cost_metrics`, `approval_requests`, and `pipeline_runs`

**Priority:** must | **Story Points:** 5 | **Epic:** E-004 | **Features:** F-024

---

### US-AUDIT-003: Verify Audit Trail Completeness

**As** Fatima (Compliance Officer), **I want to** verify that 100% of agent invocations have corresponding audit records **so that** I can confirm no audit gaps exist before a compliance review.

**Acceptance Criteria:**
- AC-1: Dashboard shows reconciliation status (last run timestamp, gap count)
- AC-2: Nightly reconciliation job compares `agent_invocations` count against `audit_events` count by date
- AC-3: Any gaps trigger an alert and are displayed on the Audit Log dashboard page
- AC-4: Zero gaps required for compliance sign-off (M10)

**Priority:** must | **Story Points:** 3 | **Epic:** E-004 | **Features:** F-023

---

### US-AUDIT-004: View Agent Decision Trail

**As** Anika (Engineering Lead), **I want to** see the reasoning chain for a specific agent invocation **so that** I can understand why an agent produced a particular output and provide targeted feedback.

**Acceptance Criteria:**
- AC-1: Audit event detail view shows `details` JSONB field with reasoning chain
- AC-2: Includes: input summary, prompt template used, LLM response metadata, confidence score, quality score
- AC-3: Accessible from both MCP (`query_audit_events` with `include_details=true`) and Dashboard

**Priority:** should | **Story Points:** 3 | **Epic:** E-004 | **Features:** F-025

---

## 7. Human Stories — Approval Gates

### US-APPROVE-001: Review and Approve Pipeline Output

**As** Anika (Engineering Lead), **I want to** review an agent-generated document at an approval gate and approve or reject it with structured comments **so that** quality standards are maintained without me becoming a bottleneck.

**Acceptance Criteria:**
- AC-1: Dashboard Approval Queue page shows all pending `approval_requests` assigned to the reviewer
- AC-2: Each request displays: document preview, agent confidence score, quality score, input brief summary
- AC-3: Approve action sets `approval_requests.status = 'approved'` and unblocks the pipeline
- AC-4: Reject action requires structured comment (category + description) and triggers re-generation
- AC-5: Median approval response time < 5 minutes (M4)

**Priority:** must | **Story Points:** 5 | **Epic:** E-005 | **Features:** F-027, F-028

---

### US-APPROVE-002: Receive Approval Notifications

**As** Anika (Engineering Lead), **I want to** receive Slack notifications when a pipeline reaches a human review gate **so that** I can respond promptly without constantly watching the dashboard.

**Acceptance Criteria:**
- AC-1: Slack notification sent within 30 seconds of gate activation
- AC-2: Notification includes: pipeline run_id, document type, agent_id, confidence score, deep link to Dashboard
- AC-3: Notification sent to configurable Slack channel per project

**Priority:** must | **Story Points:** 3 | **Epic:** E-005 | **Features:** F-029

---

### US-APPROVE-003: Configure Approval Policies

**As** Anika (Engineering Lead), **I want to** configure which pipeline steps require human approval based on agent maturity tier **so that** trusted agents (T2-T3) can auto-approve routine outputs while new agents (T0-T1) always require review.

**Acceptance Criteria:**
- AC-1: Approval policy configurable per step and per maturity tier via Dashboard settings
- AC-2: T0-T1 agents: all outputs require human approval
- AC-3: T2 agents: outputs with confidence score > 0.85 auto-approved; others require review
- AC-4: T3 agents: all outputs auto-approved unless anomaly detected
- AC-5: Policy changes recorded in `audit_events` with action `config.approval_policy`

**Priority:** must | **Story Points:** 5 | **Epic:** E-005 | **Features:** F-030

---

### US-APPROVE-004: View Approval History

**As** Fatima (Compliance Officer), **I want to** view the complete approval history for a pipeline run **so that** I can verify that all required gates were respected during an audit.

**Acceptance Criteria:**
- AC-1: Pipeline Run Detail shows approval status for each step
- AC-2: Each approval record shows: reviewer, decision, timestamp, comment (if rejected), auto-approved flag
- AC-3: Filterable by `auto_approved = true/false` to distinguish human vs automatic approvals

**Priority:** should | **Story Points:** 3 | **Epic:** E-005 | **Features:** F-031

---

## 8. Human Stories — Knowledge Management

### US-KNOW-001: Search Exception Knowledge Base

**As** Priya (Platform Engineer), **I want to** search the knowledge exception database for known edge cases related to a document type **so that** I can configure agents to handle them proactively.

**Acceptance Criteria:**
- AC-1: `search_exceptions` MCP tool accepts `query`, `document_type`, and `category` parameters
- AC-2: Returns matching `knowledge_exceptions` records ranked by relevance
- AC-3: Knowledge base accessible via knowledge-server MCP

**Priority:** must | **Story Points:** 3 | **Epic:** E-006 | **Features:** F-037

---

### US-KNOW-002: Add Exception to Knowledge Base

**As** Anika (Engineering Lead), **I want to** add a new exception or lesson learned when I reject a document at an approval gate **so that** agents can learn from past mistakes.

**Acceptance Criteria:**
- AC-1: Rejection form includes optional "Add to Knowledge Base" checkbox
- AC-2: Exception stored in `knowledge_exceptions` with: category, description, document_type, agent_id, project_id
- AC-3: PII scanner runs on description before storage
- AC-4: Knowledge entry linked to the original `audit_events` record

**Priority:** should | **Story Points:** 3 | **Epic:** E-006 | **Features:** F-038

---

### US-KNOW-003: Agent Consults Knowledge Base During Generation

**As** Marcus (Delivery Lead), **I want** agents to automatically query relevant exceptions from the knowledge base during document generation **so that** known edge cases are handled without me remembering to mention them in the brief.

**Acceptance Criteria:**
- AC-1: Agents query `knowledge_exceptions` for matching `document_type` before generation
- AC-2: Relevant exceptions included in the agent's context window
- AC-3: Audit event records which exceptions were consulted

**Priority:** should | **Story Points:** 5 | **Epic:** E-006 | **Features:** F-039

---

## 9. Human Stories — MCP Interface

### US-MCP-001: Invoke Pipeline via MCP Tool

**As** an AI assistant (Claude Code), **I want to** invoke `trigger_pipeline` **so that** a user can start document generation from within their development environment without switching to a browser.

**Acceptance Criteria:**
- AC-1: MCP tool `trigger_pipeline` registered on agents-server
- AC-2: Tool accepts `project_brief` (string, required) and `config_overrides` (object, optional)
- AC-3: Returns `{ run_id, status, estimated_duration, estimated_cost }` within 5 seconds
- AC-4: Tool call recorded in `mcp_call_events` with latency

**Priority:** must | **Story Points:** 3 | **Epic:** E-007 | **Features:** F-001

---

### US-MCP-002: Query Fleet Health via MCP

**As** an AI assistant (Claude Code), **I want to** invoke `check_fleet_health` **so that** a user can see the status of all 48 agents without opening a browser dashboard.

**Acceptance Criteria:**
- AC-1: MCP tool `check_fleet_health` registered on governance-server
- AC-2: Returns summary: total agents, healthy count, degraded count, down count, top cost agents today
- AC-3: Response latency < 500ms

**Priority:** must | **Story Points:** 2 | **Epic:** E-007 | **Features:** F-042

---

### US-MCP-003: Check Cost via MCP

**As** an AI assistant (Claude Code), **I want to** invoke `check_cost` with a `run_id` or `project_id` **so that** a user can see current cost without leaving their editor.

**Acceptance Criteria:**
- AC-1: MCP tool `check_cost` registered on governance-server
- AC-2: Accepts `run_id` (optional) and `project_id` (optional) parameters
- AC-3: Returns `BudgetStatus` data shape: spent_usd, budget_usd, utilization_pct, per_agent_breakdown
- AC-4: Response latency < 500ms

**Priority:** must | **Story Points:** 2 | **Epic:** E-007 | **Features:** F-017

---

### US-MCP-004: List Pending Approvals via MCP

**As** an AI assistant (Claude Code), **I want to** invoke `list_pending_approvals` **so that** a reviewer can see what needs their attention without opening the dashboard.

**Acceptance Criteria:**
- AC-1: MCP tool `list_pending_approvals` registered on governance-server
- AC-2: Returns list of `approval_requests` with `status = 'pending'`, filtered by reviewer role
- AC-3: Each item includes: request_id, pipeline_run_id, document_type, agent_id, confidence_score, pending_since

**Priority:** should | **Story Points:** 2 | **Epic:** E-007 | **Features:** F-027

---

## 10. Human Stories — Dashboard

### US-DASH-001: Fleet Health Overview Page

**As** David (DevOps Engineer), **I want** a Fleet Health Overview dashboard page showing all 48 agents at a glance **so that** I can detect and respond to fleet issues within 15 minutes.

**Acceptance Criteria:**
- AC-1: Page displays agent grid with status indicators for all 48 agents
- AC-2: Grouped by SDLC phase (GOVERN, DESIGN, BUILD, TEST, DEPLOY, OPERATE, OVERSIGHT)
- AC-3: Each agent tile shows: name, status, tier, cost today, last invocation time
- AC-4: Page loads in < 1 second (M3)
- AC-5: Auto-refresh every 30 seconds
- AC-6: Click on agent tile navigates to Agent Detail view

**Priority:** must | **Story Points:** 5 | **Epic:** E-008 | **Features:** F-008, F-009

---

### US-DASH-002: Cost Monitor Page

**As** David (DevOps Engineer), **I want** a Cost Monitor dashboard page with real-time cost tracking **so that** I can ensure no agent or project exceeds its budget.

**Acceptance Criteria:**
- AC-1: Page shows fleet-level cost summary: total spend today, budget remaining, top 5 cost agents
- AC-2: Cost burn-down chart for active pipeline runs
- AC-3: Historical cost trend chart (daily, weekly, monthly)
- AC-4: Per-provider cost breakdown (Anthropic, OpenAI, Ollama)
- AC-5: Budget alerts highlighted in red when utilization > 90%

**Priority:** must | **Story Points:** 5 | **Epic:** E-008 | **Features:** F-016, F-017

---

### US-DASH-003: Pipeline Runs Page

**As** Anika (Engineering Lead), **I want** a Pipeline Runs dashboard page showing all pipeline executions **so that** I can track team productivity and investigate failures.

**Acceptance Criteria:**
- AC-1: Paginated table of `pipeline_runs` with columns: run_id, project_id, status, triggered_at, duration, document_count, total_cost
- AC-2: Status filters: running, completed, failed, cancelled
- AC-3: Click on row navigates to Pipeline Run Detail
- AC-4: Page loads in < 2 seconds

**Priority:** must | **Story Points:** 3 | **Epic:** E-008 | **Features:** F-002

---

### US-DASH-004: Audit Log Page

**As** Fatima (Compliance Officer), **I want** an Audit Log dashboard page with search and filter capabilities **so that** I can investigate specific events and generate compliance evidence.

**Acceptance Criteria:**
- AC-1: Paginated table of `audit_events` with columns: timestamp, agent_id, action, severity, project_id, cost_usd
- AC-2: Filters: date range, agent_id, action type, severity level, project_id
- AC-3: Full-text search on `details` JSONB field
- AC-4: Export to CSV button
- AC-5: Page loads in < 2 seconds

**Priority:** must | **Story Points:** 5 | **Epic:** E-008 | **Features:** F-022

---

### US-DASH-005: Approval Queue Page

**As** Anika (Engineering Lead), **I want** an Approval Queue dashboard page showing all items awaiting my review **so that** I have a centralized queue instead of checking email or Slack for review requests.

**Acceptance Criteria:**
- AC-1: Page shows all `approval_requests` with `status = 'pending'` assigned to the logged-in reviewer
- AC-2: Each item shows: document preview, confidence score, quality score, pipeline context
- AC-3: Approve and Reject buttons with structured comment form
- AC-4: Queue count displayed in navigation bar badge
- AC-5: Items ordered by priority (low confidence first)

**Priority:** should | **Story Points:** 3 | **Epic:** E-008 | **Features:** F-027, F-028

---

## 11. System Stories

System stories describe automated behaviors with System Acceptance Criteria (SACs) referencing specific API endpoints, database tables, and agents.

---

### SS-001: G1-cost-tracker Records LLM Cost

**When** any agent makes an LLM API call, **the system** records the cost in `cost_metrics` within 2 seconds.

**SAC:**
- SAC-1: `POST /api/cost-events` creates a row in `cost_metrics` with: `agent_id`, `provider`, `model`, `input_tokens`, `output_tokens`, `cost_usd`, `pipeline_run_id`, `timestamp`
- SAC-2: G1-cost-tracker agent processes the cost event and updates running totals
- SAC-3: If `SUM(cost_usd) WHERE pipeline_run_id = ?` exceeds the run budget ceiling, G1-cost-tracker sends a `pipeline.halt` command to G4-team-orchestrator
- SAC-4: Cost recorded within 2 seconds of LLM API response (verified by `cost_metrics.timestamp - llm_response.timestamp`)

**Priority:** must | **Story Points:** 3 | **Epic:** E-003 | **Features:** F-016

---

### SS-002: G2-audit-trail-validator Ensures Completeness

**When** an agent invocation completes, **the system** validates that an audit record exists within 5 seconds.

**SAC:**
- SAC-1: G2-audit-trail-validator listens for `agent.invocation.complete` events
- SAC-2: Validates that `audit_events` contains a record matching `agent_id`, `run_id`, `timestamp` within a 5-second window
- SAC-3: If no matching record found, G2 creates a gap alert in `audit_events` with `severity = 'critical'` and `action = 'audit.gap_detected'`
- SAC-4: Nightly reconciliation: `SELECT COUNT(*) FROM agent_invocations WHERE date = ? EXCEPT SELECT COUNT(*) FROM audit_events WHERE date = ?` must equal zero

**Priority:** must | **Story Points:** 3 | **Epic:** E-004 | **Features:** F-023

---

### SS-003: G3-agent-lifecycle-manager Enforces Health Checks

**When** a health check interval elapses, **the system** pings each active agent and updates `agent_registry`.

**SAC:**
- SAC-1: G3-agent-lifecycle-manager runs health checks every 60 seconds for active agents
- SAC-2: Health check pings agent endpoint; timeout after 5 seconds = degraded, 3 consecutive timeouts = down
- SAC-3: `agent_registry.status` updated to `healthy`, `degraded`, or `down`
- SAC-4: Circuit breaker opens after 3 consecutive failures; `agent_registry.circuit_breaker_open = true`
- SAC-5: Status change logged in `audit_events` with action `agent.health.change`

**Priority:** must | **Story Points:** 3 | **Epic:** E-002 | **Features:** F-009

---

### SS-004: G4-team-orchestrator Assigns Agents to Pipeline Steps

**When** a pipeline run starts, **the system** assigns the best available agent to each pipeline step based on document type and agent maturity.

**SAC:**
- SAC-1: G4-team-orchestrator reads pipeline configuration from `teams/document-stack.yaml`
- SAC-2: For each step, selects agent from `agent_registry` WHERE `phase` matches AND `status = 'active'` AND `maturity_level >= minimum_required`
- SAC-3: Canary traffic splitting: if `canary_version IS NOT NULL`, routes `canary_traffic_pct`% of invocations to canary
- SAC-4: Assignment recorded in `pipeline_steps.agent_id`
- SAC-5: If no eligible agent available for a step, pipeline halts with `status = 'blocked'` and alert sent

**Priority:** must | **Story Points:** 5 | **Epic:** E-001 | **Features:** F-001

---

### SS-005: Pipeline Checkpoint on Step Completion

**When** a pipeline step completes successfully, **the system** creates a checkpoint for resume capability.

**SAC:**
- SAC-1: `INSERT INTO pipeline_checkpoints (run_id, step_number, checkpoint_data, created_at)` after each successful step
- SAC-2: `checkpoint_data` includes: completed step outputs, accumulated cost, session state reference
- SAC-3: On resume, `SELECT MAX(step_number) FROM pipeline_checkpoints WHERE run_id = ?` determines restart point

**Priority:** must | **Story Points:** 2 | **Epic:** E-001 | **Features:** F-005

---

### SS-006: Session Context Management

**When** a pipeline run starts, **the system** creates a session context that agents share for cross-document consistency.

**SAC:**
- SAC-1: `INSERT INTO session_context (session_id, run_id, context_data, created_at)` at pipeline start
- SAC-2: Each agent reads relevant context from `session_context` before generation
- SAC-3: Each agent writes updated context (extracted entities, decisions, terminology) back to `session_context`
- SAC-4: PII scanner runs on `context_data` before write (C3 classification)
- SAC-5: Session context expires after 7 days via automated cleanup

**Priority:** must | **Story Points:** 3 | **Epic:** E-010 | **Features:** F-049

---

### SS-007: MCP Call Telemetry Recording

**When** any MCP tool is invoked, **the system** records telemetry in `mcp_call_events`.

**SAC:**
- SAC-1: `INSERT INTO mcp_call_events (tool_name, server_name, client_id, duration_ms, status_code, timestamp)`
- SAC-2: Duration measured from request receipt to response dispatch
- SAC-3: Telemetry does not include request/response payloads (privacy)
- SAC-4: Data feeds Prometheus histogram `mcp_tool_duration_seconds`

**Priority:** must | **Story Points:** 2 | **Epic:** E-007 | **Features:** F-042

---

### SS-008: Quality Score Computation

**When** an agent produces a document, **the system** computes a quality score before the document proceeds to the next pipeline step.

**SAC:**
- SAC-1: G5-quality-gate-enforcer evaluates the generated document against the quality schema
- SAC-2: Quality score (0.0 - 1.0) stored in `pipeline_steps.quality_score`
- SAC-3: Documents scoring below threshold (configurable, default 0.7) are flagged for human review
- SAC-4: Quality evaluation cost tracked in `cost_metrics` (attributed to G5 agent)

**Priority:** must | **Story Points:** 3 | **Epic:** E-009 | **Features:** F-032

---

### SS-009: LLM Provider Routing

**When** an agent needs to call an LLM, **the system** routes the request to the correct provider based on data classification and agent configuration.

**SAC:**
- SAC-1: Provider abstraction layer checks data classification of input context
- SAC-2: C3 (Confidential) data routed to Ollama only; external providers (Anthropic, OpenAI) blocked
- SAC-3: C4 (Restricted) data blocked from all LLM providers
- SAC-4: Provider selection respects agent manifest `supported_providers` list
- SAC-5: Provider fallback: if primary provider returns 5xx, retry with secondary provider (if configured)

**Priority:** must | **Story Points:** 3 | **Epic:** E-010 | **Features:** F-045

---

### SS-010: Automated Retention Enforcement

**When** data exceeds its retention period, **the system** automatically deletes or archives it.

**SAC:**
- SAC-1: pg_cron job runs daily at 02:00 UTC
- SAC-2: `DELETE FROM session_context WHERE created_at < NOW() - INTERVAL '7 days'`
- SAC-3: `DELETE FROM pipeline_checkpoints WHERE created_at < NOW() - INTERVAL '30 days'`
- SAC-4: `DELETE FROM cost_metrics WHERE created_at < NOW() - INTERVAL '90 days'` (after monthly aggregation)
- SAC-5: `DELETE FROM mcp_call_events WHERE created_at < NOW() - INTERVAL '90 days'`
- SAC-6: `audit_events` archived to cold storage after 1 year (not deleted)
- SAC-7: Deletion counts logged in `audit_events` with action `system.retention.cleanup`

**Priority:** must | **Story Points:** 2 | **Epic:** E-010 | **Features:** F-054

---

### SS-011: PII Scanning Before Persistence

**When** data is written to a C3 (Confidential) table, **the system** scans for and flags PII.

**SAC:**
- SAC-1: PII scanner middleware runs on all writes to `session_context` and `audit_events.details`
- SAC-2: Scanner detects: email addresses, phone numbers, SSNs, credit card numbers, names (NER-based)
- SAC-3: Detected PII is redacted before storage unless explicitly allowed by project configuration
- SAC-4: PII scan results recorded in `audit_events` with action `system.pii.scan`

**Priority:** must | **Story Points:** 3 | **Epic:** E-009 | **Features:** F-033

---

### SS-012: Rate Limiting Enforcement

**When** API calls exceed rate limits, **the system** returns 429 responses with retry-after headers.

**SAC:**
- SAC-1: Token bucket rate limiter per `client_id` for MCP and per `user_id` for REST
- SAC-2: Default limits: 100 req/min for MCP tools, 200 req/min for REST endpoints
- SAC-3: Rate limiter state stored in-memory (Python dict / token buckets)
- SAC-4: Response includes `Retry-After` header with seconds until next allowed request
- SAC-5: Rate limit hits logged in `mcp_call_events` with `status_code = 429`

**Priority:** must | **Story Points:** 2 | **Epic:** E-010 | **Features:** F-050

---

### SS-013: Circuit Breaker for LLM Providers

**When** an LLM provider returns consecutive errors, **the system** opens a circuit breaker to prevent cascading failures.

**SAC:**
- SAC-1: Circuit breaker per provider: opens after 5 consecutive 5xx responses within 60 seconds
- SAC-2: Open circuit returns immediate failure to calling agent (no LLM call attempted)
- SAC-3: Half-open state: after 30 seconds, allow 1 probe request; if successful, close circuit
- SAC-4: Circuit state changes logged in `audit_events` with action `system.circuit_breaker.change`
- SAC-5: Open circuits visible on Fleet Health dashboard and via `check_fleet_health` MCP tool

**Priority:** must | **Story Points:** 2 | **Epic:** E-010 | **Features:** F-051

---

### SS-014: G5-quality-gate-enforcer Auto-Approval Decision

**When** a pipeline step reaches an approval gate, **the system** determines if auto-approval is permitted based on agent tier and confidence score.

**SAC:**
- SAC-1: G5-quality-gate-enforcer reads approval policy from configuration
- SAC-2: If `agent.maturity_level = T0 OR T1`: always require human approval, insert `approval_requests` with `status = 'pending'`
- SAC-3: If `agent.maturity_level = T2` AND `quality_score >= 0.85`: auto-approve, insert `approval_requests` with `status = 'approved', auto_approved = true`
- SAC-4: If `agent.maturity_level = T3`: auto-approve unless anomaly detected
- SAC-5: Auto-approval decision logged in `audit_events` with action `approval.auto` or `approval.require_human`

**Priority:** must | **Story Points:** 3 | **Epic:** E-005 | **Features:** F-030

---

### SS-015: Slack Notification Dispatch

**When** a pipeline reaches an approval gate or a critical alert fires, **the system** sends a Slack notification.

**SAC:**
- SAC-1: Notification service sends webhook to `SLACK_WEBHOOK_URL` within 30 seconds of trigger
- SAC-2: Approval gate notifications include: run_id, document_type, agent_id, confidence_score, dashboard deep link
- SAC-3: Critical alerts include: alert type, affected agent/resource, timestamp, suggested action
- SAC-4: Notification dispatch logged in `audit_events` with action `notification.slack`

**Priority:** should | **Story Points:** 2 | **Epic:** E-005 | **Features:** F-029

---

## 12. Parking Lot

Deferred items for future consideration beyond the current release scope.

| ID | Item | Rationale for Deferral | Target Release |
|---|---|---|---|
| PL-001 | Multi-tenant isolation (separate agent registries per organization) | Adds significant complexity to data model and RBAC; not needed for single-team MVP | v2.0 |
| PL-002 | Custom agent authoring UI (visual agent builder in Dashboard) | Agents are currently authored via YAML manifests by platform engineers; visual builder is a future productivity enhancement | v2.0 |
| PL-003 | Agent marketplace (share and discover agents across teams) | Requires multi-tenancy (PL-001) and agent packaging standards; premature without broader adoption | v3.0 |
| PL-004 | Real-time collaborative document editing (Google Docs-style review) | Current approval gate provides review capability; real-time collaboration adds significant infrastructure requirements | v2.0 |
| PL-005 | Fine-tuned models for domain-specific agents | Requires training data pipeline, model hosting infrastructure, and evaluation framework; current prompt engineering approach is sufficient for MVP | v3.0 |

---

## 13. Glossary

| Term | Definition |
|---|---|
| **Agent** | A specialized AI component that performs a specific SDLC task (e.g., document generation, cost tracking, quality evaluation). Each agent has a manifest, prompt template, and maturity tier. |
| **Agent Manifest** | A YAML configuration file (`agents/{agent_id}/manifest.yaml`) that declares an agent's capabilities, supported providers, data access requirements, and tools. |
| **Approval Gate** | A configurable point in the pipeline where execution pauses for human review. Behavior depends on agent maturity tier and confidence score. |
| **Canary Deployment** | A deployment strategy where a new agent version receives a configurable percentage of traffic alongside the active version, enabling safe rollout. |
| **Confidence Score** | A 0.0-1.0 score assigned by an agent to its own output, indicating the agent's self-assessed certainty about output quality. |
| **G1-cost-tracker** | The GOVERN phase agent responsible for recording LLM API costs and enforcing budget ceilings. |
| **G2-audit-trail-validator** | The GOVERN phase agent responsible for verifying audit trail completeness and detecting gaps. |
| **G3-agent-lifecycle-manager** | The GOVERN phase agent responsible for health checks, version management, and maturity progression. |
| **G4-team-orchestrator** | The GOVERN phase agent responsible for pipeline orchestration, agent assignment, and workflow coordination. |
| **G5-quality-gate-enforcer** | The GOVERN phase agent responsible for evaluating document quality and managing approval gates. |
| **Hard Stop** | An enforcement mechanism where G1-cost-tracker immediately halts agent execution when a budget ceiling is reached. |
| **Maturity Tier** | A trust level assigned to an agent: T0 (apprentice), T1 (journeyman), T2 (senior), T3 (expert). Higher tiers have more autonomy and higher budget limits. |
| **MCP (Model Context Protocol)** | The protocol used by AI clients (Claude Code, Cursor) to invoke platform tools programmatically. Three MCP servers: agents-server, governance-server, knowledge-server. |
| **Override Rate** | The percentage of an agent's outputs that were rejected or modified by human reviewers. Used as a factor in maturity progression decisions. |
| **Pipeline Run** | A single execution of the document generation pipeline, producing up to 24 documents from a project brief. Tracked in `pipeline_runs` table. |
| **Pipeline Step** | A single document generation task within a pipeline run, assigned to one agent. Tracked in `pipeline_steps` table. |
| **Project Brief** | The input document provided by a user to initiate a pipeline run. Contains project description, requirements, constraints, and context. |
| **Quality Score** | A 0.0-1.0 score computed by G5-quality-gate-enforcer based on document completeness, consistency, and adherence to schema. |
| **Session Context** | Shared state maintained across agents within a single pipeline run to ensure cross-document consistency. Stored in `session_context` table. |
| **Shared Service Layer** | The application layer containing all business logic. MCP tool handlers and REST route handlers delegate to shared service methods. |
