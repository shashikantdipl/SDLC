# Prompt 4 — Generate QUALITY.md

## Role
You are a quality spec generator agent. You produce QUALITY.md — Document #4 in the 14-document SDLC stack (Full-Stack-First approach).

## Input Required
- PRD.md (success metrics)
- ARCH.md (infrastructure, MCP servers, dashboard, shared services)

## Output: QUALITY.md

### Required Format
```
Q-NNN: [Category] — [Imperative rule with specific threshold]. Verify: [automated method].
```

### Required Categories

1. **Performance** (8+ NFRs):
   - MCP tool response time (p95)
   - REST API response time (p95)
   - Dashboard page load time
   - Dashboard real-time update latency
   - Shared service call latency
   - MCP server startup time

2. **Reliability** (5+ NFRs):
   - MCP server crash recovery
   - REST API uptime
   - Dashboard availability
   - Service layer error rate

3. **Security** (8+ NFRs):
   - MCP authentication
   - REST API authentication (JWT + API key)
   - Dashboard authentication (session)
   - MCP tool input validation
   - API input validation
   - Dashboard XSS/CSRF protection

4. **Accessibility** (4+ NFRs):
   - Dashboard WCAG compliance
   - Dashboard keyboard navigation
   - Dashboard screen reader support

5. **Coverage** (6+ NFRs):
   - Shared service test coverage (highest — it's the core)
   - MCP tool handler coverage
   - API route handler coverage
   - Dashboard component coverage
   - Integration test coverage (cross-interface)

6. **Observability** (5+ NFRs):
   - MCP tool call audit logging
   - API request logging
   - Dashboard user action logging
   - Cross-interface correlation (trace ID spans MCP → service → DB)

7. **Interface Parity** (2+ NFRs) — NEW:
   - Every MCP tool must have a REST equivalent (measured by parity check)
   - MCP and REST must return consistent error codes for same operation

8. **Data** (3+ NFRs)

9. **Compliance Matrix**

10. **Quality Scoring Rubric** — Define how documents and outputs are scored:
    ```yaml
    quality_rubric:
      completeness:
        weight: 0.25
        threshold: 0.85
        description: "All required sections present, all fields populated"
        verify: "Schema validation against document template"
      accuracy:
        weight: 0.30
        threshold: 0.85
        description: "Facts match source inputs, no hallucinated data"
        verify: "Cross-reference check against input documents"
      format_compliance:
        weight: 0.15
        threshold: 0.95
        description: "Follows naming conventions, ID formats, data shapes"
        verify: "Regex/schema validation of IDs, names, shapes"
      cross_interface_parity:
        weight: 0.15
        threshold: 1.00
        description: "MCP and REST return identical data for same operation"
        verify: "Automated parity test suite"
      traceability:
        weight: 0.15
        threshold: 0.90
        description: "Every item traces back to PRD capability or INTERACTION-MAP ID"
        verify: "Linkage check: every F-NNN → C-NNN, every S-NNN → I-NNN"

    scoring:
      pass: ">= 0.85 weighted average"
      conditional_pass: ">= 0.75 weighted average (must fix within 1 sprint)"
      fail: "< 0.75 weighted average (regenerate document)"
    ```

    Every document output must pass the rubric before downstream documents can consume it.

### Section: Per-Module Coverage Thresholds
Coverage thresholds are NOT global — they vary by module complexity and risk:
- AI guardrail modules (agent safety, PII detection): ≥ 95% line coverage
- Core business logic (pipeline orchestration, cost enforcement): ≥ 90%
- Shared services (CostService, AuditService): ≥ 85%
- API routes and MCP handlers: ≥ 80%
- Dashboard/UI components: ≥ 70%
- Utilities and helpers: ≥ 60%

Reference FEATURE-CATALOG epic groupings to assign modules to tiers.

### Section: SLI/SLO Summary
Formalize NFRs into operational Service Level Objectives:
Table: Service | SLI (what to measure) | SLO (target) | Error Budget (allowed failures/month) | Measurement Method
Example:
- MCP Server | Request latency p99 | < 500ms | 0.1% of requests can exceed | OpenTelemetry histogram
- Pipeline | End-to-end completion | < 30 min for 14-step pipeline | 1 failure per 20 runs | Pipeline completion event
- Cost Tracker | Budget accuracy | ±5% of actual spend | N/A (accuracy metric) | Monthly reconciliation

### Quality Criteria
- NFRs cover all 3 interfaces (MCP, REST, dashboard) in every applicable category
- Shared service coverage is the highest threshold (it's the shared foundation)
- Interface parity NFRs exist

### Anti-Patterns to Avoid
- NFRs only for REST API (forgetting MCP and dashboard)
- No interface parity requirements
- Dashboard accessibility missing
