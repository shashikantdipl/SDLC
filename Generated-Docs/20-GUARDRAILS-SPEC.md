# GUARDRAILS-SPEC — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-29
**Document:** 20 of 24 | Status: Draft
**Reads from:** ARCH (Doc 03), QUALITY (Doc 05), DATA-MODEL (Doc 10), API-CONTRACTS (Doc 11), FAULT-TOLERANCE (Doc 19)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Layer 1 — Input Guardrails](#2-layer-1--input-guardrails)
3. [Layer 2 — Processing Guardrails](#3-layer-2--processing-guardrails)
4. [Layer 3 — Output Guardrails](#4-layer-3--output-guardrails)
5. [Layer 4 — Governance Guardrails](#5-layer-4--governance-guardrails)
6. [Guardrail Decision Matrix](#6-guardrail-decision-matrix)
7. [Testing Strategy](#7-testing-strategy)

---

## 1. Overview

The Agentic SDLC Platform runs 48 AI agents that invoke external LLM providers (Anthropic, OpenAI, Ollama) to generate SDLC documentation. Every agent call passes through a 4-layer guardrail system that protects against prompt injection, data leakage, hallucination, cost overrun, and unauthorized actions.

### Guardrail Architecture

```
                        INPUT
                          |
                  +-------v--------+
                  | Layer 1: INPUT |
                  | - Injection    |
                  | - PII filter   |
                  | - Schema valid |
                  | - Token limit  |
                  +-------+--------+
                          |
                  +-------v-----------+
                  | Layer 2: PROCESS  |
                  | - Token budget    |
                  | - Timeout         |
                  | - Model pinning   |
                  | - Provider health |
                  +-------+-----------+
                          |
                     LLM CALL
                          |
                  +-------v--------+
                  | Layer 3: OUTPUT|
                  | - Hallucinate  |
                  | - Schema valid |
                  | - PII scan     |
                  | - ID format    |
                  | - Quality score|
                  +-------+--------+
                          |
                  +-------v-----------+
                  | Layer 4: GOVERN   |
                  | - Kill switches   |
                  | - HITL gates      |
                  | - Audit trail     |
                  | - Rate limiting   |
                  +-------+-----------+
                          |
                        OUTPUT
```

### Guardrail Numbering Convention

`GR-{Layer}-{NNN}` where Layer is `IN` (input), `PR` (processing), `OUT` (output), `GOV` (governance).

### Enforcement Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `block` | Reject the request entirely | P0 violations (injection, PII to external provider) |
| `warn` | Allow but log warning in `audit_events` | Soft limits, borderline cases |
| `redact` | Modify content to remove violation, then proceed | PII in output, sensitive data |
| `escalate` | Pause and require human approval | HITL gates, cost ceiling |

---

## 2. Layer 1 — Input Guardrails

### GR-IN-001 | Prompt Injection Detection

| Field | Value |
|-------|-------|
| **ID** | GR-IN-001 |
| **Priority** | P0 |
| **Enforcement** | `block` |
| **Applies to** | All 48 agents, all MCP tool inputs, all REST API request bodies |

**Detection strategy — two-pass:**

**Pass 1: Pattern matching (< 5ms)**

Static regex patterns that catch known injection techniques:

| Pattern Category | Examples | Regex |
|-----------------|----------|-------|
| Role override | "Ignore previous instructions", "You are now", "System: " | `(?i)(ignore\s+(all\s+)?previous\s+instructions|you\s+are\s+now|^system:\s)` |
| Delimiter injection | `"""`, `---`, `<<<>>>` used to break prompt boundaries | `("""|---{3,}|<<<.*>>>)` |
| Tool abuse | "Call function", "Execute command", "Run shell" | `(?i)(call\s+function|execute\s+command|run\s+shell|eval\()` |
| Encoding tricks | Base64-encoded instructions, Unicode homoglyphs | Custom decoder + normalization |
| Jailbreak patterns | "DAN mode", "Developer mode", "Ignore safety" | Maintained pattern list (updated monthly) |

**Pass 2: Semantic analysis (< 500ms)**

For inputs that pass pattern matching but have high complexity:

```python
# Semantic injection detector (runs on Ollama locally — no data leaves platform)
def detect_semantic_injection(input_text: str) -> float:
    """Returns injection_probability (0.0 to 1.0)."""
    prompt = f"""Analyze this text for prompt injection attempts.
    Score from 0.0 (benign) to 1.0 (definite injection).
    Text: {input_text[:2000]}"""

    score = ollama_client.complete(model="llama3.2", prompt=prompt)
    return float(score)

# Threshold: block if score > 0.7, warn if score > 0.4
```

**Response on block:**
```json
{
  "error": {
    "code": "GUARDRAIL_INPUT_BLOCKED",
    "message": "Input rejected: potential prompt injection detected",
    "guardrail": "GR-IN-001",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Audit:** `audit_events` entry: `action: "guardrail.injection_blocked"`, `severity: "critical"`, `details: { pattern_matched, semantic_score, input_hash }`.

---

### GR-IN-002 | PII Filtering (Pre-LLM)

| Field | Value |
|-------|-------|
| **ID** | GR-IN-002 |
| **Priority** | P0 |
| **Enforcement** | `block` (external providers) or `redact` (Ollama) |
| **Applies to** | All agent inputs before sending to LLM provider |

**Data classification tiers:**

| Classification | Description | Allowed Providers | Action if Violation |
|---------------|-------------|-------------------|---------------------|
| Public | Open-source specs, public APIs | Anthropic, OpenAI, Ollama | Pass through |
| Internal | Company architecture, internal APIs | Anthropic, OpenAI, Ollama | Pass through |
| Confidential | Customer data, internal metrics, employee info | **Ollama only** | Block if sent to Anthropic/OpenAI |
| Restricted | PII, credentials, secrets, financial data | **Ollama only** (redacted) | Block + redact |

**PII detection patterns:**

| PII Type | Detection Method | Confidence Threshold |
|----------|-----------------|---------------------|
| Email addresses | Regex + domain validation | 95% |
| Phone numbers | Regex + format validation | 90% |
| SSN / National ID | Regex (format-specific) | 99% |
| Credit card numbers | Regex + Luhn check | 99% |
| API keys / tokens | Regex (`sk-`, `ghp_`, `Bearer `) + entropy check | 95% |
| Names (personal) | NER model (spaCy) | 80% (warn), 95% (block) |
| Addresses (physical) | NER model (spaCy) | 80% (warn), 95% (block) |

**Routing decision:**
```python
def route_to_provider(input_data: dict, classification: str, agent_manifest: dict):
    if classification in ("confidential", "restricted"):
        if agent_manifest["provider"] != "ollama":
            # Re-route to Ollama for data safety
            log_audit("guardrail.pii_rerouted", {
                "original_provider": agent_manifest["provider"],
                "rerouted_to": "ollama",
                "classification": classification
            })
            return "ollama"
    return agent_manifest["provider"]
```

---

### GR-IN-003 | Input Schema Validation

| Field | Value |
|-------|-------|
| **ID** | GR-IN-003 |
| **Priority** | P1 |
| **Enforcement** | `block` |
| **Applies to** | All MCP tool inputs, REST API request bodies |

Every agent defines its expected input schema in `manifest.yaml`. Inputs are validated before the agent is invoked.

**Validation checks:**

| Check | Description | Example |
|-------|-------------|---------|
| Required fields present | All fields marked `required: true` in manifest | `trigger_pipeline` requires `project_id`, `pipeline_id` |
| Type correctness | Fields match declared types (string, number, boolean, object, array) | `project_id` must be string |
| Format compliance | Fields match declared formats (uuid, date, email, url) | `project_id` matches `proj-{slug}-{year}` |
| Enum membership | Fields with enums match allowed values | `pipeline_id` in `["document-stack"]` |
| String length | Min/max length constraints | `input.brief` between 100 and 50000 characters |
| Nested object validation | Recursive validation of nested structures | `input.gates` object validated |

**Response on block:**
```json
{
  "error": {
    "code": "GUARDRAIL_SCHEMA_INVALID",
    "message": "Input validation failed",
    "guardrail": "GR-IN-003",
    "violations": [
      { "field": "project_id", "issue": "required field missing" },
      { "field": "input.brief", "issue": "length 42 < minimum 100" }
    ]
  }
}
```

---

### GR-IN-004 | Token Size Limits

| Field | Value |
|-------|-------|
| **ID** | GR-IN-004 |
| **Priority** | P1 |
| **Enforcement** | `block` |
| **Applies to** | All agent inputs (system prompt + user input + context) |

**Token limits by agent tier:**

| Agent Tier | Max Input Tokens | Max Output Tokens | Max Total Tokens | Example Agents |
|-----------|-----------------|-------------------|-----------------|----------------|
| Tier 0 (governance) | 8,000 | 4,000 | 12,000 | G1-cost-tracker, G2-audit-trail-validator |
| Tier 1 (simple generation) | 16,000 | 8,000 | 24,000 | D1-D5 (early design agents) |
| Tier 2 (complex generation) | 32,000 | 16,000 | 48,000 | D6-D13 (complex design agents), B1-B9 |
| Tier 3 (orchestration) | 64,000 | 8,000 | 72,000 | G4-team-orchestrator |

**Token counting:**
```python
def check_token_limit(agent_id: str, system_prompt: str, user_input: str, context: str):
    manifest = load_manifest(agent_id)
    tier = manifest["tier"]
    limits = TOKEN_LIMITS[tier]

    total_tokens = count_tokens(system_prompt + user_input + context)

    if total_tokens > limits["max_input_tokens"]:
        raise GuardrailBlocked(
            guardrail="GR-IN-004",
            message=f"Input tokens ({total_tokens}) exceed limit ({limits['max_input_tokens']}) for tier {tier}",
            details={"agent_id": agent_id, "tokens": total_tokens, "limit": limits["max_input_tokens"]}
        )
```

---

## 3. Layer 2 — Processing Guardrails

### GR-PR-001 | Token Budget Enforcement

| Field | Value |
|-------|-------|
| **ID** | GR-PR-001 |
| **Priority** | P0 |
| **Enforcement** | `block` (abort stream) |
| **Applies to** | All LLM API calls |

**Budget hierarchy:**

| Scope | Budget | Enforced By | Action on Breach |
|-------|--------|-------------|-----------------|
| Per-call | $0.50 | LLM adapter middleware | Abort streaming response |
| Per-agent (daily) | $5.00 | G1-cost-tracker | Disable agent for remainder of day |
| Per-pipeline run | $25.00 (standard), $45.00 (hard ceiling) | G1-cost-tracker | Pause pipeline (standard), halt pipeline (hard) |
| Per-project (monthly) | $500.00 | G1-cost-tracker | Alert project owner, require approval to continue |
| Platform (daily) | $200.00 | G1-cost-tracker | Alert platform admin, shed low-priority work |

**Real-time cost tracking:**
```python
async def enforce_token_budget(agent_id: str, run_id: str, stream):
    """Wraps LLM streaming response with cost enforcement."""
    running_cost = 0.0
    async for chunk in stream:
        token_cost = calculate_cost(chunk, model=stream.model)
        running_cost += token_cost

        # Per-call check
        if running_cost > 0.50:
            await stream.abort()
            await log_cost_breach(agent_id, run_id, running_cost, "per_call")
            raise GuardrailBlocked(guardrail="GR-PR-001", scope="per_call")

        # Update running total in cost_metrics
        await update_running_cost(agent_id, run_id, running_cost)

        yield chunk
```

**Cost recorded in `cost_metrics`:**
```sql
INSERT INTO cost_metrics (
  agent_id, pipeline_run_id, project_id, provider,
  model, input_tokens, output_tokens, cost_usd, created_at
) VALUES (
  'G1-cost-tracker', 'run-abc-123', 'proj-acme-2026', 'anthropic',
  'claude-sonnet-4-20250514', 1500, 800, 0.012, NOW()
);
```

---

### GR-PR-002 | Timeout Enforcement

| Field | Value |
|-------|-------|
| **ID** | GR-PR-002 |
| **Priority** | P1 |
| **Enforcement** | `block` (kill call) + circuit breaker |
| **Applies to** | All LLM API calls |

**Timeout configuration:**

| Timeout Type | Duration | Action on Timeout |
|-------------|----------|-------------------|
| Single call timeout | 120 seconds (default) | Kill call, log, retry once |
| Streaming first-byte | 30 seconds | Kill call, failover to secondary provider |
| Total pipeline step | 300 seconds | Kill step, mark as failed, proceed to retry logic |

**Circuit breaker (per provider):**

| Parameter | Value |
|-----------|-------|
| Failure threshold | 5 timeouts in 5-minute window |
| State transition | `closed` → `open` (reject all calls to this provider) |
| Half-open after | 60 seconds (allow 1 test call) |
| Reset after | 3 consecutive successes in half-open state |

```python
class ProviderCircuitBreaker:
    def __init__(self, provider: str):
        self.provider = provider
        self.state = "closed"  # closed | open | half_open
        self.failure_count = 0
        self.last_failure = None

    async def call(self, request):
        if self.state == "open":
            if time_since(self.last_failure) > 60:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpen(self.provider)

        try:
            result = await self.provider_client.call(request, timeout=120)
            self._on_success()
            return result
        except TimeoutError:
            self._on_failure()
            raise
```

---

### GR-PR-003 | Model Pinning

| Field | Value |
|-------|-------|
| **ID** | GR-PR-003 |
| **Priority** | P1 |
| **Enforcement** | `block` |
| **Applies to** | All agent LLM calls |

Each agent's `manifest.yaml` specifies the exact model version to use. The guardrail prevents agents from using unregistered models.

**Model registry:**

| Provider | Model ID | Tier | Cost (input/1K) | Cost (output/1K) | Approved |
|----------|----------|------|-----------------|------------------|----------|
| Anthropic | `claude-sonnet-4-20250514` | Production | $0.003 | $0.015 | Yes |
| Anthropic | `claude-haiku-35-20241022` | Budget | $0.0008 | $0.004 | Yes |
| OpenAI | `gpt-4o-2024-11-20` | Production | $0.0025 | $0.010 | Yes |
| OpenAI | `gpt-4o-mini-2024-07-18` | Budget | $0.00015 | $0.0006 | Yes |
| Ollama | `llama3.2:latest` | Local/Free | $0.00 | $0.00 | Yes |
| Ollama | `mistral:latest` | Local/Free | $0.00 | $0.00 | Yes |

**Pinning rules:**
1. Production environment: only models with `approved: true` in the registry
2. Agent manifest declares `model_id` — guardrail verifies the call uses this exact model
3. Model version changes require PR review and approval via `POST /api/v1/agents/{id}/update-model`
4. Canary deployments (via `agent_registry.canary_version`) may use a different model for `canary_traffic_pct` of calls

---

### GR-PR-004 | Provider Health Monitoring

| Field | Value |
|-------|-------|
| **ID** | GR-PR-004 |
| **Priority** | P1 |
| **Enforcement** | `warn` → `block` (if unhealthy) |
| **Applies to** | All LLM provider calls |

**Health check protocol:**

| Check | Frequency | Method | Healthy Threshold |
|-------|-----------|--------|-------------------|
| Latency probe | Every 30s | Lightweight completion request (10 tokens) | < 5s response |
| Error rate | Rolling 5-min window | Track 4xx/5xx from real traffic | < 5% error rate |
| Rate limit headroom | Every 60s | Check `x-ratelimit-remaining` headers | > 20% remaining |

**Provider health state in `agent_registry`:**
```sql
-- Provider health tracked per-agent (agents may use different providers)
SELECT agent_id, provider, provider_status,
       circuit_breaker_state, last_health_check_at
FROM agent_registry
WHERE provider_status != 'healthy';
```

**Unhealthy provider actions:**
1. Log to `audit_events`: `action: "guardrail.provider_unhealthy"`
2. Agents with `failover_provider` in manifest: automatically switch
3. Agents without failover: queue calls, retry after health recovers
4. If unhealthy > 5 minutes: alert on-call via PagerDuty

---

## 4. Layer 3 — Output Guardrails

### GR-OUT-001 | Hallucination Detection

| Field | Value |
|-------|-------|
| **ID** | GR-OUT-001 |
| **Priority** | P0 |
| **Enforcement** | `block` (discard output, retry) |
| **Applies to** | All agent outputs that reference platform entities |

**Detection method — entity cross-reference:**

The guardrail extracts all entity references from the agent output and verifies each against the input data and known platform entities.

| Entity Type | Format | Verification Source |
|-------------|--------|-------------------|
| Feature IDs | `F-NNN` | `input_data.features[]` or FEATURE-CATALOG |
| Quality requirements | `Q-NNN` | `input_data.quality[]` or QUALITY doc |
| User stories | `US-{DOMAIN}-NNN` | `input_data.stories[]` or BACKLOG |
| Agent IDs | `{PHASE}{N}-{name}` | `agent_registry` table |
| API endpoints | `/api/v1/*` | API-CONTRACTS doc or route registry |
| Table names | `*` (SQL identifiers) | DATA-MODEL schema |
| MCP tool names | `*` | MCP-TOOL-SPEC tool registry |

**Verification process:**
```python
async def check_hallucination(output: str, input_context: dict) -> HallucinationResult:
    """Cross-reference output entities against input data."""
    entities = extract_entities(output)
    hallucinated = []

    for entity in entities:
        if entity.type == "feature_id":
            if entity.value not in input_context.get("features", []):
                hallucinated.append(entity)
        elif entity.type == "agent_id":
            if not await agent_registry_contains(entity.value):
                hallucinated.append(entity)
        elif entity.type == "table_name":
            if entity.value not in KNOWN_TABLES:
                hallucinated.append(entity)
        # ... similar for each entity type

    return HallucinationResult(
        is_hallucinated=len(hallucinated) > 0,
        hallucinated_entities=hallucinated,
        total_entities=len(entities),
        faithfulness_score=1.0 - (len(hallucinated) / max(len(entities), 1))
    )
```

**Known tables (from DATA-MODEL):**
`agent_registry`, `cost_metrics`, `audit_events`, `pipeline_runs`, `pipeline_steps`, `knowledge_exceptions`, `session_context`, `approval_requests`, `pipeline_checkpoints`, `mcp_call_events`

---

### GR-OUT-002 | JSON Schema Validation for Structured Outputs

| Field | Value |
|-------|-------|
| **ID** | GR-OUT-002 |
| **Priority** | P1 |
| **Enforcement** | `block` (retry with schema reminder) |
| **Applies to** | All agents that produce structured (JSON) output |

**Validation against INTERACTION-MAP data shapes:**

Each agent declares its output shape in `manifest.yaml`. The guardrail validates that the actual output conforms to the declared shape.

| Output Shape | Required Fields | Validation |
|-------------|----------------|------------|
| `PipelineRun` | `id`, `project_id`, `status`, `triggered_at` | JSON Schema + enum check on `status` |
| `AgentSummary` | `agent_id`, `name`, `phase`, `status` | JSON Schema + agent_id format check |
| `CostReport` | `scope`, `period`, `total_usd`, `by_agent[]` | JSON Schema + numeric range check |
| `AuditEvent` | `id`, `action`, `agent_id`, `severity`, `created_at` | JSON Schema + ISO 8601 date check |
| `ApprovalRequest` | `id`, `pipeline_run_id`, `request_type`, `status` | JSON Schema + enum check on `status` |

**Retry on failure:**
```python
if not validate_json_schema(output, expected_shape):
    # Retry with explicit schema in prompt
    retry_prompt = f"""Your previous output did not match the required schema.
    Required schema: {json.dumps(expected_shape)}
    Violations: {violations}
    Please regenerate, strictly following the schema."""
    output = await invoke_agent(agent_id, retry_prompt)
```

---

### GR-OUT-003 | PII Leakage Scan (Post-LLM)

| Field | Value |
|-------|-------|
| **ID** | GR-OUT-003 |
| **Priority** | P0 |
| **Enforcement** | `redact` |
| **Applies to** | All agent outputs before delivery to caller |

Uses the same PII detection patterns as GR-IN-002 but applied to the output. If PII is detected in the output that was not present in the input, it is hallucinated PII (doubly concerning).

**Redaction process:**
```python
async def scan_and_redact_output(output: str, input_data: dict) -> RedactionResult:
    pii_found = detect_pii(output)

    for pii in pii_found:
        if pii.value not in str(input_data):
            # Hallucinated PII — flag as critical
            pii.hallucinated = True
            log_audit("guardrail.pii_hallucinated", severity="critical", details=pii)

        output = output.replace(pii.value, pii.redaction_token)

    return RedactionResult(
        redacted_output=output,
        pii_count=len(pii_found),
        hallucinated_pii_count=sum(1 for p in pii_found if p.hallucinated)
    )
```

**Audit:** Every PII detection logged to `audit_events` with `action: "guardrail.pii_output_redacted"`.

---

### GR-OUT-004 | ID Format Validation

| Field | Value |
|-------|-------|
| **ID** | GR-OUT-004 |
| **Priority** | P2 |
| **Enforcement** | `warn` |
| **Applies to** | All agents generating documents with cross-references |

**Expected ID formats:**

| ID Type | Format | Regex | Example |
|---------|--------|-------|---------|
| Feature ID | `F-NNN` | `^F-\d{3}$` | `F-001`, `F-042` |
| Quality Requirement | `Q-NNN` | `^Q-\d{3}$` | `Q-001`, `Q-049` |
| User Story | `US-{DOMAIN}-NNN` | `^US-[A-Z]+-\d{3}$` | `US-PIPE-001`, `US-COST-003` |
| Interaction | `I-NNN` | `^I-\d{3}$` | `I-001`, `I-045` |
| Agent ID | `{PHASE}{N}-{name}` | `^[A-Z]\d+-[a-z-]+$` | `G1-cost-tracker`, `D12-localisation-planner` |
| Pipeline Run | `run-{uuid-short}` | `^run-[a-f0-9-]+$` | `run-abc-123-def` |
| Project ID | `proj-{slug}-{year}` | `^proj-[a-z-]+-\d{4}$` | `proj-acme-2026` |

**Validation:**
```python
def validate_ids_in_output(output: str) -> list[IDViolation]:
    violations = []
    for id_type, pattern in ID_PATTERNS.items():
        found_ids = extract_ids(output, id_type)
        for found_id in found_ids:
            if not re.match(pattern, found_id):
                violations.append(IDViolation(
                    id_type=id_type, found=found_id, expected_pattern=pattern
                ))
    return violations
```

---

### GR-OUT-005 | Quality Scoring

| Field | Value |
|-------|-------|
| **ID** | GR-OUT-005 |
| **Priority** | P0 |
| **Enforcement** | `block` (if score < threshold) → retry → escalate |
| **Applies to** | All pipeline step outputs |

**Quality dimensions (from QUALITY Doc 05):**

| Dimension | Weight | Measurement | Threshold |
|-----------|--------|-------------|-----------|
| Schema compliance | 25% | % of required sections present in output | >= 90% |
| Completeness | 25% | % of input concepts addressed in output | >= 80% |
| Faithfulness | 30% | % of output claims traceable to input | >= 85% |
| Consistency | 20% | % of cross-references that resolve to valid entities | >= 90% |

**Composite quality score:**
```python
def calculate_quality_score(output: str, input_data: dict, doc_schema: dict) -> float:
    schema_score = check_schema_compliance(output, doc_schema)      # 0.0-1.0
    completeness = check_completeness(output, input_data)           # 0.0-1.0
    faithfulness = check_faithfulness(output, input_data)           # 0.0-1.0
    consistency = check_cross_references(output)                    # 0.0-1.0

    composite = (
        schema_score * 0.25 +
        completeness * 0.25 +
        faithfulness * 0.30 +
        consistency * 0.20
    )
    return composite

# Stored in pipeline_steps.quality_score
```

**Score thresholds:**

| Score Range | Action |
|-------------|--------|
| >= 85% | Accept — proceed to next pipeline step |
| 70% - 84% | Retry with feedback (max 2 retries, per FUNC-001) |
| < 70% | Escalate to human review via `approval_requests` |

---

## 5. Layer 4 — Governance Guardrails

### GR-GOV-001 | Kill Switches

| Field | Value |
|-------|-------|
| **ID** | GR-GOV-001 |
| **Priority** | P0 |
| **Enforcement** | `block` (immediate) |
| **Applies to** | All agent invocations |

**Kill switch scopes:**

| Scope | Activation | Effect | Activation Method |
|-------|-----------|--------|-------------------|
| Per-agent | Disable single agent | All calls to that agent rejected with 503 | `POST /api/v1/agents/{id}/disable` |
| Per-provider | Disable LLM provider | All agents using that provider fail over or reject | `POST /api/v1/system/providers/{name}/disable` |
| Per-project | Disable all pipelines for a project | No new pipeline runs; in-flight paused | `POST /api/v1/pipelines/disable?project_id={id}` |
| Global | Disable ALL agent invocations | Platform enters read-only mode | `POST /api/v1/system/kill-switch` |

**Kill switch state stored in `agent_registry`:**
```sql
-- Per-agent kill switch
UPDATE agent_registry
SET status = 'disabled', disabled_reason = '{reason}', disabled_by = '{user}'
WHERE agent_id = '{agent_id}';

-- Check kill switch before every invocation
SELECT status, disabled_reason FROM agent_registry WHERE agent_id = '{agent_id}';
-- If status = 'disabled', reject with: "Agent disabled: {reason}"
```

**Global kill switch:**
```sql
-- Stored in system configuration (environment variable or config table)
-- GLOBAL_KILL_SWITCH=true → all agent calls rejected
-- Checked at the top of every agent invocation path
```

**Audit:** Every kill switch activation/deactivation logged to `audit_events` with `action: "governance.kill_switch"`, `details: { scope, target, activated_by, reason }`.

---

### GR-GOV-002 | Human-in-the-Loop (HITL) Gates

| Field | Value |
|-------|-------|
| **ID** | GR-GOV-002 |
| **Priority** | P0 |
| **Enforcement** | `escalate` |
| **Applies to** | Pipeline steps configured with approval gates |

**Autonomy tiers (from ARCH Doc 03):**

| Tier | Label | Human Involvement | Example Agents |
|------|-------|-------------------|----------------|
| T0 | Full autonomy | No human review | G1-cost-tracker, G2-audit-trail-validator |
| T1 | Post-review | Human reviews after execution | D1-D5 (simple design agents) |
| T2 | Pre-approval | Human approves before execution | D6-D13 (complex design agents), B1-B9 |
| T3 | Human-driven | Agent assists, human decides | G4-team-orchestrator (pipeline config changes) |

**Gate enforcement:**
```python
async def enforce_hitl_gate(agent_id: str, run_id: str, step_name: str):
    manifest = await load_manifest(agent_id)
    tier = manifest["autonomy_tier"]

    if tier == "T2":
        # Create approval request BEFORE execution
        await create_approval_request(
            pipeline_run_id=run_id,
            step_name=step_name,
            request_type="pre_approval",
            assignee=manifest.get("approval_assignee", "tech_lead")
        )
        # Pipeline pauses here until approved
        # Approval via: POST /api/v1/approvals/{id}/approve
        # Or MCP: approve_gate tool

    elif tier == "T1":
        # Execute first, then request review
        output = await execute_agent(agent_id, ...)
        await create_approval_request(
            pipeline_run_id=run_id,
            step_name=step_name,
            request_type="post_review",
            output_preview=output[:500]
        )
```

**Approval stored in `approval_requests`:**
```sql
INSERT INTO approval_requests (
  pipeline_run_id, step_name, request_type, status,
  assignee, details, created_at
) VALUES (
  '{run_id}', '{step_name}', 'pre_approval', 'pending',
  'jason', '{"agent_id": "D8-api-designer", "tier": "T2"}', NOW()
);
```

---

### GR-GOV-003 | Audit Trail

| Field | Value |
|-------|-------|
| **ID** | GR-GOV-003 |
| **Priority** | P0 |
| **Enforcement** | Always active (no bypass) |
| **Applies to** | Every guardrail trigger, every agent invocation, every state change |

**What gets logged:**

| Event Category | Logged Fields | Table |
|---------------|---------------|-------|
| Guardrail trigger | `guardrail_id`, `action`, `enforcement`, `input_hash`, `agent_id` | `audit_events` |
| Agent invocation | `agent_id`, `provider`, `model`, `tokens`, `cost_usd`, `duration_ms` | `audit_events` + `cost_metrics` |
| Pipeline state change | `run_id`, `from_status`, `to_status`, `step_name` | `audit_events` |
| Kill switch toggle | `scope`, `target`, `activated_by`, `reason` | `audit_events` |
| Approval decision | `request_id`, `decision`, `decided_by`, `comments` | `audit_events` + `approval_requests` |
| Provider failover | `from_provider`, `to_provider`, `reason` | `audit_events` |

**Immutability guarantee:**
- `audit_events` table is append-only (no UPDATE or DELETE)
- RLS policy prevents modification
- Nightly reconciliation (CROSS-002 in FAULT-TOLERANCE) verifies integrity
- G2-audit-trail-validator agent periodically validates the trail

---

### GR-GOV-004 | Rate Limiting

| Field | Value |
|-------|-------|
| **ID** | GR-GOV-004 |
| **Priority** | P1 |
| **Enforcement** | `block` (HTTP 429) |
| **Applies to** | REST API endpoints, MCP tool calls |

**Rate limit tiers:**

| Scope | Limit | Window | Applies To |
|-------|-------|--------|-----------|
| Per-agent | 60 calls | 1 minute | Individual agent invocations |
| Per-provider | 100 calls | 1 minute | LLM API calls to single provider |
| Per-project | 200 API calls | 1 minute | All REST/MCP calls for a project |
| Per-user | 300 API calls | 1 minute | All calls from a single authenticated user |
| Global | 1000 API calls | 1 minute | Total platform throughput |

**Implementation:**
```python
# Token bucket rate limiter (in-memory, per-process)
class RateLimiter:
    def __init__(self, rate: int, window_seconds: int):
        self.rate = rate
        self.window = window_seconds
        self.buckets: dict[str, TokenBucket] = {}

    async def check(self, key: str) -> bool:
        bucket = self.buckets.setdefault(key, TokenBucket(self.rate, self.window))
        if bucket.consume():
            return True
        else:
            log_audit("guardrail.rate_limited", details={"key": key, "rate": self.rate})
            raise RateLimitExceeded(key, self.rate, self.window)
```

**Rate limit headers (REST API):**
```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 287
X-RateLimit-Reset: 1711670460
Retry-After: 12  (only on 429 response)
```

---

## 6. Guardrail Decision Matrix

| Guardrail ID | Layer | Priority | Enforcement | RTO | Automated | Dependencies |
|-------------|-------|----------|-------------|-----|-----------|-------------|
| GR-IN-001 | Input | P0 | block | < 5ms (pattern) / < 500ms (semantic) | Yes | Ollama (semantic pass) |
| GR-IN-002 | Input | P0 | block/redact | < 100ms | Yes | spaCy NER model |
| GR-IN-003 | Input | P1 | block | < 10ms | Yes | Agent manifests |
| GR-IN-004 | Input | P1 | block | < 5ms | Yes | Token counter |
| GR-PR-001 | Processing | P0 | block | < 2s | Yes | G1-cost-tracker |
| GR-PR-002 | Processing | P1 | block | 120s (timeout) | Yes | Circuit breaker state |
| GR-PR-003 | Processing | P1 | block | < 5ms | Yes | Model registry |
| GR-PR-004 | Processing | P1 | warn/block | 30s (probe) | Yes | Provider APIs |
| GR-OUT-001 | Output | P0 | block | 1-5s | Yes | Entity extractor |
| GR-OUT-002 | Output | P1 | block | < 100ms | Yes | JSON Schema definitions |
| GR-OUT-003 | Output | P0 | redact | < 200ms | Yes | PII detector |
| GR-OUT-004 | Output | P2 | warn | < 50ms | Yes | ID regex patterns |
| GR-OUT-005 | Output | P0 | block/escalate | 5-30s | Partial (human escalation) | Quality scorer |
| GR-GOV-001 | Governance | P0 | block | immediate | Yes | `agent_registry.status` |
| GR-GOV-002 | Governance | P0 | escalate | N/A (human wait) | No (by design) | `approval_requests` |
| GR-GOV-003 | Governance | P0 | always-on | N/A | Yes | `audit_events` table |
| GR-GOV-004 | Governance | P1 | block | immediate | Yes | In-memory token buckets |

### Summary Counts

| Layer | Guardrails | P0 | P1 | P2 |
|-------|-----------|----|----|-----|
| Input | 4 | 2 | 2 | 0 |
| Processing | 4 | 1 | 3 | 0 |
| Output | 5 | 3 | 1 | 1 |
| Governance | 4 | 3 | 1 | 0 |
| **Total** | **17** | **9** | **7** | **1** |

---

## 7. Testing Strategy

### 7.1 Adversarial Test Suite

Automated test suite that attempts to bypass each guardrail. Run on every deployment and nightly.

| Test Category | Test Count | Guardrails Tested | Method |
|--------------|-----------|-------------------|--------|
| Prompt injection variants | 200+ | GR-IN-001 | Known injection patterns + generated variants |
| PII injection | 50+ | GR-IN-002, GR-OUT-003 | Synthetic PII in various formats |
| Schema violations | 100+ | GR-IN-003, GR-OUT-002 | Malformed inputs, missing fields, wrong types |
| Token overflow | 20+ | GR-IN-004, GR-PR-001 | Oversized inputs, verbose prompts |
| Timeout scenarios | 15+ | GR-PR-002 | Mock slow provider responses |
| Hallucination seeds | 50+ | GR-OUT-001 | Inputs designed to trigger fabrication |
| ID format violations | 30+ | GR-OUT-004 | Invalid ID formats in mock outputs |
| Rate limit flood | 10+ | GR-GOV-004 | Burst traffic patterns |

**Test execution:**
```bash
# Run full adversarial suite
pytest tests/guardrails/ -v --adversarial

# Run specific layer
pytest tests/guardrails/test_input_guardrails.py -v
pytest tests/guardrails/test_output_guardrails.py -v

# Run with coverage
pytest tests/guardrails/ --cov=src/guardrails --cov-report=html
```

### 7.2 Chaos Testing

Inject failures to verify guardrail resilience:

| Chaos Scenario | Guardrails Exercised | Injection Method |
|---------------|---------------------|------------------|
| LLM provider returns garbage | GR-OUT-001, GR-OUT-002 | Mock provider returns random bytes |
| LLM provider 10x latency | GR-PR-002, GR-PR-004 | Network delay injection |
| Database connection dropped | GR-GOV-003 (buffering), CROSS-001 | Kill DB connection mid-write |
| Agent manifest corrupted | GR-IN-003, GR-PR-003 | Modify YAML file at runtime |
| Token counter underreports | GR-PR-001 | Mock token counter returns 50% of actual |
| PII detector false negative | GR-OUT-003 | Inject novel PII format not in regex set |

**Chaos testing schedule:**
- **Weekly** (automated): Random subset of 3 chaos scenarios
- **Monthly** (manual): Full chaos suite with team observation
- **Pre-release**: All chaos scenarios before any production deployment

### 7.3 Red Team Protocol

Quarterly red team exercise with external or cross-team participants.

**Red team scope:**
1. **Prompt injection bypass** — attempt to get agents to ignore system prompts
2. **PII exfiltration** — attempt to extract PII through agent outputs
3. **Cost abuse** — attempt to trigger excessive LLM spending
4. **Privilege escalation** — attempt to invoke agents above authorized tier
5. **Data isolation breach** — attempt to access data from other projects (CROSS-003)

**Red team rules of engagement:**
- Scope limited to staging environment
- No attacks on infrastructure (only application-layer)
- All findings logged and reported within 48 hours
- P0 findings trigger immediate production mitigation

**Red team output:**
- Findings report with severity ratings
- Guardrail bypass techniques documented
- Remediation recommendations
- Updated adversarial test suite with new attack patterns

### 7.4 Guardrail Monitoring Dashboard

Real-time metrics on Fleet Health and Audit Log dashboard pages:

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Injection blocks / hour | `audit_events` WHERE `action = 'guardrail.injection_blocked'` | > 10 / hour (potential attack) |
| PII detections / day | `audit_events` WHERE `action LIKE 'guardrail.pii%'` | > 5 / day (review data handling) |
| Quality gate failures / day | `audit_events` WHERE `action = 'pipeline.quality_gate_fail'` | > 20% of pipeline steps |
| Kill switch activations / week | `audit_events` WHERE `action = 'governance.kill_switch'` | Any activation |
| Rate limit hits / hour | `audit_events` WHERE `action = 'guardrail.rate_limited'` | > 100 / hour |
| Circuit breaker opens / day | `audit_events` WHERE `action LIKE 'fault.app_002%'` | > 3 / day |

---

*End of GUARDRAILS-SPEC. This document defines the safety boundary for all 48 agents. No agent invocation bypasses these guardrails. Review and update quarterly, or immediately after any red team finding.*
