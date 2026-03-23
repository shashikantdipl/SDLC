# 04-QUALITY.md --- Non-Functional Requirements Specification

| Field | Value |
|---|---|
| **Document** | QUALITY-001 |
| **Title** | Agentic SDLC Platform --- Non-Functional Requirements |
| **Version** | 1.0.0 |
| **Date** | 2026-03-23 |
| **Status** | Draft |
| **Owner** | Sarah (Engineering Lead) |
| **Reviewers** | Priya (Platform Engineer), Marcus (DevOps), Lisa (Compliance Officer) |
| **Applies to** | All subsystems: SDK Runtime, Pipeline Orchestration, SessionStore, Dashboard, REST API, PostgreSQL schema |

---

## 1. Purpose

This document defines 36 non-functional requirements (NFRs) across eight quality categories for the Agentic SDLC Platform. Every NFR is specific, measurable, and includes an automated verification method. These requirements are binding for all code merged to `main` and are enforced through CI gates, runtime monitors, and periodic audits.

## 2. Conventions

- **NFR Identifier:** `Q-NNN` where NNN is a zero-padded sequence number.
- **Format:** `Q-NNN: [Category] --- [Imperative rule with specific threshold]. Verify: [automated verification method].`
- **Priority tiers:** P0 (launch blocker), P1 (required within 30 days of GA), P2 (required within 90 days of GA).
- **Measurement cadence:** Continuous (C) = every invocation or request; Periodic (P) = scheduled job; Gate (G) = CI/CD pipeline check.

## 3. Summary Matrix

| Category | NFR Range | Count | P0 | P1 | P2 |
|---|---|---|---|---|---|
| Performance | Q-001 -- Q-006 | 6 | 3 | 2 | 1 |
| Reliability | Q-007 -- Q-012 | 6 | 4 | 2 | 0 |
| Security | Q-013 -- Q-018 | 6 | 5 | 1 | 0 |
| Accessibility | Q-019 -- Q-021 | 3 | 0 | 2 | 1 |
| Coverage | Q-022 -- Q-027 | 6 | 2 | 3 | 1 |
| Observability | Q-028 -- Q-032 | 5 | 3 | 2 | 0 |
| Data | Q-033 -- Q-036 | 4 | 3 | 1 | 0 |
| **Total** | | **36** | **20** | **13** | **3** |

---

## 4. Performance (Q-001 -- Q-006)

```
Q-001: Performance --- Agent invocation latency SHALL NOT exceed 30 seconds at p95
for haiku-tier agents or 120 seconds at p95 for opus-tier agents, measured from
SDK invoke() call to result return, excluding network transit to Claude API.
Verify: Prometheus histogram `agent_invocation_duration_seconds` bucketed by
agent_tier; CI runs a 50-invocation load test per tier and asserts p95 thresholds
via pytest-benchmark; Grafana alert fires if rolling 5-minute p95 exceeds limit.
```
**Priority:** P0 | **Cadence:** Continuous | **Owner:** Priya

```
Q-002: Performance --- A full 12-document pipeline run SHALL complete in less than
30 minutes wall-clock time, measured from pipeline_runs.started_at to
pipeline_runs.completed_at, when executed with default parallelism settings and
no human-approval gates pending.
Verify: Integration test `test_full_pipeline_e2e` executes all 12 agents against
golden inputs and asserts wall-clock < 1800s; production pipeline_runs table
queried nightly by a scheduled job that flags any run exceeding 30 minutes;
Grafana dashboard panel "Pipeline Duration p95" with 30-min threshold line.
```
**Priority:** P0 | **Cadence:** Continuous + Gate | **Owner:** Sarah

