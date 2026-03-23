# Product Requirements Document: Agentic SDLC Platform

| Field            | Value                                      |
| ---------------- | ------------------------------------------ |
| Document ID      | PRD-ASDLC-001                              |
| Version          | 1.0.0                                      |
| Status           | Draft                                      |
| Owner            | Platform Engineering                       |
| Last Updated     | 2026-03-23                                 |
| Target Release   | v1.0.0                                     |
| Tech Stack       | Python 3.12, Claude Agent SDK, PostgreSQL, asyncio, aiohttp, Streamlit |

---

## 1. Problem Statement

Software delivery teams across mid-to-large organizations spend 40-60% of their engineering hours on repetitive, context-heavy SDLC tasks: writing requirements documents, reviewing code for compliance, executing test plans, orchestrating deployments, tracking spend against budgets, and generating audit trails. Each of these tasks demands deep domain context, yet the humans performing them must constantly context-switch between tools, codebases, and stakeholder expectations, leading to inconsistent output quality, missed compliance requirements, cost overruns that go undetected until month-end reconciliation, and delivery timelines that slip by weeks. Platform engineers lack a unified control plane for managing AI-assisted automation across the full lifecycle; delivery leads cannot produce a coherent set of engagement documents without days of manual effort; engineering leads have no systematic way to enforce quality gates; DevOps engineers fight alert fatigue without intelligent triage; and compliance officers must manually reconstruct audit trails from scattered logs. The cumulative cost is slower delivery, lower quality, higher risk, and wasted engineering talent on work that machines should handle.

---

## 2. Success Metrics

| ID   | Metric                                    | Target                          | Verification Method                                                    |
| ---- | ----------------------------------------- | ------------------------------- | ---------------------------------------------------------------------- |
| SM-1 | Document pipeline end-to-end time         | < 30 minutes for 12 documents  | Timestamp delta between pipeline trigger and final document commit      |
| SM-2 | Document pipeline cost per run            | <= $25                          | Sum of `cost_usd` in `audit_events` table filtered by pipeline run ID  |
| SM-3 | Agent test coverage                       | >= 90% line coverage            | `pytest --cov` report across all agent modules                         |
| SM-4 | Agent quality score (rubric-based)        | >= 8.0 / 10.0 average          | Automated rubric evaluation on golden test outputs per agent           |
| SM-5 | Fleet daily cost                          | <= $50/day                      | Daily aggregation query on `audit_events.cost_usd` grouped by date     |
| SM-6 | Approval gate response time               | < 15 minutes (P95)             | Timestamp delta between gate notification sent and human response       |
| SM-7 | Agent dry-run pass rate                   | 100% (48/48 agents)            | CI pipeline `agent dry-run --all` exit code                            |
| SM-8 | Mean time to pipeline recovery (MTTR)     | < 5 minutes                    | Checkpoint resume timestamp minus failure timestamp in pipeline logs    |
| SM-9 | Audit trail completeness                  | 100% of invocations logged     | Count of invocations vs. count of `audit_events` rows; ratio must be 1 |
| SM-10| PII detection recall                      | >= 95%                          | Precision/recall on labeled PII test corpus                            |

---

## 3. Personas

### 3.1 Priya Mehta — Platform Engineer

| Attribute        | Detail                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Role             | Senior Platform Engineer                                                                    |
| Experience       | 7 years in infrastructure and developer tooling; 2 years with LLM-based systems             |
| Daily Workflow   | Writes and maintains agent code, reviews manifests, runs integration tests, debugs pipeline failures, deploys new agent versions via canary slots |
| Goals            | Ship reliable agents quickly; maintain a clean, extensible agent framework; keep all 48 agents passing dry-run and golden tests |
| Frustrations     | Manifest drift between code and config; no unified way to test agents without burning API credits; debugging agent failures requires reading raw JSONL logs |
| Tech Comfort     | Expert — writes Python daily, comfortable with asyncio, PostgreSQL, CI/CD pipelines          |

### 3.2 David Chen — Delivery Lead

