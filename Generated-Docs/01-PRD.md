# PRD — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 1 of 14 | Status: Draft

---

## 1. Problem Statement

Software delivery teams spanning platform engineering, delivery management, quality assurance, operations, and compliance spend 60-70% of their capacity on repetitive, context-heavy lifecycle tasks: drafting requirements documents, reviewing outputs for consistency, running test strategies, tracking spend against budgets, orchestrating deployments, and assembling audit trails from scattered logs. These tasks follow predictable patterns yet demand sustained attention and deep domain context, forcing constant context-switching that degrades both speed and quality. Developers working inside AI coding assistants cannot programmatically trigger, monitor, or control these workflows from within their development environment -- they must break flow, switch to browser-based tools, and manually correlate information across disconnected systems. Operators -- engineering leads reviewing deliverables, DevOps engineers monitoring infrastructure health, and compliance officers verifying governance policies -- lack a centralized visual interface to see fleet status at a glance, approve work at critical decision gates, or produce audit-ready reports without querying multiple databases and formatting results by hand. The compounding effect is slower delivery cycles, inconsistent document quality that varies by author and workload, cost overruns discovered only at month-end reconciliation, compliance gaps that surface during audits rather than in real-time, and a widening disconnect between the people who produce work and the people who govern it.

---

## 2. Success Metrics

| # | Metric Name | Target | Verification Method |
|---|------------|--------|-------------------|
| M1 | MCP tool call latency (p95) | < 500ms for read operations; < 2s for write/trigger operations | Automated latency instrumentation on the MCP server endpoint; p95 computed from the `audit_events` table over a rolling 24-hour window; verified weekly via observability dashboard |
| M2 | Pipeline trigger-to-first-output time via MCP | < 30 seconds from `trigger_pipeline` MCP call to the first agent writing output to session store | End-to-end timing recorded in pipeline run metadata (`pipeline_runs.first_output_at - pipeline_runs.triggered_at`); validated by integration test `test_pipeline_trigger_latency` |
| M3 | Dashboard page load time (p95) | < 2 seconds for all pages; < 1 second for the Fleet Health Overview | Streamlit performance instrumentation logging render times per page; synthetic monitoring job hitting each dashboard route every 60 seconds and recording load times |
| M4 | Approval gate median response time (dashboard) | < 5 minutes from gate notification sent to human approval or rejection recorded | Computed as median of (`approval_events.resolved_at - approval_events.pending_at`) over rolling 7-day window; surfaced on the Cost Governance dashboard tab |
| M5 | Cross-interface round-trip time | < 10 minutes end-to-end for MCP trigger through dashboard approval through MCP status confirmation (excluding human think time) | Pipeline run log analysis: delta between MCP `trigger_pipeline` timestamp and MCP `check_pipeline_status` returning `completed`; human wait time tracked separately via `gate_pending_duration` |
| M6 | Agent phase coverage | 48 agents operational across all 7 SDLC phases | Automated manifest validation: `pytest tests/test_agent_registry.py` confirms all 48 manifests load, validate against `agent-manifest.schema.json`, and respond to health checks; run nightly in CI |
| M7 | Cost tracking accuracy | Tracked spend within 2% of actual Claude API billing at fleet, project, and agent levels | Weekly reconciliation job comparing `cost_events` table totals against the Anthropic API billing dashboard; automated alert if delta exceeds 2% at any aggregation level |
| M8 | 12-document pipeline completion rate | > 95% of triggered runs produce all 12 documents without manual intervention | Query: `SELECT COUNT(*) FILTER (WHERE status = 'completed' AND document_count = 12) * 100.0 / COUNT(*) FROM pipeline_runs WHERE triggered_at > now() - interval '30 days'` |
| M9 | Pipeline cost per run | < $25.00 per full 12-document generation run | Real-time cost accumulator in G1-cost-tracker with hard-stop enforcement at $25.00; verified by aggregating `cost_events` per `pipeline_run_id` and alerting on any run exceeding ceiling |
| M10 | Audit trail completeness | 100% of agent invocations produce a complete 13-field JSONL audit record within 5 seconds of invocation completion | Nightly reconciliation comparing `agent_invocations` count against `audit_events` count grouped by date; alert triggered on any delta > 0; spot-checked monthly by compliance officer |

---

## 3. Personas

### Persona 1: Priya Sharma — Platform Engineer

| Attribute | Detail |
|-----------|--------|
| **Role** | Senior Platform Engineer |
| **Experience** | 7 years in infrastructure and developer tooling; 2 years building AI agent systems |
| **Primary Interface** | **MCP via Claude Code** |
| **Tech Comfort** | Very High |
| **Daily Workflow** | Priya spends her entire day inside Claude Code and VS Code, building and maintaining the agent platform. She writes new agent manifests, debugs orchestration pipelines, deploys agent version upgrades via canary slots, and monitors cost budgets. She runs MCP tool calls (`query_agent`, `list_agents`, `check_cost`, `check_fleet_health`) dozens of times daily without leaving her editor. She reviews fleet metrics via MCP before standup every morning and uses MCP to run targeted diagnostic queries when incidents are escalated to her. |
| **Goals** | Ship reliable agent updates with zero downtime. Keep all 48 agents healthy and within budget. Reduce the cycle time for adding a new agent from days to hours. Never have to open a separate browser-based tool just to check if a deployment succeeded or a pipeline is healthy. |
| **Frustrations** | Checking fleet health currently requires switching from her IDE to a browser-based monitoring tool, breaking her development flow. Cost data lives in spreadsheets updated manually by finance, so she never knows the real-time spend. When a pipeline fails at 2 AM, she has no way to query the failure reason from her terminal -- she must SSH into the server and search logs. Deploying a new agent version requires editing 4 configuration files across 3 repositories with no automated validation. |