```
Q-003: Performance --- Dashboard initial page load SHALL complete in less than
3 seconds (DOMContentLoaded) and subsequent in-app navigation SHALL complete in
less than 500 milliseconds, measured via Lighthouse CI on a simulated 4G
connection with 4x CPU throttling.
Verify: Lighthouse CI GitHub Action runs on every PR touching `dashboard/**`;
asserts First Contentful Paint < 2s, Time to Interactive < 3s; Streamlit
performance profiler measures navigation transitions and asserts < 500ms;
synthetic monitoring (Playwright script) runs every 15 minutes in staging.
```
**Priority:** P1 | **Cadence:** Gate + Periodic | **Owner:** Priya

```
Q-004: Performance --- SessionStore read and write operations SHALL NOT exceed
50 milliseconds at p95, measured at the Python asyncpg call boundary including
connection acquisition from the pool.
Verify: Unit test `test_session_store_latency` runs 1000 read/write cycles and
asserts p95 < 50ms against a local PostgreSQL instance; production metric
`session_store_op_duration_ms` emitted on every call; Grafana alert if rolling
1-minute p95 exceeds 50ms.
```
**Priority:** P0 | **Cadence:** Continuous | **Owner:** Priya

```
Q-005: Performance --- ManifestLoader.validate() SHALL complete in less than
200 milliseconds per manifest file, including JSON Schema validation and
tool-permission cross-referencing.
Verify: Benchmark test `test_manifest_validation_speed` loads all 48 agent
manifests and asserts each validates in < 200ms; CI gate fails if any single
manifest exceeds threshold; metric `manifest_validation_ms` logged per load.
```
**Priority:** P1 | **Cadence:** Gate | **Owner:** Sarah

```
Q-006: Performance --- All non-LLM REST API endpoints (health, config, list,
status) SHALL respond in less than 200 milliseconds at p95 under a sustained
load of 100 concurrent requests.
Verify: Locust load test in CI targets `/health`, `/agents`, `/pipelines`,
`/cost` endpoints with 100 concurrent users for 60 seconds; asserts p95 < 200ms
and 0% error rate; production metric `api_response_duration_ms` partitioned by
endpoint with Grafana alerting.
```
**Priority:** P2 | **Cadence:** Gate + Continuous | **Owner:** Priya

---

## 5. Reliability (Q-007 -- Q-012)

```
Q-007: Reliability --- The platform SHALL maintain 99.5% monthly uptime for all
critical-path services (SDK runtime, pipeline orchestrator, SessionStore,
PostgreSQL), calculated as (total_minutes - downtime_minutes) / total_minutes
where downtime is defined as inability to accept and process new pipeline runs.
Verify: Uptime Robot or equivalent synthetic check pings /health every 60 seconds;
monthly SLA report auto-generated from check history; incident post-mortem
required for any downtime exceeding 15 minutes; status page updated automatically.
```
**Priority:** P0 | **Cadence:** Continuous | **Owner:** Marcus

```
Q-008: Reliability --- Pipeline execution SHALL resume from the last successful
checkpoint within 60 seconds of a platform restart, using data from the
pipeline_checkpoints table, without re-executing completed steps or losing
intermediate outputs.
Verify: Integration test `test_checkpoint_recovery` kills the orchestrator mid-
pipeline, restarts it, and asserts: (a) resumed within 60s, (b) no duplicate
agent invocations, (c) final output matches baseline; chaos engineering job
runs weekly in staging.
```
**Priority:** P0 | **Cadence:** Gate + Periodic | **Owner:** Sarah

```
Q-009: Reliability --- The circuit breaker for Claude API calls SHALL activate
within 5 seconds after 3 consecutive failures (HTTP 5xx, timeout, or connection
refused), shifting the agent to a queued-retry state with exponential backoff
(base 2s, max 60s, jitter +/- 500ms).
Verify: Unit test `test_circuit_breaker_activation` mocks 3 consecutive 503
responses and asserts breaker opens within 5s; test `test_circuit_breaker_backoff`
verifies retry intervals follow exponential schedule; production metric
`circuit_breaker_state` (closed/open/half-open) emitted on every transition.
```
**Priority:** P0 | **Cadence:** Continuous | **Owner:** Priya

```
Q-010: Reliability --- Recovery Point Objective (RPO) SHALL be 0 (zero data loss)
for audit_events via synchronous WAL commit, and less than 1 minute for
session_context and pipeline_runs via WAL archiving with 60-second segments.
Verify: PostgreSQL configured with `synchronous_commit = on` for audit_events;
WAL archive shipping lag monitored via `pg_stat_archiver`; restore drill
executed monthly verifying audit completeness to the transaction and session
data loss < 60s; automated test restores from backup and counts audit rows.
```
**Priority:** P0 | **Cadence:** Periodic (monthly drill) | **Owner:** Marcus

```
Q-011: Reliability --- If the Claude API becomes unreachable, the platform SHALL
NOT crash or lose data. Instead it SHALL: (a) queue pending invocations in
PostgreSQL, (b) activate circuit breaker per Q-009, (c) emit a structured warning
log, (d) return a degraded-mode status via /health, (e) automatically retry when
connectivity restores. No invocation SHALL be silently dropped.
Verify: Integration test `test_graceful_degradation` blocks Claude API DNS,
submits 10 invocations, restores DNS, and asserts all 10 eventually complete
with correct outputs; production alert fires if /health reports degraded for
more than 5 minutes.
```
**Priority:** P1 | **Cadence:** Gate + Periodic | **Owner:** Priya

```
Q-012: Reliability --- The asyncpg connection pool SHALL recover from a full
database restart within 10 seconds, re-establishing the minimum pool size
without manual intervention and without dropping in-flight requests that can
be retried.
Verify: Integration test `test_db_pool_recovery` restarts PostgreSQL, issues
requests, and asserts: (a) pool re-establishes within 10s, (b) retryable
requests succeed, (c) non-retryable requests return 503 (not 500 or hang);
production metric `db_pool_active_connections` monitored with alert on sustained
zero count.
```
**Priority:** P1 | **Cadence:** Gate + Periodic | **Owner:** Marcus

---

## 6. Security (Q-013 -- Q-018)

```
Q-013: Security --- Agent outputs SHALL contain zero secrets, PII, or sensitive
credentials. A PII/secret scanner SHALL execute on every agent output before it
is persisted to SessionStore or returned to the caller. Detected secrets SHALL
cause the output to be rejected, the invocation to be flagged in audit_events
with reason "secret_detected", and an alert to fire within 30 seconds.
Verify: Scanner runs regex + entropy-based detection (API keys, JWTs, SSNs,
emails, credit card numbers) via `detect-secrets` library integrated as a
post-processing hook in BaseAgent; unit tests with 20+ secret patterns assert
100% detection; CI gate runs `detect-secrets scan` on all test fixtures;
production metric `secret_detections_total` tracked with zero-tolerance alert.
```
**Priority:** P0 | **Cadence:** Continuous | **Owner:** Lisa

```
Q-014: Security --- Every REST API and WebSocket endpoint SHALL require valid
authentication. Public endpoints are limited to: GET /health (unauthenticated,
returns only {"status":"ok"}). All other endpoints SHALL validate a JWT bearer
token (RS256, max 1-hour expiry) or API key (SHA-256 hashed, stored in
agent_registry). Requests with missing, expired, or invalid credentials SHALL
receive HTTP 401 with no information leakage in the response body.
Verify: Integration test `test_auth_enforcement` iterates all registered routes
and asserts 401 for unauthenticated requests; OWASP ZAP scan runs in CI on
every release candidate; JWT expiry test confirms rejection of tokens older
than 3600 seconds.
```
**Priority:** P0 | **Cadence:** Gate + Periodic | **Owner:** Priya

```
Q-015: Security --- Row-Level Security (RLS) SHALL be enabled on all multi-tenant
tables (agent_registry, cost_metrics, audit_events, pipeline_runs,
session_context, approval_requests, pipeline_checkpoints, knowledge_exceptions).
Every query executed by the application SHALL run under a PostgreSQL role that
has RLS policies enforced, scoped by project_id and client_id. The superuser
role SHALL NOT be used by the application at runtime.
Verify: SQL migration test `test_rls_enforcement` connects as the application
role and asserts: (a) SELECT returns only rows matching the session's
project_id/client_id, (b) INSERT with mismatched tenant IDs is rejected,
(c) the application role is not a superuser; `pg_policies` catalog queried
in CI to confirm policies exist on all 8 tables.
```
**Priority:** P0 | **Cadence:** Gate | **Owner:** Marcus

```
Q-016: Security --- All external connections (Claude API, PostgreSQL if remote,
webhook callbacks, dashboard-to-API) SHALL use TLS 1.2 or higher. TLS 1.0 and
1.1 SHALL be disabled at the server configuration level. Certificate validation
SHALL NOT be disabled in any environment including development.
Verify: SSL Labs scan (or equivalent) runs against all exposed endpoints in CI;
`testssl.sh` script asserts no TLS 1.0/1.1 support; Python `ssl` context in
aiohttp configured with `ssl.PROTOCOL_TLS_CLIENT` and minimum_version =
TLSVersion.TLSv1_2; grep for `verify=False` or `ssl=False` in CI fails the
build if found in non-test code.
```
**Priority:** P0 | **Cadence:** Gate + Periodic | **Owner:** Marcus

```
Q-017: Security --- The project SHALL have zero critical or high severity CVEs in
production dependencies, as reported by `pip-audit` and `safety` scanners.
Medium-severity CVEs SHALL be triaged within 7 days. A Software Bill of
Materials (SBOM) in CycloneDX format SHALL be generated on every release.
Verify: `pip-audit --strict` and `safety check` run in CI on every PR and block
merge on critical/high findings; Dependabot or Renovate configured for
automated dependency PRs; SBOM generated via `cyclonedx-py` and stored as
release artifact; weekly scheduled scan of production dependencies.
```
**Priority:** P0 | **Cadence:** Gate + Periodic (weekly) | **Owner:** Sarah

```
Q-018: Security --- Tier-0 (T0) agents operating in autonomous mode SHALL NOT
have access to the Bash tool, file-system write operations, or network egress
beyond the Claude API. Tool permissions SHALL be declared in the agent manifest
and enforced by the SDK runtime before tool invocation. Any attempt by an agent
to invoke a disallowed tool SHALL be blocked, logged to audit_events, and
counted in metric `tool_permission_violations_total`.
Verify: Unit test `test_t0_tool_restrictions` loads every T0 agent manifest and
asserts Bash, file_write, and network tools are absent from allowed_tools;
integration test mocks a T0 agent attempting Bash and asserts the call is
blocked with an audit entry; CI gate scans all manifests for policy compliance.
```
**Priority:** P1 | **Cadence:** Gate | **Owner:** Lisa

---

## 7. Accessibility (Q-019 -- Q-021)

```
Q-019: Accessibility --- The Streamlit dashboard SHALL comply with WCAG 2.1 Level
AA success criteria for all interactive pages: fleet health, cost monitoring,
pipeline runs, audit logs, and approval queue. Non-compliant elements SHALL be
tracked as P1 bugs.
Verify: axe-core accessibility audit runs via Playwright on every dashboard PR,
scanning all 5 primary pages; CI gate fails on any Level A or AA violation;
quarterly manual audit by an accessibility specialist using NVDA screen reader;
results tracked in accessibility-audit.json artifact.
```
**Priority:** P1 | **Cadence:** Gate + Periodic (quarterly) | **Owner:** Priya

```
Q-020: Accessibility --- All interactive elements in the dashboard (buttons, links,
form controls, data tables, modal dialogs, approval actions) SHALL be fully
operable via keyboard alone, with visible focus indicators and logical tab order.
No keyboard traps SHALL exist.
Verify: Playwright test `test_keyboard_navigation` tabs through every interactive
element on each page and asserts: (a) all elements reachable, (b) focus
indicator visible (outline width >= 2px), (c) Escape closes modals, (d) no
element traps focus; axe-core "keyboard" rule group included in CI scan.
```
**Priority:** P1 | **Cadence:** Gate | **Owner:** Priya

```
Q-021: Accessibility --- All text and interactive elements in the dashboard SHALL
maintain a color contrast ratio of at least 4.5:1 for normal text and 3:1 for
large text (>= 18pt or >= 14pt bold), as defined by WCAG 2.1 SC 1.4.3.
Verify: axe-core contrast rules enforced in CI; Figma design tokens validated
against contrast checker before implementation; Playwright screenshot
comparison flags contrast regressions; CSS custom properties for all colors
centralized in a theme file for single-point-of-change.
```
**Priority:** P2 | **Cadence:** Gate | **Owner:** Priya

---

## 8. Coverage (Q-022 -- Q-027)

```
Q-022: Coverage --- The SDK core modules (base_agent.py, manifest_loader.py,
session_store.py, message_envelope.py, cost_tracker.py, tool_permissions.py)
SHALL maintain >= 90% line coverage and >= 85% branch coverage as measured by
coverage.py with the `--branch` flag.
Verify: `pytest --cov=sdk --cov-branch --cov-fail-under=90` runs in CI on every
PR; coverage report uploaded to Codecov; PR blocked if SDK core coverage drops
below 90% line or 85% branch; nightly trend report flags coverage regressions
> 1 percentage point.
```
**Priority:** P0 | **Cadence:** Gate | **Owner:** Sarah

```
Q-023: Coverage --- The pipeline orchestration modules (orchestrator.py,
scheduler.py, checkpoint_manager.py, parallel_executor.py) SHALL maintain
>= 85% line coverage and >= 80% branch coverage.
Verify: `pytest --cov=orchestration --cov-branch --cov-fail-under=85` in CI;
coverage delta reported on PRs touching orchestration code; merge blocked if
threshold not met.
```
**Priority:** P1 | **Cadence:** Gate | **Owner:** Sarah

```
Q-024: Coverage --- All REST API endpoint handlers and middleware (authentication,
rate limiting, error handling, request validation) SHALL maintain >= 80% line
coverage.
Verify: `pytest --cov=api --cov-fail-under=80` in CI; every new endpoint must
include tests for: (a) happy path, (b) 401 unauthenticated, (c) 400 invalid
input, (d) 500 internal error; PR template includes coverage checklist.
```
**Priority:** P1 | **Cadence:** Gate | **Owner:** Priya

```
Q-025: Coverage --- Dashboard Python code and Streamlit component logic SHALL
maintain >= 70% line coverage. Visual regression tests SHALL cover all 5
primary pages.
Verify: `pytest --cov=dashboard --cov-fail-under=70` in CI; Playwright visual
regression snapshots for fleet health, cost monitoring, pipeline runs, audit
logs, and approval queue pages; snapshot diff threshold set to 0.1% pixel
difference.
```
**Priority:** P2 | **Cadence:** Gate | **Owner:** Priya

```
Q-026: Coverage --- Every agent in the 48-agent fleet SHALL have at minimum:
(a) 3 golden-path test cases using curated input/expected-output pairs,
(b) 1 adversarial test case that supplies malformed, oversized, or prompt-
injection input and asserts graceful rejection. Golden tests SHALL assert
output confidence >= 0.85.
Verify: Test discovery script `scripts/verify_agent_tests.py` scans
`tests/agents/` and asserts each of the 48 agents has >= 3 files matching
`test_{agent}_golden_*.py` and >= 1 matching `test_{agent}_adversarial_*.py`;
CI gate fails if any agent is under-tested; test matrix in CI runs all agent
tests in parallel.
```
**Priority:** P0 | **Cadence:** Gate | **Owner:** Sarah

```
Q-027: Coverage --- Every named team pipeline (requirements, design, implementation,
testing, deployment, monitoring, compliance) SHALL have at least one end-to-end
integration test that executes the full pipeline against synthetic inputs and
asserts: (a) all expected documents produced, (b) pipeline status = "completed",
(c) cost within budget, (d) no checkpoint corruption.
Verify: Integration test suite `tests/integration/test_pipelines.py` contains
one test per pipeline; CI runs the full suite against a PostgreSQL test database;
pipeline names validated against pipeline_registry to ensure no pipeline is
untested; weekly nightly run against staging environment.
```
**Priority:** P1 | **Cadence:** Gate + Periodic (weekly) | **Owner:** Sarah

---

## 9. Observability (Q-028 -- Q-032)

```
Q-028: Observability --- Every agent invocation SHALL produce a structured JSONL
audit record containing exactly these 13 fields: timestamp, correlation_id,
agent_id, agent_tier, pipeline_run_id, project_id, client_id, action,
input_hash, output_hash, confidence_score, cost_usd, duration_ms. Records
SHALL be written to both the audit_events table and the JSONL log stream
within the same transaction.
Verify: Unit test `test_audit_record_schema` validates every field is present
and correctly typed on 100 sample invocations; integration test asserts audit
row count equals invocation count after a pipeline run; JSON Schema validator
runs on JSONL output in CI; production monitor alerts if any invocation lacks
a corresponding audit row within 5 seconds.
```
**Priority:** P0 | **Cadence:** Continuous | **Owner:** Lisa

```
Q-029: Observability --- Cost tracking SHALL be accurate to within 1% of actual
Claude API spend, reconciled daily. The cost_metrics table SHALL record
input_tokens, output_tokens, model, and unit_cost for every invocation. Daily
reconciliation SHALL compare platform-recorded cost against the Claude API
billing dashboard (via API) and flag discrepancies exceeding 1%.
Verify: Daily reconciliation job `scripts/reconcile_costs.py` queries Claude
billing API and cost_metrics table, computes delta, and asserts |delta| < 1%;
alert fires on breach; unit test mocks known token counts and asserts cost
calculation matches expected value to 4 decimal places.
```
**Priority:** P0 | **Cadence:** Continuous + Periodic (daily) | **Owner:** David

```
Q-030: Observability --- Every log line emitted by the platform SHALL be structured
JSON containing at minimum: timestamp (ISO-8601), level, logger, message, and
correlation_id. The correlation_id SHALL propagate across all function calls,
database queries, and external API calls within a single request or pipeline
step. Unstructured print() statements SHALL NOT exist in production code.
Verify: CI linter `scripts/lint_logging.py` scans all Python files for bare
print() calls and logging calls without correlation_id and fails the build;
integration test captures log output of a full pipeline run and asserts every
line parses as valid JSON with all 5 required fields; log aggregator (e.g.,
Loki) configured to reject non-JSON log lines.
```
**Priority:** P0 | **Cadence:** Gate + Continuous | **Owner:** Marcus

```
Q-031: Observability --- Pipeline step duration SHALL be recorded in the
pipeline_runs table (step_durations JSONB column) for every step, enabling
queries like "average duration of requirements-agent across all runs this week."
Step duration SHALL be measured from step dispatch to result receipt, inclusive
of queue wait time.
Verify: Integration test `test_step_duration_tracking` runs a 3-step pipeline
and asserts step_durations contains exactly 3 entries with duration_ms > 0;
SQL query test validates the JSONB structure; Grafana dashboard panel "Step
Duration Heatmap" renders correctly from production data.
```
**Priority:** P1 | **Cadence:** Continuous | **Owner:** Priya

```
Q-032: Observability --- The platform SHALL emit an alert within 60 seconds of any
budget threshold breach: (a) agent invocation cost > $0.50, (b) agent daily
cost > $5, (c) project daily cost > $20, (d) fleet daily cost > $50,
(e) pipeline run cost > $25. Alerts SHALL include: threshold name, current
value, limit, project_id, and recommended action.
Verify: Unit test `test_budget_alerts` injects cost records exceeding each
threshold and asserts alert emission within 60s with all required fields;
integration test with a mock alert sink verifies end-to-end delivery;
production alert channel (Slack/PagerDuty) confirmed operational via weekly
synthetic alert.
```
**Priority:** P1 | **Cadence:** Continuous | **Owner:** David

---

## 10. Data (Q-033 -- Q-036)

```
Q-033: Data --- The audit_events table SHALL be append-only. UPDATE and DELETE
operations SHALL be blocked by a PostgreSQL trigger that raises an exception.
The trigger SHALL exist in the migration baseline and SHALL NOT be removable
without a dual-approval PR from both Engineering Lead and Compliance Officer.
Verify: Migration test `test_audit_immutability` attempts UPDATE and DELETE on
audit_events and asserts both raise `RAISE EXCEPTION`; CI scans migration
files for any `DROP TRIGGER` on the immutability trigger and blocks merge;
weekly audit queries `pg_trigger` catalog to confirm trigger is active;
production monitoring alerts if trigger is disabled.
```
**Priority:** P0 | **Cadence:** Gate + Periodic (weekly) | **Owner:** Lisa

```
Q-034: Data --- Session context entries SHALL have a configurable TTL (default
86,400 seconds / 24 hours). Expired entries SHALL be purged by a scheduled
cleanup job running every hour. The cleanup job SHALL NOT lock the table for
more than 1 second and SHALL process deletions in batches of 1,000 rows.
Verify: Unit test `test_session_ttl_enforcement` inserts a record with TTL=1s,
waits 2s, runs cleanup, and asserts record is deleted; integration test
verifies batch deletion does not exceed 1s lock time via `pg_stat_activity`;
production metric `session_cleanup_rows_deleted` and
`session_cleanup_duration_ms` tracked per run.
```
**Priority:** P0 | **Cadence:** Periodic (hourly) | **Owner:** Priya

```
Q-035: Data --- Agent output size SHALL NOT exceed 100KB per invocation, measured
as the UTF-8 byte length of the serialized output payload. Outputs exceeding
100KB SHALL be truncated with a `[TRUNCATED]` marker and a warning logged.
The full output SHALL be stored in an overflow table (agent_output_overflow)
with a foreign key to the audit record.
Verify: Unit test `test_output_size_limit` generates a 150KB output and asserts:
(a) stored output is <= 100KB, (b) `[TRUNCATED]` marker present, (c) overflow
row exists with full content; CI gate scans golden test expected outputs and
warns if any exceed 80KB; production metric `agent_output_bytes` histogrammed
for capacity planning.
```
**Priority:** P0 | **Cadence:** Continuous | **Owner:** Sarah

```
Q-036: Data --- Data retention SHALL be enforced automatically: audit_events
retained for 365 days, session_context for 30 days, cost_metrics for 90 days.
A nightly retention job SHALL delete expired data in batches. Retention
periods SHALL be configurable via environment variables but SHALL NOT be
shortened below regulatory minimums (audit: 365 days per SOC2).
Verify: Retention job `scripts/enforce_retention.py` runs nightly; unit test
inserts records with timestamps beyond retention and asserts deletion after
job execution; integration test verifies audit records at 364 days are
retained and at 366 days are deleted; production metric
`retention_rows_deleted` by table tracked per run; compliance dashboard
displays current retention configuration.
```
**Priority:** P1 | **Cadence:** Periodic (nightly) | **Owner:** Lisa

---

## 11. Compliance Matrix

The following matrix maps NFRs to external compliance controls. Each mapping has been reviewed by Lisa (Compliance Officer) and is validated by the corresponding verification method.

### 11.1 SOC2 Trust Service Criteria Mapping

| SOC2 Control | Control Description | Mapped NFRs | Verification |
|---|---|---|---|
| **CC6.1** | Logical and Physical Access Controls | Q-014, Q-015, Q-018 | JWT auth enforced on all endpoints (Q-014); RLS on all tenant tables (Q-015); T0 agents sandboxed from privileged tools (Q-018). Verified by integration tests and OWASP ZAP scans. |
| **CC6.6** | System Boundaries and External Connections | Q-016 | TLS 1.2+ enforced on all external connections. Verified by testssl.sh and SSL Labs scans in CI. |
| **CC7.1** | System Monitoring | Q-028, Q-029, Q-030, Q-031, Q-032 | 13-field audit on every invocation (Q-028); cost accuracy within 1% (Q-029); structured logging with correlation_id (Q-030); step duration tracking (Q-031); budget alerts within 60s (Q-032). Verified by continuous monitoring and daily reconciliation. |
| **CC7.2** | Incident Detection and Response | Q-009, Q-011, Q-032 | Circuit breaker activates within 5s (Q-009); graceful degradation on API failure (Q-011); budget breach alerts within 60s (Q-032). Verified by chaos engineering tests and alert sink integration tests. |
| **CC7.3** | Incident Recovery | Q-008, Q-010, Q-012 | Checkpoint recovery within 60s (Q-008); RPO=0 for audit data (Q-010); DB pool recovery within 10s (Q-012). Verified by integration tests and monthly restore drills. |
| **CC8.1** | Change Management and Software Integrity | Q-017, Q-022, Q-023, Q-024, Q-026, Q-027 | Zero critical CVEs (Q-017); coverage gates on all modules (Q-022--Q-024); golden + adversarial tests for all agents (Q-026); integration tests for all pipelines (Q-027). Verified by CI gates that block merge on violation. |
| **CC9.1** | Risk Mitigation | Q-013, Q-035 | PII/secret scanning on all outputs (Q-013); output size limits to prevent resource exhaustion (Q-035). Verified by scanner integration tests and CI gates. |

### 11.2 EU AI Act Mapping

| AI Act Article | Requirement | Mapped NFRs | Verification |
|---|---|---|---|
| **Article 9** | Risk Management System | Q-009, Q-011, Q-013, Q-018, Q-032 | Circuit breaker and graceful degradation manage operational risk (Q-009, Q-011); secret scanning prevents data leakage risk (Q-013); tool sandboxing limits agent capability risk (Q-018); budget alerts manage financial risk (Q-032). |
| **Article 12** | Record-Keeping | Q-028, Q-029, Q-033, Q-036 | 13-field audit record on every invocation (Q-028); cost tracking per invocation (Q-029); immutable audit trail (Q-033); retention policies meeting regulatory minimums (Q-036). |
| **Article 13** | Transparency | Q-028, Q-030 | Full audit trail with input/output hashes enables traceability (Q-028); structured logging with correlation_id enables end-to-end request tracing (Q-030). |
| **Article 14** | Human Oversight | Q-018, Q-026 | Tiered agent permissions with human-in-the-loop for sensitive operations (Q-018); golden tests establish known-good baselines and adversarial tests verify rejection of bad inputs (Q-026). Approval queue in dashboard provides runtime human override. |
| **Article 15** | Accuracy, Robustness, Cybersecurity | Q-001, Q-007, Q-010, Q-016, Q-017 | Latency SLAs ensure timely responses (Q-001); uptime SLA ensures availability (Q-007); RPO=0 ensures data durability (Q-010); TLS enforcement ensures transit security (Q-016); CVE scanning ensures supply chain security (Q-017). |
| **Article 52** | Transparency for AI-Generated Content | Q-028 | Every output is traceable to its agent, model, confidence score, and pipeline context via the 13-field audit record. Users can query the audit trail to determine which outputs were AI-generated and with what confidence. |

---

## 12. Enforcement Rules

1. **CI Gate Policy:** PRs SHALL NOT be merged if any P0 or P1 NFR verification fails. P2 NFRs generate warnings but do not block merge.
2. **Exception Process:** A temporary exception to any NFR requires a `knowledge_exceptions` record with: NFR ID, justification, expiry date (max 30 days), and approval from both the NFR owner and Lisa (Compliance Officer).
3. **Regression Policy:** If a previously passing NFR begins failing, the responsible team has 24 hours (P0) or 72 hours (P1) to restore compliance or file an exception.
4. **Audit Cadence:** Lisa SHALL review all active exceptions and compliance matrix mappings quarterly. Results are recorded in the audit_events table.
5. **Dashboard Visibility:** All NFR metrics SHALL be visible on the Streamlit dashboard under a dedicated "Quality Gate" page showing: current status (pass/fail/exception), trend sparkline (30 days), and last verification timestamp.

---

## 13. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-03-23 | Sarah (Engineering Lead) | Initial release with 36 NFRs across 8 categories |

---

*This document is machine-verifiable. Every NFR includes a `Verify:` clause that maps to a concrete test, CI gate, or monitoring check. No NFR is aspirational --- all are enforced by automation.*
