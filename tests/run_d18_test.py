"""Live test of D18-test-strategy-generator — Test Strategy (v2 upgraded)."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D18-test-strategy-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps",
            "components": [
                {"name": "MCP Server", "technology": "Python 3.12 + FastMCP"},
                {"name": "REST API", "technology": "Python 3.12 + FastAPI"},
                {"name": "Dashboard", "technology": "Python 3.12 + Streamlit"},
                {"name": "PostgreSQL", "technology": "PostgreSQL 16"},
                {"name": "Agent Runtime", "technology": "Python 3.12 + SDK"},
                {"name": "Samsara Integration", "technology": "Python 3.12 + httpx"},
            ],
            "quality_thresholds": {
                "ai_safety": 95,
                "core_business": 90,
                "shared_services": 85,
                "mcp_handlers": 80,
                "rest_handlers": 80,
                "dashboard": 70,
            },
            "mcp_tools": [
                "list_vehicles",
                "get_vehicle_status",
                "create_maintenance_order",
                "approve_maintenance",
                "get_fleet_analytics",
            ],
            "dashboard_screens": [
                "Fleet Overview",
                "Vehicle Detail",
                "Maintenance Queue",
                "Analytics Dashboard",
            ],
            "interaction_ids": [
                "I-001",
                "I-002",
                "I-003",
                "I-004",
                "I-005",
                "I-006",
            ],
            "data_tables": [
                "vehicles",
                "maintenance_orders",
                "drivers",
                "telemetry_events",
                "audit_logs",
                "agent_invocations",
            ],
            "security_test_requirements": [
                "JWT validation on all endpoints",
                "Role-based access control enforcement",
                "SQL injection prevention verified",
            ],
        },
        project_id="fleetops-018",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == All 15 sections present (some may merge, so check key terms) ===========
    sections = [
        "Test Pyramid",
        "Test Framework",
        "Database",
        "Directory Structure",
        "Shared Service",
        "MCP Tool",
        "REST API",
        "Dashboard",
        "Cross-Interface",
        "LLM Evaluation",
        "Production Readiness",
        "Agent Test",
        "Performance",
        "Coverage Threshold",
        "CI Pipeline",
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
        print(f"  PASS: All 15 section keywords present")

    # == Test pyramid present ===================================================
    pyramid_terms = ["schema", "service", "interface", "cross-interface"]
    pyr_found = [t for t in pyramid_terms if t.lower() in output.lower()]
    pyr_missing = [t for t in pyramid_terms if t.lower() not in output.lower()]
    print(f"Test Pyramid layers: {len(pyr_found)}/{len(pyramid_terms)}")
    if pyr_missing:
        print(f"  MISSING: {pyr_missing}")
    else:
        print(f"  PASS: All 4 pyramid layers found")

    # == Framework table present ================================================
    framework_terms = ["pytest", "testcontainers", "httpx", "k6", "locust"]
    fw_found = [t for t in framework_terms if t.lower() in output.lower()]
    fw_missing = [t for t in framework_terms if t.lower() not in output.lower()]
    print(f"Framework terms: {len(fw_found)}/{len(framework_terms)}")
    if fw_missing:
        print(f"  MISSING: {fw_missing}")
    else:
        print(f"  PASS: All framework terms found")

    # == Testcontainers mentioned ===============================================
    has_testcontainers = "testcontainers" in output.lower()
    has_postgres = "postgres" in output.lower()
    has_rollback = "rollback" in output.lower()
    print(f"Testcontainers DB strategy: {'PASS' if has_testcontainers else 'FAIL'}")
    print(f"  PostgreSQL mentioned: {'PASS' if has_postgres else 'FAIL'}")
    print(f"  Transaction rollback: {'PASS' if has_rollback else 'FAIL'}")

    # == Parity tests present ===================================================
    has_parity = "parity" in output.lower()
    interaction_ids_found = []
    for iid in ["I-001", "I-002", "I-003", "I-004", "I-005", "I-006"]:
        if iid in output:
            interaction_ids_found.append(iid)
    print(f"Parity tests: {'PASS' if has_parity else 'FAIL'}")
    print(f"  Interaction IDs referenced: {len(interaction_ids_found)}/6 ({interaction_ids_found})")

    # == LLM Evaluation section (v2 NEW) ========================================
    llm_eval_terms = ["golden", "quality scor", "prompt regression", "adversarial", "faithfulness"]
    le_found = [t for t in llm_eval_terms if t.lower() in output.lower()]
    le_missing = [t for t in llm_eval_terms if t.lower() not in output.lower()]
    print(f"LLM Evaluation (v2): {len(le_found)}/{len(llm_eval_terms)}")
    if le_missing:
        print(f"  MISSING: {le_missing}")
    else:
        print(f"  PASS: All LLM eval terms found")

    # == Go-live checklist (v2 NEW) =============================================
    has_go_live = "go-live" in output.lower() or "go live" in output.lower()
    has_checklist = "checklist" in output.lower() or "gate" in output.lower()
    has_g3 = "g3" in output.lower()
    print(f"Go-live checklist (v2): {'PASS' if has_go_live else 'FAIL'}")
    print(f"  Checklist/gate table: {'PASS' if has_checklist else 'FAIL'}")
    print(f"  G3 enforcement mentioned: {'PASS' if has_g3 else 'FAIL'}")

    # == Coverage thresholds per-module =========================================
    threshold_terms = ["95", "90", "85", "80", "70"]
    th_found = [t for t in threshold_terms if t in output]
    print(f"Coverage threshold values: {len(th_found)}/{len(threshold_terms)} ({th_found})")
    has_per_module = "per-module" in output.lower() or "per module" in output.lower() or (
        "ai_safety" in output.lower() or "ai safety" in output.lower()
    )
    print(f"  Per-module thresholds: {'PASS' if has_per_module else 'FAIL'}")

    # == CI Pipeline stages =====================================================
    has_ci_pipeline = "ci" in output.lower() and "pipeline" in output.lower()
    has_parallel = "parallel" in output.lower()
    stage_count = len(re.findall(r"stage\s*\d", output, re.IGNORECASE))
    print(f"CI Pipeline: {'PASS' if has_ci_pipeline else 'FAIL'}")
    print(f"  Parallel execution mentioned: {'PASS' if has_parallel else 'FAIL'}")
    print(f"  Stage references found: {stage_count}")

    # == Directory structure ====================================================
    dir_terms = ["tests/schemas", "tests/services", "tests/mcp", "tests/api",
                 "tests/dashboard", "tests/integration", "tests/agents", "tests/performance"]
    dir_found = [d for d in dir_terms if d.lower() in output.lower()]
    dir_missing = [d for d in dir_terms if d.lower() not in output.lower()]
    print(f"Test directories: {len(dir_found)}/{len(dir_terms)}")
    if dir_missing:
        print(f"  MISSING: {dir_missing}")
    else:
        print(f"  PASS: All 8 test directories found")

    # == MCP tools referenced ===================================================
    mcp_tools = ["list_vehicles", "get_vehicle_status", "create_maintenance_order",
                 "approve_maintenance", "get_fleet_analytics"]
    mcp_found = [t for t in mcp_tools if t.lower() in output.lower()]
    mcp_missing = [t for t in mcp_tools if t.lower() not in output.lower()]
    print(f"MCP tools referenced: {len(mcp_found)}/{len(mcp_tools)}")
    if mcp_missing:
        print(f"  MISSING: {mcp_missing}")
    else:
        print(f"  PASS: All 5 MCP tools referenced")

    # == Dashboard screens referenced ===========================================
    screens = ["fleet overview", "vehicle detail", "maintenance queue", "analytics dashboard"]
    scr_found = [s for s in screens if s.lower() in output.lower()]
    scr_missing = [s for s in screens if s.lower() not in output.lower()]
    print(f"Dashboard screens referenced: {len(scr_found)}/{len(screens)}")
    if scr_missing:
        print(f"  MISSING: {scr_missing}")
    else:
        print(f"  PASS: All 4 dashboard screens referenced")

    # == Data tables referenced =================================================
    tables = ["vehicles", "maintenance_orders", "drivers", "telemetry_events",
              "audit_logs", "agent_invocations"]
    tbl_found = [t for t in tables if t.lower() in output.lower()]
    tbl_missing = [t for t in tables if t.lower() not in output.lower()]
    print(f"Data tables referenced: {len(tbl_found)}/{len(tables)}")
    if tbl_missing:
        print(f"  MISSING: {tbl_missing}")
    else:
        print(f"  PASS: All 6 data tables referenced")

    # == Security test terms ====================================================
    sec_terms = ["jwt", "role-based", "sql injection"]
    sec_found = [t for t in sec_terms if t.lower() in output.lower()]
    sec_missing = [t for t in sec_terms if t.lower() not in output.lower()]
    print(f"Security test terms: {len(sec_found)}/{len(sec_terms)}")
    if sec_missing:
        print(f"  MISSING: {sec_missing}")
    else:
        print(f"  PASS: All security test requirements referenced")

    # == Error handling section =================================================
    error_terms = ["retry", "quarantine", "divergence", "flaky"]
    err_found = [t for t in error_terms if t.lower() in output.lower()]
    err_missing = [t for t in error_terms if t.lower() not in output.lower()]
    print(f"Error handling terms: {len(err_found)}/{len(error_terms)}")
    if err_missing:
        print(f"  MISSING: {err_missing}")
    else:
        print(f"  PASS: All error handling terms found")

    # == Tables present =========================================================
    table_rows = len(re.findall(r"^\|.*\|$", output, re.MULTILINE))
    print(f"Markdown table rows: {table_rows}")
    print(f"  Tables present (10+ rows): {'PASS' if table_rows >= 10 else 'FAIL'}")

    # == Code examples present ==================================================
    code_blocks = len(re.findall(r"```", output))
    print(f"Code fence markers: {code_blocks} ({'PASS' if code_blocks >= 4 else 'FAIL — expected 4+'})")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