---

### Persona 2: Marcus Chen — Delivery Lead

| Attribute | Detail |
|-----------|--------|
| **Role** | Delivery Lead, Client Engagements |
| **Experience** | 10 years in software consulting; 3 years leading AI-augmented delivery teams |
| **Primary Interface** | **MCP via Claude Code** |
| **Tech Comfort** | High |
| **Daily Workflow** | Marcus kicks off new client engagements by preparing the 12-document deliverable set. He receives a client brief, refines it in Claude Code, then triggers the document generation pipeline via MCP. He monitors pipeline progress through periodic MCP status checks while working on other tasks in the same editor. He reviews generated documents inline and triggers re-generation of individual documents when requirements change. On a typical day, he runs 2-3 pipeline triggers and reviews 5-8 generated documents. |
| **Goals** | Generate a complete, high-quality 12-document engagement package in under 30 minutes and under $25. Eliminate the 2-3 days currently spent manually writing PRDs, architecture documents, and test strategies for each new engagement. Maintain consistent document quality across all client engagements regardless of which team member runs the pipeline. |
| **Frustrations** | Each document currently takes 2-4 hours to write manually, and the quality varies widely depending on the author's experience and available time. When a document needs revision, all downstream documents become stale but nobody tracks the dependency chain. He has no visibility into how much each document generation costs until the monthly bill arrives. Re-running a single document means re-running the entire pipeline because there is no checkpoint/resume capability. |

---

### Persona 3: Anika Patel — Engineering Lead

| Attribute | Detail |
|-----------|--------|
| **Role** | Engineering Lead, Quality and Architecture |
| **Experience** | 12 years in software engineering; 4 years in engineering management |
| **Primary Interface** | **Dashboard (Streamlit)** |
| **Tech Comfort** | High |
| **Daily Workflow** | Anika reviews agent-generated outputs at approval gates throughout the day. She receives Slack notifications when a pipeline reaches a human review gate, opens the dashboard to inspect the generated document, compares it against input requirements, and approves or rejects with structured comments. She reviews the approval queue first thing each morning and before end of day. She tracks which pipelines are pending her review and which were auto-approved at lower autonomy tiers. She also monitors agent maturity progression to decide when to increase autonomy levels. |
| **Goals** | Approve or reject pipeline outputs within 15 minutes of notification. Maintain quality standards across all agent-generated documents without becoming a bottleneck. Have clear visibility into what the agent produced, what inputs it used, what confidence score it assigned, and what its reasoning chain looked like. Gradually increase agent autonomy as trust is established through consistent quality. |
| **Frustrations** | Reviewing agent outputs currently means downloading files from a shared drive, opening them in separate applications, and manually comparing against requirements in yet another tool. There is no centralized queue of items awaiting her review. She cannot see the agent's confidence score or reasoning chain -- just the final output. When she rejects a document, there is no structured feedback mechanism; she sends an email that may or may not be acted upon, and the revision often misses her original point. |

---

### Persona 4: David Okonkwo — DevOps Engineer

| Attribute | Detail |
|-----------|--------|
| **Role** | Senior DevOps Engineer |
| **Experience** | 8 years in operations and site reliability; 1 year managing AI agent infrastructure |
| **Primary Interface** | **Dashboard (Streamlit)** |
| **Tech Comfort** | Very High |
| **Daily Workflow** | David monitors the agent fleet's operational health on a 2-hour check cycle. He starts with the fleet health dashboard to scan for anomalies: agents consuming excessive tokens, pipeline failure rate spikes, cost budgets approaching limits. He manages agent deployments -- promoting canary slots to primary, rolling back failed versions. When incidents occur (agent stuck in a loop, cost runaway, pipeline deadlock), he triages from the dashboard's real-time views and takes corrective action. He occasionally drops into MCP via his terminal for targeted diagnostic queries during complex incidents. |
| **Goals** | Detect and resolve fleet issues within 15 minutes. Keep fleet uptime above 99.5%. Ensure no agent or project exceeds its cost budget. Perform agent version deployments with zero pipeline disruption. Have a single pane of glass that shows fleet health at a glance instead of checking 5 separate systems. |
| **Frustrations** | Fleet monitoring currently requires checking application logs, cost spreadsheets, deployment manifests, health check endpoints, and a custom aggregation script -- 5 separate systems with no unified view. Cost alerts arrive via email 30 minutes after the budget was already exceeded. Agent deployments are manual and have caused 3 pipeline interruptions in the last quarter due to configuration drift. There is no rollback mechanism; fixing a bad deployment means manually reverting files. |

---

### Persona 5: Fatima Al-Rashidi — Compliance Officer

