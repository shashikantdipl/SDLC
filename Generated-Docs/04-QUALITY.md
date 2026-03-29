# QUALITY — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 4 of 14 | Status: Draft

---

## 1. Purpose

This document defines every non-functional requirement (NFR) for the Agentic SDLC Platform with specific, measurable thresholds and automated verification methods. Following the Full-Stack-First approach, NFRs cover all three interface layers (MCP, REST, Dashboard) as equal citizens, plus interface parity requirements ensuring behavioral consistency across layers. All NFRs are binding for code merged to `main` and enforced through CI gates, runtime monitors, and periodic audits.

---

## 2. Conventions

- **NFR Identifier:** `Q-NNN` where NNN is a zero-padded three-digit sequence number.
- **Format:** `Q-NNN: [Category] — [Imperative rule with specific threshold]. Verify: [automated verification method].`
- **Priority tiers:** P0 (launch blocker), P1 (required within 30 days of GA), P2 (required within 90 days of GA).
- **Measurement cadence:** Continuous (C) = every invocation or request; Periodic (P) = scheduled job; Gate (G) = CI/CD pipeline check.
- **PRD traceability:** Each NFR maps to one or more PRD success metrics (M1–M10).

---

## 3. Summary Matrix

| Category | NFR Range | Count | P0 | P1 | P2 |
|---|---|---|---|---|---|
| Performance | Q-001 – Q-010 | 10 | 6 | 3 | 1 |
| Reliability | Q-011 – Q-018 | 8 | 5 | 3 | 0 |
| Security | Q-019 – Q-028 | 10 | 8 | 2 | 0 |
| Accessibility | Q-029 – Q-033 | 5 | 0 | 3 | 2 |
| Coverage | Q-034 – Q-041 | 8 | 3 | 4 | 1 |
| Observability | Q-042 – Q-048 | 7 | 4 | 3 | 0 |
| Interface Parity | Q-049 – Q-053 | 5 | 4 | 1 | 0 |
| Data | Q-054 – Q-059 | 6 | 4 | 2 | 0 |
| Cost | Q-060 – Q-064 | 5 | 4 | 1 | 0 |
| Provider Portability | Q-065 – Q-066 | 2 | 1 | 1 | 0 |
| **Total** | | **66** | **39** | **23** | **4** |

---

## 4. Performance (Q-001 – Q-010)

**PRD traceability:** M1, M2, M3, M5

```
Q-001: Performance — MCP tool read response time SHALL NOT exceed 500ms at p95,
measured from MCP request receipt to response dispatch, excluding Claude client
network transit. Verify: Prometheus histogram `mcp_tool_duration_seconds{operation=
"read"}` with p95 assertion; CI runs 200-request load test against each MCP read
tool and asserts p95 < 500ms via pytest-benchmark; Grafana alert fires if rolling
5-minute p95 exceeds 500ms. [P0] [C] [M1]
```

```
Q-002: Performance — MCP tool write/trigger response time SHALL NOT exceed 2s at
p95, measured from MCP request receipt to response dispatch. Verify: Prometheus
histogram `mcp_tool_duration_seconds{operation="write"}` with p95 assertion; CI
runs 100-request load test against each MCP write tool and asserts p95 < 2s;
Grafana alert fires if rolling 5-minute p95 exceeds 2s. [P0] [C] [M1]
```

```
Q-003: Performance — Each MCP server (agents:3100, governance:3101, knowledge:3102)
SHALL reach ready state within 5 seconds of process start, defined as accepting
the first MCP initialize handshake. Verify: Integration test `test_mcp_server_
startup` times process spawn to first successful initialize call; CI asserts < 5s
for all 3 servers; startup time logged to `mcp_server_startup_seconds` metric.
[P0] [G]
```

```
Q-004: Performance — REST API response time SHALL NOT exceed 500ms at p95 for all
GET endpoints and 1s at p95 for all POST/PUT/PATCH endpoints, measured from aiohttp
request receipt to response dispatch. Verify: Prometheus histogram `http_request_
duration_seconds` bucketed by method and route; CI runs k6 load test with 50
concurrent users for 60s and asserts p95 thresholds; Grafana alert on threshold
breach. [P0] [C] [M1]
```

```
Q-005: Performance — Dashboard page load time SHALL NOT exceed 2s at p95 for any
page, measured from browser navigation start to Streamlit `onLoad` complete.
Verify: Synthetic monitoring job (Playwright) hits each dashboard route every 60s
and records `page_load_ms`; CI runs Lighthouse against each page and asserts
Performance score >= 70; alert fires if rolling p95 exceeds 2s. [P0] [C] [M3]
```

```
Q-006: Performance — Dashboard Fleet Health Overview page SHALL load in under 1s at
p95, including all agent status tiles and summary metrics. Verify: Dedicated
synthetic monitor targeting `/fleet-health` route; Streamlit server-side render
time logged to `dashboard_render_seconds{page="fleet_health"}`; CI Playwright test
asserts full render < 1s. [P0] [C] [M3]
```

```
Q-007: Performance — Pipeline trigger-to-first-output time SHALL NOT exceed 30s,
measured from `trigger_pipeline` call (MCP or REST) to the first agent writing
output to session store. Verify: Pipeline run metadata records `first_output_at -
triggered_at`; integration test `test_pipeline_trigger_latency` asserts < 30s;
Grafana panel tracks rolling p95. [P0] [C] [M2]
```

