# Prompt 13 — Generate TESTING.md

## Role
You are a test strategy generator agent. You produce TESTING.md — Document #13 in the 14-document SDLC stack (Full-Stack-First approach).

## Input Required
- ARCH.md (languages, frameworks, all interfaces)
- QUALITY.md (coverage thresholds, performance NFRs)
- DATA-MODEL.md (database schema)
- CLAUDE.md (testing conventions)
- MCP-TOOL-SPEC.md (MCP tools to test)
- DESIGN-SPEC.md (dashboard screens to test)
- INTERACTION-MAP.md (cross-interface journeys to test)

## Output: TESTING.md

### Required Sections

1. **Test Pyramid** — Full-Stack test pyramid:
   ```
   ┌─────────────────────┐
   │   Cross-Interface    │  ← MCP trigger → Dashboard approval (fewest tests)
   ├─────────────────────┤
   │   Interface Tests    │  ← MCP protocol, REST API, Dashboard render
   ├─────────────────────┤
   │   Service Tests      │  ← Shared service unit + integration (most tests)
   ├─────────────────────┤
   │   Schema Tests       │  ← Data shape validation, migration
   └─────────────────────┘
   ```

2. **Test Frameworks** — Per layer: service tests (pytest), MCP tests (MCP Inspector + pytest), API tests (httpx/pytest), dashboard tests (Selenium/Playwright), cross-interface (full stack integration).

3. **Database Strategy** — Testcontainers for PostgreSQL. Real DB, never mocks.

4. **Shared Service Tests** — The most important test layer:
   - Every service method has unit tests with mocked dependencies
   - Every service method has integration tests with real database
   - Test the SAME service both MCP and REST will call

5. **MCP Tool Tests**:
   - Unit: Handler logic with mocked service
   - Protocol: MCP Inspector verifies tool schemas, descriptions
   - Integration: Full MCP client → tool → service → DB → response

6. **REST API Tests**:
   - Unit: Route handler with mocked service
   - Integration: HTTP client → route → service → DB → response

7. **Dashboard Tests**:
   - Component: Render tests with mocked API
   - Integration: Dashboard → REST API → service → DB → render

8. **Cross-Interface Tests** — NEW (Full-Stack-First only):
   - End-to-end tests that span interfaces:
     ```
     Test: Pipeline with approval handoff
     1. MCP client calls trigger_pipeline → gets run_id
     2. Pipeline runs to approval gate → pauses
     3. REST API: GET /approvals/pending → sees approval
     4. REST API: POST /approvals/{id}/approve → approved
     5. MCP client calls get_pipeline_status → sees completed
     ```
   - Parity tests:
     ```
     Test: MCP and REST return same data
     1. Call trigger_pipeline via MCP → get response A
     2. Call POST /api/v1/pipelines via REST with same input → get response B
     3. Assert A.data == B.data (same shared service, same shape)
     ```

9. **Coverage Thresholds** (from QUALITY.md):
   - Shared services: highest (90%+)
   - MCP handlers: high (85%+)
   - REST handlers: high (85%+)
   - Dashboard: medium (75%+)
   - Cross-interface: at least 1 test per INTERACTION-MAP cross-interface journey

10. **CI Pipeline**:
    ```
    Stage 1: Schema validation + lint
    Stage 2: Shared service unit tests
    Stage 3 (parallel): MCP tests | REST tests | Dashboard tests
    Stage 4: Cross-interface integration tests
    Stage 5: Performance tests (MCP latency, API latency, page load)
    ```

### Quality Criteria
- Test pyramid has shared services at the base (most tests)
- Cross-interface tests exist for every handoff journey
- Parity tests ensure MCP and REST return same data
- CI pipeline runs interface tests in parallel

11. **Error Handling & Recovery Strategy**:
    - **Document generation failure**: If an agent produces a document below the quality rubric threshold (< 0.75):
      1. Log the failure with rubric scores per dimension
      2. Retry with enhanced prompt (include specific rubric failures as guidance)
      3. Max 2 retries, then escalate to human review
    - **Dependency failure**: If a downstream document fails because an upstream document has bad data:
      1. Identify which upstream data shape or ID is incorrect
      2. Regenerate the upstream document (not just patch it)
      3. Regenerate all documents that depend on the fixed upstream
      4. Use the dependency graph from Correct Build Sequence.md to determine blast radius
    - **Cross-interface divergence detected**: If parity tests fail (MCP returns different data than REST):
      1. Check shared service — is it returning consistent results?
      2. Check MCP handler — is it transforming the service response?
      3. Check REST handler — same question
      4. Fix the handler that diverges, never fix the shared service to accommodate a broken handler
    - **Partial pipeline completion**: If the pipeline fails at step N:
      1. Documents 0 through N-1 are valid and should NOT be regenerated
      2. Resume from step N after fixing the issue
      3. Never restart from step 0 unless PRD or ARCH changes fundamentally

### Section: LLM Evaluation Framework
Testing strategy for non-deterministic agent outputs:

1. **Golden Path Tests**: Fixed input → validate output matches expected JSON schema
2. **Quality Scoring**: LLM-as-Judge evaluates each agent output on:
   - Schema compliance (0-1): Does output match expected structure?
   - Completeness (0-1): Are all required sections present?
   - Faithfulness (0-1): Does output cite actual data from input (not hallucinated)?
   - Consistency (0-1): Does output match previous runs on same input within tolerance?
3. **Prompt Regression Tests**: Before/after prompt change → compare quality scores
   - If any score drops > 5%, flag as regression
   - Store golden outputs per prompt version for comparison
4. **Adversarial Tests**: Prompt injection attempts, oversized inputs, malformed JSON
5. **Provider Portability Tests**: Run same agent on Anthropic and OpenAI → compare schema compliance
   - Outputs will differ in content but must match in structure

### Section: Go-Live Checklist (Production Readiness Gate)
Before any agent or service deploys to production:
- [ ] All golden tests pass
- [ ] Quality score ≥ 0.85 on all evaluation dimensions
- [ ] Security review completed (SECURITY-ARCH controls verified)
- [ ] Observability instrumented (metrics, logs, traces)
- [ ] Runbook exists for P0/P1 failure scenarios
- [ ] SLOs defined and measurable
- [ ] On-call rotation staffed
- [ ] Rollback procedure tested
- [ ] Cost estimate within budget
- [ ] Compliance controls documented in COMPLIANCE-MATRIX

### Anti-Patterns to Avoid
- Testing MCP and REST separately without parity tests
- No cross-interface tests
- Dashboard tests that mock the API instead of testing against real API (at least some integration)
- Shared services with lower coverage than handlers (should be highest)
- Retrying failed document generation without diagnosing why it failed
- Regenerating all documents when only one upstream changed
