"""Live test of D19-fault-tolerance-planner — Fault Tolerance Plan (v2 new)."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D19-fault-tolerance-planner"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps",
            "components": [
                {"name": "MCP Server", "technology": "Python 3.12 + FastMCP", "port": 8811},
                {"name": "REST API", "technology": "Python 3.12 + FastAPI", "port": 8000},
                {"name": "Dashboard", "technology": "Python 3.12 + Streamlit", "port": 8501},
                {"name": "PostgreSQL", "technology": "PostgreSQL 16", "port": 5432},
                {"name": "Agent Runtime", "technology": "Python 3.12 + SDK"},
                {"name": "Samsara Integration", "technology": "Python 3.12 + httpx"},
            ],
            "data_tables": [
                "vehicles",
                "maintenance_orders",
                "drivers",
                "telemetry_events",
                "audit_logs",
                "agent_invocations",
            ],
            "api_endpoints": [
                "GET /api/v1/vehicles",
                "POST /api/v1/maintenance-orders",
                "GET /api/v1/analytics/fleet",
                "PUT /api/v1/vehicles/{id}",
                "GET /api/v1/drivers",
            ],
            "quality_nfrs": [
                "99.9% uptime SLA",
                "API p95 latency < 500ms",
                "Database failover RTO < 60s",
                "Zero data loss (RPO = 0)",
            ],
            "security_concerns": [
                "JWT token lifecycle (issue, refresh, revoke)",
                "Role-based access control (admin, operator, viewer)",
                "Cross-interface session consistency",
            ],
            "infra_details": {
                "cloud_provider": "AWS",
                "container_orchestrator": "ECS Fargate",
                "database": "RDS PostgreSQL 16 Multi-AZ",
                "monitoring": "CloudWatch + Prometheus + Grafana",
                "ci_cd": "GitHub Actions",
            },
            "llm_providers": [
                "anthropic",
                "openai",
                "ollama",
            ],
        },
        project_id="fleetops-019",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == 5 Layers present ======================================================
    layers = [
        "Application",
        "Functional",
        "Database",
        "Session",
        "Cross-Cutting",
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
        print(f"  PASS: All 5 failure layers present")

    # == Scenario IDs by pattern ===============================================
    app_ids = re.findall(r"APP-\d{3}", output)
    func_ids = re.findall(r"FUNC-\d{3}", output)
    db_ids = re.findall(r"DB-\d{3}", output)
    sess_ids = re.findall(r"SESS-\d{3}", output)
    cross_ids = re.findall(r"CROSS-\d{3}", output)

    unique_app = sorted(set(app_ids))
    unique_func = sorted(set(func_ids))
    unique_db = sorted(set(db_ids))
    unique_sess = sorted(set(sess_ids))
    unique_cross = sorted(set(cross_ids))

    total_unique = len(unique_app) + len(unique_func) + len(unique_db) + len(unique_sess) + len(unique_cross)
    print(f"Scenario IDs found:")
    print(f"  APP-NNN:   {len(unique_app)} unique — {unique_app}")
    print(f"  FUNC-NNN:  {len(unique_func)} unique — {unique_func}")
    print(f"  DB-NNN:    {len(unique_db)} unique — {unique_db}")
    print(f"  SESS-NNN:  {len(unique_sess)} unique — {unique_sess}")
    print(f"  CROSS-NNN: {len(unique_cross)} unique — {unique_cross}")
    print(f"  Total unique scenarios: {total_unique}")
    print(f"  Minimum 15 scenarios: {'PASS' if total_unique >= 15 else 'FAIL'}")

    # == Priority levels present ===============================================
    priorities = ["P0", "P1", "P2", "P3"]
    pri_found = [p for p in priorities if p in output]
    pri_missing = [p for p in priorities if p not in output]
    print(f"Priorities: {len(pri_found)}/{len(priorities)}")
    if pri_missing:
        print(f"  MISSING: {pri_missing}")
    else:
        print(f"  PASS: All P0-P3 priorities present")

    # == Detection specificity (metric + threshold) ============================
    detection_terms = ["metric", "threshold"]
    det_found = [t for t in detection_terms if t.lower() in output.lower()]
    det_missing = [t for t in detection_terms if t.lower() not in output.lower()]
    # Also check for actual metric patterns (metric_name > number)
    metric_patterns = re.findall(r"[a-z_]+\s*[><=]+\s*\d+", output.lower())
    print(f"Detection specificity:")
    print(f"  Terms ({detection_terms}): {len(det_found)}/{len(detection_terms)} — {'PASS' if not det_missing else 'MISSING: ' + str(det_missing)}")
    print(f"  Metric threshold patterns found: {len(metric_patterns)}")
    print(f"  Detection specificity: {'PASS' if len(metric_patterns) >= 5 else 'FAIL — expected 5+ metric>threshold patterns'}")

    # == Handling specificity (retry, backoff, timeout, circuit) ===============
    handling_terms = ["retry", "backoff", "timeout", "circuit"]
    hdl_found = [t for t in handling_terms if t.lower() in output.lower()]
    hdl_missing = [t for t in handling_terms if t.lower() not in output.lower()]
    print(f"Handling terms: {len(hdl_found)}/{len(handling_terms)}")
    if hdl_missing:
        print(f"  MISSING: {hdl_missing}")
    else:
        print(f"  PASS: All handling terms (retry, backoff, timeout, circuit) present")

    # == RTO values present ====================================================
    rto_matches = re.findall(r"RTO\s*[:\s]*\d+\s*(?:s|sec|second|min|minute|ms)", output, re.IGNORECASE)
    rto_any = re.findall(r"RTO", output, re.IGNORECASE)
    print(f"RTO references: {len(rto_any)} total, {len(rto_matches)} with numeric values")
    print(f"  RTO numeric values: {'PASS' if len(rto_matches) >= 3 else 'FAIL — expected 3+ RTO with numeric values'}")

    # == On-call procedures ====================================================
    has_oncall = "on-call" in output.lower() or "on call" in output.lower() or "oncall" in output.lower()
    has_pagerduty = "pagerduty" in output.lower() or "pager" in output.lower() or "alert" in output.lower()
    has_escalation = "escalat" in output.lower()
    has_triage = "triage" in output.lower()
    has_post_incident = "post-incident" in output.lower() or "post incident" in output.lower() or "postmortem" in output.lower()
    print(f"On-call procedures:")
    print(f"  On-call section: {'PASS' if has_oncall else 'FAIL'}")
    print(f"  Alert/pager: {'PASS' if has_pagerduty else 'FAIL'}")
    print(f"  Escalation: {'PASS' if has_escalation else 'FAIL'}")
    print(f"  Triage: {'PASS' if has_triage else 'FAIL'}")
    print(f"  Post-incident review: {'PASS' if has_post_incident else 'FAIL'}")

    # == LLM provider failover =================================================
    has_failover = "failover" in output.lower()
    llm_providers_found = []
    for provider in ["anthropic", "openai", "ollama"]:
        if provider.lower() in output.lower():
            llm_providers_found.append(provider)
    has_circuit_breaker = "circuit breaker" in output.lower() or "circuit-breaker" in output.lower()
    print(f"LLM provider failover:")
    print(f"  Failover mentioned: {'PASS' if has_failover else 'FAIL'}")
    print(f"  Providers referenced: {len(llm_providers_found)}/3 — {llm_providers_found}")
    print(f"  Circuit breaker: {'PASS' if has_circuit_breaker else 'FAIL'}")

    # == Nightly reconciliation ================================================
    has_reconciliation = "reconciliation" in output.lower()
    has_nightly = "nightly" in output.lower() or "02:00" in output or "daily" in output.lower()
    print(f"Nightly reconciliation:")
    print(f"  Reconciliation section: {'PASS' if has_reconciliation else 'FAIL'}")
    print(f"  Nightly/daily schedule: {'PASS' if has_nightly else 'FAIL'}")

    # == Summary statistics table ==============================================
    has_summary = "summary" in output.lower()
    has_total = "total" in output.lower()
    summary_table_rows = 0
    in_summary = False
    for line in output.split("\n"):
        if "summary" in line.lower() and ("statistic" in line.lower() or "#" in line):
            in_summary = True
        if in_summary and line.strip().startswith("|"):
            summary_table_rows += 1
        if in_summary and line.strip() == "" and summary_table_rows > 0:
            break
    print(f"Summary statistics:")
    print(f"  Summary section: {'PASS' if has_summary else 'FAIL'}")
    print(f"  Total row: {'PASS' if has_total else 'FAIL'}")
    print(f"  Table rows in summary area: {summary_table_rows}")

    # == Components referenced =================================================
    components = ["mcp server", "rest api", "dashboard", "postgresql", "agent runtime", "samsara"]
    comp_found = [c for c in components if c.lower() in output.lower()]
    comp_missing = [c for c in components if c.lower() not in output.lower()]
    print(f"Components referenced: {len(comp_found)}/{len(components)}")
    if comp_missing:
        print(f"  MISSING: {comp_missing}")
    else:
        print(f"  PASS: All 6 components referenced")

    # == Tables present ========================================================
    table_rows = len(re.findall(r"^\|.*\|$", output, re.MULTILINE))
    print(f"Markdown table rows: {table_rows}")
    print(f"  Tables present (10+ rows): {'PASS' if table_rows >= 10 else 'FAIL'}")

    # == Audit trail mentions ==================================================
    has_audit = "audit" in output.lower()
    print(f"Audit trail: {'PASS' if has_audit else 'FAIL'}")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
