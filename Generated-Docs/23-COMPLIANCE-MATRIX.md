# COMPLIANCE-MATRIX — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-29
**Document:** 23 (Extended) | Status: Draft
**Reads from:** ARCH (Doc 2), QUALITY (Doc 4), DATA-MODEL (Doc 9), GUARDRAILS-SPEC (Doc 22), FAULT-TOLERANCE (Doc 21)

---

## Table of Contents

1. [Overview](#1-overview)
2. [SOC 2 Trust Service Criteria](#2-soc-2-trust-service-criteria)
3. [GDPR Articles](#3-gdpr-articles)
4. [EU AI Act](#4-eu-ai-act)
5. [NIST AI Risk Management Framework](#5-nist-ai-risk-management-framework)
6. [Control-to-Feature Cross-Reference](#6-control-to-feature-cross-reference)
7. [Evidence Collection Procedures](#7-evidence-collection-procedures)
8. [Audit Readiness Checklist](#8-audit-readiness-checklist)
9. [Exception Log Format](#9-exception-log-format)
10. [Compliance Review Schedule](#10-compliance-review-schedule)

---

## 1. Overview

The Agentic SDLC Platform processes project specifications through 48 AI agents using external LLM providers. This compliance matrix maps regulatory and framework requirements to specific platform features, agents, database tables, API endpoints, and test cases.

### Compliance Scope

| Framework | Applicability | Primary Concern |
|-----------|--------------|-----------------|
| SOC 2 Type II | Platform operates as a SaaS tool processing customer project data | Security, availability, processing integrity of agent pipeline |
| GDPR | Platform may process personal data in project specifications | Data protection, right to erasure, processing records |
| EU AI Act | Platform uses AI systems for automated document generation | Transparency, human oversight, risk management |
| NIST AI RMF | Best-practice framework for AI risk management | Governance, measurement, risk mitigation |

### Compliance Responsibility Matrix

| Role | SOC 2 | GDPR | EU AI Act | NIST AI RMF |
|------|-------|------|-----------|-------------|
| Fatima (Compliance Officer) | Control owner | DPO delegate | AI Act compliance lead | RMF coordinator |
| David (DevOps) | Technical implementer | Technical measures | System monitoring | Measurement implementation |
| Jason (Tech Lead) | Architecture reviewer | Privacy by design | Technical documentation | Risk assessment |
| Priya (Platform Engineer) | Agent governance | Data processing logic | Agent transparency | Agent governance |
| Marcus (Delivery Lead) | Process compliance | Consent workflows | Human oversight | Management oversight |

---

## 2. SOC 2 Trust Service Criteria

### 2.1 Security (Common Criteria)

| Control ID | SOC 2 Criteria | Requirement | Platform Implementation | Evidence Source |
|-----------|---------------|-------------|------------------------|----------------|
| SOC-SEC-001 | CC6.1 | Logical access controls | API key authentication via `POST /api/v1/auth/token`; role-based access on all endpoints; RLS on PostgreSQL tables (`pipeline_runs`, `cost_metrics`, `audit_events`, `session_context`) | `audit_events` WHERE `action LIKE 'auth.%'` |
| SOC-SEC-002 | CC6.2 | Access provisioning | User creation via `POST /api/v1/auth/users`; role assignment (admin, engineer, viewer); G3-agent-lifecycle-manager controls agent permissions | `audit_events` WHERE `action = 'auth.user_created'` |
| SOC-SEC-003 | CC6.3 | Access removal | API key revocation via `DELETE /api/v1/auth/token/{id}`; immediate effect on all sessions (SESS-001 fault handling) | `audit_events` WHERE `action = 'auth.token_revoked'` |
| SOC-SEC-004 | CC6.6 | Protection against external threats | GR-IN-001 prompt injection detection; GR-IN-002 PII filtering; rate limiting (GR-GOV-004); WAF on production | Guardrail trigger events in `audit_events` |
| SOC-SEC-005 | CC6.7 | Restriction of data transmission | Data classification tiers (Public/Internal/Confidential/Restricted); Confidential/Restricted data routed to Ollama only (GR-IN-002) | `audit_events` WHERE `action = 'guardrail.pii_rerouted'` |
| SOC-SEC-006 | CC6.8 | Prevention of unauthorized software | Model pinning (GR-PR-003); approved model registry; agent manifests locked in version control | `agent_registry.model_id` + Git history |

### 2.2 Availability

| Control ID | SOC 2 Criteria | Requirement | Platform Implementation | Evidence Source |
|-----------|---------------|-------------|------------------------|----------------|
| SOC-AVL-001 | A1.1 | Processing capacity management | Rate limiting (GR-GOV-004); connection pool management (DB-002); load shedding (APP-005) | `audit_events` WHERE `action LIKE 'fault.%'` |
| SOC-AVL-002 | A1.2 | Recovery and continuity | DB failover (DB-001, RTO 60s); MCP server restart (APP-001, RTO 30s); pipeline checkpoints (`pipeline_checkpoints` table) | `audit_events` WHERE `action LIKE 'fault.%.recovered'` |
| SOC-AVL-003 | A1.3 | Recovery testing | Quarterly failover drills; chaos testing (GUARDRAILS-SPEC Section 7.2); rollback testing (MIGRATION-PLAN Section 8) | Chaos test reports + drill logs |

### 2.3 Processing Integrity

| Control ID | SOC 2 Criteria | Requirement | Platform Implementation | Evidence Source |
|-----------|---------------|-------------|------------------------|----------------|
| SOC-PI-001 | PI1.1 | Complete and accurate processing | Quality scoring (GR-OUT-005); hallucination detection (GR-OUT-001); JSON schema validation (GR-OUT-002) | `pipeline_steps.quality_score`; guardrail events |
| SOC-PI-002 | PI1.2 | System inputs validated | Input schema validation (GR-IN-003); token size limits (GR-IN-004) | Guardrail events in `audit_events` |
| SOC-PI-003 | PI1.3 | Processing error detection | Pipeline quality gates (FUNC-001); nightly reconciliation (CROSS-002); cost anomaly detection | `audit_events` WHERE `action LIKE 'pipeline.quality%'` |
| SOC-PI-004 | PI1.4 | Output completeness | 14-doc pipeline produces all required documents; `pipeline_steps` table tracks each step completion | `pipeline_steps` WHERE `run_id = ?` AND `status = 'completed'` |

### 2.4 Confidentiality

| Control ID | SOC 2 Criteria | Requirement | Platform Implementation | Evidence Source |
|-----------|---------------|-------------|------------------------|----------------|
| SOC-CON-001 | C1.1 | Identification of confidential data | Data classification in GR-IN-002 (Public/Internal/Confidential/Restricted); classification stored in `session_context.context_data` | `session_context` WHERE `context_data->>'classification' IN ('confidential','restricted')` |
| SOC-CON-002 | C1.2 | Disposal of confidential data | PII redaction (GR-OUT-003); session cleanup after pipeline completion; configurable data retention | `audit_events` WHERE `action = 'data.retention_purge'` |
| SOC-CON-003 | C1.3 | Confidentiality commitments | Confidential/Restricted data never sent to external LLM providers (Ollama-only routing) | `cost_metrics` WHERE `classification = 'confidential'` AND `provider != 'ollama'` (should return 0 rows) |

### 2.5 Privacy

| Control ID | SOC 2 Criteria | Requirement | Platform Implementation | Evidence Source |
|-----------|---------------|-------------|------------------------|----------------|
| SOC-PRI-001 | P1.1 | Privacy notice | Platform displays data handling notice on Dashboard login; API docs include privacy section | Dashboard UI + API documentation |
| SOC-PRI-002 | P3.1 | Collection limitation | Only project specification data collected; no unnecessary personal data; PII scanning on input (GR-IN-002) | `session_context` schema + GR-IN-002 logs |
| SOC-PRI-003 | P4.1 | Use and retention | Data used only for document generation; retention policy configurable per project; automated purge | `audit_events` WHERE `action = 'data.retention_purge'` |
| SOC-PRI-004 | P6.1 | Quality of personal data | PII accuracy not applicable (platform does not store PII as primary data; any PII in specs is incidental) | GR-IN-002 PII detection logs |

---

## 3. GDPR Articles

| Control ID | GDPR Article | Requirement | Platform Implementation | Evidence Source |
|-----------|-------------|-------------|------------------------|----------------|
| GDPR-001 | Art. 5 (Principles) | Lawfulness, fairness, transparency; purpose limitation; data minimization | Data classification (GR-IN-002); purpose-limited processing (document generation only); no surplus data collection | `session_context` schema; data flow documentation |
| GDPR-002 | Art. 6 (Lawful basis) | Legal basis for processing | Legitimate interest (internal tool); contract basis (if used for client projects); consent for external LLM processing | Consent records in `session_context.context_data` |
| GDPR-003 | Art. 13-14 (Information to data subject) | Transparency about processing | Dashboard privacy notice; API documentation; LLM provider disclosure (which provider processes which data) | Privacy notice content + `cost_metrics.provider` field |
| GDPR-004 | Art. 15 (Right of access) | Data subject access requests | `GET /api/v1/audit/events?subject_id={id}` returns all processing records for a data subject; `session_context` query by subject | DSAR endpoint + query results |
| GDPR-005 | Art. 17 (Right to erasure) | Right to be forgotten | `DELETE /api/v1/projects/{id}/data` purges `session_context`, `pipeline_runs`, `pipeline_steps`, generated files for a project; `audit_events` retained (legal obligation) with PII redacted | `audit_events` WHERE `action = 'gdpr.erasure_executed'` |
| GDPR-006 | Art. 25 (Data protection by design) | Privacy by design and default | GR-IN-002 PII filtering by default; Ollama routing for sensitive data; minimum data principle in agent prompts | Guardrail configuration + agent manifests |
| GDPR-007 | Art. 30 (Records of processing) | Processing activity records | `audit_events` table records every agent invocation with: purpose, data categories, recipients (LLM provider), retention period | `audit_events` full table |
| GDPR-008 | Art. 32 (Security of processing) | Appropriate technical measures | Encryption at rest (PostgreSQL TDE); encryption in transit (TLS 1.3); access controls (RLS); guardrails (all 4 layers) | Infrastructure config + guardrail audit trail |
| GDPR-009 | Art. 33-34 (Breach notification) | 72-hour breach notification | CROSS-003 multi-tenant leak detection; P0 incident response (FAULT-TOLERANCE Section 7.1); breach notification template | Incident response runbook + `audit_events` WHERE `action = 'security.tenant_isolation_violation'` |
| GDPR-010 | Art. 35 (DPIA) | Data protection impact assessment | DPIA completed for: (1) external LLM processing of specs, (2) automated document generation, (3) cost/usage analytics | DPIA document (maintained separately) |

---

## 4. EU AI Act

| Control ID | EU AI Act Requirement | Risk Level | Platform Implementation | Evidence Source |
|-----------|----------------------|------------|------------------------|----------------|
| EUAI-001 | Art. 9 — Risk management system | Limited Risk (document generation tool) | NIST AI RMF implementation (Section 5); GUARDRAILS-SPEC (Doc 22) 4-layer guardrail system; quarterly risk reviews | Risk register + guardrail audit trail |
| EUAI-002 | Art. 10 — Data governance | Limited Risk | Data classification (GR-IN-002); input validation (GR-IN-003); training data not stored (uses pre-trained models via API) | Data classification logs + GR-IN-003 events |
| EUAI-003 | Art. 11 — Technical documentation | Limited Risk | Full documentation set (14 core docs + extended docs 20-23); agent manifests with model versions; ARCH (Doc 2) system design | Generated-Docs/ directory; `agent_registry` table |
| EUAI-004 | Art. 13 — Transparency | Limited Risk | Dashboard shows: which agent generated each document, which LLM model was used, quality scores, cost; all in `pipeline_steps` | `pipeline_steps` fields: `agent_id`, `model`, `quality_score`, `cost_usd` |
| EUAI-005 | Art. 14 — Human oversight | Limited Risk | HITL gates (GR-GOV-002): T0-T3 autonomy tiers; approval workflow via `approval_requests`; kill switches (GR-GOV-001) | `approval_requests` table; `audit_events` WHERE `action LIKE 'governance.%'` |
| EUAI-006 | Art. 15 — Accuracy and robustness | Limited Risk | Quality scoring (GR-OUT-005); hallucination detection (GR-OUT-001); adversarial testing (GUARDRAILS-SPEC Section 7.1) | `pipeline_steps.quality_score`; test reports |
| EUAI-007 | Art. 16-22 — Provider obligations | Limited Risk | Model pinning (GR-PR-003); provider health monitoring (GR-PR-004); audit trail of all LLM interactions (GR-GOV-003) | `cost_metrics` (provider, model); `mcp_call_events` |
| EUAI-008 | Art. 52 — Transparency for AI-generated content | Limited Risk | All generated documents include header: "Generated by Agentic SDLC Platform — Agent: {agent_id}, Model: {model}"; watermark metadata | Document headers + `pipeline_steps` metadata |
| EUAI-009 | Art. 69 — Codes of conduct | Limited Risk | ENFORCEMENT (Doc 12) defines agent behavior rules; agent rubrics (`rubric.yaml`) define scoring criteria | `agents/{id}/rubric.yaml` + ENFORCEMENT doc |

---

## 5. NIST AI Risk Management Framework

### 5.1 GOVERN Function

| Control ID | NIST AI RMF | Subcategory | Platform Implementation | Evidence Source |
|-----------|-------------|-------------|------------------------|----------------|
| NIST-GOV-001 | GOVERN 1 | Policies and processes | ENFORCEMENT (Doc 12) rules; CLAUDE (Doc 3) coding standards; agent manifests define agent boundaries | Generated-Docs/12-ENFORCEMENT.md + manifests |
| NIST-GOV-002 | GOVERN 2 | Accountability structures | Compliance responsibility matrix (Section 1); G3-agent-lifecycle-manager manages agent governance; Fatima as compliance owner | This document Section 1; `agent_registry` |
| NIST-GOV-003 | GOVERN 3 | Workforce diversity and expertise | 5 personas with distinct roles (Priya, Marcus, Jason, Anika, David, Fatima); cross-functional review in approval gates | PRD (Doc 1) persona definitions |
| NIST-GOV-004 | GOVERN 4 | Organizational culture | Transparency-first: all agent actions audited; quality scores visible; cost visible; no black-box processing | Dashboard pages; `audit_events` |
| NIST-GOV-005 | GOVERN 5 | Engagement with stakeholders | Approval Queue page for stakeholder review; Slack notifications; pipeline gate assignments | `approval_requests` table; notification logs |

### 5.2 MAP Function

| Control ID | NIST AI RMF | Subcategory | Platform Implementation | Evidence Source |
|-----------|-------------|-------------|------------------------|----------------|
| NIST-MAP-001 | MAP 1 | Context and intended use | PRD (Doc 1) defines platform purpose; each agent manifest defines specific scope and constraints | Generated-Docs/01-PRD.md; agent manifests |
| NIST-MAP-002 | MAP 2 | AI system categorization | Agents categorized by phase (GOVERN/DESIGN/BUILD/TEST/DEPLOY); risk-tiered by autonomy (T0-T3) | `agent_registry.phase`, `agent_registry.autonomy_tier` |
| NIST-MAP-003 | MAP 3 | Benefits and costs assessed | G1-cost-tracker provides real-time cost visibility; quality scoring measures benefit; Cost Monitor dashboard | `cost_metrics` table; `pipeline_steps.quality_score` |
| NIST-MAP-004 | MAP 5 | Impact characterization | FAULT-TOLERANCE (Doc 21) defines impact per fault scenario; priority-based (P0/P1/P2) | Doc 21 fault definitions |

### 5.3 MEASURE Function

| Control ID | NIST AI RMF | Subcategory | Platform Implementation | Evidence Source |
|-----------|-------------|-------------|------------------------|----------------|
| NIST-MEA-001 | MEASURE 1 | Appropriate metrics identified | Quality dimensions: schema compliance, completeness, faithfulness, consistency (GR-OUT-005); cost per run; error rates | QUALITY (Doc 4) metrics |
| NIST-MEA-002 | MEASURE 2 | AI systems evaluated | Quality gate at every pipeline step; adversarial test suite (GUARDRAILS-SPEC Section 7.1); red team quarterly | Test reports; `pipeline_steps.quality_score` |
| NIST-MEA-003 | MEASURE 3 | Mechanisms for tracking metrics | `cost_metrics` table (cost tracking); `pipeline_steps` (quality tracking); `audit_events` (event tracking); `mcp_call_events` (tool tracking) | Database tables + Dashboard |
| NIST-MEA-004 | MEASURE 4 | Feedback incorporated | Pipeline retry with quality feedback (FUNC-001); agent prompt tuning based on quality scores; G4-team-orchestrator adapts pipeline | `audit_events` WHERE `action LIKE 'pipeline.quality%'` |

### 5.4 MANAGE Function

| Control ID | NIST AI RMF | Subcategory | Platform Implementation | Evidence Source |
|-----------|-------------|-------------|------------------------|----------------|
| NIST-MAN-001 | MANAGE 1 | Risks prioritized and responded to | Fault tolerance 5-layer model (Doc 21); P0/P1/P2 prioritization; automated recovery for all P0 | FAULT-TOLERANCE doc |
| NIST-MAN-002 | MANAGE 2 | Risk mitigation planned and implemented | Guardrails (Doc 22) 4-layer mitigation; kill switches (GR-GOV-001); HITL gates (GR-GOV-002) | GUARDRAILS-SPEC doc |
| NIST-MAN-003 | MANAGE 3 | Risks managed and monitored | Real-time Fleet Health dashboard; Cost Monitor dashboard; audit log; PagerDuty alerts | Dashboard pages; alert configuration |
| NIST-MAN-004 | MANAGE 4 | Regular risk reassessment | Quarterly compliance review (Section 10); red team exercises; chaos testing | Review schedule; test reports |

---

## 6. Control-to-Feature Cross-Reference

This table maps compliance controls to specific platform features (F-NNN from FEATURE-CATALOG), implementing agents, and test cases.

| Control ID | Feature(s) | Agent(s) | API Endpoint(s) | DB Table(s) | Test Case(s) |
|-----------|-----------|----------|-----------------|-------------|-------------|
| SOC-SEC-001 | F-024, F-025 | G3-agent-lifecycle-manager | `POST /api/v1/auth/token` | `audit_events` | `test_auth_token_required`, `test_rls_enforcement` |
| SOC-SEC-004 | F-030 | All agents (guardrail layer) | All endpoints | `audit_events` | `test_prompt_injection_blocked`, `test_pii_filtered` |
| SOC-SEC-005 | F-031 | G1-cost-tracker | `GET /api/v1/cost/report` | `cost_metrics` | `test_confidential_data_ollama_only` |
| SOC-AVL-002 | F-032 | G4-team-orchestrator | `POST /api/v1/pipelines/{id}/resume` | `pipeline_checkpoints` | `test_pipeline_resume_from_checkpoint` |
| SOC-PI-001 | F-001, F-002 | All pipeline agents | `GET /api/v1/pipelines/{id}/steps` | `pipeline_steps` | `test_quality_score_above_threshold` |
| SOC-PI-003 | F-014, F-015 | G1-cost-tracker | `GET /api/v1/cost/report` | `cost_metrics` | `test_nightly_reconciliation` |
| SOC-CON-003 | F-031 | All agents | N/A (internal routing) | `cost_metrics` | `test_no_confidential_to_external_provider` |
| GDPR-004 | F-020 | G2-audit-trail-validator | `GET /api/v1/audit/events` | `audit_events` | `test_dsar_returns_all_subject_data` |
| GDPR-005 | F-033 | G2-audit-trail-validator | `DELETE /api/v1/projects/{id}/data` | `session_context`, `pipeline_runs` | `test_erasure_purges_all_project_data` |
| GDPR-007 | F-020 | G2-audit-trail-validator | `GET /api/v1/audit/events` | `audit_events` | `test_audit_trail_complete` |
| EUAI-004 | F-001 | All pipeline agents | `GET /api/v1/pipelines/{id}/steps` | `pipeline_steps` | `test_generated_doc_has_agent_attribution` |
| EUAI-005 | F-024 | G4-team-orchestrator | `POST /api/v1/approvals/{id}/approve` | `approval_requests` | `test_hitl_gate_blocks_until_approved` |
| EUAI-006 | F-002 | All pipeline agents | `GET /api/v1/pipelines/{id}/steps` | `pipeline_steps` | `test_hallucination_detection`, `test_quality_scoring` |
| NIST-GOV-002 | F-008, F-009 | G3-agent-lifecycle-manager | `GET /api/v1/agents` | `agent_registry` | `test_agent_lifecycle_transitions` |
| NIST-MEA-003 | F-014, F-020 | G1-cost-tracker, G2-audit-trail-validator | `GET /api/v1/cost/report`, `GET /api/v1/audit/events` | `cost_metrics`, `audit_events` | `test_cost_tracking_accuracy`, `test_audit_completeness` |

---

## 7. Evidence Collection Procedures

### 7.1 Automated Evidence Collection

Evidence is continuously collected from platform operations. No manual evidence gathering needed for most controls.

| Evidence Type | Source | Collection Method | Storage | Retention |
|--------------|--------|-------------------|---------|-----------|
| Access logs | `audit_events` WHERE `action LIKE 'auth.%'` | Continuous (append-only) | PostgreSQL + JSONL backup | 2 years |
| Agent invocation logs | `audit_events` WHERE `action LIKE 'agent.%'` | Continuous | PostgreSQL + JSONL backup | 2 years |
| Cost records | `cost_metrics` | Continuous | PostgreSQL | 2 years |
| Quality scores | `pipeline_steps.quality_score` | Per pipeline step | PostgreSQL | 1 year |
| Guardrail trigger logs | `audit_events` WHERE `action LIKE 'guardrail.%'` | Continuous | PostgreSQL + JSONL backup | 2 years |
| Pipeline run history | `pipeline_runs` + `pipeline_steps` | Per pipeline run | PostgreSQL | 1 year |
| Approval records | `approval_requests` | Per approval action | PostgreSQL | 2 years |
| System health history | `GET /api/v1/system/health` response logs | Every 10 seconds | JSONL files | 90 days |
| MCP call history | `mcp_call_events` | Per MCP call | PostgreSQL | 90 days |

### 7.2 Evidence Export for Audit

```bash
# Export audit evidence for a specific time period
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.agentic-sdlc.io/api/v1/audit/export?from=2026-01-01&to=2026-03-31&format=csv" \
  -o audit_evidence_q1_2026.csv

# Export cost evidence
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.agentic-sdlc.io/api/v1/cost/export?from=2026-01-01&to=2026-03-31&format=csv" \
  -o cost_evidence_q1_2026.csv

# Export guardrail trigger summary
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.agentic-sdlc.io/api/v1/audit/events?action=guardrail.*&from=2026-01-01&to=2026-03-31" \
  -o guardrail_evidence_q1_2026.json
```

### 7.3 Evidence Integrity

| Measure | Implementation |
|---------|---------------|
| Tamper detection | `audit_events` is append-only; no UPDATE or DELETE allowed; G2-audit-trail-validator verifies integrity |
| Hash chain | Each audit event includes `prev_event_hash` for sequential integrity verification |
| Backup verification | Nightly backup of `audit_events` to JSONL; hash comparison on restore |
| Access control | Evidence export requires `admin` or `compliance` role |

---

## 8. Audit Readiness Checklist

Run this checklist before any external audit. All items must pass.

### 8.1 Technical Readiness

| # | Check | Verification Command | Expected Result | Owner |
|---|-------|---------------------|-----------------|-------|
| 1 | All 48 agents registered | `GET /api/v1/agents` | 48 agents, all `status: active` | Priya |
| 2 | Audit trail continuous | `SELECT MIN(created_at), MAX(created_at), COUNT(*) FROM audit_events` | No gaps > 1 hour in the audit period | David |
| 3 | Cost reconciliation passing | Run CROSS-002 reconciliation query | Delta < $0.01 for all days | David |
| 4 | Guardrails active | `GET /api/v1/system/health` | All guardrail layers `active` | Priya |
| 5 | RLS enforced | Attempt cross-project query without RLS | Query returns 0 rows | David |
| 6 | Encryption at rest | Verify PostgreSQL TDE status | `on` | David |
| 7 | Encryption in transit | Verify TLS 1.3 on all endpoints | TLS 1.3 confirmed | David |
| 8 | Backup tested | Restore latest backup to staging | Restore successful, data matches | David |
| 9 | Kill switches functional | Test per-agent and global kill switches | Agent calls rejected when disabled | Priya |
| 10 | HITL gates functional | Trigger T2 pipeline step | Pauses for approval, resumes after | Jason |

### 8.2 Documentation Readiness

| # | Document | Location | Current | Owner |
|---|----------|----------|---------|-------|
| 1 | System architecture | `Generated-Docs/02-ARCH.md` | v1.0 | Jason |
| 2 | Data model | `Generated-Docs/09-DATA-MODEL.md` | v1.0 | Jason |
| 3 | API contracts | `Generated-Docs/10-API-CONTRACTS.md` | v1.0 | Jason |
| 4 | Fault tolerance | `Generated-Docs/21-FAULT-TOLERANCE.md` | v1.0 | David |
| 5 | Guardrails spec | `Generated-Docs/22-GUARDRAILS-SPEC.md` | v1.0 | Priya |
| 6 | This compliance matrix | `Generated-Docs/23-COMPLIANCE-MATRIX.md` | v1.0 | Fatima |
| 7 | DPIA (GDPR) | Maintained separately | Current | Fatima |
| 8 | Incident response plan | FAULT-TOLERANCE Section 7 | v1.0 | David |
| 9 | Agent manifests | `agents/{phase}/{id}/manifest.yaml` | Per agent | Priya |
| 10 | Quality rubrics | `agents/{phase}/{id}/rubric.yaml` | Per agent | Jason |

### 8.3 Process Readiness

| # | Process | Evidence | Frequency | Owner |
|---|---------|----------|-----------|-------|
| 1 | Access review | User list + role audit | Quarterly | Fatima |
| 2 | Guardrail adversarial testing | Test report | Monthly | Priya |
| 3 | Red team exercise | Findings report | Quarterly | External + Jason |
| 4 | Chaos testing | Test report | Monthly (automated), quarterly (manual) | David |
| 5 | Compliance review | Review minutes | Quarterly (Section 10) | Fatima |
| 6 | Incident post-mortems | Post-mortem documents | Per P0/P1 incident | David |
| 7 | Agent quality trending | Quality score dashboard export | Monthly | Jason |
| 8 | Cost anomaly review | Cost anomaly report | Weekly | Marcus |

---

## 9. Exception Log Format

When a compliance control cannot be fully met, an exception is logged.

### 9.1 Exception Record Schema

```json
{
  "exception_id": "EXC-2026-001",
  "control_id": "SOC-SEC-005",
  "title": "Temporary external LLM processing of internal data",
  "description": "During migration Phase 2, some internal-classified project specs were processed by Anthropic API due to Ollama capacity constraints",
  "risk_level": "medium",
  "status": "open",
  "raised_by": "fatima",
  "raised_date": "2026-03-29",
  "review_date": "2026-04-15",
  "compensating_controls": [
    "PII scanning (GR-IN-002) active on all inputs",
    "All calls logged in audit_events with provider field",
    "Data limited to architecture specifications (no PII)"
  ],
  "remediation_plan": "Scale Ollama cluster to handle internal workload by 2026-04-15",
  "approved_by": "jason",
  "approval_date": "2026-03-30",
  "expiry_date": "2026-04-30",
  "related_audit_events": ["evt-abc-123", "evt-def-456"]
}
```

### 9.2 Exception Storage

Exceptions are stored in the `knowledge_exceptions` table:

```sql
INSERT INTO knowledge_exceptions (
  exception_id, category, title, description, severity,
  status, raised_by, details, created_at
) VALUES (
  'EXC-2026-001', 'compliance', 'Temporary external LLM for internal data',
  'During migration Phase 2...', 'medium', 'open', 'fatima',
  '{"control_id": "SOC-SEC-005", "compensating_controls": [...], ...}'::jsonb,
  NOW()
);
```

### 9.3 Exception Lifecycle

```
RAISED → REVIEWED → APPROVED (with compensating controls)
                  → REJECTED (must remediate immediately)

APPROVED → REMEDIATED → CLOSED
         → EXPIRED → ESCALATED (if not remediated by expiry)
```

**Query active exceptions:**
```sql
SELECT exception_id, category, title, severity, status,
       details->>'control_id' as control_id,
       details->>'expiry_date' as expiry_date
FROM knowledge_exceptions
WHERE category = 'compliance'
  AND status IN ('open', 'approved')
ORDER BY severity, created_at;
```

---

## 10. Compliance Review Schedule

### 10.1 Regular Reviews

| Review Type | Frequency | Participants | Deliverable | Duration |
|------------|-----------|-------------|-------------|----------|
| Guardrail effectiveness | Monthly | Priya, Jason | Guardrail metrics report | 30 min |
| Cost compliance | Monthly | Marcus, Fatima | Cost anomaly report | 30 min |
| Access review | Quarterly | Fatima, David | User access audit report | 60 min |
| Full compliance review | Quarterly | All compliance team | Updated compliance matrix | 120 min |
| Red team debrief | Quarterly | Jason, Priya, External | Red team findings + remediation | 90 min |
| DPIA review | Annually | Fatima, Jason | Updated DPIA document | 120 min |
| SOC 2 evidence prep | Annually | Fatima, David | Evidence package for auditor | Full day |

### 10.2 Quarterly Compliance Review Agenda

| # | Agenda Item | Time | Owner |
|---|------------|------|-------|
| 1 | Review open exceptions (Section 9) | 15 min | Fatima |
| 2 | Review guardrail trigger metrics (last 90 days) | 15 min | Priya |
| 3 | Review incident post-mortems (last 90 days) | 15 min | David |
| 4 | Review quality score trends | 10 min | Jason |
| 5 | Review cost trends and anomalies | 10 min | Marcus |
| 6 | Regulatory update scan (new SOC 2 guidance, GDPR enforcement, EU AI Act developments) | 15 min | Fatima |
| 7 | Update compliance matrix (this document) | 20 min | Fatima |
| 8 | Action items and next review date | 10 min | Fatima |

### 10.3 Compliance Metrics Dashboard

Tracked on the Audit Log dashboard page:

| Metric | Query | Target | Alert Threshold |
|--------|-------|--------|----------------|
| Open exceptions count | `SELECT COUNT(*) FROM knowledge_exceptions WHERE category = 'compliance' AND status IN ('open','approved')` | 0 | > 3 open |
| Overdue exceptions | `WHERE details->>'expiry_date' < NOW()` | 0 | Any overdue |
| Guardrail triggers / week | `SELECT COUNT(*) FROM audit_events WHERE action LIKE 'guardrail.%' AND created_at > NOW() - INTERVAL '7 days'` | Baseline +/- 20% | > 2x baseline |
| Audit trail gap hours | `SELECT MAX gap in audit_events sequence` | 0 hours | > 1 hour gap |
| Cross-tenant violations | `SELECT COUNT(*) FROM audit_events WHERE action = 'security.tenant_isolation_violation'` | 0 | Any violation |
| PII detections / month | `SELECT COUNT(*) FROM audit_events WHERE action LIKE 'guardrail.pii%'` | < 10 | > 25 |

---

*End of COMPLIANCE-MATRIX. This document is reviewed and updated quarterly (Section 10). Fatima (Compliance Officer) owns this document. All control IDs are stable — new controls are appended, never renumbered.*
