"""Live test of D16-infra-designer — Infrastructure Design."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D16-infra-designer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps",
            "components": [
                {"name": "MCP Server", "technology": "Python 3.12 + FastMCP", "port": 8001},
                {"name": "REST API", "technology": "Python 3.12 + FastAPI", "port": 8000},
                {"name": "Dashboard", "technology": "Python 3.12 + Streamlit", "port": 8501},
                {"name": "PostgreSQL", "technology": "PostgreSQL 16", "port": 5432},
                {"name": "Agent Runtime", "technology": "Python 3.12 + SDK", "port": 8002},
                {"name": "Samsara Integration", "technology": "Python 3.12 + httpx", "port": 8003},
            ],
            "quality_nfrs": [
                "API latency p95 < 200ms",
                "System uptime 99.9%",
                "Dashboard load time < 2s",
                "Agent response time p95 < 30s",
                "Database query time p95 < 50ms",
            ],
            "security_requirements": [
                "TLS 1.3 on all endpoints",
                "Network isolation between tiers",
                "Secrets stored in Vault/KMS — no plaintext env vars",
            ],
            "feature_summary": {
                "total_features": 55,
                "ai_features_count": 10,
                "total_story_points": 440,
            },
            "constraints": {
                "annual_budget_usd": 350000,
                "timeline_months": 12,
                "team_size": 8,
            },
        },
        project_id="fleetops-016",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == All 11 sections present ===============================================
    sections = [
        "Environment Strategy",
        "Network Architecture",
        "Compute",
        "CI/CD Pipeline",
        "Database Deployment",
        "Infrastructure as Code",
        "Cost Estimate",
        "Observability",
        "Disaster Recovery",
        "Capacity Planning",
        "Rollback Procedure",
    ]
    found_sections = []
    missing_sections = []
    for s in sections:
        if s.lower() in output.lower():
            found_sections.append(s)
        else:
            missing_sections.append(s)
    print(f"Sections: {len(found_sections)}/{len(sections)}")
    if missing_sections:
        print(f"  MISSING: {missing_sections}")
    else:
        print(f"  PASS: All 11 sections present")

    # == 4 environments found ==================================================
    environments = ["local", "dev", "staging", "production"]
    env_found = [e for e in environments if e.lower() in output.lower()]
    env_missing = [e for e in environments if e.lower() not in output.lower()]
    print(f"Environments: {len(env_found)}/{len(environments)}")
    if env_missing:
        print(f"  MISSING: {env_missing}")
    else:
        print(f"  PASS: All 4 environments found")

    # == CI/CD stages numbered =================================================
    cicd_stages_found = set()
    for i in range(1, 10):
        # Look for numbered stages like "| 1 |", "Stage 1", "1.", "1)"
        patterns = [
            rf"\|\s*{i}\s*\|",
            rf"Stage\s+{i}",
            rf"^\s*{i}\.\s+",
        ]
        for pattern in patterns:
            if re.search(pattern, output, re.MULTILINE):
                cicd_stages_found.add(i)
                break
    print(f"CI/CD numbered stages: {len(cicd_stages_found)}/9")
    if len(cicd_stages_found) >= 7:
        print(f"  PASS: At least 7 numbered CI/CD stages found")
    else:
        print(f"  WARNING: Expected 9 numbered stages, found {sorted(cicd_stages_found)}")

    # == Compute sizing table ==================================================
    compute_keywords = ["cpu", "memory", "replica", "scaling"]
    ck_found = [k for k in compute_keywords if k.lower() in output.lower()]
    has_compute_table = len(re.findall(r"^\|.*\|$", output, re.MULTILINE)) >= 4
    print(f"Compute sizing keywords: {len(ck_found)}/{len(compute_keywords)} ({ck_found})")
    print(f"  Tables present (4+ rows): {'PASS' if has_compute_table else 'FAIL'}")

    # == Cost estimates with LLM mentions ======================================
    has_cost_section = "cost" in output.lower()
    has_llm_cost = (
        "llm" in output.lower()
        and ("cost" in output.lower() or "pricing" in output.lower() or "budget" in output.lower())
    )
    has_per_provider = "provider" in output.lower() and ("token" in output.lower() or "pricing" in output.lower())
    print(f"Cost estimates section: {'PASS' if has_cost_section else 'FAIL'}")
    print(f"  LLM cost mentioned: {'PASS' if has_llm_cost else 'FAIL'}")
    print(f"  Per-provider pricing: {'PASS' if has_per_provider else 'FAIL'}")

    # == Observability terms ===================================================
    obs_terms = ["opentelemetry", "structlog", "metrics"]
    obs_found = [t for t in obs_terms if t.lower() in output.lower()]
    obs_missing = [t for t in obs_terms if t.lower() not in output.lower()]
    print(f"Observability terms: {len(obs_found)}/{len(obs_terms)}")
    if obs_missing:
        print(f"  MISSING: {obs_missing}")
    else:
        print(f"  PASS: All observability terms found (OpenTelemetry, structlog, metrics)")

    # AI-specific telemetry
    ai_telemetry_terms = ["token usage", "quality score", "agent"]
    ai_found = [t for t in ai_telemetry_terms if t.lower() in output.lower()]
    print(f"  AI-specific telemetry terms: {len(ai_found)}/{len(ai_telemetry_terms)} ({ai_found})")

    # == DR terms ==============================================================
    dr_terms = ["rpo", "rto", "backup"]
    dr_found = [t for t in dr_terms if t.lower() in output.lower()]
    dr_missing = [t for t in dr_terms if t.lower() not in output.lower()]
    print(f"DR terms: {len(dr_found)}/{len(dr_terms)}")
    if dr_missing:
        print(f"  MISSING: {dr_missing}")
    else:
        print(f"  PASS: All DR terms found (RPO, RTO, backup)")

    # DR test schedule
    has_dr_test = (
        "quarterly" in output.lower()
        or "dr test" in output.lower()
        or "disaster recovery test" in output.lower()
        or "failover drill" in output.lower()
    )
    print(f"  DR test schedule: {'PASS' if has_dr_test else 'FAIL'}")

    # == Capacity terms ========================================================
    cap_terms = ["growth", "scaling"]
    cap_found = [t for t in cap_terms if t.lower() in output.lower()]
    cap_missing = [t for t in cap_terms if t.lower() not in output.lower()]
    print(f"Capacity terms: {len(cap_found)}/{len(cap_terms)}")
    if cap_missing:
        print(f"  MISSING: {cap_missing}")
    else:
        print(f"  PASS: All capacity terms found (growth, scaling)")

    # LLM token forecasting
    has_token_forecast = "token" in output.lower() and (
        "forecast" in output.lower()
        or "budget" in output.lower()
        or "projection" in output.lower()
    )
    print(f"  LLM token forecasting: {'PASS' if has_token_forecast else 'FAIL'}")

    # == Rollback procedures ===================================================
    has_rollback = "rollback" in output.lower()
    rollback_terms = ["trigger", "duration", "step"]
    rb_found = [t for t in rollback_terms if t.lower() in output.lower()]
    print(f"Rollback procedures: {'PASS' if has_rollback else 'FAIL'}")
    print(f"  Rollback detail terms: {len(rb_found)}/{len(rollback_terms)} ({rb_found})")

    # == All 6 components referenced ===========================================
    component_names = ["mcp server", "rest api", "dashboard", "postgresql", "agent runtime", "samsara"]
    comp_found = [c for c in component_names if c.lower() in output.lower()]
    comp_missing = [c for c in component_names if c.lower() not in output.lower()]
    print(f"Components referenced: {len(comp_found)}/{len(component_names)}")
    if comp_missing:
        print(f"  MISSING: {comp_missing}")
    else:
        print(f"  PASS: All 6 components referenced")

    # == Security requirements referenced ======================================
    sec_terms = ["tls", "network isolation", "vault", "kms", "secret"]
    sec_found = [t for t in sec_terms if t.lower() in output.lower()]
    sec_missing = [t for t in sec_terms if t.lower() not in output.lower()]
    print(f"Security requirements: {len(sec_found)}/{len(sec_terms)}")
    if sec_missing:
        print(f"  MISSING: {sec_missing}")
    else:
        print(f"  PASS: All security requirements referenced")

    # == Module-aware sizing (AI vs CRUD) ======================================
    has_module_aware = (
        ("ai" in output.lower() or "agent" in output.lower())
        and ("higher memory" in output.lower() or "2gi" in output.lower() or "4gi" in output.lower()
             or "module-aware" in output.lower() or "ai container" in output.lower()
             or "agent runtime" in output.lower())
    )
    print(f"Module-aware sizing (AI vs CRUD): {'PASS' if has_module_aware else 'FAIL'}")

    # == IaC structure =========================================================
    has_iac = "terraform" in output.lower() or "pulumi" in output.lower() or "infrastructure as code" in output.lower()
    has_drift = "drift" in output.lower()
    has_state = "state" in output.lower()
    print(f"IaC section: {'PASS' if has_iac else 'FAIL'}")
    print(f"  Drift detection: {'PASS' if has_drift else 'FAIL'}")
    print(f"  State management: {'PASS' if has_state else 'FAIL'}")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