| Attribute | Detail |
|-----------|--------|
| **Role** | Compliance and Data Governance Officer |
| **Experience** | 6 years in regulatory compliance; 2 years overseeing AI system governance |
| **Primary Interface** | **Dashboard (Streamlit)** |
| **Tech Comfort** | Medium |
| **Daily Workflow** | Fatima conducts weekly audits of agent behavior, reviewing cost reports, PII detection logs, and agent decision trails. She generates compliance reports for monthly governance board reviews. She spot-checks specific pipeline runs to verify that human approval gates were respected and agents did not exceed their declared autonomy tiers. She reviews the audit log for anomalies: unusual cost spikes, rejected gates that were later bypassed, or agents accessing data outside their declared data inventory. |
| **Goals** | Produce audit-ready compliance reports in under 10 minutes. Verify that every agent invocation has a complete, immutable audit trail. Confirm that PII scanning caught all sensitive data before persistence. Ensure cost governance policies are enforced consistently -- no agent should ever operate without budget limits. Have confidence in the data without needing to read source code. |
| **Frustrations** | Assembling an audit trail currently requires querying 3 separate databases, correlating timestamps manually, and formatting results in a spreadsheet. PII detection is an afterthought -- she discovers leaks during audits, not in real-time. Cost reports produced monthly by finance contain discrepancies she cannot trace to root cause. She has no way to verify that an agent's declared data inventory matches its actual data access patterns without reading code, which she is not comfortable doing. |

---

### Persona 6: Jason Torres — Full-Stack Tech Lead

| Attribute | Detail |
|-----------|--------|
| **Role** | Tech Lead, Agent Development and Operations |
| **Experience** | 9 years in full-stack engineering; 3 years leading AI platform teams |
| **Primary Interface** | **Both MCP and Dashboard** |
| **Tech Comfort** | Very High |
| **Daily Workflow** | Jason bridges the developer and operator worlds. In the morning, he reviews fleet health and the approval queue on the dashboard. During development hours, he works in Claude Code -- triggering test pipelines via MCP, querying agent outputs, checking cost consumption, and debugging failed runs. When incidents escalate, he switches to the dashboard for the visual overview, then drops into MCP for targeted diagnostic queries. He mentors both developer-type and operator-type team members on using their preferred interface effectively. He is the person who notices when MCP and dashboard data are out of sync. |
| **Goals** | Seamless transitions between MCP and dashboard without losing context or encountering data inconsistencies. Use the best interface for each task: MCP for speed, scripting, and staying in flow; dashboard for visual overviews, complex approval workflows, and sharing status with non-technical stakeholders. Ensure both interfaces are treated as first-class citizens in platform development. |
| **Frustrations** | MCP and the dashboard currently feel like separate products with different data freshness and different terminology for the same concepts. A pipeline triggered via MCP shows a different status label on the dashboard. Cost data in MCP is 5 minutes behind the dashboard. He cannot share a dashboard deep-link to a specific pipeline run -- colleagues must navigate manually. Cross-interface workflows feel stitched together rather than designed as a unified experience. |

---

## 4. Core User Journeys

### Journey 1: Developer Triggers 12-Document Pipeline via MCP

**Trigger:** Marcus receives a new client brief and needs to generate the full 12-document engagement package without leaving Claude Code.

| Step | Action | Interface |
|------|--------|-----------|
| 1 | Marcus opens Claude Code and loads the client brief into his working context. | Claude Code (local) |
| 2 | He calls the `trigger_pipeline` MCP tool with parameters: `pipeline_id: "document-stack"`, `project_id: "proj-acme-2026"`, `input: { brief: "<client brief content>", client_profile: "acme-corp" }`. | **MCP tool call** |
| 3 | The MCP server validates the brief against the pipeline's input schema, creates a pipeline run record, and returns `{ "run_id": "run-20260324-042", "status": "started", "estimated_cost": "$18-22" }`. | **MCP response** |
| 4 | Marcus continues working on other tasks. Periodically, he calls `check_pipeline_status` MCP tool with the `run_id`. | **MCP tool call** |
| 5 | MCP returns progress updates: `{ "status": "running", "completed_steps": 7, "total_steps": 12, "current_agent": "D7-api-contract-generator", "cost_so_far": "$14.20", "elapsed": "12m 34s" }`. | **MCP response** |
| 6 | Pipeline completes. Marcus calls `get_pipeline_outputs` MCP tool to retrieve the list of generated documents with their metadata (word count, confidence score, schema validation status). | **MCP tool call** |
| 7 | He calls `get_document` MCP tool for each document he wants to review, receiving the content directly in Claude Code for inline review and editing. | **MCP tool call** |
| 8 | Satisfied with the outputs, he calls `finalize_pipeline` MCP tool to mark the run as accepted and lock the document versions. | **MCP tool call** |

**Success:** All 12 documents generated and schema-validated. Total cost < $25.00. Total elapsed time < 30 minutes. All documents written to `reports/proj-acme-2026/`. Pipeline run record shows `status: completed, documents: 12/12`.

**Failure:** Pipeline halts mid-run because an agent's confidence drops below 0.5 (triggers mandatory human review gate), cost accumulator reaches $25.00 ceiling (hard stop), or a document fails output schema validation. Marcus receives an MCP error response with a structured failure object containing `failure_reason`, `failed_step`, `cost_at_failure`, and `recovery_options`. He can call `get_pipeline_logs` MCP tool for detailed diagnostics or `resume_pipeline` to retry from the failed checkpoint.

---

### Journey 2: Engineering Lead Reviews Pipeline Output via Dashboard

**Trigger:** Anika receives a Slack notification that pipeline run `run-20260324-042` has reached the architecture review gate and requires her approval.