```
Q-008: Performance — Shared service method call latency SHALL NOT exceed 200ms at
p95 for any service method, measured from method entry to return, excluding
external I/O (Claude API, PostgreSQL). Verify: Decorator-based timing on all
service methods logging to `service_method_duration_seconds{service, method}`;
CI unit test suite asserts p95 < 200ms from 1000 iterations per method using
mock I/O. [P1] [C]
```

```
Q-009: Performance — PostgreSQL query execution time SHALL NOT exceed 100ms at p95
for indexed queries and 500ms at p95 for analytical/aggregate queries. Verify:
`pg_stat_statements` monitored via Prometheus postgres_exporter; CI migration test
runs EXPLAIN ANALYZE on all ORM queries and asserts execution plans use indexes;
slow query log threshold set to 500ms. [P1] [P]
```

```
Q-010: Performance — Cross-interface round-trip (MCP trigger → pipeline execution
→ dashboard approval → MCP status confirmation) SHALL complete in under 10 minutes
excluding human think time. Verify: End-to-end integration test `test_cross_
interface_roundtrip` with auto-approving gate stub; pipeline run log analysis
computing delta between MCP `trigger_pipeline` timestamp and MCP `check_pipeline_
status` returning `completed`; human wait time tracked separately via
`gate_pending_duration`. [P2] [P] [M5]
```

---

## 5. Reliability (Q-011 – Q-018)

**PRD traceability:** M6, M8

```
Q-011: Reliability — MCP server crash recovery SHALL complete within 30s, defined
as time from process exit to accepting new MCP connections. The process supervisor
(systemd/Docker restart policy) SHALL automatically restart crashed MCP servers.
Verify: Chaos test `test_mcp_crash_recovery` kills each MCP server process and
asserts reconnection within 30s; supervisor configured with `restart: always` and
`restart_delay: 5s`; Prometheus `mcp_server_restarts_total` counter tracked.
[P0] [C]
```

```
Q-012: Reliability — MCP connection resilience SHALL survive transient network
disruptions up to 30s without data loss. Clients SHALL automatically reconnect
and resume after network blip. Verify: Integration test `test_mcp_network_
resilience` uses `tc netem` (or equivalent) to inject 30s network partition then
verifies client reconnects and pending operations complete; MCP SDK retry config:
3 retries with exponential backoff (1s, 2s, 4s). [P0] [C]
```

```
Q-013: Reliability — REST API uptime SHALL be >= 99.5% measured over any rolling
30-day window, excluding planned maintenance windows announced 48h in advance.
Verify: Synthetic health check (`GET /health`) every 30s from external monitor;
uptime computed as `(total_checks - failed_checks) / total_checks * 100`;
PagerDuty alert if 5-minute availability drops below 99%. [P0] [C]
```

```
Q-014: Reliability — Dashboard availability SHALL be >= 99.0% measured over any
rolling 30-day window. Verify: Synthetic monitor hitting Streamlit health endpoint
every 60s; availability computed from successful responses; alert on 5-minute
downtime. [P1] [C]
```

```
Q-015: Reliability — Pipeline completion rate SHALL exceed 95% of triggered runs
producing all 12 documents without manual intervention, measured over rolling 30-day
window. Verify: SQL query `SELECT COUNT(*) FILTER (WHERE status = 'completed' AND
document_count = 12) * 100.0 / COUNT(*) FROM pipeline_runs WHERE triggered_at >
now() - interval '30 days'`; weekly report; alert if rate drops below 95%. [P0] [P]
[M8]
```

```
Q-016: Reliability — Shared service layer error rate SHALL NOT exceed 1% of total
invocations per service per rolling 1-hour window. Verify: Prometheus counter
`service_errors_total{service}` divided by `service_calls_total{service}`;
Grafana alert fires if any service exceeds 1% error rate in 1h; CI asserts zero
errors in happy-path integration tests. [P0] [C]
```

```
Q-017: Reliability — All 48 agents SHALL pass health checks and respond to
invocations. Agent manifest validation SHALL confirm all 48 manifests load and
validate against `agent-manifest.schema.json`. Verify: `pytest tests/test_agent_
registry.py` confirms all 48 manifests load and validate; nightly CI job runs
health check against each agent; Prometheus gauge `agents_healthy_total` tracked.
[P1] [P] [M6]
```

```
Q-018: Reliability — Pipeline checkpoint/resume SHALL survive process restart.
If the orchestrator crashes mid-pipeline, restart SHALL resume from the last
completed phase, not from the beginning. Verify: Integration test `test_pipeline_
checkpoint_resume` triggers a pipeline, kills the orchestrator after phase 3
completes, restarts, and asserts phases 1-3 are not re-executed; checkpoint state
stored in `pipeline_runs.checkpoint_state` JSONB column. [P1] [C]
```

---

## 6. Security (Q-019 – Q-028)

**PRD traceability:** M10

```
Q-019: Security — Every MCP tool call SHALL require a valid API key in the MCP
authentication handshake. Unauthenticated requests SHALL receive an MCP error
response with code -32001 (Unauthorized). Verify: Integration test `test_mcp_auth_
required` sends requests without API key and asserts error code -32001; penetration
test confirms no MCP tool is accessible without authentication; audit log records
all authentication failures. [P0] [C]
```

```
Q-020: Security — MCP tool input parameters SHALL be validated against JSON Schema
definitions before execution. No tool handler SHALL directly interpolate user-
supplied parameters into SQL queries, shell commands, or file paths. Verify: Static
analysis (semgrep rule `mcp-sql-injection`) scans all tool handlers for raw string
interpolation into queries; CI gate blocks merge on violation; fuzz test sends
1000 malformed inputs per tool and asserts no unhandled exceptions. [P0] [G]
```

