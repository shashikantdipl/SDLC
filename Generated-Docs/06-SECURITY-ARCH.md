# SECURITY-ARCH — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-29
**Document:** 06 of 24 | Status: Draft

---

## Table of Contents

1. [Overview](#1-overview)
2. [Data Classification](#2-data-classification)
3. [Authentication](#3-authentication)
4. [Authorization and RBAC](#4-authorization-and-rbac)
5. [Agent Permission Model](#5-agent-permission-model)
6. [Secrets Management](#6-secrets-management)
7. [Threat Model (STRIDE)](#7-threat-model-stride)
8. [Attack Surface Analysis](#8-attack-surface-analysis)
9. [OWASP Top 10 Mitigations](#9-owasp-top-10-mitigations)
10. [Data Governance](#10-data-governance)
11. [Supply Chain Security](#11-supply-chain-security)
12. [Compliance Scope](#12-compliance-scope)

---

## 1. Overview

This document defines the security architecture for the Agentic SDLC Platform — a system that orchestrates 48 AI agents across 7 SDLC phases via three interface layers (MCP, REST API, Streamlit Dashboard). The security model must protect against threats unique to AI agent platforms: prompt injection, cost runaway, unauthorized agent escalation, data exfiltration through LLM providers, and uncontrolled autonomous behavior.

### Security Principles

| # | Principle | Application |
|---|---|---|
| SP-1 | Defense in depth | Every layer (network, application, data, agent) has independent controls |
| SP-2 | Least privilege | Agents, users, and services receive minimum permissions for their function |
| SP-3 | Zero trust for agents | No agent is trusted by default; trust is earned through maturity progression (T0-T3) |
| SP-4 | Confidential data never leaves the boundary | Data classified as Confidential is never sent to external LLM providers |
| SP-5 | Immutable audit | All security-relevant events are append-only and tamper-evident |
| SP-6 | Fail closed | Authentication/authorization failures result in denial, not degraded access |

---

## 2. Data Classification

Every data store in the platform is classified according to a four-tier scheme. Classifications drive encryption requirements, access controls, retention policies, and LLM processing eligibility.

### 2.1 Classification Tiers

| Tier | Label | Description | Encryption at Rest | Encryption in Transit | LLM Processing |
|---|---|---|---|---|---|
| C1 | Public | Data intended for public consumption | Optional | Required (TLS 1.2+) | Any provider |
| C2 | Internal | Operational data not containing PII or secrets | Required (AES-256) | Required (TLS 1.2+) | Any provider |
| C3 | Confidential | Data containing PII, customer content, or audit trails | Required (AES-256) | Required (TLS 1.3) | Local provider only (Ollama) |
| C4 | Restricted | Secrets, credentials, encryption keys | Required (HSM/KMS) | Required (mTLS) | Never processed by LLM |

### 2.2 Database Table Classification

| Table | Classification | Justification | PII Fields | Special Handling |
|---|---|---|---|---|
| `agent_registry` | C2 — Internal | Agent metadata, no PII, no customer data | None | Standard access controls |
| `cost_metrics` | C2 — Internal | Aggregated cost data, no PII | None | Standard access controls |
| `audit_events` | C3 — Confidential | May contain input/output hashes linked to customer content; compliance-critical | `details` (JSONB may reference customer data) | Append-only, no UPDATE/DELETE, 1-year retention |
| `pipeline_runs` | C2 — Internal | Pipeline execution metadata | None | Standard access controls |
| `pipeline_steps` | C2 — Internal | Step-level execution metadata | None | Standard access controls |
| `knowledge_exceptions` | C2 — Internal | Anonymized exception patterns | None (anonymized before storage) | PII scan before insert |
| `session_context` | C3 — Confidential | Contains agent session state with customer project brief content | `context_data` (may contain project brief excerpts) | 7-day retention, encrypted JSONB, PII scan on read |
| `approval_requests` | C2 — Internal | Approval metadata, no document content | None | Standard access controls |
| `pipeline_checkpoints` | C2 — Internal | Checkpoint state, references but does not contain document content | None | 30-day retention |
| `mcp_call_events` | C2 — Internal | MCP telemetry, tool names, latency, no payloads | None | 90-day retention |

### 2.3 File Store Classification

| Store | Classification | Justification |
|---|---|---|
| Generated documents (`reports/{project_id}/{run_id}/`) | C3 — Confidential | Contains customer-specific specification content |
| Agent manifests (`agents/{agent_id}/manifest.yaml`) | C2 — Internal | Agent configuration, no secrets |
| Structured logs (JSONL) | C3 — Confidential | May contain audit data with customer context references |
| Environment files (`.env`) | C4 — Restricted | Contains API keys and database credentials |

---

## 3. Authentication

### 3.1 Authentication by Interface

| Interface | Transport | Auth Method | Token Format | Expiry | Refresh |
|---|---|---|---|---|---|
| MCP (stdio) | Local process | API key in MCP config | Static key string | No expiry (rotated quarterly) | Manual rotation |
| MCP (streamable-http) | HTTPS | API key in `Authorization` header | `Bearer <api-key>` | No expiry (rotated quarterly) | Manual rotation |
| REST API | HTTPS | JWT (JSON Web Token) | `Bearer <jwt>` | 1 hour | Refresh token (24h expiry) |
| Streamlit Dashboard | HTTPS (session) | Session cookie after login | Signed session cookie | 8 hours | Re-authentication required |
| Agent-to-Agent | Internal (in-process or localhost) | Service token | Signed JWT with `iss=agent-runtime` | 5 minutes | Auto-renewed per invocation |
| Database | TCP/TLS | Connection string with credentials | PostgreSQL auth | N/A (connection pool) | Connection pool recycling |
| LLM Providers | HTTPS | API key per provider | Provider-specific header | Per provider policy | Manual rotation |

### 3.2 Authentication Flow — REST API

```
Client                    REST API                  Auth Service
  |                          |                           |
  |--- POST /auth/login ---->|                           |
  |    {email, password}     |--- validate_credentials ->|
  |                          |<-- user_record + roles ----|
  |                          |--- sign_jwt(user, roles) --|
  |<-- {access_token,        |                           |
  |     refresh_token} ------|                           |
  |                          |                           |
  |--- GET /api/agents ----->|                           |
  |    Authorization: Bearer |--- verify_jwt(token) ---->|
  |                          |<-- {user_id, roles} ------|
  |                          |--- check_rbac(role, resource)
  |<-- 200 [agents] ---------|                           |
```

### 3.3 Authentication Flow — MCP

```
Claude Code                 MCP Server (stdio)
  |                              |
  |--- MCP initialize --------->|
  |    (API key in config)       |--- validate_api_key(key) --> KeyStore
  |                              |<-- {client_id, permissions} --|
  |<-- initialized + caps ------|
  |                              |
  |--- tools/call -------------->|
  |    {tool: "list_agents"}     |--- check_permission(client_id, tool)
  |                              |--- AgentService.list_agents()
  |<-- result ------------------|
```

---

## 4. Authorization and RBAC

### 4.1 Role Definitions

| Role | Description | Assigned To | Interface Access |
|---|---|---|---|
| `admin` | Full platform access, user management, configuration | Platform team lead | All interfaces |
| `operator` | Fleet management, deployments, cost monitoring, incident response | Priya (Platform Engineer), David (DevOps) | MCP + Dashboard |
| `reviewer` | Approval gate decisions, quality review, agent maturity management | Anika (Engineering Lead) | Dashboard |
| `auditor` | Read-only access to audit trails, compliance reports, cost reports | Fatima (Compliance Officer) | Dashboard |
| `user` | Pipeline triggering, document generation, document viewing | Marcus (Delivery Lead), developers | MCP + Dashboard |
| `agent` | Programmatic access scoped by agent maturity tier (T0-T3) | 48 platform agents | Internal (agent-to-service) |

### 4.2 RBAC Permission Matrix

| Resource | Action | admin | operator | reviewer | auditor | user | agent (T0) | agent (T1) | agent (T2) | agent (T3) |
|---|---|---|---|---|---|---|---|---|---|---|
| `agent_registry` | read | Y | Y | Y | Y | Y | Own only | Own only | Own only | Own only |
| `agent_registry` | write | Y | Y | N | N | N | N | N | N | N |
| `agent_registry` | promote_tier | Y | N | Y | N | N | N | N | N | N |
| `cost_metrics` | read | Y | Y | Y | Y | Own projects | Own only | Own only | Own only | Own only |
| `cost_metrics` | write | Y | N | N | N | N | Own only | Own only | Own only | Own only |
| `audit_events` | read | Y | Y | Y | Y | Own projects | N | N | Own only | Own only |
| `audit_events` | append | Y | Y | N | N | N | Y | Y | Y | Y |
| `pipeline_runs` | trigger | Y | Y | N | N | Y | N | N | Y | Y |
| `pipeline_runs` | read | Y | Y | Y | Y | Own projects | Own run | Own run | Own run | Own run |
| `pipeline_runs` | cancel | Y | Y | N | N | Own runs | N | N | N | N |
| `approval_requests` | read | Y | Y | Y | Y | Own projects | N | N | N | N |
| `approval_requests` | approve/reject | Y | N | Y | N | N | N | N | N | N |
| `knowledge_exceptions` | read | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| `knowledge_exceptions` | write | Y | Y | N | N | N | N | Y | Y | Y |
| `session_context` | read | Y | Y | N | N | N | Own session | Own session | Own session | Own session |
| `session_context` | write | Y | N | N | N | N | Own session | Own session | Own session | Own session |
| Platform config | read | Y | Y | N | N | N | N | N | N | N |
| Platform config | write | Y | N | N | N | N | N | N | N | N |
| User management | all | Y | N | N | N | N | N | N | N | N |

---

## 5. Agent Permission Model

### 5.1 Agent Maturity Tiers and Security Implications

| Tier | Label | Autonomy | Approval Required | Budget Limit (per invocation) | Data Access | LLM Provider Access |
|---|---|---|---|---|---|---|
| T0 | Apprentice | None — every output reviewed | Always | $0.50 | C1, C2 only | Any (output reviewed before persistence) |
| T1 | Journeyman | Low — most outputs reviewed | Most actions | $2.00 | C1, C2 only | Any (output reviewed before persistence) |
| T2 | Senior | Medium — routine outputs auto-approved | High-risk actions only | $5.00 | C1, C2, C3 (read only) | Any for C1/C2 data; Ollama only for C3 |
| T3 | Expert | High — auto-approved below confidence threshold | Anomalous actions only | $10.00 | C1, C2, C3 (read/write) | Any for C1/C2 data; Ollama only for C3 |

### 5.2 Agent Permission Enforcement

```
Agent Invocation
       |
       v
[1] Verify agent_id in agent_registry (exists, status=active)
       |
       v
[2] Check maturity tier (T0/T1/T2/T3)
       |
       v
[3] Validate requested tools against agent manifest allowed_tools[]
       |
       v
[4] Check data classification of requested resources
       |--- C3/C4 data + T0/T1 agent --> DENY
       |--- C3 data + external LLM provider --> DENY (route to Ollama)
       |--- C4 data --> ALWAYS DENY (secrets never processed by agents)
       |
       v
[5] Check budget: remaining_budget >= estimated_cost
       |--- insufficient budget --> DENY + alert operator
       |
       v
[6] Execute agent invocation
       |
       v
[7] Record audit event (append to audit_events)
       |
       v
[8] Check if approval gate required (based on tier + action type)
       |--- approval required --> pause, notify reviewer, await decision
       |--- auto-approved --> persist output
```

### 5.3 Agent Tool Permissions (Sample — GOVERN Phase)

| Agent ID | Agent Name | Allowed Tools | Max Budget/Invocation | Data Classification Access |
|---|---|---|---|---|
| G1 | cost-tracker | `record_cost`, `check_budget`, `alert_budget` | $0.10 (mostly tracking) | C2 (cost_metrics) |
| G2 | audit-trail-validator | `append_audit`, `query_audit`, `reconcile_audit` | $0.50 | C3 (audit_events) |
| G3 | agent-lifecycle-manager | `update_agent_status`, `promote_tier`, `deploy_canary` | $0.25 | C2 (agent_registry) |
| G4 | team-orchestrator | `trigger_pipeline`, `assign_agent`, `checkpoint_pipeline` | $5.00 | C2 (pipeline_runs, pipeline_steps) |
| G5 | quality-gate-enforcer | `evaluate_quality`, `approve_auto`, `reject_with_feedback` | $2.00 | C2 (approval_requests), C3 (generated docs) |
| G6 | session-manager | `create_session`, `read_session`, `expire_session` | $0.10 | C3 (session_context) |
| G7 | compliance-monitor | `check_compliance`, `generate_report`, `flag_violation` | $1.00 | C3 (audit_events, generated docs) |

---

## 6. Secrets Management

### 6.1 Secret Inventory

| Secret | Storage | Rotation Policy | Access Scope |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Environment variable (`.env` file, never committed) | Quarterly or on suspected compromise | LLM provider adapter only |
| `OPENAI_API_KEY` | Environment variable | Quarterly or on suspected compromise | LLM provider adapter only |
| `DATABASE_URL` | Environment variable | Quarterly; password rotated independently | Shared service layer (connection pool) |
| `SLACK_WEBHOOK_URL` | Environment variable | Annually or on suspected compromise | Notification service only |
| `PAGERDUTY_API_KEY` | Environment variable | Annually or on suspected compromise | Alert service only |
| `JWT_SECRET` | Environment variable | Monthly | Auth service only |
| `MCP_API_KEY` | MCP client configuration | Quarterly | MCP server authentication |
| `SESSION_SECRET` | Environment variable | Monthly | Streamlit dashboard session signing |

### 6.2 Secret Handling Rules

| Rule | Enforcement |
|---|---|
| `.env` files NEVER committed to version control | `.gitignore` entry + pre-commit hook scan |
| Secrets NEVER logged (even at DEBUG level) | Log sanitization middleware strips known secret patterns |
| Secrets NEVER included in audit_events details | PII/secret scanner on `audit_events.details` JSONB before insert |
| Secrets NEVER sent to LLM providers in prompts | Prompt sanitization step in LLM adapter |
| Secrets NEVER appear in error messages or stack traces | Error handler strips environment variables from exception context |
| Rotation triggers immediate key invalidation | Old key revoked within 5 minutes of new key activation |

### 6.3 Production Secret Management (Target State)

| Environment | Secret Store | Injection Method |
|---|---|---|
| Local | `.env` file | `python-dotenv` at startup |
| Dev | `.env` file on dev server | `python-dotenv` at startup |
| Staging | HashiCorp Vault or AWS Secrets Manager | Sidecar injection / init container |
| Production | HashiCorp Vault or AWS Secrets Manager | Sidecar injection / init container |

---

## 7. Threat Model (STRIDE)

### 7.1 MCP Servers (agents-server, governance-server, knowledge-server)

| Threat Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **Spoofing** | Attacker impersonates a legitimate MCP client | Medium | High | API key authentication on all MCP connections; key rotation quarterly |
| **Tampering** | Malicious MCP client sends crafted tool parameters to bypass validation | Medium | High | JSON Schema validation on all tool inputs; shared service layer re-validates |
| **Repudiation** | Agent denies performing an action | Low | High | Immutable `audit_events` with cryptographic hash chain |
| **Information Disclosure** | MCP response leaks data beyond client's permission scope | Medium | High | RBAC check in shared service before data retrieval; response filtering by role |
| **Denial of Service** | Flood of MCP tool calls exhausts server resources | Medium | Medium | Rate limiting (token bucket per client_id); circuit breaker on downstream services |
| **Elevation of Privilege** | MCP client calls tools beyond its permitted scope | Medium | High | Tool-level permission check against client role; agent tier validation |

### 7.2 REST API (aiohttp, port 8080)

| Threat Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **Spoofing** | Stolen JWT used to impersonate user | Medium | High | Short JWT expiry (1h); refresh token rotation; JWT blacklist on logout |
| **Tampering** | Modified JWT claims (role escalation) | Low | Critical | JWT signature verification with `JWT_SECRET`; claims validated against user store |
| **Repudiation** | User denies triggering a pipeline | Low | Medium | All API calls logged in `mcp_call_events` and `audit_events` with user_id |
| **Information Disclosure** | API returns data beyond user's project scope | Medium | High | Row-level filtering by `project_id` in shared service queries |
| **Denial of Service** | API flood from unauthenticated source | High | Medium | Rate limiting per IP; authentication required for all endpoints except `/health` |
| **Elevation of Privilege** | User exploits API to access admin endpoints | Medium | Critical | RBAC middleware on every route; admin endpoints require `admin` role |

### 7.3 Streamlit Dashboard (port 8501)

| Threat Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **Spoofing** | Session hijacking via stolen cookie | Medium | High | Secure, HttpOnly, SameSite=Strict cookies; session bound to IP |
| **Tampering** | XSS injection via user-controlled content in dashboard | Medium | High | Output encoding; CSP headers; Streamlit's built-in XSS protection |
| **Repudiation** | Reviewer denies approving/rejecting a gate | Low | Medium | Approval actions logged with user_id, timestamp, and IP in `approval_requests` |
| **Information Disclosure** | Dashboard displays data beyond user's role | Medium | High | Dashboard calls REST API which enforces RBAC; no direct DB access |
| **Denial of Service** | Excessive dashboard sessions consume server memory | Medium | Low | Session limit per user (max 3 concurrent); idle timeout (30 min) |
| **Elevation of Privilege** | User modifies Streamlit URL parameters to access restricted pages | Low | Medium | Server-side role check on every page render; URL parameters are informational only |

### 7.4 Agent Runtime

| Threat Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **Spoofing** | Rogue agent impersonates a legitimate agent | Low | Critical | Agent identity verified via `agent_registry`; service tokens signed with runtime key |
| **Tampering** | Prompt injection causes agent to deviate from intended behavior | High | High | Input sanitization; output validation against quality schema; human approval gates |
| **Repudiation** | Agent produces output with no traceable reasoning | Medium | High | Full reasoning chain stored in `audit_events.details`; input/output hashes recorded |
| **Information Disclosure** | Agent sends Confidential data to external LLM provider | Medium | Critical | Data classification check before LLM call; C3 data routed to Ollama only |
| **Denial of Service** | Agent enters infinite loop consuming tokens and budget | Medium | High | Per-invocation budget ceiling; G1-cost-tracker hard-stop; circuit breaker |
| **Elevation of Privilege** | Agent attempts to promote its own maturity tier | Low | Critical | Self-promotion blocked; tier changes require `reviewer` or `admin` role |

### 7.5 PostgreSQL Database

| Threat Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **Spoofing** | Attacker connects with stolen database credentials | Low | Critical | Database in isolated subnet; connection via TLS; credentials in Vault (production) |
| **Tampering** | Direct modification of `audit_events` to cover tracks | Low | Critical | Append-only table (no UPDATE/DELETE via RLS); application user has INSERT only |
| **Repudiation** | Database admin modifies records without trace | Low | High | Database audit logging enabled; admin access requires MFA and is logged |
| **Information Disclosure** | SQL injection exposes data across tables | Medium | Critical | Parameterized queries exclusively (no string concatenation); ORM with SQLAlchemy |
| **Denial of Service** | Slow queries lock tables or exhaust connections | Medium | Medium | Connection pool limits; query timeout (30s); index coverage for all query patterns |
| **Elevation of Privilege** | Application user escalates to database superuser | Low | Critical | Separate DB users: `app_user` (DML only), `migration_user` (DDL), `admin_user` (superuser, break-glass) |

---

## 8. Attack Surface Analysis

### 8.1 Entry Points

| # | Entry Point | Protocol | Exposed To | Authentication | Authorization |
|---|---|---|---|---|---|
| EP-1 | MCP stdio interface | stdio (local) | Claude Code / AI clients on same machine | API key in MCP config | Tool-level RBAC |
| EP-2 | MCP streamable-http | HTTPS (port 443) | Remote MCP clients | API key in Authorization header | Tool-level RBAC |
| EP-3 | REST API | HTTPS (port 8080) | Dashboard, external integrations | JWT | Route-level RBAC |
| EP-4 | Streamlit Dashboard | HTTPS (port 8501) | Browser users (Anika, David, Fatima) | Session cookie | Page-level RBAC |
| EP-5 | Prometheus metrics | HTTP (port 9090) | Internal monitoring | None (network isolation) | Read-only metrics |
| EP-6 | Database | TCP (port 5432) | Application services only | Connection string | Database role-based |

### 8.2 Attack Surface Reduction Measures

| Measure | Implementation |
|---|---|
| Network segmentation | Database in isolated subnet, no direct internet access |
| Minimal exposed ports | Only ports 443 (MCP-HTTP), 8080 (REST), 8501 (Dashboard) externally |
| No admin endpoints on public interfaces | Admin operations require VPN or bastion host |
| Dependencies minimized | SBOM tracked; unused dependencies removed quarterly |
| Debug endpoints disabled in production | `/debug/*` routes return 404 outside `dev` environment |

---

## 9. OWASP Top 10 Mitigations

| # | OWASP Category | Platform Risk | Mitigation |
|---|---|---|---|
| A01 | Broken Access Control | High — multi-role system with agent tiers | RBAC middleware on all routes; row-level security in PostgreSQL; agent tier enforcement in shared service |
| A02 | Cryptographic Failures | Medium — secrets in env vars, data at rest | AES-256 encryption for C2+ data at rest; TLS 1.2+ in transit; JWT signed with HS256; secret rotation policy |
| A03 | Injection | High — user input flows to LLM prompts and SQL queries | Parameterized SQL (SQLAlchemy ORM); prompt template sanitization; input validation via JSON Schema |
| A04 | Insecure Design | Medium — AI agent autonomy creates novel design risks | Maturity tier model (T0-T3); budget ceilings; human approval gates; defense-in-depth at every layer |
| A05 | Security Misconfiguration | Medium — multi-environment deployment | Infrastructure-as-Code (Terraform); hardened base images; security headers on all HTTP responses; CSP policy |
| A06 | Vulnerable and Outdated Components | Medium — Python ecosystem, npm (Streamlit) | Dependabot alerts; SBOM generation; vulnerability scanning in CI; 7-day SLA for critical CVEs |
| A07 | Identification and Authentication Failures | Medium — multiple auth mechanisms | JWT with short expiry; API key rotation; session timeout; account lockout after 5 failed attempts |
| A08 | Software and Data Integrity Failures | High — agent outputs become downstream inputs | Output quality scoring; hash verification on generated documents; signed agent manifests; CI integrity checks |
| A09 | Security Logging and Monitoring Failures | Low (well-addressed) — core platform capability | Immutable `audit_events`; structured JSON logs; OpenTelemetry tracing; real-time anomaly detection |
| A10 | Server-Side Request Forgery | Low — limited outbound connections | Allowlist of outbound destinations (LLM provider URLs only); no user-controlled URLs in agent prompts |

---

## 10. Data Governance

### 10.1 Retention Policies

| Data Category | Table / Store | Retention Period | Deletion Method | Justification |
|---|---|---|---|---|
| Audit trail | `audit_events` | 1 year | Automated archival to cold storage, then deletion | SOC2 and EU AI Act require 1-year retention |
| Cost metrics | `cost_metrics` | 90 days | Automated deletion via pg_cron job | Operational data; monthly aggregates preserved indefinitely |
| Session context | `session_context` | 7 days | Automated deletion via pg_cron job | Ephemeral execution state; contains project brief excerpts |
| Pipeline checkpoints | `pipeline_checkpoints` | 30 days | Automated deletion via pg_cron job | Resume capability; stale checkpoints serve no purpose |
| MCP call events | `mcp_call_events` | 90 days | Automated deletion via pg_cron job | Telemetry data; aggregated metrics preserved indefinitely |
| Generated documents | File system | 1 year (aligned with audit trail) | Archive to object storage, then deletion | Customer deliverables; retention matches audit trail |
| Structured logs | JSONL files | 90 days | Log rotation and deletion | Backup of audit trail; primary source is database |
| Pipeline runs | `pipeline_runs` | 1 year | Automated archival | Business records; linked to audit trail |
| Pipeline steps | `pipeline_steps` | 1 year | Automated archival (cascades from pipeline_runs) | Linked to pipeline_runs |
| Agent registry | `agent_registry` | Indefinite | Manual removal when agent decommissioned | Platform configuration; 48 rows |
| Knowledge exceptions | `knowledge_exceptions` | Indefinite | Manual review and pruning annually | Organizational knowledge; grows slowly |
| Approval requests | `approval_requests` | 1 year | Automated archival | Governance records; linked to audit trail |

### 10.2 GDPR Compliance

| GDPR Requirement | Implementation |
|---|---|
| **Right to Access (Art. 15)** | API endpoint `GET /api/gdpr/export?subject_id=X` exports all data associated with a data subject |
| **Right to Erasure (Art. 17)** | Deletion propagation: `session_context` -> `pipeline_runs` -> `pipeline_steps` -> `generated_documents` (file system). `audit_events` anonymized (PII fields hashed) rather than deleted to preserve audit integrity |
| **Right to Rectification (Art. 16)** | `session_context` and `pipeline_runs` support update of PII fields; `audit_events` append a correction record |
| **Data Minimization (Art. 5.1c)** | Project briefs stripped of unnecessary PII before agent processing; PII scanner runs before `session_context` write |
| **Purpose Limitation (Art. 5.1b)** | Data collected only for declared purposes (document generation, cost tracking, audit); no secondary use |
| **Storage Limitation (Art. 5.1e)** | Retention policies enforced via automated pg_cron jobs (see 10.1) |
| **Data Protection Impact Assessment** | DPIA completed for the agent processing pipeline; reviewed annually |

### 10.3 GDPR Deletion Propagation

```
DELETE request for subject_id = X
       |
       v
[1] session_context: DELETE WHERE project_id IN (SELECT id FROM projects WHERE owner_id = X)
       |
       v
[2] pipeline_runs: DELETE WHERE project_id IN (...)
       |--- CASCADE: pipeline_steps, pipeline_checkpoints
       |
       v
[3] Generated documents: rm -rf reports/{project_id}/
       |
       v
[4] audit_events: UPDATE SET details = anonymize(details) WHERE project_id IN (...)
       |--- Note: audit_events are anonymized, NOT deleted (compliance requirement)
       |
       v
[5] cost_metrics: DELETE WHERE project_id IN (...)
       |
       v
[6] approval_requests: DELETE WHERE pipeline_run_id IN (...)
       |
       v
[7] knowledge_exceptions: UPDATE SET description = anonymize(description) WHERE project_id IN (...)
       |
       v
[8] Log deletion event in audit_events with action = 'gdpr.erasure'
```

### 10.4 AI Training Data Policy

| Rule | Enforcement |
|---|---|
| Confidential (C3) data NEVER sent to external LLM providers | Data classification check in LLM adapter; C3 routes to Ollama |
| Restricted (C4) data NEVER processed by any LLM | C4 data excluded from all agent processing paths |
| Anthropic API: opt out of training | `anthropic-beta: no-training` header on all API calls |
| OpenAI API: opt out of training | Organization-level data usage policy set to `opt-out` |
| Customer project briefs: anonymize before LLM processing | PII scanner strips names, emails, phone numbers before prompt assembly |
| Generated outputs: no re-ingestion for model fine-tuning | Platform does not collect outputs for training; policy documented in DPA |

---

## 11. Supply Chain Security

### 11.1 SBOM Generation

| Aspect | Implementation |
|---|---|
| Tool | `syft` for Python packages, `npm audit` for Streamlit frontend dependencies |
| Format | SPDX 2.3 and CycloneDX 1.4 |
| Frequency | Generated on every CI build; stored as build artifact |
| Storage | Artifact registry alongside container images |
| Review | Automated vulnerability scan against SBOM on every PR |

### 11.2 Vulnerability Scanning SLAs

| Severity | Detection | Patch SLA | Escalation |
|---|---|---|---|
| Critical (CVSS 9.0+) | Real-time (Dependabot + CI scan) | 24 hours | Immediate escalation to platform team lead |
| High (CVSS 7.0-8.9) | Real-time | 7 days | Escalation if not patched within 5 days |
| Medium (CVSS 4.0-6.9) | Daily scan | 30 days | Included in sprint planning |
| Low (CVSS 0.1-3.9) | Weekly scan | 90 days | Best effort |

### 11.3 Dependency Management

| Practice | Implementation |
|---|---|
| Pinned dependencies | `requirements.txt` with exact versions; `poetry.lock` for dependency resolution |
| Dependency review on PR | GitHub Dependency Review Action blocks PRs introducing known vulnerabilities |
| Minimal dependency tree | Quarterly review to remove unused packages; prefer standard library over third-party |
| Container base image | `python:3.11-slim` with security patches; rebuilt weekly |

---

## 12. Compliance Scope

### 12.1 Compliance Matrix

| Framework | Applicability | Scope | Target Date | Key Requirements |
|---|---|---|---|---|
| **SOC2 Type II** | Applicable (enterprise customers require it) | All platform components, all data stores | 2027-Q1 | Access controls (CC6), audit logging (CC7), change management (CC8), availability (A1) |
| **GDPR** | Applicable (EU customer data in project briefs) | `session_context`, `pipeline_runs`, generated documents, `audit_events` | Ongoing | Data minimization, right to erasure, DPA, DPIA, breach notification (72h) |
| **EU AI Act** | Mandatory (AI system making decisions affecting workflow) | Agent runtime, approval gates, maturity progression, audit trail | August 2026 | Risk classification (Art. 6), human oversight (Art. 14), transparency (Art. 13), technical documentation (Art. 11), logging (Art. 12) |

### 12.2 EU AI Act Compliance Detail

| Article | Requirement | Platform Implementation |
|---|---|---|
| Art. 6 | Risk classification | Platform classified as Limited Risk (AI system for content generation). Self-assessment documented. |
| Art. 9 | Risk management system | G1-cost-tracker + G5-quality-gate-enforcer + G7-compliance-monitor form the risk management system |
| Art. 11 | Technical documentation | 24-document SDLC stack serves as technical documentation; auto-generated and version-controlled |
| Art. 12 | Record-keeping (logging) | `audit_events` table provides immutable, complete logging of all AI agent actions |
| Art. 13 | Transparency | Agent manifests declare capabilities, data access, and autonomy tier; visible via Dashboard and MCP |
| Art. 14 | Human oversight | Approval gates at configurable pipeline steps; T0-T1 agents require human approval on all outputs |
| Art. 52 | Transparency obligations | Generated documents clearly marked as AI-generated with agent_id, model, and confidence score |

### 12.3 SOC2 Control Mapping

| SOC2 Criteria | Platform Control | Evidence |
|---|---|---|
| CC6.1 — Logical access | RBAC matrix (Section 4); JWT/API key authentication (Section 3) | Access logs in `mcp_call_events` and `audit_events` |
| CC6.2 — Authentication | Multi-mechanism auth per interface (Section 3.1) | Auth configuration in IaC; login event logs |
| CC6.3 — Authorization | Role-based permission matrix (Section 4.2); agent tier model (Section 5) | RBAC test suite; agent permission audit logs |
| CC7.1 — Change detection | Immutable `audit_events`; Git-based change tracking for manifests | Audit trail reconciliation reports |
| CC7.2 — Monitoring | OpenTelemetry tracing; Prometheus metrics; Grafana dashboards | Monitoring configuration in IaC; alert history |
| CC8.1 — Change management | CI/CD pipeline with 9 stages; canary deployments; rollback procedures | Pipeline run history; deployment logs |
| A1.1 — Availability | Health checks; circuit breakers; auto-restart; DR plan (RPO 1h, RTO 4h) | Uptime metrics; DR test reports |
