# BRD — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-29
**Document:** 00 of 24 | Status: Draft

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Case](#2-business-case)
3. [Stakeholder Map](#3-stakeholder-map)
4. [Current State Analysis](#4-current-state-analysis)
5. [Business Requirements](#5-business-requirements)
6. [Constraints](#6-constraints)
7. [Data Inventory](#7-data-inventory)
8. [Integration Points](#8-integration-points)
9. [Success Criteria](#9-success-criteria)
10. [Open Questions](#10-open-questions)

---

## 1. Executive Summary

The Agentic SDLC Platform is an AI agent control plane that orchestrates 48 specialized agents across 7 software development lifecycle phases: GOVERN, DESIGN, BUILD, TEST, DEPLOY, OPERATE, and OVERSIGHT. The platform automates the generation of a 24-document SDLC specification stack (previously 12 documents, expanded to the full 24-doc suite) from a single project brief, enforces cost governance with hard budget ceilings, maintains immutable audit trails for every agent invocation, and provides both programmatic (MCP) and visual (Streamlit Dashboard) interfaces for operators.

The platform addresses a critical industry problem: 30-40% of development budgets are lost to rework caused by inconsistent specifications, context gaps between lifecycle phases, and manual handoffs that introduce errors. By replacing manual document generation with AI-orchestrated pipelines governed by cost controls and human approval gates, the platform targets a 60% reduction in specification-related rework costs and a 10x reduction in document generation time (from 2-3 days to under 30 minutes per full pipeline run).

---

## 2. Business Case

### 2.1 Problem Quantification

| Problem Area | Current Cost | Evidence |
|---|---|---|
| Manual document authoring | 2-4 hours per document, 12 documents per engagement = 24-48 person-hours | Internal time tracking data across 40+ client engagements |
| Specification rework | 30-40% of dev budgets lost to rework from inconsistent specs | Industry benchmarks (Capers Jones, DORA reports) |
| Context-switching overhead | Engineers switch tools 5-8 times per SDLC task, losing 20-30 min per switch | Developer experience surveys (2025 internal) |
| Late compliance discovery | Compliance gaps found during audits, not during development | Post-mortem analysis of 12 audit findings in 2025 |
| Cost visibility lag | LLM spend visible only at month-end reconciliation | Finance team reports showing 15-25% budget overruns detected late |

### 2.2 Proposed Solution Value

| Benefit | Projected Impact | Measurement Method |
|---|---|---|
| Automated specification generation | 10x faster (24-48 hours reduced to <30 min) | Pipeline completion time metrics in `pipeline_runs` table |
| Reduced rework costs | 60% reduction in specification-related rework | Pre/post deployment defect tracking comparison |
| Real-time cost governance | Zero budget overruns via hard-stop enforcement at $45 ceiling | G1-cost-tracker enforcement logs in `cost_metrics` |
| Continuous compliance | 100% audit trail completeness within 5s of each invocation | `audit_events` reconciliation vs `agent_invocations` |
| Consistent quality | Agent-generated documents pass quality gates >95% of the time | `pipeline_steps.quality_score` analysis |

### 2.3 ROI Projection

| Metric | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Development cost savings | $180,000 | $320,000 | $450,000 |
| Rework reduction savings | $240,000 | $420,000 | $580,000 |
| Platform operating cost (LLM + infra) | -$95,000 | -$110,000 | -$120,000 |
| Net benefit | $325,000 | $630,000 | $910,000 |
| Cumulative ROI | 185% | 380% | 550% |

---

## 3. Stakeholder Map

| Stakeholder | Role | Responsibility | Primary Interface | Decision Authority |
|---|---|---|---|---|
| Priya Sharma | Platform Engineer | Builds, deploys, and maintains the agent platform. Writes agent manifests, debugs orchestration pipelines, monitors cost budgets. | MCP via Claude Code | Technical implementation decisions |
| Marcus Chen | Delivery Lead | Triggers pipeline runs for client engagements, reviews generated documents, manages document quality. | MCP via Claude Code | Pipeline configuration, document acceptance |
| Anika Patel | Engineering Lead | Reviews agent-generated outputs at approval gates, manages agent maturity progression, sets quality standards. | Streamlit Dashboard | Approval/rejection at quality gates, autonomy tier decisions |
| David Okonkwo | DevOps Engineer | Monitors fleet health, manages agent deployments, handles incidents and rollbacks. | Streamlit Dashboard | Deployment decisions, incident response |
| Fatima Al-Rashidi | Compliance Officer | Audits agent behavior, verifies governance policies, produces compliance reports. | Streamlit Dashboard | Compliance sign-off, policy enforcement |
| Platform Team | Owner | End-to-end platform ownership, roadmap prioritization, architectural decisions. | All interfaces | Strategic direction, budget allocation |
| Engineering Leads | Decision-Maker | Evaluate platform capabilities against team needs, approve adoption. | Dashboard + MCP | Adoption decisions, resource allocation |
| DevOps Team | Subject Matter Expert | Advise on infrastructure requirements, CI/CD integration, observability. | Dashboard | Infrastructure recommendations |
| Developers | End Users | Consume generated documents, provide feedback on quality, use MCP tools in IDE. | MCP via IDE | Feature requests, quality feedback |

---

## 4. Current State Analysis

### 4.1 Current SDLC Process

| Phase | Current Approach | Pain Points |
|---|---|---|
| Requirements | Manual PRD authoring in Google Docs or Confluence | 4-8 hours per document, quality varies by author, no version linkage |
| Architecture | Architecture diagrams drawn manually, reviewed in meetings | Diagrams go stale within weeks, no automated consistency checks |
| Design | UI/UX specs created in Figma, API specs in separate tools | Interface divergence between MCP/REST/Dashboard discovered late |
| Implementation | Developers interpret specs manually | Context lost between spec and code, leading to 30% rework |
| Testing | Test strategies written after implementation begins | Insufficient coverage, tests don't trace back to requirements |
| Deployment | Manual deployment checklists | Configuration drift, 3 pipeline interruptions per quarter |
| Compliance | Quarterly audit assembles data from 3+ databases manually | 10+ hours per audit report, gaps discovered post-facto |

### 4.2 Current Agent Landscape

- **No orchestration layer:** Individual AI tools (ChatGPT, Claude) used ad-hoc by team members
- **No cost tracking:** LLM API costs discovered at month-end billing reconciliation
- **No audit trail:** No record of which AI tool generated which output, with what inputs
- **No governance:** No budget ceilings, no approval gates, no maturity progression
- **No agent registry:** No inventory of which AI capabilities are available or their health status

### 4.3 Target State

The Agentic SDLC Platform replaces the manual, uncoordinated approach with a governed, orchestrated system:

- **48 agents** organized into 7 SDLC phase teams (GOVERN, DESIGN, BUILD, TEST, DEPLOY, OPERATE, OVERSIGHT)
- **Automated pipeline** generates 24 specification documents from a single project brief
- **Cost governance** with per-agent, per-project, and per-run budget enforcement
- **Immutable audit trail** for every agent invocation with 13-field JSONL records
- **Three equal interfaces:** MCP (programmatic), REST API (integration), Streamlit Dashboard (visual)
- **Human approval gates** at configurable points with structured feedback
- **Agent maturity progression** from apprentice (T0) to expert (T3) based on performance

---

## 5. Business Requirements

### BR-001: Automated Document Generation Pipeline

**Priority:** Must
**Description:** The platform SHALL provide an automated pipeline that generates a complete 24-document SDLC specification stack from a single project brief input, with each document assigned to a specialized agent.
**Rationale:** Manual document generation consumes 24-48 person-hours per engagement. Automation reduces this to <30 minutes of pipeline execution plus human review time.
**Acceptance Criteria:**
- A `trigger_pipeline` MCP tool call initiates end-to-end generation
- Pipeline produces all 24 documents with status tracking per step in `pipeline_steps`
- Each document passes a quality score threshold (configurable, default 0.7)
- Pipeline supports checkpoint/resume via `pipeline_checkpoints` table
**Traceability:** PRD C2, Feature F-001

---

### BR-002: Agent Orchestration and Lifecycle Management

**Priority:** Must
**Description:** The platform SHALL maintain a registry of all 48 agents with health monitoring, version management, canary deployments, and maturity-based autonomy progression (T0-apprentice through T3-expert).
**Rationale:** Unmanaged agents create operational risk. A registry with lifecycle management ensures fleet visibility, controlled rollouts, and progressive trust building.
**Acceptance Criteria:**
- `agent_registry` table stores all 48 agents with status, tier, version, and health data
- Health checks run on configurable intervals with circuit breaker protection
- Canary deployment supports traffic splitting between active and canary versions
- Maturity progression from T0 to T3 based on invocation count, quality scores, and override rate
**Traceability:** PRD C1, C3, Features F-008 through F-015

---

### BR-003: Real-Time Cost Governance

**Priority:** Must
**Description:** The platform SHALL track LLM API costs in real-time at agent, project, and pipeline-run levels, enforce configurable budget ceilings with hard-stop capability, and alert operators when budgets approach thresholds.
**Rationale:** LLM API costs are variable and can run away without controls. Real-time tracking with hard stops prevents budget overruns.
**Acceptance Criteria:**
- G1-cost-tracker records every LLM API call cost in `cost_metrics` within 2 seconds
- Budget ceilings configurable per agent, per project, and per pipeline run
- Hard-stop enforcement halts agent execution when ceiling is reached
- Tracked spend within 2% of actual provider billing (M7)
- Cost burn-down visible via `check_cost` MCP tool and Cost Monitor dashboard page
**Traceability:** PRD C4, M7, M9, Features F-016 through F-021

---

### BR-004: Immutable Audit Trail

**Priority:** Must
**Description:** The platform SHALL produce a complete, immutable 13-field JSONL audit record for every agent invocation within 5 seconds of completion, with no gaps between invocations and audit records.
**Rationale:** Compliance requirements (SOC2, EU AI Act) mandate complete traceability of AI system decisions. Immutable audit trails enable post-facto verification without code access.
**Acceptance Criteria:**
- `audit_events` table is append-only (no UPDATE or DELETE permitted)
- 100% of agent invocations produce audit records (M10)
- Each record includes: timestamp, agent_id, action, project_id, run_id, input_hash, output_hash, cost_usd, token_count, duration_ms, severity, details (JSONB), session_id
- Nightly reconciliation job verifies zero gaps
- Audit records queryable via `query_audit_events` MCP tool and Audit Log dashboard page
**Traceability:** PRD C5, M10, Features F-022 through F-026

---

### BR-005: LLM Provider Agnosticism

**Priority:** Must
**Description:** The platform SHALL support multiple LLM providers (Anthropic Claude, OpenAI GPT, Ollama local models) through a provider abstraction layer, enabling runtime provider selection per agent without code changes.
**Rationale:** Vendor lock-in creates cost risk and limits deployment flexibility. Local models (Ollama) enable air-gapped and cost-sensitive deployments.
**Acceptance Criteria:**
- Provider abstraction layer exposes a uniform interface regardless of underlying provider
- Agent manifests declare supported providers; runtime configuration selects the active provider
- Provider switch requires only configuration change, zero code modification
- All providers pass the same integration test suite (Q-065, Q-066)
- Provider latency and cost tracked per-provider in `cost_metrics`
**Traceability:** PRD C11, Features F-045 through F-048

---

### BR-006: Multi-Interface Parity

**Priority:** Must
**Description:** The platform SHALL expose all capabilities through three equal interfaces -- MCP (programmatic via Claude Code), REST API (integration), and Streamlit Dashboard (visual) -- with behavioral parity ensuring identical business logic outcomes regardless of interface used.
**Rationale:** Full-Stack-First architecture demands that no interface is a second-class citizen. MCP users and Dashboard users must see identical data and trigger identical operations.
**Acceptance Criteria:**
- Every MCP tool has a corresponding REST endpoint (Q-049)
- Dashboard pages consume REST API exclusively (no direct database access)
- Shared Service Layer owns all business logic; interface handlers are thin adapters
- Interface parity tests verify identical responses for matching inputs across MCP and REST
**Traceability:** PRD C6, C7, Q-049 through Q-053

---

### BR-007: Human Approval Gates

**Priority:** Must
**Description:** The platform SHALL support configurable human approval gates in the pipeline where execution pauses until a human reviewer approves or rejects with structured comments, enabling controlled autonomy based on agent maturity tier.
**Rationale:** AI-generated outputs require human oversight, especially during early maturity stages. Approval gates provide quality control without blocking the entire pipeline.
**Acceptance Criteria:**
- Approval gates configurable per pipeline step and per agent maturity tier
- T0-T1 agents require approval at every step; T2-T3 agents can auto-approve below confidence threshold
- Approval requests stored in `approval_requests` table with pending/approved/rejected status
- Reviewers receive Slack notifications and can approve via Dashboard Approval Queue
- Structured rejection comments feed back to agents for re-generation
**Traceability:** PRD C9, Features F-027 through F-031

---

### BR-008: Knowledge Management and Exception Handling

**Priority:** Should
**Description:** The platform SHALL maintain a searchable knowledge base of exceptions, edge cases, and lessons learned that agents can query during generation to improve output quality over time.
**Rationale:** Repeated mistakes and known edge cases should inform future agent behavior. A knowledge base enables organizational learning across pipeline runs.
**Acceptance Criteria:**
- `knowledge_exceptions` table stores categorized exceptions with search capability
- Agents query relevant exceptions during generation via `search_exceptions` MCP tool
- Knowledge entries linked to agent_id, project_id, and document type
- Knowledge base accessible via MCP (knowledge-server) and Dashboard
**Traceability:** PRD C10, Features F-037 through F-041

---

### BR-009: Pipeline Resilience and Recovery

**Priority:** Must
**Description:** The platform SHALL support pipeline checkpoint/resume, automatic retry with exponential backoff, and graceful degradation when individual agents fail, ensuring partial results are preserved.
**Rationale:** Long-running pipelines (24 documents, multiple agents) must tolerate transient failures without requiring full restart from scratch.
**Acceptance Criteria:**
- Pipeline state checkpointed after each successful step in `pipeline_checkpoints`
- Failed steps retry with exponential backoff (configurable max retries, default 3)
- Pipeline continues past non-critical failures, marking affected documents as degraded
- Resume from checkpoint via `resume_pipeline` MCP tool
- Circuit breaker prevents repeated calls to a failing agent or LLM provider
**Traceability:** PRD C8, Features F-005 through F-007

---

### BR-010: Observability and Operational Visibility

**Priority:** Must
**Description:** The platform SHALL provide comprehensive observability through structured logging, distributed tracing, metrics collection, and real-time dashboards covering system health, agent performance, cost burn-down, and audit trail status.
**Rationale:** A platform running 48 autonomous agents requires deep visibility to detect anomalies, debug failures, and maintain operational confidence.
**Acceptance Criteria:**
- Structured JSON logs for all components with correlation IDs
- OpenTelemetry traces spanning MCP call through agent execution through LLM API call
- Prometheus metrics for latency, throughput, error rates, and cost
- Grafana dashboards for system health, agent performance, and cost monitoring
- Fleet Health Overview dashboard page loads in <1 second (M3)
- MCP tools (`check_fleet_health`, `get_cost_report`) provide programmatic access to operational data
**Traceability:** PRD C1, M1, M3, M6, Features F-042 through F-044

---

## 6. Constraints

### 6.1 Budget Constraints

| Constraint | Limit | Rationale |
|---|---|---|
| Per-pipeline-run LLM cost | < $45 USD | Business viability requires predictable per-run costs; $45 ceiling provides headroom above $25 target |
| Monthly infrastructure cost (non-LLM) | < $500 USD | Early-stage platform; infrastructure cost must remain within startup budget |
| Year 1 total platform investment | < $200,000 USD | Approved budget for platform development team and infrastructure |

### 6.2 Timeline Constraints

| Milestone | Target Date | Deliverable |
|---|---|---|
| MVP (12-doc pipeline, basic governance) | 2026-06-30 | Core pipeline, G1-cost-tracker, basic dashboard |
| GA (24-doc pipeline, full governance) | 2026-09-30 | All 48 agents, full audit trail, all dashboard pages |
| EU AI Act compliance | 2026-08-01 | Complete audit trail, risk classification documentation, human oversight gates |

### 6.3 Regulatory Constraints

| Regulation | Applicability | Key Requirements | Deadline |
|---|---|---|---|
| EU AI Act | Mandatory (AI system generating decisions) | Risk classification, human oversight, transparency, audit trail | August 2026 |
| GDPR | Applicable (EU customer data in project briefs) | Data minimization, right to deletion, consent management, DPA | Ongoing |
| SOC2 Type II | Applicable (enterprise customers) | Access controls, audit logging, change management, availability | 2027-Q1 target |

### 6.4 Technical Constraints

| Constraint | Detail |
|---|---|
| Python runtime | Platform implemented in Python 3.11+ (agent SDK, MCP servers, REST API, Dashboard) |
| PostgreSQL 15+ | Primary data store; no alternative RDBMS support planned for v1 |
| MCP protocol compliance | All MCP servers must comply with MCP specification (stdio and streamable-http transports) |
| LLM provider rate limits | Anthropic: 4000 RPM, OpenAI: 3500 RPM, Ollama: local (no rate limit) |

---

## 7. Data Inventory

The platform persists operational data across 10 PostgreSQL tables and supplementary file-based stores. All tables are defined in the DATA-MODEL (Doc 10).

| Table | Description | Growth Rate | Classification | Retention |
|---|---|---|---|---|
| `agent_registry` | Registry of all 48 agents with status, tier, version, health | Slow (48 rows) | Internal | Indefinite |
| `cost_metrics` | Per-invocation LLM cost records | High (100-500/day) | Internal | 90 days |
| `audit_events` | Immutable 13-field audit records | High (200-1000/day) | Confidential | 1 year |
| `pipeline_runs` | Pipeline execution records | Medium (5-10/day) | Internal | 1 year |
| `pipeline_steps` | Per-step execution records within a pipeline run | Medium (70-140/day) | Internal | 1 year |
| `knowledge_exceptions` | Exception cases and lessons learned | Low (10-50/month) | Internal | Indefinite |
| `session_context` | Agent session state during pipeline execution | High (140-280/day) | Confidential | 7 days |
| `approval_requests` | Human approval gate records | Low (5-20/day) | Internal | 1 year |
| `pipeline_checkpoints` | Pipeline checkpoint/resume state | Medium (5-10/day) | Internal | 30 days |
| `mcp_call_events` | MCP tool invocation telemetry | High (200-1000/day) | Internal | 90 days |

### Supplementary Stores

| Store | Technology | Content | Classification |
|---|---|---|---|
| Generated documents | Local filesystem (`reports/{project_id}/{run_id}/`) | Generated specification documents | Confidential |
| Agent manifests | YAML files (`agents/{agent_id}/manifest.yaml`) | Agent configuration and metadata | Internal |
| Structured logs | JSONL files | Audit trail backup, structured log archive | Confidential |
| Rate limiter state | Python in-memory (dict / token buckets) | Ephemeral rate limiting counters | Internal |

---

## 8. Integration Points

| # | System | Protocol | Direction | Data Exchanged | Authentication |
|---|---|---|---|---|---|
| INT-001 | Anthropic Claude API | HTTPS/REST | Outbound | Prompts, completions, token counts, cost | API key (env: `ANTHROPIC_API_KEY`) |
| INT-002 | OpenAI GPT API | HTTPS/REST | Outbound | Prompts, completions, token counts, cost | API key (env: `OPENAI_API_KEY`) |
| INT-003 | Ollama (local) | HTTP/REST | Outbound (localhost) | Prompts, completions, token counts | None (localhost only) |
| INT-004 | PostgreSQL 15+ | TCP/SQL | Bidirectional | All operational data (10 tables) | Connection string (env: `DATABASE_URL`) |
| INT-005 | MCP Protocol (stdio) | stdio | Bidirectional | Tool calls and responses (agents-server, governance-server, knowledge-server) | API key header |
| INT-006 | MCP Protocol (streamable-http) | HTTPS | Bidirectional | Tool calls and responses for remote MCP clients | API key header |
| INT-007 | Slack Webhooks | HTTPS | Outbound | Approval gate notifications, incident alerts | Webhook URL (env: `SLACK_WEBHOOK_URL`) |
| INT-008 | PagerDuty | HTTPS | Outbound | Incident escalation for critical fleet failures | API key (env: `PAGERDUTY_API_KEY`) |
| INT-009 | Prometheus | HTTP | Inbound (scrape) | Metrics endpoint (`/metrics`) | None (internal network) |
| INT-010 | OpenTelemetry Collector | gRPC/HTTP | Outbound | Distributed traces | None (internal network) |

---

## 9. Success Criteria

| # | Criterion | Target | Measurement |
|---|---|---|---|
| SC-001 | Pipeline generates complete document stack | 24 documents per run, >95% completion rate | `pipeline_runs` query: completed runs with `document_count = 24` |
| SC-002 | Pipeline execution time | < 30 minutes end-to-end | `pipeline_runs.completed_at - pipeline_runs.triggered_at` |
| SC-003 | Pipeline cost per run | < $45 USD | `SUM(cost_metrics.cost_usd) WHERE pipeline_run_id = ?` |
| SC-004 | Cost tracking accuracy | Within 2% of actual provider billing | Weekly reconciliation against Anthropic/OpenAI billing dashboards |
| SC-005 | Audit trail completeness | 100% of invocations have audit records | Nightly reconciliation: `COUNT(agent_invocations)` vs `COUNT(audit_events)` |
| SC-006 | MCP tool latency (p95) | < 500ms read, < 2s write | Prometheus histogram `mcp_tool_duration_seconds` |
| SC-007 | Dashboard page load (p95) | < 2s all pages, < 1s Fleet Health | Streamlit performance instrumentation |
| SC-008 | Agent fleet coverage | 48 agents across 7 phases | `agent_registry` count with health check validation |
| SC-009 | Provider portability | Minimum 2 providers pass integration suite | Provider integration test results |
| SC-010 | Approval gate response time | Median < 5 minutes | `approval_requests.resolved_at - approval_requests.pending_at` |

---

## 10. Open Questions

| ID | Question | Owner | Impact | Target Resolution Date |
|---|---|---|---|---|
| OQ-001 | Should the platform support multi-tenant isolation (separate agent registries per team/org) in v1, or defer to v2? | Platform Team | Architecture: multi-tenancy adds complexity to `agent_registry`, `cost_metrics`, and all shared services | 2026-04-15 |
| OQ-002 | What is the maximum acceptable pipeline run duration for the 24-document stack? Current target is 30 minutes; some stakeholders want 15 minutes. | Marcus Chen, Anika Patel | Pipeline architecture: parallelization strategy and LLM concurrency limits | 2026-04-10 |
| OQ-003 | How should the platform handle LLM provider outages mid-pipeline? Current design retries with backoff, but should it auto-failover to an alternate provider? | Priya Sharma | Resilience: auto-failover requires all agents to support multiple providers simultaneously | 2026-04-20 |
| OQ-004 | What data residency requirements apply to project briefs containing customer data? Can they be sent to US-hosted LLM APIs, or do EU customers require EU-region processing? | Fatima Al-Rashidi | Compliance: may require EU-hosted Ollama instances or EU-region API endpoints | 2026-04-15 |
| OQ-005 | Should agent maturity progression be automatic (based on metrics thresholds) or require explicit human promotion? Current design requires human approval via dashboard. | Anika Patel | Governance: automatic promotion reduces overhead but increases risk of premature autonomy | 2026-04-30 |