```
Q-021: Security — MCP resource access SHALL enforce project_id scoping. An MCP
client authenticated for project P1 SHALL NOT access data belonging to project P2.
Verify: Integration test `test_mcp_project_isolation` authenticates as project P1,
attempts to read project P2 data via every MCP tool, and asserts permission denied
for all; PostgreSQL RLS policy `project_isolation_policy` enforced at database
level. [P0] [C]
```

```
Q-022: Security — REST API authentication SHALL require either a valid JWT token
(for dashboard sessions) or a valid API key (for programmatic access) on every
endpoint except `GET /health` and `POST /auth/login`. Verify: Integration test
`test_rest_auth_enforcement` iterates every registered route and asserts 401 for
unauthenticated requests; CI gate runs this test on every PR. [P0] [G]
```

```
Q-023: Security — REST API input validation SHALL reject payloads exceeding 1MB,
malformed JSON, and fields failing schema validation with HTTP 400 and structured
error response. Verify: Fuzz test `test_rest_input_validation` sends oversized
payloads, malformed JSON, SQL injection attempts, and XSS payloads to every POST
endpoint and asserts HTTP 400; aiohttp request size limit configured to 1MB.
[P0] [G]
```

```
Q-024: Security — Dashboard sessions SHALL use secure, HttpOnly, SameSite=Strict
cookies with 24-hour expiration. Session tokens SHALL be invalidated on logout.
Verify: Integration test `test_dashboard_session_security` inspects Set-Cookie
headers for HttpOnly, Secure, and SameSite flags; verifies session token rejected
after logout; OWASP ZAP scan confirms no session fixation vulnerabilities. [P0] [G]
```

```
Q-025: Security — Dashboard SHALL implement CSRF protection on all state-mutating
operations and XSS protection via Content-Security-Policy headers. Verify: OWASP
ZAP automated scan against all dashboard routes; CSP header validation test asserts
`script-src 'self'`; Streamlit configured with `server.enableXsrfProtection=true`.
[P0] [G]
```

```
Q-026: Security — PII detection SHALL scan all agent outputs before persistence.
Detected PII SHALL be flagged in the audit record and optionally redacted based on
project policy. Verify: Unit test `test_pii_detection` runs scanner against 200
synthetic outputs containing SSN, email, phone, credit card patterns and asserts
>= 99% detection rate; integration test confirms `audit_events.pii_detected`
flag set correctly. [P0] [C]
```

```
Q-027: Security — No secrets (API keys, tokens, passwords, connection strings)
SHALL appear in application logs, agent outputs, audit records, or error responses.
Verify: Log scrubber middleware strips patterns matching secret formats before
write; CI test `test_no_secrets_in_logs` runs full integration suite, captures all
log output, and scans for secret patterns (regex for API keys, JWTs, connection
strings); semgrep rule `no-secrets-in-logs` blocks merges containing hardcoded
secrets. [P0] [G]
```

```
Q-028: Security — All inter-service communication SHALL use TLS 1.2+ in production.
Database connections SHALL use SSL mode `verify-full`. Verify: Integration test
`test_tls_enforcement` asserts all outbound connections use TLS; PostgreSQL
connection string includes `sslmode=verify-full`; nmap scan confirms no plaintext
ports exposed. [P1] [G]
```

---

## 7. Accessibility (Q-029 – Q-033)

```
Q-029: Accessibility — Dashboard SHALL comply with WCAG 2.1 Level AA for all
pages, including sufficient color contrast (4.5:1 for normal text, 3:1 for large
text), focus indicators, and alt text for non-decorative images. Verify: axe-core
automated scan integrated into CI via Playwright; scan runs against every dashboard
page; CI gate blocks merge if any Level AA violations detected. [P1] [G]
```

```
Q-030: Accessibility — All dashboard interactive elements SHALL be operable via
keyboard alone, with visible focus indicators and logical tab order. No keyboard
trap SHALL exist on any page. Verify: Playwright test `test_keyboard_navigation`
tabs through every page and asserts all interactive elements receive focus in
logical order; manual audit quarterly. [P1] [G]
```

```
Q-031: Accessibility — Dashboard SHALL provide ARIA labels for all dynamic content
regions (agent status tiles, pipeline progress bars, approval queue items) and
support screen reader navigation. Verify: axe-core ARIA validation; manual screen
reader test (NVDA/VoiceOver) covering Fleet Health, Pipeline Status, and Approval
Queue pages quarterly. [P1] [P]
```

```
Q-032: Accessibility — Dashboard color contrast ratios SHALL meet WCAG 2.1 AA
minimums: 4.5:1 for normal text (<18pt), 3:1 for large text (>=18pt), 3:1 for
UI components and graphical objects. Verify: Automated contrast checker in CI
(axe-core); Lighthouse accessibility audit score >= 90; design token validation
test asserts all color pairs meet ratio requirements. [P2] [G]
```

```
Q-033: Accessibility — Dashboard error messages and status notifications SHALL be
announced to assistive technologies via ARIA live regions with appropriate
politeness levels (assertive for errors, polite for status updates). Verify:
Playwright test validates `aria-live` attributes on notification elements; manual
screen reader verification quarterly. [P2] [G]
```

---

## 8. Coverage (Q-034 – Q-041)

