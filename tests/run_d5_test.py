"""Live test of D5-quality-spec-generator."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D5-quality-spec-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "success_metrics": [
                {"id": "SM-01", "name": "Fleet dashboard load time", "target": "< 2 seconds", "verification": "Synthetic monitoring P95"},
                {"id": "SM-02", "name": "Route reassignment time", "target": "< 30 seconds", "verification": "End-to-end timing"},
                {"id": "SM-03", "name": "HOS compliance alert latency", "target": "< 5 minutes", "verification": "Alert timestamp vs violation timestamp"},
                {"id": "SM-04", "name": "Cost-per-delivery calculation", "target": "< 1 hour post-delivery", "verification": "Cost record timestamp"},
                {"id": "SM-05", "name": "GPS update frequency", "target": "Every 30 seconds", "verification": "GPS event timestamps"},
                {"id": "SM-06", "name": "System uptime", "target": "99.5%", "verification": "Health check monitoring"},
            ],
            "components": [
                {"name": "MCP Fleet Server", "technology": "Python MCP SDK"},
                {"name": "REST API", "technology": "aiohttp"},
                {"name": "Dashboard", "technology": "Streamlit"},
                {"name": "Fleet Service", "technology": "Python async"},
                {"name": "Compliance Service", "technology": "Python async"},
                {"name": "Cost Service", "technology": "Python async"},
                {"name": "PostgreSQL", "technology": "PostgreSQL 15"},
            ],
            "feature_summary": {
                "total_features": 55,
                "total_story_points": 347,
                "epics": [
                    {"id": "E-001", "name": "Fleet Monitoring Core", "story_points": 40, "ai_feature_count": 2},
                    {"id": "E-002", "name": "Route Management", "story_points": 42, "ai_feature_count": 1},
                    {"id": "E-003", "name": "HOS Compliance", "story_points": 38, "ai_feature_count": 1},
                    {"id": "E-004", "name": "Cost Analytics", "story_points": 35, "ai_feature_count": 1},
                    {"id": "E-005", "name": "Exception Handling", "story_points": 34, "ai_feature_count": 2},
                    {"id": "E-006", "name": "Driver Management", "story_points": 28, "ai_feature_count": 0},
                    {"id": "E-007", "name": "Reporting & Audit", "story_points": 42, "ai_feature_count": 1},
                    {"id": "E-008", "name": "Integration Layer", "story_points": 38, "ai_feature_count": 0},
                    {"id": "E-009", "name": "MCP Interface", "story_points": 30, "ai_feature_count": 2},
                    {"id": "E-010", "name": "Notifications", "story_points": 20, "ai_feature_count": 0},
                ],
                "ai_features_count": 10,
            },
            "interfaces": ["mcp", "rest", "dashboard"],
            "regulatory": ["DOT_HOS", "SOC2", "GDPR"],
        },
        project_id="fleetops-001",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # Count Q-NNN IDs
    q_ids = set(re.findall(r"Q-\d+", output))
    print(f"NFR count: {len(q_ids)} unique Q-NNN IDs (target: 50+)")

    # Section checks
    sections = ["Performance", "Reliability", "Security", "Accessibility", "Coverage",
                "Observability", "Parity", "Data", "Cost", "Per-Module", "SLI", "Rubric",
                "Compliance", "Summary"]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")

    # Key v2 checks
    has_per_module = "per-module" in output.lower() or "per module" in output.lower()
    has_sli_slo = "SLI" in output and "SLO" in output
    has_rubric = "rubric" in output.lower()
    has_epic_refs = bool(re.findall(r"E-\d+", output))
    has_ai_coverage = "95%" in output or "ai" in output.lower() and "coverage" in output.lower()

    print(f"Per-module thresholds: {has_per_module}")
    print(f"SLI/SLO: {has_sli_slo}")
    print(f"Quality rubric: {has_rubric}")
    print(f"Epic references: {has_epic_refs}")
    print(f"AI-aware coverage (95%): {has_ai_coverage}")

    # Interface coverage
    has_mcp_nfr = "MCP" in output and ("Q-" in output)
    has_rest_nfr = "REST" in output and ("Q-" in output)
    has_dashboard_nfr = "Dashboard" in output.lower() or "dashboard" in output.lower()
    print(f"MCP NFRs: {has_mcp_nfr}")
    print(f"REST NFRs: {has_rest_nfr}")
    print(f"Dashboard NFRs: {has_dashboard_nfr}")

    print()
    print("=== FIRST 2000 CHARS ===")
    print(output[:2000])


if __name__ == "__main__":
    asyncio.run(main())
