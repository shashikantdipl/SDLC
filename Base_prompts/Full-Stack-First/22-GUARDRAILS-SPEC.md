# Prompt 22 — Generate GUARDRAILS-SPEC.md

## Role
You are an AI safety guardrails agent. You produce GUARDRAILS-SPEC.md — Document #22 in the 24-document SDLC stack (Full-Stack-First approach). This document defines the 4-layer defense-in-depth guardrail architecture that protects the platform from AI-specific risks: prompt injection, hallucination, data leakage, toxicity, and runaway costs.

This document does NOT exist in traditional SDLC — it is unique to AI-native platforms.

## Approach: Full-Stack-First
Guardrails protect ALL agent interactions across:
1. MCP tool calls (agents invoking tools with LLM-generated parameters)
2. REST API responses (LLM-generated content served to dashboard)
3. Agent-to-agent handoffs (output of one agent becomes input to next)
4. Direct LLM API calls (every call through sdk/llm/LLMProvider)

## Input Required
- ARCH.md (agent topology, data flow)
- SECURITY-ARCH.md (threat model, data classification)
- ENFORCEMENT.md (coding rules)
- QUALITY.md (quality gates, safety NFRs)
- AGENT-HANDOFF-PROTOCOL.md (inter-agent data flow)

## Output: GUARDRAILS-SPEC.md

### Required Sections

1. **Layer 1: Input Guardrails (Before LLM Call)** — What gets checked BEFORE sending to the LLM:

   1. **Prompt Injection Detection**
      - Pattern matching for known injection patterns
      - Semantic analysis for instruction override attempts
      - Input sanitization rules per agent
      - Action on detection: Block + log + alert

   2. **PII/Sensitive Data Filtering**
      - Scan input for PII before sending to external LLM provider
      - Classification-aware: Confidential/Restricted data NEVER sent to external LLM
      - Redaction strategy: Replace with tokens, restore after response
      - Ollama (local) exemption: Local models can process Restricted data

   3. **Input Validation**
      - Schema validation against manifest input_schema
      - Size limits (max tokens per input)
      - Dependency verification (all required session keys present)

2. **Layer 2: Processing Guardrails (During LLM Call)** — What limits apply during generation:

   1. **Token Budget Enforcement**
      - Per-call max_tokens from manifest
      - Per-agent budget from safety.max_budget_usd
      - Per-pipeline cost ceiling ($45.00)
      - Action on breach: Terminate call + log + alert

   2. **Timeout Enforcement**
      - Per-call timeout (default 120s)
      - Circuit breaker: 5 consecutive timeouts — provider marked unhealthy
      - Fallback: Switch to secondary provider

   3. **Model Pinning**
      - Agent manifests specify tier (fast/balanced/powerful)
      - Runtime resolves to specific model version
      - No silent model upgrades — version changes require lifecycle review

3. **Layer 3: Output Guardrails (After LLM Response)** — What gets checked BEFORE using the response:

   1. **Hallucination Detection**
      - Cross-reference output against input data (does output cite entities that exist?)
      - Schema compliance check (does JSON output match expected schema?)
      - Confidence scoring (quality gate from AGENT-HANDOFF-PROTOCOL)
      - Action on detection: Retry with feedback (max 2 retries) — escalate to human

   2. **Toxicity/Bias Filtering**
      - Scan output for toxic, biased, or inappropriate content
      - Especially critical for client-facing documents (USER-STORIES, BRD, PRD)
      - Action on detection: Block + regenerate + log

   3. **PII Leakage Detection**
      - Scan output for PII that should not appear (e.g., real names in test data)
      - Verify output classification matches agent's allowed output classification
      - Action on detection: Redact + log + alert

   4. **Format Validation**
      - JSON schema validation for structured outputs
      - Markdown structure validation for document outputs
      - ID format validation (F-NNN, Q-NNN, US-DOMAIN-NNN match patterns)

4. **Layer 4: Governance Guardrails (Operational)** — What protects the platform at the system level:

   1. **Kill Switch**
      - Per-agent kill switch (disable specific agent immediately)
      - Per-provider kill switch (disable all calls to a provider)
      - Global kill switch (disable all LLM calls platform-wide)
      - Triggered by: cost spike, error rate spike, security incident

   2. **Human-in-the-Loop Gates**
      - T3 agents: Every action requires human approval
      - T2 agents: High-stakes actions require approval
      - T1 agents: Approval for promote/rollback
      - T0 agents: Fully autonomous (but still audited)

   3. **Audit Trail**
      - Every guardrail trigger logged with: timestamp, agent_id, layer, guardrail_type, action_taken, input_hash, output_hash
      - Immutable audit log (append-only)
      - Queryable for compliance evidence

   4. **Rate Limiting**
      - Per-agent: Max N invocations per minute
      - Per-provider: Max N API calls per minute
      - Per-project: Max $X per day

5. **Guardrail Decision Matrix** — Table: Guardrail | Trigger Condition | Action | Severity | Blocks Pipeline? | Human Notified?

6. **Testing Guardrails**:
   - Adversarial test suite: prompt injection attempts, PII injection, oversized inputs
   - Chaos testing: provider failure during generation, timeout during output validation
   - Red team protocol: quarterly adversarial testing by security team

### Quality Criteria
- Every agent must pass through ALL 4 layers — no bypass
- Kill switches must work within 5 seconds
- PII scanning must cover ALL data classifications from SECURITY-ARCH
- Hallucination detection must cross-reference against actual input data, not just pattern matching
- Guardrail triggers must be logged even if action is "allow" (for audit trail)

### Error Handling & Recovery Strategy
- **Guardrail false positive**: If a guardrail blocks legitimate content:
  1. Log the false positive with full context (input, output, guardrail triggered)
  2. Allow manual override with human approval (audit logged)
  3. Add the pattern to the allowlist after review
  4. Never disable the guardrail — tune it
- **Guardrail bypass detected**: If content passes guardrails but is later found harmful:
  1. Immediately add the pattern to the detection rules
  2. Retroactively scan recent outputs for similar patterns
  3. Notify affected downstream agents/users
  4. Post-incident: update adversarial test suite with the bypass vector
- **Kill switch activation**: If a kill switch is triggered:
  1. All in-flight requests to the affected scope are terminated
  2. Queued requests are rejected with a clear error message
  3. Alert sent to on-call and engineering leadership
  4. Kill switch remains active until manually deactivated after root cause analysis

### Anti-Patterns to Avoid
- Guardrails that only check outputs (input guardrails are cheaper and catch problems earlier)
- PII detection that only uses regex (must include named entity recognition for edge cases)
- Kill switches that require a deploy to activate (must be runtime-configurable)
- Guardrail testing only at launch (adversarial testing must be continuous)
- Bypassing guardrails for "trusted" agents (all agents go through all 4 layers)
- Logging only blocked content (must also log allowed content for audit trail)

### Constraints
- ESCALATE if: no PII detection capability, no kill switch mechanism, no adversarial test suite