**PRD traceability:** M6

```
Q-034: Coverage — Shared service layer unit test coverage SHALL be >= 90% line
coverage and >= 85% branch coverage. The shared service layer is the foundation
for all three interfaces; it has the HIGHEST coverage requirement. Verify:
`pytest --cov=src/services --cov-branch` with `--cov-fail-under=90` for line and
custom branch threshold check; coverage report uploaded to CI artifacts; merge
blocked if coverage drops below 90%. [P0] [G]
```

```
Q-035: Coverage — MCP tool handler test coverage SHALL be >= 85% line coverage
for all tool handler modules across all 3 MCP servers. Verify: `pytest --cov=
src/mcp/tools --cov-fail-under=85`; coverage measured per MCP server (agents,
governance, knowledge); CI gate blocks merge on violation. [P0] [G]
```

```
Q-036: Coverage — REST API route handler test coverage SHALL be >= 85% line
coverage for all route modules. Verify: `pytest --cov=src/api/routes --cov-fail-
under=85`; coverage measured across all route modules; CI gate blocks merge on
violation. [P0] [G]
```

```
Q-037: Coverage — Dashboard component test coverage SHALL be >= 75% line coverage
for all Streamlit page modules and widget components. Verify: `pytest --cov=src/
dashboard --cov-fail-under=75`; Streamlit AppTest framework for component testing;
CI gate blocks merge on violation. [P1] [G]
```

```
Q-038: Coverage — Integration/parity test suite SHALL include >= 1 end-to-end test
per cross-interface user journey defined in the INTERACTION-MAP document. Each test
SHALL exercise the same operation via MCP and REST and assert identical outcomes.
Verify: Test manifest file `tests/parity/manifest.json` lists all cross-interface
journeys; CI asserts every journey has a corresponding test file; test count
validated in `test_parity_coverage` meta-test. [P1] [G]
```

```
Q-039: Coverage — Agent test coverage SHALL include >= 3 golden-path test cases
and >= 1 adversarial test case per agent. Golden-path tests validate expected
outputs from known inputs; adversarial tests validate graceful handling of
malformed, oversized, or malicious inputs. Verify: Test manifest `tests/agents/
manifest.json` lists required test counts per agent; meta-test `test_agent_
coverage_manifest` asserts >= 3 golden and >= 1 adversarial per agent_id;
CI gate blocks merge on violation. [P1] [G]
```

```
Q-040: Coverage — Mutation testing score SHALL be >= 70% for shared service layer,
measured by mutmut or equivalent. This ensures tests catch real bugs, not just
exercise code paths. Verify: `mutmut run --paths-to-mutate=src/services/ --runner=
pytest` in nightly CI; results published to coverage dashboard; alert if score
drops below 70%. [P2] [P]
```

```
Q-041: Coverage — Every database migration SHALL have a corresponding rollback
migration and both SHALL be tested in CI. Verify: `pytest tests/test_migrations.py`
runs every migration forward and backward on a fresh database; CI gate blocks merge
if any migration lacks a rollback or if rollback fails. [P1] [G]
```

---

## 9. Observability (Q-042 – Q-048)

**PRD traceability:** M7, M10

```
Q-042: Observability — Every MCP tool call SHALL produce an audit log entry within
5 seconds of completion containing: trace_id, tool_name, project_id, user_id,
input_hash, output_hash, duration_ms, cost_usd, timestamp, status, error_code
(if any). Verify: Integration test `test_mcp_audit_logging` invokes every MCP tool
and asserts corresponding audit record exists in `audit_events` within 5s with all
13 required fields populated; nightly reconciliation compares `mcp_invocations`
count against `audit_events` count. [P0] [C] [M10]
```

```
Q-043: Observability — Every REST API request SHALL produce a structured log entry
containing: trace_id, method, path, status_code, duration_ms, user_id, request_id,
timestamp. Verify: aiohttp middleware `AccessLogMiddleware` emits JSON log per
request; integration test `test_rest_request_logging` issues requests to every
endpoint and asserts corresponding log entries; log format validated by JSON schema.
[P0] [C]
```

```
Q-044: Observability — Dashboard user actions (page navigation, filter changes,
approval decisions, report exports) SHALL be logged with: trace_id, user_id,
action_type, page, timestamp, metadata. Verify: Streamlit callback wrapper emits
action events; integration test `test_dashboard_action_logging` navigates through
all pages and asserts action log entries; log completeness checked weekly. [P1] [C]
```

```
Q-045: Observability — Cross-interface trace correlation SHALL use a single trace_id
propagated from MCP request → shared service → database audit record → REST
notification → dashboard display. Verify: End-to-end test `test_trace_correlation`
triggers a pipeline via MCP, retrieves the trace_id, queries audit_events by
trace_id, checks REST notification payload for same trace_id, and verifies
dashboard displays the trace_id on the pipeline detail page. [P0] [C]
```

```
Q-046: Observability — Cost events SHALL be recorded within 5 seconds of Claude API
response receipt, containing: agent_id, model, input_tokens, output_tokens,
cost_usd, pipeline_run_id, trace_id. Verify: Integration test `test_cost_event_
recording` triggers an agent invocation and asserts cost event exists in
`cost_events` table within 5s with accurate token counts; weekly reconciliation
against Anthropic billing API. [P0] [C] [M7]
```