| Step | Action | Interface |
|------|--------|-----------|
| 1 | Anika clicks the deep-link in the Slack notification, which opens the dashboard directly to the approval queue with the relevant gate highlighted. | **Dashboard: Approval Queue** |
| 2 | She sees the pending gate details: pipeline "document-stack", project "proj-acme-2026", gate "architecture-review", agent "D5-architecture-drafter", confidence: 0.78, cost so far: $16.40. | **Dashboard: Approval Queue** |
| 3 | She clicks "Review" to open the generated architecture document. The dashboard displays the document in a main panel alongside collapsible side panels showing the input requirements (PRD, feature catalog) and the agent's reasoning chain. | **Dashboard: Document Review** |
| 4 | She reviews the architecture document section by section, checking component diagrams, technology decisions, and pattern selections against the upstream documents shown in the side panels. | **Dashboard: Document Review** |
| 5 | She identifies a concern with the data layer and clicks "Request Revision" with a structured comment: category "Technology Decision", section "Data Layer", severity "Medium", comment "PostgreSQL selection is correct but missing read-replica strategy for the reporting workload. Add a read-replica section." | **Dashboard: Approval Gate** |
| 6 | The pipeline receives the rejection, injects the revision feedback into the agent's context, re-runs D5-architecture-drafter, and re-submits for approval. | System (automatic) |
| 7 | Anika receives a new Slack notification, reviews the revised document on the dashboard, confirms the read-replica strategy is addressed, and clicks "Approve" with a note: "Read-replica strategy looks good. Approved." | **Dashboard: Approval Gate** |
| 8 | The pipeline resumes from the architecture step, proceeding to parallel execution of Data Model and API Contracts generation. | System (automatic) |

**Success:** Anika reviews and approves (including one revision cycle) within 15 minutes. The revision feedback, rejection reason, and final approval are all preserved in the audit trail with timestamps. The pipeline resumes without requiring a full restart -- only the failed step is re-executed.

**Failure:** Gate times out after 4 hours with no response (configurable timeout). Pipeline is paused and a Slack escalation is sent to a backup reviewer configured in the pipeline's `escalation_chain`. If Anika rejects the same gate 3 consecutive times, the pipeline halts permanently and sends a notification to the delivery lead (Marcus) with the full rejection history.

---

### Journey 3: Cross-Interface Handoff — Developer Triggers, Lead Approves, Developer Checks

**Trigger:** Marcus needs to generate documents for a high-stakes engagement that requires mandatory human approval at the PRD gate, assigned to Anika.

| Step | Action | Interface | Actor |
|------|--------|-----------|-------|
| 1 | Marcus calls `trigger_pipeline` MCP tool for project "proj-beta-2026" with `gates: { "prd-review": { "required": true, "assignee": "anika.patel" } }`. | **MCP tool call** | Marcus (Delivery Lead) |
| 2 | Pipeline executes Roadmap (D1) and CLAUDE.md generation autonomously. Both complete with confidence > 0.8. | System (automatic) | -- |
| 3 | Pipeline reaches PRD generation (step 3). Agent D2-prd-generator completes with confidence 0.72, below the 0.8 auto-approve threshold for this gate. The gate fires and the pipeline pauses. | System (automatic) | -- |
| 4 | Anika receives a Slack notification: "PRD review required for proj-beta-2026. Agent: D2-prd-generator. Confidence: 0.72. [Review in Dashboard]". | **Slack notification** | Anika (Engineering Lead) |
| 5 | Anika opens the dashboard via the Slack deep-link, navigates to the approval queue, and reviews the generated PRD alongside the input brief and roadmap in side panels. | **Dashboard: Approval Queue + Document Review** | Anika (Engineering Lead) |
| 6 | Anika approves the PRD with a note: "Solid coverage. Add a note about GDPR data residency requirements in the constraints section." | **Dashboard: Approval Gate** | Anika (Engineering Lead) |
| 7 | The pipeline resumes. Anika's approval note is injected into the session context for downstream agents to consider. | System (automatic) | -- |
| 8 | Meanwhile, Marcus checks status periodically. He calls `check_pipeline_status` MCP tool and receives: `{ "status": "running", "completed_steps": 5, "last_gate": { "gate": "prd-review", "result": "approved", "approved_by": "anika.patel", "timestamp": "2026-03-24T10:34:12Z", "note": "Add GDPR data residency..." } }`. | **MCP tool call** | Marcus (Delivery Lead) |
| 9 | Pipeline completes all 12 documents. Marcus calls `get_pipeline_outputs` MCP tool to retrieve the final document set. | **MCP tool call** | Marcus (Delivery Lead) |

