"""Live test of D20-guardrails-spec-writer — AI Safety Guardrails Specification."""

import asyncio
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from sdk.base_agent import BaseAgent
from pathlib import Path


async def main():
    agent = BaseAgent(agent_dir=Path("agents/design/D20-guardrails-spec-writer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps",
            "agent_count": 48,
            "agent_phases": [
                "GOVERN",
                "DESIGN",
                "BUILD",
                "TEST",
                "DEPLOY",
                "MONITOR",
                "OPTIMIZE",
            ],
            "autonomy_tiers": [
                {"tier": "T0", "description": "Fully autonomous — no human approval", "hitl_required": False},
                {"tier": "T1", "description": "Supervised — human reviews output post-hoc", "hitl_required": False},
                {"tier": "T2", "description": "Assisted — human approves before execution", "hitl_required": True},
                {"tier": "T3", "description": "Manual — human approves every action", "hitl_required": True},
            ],
            "data_classification": [
                {"level": "Public", "examples": ["marketing copy", "public docs"], "llm_policy": "any provider"},
                {"level": "Internal", "examples": ["sprint plans", "architecture docs"], "llm_policy": "any provider"},
                {"level": "Confidential", "examples": ["customer PII", "financial data"], "llm_policy": "ollama only"},
                {"level": "Restricted", "examples": ["encryption keys", "auth tokens"], "llm_policy": "ollama only"},
            ],
            "enforcement_rules": [
                "no-todo-in-code.yaml",
                "max-file-size.yaml",
                "required-tests.yaml",
                "api-version-header.yaml",
                "prompt-version-lock.yaml",
            ],
            "quality_gates": [
                "completeness >= 0.85",
                "accuracy >= 0.90",
                "faithfulness >= 0.85",
            ],
            "llm_providers": [
                "anthropic",
                "openai",
                "ollama",
            ],
        },
        project_id="fleetops-020",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == 4 Layers present ======================================================
    layers = [
        "Input Guardrails",
        "Processing Guardrails",
        "Output Guardrails",
        "Governance Guardrails",
    ]
    found_layers = []
    missing_layers = []
    for layer in layers:
        if layer.lower() in output.lower():
            found_layers.append(layer)
        else:
            missing_layers.append(layer)
    print(f"Layers: {len(found_layers)}/{len(layers)}")
    if missing_layers:
        print(f"  MISSING: {missing_layers}")
    else:
        print(f"  PASS: All 4 defense layers present")

    # == Guardrail IDs by pattern ==============================================
    ig_ids = sorted(set(re.findall(r"IG-\d{3}", output)))
    pg_ids = sorted(set(re.findall(r"PG-\d{3}", output)))
    og_ids = sorted(set(re.findall(r"OG-\d{3}", output)))
    gg_ids = sorted(set(re.findall(r"GG-\d{3}", output)))

    total_guardrails = len(ig_ids) + len(pg_ids) + len(og_ids) + len(gg_ids)
    print(f"Guardrail IDs found:")
    print(f"  IG-NNN (Input):      {len(ig_ids)} — {ig_ids}")
    print(f"  PG-NNN (Processing): {len(pg_ids)} — {pg_ids}")
    print(f"  OG-NNN (Output):     {len(og_ids)} — {og_ids}")
    print(f"  GG-NNN (Governance): {len(gg_ids)} — {gg_ids}")
    print(f"  Total unique guardrails: {total_guardrails}")
    print(f"  Minimum 17 guardrails: {'PASS' if total_guardrails >= 17 else 'FAIL — got ' + str(total_guardrails)}")

    # == Prompt injection detection ============================================
    has_prompt_injection = "prompt injection" in output.lower()
    has_injection_pattern = "pattern matching" in output.lower() or "pattern" in output.lower()
    has_semantic = "semantic" in output.lower()
    print(f"Prompt injection detection:")
    print(f"  Mentioned: {'PASS' if has_prompt_injection else 'FAIL'}")
    print(f"  Pattern-based: {'PASS' if has_injection_pattern else 'FAIL'}")
    print(f"  Semantic analysis: {'PASS' if has_semantic else 'FAIL'}")

    # == PII filtering =========================================================
    has_pii = "pii" in output.lower()
    has_redaction = "redact" in output.lower()
    has_ner = "ner" in output.lower() or "named entity" in output.lower() or "entity recognition" in output.lower()
    print(f"PII filtering:")
    print(f"  PII mentioned: {'PASS' if has_pii else 'FAIL'}")
    print(f"  Redaction: {'PASS' if has_redaction else 'FAIL'}")

    # == Hallucination detection ===============================================
    has_hallucination = "hallucination" in output.lower()
    has_faithfulness = "faithfulness" in output.lower()
    has_cross_ref = "cross-reference" in output.lower() or "cross reference" in output.lower() or "crossreference" in output.lower()
    print(f"Hallucination detection:")
    print(f"  Mentioned: {'PASS' if has_hallucination else 'FAIL'}")
    print(f"  Faithfulness scoring: {'PASS' if has_faithfulness else 'FAIL'}")
    print(f"  Cross-reference against input: {'PASS' if has_cross_ref else 'FAIL'}")

    # == Kill switch ===========================================================
    has_kill_switch = "kill switch" in output.lower() or "kill-switch" in output.lower()
    has_per_agent = "per-agent" in output.lower() or "per agent" in output.lower()
    has_per_provider = "per-provider" in output.lower() or "per provider" in output.lower()
    has_global = "global" in output.lower()
    has_5_seconds = "5 second" in output.lower() or "5s" in output.lower() or "five second" in output.lower()
    print(f"Kill switch:")
    print(f"  Mentioned: {'PASS' if has_kill_switch else 'FAIL'}")
    print(f"  Per-agent scope: {'PASS' if has_per_agent else 'FAIL'}")
    print(f"  Per-provider scope: {'PASS' if has_per_provider else 'FAIL'}")
    print(f"  Global scope: {'PASS' if has_global else 'FAIL'}")
    print(f"  5-second activation: {'PASS' if has_5_seconds else 'FAIL'}")

    # == HITL tiers (T0-T3) ====================================================
    tiers_found = []
    tiers_missing = []
    for tier in ["T0", "T1", "T2", "T3"]:
        if tier in output:
            tiers_found.append(tier)
        else:
            tiers_missing.append(tier)
    print(f"HITL autonomy tiers:")
    print(f"  Found: {len(tiers_found)}/4 — {tiers_found}")
    if tiers_missing:
        print(f"  MISSING: {tiers_missing}")
    else:
        print(f"  PASS: All T0-T3 tiers present")

    # == Audit trail ===========================================================
    has_audit = "audit trail" in output.lower() or "audit log" in output.lower()
    has_timestamp = "timestamp" in output.lower()
    has_agent_id = "agent_id" in output.lower() or "agent id" in output.lower()
    has_input_hash = "input_hash" in output.lower() or "hash" in output.lower()
    print(f"Audit trail:")
    print(f"  Mentioned: {'PASS' if has_audit else 'FAIL'}")
    print(f"  Timestamp field: {'PASS' if has_timestamp else 'FAIL'}")
    print(f"  Agent ID field: {'PASS' if has_agent_id else 'FAIL'}")
    print(f"  Hash (input/output): {'PASS' if has_input_hash else 'FAIL'}")

    # == Rate limiting =========================================================
    has_rate_limit = "rate limit" in output.lower() or "rate-limit" in output.lower()
    print(f"Rate limiting: {'PASS' if has_rate_limit else 'FAIL'}")

    # == Decision matrix table =================================================
    has_decision_matrix = "decision matrix" in output.lower()
    # Count table rows that contain guardrail IDs
    matrix_rows = 0
    for line in output.split("\n"):
        if "|" in line and re.search(r"[IPOG]G-\d{3}", line):
            matrix_rows += 1
    print(f"Decision matrix:")
    print(f"  Section present: {'PASS' if has_decision_matrix else 'FAIL'}")
    print(f"  Table rows with guardrail IDs: {matrix_rows}")
    print(f"  Minimum 17 rows: {'PASS' if matrix_rows >= 17 else 'FAIL — got ' + str(matrix_rows)}")

    # == Adversarial testing ===================================================
    has_adversarial = "adversarial" in output.lower()
    has_chaos = "chaos" in output.lower()
    has_red_team = "red team" in output.lower()
    print(f"Testing guardrails:")
    print(f"  Adversarial tests: {'PASS' if has_adversarial else 'FAIL'}")
    print(f"  Chaos testing: {'PASS' if has_chaos else 'FAIL'}")
    print(f"  Red team protocol: {'PASS' if has_red_team else 'FAIL'}")

    # == Ollama for sensitive data =============================================
    has_ollama = "ollama" in output.lower()
    has_ollama_only = "ollama only" in output.lower()
    has_confidential = "confidential" in output.lower()
    has_restricted = "restricted" in output.lower()
    print(f"Ollama for sensitive data:")
    print(f"  Ollama mentioned: {'PASS' if has_ollama else 'FAIL'}")
    print(f"  'Ollama only' policy: {'PASS' if has_ollama_only else 'FAIL'}")
    print(f"  Confidential classification: {'PASS' if has_confidential else 'FAIL'}")
    print(f"  Restricted classification: {'PASS' if has_restricted else 'FAIL'}")

    # == Budget enforcement ($45 ceiling) ======================================
    has_budget = "budget" in output.lower()
    has_45 = "$45" in output or "45.00" in output or "$45.00" in output
    has_050 = "$0.50" in output or "0.50" in output
    print(f"Budget enforcement:")
    print(f"  Budget mentioned: {'PASS' if has_budget else 'FAIL'}")
    print(f"  $45 pipeline ceiling: {'PASS' if has_45 else 'FAIL'}")
    print(f"  $0.50 per-agent cap: {'PASS' if has_050 else 'FAIL'}")

    # == LLM providers referenced ==============================================
    providers_found = []
    for provider in ["anthropic", "openai", "ollama"]:
        if provider.lower() in output.lower():
            providers_found.append(provider)
    print(f"LLM providers referenced: {len(providers_found)}/3 — {providers_found}")
    print(f"  All providers: {'PASS' if len(providers_found) == 3 else 'FAIL'}")

    # == Markdown tables present ===============================================
    table_rows = len(re.findall(r"^\|.*\|$", output, re.MULTILINE))
    print(f"Markdown table rows: {table_rows}")
    print(f"  Tables present (10+ rows): {'PASS' if table_rows >= 10 else 'FAIL'}")

    # == Toxicity filtering ====================================================
    has_toxicity = "toxicity" in output.lower() or "toxic" in output.lower()
    has_bias = "bias" in output.lower()
    print(f"Toxicity/bias filtering:")
    print(f"  Toxicity mentioned: {'PASS' if has_toxicity else 'FAIL'}")
    print(f"  Bias mentioned: {'PASS' if has_bias else 'FAIL'}")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