```
Q-047: Observability — Structured logs SHALL be emitted in JSON format with
consistent field names across all three interfaces. Log level SHALL be configurable
per component without restart (via environment variable or config reload). Verify:
JSON schema validation test parses sample logs from each component and asserts
consistent field naming; integration test verifies log level change takes effect
within 10s. [P1] [C]
```

```
Q-048: Observability — Health check endpoints SHALL exist for all services: MCP
servers (`initialize` handshake), REST API (`GET /health`), Dashboard (`GET /
_stcore/health`), PostgreSQL (connection pool check). Each SHALL return structured
status including dependency health. Verify: Synthetic monitor hits all health
endpoints every 30s; integration test `test_health_endpoints` asserts 200 response
with expected schema from each endpoint. [P0] [C]
```

---

## 10. Interface Parity (Q-049 – Q-053)

**PRD traceability:** M5

```
Q-049: Interface Parity — Every MCP tool SHALL have a corresponding REST API
endpoint that performs the same operation on the same shared service method. The
mapping SHALL be documented in an interface parity matrix and validated by CI.
Verify: Parity matrix file `docs/interface-parity-matrix.json` lists every MCP
tool and its REST equivalent; meta-test `test_parity_matrix_completeness` asserts
every registered MCP tool has a REST mapping; CI gate blocks merge if a new MCP
tool lacks a REST equivalent. [P0] [G]
```

```
Q-050: Interface Parity — MCP and REST SHALL return consistent error codes for the
same operation failure. A shared error code enum SHALL be used by both interfaces,
mapped to MCP error codes and HTTP status codes respectively. Verify: Error code
mapping file `src/shared/error_codes.py` defines all error codes with MCP and HTTP
mappings; integration test `test_parity_error_codes` triggers the same error
condition via MCP and REST and asserts the mapped error codes match the enum;
CI gate blocks divergent error handling. [P0] [G]
```

```
Q-051: Interface Parity — The same shared service call invoked from MCP and REST
SHALL return identical data shapes (same JSON keys, same value types, same nesting
structure). Verify: Parity test suite `tests/parity/test_data_shape_parity.py`
calls every shared service method via both MCP tool handler and REST route handler,
serializes both responses to JSON, and asserts structural equality (keys and types
match, values may differ only by serialization format); CI gate blocks merge on
shape divergence. [P0] [G]
```

```
Q-052: Interface Parity — Dashboard data displays SHALL reflect the same data
available via MCP and REST queries with no more than 5 seconds of staleness.
Verify: Integration test `test_dashboard_data_freshness` writes data via shared
service, then reads via dashboard component and asserts visibility within 5s;
Streamlit cache TTL configured <= 5s for real-time pages (Fleet Health, Pipeline
Status). [P0] [C]
```

```
Q-053: Interface Parity — API versioning changes SHALL be applied simultaneously
to MCP tool schemas and REST endpoint schemas. No interface SHALL expose a newer
or older schema version than another. Verify: Schema version validation test
`test_schema_version_parity` extracts version from MCP tool JSON schemas and REST
OpenAPI spec and asserts equality; CI gate blocks merge if versions diverge. [P1]
[G]
```

---

## 11. Data (Q-054 – Q-059)

**PRD traceability:** M10

```
Q-054: Data — Audit event records SHALL be immutable. No UPDATE or DELETE operation
SHALL be permitted on the `audit_events` table. Verify: PostgreSQL trigger
`prevent_audit_mutation` raises exception on UPDATE/DELETE; RLS policy denies
UPDATE/DELETE to all roles; integration test `test_audit_immutability` attempts
UPDATE and DELETE on `audit_events` and asserts both fail with permission error;
database migration test verifies trigger exists. [P0] [C]
```

```
Q-055: Data — Data retention policies SHALL be enforced automatically: audit_events
retained for 365 days, cost_events retained for 90 days, session data retained for
24 hours. Expired data SHALL be archived to cold storage before deletion. Verify:
PostgreSQL partition-based retention with `pg_partman`; nightly job `retention_
enforcement` drops expired partitions after archival; integration test `test_data_
retention` creates records with backdated timestamps and asserts they are removed
after retention job runs. [P0] [P]
```

```
Q-056: Data — PostgreSQL database SHALL be backed up daily with point-in-time
recovery capability. Backup verification SHALL restore to a test instance and
validate row counts weekly. Verify: `pg_dump` or WAL archiving configured with
daily schedule; weekly restore test `test_backup_restore` restores latest backup
to ephemeral instance and asserts table existence and row count within 1% of
source; backup completion logged and alerted on failure. [P0] [P]
```

```
Q-057: Data — PII fields (user email, name, API keys) SHALL be encrypted at rest
using AES-256 via PostgreSQL pgcrypto extension or application-level encryption.
Verify: Database schema test `test_pii_encryption` asserts PII columns use
`pgp_sym_encrypt`; integration test writes and reads PII, verifying raw column
value is ciphertext; annual penetration test validates encryption at rest. [P0] [G]
```

```
Q-058: Data — Database schema changes SHALL be applied exclusively through versioned
migrations (Alembic or equivalent). No manual DDL SHALL be executed in production.
Verify: CI gate runs `alembic check` and blocks merge if model state diverges from
migration history; production deploy pipeline applies migrations automatically;
audit log records all DDL execution. [P1] [G]
```

```
Q-059: Data — Database connection pool SHALL be sized between 10 (min) and 50 (max)
connections per service instance, with connection timeout of 5s and idle timeout of
300s. Verify: Connection pool metrics exported to Prometheus (`db_pool_active`,
`db_pool_idle`, `db_pool_waiting`); alert fires if pool utilization exceeds 80%
for 5 minutes; integration test validates pool configuration parameters. [P1] [C]
```

