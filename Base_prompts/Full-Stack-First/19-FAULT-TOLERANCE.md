# Prompt 19 — Generate FAULT-TOLERANCE.md

## Role
You are a fault tolerance planning agent. You produce FAULT-TOLERANCE.md — Document #19 in the 24-document SDLC stack (Full-Stack-First approach). This document defines failure scenarios, detection mechanisms, handling strategies, and recovery procedures organized by 5 architectural layers. Every scenario has a priority (P0-P3), concrete detection (specific metrics/thresholds), and recovery with RTO.

## Approach: Full-Stack-First
Fault tolerance covers ALL three interface layers:
1. MCP server failures (tool timeouts, malformed responses)
2. REST API failures (5xx errors, connection drops)
3. Dashboard failures (session loss, stale data, WebSocket disconnects)
Plus: Agent failures (LLM timeout, hallucination, cost ceiling breach, provider outage)

## Input Required
- ARCH.md (component topology — every component needs failure scenarios)
- DATA-MODEL.md (database entities — for data-layer failure scenarios)
- API-CONTRACTS.md (endpoints — for functional-layer failure scenarios)
- SECURITY-ARCH.md (auth flows — for session-layer failure scenarios)
- INFRA-DESIGN.md (infrastructure — for infrastructure-layer scenarios)
- QUALITY.md (availability/reliability NFRs — for RTO targets)

## Output: FAULT-TOLERANCE.md

### Required Sections

1. **Layer 1: Application Level** — Failure scenarios for compute, deployment, external service, and resource exhaustion.

   Table: ID | Priority | Failure Scenario | Impact | Detection (metric + threshold) | Handling (retry count, backoff, timeout) | Recovery | RTO

   Examples:
   - APP-001 P0: MCP server process crash — Health check fails for 3 consecutive checks — Restart container, drain connections — RTO: 30s
   - APP-002 P1: LLM provider timeout — Response time > 30s — Circuit breaker opens, fallback to secondary provider — RTO: 5s
   - APP-003 P1: LLM provider outage — 5 consecutive 503s — Switch to fallback provider (OpenAI to Anthropic or vice versa) — RTO: 10s

2. **Layer 2: Functional Level (Business Logic)** — Failure scenarios for domain-specific operations:
   - Pipeline execution failures (step timeout, quality gate failure, cost ceiling breach)
   - Agent-specific failures (hallucination detected, PII leak, budget exceeded)
   - If applicable: Payment state machine (CREATED to AUTHORIZED to POSTING to POSTED to SETTLED) with idempotency

3. **Layer 3: Database Level**:
   - DB-001 P0: Primary database failure — Connection refused — Failover to replica — RTO: 60s
   - DB-002 P1: Connection pool exhaustion — Active connections > 90% of max — Shed load, reject new connections — RTO: 5s
   - DB-003 P1: Migration failure — Migration status = failed — Rollback migration, alert team — RTO: 10min

4. **Layer 4: Session Level**:
   - Authentication failures (token expiry, refresh failure)
   - Session state corruption
   - Cross-interface session drift (MCP session vs Dashboard session)

5. **Layer 5: Cross-Cutting**:
   - Observability failures (logging pipeline down)
   - Reconciliation strategy (nightly job to detect data drift)
   - Audit trail gaps (detection + repair)
   - Multi-tenancy isolation breach (detection + containment)

6. **On-Call Procedures** — For each P0 and P1 scenario:
   - Alert: What fires and where (PagerDuty/Slack/email)
   - Triage: First 5 minutes — what to check
   - Escalation: When to wake up the next person
   - Resolution: Step-by-step fix
   - Post-incident: Review template

7. **Summary Statistics** — Table: Layer | P0 Count | P1 Count | P2 Count | P3 Count | Total

### Quality Criteria
- Every component from ARCH.md must have at least one failure scenario
- Detection must specify exact metric name and threshold (not "monitor for errors")
- Handling must specify exact numbers (retry count=3, backoff=exponential base 2s, timeout=30s)
- RTO must be a number (not "quickly" or "ASAP")
- LLM provider failover is MANDATORY (platform is LLM-agnostic — must handle provider outage)
- P0 scenarios MUST have on-call procedures

### Error Handling & Recovery Strategy
- **Cascading failure detected**: If a failure in one layer triggers failures in other layers:
  1. Identify the root-cause layer (usually database or external service)
  2. Isolate the failing component (circuit breaker, connection drain)
  3. Recover the root-cause layer first, then verify dependent layers recover automatically
  4. If dependent layers do not auto-recover: restart them in dependency order (database first, then services, then interfaces)
- **RTO breach**: If recovery takes longer than the documented RTO:
  1. Escalate immediately (do not wait for the full recovery attempt)
  2. Activate the next-tier recovery plan (e.g., failover to DR region)
  3. Post-incident: update the RTO to reflect reality, or improve the recovery mechanism
- **Detection blind spot discovered**: If a failure occurs that was not detected by monitoring:
  1. Add the failure scenario to the fault tolerance matrix immediately
  2. Implement detection metric and threshold
  3. Add to the adversarial test suite to prevent regression

### Anti-Patterns to Avoid
- Vague detection criteria ("monitor for errors" instead of "error_rate > 5% over 1min window")
- Vague RTO targets ("recover quickly" instead of "RTO: 30s")
- Missing LLM provider failover (single provider dependency is a P0 risk for an LLM-agnostic platform)
- No on-call procedures for P0 scenarios
- Testing only the happy path — fault tolerance must be tested with chaos engineering
- Ignoring cross-interface session drift (MCP and Dashboard sessions can diverge)

### Constraints
- ESCALATE if: no health check endpoints, no idempotency for critical operations, no circuit breaker pattern