**Success:** Total round-trip from MCP trigger to final MCP status check returning `completed` is under 30 minutes (excluding Anika's review time, which is tracked separately). The approval event is visible in both MCP responses and dashboard views with identical data, timestamps, and status labels. Anika's approval note appears in the session context consumed by downstream agents.

**Failure:** MCP status check and dashboard show inconsistent gate status -- Marcus sees "pending" via MCP after Anika has already approved on the dashboard (data sync failure). Mitigation: both interfaces read from the same `approval_events` PostgreSQL table with no caching layer between them. If the database is unreachable, both interfaces return an explicit error rather than stale data.

---

### Journey 4: DevOps Monitors Fleet Health via Dashboard

**Trigger:** David begins his 9:00 AM operational health review.

| Step | Action | Interface |
|------|--------|-----------|
| 1 | David opens the Fleet Health Overview page. The dashboard displays: 46/48 agents healthy (green), 1 degraded (yellow), 1 offline (red). Fleet cost today: $32.40 of $50.00 daily budget (64.8% utilized). Active pipelines: 3. Pending approval gates: 1. | **Dashboard: Fleet Overview** |
| 2 | He clicks the red (offline) agent indicator: "B3-security-scanner". The agent detail view shows: last heartbeat 47 minutes ago, last error "Claude API rate limit exceeded", invocations today: 312 (vs. typical daily average ~80), error rate: 34%. | **Dashboard: Agent Detail** |
| 3 | He checks B3's cost tab: $4.80 spent today against a $5.00 daily budget. The cost trend chart shows a steep spike starting at 7:15 AM, correlating with the invocation spike. | **Dashboard: Agent Cost Detail** |
| 4 | He navigates to Pipeline Runs and filters by agent "B3-security-scanner". Pipeline "proj-gamma-security-audit" has invoked B3 142 times in a retry loop -- the pipeline's self-healing mechanism is retrying a consistently failing step without backoff. | **Dashboard: Pipeline Runs** |
| 5 | He clicks "Pause Pipeline" on the runaway pipeline. The dashboard confirms the pause with a toast notification and updates the pipeline status to "paused". He then clicks "Restart Agent" on B3 with a rate-limit backoff configuration override (exponential backoff, max 60s). | **Dashboard: Fleet Controls** |
| 6 | He checks the yellow (degraded) agent: "O2-runbook-executor". The detail view shows: healthy but slow -- p95 latency 12s (vs. normal 3s). Root cause: upstream dependency (knowledge base) is responding slowly. David notes this for follow-up but takes no immediate action. | **Dashboard: Agent Detail** |
| 7 | He clicks "Export Health Report" to generate a morning fleet summary PDF: current agent statuses, cost utilization, incident summary, and pipeline throughput. | **Dashboard: Reports** |

**Success:** David identifies the offline agent, diagnoses the root cause (retry loop in a pipeline), pauses the offending pipeline, and restarts the agent -- all within 10 minutes. Fleet returns to 48/48 healthy within 15 minutes of intervention. The morning health report PDF is generated in under 5 seconds.

**Failure:** Dashboard displays stale data (last refresh > 60 seconds ago), causing David to miss an active incident. "Pause Pipeline" action fails silently -- the button appears to work but the pipeline continues running. Agent restart does not take effect. Mitigation: dashboard auto-refreshes every 10 seconds via WebSocket; all control actions return explicit success/failure confirmations; fleet controller emits state-change events that the dashboard consumes in real-time.

---

### Journey 5: Developer Queries Agent Cost via MCP

**Trigger:** Priya needs to check fleet and project-level spending before her team sync to justify the current budget allocation.

| Step | Action | Interface |
|------|--------|-----------|
| 1 | Priya calls `get_cost_summary` MCP tool: `{ "scope": "fleet", "period": "this_week" }`. | **MCP tool call** |
| 2 | MCP returns: `{ "fleet_total": "$187.40", "daily_budget": "$50.00", "weekly_budget": "$350.00", "utilization": "53.5%", "top_agents_by_cost": [{ "agent_id": "D5-architecture-drafter", "cost": "$34.20", "invocations": 28 }, { "agent_id": "D9-design-spec-writer", "cost": "$28.90", "invocations": 14 }, { "agent_id": "B1-code-generator", "cost": "$22.10", "invocations": 45 }] }`. | **MCP response** |
| 3 | She drills into a specific project: `get_cost_summary` with `{ "scope": "project", "project_id": "proj-acme-2026", "period": "this_week" }`. | **MCP tool call** |
| 4 | MCP returns: `{ "project_total": "$62.30", "project_budget": "$140.00", "utilization": "44.5%", "pipeline_runs": 4, "cost_per_run_avg": "$15.58", "cost_per_run_range": "$12.40 - $19.20" }`. | **MCP response** |
| 5 | She calls `get_cost_forecast` MCP tool: `{ "scope": "fleet", "period": "end_of_week" }`. | **MCP tool call** |
| 6 | MCP returns: `{ "projected_weekly_total": "$312.00", "weekly_budget": "$350.00", "utilization_projected": "89.1%", "risk": "medium", "recommendation": "Current trajectory reaches 89% of weekly budget. Consider deferring non-critical pipeline runs to next week or reducing D5 temperature to lower token usage." }`. | **MCP response** |
| 7 | Priya uses this data in her team sync to show budget health and justify the allocation, without ever leaving Claude Code. | Claude Code (local) |

**Success:** All cost queries return within 500ms (p95). Data matches the dashboard's Cost Governance page to within 2%. Priya gets complete budget context (actuals + forecast + recommendation) in 3 MCP calls taking less than 2 seconds total.

**Failure:** MCP returns cost data more than 5 minutes stale, or cost totals differ from dashboard values by more than 2%. Mitigation: both MCP and dashboard query the same `cost_events` materialized view, refreshed every 60 seconds. If the materialized view is stale (refresh failed), the MCP response includes a `data_freshness` field indicating the age of the data.

---

### Journey 6: Compliance Officer Runs Monthly Audit via Dashboard

**Trigger:** Fatima needs to produce a monthly compliance report for the governance review board meeting scheduled for tomorrow.

| Step | Action | Interface |
|------|--------|-----------|
| 1 | Fatima opens the Audit Log dashboard and sets the date range filter to March 1-24, 2026. | **Dashboard: Audit Log** |
| 2 | The dashboard loads an audit summary: 12,847 agent invocations, 47 pipeline runs completed, 23 approval gates triggered (22 approved, 1 rejected, 0 bypassed), 0 autonomy tier violations. PII detections: 14 instances across 9 invocations (all scrubbed before persistence). Total cost: $612.40. | **Dashboard: Audit Summary** |
| 3 | She filters the audit log to "PII detection" events. Each entry shows: timestamp, agent_id, data type detected (email / phone / SSN), action taken (scrubbed), original field location, and the audit record's immutability hash. | **Dashboard: Audit Log (filtered)** |
| 4 | She clicks on one PII detection event to inspect the full 13-field audit record. She verifies: `correlation_id` links to the correct pipeline run, `trust_chain` shows the correct authorization path from the triggering user through the orchestrator to the agent, `cost_usd` is within the expected range for this agent type. | **Dashboard: Audit Event Detail** |
| 5 | She navigates to the "Cost Governance" tab. The dashboard shows: all 48 agents have budget limits configured (0 unconfigured), 0 agents exceeded their daily budget limit during the period, 2 agents triggered 80% budget warnings (with alerts sent within 30 seconds). | **Dashboard: Cost Governance** |
| 6 | She navigates to the "Autonomy Compliance" tab. The dashboard displays the tier distribution: T0 (full-auto): 12 agents, T1 (notify): 18 agents, T2 (pre-approve): 14 agents, T3 (every action): 4 agents. No tier violations detected. All T2/T3 agents had their required approvals obtained before proceeding. | **Dashboard: Autonomy Compliance** |
| 7 | She clicks "Generate Compliance Report" and selects the "Monthly Governance Review" template. The system assembles a PDF incorporating: audit summary statistics, PII handling log, cost governance status, autonomy tier compliance, approval gate history, and the immutability hash chain for the entire audit period. | **Dashboard: Report Generator** |
| 8 | Fatima downloads the PDF and verifies it includes the hash chain validation section, confirming no audit records were tampered with during the reporting period. | **Dashboard: Report Download** |

**Success:** Complete compliance report generated in under 10 minutes of Fatima's time. All 12,847 invocations have valid 13-field audit records (100% completeness). PII detection coverage is 100% of invocations that processed unstructured text. Immutability hash chain validates successfully across the entire period. The PDF is board-ready without manual formatting.

**Failure:** Audit records are missing for some invocations (completeness < 100%), indicating a gap in the audit logging pipeline. PII detections are absent from the log despite sensitive data having been processed, indicating the PII scanning pre-hook was bypassed. Immutability hashes fail validation, suggesting record tampering or corruption. Mitigation: nightly reconciliation job flags audit gaps and alerts the platform team; PII scanning is a mandatory, non-bypassable pre-hook enforced by BaseAgent; audit records are written to an append-only table with cryptographic hash chaining.

---

## 5. Capabilities

### C1: Agent Orchestration

The platform orchestrates 48 specialized AI agents organized across 7 SDLC phases: GOVERN (cost, audit, lifecycle, orchestration), DESIGN (requirements through test strategy), BUILD (code generation, review, security), TEST (static analysis, test running, coverage), DEPLOY (checklist, IaC, release, rollback), OPERATE (incident triage, runbook, SLA, alerts), and OVERSIGHT (structural and design audits). Orchestration operates at 5 hierarchical levels: L0 agent loop (single agent execution via Claude Agent SDK `query()`), L1 subagent spawn (nested delegation), L2 pipeline (sequential agent chain with gates), L3 team (complex DAG workflows with parallel and conditional branches), and L4 fleet (fleet-wide scaling, health management, and resource allocation). All levels share a common typed message envelope format for inter-agent communication, enabling traceability from any individual agent invocation up to the fleet level.

### C2: 12-Document Generation Pipeline

A single client brief triggers the generation of 12 interconnected engagement deliverables in a defined dependency sequence: Roadmap, CLAUDE.md, PRD, Feature Catalog, Backlog, Architecture, Data Model + API Contracts (parallel pair), Enforcement Scaffold, Quality Spec + Test Strategy (parallel pair), and Design Spec. The pipeline uses a context accumulation strategy where each agent receives all prior outputs via the SessionStore. A $25/run cost ceiling is enforced in real-time by G1-cost-tracker. Parallel steps (Data Model + API Contracts; Quality Spec + Test Strategy) execute concurrently via `asyncio.gather()` with results merged using a configurable union strategy. The pipeline supports checkpoint/resume so that a failed step can be retried from its checkpoint without re-running completed upstream steps.

### C3: Cost Control and Governance

Real-time budget enforcement operates at four hierarchical levels: fleet ($50/day), project ($20/day), agent ($5/day), and individual invocation ($0.50). The G1-cost-tracker agent monitors spend continuously and the system enforces hard stops when any budget ceiling is reached at any level. The fail-safe principle is non-negotiable: if the cost database is unreachable or the cost tracking service is degraded, all agent invocations are blocked rather than allowed to run untracked. Cost data is exposed through both MCP tool calls (for developer personas querying from their IDE) and dashboard views (for operator personas monitoring visually), reading from the same underlying `cost_events` materialized view to ensure consistency.

### C4: Human-in-the-Loop Approval Gates

Pipelines support configurable approval gates where execution pauses and waits for human review before proceeding. Gates are triggered by two mechanisms: agent confidence scores falling below configurable per-gate thresholds, or mandatory review points defined in the pipeline YAML configuration. Agents operate at one of four autonomy tiers: T0 (full autonomous -- no human involvement), T1 (notify after action -- human informed but not blocking), T2 (pre-approval required for sensitive actions -- human must approve before the agent proceeds), T3 (every action requires approval -- maximum oversight). Approval notifications are delivered via Slack with deep-links to the dashboard's approval queue. Approvals and rejections include structured comments (category, section, severity, message) that are preserved in the audit trail and fed back into the agent's context on retry.

### C5: Quality Assurance

Every agent is validated against two categories of tests: golden tests (expected input/output pairs covering normal, edge, and minimal cases stored in `tests/golden/`) and adversarial tests (malformed inputs, prompt injection attempts, and boundary violations stored in `tests/adversarial/`). Agent outputs are scored against rubric-based quality criteria defined in each agent's `rubric.yaml`, evaluating dimensions such as completeness, accuracy, coherence, and format compliance. A minimum 90% code coverage threshold is enforced for all agent implementations. Quality gates embedded in pipelines verify that generated documents meet structural and content standards (schema validation, minimum section count, confidence threshold) before the pipeline proceeds to the next step.

### C6: Observability and Audit Trail

Every agent invocation produces a 13-field JSONL audit record written to an immutable, append-only `audit_events` table: `envelope_id`, `correlation_id`, `session_id`, `project_id`, `agent_id`, `timestamp`, `input_hash`, `output_hash`, `cost_usd`, `latency_ms`, `confidence`, `model`, and `status`. Records are linked via cryptographic hash chaining for tamper detection -- each record includes the hash of the previous record, enabling end-to-end integrity verification over any time range. PII scanning runs as a mandatory pre-hook on all agents via the BaseAgent class, detecting and scrubbing sensitive data (emails, phone numbers, SSNs, API keys) before any data is persisted. Cost tracking, agent health metrics, pipeline run status, and approval gate events are continuously recorded and exposed through both MCP queries and dashboard views.

### C7: Knowledge Management and Exception Flywheel

The platform maintains a 3-tier knowledge base: client-specific knowledge (engagement context, preferences, past decisions, stored in `knowledge/client/{client_id}/`), stack-specific knowledge (technology patterns, common issues for specific tech stacks), and universal knowledge (cross-client best practices, anti-patterns, proven resolution strategies). An exception flywheel promotes learnings upward through the tiers: a resolution discovered during one client engagement is evaluated by the knowledge promotion agent for stack-level applicability; proven stack-level patterns that demonstrate cross-stack validity are promoted to universal knowledge. The 4-layer configuration resolution system (archetype defaults, mixin capabilities, agent manifest overrides, client profile customizations) incorporates knowledge at each layer, allowing agents to benefit from accumulated organizational learning.

### C8: Pipeline Resilience

Pipelines support checkpoint/resume at step granularity: when a step fails, all prior completed steps and their outputs are preserved in the SessionStore, and the pipeline can be restarted from the exact failure point without re-executing completed work. Self-healing is implemented for specific recoverable failure modes: when an agent produces output that fails schema validation, the system can automatically retry with an adjusted prompt; when a test failure occurs in a quality gate, the system can trigger a targeted fix agent before retrying the original step. The pipeline execution engine supports DAG-based parallel execution (e.g., Data Model and API Contracts run concurrently after Architecture completes), with results merged via a configurable strategy (union, override, or custom merge function). All pipeline state -- step statuses, checkpoints, session context, cost accumulation -- is persisted to PostgreSQL, surviving server restarts and enabling distributed execution.

### C9: Agent Lifecycle Management

Agents progress through three maturity levels that determine their operational autonomy: apprentice (high human oversight, all outputs reviewed at approval gates), professional (moderate oversight, only low-confidence outputs trigger review), and expert (minimal oversight, autonomous operation within budget and quality constraints). Promotion criteria are data-driven and configurable per agent: human override rate below 5%, mean confidence score above 0.85, sustained over 14 consecutive operational days. Agent versioning supports canary deployment: a new agent version is deployed to a canary slot that receives a configurable percentage of traffic (default 10%) while the stable version handles the remainder. If the canary's error rate, cost per invocation, or quality score deviates beyond configurable thresholds, automatic rollback is triggered. Version history and deployment events are recorded in the audit trail.

### C10: Multi-Project Isolation

The platform supports concurrent operation across multiple client projects with strict namespace isolation. Each project has its own: budget allocation (drawn from the fleet budget), session context namespace (preventing cross-project data leakage in the SessionStore), knowledge base partition (client-specific knowledge is scoped to the project), audit trail scope (queries can be filtered by project), and pipeline execution context. Per-client profiles stored in `knowledge/client/{client_id}/` customize agent behavior -- tone, output format, domain terminology, technology preferences -- without modifying the underlying agent code or manifests. Project isolation extends to failure containment: a pipeline failure, budget exhaustion, or agent error in one project does not affect pipelines or agents running for other projects.

### C11: MCP Server Exposure

The platform exposes its full operational functionality to AI coding clients (Claude Code, Cursor, and future MCP-compatible tools) via the Model Context Protocol. The MCP tool surface includes: `trigger_pipeline` (start a document generation or custom pipeline), `check_pipeline_status` (poll progress, cost, current step), `get_pipeline_outputs` (retrieve generated document list with metadata), `get_document` (fetch a specific document's content), `resume_pipeline` (restart from checkpoint after failure), `query_agent` (invoke a specific agent directly), `list_agents` (enumerate available agents with health status), `get_cost_summary` (fleet/project/agent cost breakdown), `get_cost_forecast` (projected spend based on current trajectory), `approve_gate` / `reject_gate` (respond to approval gates programmatically), `check_fleet_health` (agent status grid and key metrics), and `get_audit_log` (filtered audit trail query). MCP is a first-class interface that connects directly to the same service layer as the dashboard -- not a wrapper or adapter. Performance targets: read operations < 500ms p95, write/trigger operations < 2s p95.

### C12: Dashboard / Operator UI

A Streamlit-based dashboard provides visual monitoring, control, and reporting for human operators who need graphical overviews and point-and-click workflows. Core screens include: **Fleet Health Overview** (agent status grid with green/yellow/red indicators, cost utilization gauges, active pipeline count, pending gate count), **Pipeline Runs** (status timeline per run, step-by-step progress with agent names and durations, cost accumulation graph, filter by project/status/date), **Approval Queue** (pending gates with document preview, side-by-side comparison with input requirements, approve/reject with structured comments, escalation timer), **Agent Detail** (configuration summary, health history chart, cost trend, maturity level and promotion progress, version and deployment status), **Audit Log** (filterable 13-field event viewer with immutability hash verification, drill-down to individual records, correlation_id-based pipeline trace), **Cost Governance** (budget utilization at fleet/project/agent levels with trend charts, budget warning history, forecast visualization), and **Report Generator** (compliance reports, fleet health reports, and cost summaries as downloadable PDFs with configurable templates). The dashboard reads from the same PostgreSQL tables and materialized views as the MCP server, ensuring data consistency across interfaces.

---

## 6. Explicit Out of Scope

1. **Multi-LLM provider support** -- The platform uses Anthropic Claude models exclusively (Haiku, Sonnet, Opus). Supporting additional LLM providers (OpenAI GPT, Google Gemini, Meta Llama, Mistral) would require a model abstraction layer that adds complexity without benefit for an internal tool purpose-built on the Claude Agent SDK.

2. **Mobile application** -- No native iOS or Android application will be developed. The Streamlit dashboard is designed for desktop workstation use. All target personas operate from desktop environments during their working hours.

3. **Third-party project management tool integration** -- No integration with Jira, Linear, Asana, Monday, or other PM tools. The backlog generator (D8) produces standalone task lists in structured format. Export adapters to PM tools may be considered in a future phase but are explicitly excluded from v1.0.

4. **Self-hosted or local LLM inference** -- All LLM inference uses Anthropic's hosted Claude API. Running local models, self-hosted inference servers, or on-premises LLM deployments is out of scope. This creates a hard dependency on Anthropic API availability but eliminates infrastructure complexity.

5. **Real-time collaborative editing** -- Generated documents are produced by AI agents and reviewed by individual humans. Multi-user simultaneous editing (Google Docs-style collaboration) of agent outputs is not supported. Documents are versioned and individually reviewed, not collaboratively edited.

6. **Billing, invoicing, or payment processing** -- The platform tracks costs for internal operational governance and budget enforcement. It does not generate client invoices, process payments, manage subscriptions, or integrate with billing systems. Cost data is for visibility and control only.

7. **Public SaaS or multi-tenant deployment** -- This is an internal tool deployed within a single organization's infrastructure. No multi-tenant architecture, public user registration, customer-facing authentication flows, public API rate limiting, or external SLA commitments are in scope.

8. **Natural language querying of the dashboard** -- The dashboard uses structured filters, predefined views, and point-and-click interactions. A conversational "ask anything" natural language interface for the dashboard is not in scope. Developers who prefer natural language interaction can use MCP via Claude Code, which inherently supports natural language.

9. **Agent marketplace or third-party plugin system** -- All 48 agents are built, maintained, and deployed by the platform team. There is no mechanism for external developers to contribute, publish, install, or manage custom agents. Extensibility is limited to the internal archetype/mixin system.

10. **ML-based predictive analytics** -- The platform stores operational, cost, and audit data for governance purposes. Machine learning-based anomaly detection, predictive capacity planning, spend forecasting using trained models, or automated root cause analysis are out of scope. Basic cost forecasting using linear projection from current trajectory is included; ML models are not.

11. **Email-based notifications** -- All notifications (approval gate alerts, budget warnings, fleet health alerts, incident escalations) are delivered via Slack. Email-based alerting, digest emails, scheduled report delivery via email, or SMTP integration are not supported.

12. **Internationalization and localization** -- The platform operates in English only. Multi-language support for the dashboard UI, generated document content, agent system prompts, error messages, or compliance reports is not in scope.

---

*This PRD defines WHAT the Agentic SDLC Platform does and FOR WHOM. It intentionally excludes architectural decisions (HOW), which are the domain of Document 2 (ARCH.md). Implementation sequencing, sprint planning, and task breakdown are deferred to downstream documents in the 14-document pipeline (Feature Catalog, Backlog, Design Spec, etc.).*