---

## 12. Cost (Q-060 – Q-064)

**PRD traceability:** M7, M9

```
Q-060: Cost — Pipeline cost per full 12-document generation run SHALL NOT exceed
$25.00. The cost tracker SHALL enforce a hard-stop at $25.00, halting the pipeline
and notifying the user. Verify: Real-time cost accumulator in G1-cost-tracker
sums `cost_events` per `pipeline_run_id`; integration test `test_pipeline_cost_
ceiling` runs a full pipeline and asserts total cost < $25; hard-stop test
simulates cost reaching $25 and asserts pipeline halts. [P0] [C] [M9]
```

```
Q-061: Cost — Individual agent invocation cost SHALL NOT exceed $0.50. Agent
invocations approaching $0.50 SHALL receive a warning at $0.40 and a hard-stop at
$0.50. Verify: Agent cost guard in shared service layer checks accumulated cost
per invocation; integration test `test_agent_cost_ceiling` uses a long-running
prompt and asserts hard-stop triggers at $0.50; cost event records individual
invocation costs. [P0] [C]
```

```
Q-062: Cost — Cost tracking accuracy SHALL be within 2% of actual LLM provider API
billing at fleet, project, and agent aggregation levels. Cost calculation is
provider-aware (Anthropic pricing, OpenAI pricing, Ollama = $0.00). Verify: Weekly
reconciliation job `cost_reconciliation` compares `cost_events` totals against
provider billing APIs; automated alert if delta exceeds 2% at any aggregation
level; monthly report published to compliance dashboard. [P0] [P] [M7]
```

```
Q-063: Cost — Budget enforcement SHALL follow a fail-safe pattern: if the cost
tracking database is unavailable, agent invocations SHALL be blocked (fail-closed),
NOT allowed to proceed without tracking (fail-open). Verify: Integration test
`test_cost_failsafe` disconnects the database during an agent invocation and
asserts the invocation is rejected with a cost-tracking-unavailable error; circuit
breaker pattern implemented in cost service. [P0] [C]
```

```
Q-064: Cost — Budget tiers SHALL be enforced at three levels: Fleet ($50/day),
Project ($20/day), Agent ($5/day). Exceeding any tier SHALL block further
invocations at that level and notify the project owner. Verify: Integration test
`test_budget_tier_enforcement` simulates spend exceeding each tier and asserts
invocation blocked; cost dashboard displays current spend vs. budget for each tier;
Prometheus gauges `budget_remaining{tier}` tracked. [P1] [C]
```

---

## 12a. Provider Portability (Q-065 – Q-066)

**PRD traceability:** C1, R-13

```
Q-065: Provider Portability — System SHALL produce equivalent outputs when switching
between LLM providers at the same tier. Verify: Run G1-cost-tracker on Anthropic
(`LLM_PROVIDER=anthropic`) and OpenAI (`LLM_PROVIDER=openai`), compare JSON schema
compliance of both outputs; integration test `test_provider_portability` asserts both
providers return valid CostReport schema; output structure test validates all required
fields present regardless of provider. [P1] [P]
```

```
Q-066: Provider Failover — If primary LLM provider fails (API error, timeout, rate
limit), system SHALL failback to secondary provider within 30 seconds. Verify: Chaos
test `test_provider_failover` kills the primary provider connection mid-invocation
and asserts the agent completes using the fallback provider; failover event is logged
to audit trail with original and fallback provider names; total latency including
failover does not exceed 30s. [P1] [C]
```

---

## 12b. Per-Module Coverage Thresholds