| Attribute        | Detail                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Role             | Delivery Lead, Professional Services                                                        |
| Experience       | 10 years in consulting delivery; 1 year using AI-assisted tooling                            |
| Daily Workflow   | Receives client briefs, kicks off document generation pipelines, reviews generated PRDs and roadmaps, presents deliverables to clients, tracks project budgets |
| Goals            | Produce a complete, high-quality set of 12 engagement documents from a single brief in under an hour; keep pipeline cost under $25 per run |
| Frustrations     | Manually assembling documents takes 2-3 days; inconsistency between documents (e.g., backlog items that don't trace to PRD capabilities); no visibility into pipeline progress while it runs |
| Tech Comfort     | Intermediate — uses CLI tools and Streamlit dashboards but does not write code                |

### 3.3 Sarah Kim — Engineering Lead

| Attribute        | Detail                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Role             | Engineering Lead                                                                            |
| Experience       | 12 years in software engineering; leads a team of 8 engineers                                |
| Daily Workflow   | Reviews pull requests, approves architecture decisions, participates in approval gates for agent-generated outputs, sets quality standards for the team |
| Goals            | Ensure agent outputs meet the same quality bar as human-authored work; reduce review burden by trusting agent outputs that pass quality thresholds; maintain traceability from requirements to tests |
| Frustrations     | Reviewing AI-generated code without context on what the agent was told to do; no rubric-based scoring to pre-filter low-quality outputs before they reach her; approval gate notifications buried in email |
| Tech Comfort     | Advanced — reads and writes code daily, comfortable with architecture diagrams and data models |

### 3.4 Marcus Johnson — DevOps Engineer

| Attribute        | Detail                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Role             | Senior DevOps Engineer                                                                      |
| Experience       | 6 years in SRE/DevOps; 1 year managing AI agent infrastructure                              |
| Daily Workflow   | Monitors fleet health dashboards, responds to cost alerts, manages agent deployment slots, investigates pipeline failures, handles incident escalations |
| Goals            | Keep the agent fleet running within budget; detect and resolve failures before they cascade; maintain zero-downtime deployments for agent version updates |
| Frustrations     | Cost spikes are invisible until the daily report; no canary mechanism to safely roll out new agent versions; pipeline failures produce cryptic error messages |
| Tech Comfort     | Advanced — manages infrastructure as code, writes deployment scripts, comfortable with observability stacks |

### 3.5 Lisa Patel — Compliance Officer

| Attribute        | Detail                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------- |
| Role             | Compliance & Risk Officer                                                                   |
| Experience       | 9 years in regulatory compliance; 3 years overseeing AI governance                           |
| Daily Workflow   | Reviews audit logs for agent decisions, validates PII handling, generates compliance reports, audits cost allocation per client, verifies that approval gates were respected |
| Goals            | Prove that every agent action is traceable and auditable; ensure PII is detected and handled per policy; confirm budget guardrails were never bypassed |
| Frustrations     | Audit trails are spread across multiple log files; no immutable record of agent decisions; PII detection is inconsistent; cost reports require manual SQL queries |
| Tech Comfort     | Basic-to-intermediate — uses dashboards and reports; can write simple SQL but prefers pre-built views |

---

## 4. Core User Journeys

### 4.1 Journey: Generate Engagement Documents from Client Brief

**Persona:** David Chen (Delivery Lead)
**Trigger:** David receives a new client brief via email and needs to produce the full 12-document engagement package.

| Step | Action                                                                                         |
| ---- | ---------------------------------------------------------------------------------------------- |
| 1    | David opens the Streamlit dashboard and navigates to "New Pipeline Run."                       |
| 2    | David pastes the client brief text into the input field and selects "12-Document Pipeline."    |
| 3    | David sets the project budget ceiling to $25 and clicks "Start Pipeline."                      |
| 4    | The system validates the brief (minimum length, required fields) and creates a pipeline run.   |
| 5    | Agents execute sequentially and in parallel per the DAG: Roadmap, then CLAUDE.md, then PRD, then Feature Catalog, then Backlog, then Architecture, then Data Model + API Contracts in parallel, then Enforcement Scaffold, then Quality Spec + Test Strategy in parallel, then Design Spec. |
| 6    | At the Architecture approval gate, the system sends a Slack notification to Sarah Kim.         |
| 7    | Sarah reviews and approves. The pipeline resumes.                                              |
| 8    | David monitors progress on the dashboard: completed steps are green, active steps pulse blue.  |
| 9    | All 12 documents are generated and committed to the project repository.                        |
| 10   | David reviews the document set on the dashboard, downloads the bundle, and shares with client. |

**Success:** All 12 documents generated, total cost <= $25, elapsed time < 30 minutes, all documents pass rubric scoring >= 8.0/10.
**Failure:** Pipeline halts mid-run with no checkpoint to resume; cost exceeds $25; any document scores below 6.0/10 on rubric.

---

### 4.2 Journey: Deploy a New Agent Version via Canary

**Persona:** Priya Mehta (Platform Engineer)
**Trigger:** Priya has finished developing v1.2 of the `code-review-agent` and wants to deploy it safely.

| Step | Action                                                                                         |
| ---- | ---------------------------------------------------------------------------------------------- |
| 1    | Priya runs `agent deploy code-review-agent --version 1.2 --slot canary --traffic 10%`.        |
| 2    | The system creates a canary version slot alongside the current production slot (v1.1).         |
| 3    | 10% of incoming code-review requests are routed to v1.2; 90% continue to v1.1.                |
| 4    | Priya monitors the canary dashboard: quality scores, latency, error rate, cost per invocation. |
| 5    | After 50 invocations with no quality regression (score delta < 0.5), Priya promotes to 100%.  |
| 6    | The system shifts all traffic to v1.2 and archives the v1.1 slot.                             |
| 7    | The deployment event is recorded in the audit trail with before/after version metadata.        |

**Success:** v1.2 deployed to 100% traffic with zero quality regression and no downtime.
**Failure:** Canary detects quality regression; system auto-rolls back to v1.1 and alerts Priya.

---

### 4.3 Journey: Investigate a Cost Spike

**Persona:** Marcus Johnson (DevOps Engineer)
**Trigger:** Marcus receives a Slack alert: "Fleet daily spend at 80% of $50 ceiling at 2:00 PM."

| Step | Action                                                                                         |
| ---- | ---------------------------------------------------------------------------------------------- |
| 1    | Marcus opens the Streamlit cost dashboard and sees spend at $40 by 2:00 PM (normal is ~$25).   |
| 2    | Marcus drills into the cost breakdown by project and identifies Project "Acme-Redesign" at $18. |
| 3    | Marcus drills further into Acme-Redesign and sees the `architecture-agent` has consumed $12.   |
| 4    | Marcus views the agent's recent invocations and finds a retry loop: 8 invocations in 10 min.   |
| 5    | Marcus pauses the agent via `agent pause architecture-agent --project acme-redesign`.          |
| 6    | Marcus inspects the audit log and finds the agent was retrying due to a malformed input.       |
| 7    | Marcus fixes the input, resumes the agent, and verifies the next invocation succeeds.          |
| 8    | Marcus sets a per-agent alert threshold of $8/day for architecture-agent to catch this earlier. |

**Success:** Cost spike root-caused and resolved within 15 minutes; no budget ceiling breached.
**Failure:** Fleet ceiling reached before Marcus can intervene; all agents blocked until next day.

---

### 4.4 Journey: Audit Agent Behavior for Compliance

**Persona:** Lisa Patel (Compliance Officer)
**Trigger:** Quarterly compliance review requires Lisa to verify that all agent actions on client data are auditable and PII-free.

| Step | Action                                                                                         |
| ---- | ---------------------------------------------------------------------------------------------- |
| 1    | Lisa opens the Streamlit audit dashboard and selects the date range for Q1 2026.               |
| 2    | Lisa filters by project "FinServ-Onboarding" and views the audit event timeline.               |
| 3    | Lisa verifies that every agent invocation has a corresponding 13-field audit record.           |
| 4    | Lisa runs the PII detection report and confirms zero PII leaks in agent outputs.               |
| 5    | Lisa checks that all approval gates were respected: no T2/T3 actions executed without approval.|
| 6    | Lisa exports the audit report as PDF for the compliance filing.                                |
| 7    | Lisa flags one anomaly: an agent invocation missing a `project_id` field. She opens a ticket.  |

**Success:** 100% audit coverage confirmed; zero PII leaks; all gates respected; report exported.
**Failure:** Missing audit records; PII detected in outputs; approval gates bypassed.

---

### 4.5 Journey: Resume a Failed Pipeline from Checkpoint

**Persona:** David Chen (Delivery Lead), assisted by Priya Mehta (Platform Engineer)
**Trigger:** David's document pipeline failed at step 6 (Architecture generation) due to a transient API timeout.

| Step | Action                                                                                         |
| ---- | ---------------------------------------------------------------------------------------------- |
| 1    | David sees the pipeline status turn red on the dashboard at step 6.                            |
| 2    | David clicks "View Failure Details" and sees "API timeout after 3 retries."                    |
| 3    | David clicks "Resume from Checkpoint." The system reloads state from step 5 checkpoint.        |
| 4    | The pipeline re-executes step 6 (Architecture) without re-running steps 1-5.                  |
| 5    | Step 6 succeeds. The pipeline continues through steps 7-12.                                    |
| 6    | David verifies all 12 documents are complete. Total cost includes both attempts but stays < $25.|

**Success:** Pipeline resumed without re-running completed steps; total cost within budget; no data loss.
**Failure:** Checkpoint corrupted; pipeline must restart from step 1; cost doubles.

---

## 5. Capabilities

### C1: Agent Orchestration

The platform orchestrates 48 specialized AI agents across 7 SDLC phases: GOVERN, DESIGN, BUILD, TEST, DEPLOY, OPERATE, and OVERSIGHT. Orchestration operates at five hierarchical levels -- agent loop (single agent execution), subagent (agent delegates to child agents), pipeline (DAG of agents with checkpoints), team (cross-functional agent groups), and fleet (all agents across all projects). Each level has its own scheduling, error handling, and resource allocation logic, enabling fine-grained control from individual invocations up to organization-wide fleet management.

### C2: 12-Document Generation Pipeline

From a single client brief, the platform produces 12 interconnected deliverables in a defined DAG order: Roadmap, CLAUDE.md, PRD, Feature Catalog, Backlog, Architecture, Data Model and API Contracts (parallel), Enforcement Scaffold, Quality Spec and Test Strategy (parallel), and Design Spec. Each document is generated by a dedicated agent that receives upstream documents as context, ensuring cross-document consistency. The entire pipeline enforces a $25 cost ceiling and targets completion in under 30 minutes.

### C3: Cost Control and Governance

Real-time budget enforcement operates at four hierarchical levels: fleet ($50/day), project ($20/day), agent ($5/day), and invocation ($0.50). Every API call is metered before execution; if the projected cost would breach a ceiling, the invocation is blocked. The system implements a fail-safe design: if the cost-tracking database is unreachable, all invocations are blocked rather than allowed to proceed unmetered. Cost data is surfaced through dashboards with configurable alert thresholds.

### C4: Human-in-the-Loop

Configurable approval gates are embedded in pipelines at critical decision points (e.g., architecture review, deployment approval). The platform supports four autonomy tiers: T0 (fully autonomous, no approval needed), T1 (log-only, human notified post-execution), T2 (approval required before execution), and T3 (human must co-execute). Notifications are delivered via Slack integration with configurable escalation paths and timeout policies.

### C5: Quality Assurance

Every agent has a suite of golden tests (expected outputs for known inputs) and adversarial tests (malformed inputs, edge cases, prompt injections). Agent outputs are evaluated against rubric-based quality scoring with a minimum threshold of 8.0/10. The platform enforces a minimum of 90% line coverage across all agent modules. Quality scores are tracked over time per agent version, enabling regression detection during canary deployments.

### C6: Observability and Audit

Every agent invocation produces a 13-field JSONL audit record written to an immutable `audit_events` PostgreSQL table. Fields include timestamp, agent ID, agent version, project ID, invocation ID, input hash, output hash, cost in USD, latency in milliseconds, quality score, autonomy tier, approval status, and error details. PII detection runs on all agent inputs and outputs, flagging any personally identifiable information before it is persisted. Cost tracking, quality trends, and fleet health are surfaced through Streamlit dashboards.

### C7: Knowledge Management

The platform implements a three-tier knowledge base: client-specific knowledge (engagement context, preferences, prior decisions), stack-specific knowledge (technology patterns, framework idioms), and universal knowledge (cross-cutting best practices). An exception flywheel promotes learnings upward: a fix discovered for one client engagement can be promoted to the stack tier and eventually to the universal tier. Agents consult the knowledge base during execution to avoid repeating known mistakes and to apply established patterns.

### C8: Pipeline Resilience

Pipelines execute as directed acyclic graphs (DAGs) with checkpoint/resume capability at every node. When a step fails, the system performs automatic retry with exponential backoff. If retries are exhausted, the pipeline pauses at the failed step and preserves all upstream state, allowing resume without re-execution. Self-healing logic detects common failure modes (e.g., test failures) and triggers targeted auto-fix agents before retrying. Parallel branches in the DAG execute concurrently to minimize total pipeline latency.

### C9: Agent Lifecycle

Each agent progresses through a maturity model: apprentice (limited autonomy, all outputs reviewed), professional (standard autonomy, sampled review), and expert (high autonomy, exception-only review). Deployment uses version slots with canary support: a new agent version receives a configurable percentage of traffic while metrics are compared against the incumbent version. Promotion to full traffic requires no quality regression. Rollback is automatic if the canary exceeds error or quality thresholds.

### C10: Multi-Project Isolation

The platform supports concurrent projects with strict namespace isolation. Each project has its own budget allocation, knowledge base partition, pipeline state, and audit trail. Per-client profiles store engagement-specific configuration (autonomy tier overrides, approval gate assignments, notification preferences). Resource isolation ensures that a cost spike or failure in one project cannot affect another project's execution or budget.

---

## 6. Explicit Out of Scope

The following items are deliberately excluded from the v1.0.0 release of the Agentic SDLC Platform:

| ID    | Exclusion                                      | Rationale                                                                 |
| ----- | ---------------------------------------------- | ------------------------------------------------------------------------- |
| OOS-1 | End-user-facing UI beyond Streamlit dashboards | A production frontend (React, etc.) is a future initiative; Streamlit suffices for internal users in v1. |
| OOS-2 | Multi-LLM provider support                     | All agents use Claude via Claude Agent SDK. Supporting OpenAI, Gemini, or other providers is deferred to v2. |
| OOS-3 | Self-hosted LLM inference                      | The platform calls the Anthropic API. On-premise or self-hosted model serving is out of scope. |
| OOS-4 | Natural language chat interface to the platform | Users interact via CLI, Streamlit dashboards, and Slack notifications, not a conversational chatbot. |
| OOS-5 | Automated client brief intake from email        | Briefs are manually pasted into the pipeline trigger UI. Email parsing and auto-intake are deferred. |
| OOS-6 | Fine-tuning or training of foundation models   | Agents use prompting and in-context learning only. No model fine-tuning is performed. |
| OOS-7 | Mobile application                             | All interfaces are desktop/browser-based. A mobile app is not planned.    |
| OOS-8 | Real-time collaborative editing of documents   | Generated documents are committed to a repository. Google Docs-style collaboration is not supported. |
| OOS-9 | Integration with third-party project management tools (Jira, Asana, Linear) | The platform generates documents and backlogs internally. Export to external PM tools is deferred to v2. |
| OOS-10| Agent marketplace or plugin system             | All 48 agents are built and maintained by the platform team. Third-party agent contribution is not supported in v1. |
| OOS-11| Automated billing or charge-back to clients    | Cost tracking is for internal governance. Client invoicing integration is out of scope. |
| OOS-12| Disaster recovery and multi-region deployment  | The platform runs in a single region. HA/DR across regions is a future infrastructure initiative. |

---

*End of document.*