| Module Category | Examples | Line Coverage | Branch Coverage | Rationale |
|---|---|---|---|---|
| AI Safety (guardrails, PII) | sdk/llm/, base_hooks.py pii_scan | >= 95% | >= 90% | Safety-critical — failures cause data leaks |
| Core Business Logic | services/pipeline_service.py, cost_service.py | >= 90% | >= 85% | Revenue-critical — failures break pipelines |
| Shared Services | services/audit_service.py, health_service.py | >= 85% | >= 80% | Reliability-critical |
| MCP Handlers | mcp/agents_server.py, governance_server.py | >= 80% | >= 75% | Interface layer |
| REST Handlers | api/routes/*.py | >= 80% | >= 75% | Interface layer |
| Dashboard | dashboard/pages/*.py | >= 70% | >= 65% | UI — visual testing supplements |
| Utilities | sdk/llm/factory.py, schemas/ | >= 60% | >= 55% | Low-risk helpers |

---

## 12c. SLI/SLO Summary

| Service | SLI | SLO Target | Error Budget (monthly) | Measurement |
|---|---|---|---|---|
| MCP Servers | Request latency p99 | < 500ms | 0.1% requests can exceed | OpenTelemetry histogram |
| REST API | Request latency p99 | < 200ms | 0.1% | OpenTelemetry histogram |
| Dashboard | Page load time | < 3s | 1% pages can exceed | Lighthouse CI |
| Pipeline | End-to-end completion | < 30min for 24-step pipeline | 1 failure per 20 runs | Pipeline completion events |
| Agent Invocation | LLM response time | < 30s (fast tier) | 2% calls can exceed | Provider latency metric |
| Cost Tracking | Budget accuracy | +/-5% of actual spend | N/A | Monthly reconciliation |
| Audit Trail | Event capture latency | < 5s from action | 0.01% events delayed | Timestamp comparison |

---

## 13. Compliance Matrix

| NFR | SOC2 Trust Service Criteria | EU AI Act | Notes |
|---|---|---|---|
| Q-019 (MCP auth) | CC6.1 — Logical access security | Art. 9 — Access control | API key required for all MCP tool calls |
| Q-020 (MCP input validation) | CC6.1 — Input validation | Art. 15 — Accuracy/robustness | Prevents injection attacks via MCP params |
| Q-021 (Project isolation) | CC6.3 — Restrict access | Art. 9 — Access control | RLS enforces project_id scoping |
| Q-022 (REST auth) | CC6.1 — Logical access security | Art. 9 — Access control | JWT + API key on all endpoints |
| Q-023 (REST input validation) | CC6.1 — Input validation | Art. 15 — Accuracy/robustness | Schema validation, size limits |
| Q-024 (Session security) | CC6.1 — Session management | — | Secure cookies, 24h expiry |
| Q-025 (CSRF/XSS) | CC6.1 — Web security | — | CSP headers, XSRF protection |
| Q-026 (PII detection) | CC6.5 — Data classification | Art. 10 — Data governance | Scan all agent outputs for PII |
| Q-027 (No secrets in logs) | CC6.1 — Credential protection | — | Log scrubber, semgrep rules |
| Q-028 (TLS enforcement) | CC6.7 — Encryption in transit | — | TLS 1.2+ for all connections |
| Q-042 (MCP audit logging) | CC7.2 — Monitoring | Art. 12 — Record-keeping | Every MCP call produces audit record |
| Q-043 (REST audit logging) | CC7.2 — Monitoring | Art. 12 — Record-keeping | Every REST request logged |
| Q-045 (Trace correlation) | CC7.2 — Cross-system monitoring | Art. 12 — Traceability | Single trace_id across interfaces |
| Q-054 (Audit immutability) | CC7.3 — Tamper-evident logs | Art. 12 — Record-keeping | No UPDATE/DELETE on audit_events |
| Q-055 (Data retention) | CC6.5 — Data lifecycle | Art. 10 — Data governance | 365d audit, 90d cost, 24h session |
| Q-056 (Database backup) | CC7.5 — Recovery | — | Daily backup, weekly restore test |
| Q-057 (PII encryption) | CC6.7 — Encryption at rest | Art. 10 — Data governance | AES-256 for PII fields |
| Q-060 (Cost ceiling) | CC8.1 — Change management | Art. 9 — Risk management | Hard-stop at $25/pipeline run |
| Q-062 (Cost accuracy) | CC8.1 — Monitoring accuracy | Art. 13 — Transparency | Within 2% of Anthropic billing |
| Q-063 (Cost fail-safe) | CC8.1 — System integrity | Art. 15 — Robustness | Fail-closed on DB unavailability |
| Q-015 (Pipeline completion) | CC8.1 — Processing integrity | Art. 15 — Reliability | >95% completion rate |
| Q-029 (WCAG 2.1 AA) | — | Art. 5 — Non-discrimination | Dashboard accessibility compliance |
| Q-049 (Interface parity) | — | Art. 13 — Transparency | Consistent behavior across interfaces |
| Q-051 (Data shape parity) | CC8.1 — Processing integrity | Art. 13 — Transparency | Identical responses from MCP/REST |

---

## 14. Quality Scoring Rubric

This rubric defines the scoring model used by the QualityScorer agent to evaluate all document outputs in the pipeline. Every generated document is scored against these five dimensions.

```yaml
quality_rubric:
  completeness:
    weight: 0.25
    threshold: 0.85
    description: "All required sections present, all fields populated"
    verify: "Schema validation against document template"
    scoring_guide:
      1.0: "Every required section present, every field populated, no TODOs or placeholders"
      0.85: "All required sections present, <= 2 optional fields missing"
      0.70: "1-2 required sections missing or > 5 fields unpopulated"
      0.50: "3+ required sections missing"
      0.0: "Document structurally incomplete or wrong template"

  accuracy:
    weight: 0.30
    threshold: 0.85
    description: "Facts match source inputs, no hallucinated data"
    verify: "Cross-reference check against input documents"
    scoring_guide:
      1.0: "Every fact traces to source input, zero hallucinated data"
      0.85: "All critical facts accurate, <= 2 minor inaccuracies in non-critical fields"
      0.70: "1-2 factual errors in critical fields or > 5 minor inaccuracies"
      0.50: "3+ factual errors in critical fields"
      0.0: "Pervasive hallucination or contradicts source inputs"

  format_compliance:
    weight: 0.15
    threshold: 0.95
    description: "Follows naming conventions, ID formats, data shapes"
    verify: "Regex/schema validation of IDs, names, shapes"
    scoring_guide:
      1.0: "All IDs match format (Q-NNN, F-NNN, etc.), all naming conventions followed"
      0.95: "1-2 minor format deviations (e.g., inconsistent capitalization)"
      0.85: "3-5 format violations or 1 ID format error"
      0.70: "> 5 format violations or > 2 ID format errors"
      0.0: "No consistent formatting applied"

  cross_interface_parity:
    weight: 0.15
    threshold: 1.00
    description: "MCP and REST return identical data for same operation"
    verify: "Automated parity test suite"
    scoring_guide:
      1.0: "All operations produce identical data shapes and semantically equivalent values across MCP and REST"
      0.90: "1-2 non-critical field differences (e.g., date format variation)"
      0.75: "Structural differences in 1-2 operations"
      0.50: "Structural differences in > 2 operations or missing fields"
      0.0: "MCP and REST return fundamentally different data models"

  traceability:
    weight: 0.15
    threshold: 0.90
    description: "Every item traces to PRD capability or INTERACTION-MAP ID"
    verify: "Linkage check: every F-NNN → C-NNN, every S-NNN → I-NNN"
    scoring_guide:
      1.0: "Every item has a valid trace link, no orphaned items, no broken references"
      0.90: "<= 5% of items missing trace links"
      0.75: "5-15% of items missing trace links"
      0.50: "> 15% of items missing trace links"
      0.0: "No traceability implemented"

scoring:
  pass: ">= 0.85 weighted average"
  conditional_pass: ">= 0.75 (must fix within 1 sprint)"
  fail: "< 0.75 (regenerate document)"

  weighted_formula: |
    score = (completeness * 0.25) + (accuracy * 0.30) + (format_compliance * 0.15)
            + (cross_interface_parity * 0.15) + (traceability * 0.15)

  minimum_dimension_scores:
    completeness: 0.70
    accuracy: 0.70
    format_compliance: 0.80
    cross_interface_parity: 0.75
    traceability: 0.70

  override_rules:
    - "If any dimension scores below its minimum, overall result is 'fail' regardless of weighted average"
    - "If cross_interface_parity < 1.0, result is capped at 'conditional_pass' even if weighted average >= 0.85"
    - "If accuracy < 0.85, result is capped at 'conditional_pass' even if weighted average >= 0.85"
```

---

## 15. NFR Verification Automation Summary

| Verification Method | NFR Count | Execution Context | Frequency |
|---|---|---|---|
| CI gate (pytest) | 38 | GitHub Actions / CI pipeline | Every PR merge |
| Prometheus + Grafana alert | 16 | Production runtime | Continuous |
| Synthetic monitoring (Playwright) | 5 | External monitor | Every 30-60s |
| Load test (k6 / pytest-benchmark) | 6 | CI pipeline | Nightly |
| OWASP ZAP scan | 2 | CI pipeline | Weekly |
| axe-core accessibility scan | 4 | CI pipeline | Every PR merge |
| Database reconciliation job | 4 | Scheduled job | Daily/Weekly |
| Manual audit | 3 | Human review | Quarterly |
| Chaos/fault injection test | 2 | CI pipeline | Weekly |
| Fuzz testing | 2 | CI pipeline | Nightly |
| Static analysis (semgrep) | 2 | CI pipeline | Every PR merge |
| Mutation testing (mutmut) | 1 | CI pipeline | Nightly |

---

## 16. NFR Cross-Reference Index

### By PRD Success Metric

| Metric | NFRs |
|---|---|
| M1 — MCP latency | Q-001, Q-002, Q-004 |
| M2 — Pipeline trigger-to-first-output | Q-007 |
| M3 — Dashboard page load | Q-005, Q-006 |
| M4 — Approval gate response | Q-010 (related) |
| M5 — Cross-interface round-trip | Q-010, Q-049, Q-050, Q-051, Q-052, Q-053 |
| M6 — Agent phase coverage | Q-017, Q-039 |
| M7 — Cost tracking accuracy | Q-046, Q-062 |
| M8 — Pipeline completion rate | Q-015 |
| M9 — Pipeline cost per run | Q-060 |
| M10 — Audit trail completeness | Q-042, Q-043, Q-054, Q-055 |

### By Interface

| Interface | NFRs |
|---|---|
| MCP | Q-001, Q-002, Q-003, Q-011, Q-012, Q-019, Q-020, Q-021, Q-035, Q-042, Q-049, Q-050, Q-051 |
| REST | Q-004, Q-013, Q-022, Q-023, Q-036, Q-043, Q-049, Q-050, Q-051 |
| Dashboard | Q-005, Q-006, Q-014, Q-024, Q-025, Q-029, Q-030, Q-031, Q-032, Q-033, Q-037, Q-044, Q-052 |
| Shared Service | Q-008, Q-016, Q-034, Q-040 |
| All / Cross-cutting | Q-007, Q-009, Q-010, Q-015, Q-017, Q-018, Q-026, Q-027, Q-028, Q-038, Q-039, Q-041, Q-045, Q-046, Q-047, Q-048, Q-054, Q-055, Q-056, Q-057, Q-058, Q-059, Q-060, Q-061, Q-062, Q-063, Q-064 |

---

## 17. Glossary

| Term | Definition |
|---|---|
| p95 | 95th percentile — 95% of measurements fall below this value |
| RLS | Row-Level Security — PostgreSQL feature enforcing data isolation |
| MCP | Model Context Protocol — protocol for AI tool invocation |
| WCAG | Web Content Accessibility Guidelines |
| CSP | Content Security Policy — HTTP header preventing XSS |
| CSRF | Cross-Site Request Forgery |
| PII | Personally Identifiable Information |
| WAL | Write-Ahead Logging — PostgreSQL recovery mechanism |
| SOC2 | Service Organization Control Type 2 — compliance framework |
| EU AI Act | European Union Artificial Intelligence Act (Regulation 2024/1689) |
| Fail-closed | Security pattern where system denies access when control mechanism fails |
| Golden-path test | Test case covering the expected successful workflow |
| Adversarial test | Test case covering malicious, malformed, or edge-case inputs |

---

*End of document. Total NFRs: 64. All Q-NNN IDs referenced by TESTING.md (Doc 13).*
