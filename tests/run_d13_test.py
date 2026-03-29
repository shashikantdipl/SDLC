"""Live test of D13-backlog-builder — Sprint-Ready Developer Backlog."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D13-backlog-builder"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Backlog",
            "features": [
                {
                    "id": "F-001",
                    "title": "Real-Time Fleet Tracking",
                    "epic": "Fleet Visibility",
                    "moscow": "Must-Have",
                    "story_points": 13,
                    "interfaces": ["Dashboard", "MCP"],
                },
                {
                    "id": "F-002",
                    "title": "Route Assignment & Optimization",
                    "epic": "Route Management",
                    "moscow": "Must-Have",
                    "story_points": 8,
                    "interfaces": ["Dashboard", "MCP", "REST"],
                },
                {
                    "id": "F-003",
                    "title": "HOS Compliance Monitoring",
                    "epic": "Compliance & Safety",
                    "moscow": "Must-Have",
                    "story_points": 8,
                    "interfaces": ["Dashboard", "REST"],
                },
                {
                    "id": "F-004",
                    "title": "Delivery Exception Reporting",
                    "epic": "Delivery Operations",
                    "moscow": "Should-Have",
                    "story_points": 5,
                    "interfaces": ["Dashboard", "REST"],
                },
                {
                    "id": "F-005",
                    "title": "Driver Performance Scorecards",
                    "epic": "Fleet Visibility",
                    "moscow": "Should-Have",
                    "story_points": 5,
                    "interfaces": ["Dashboard"],
                },
                {
                    "id": "F-006",
                    "title": "Predictive Maintenance Alerts",
                    "epic": "Fleet Visibility",
                    "moscow": "Could-Have",
                    "story_points": 8,
                    "interfaces": ["Dashboard", "MCP"],
                },
            ],
            "user_stories": [
                {
                    "id": "US-FLEET-001",
                    "title": "Track vehicle locations in real time",
                    "epic": "Fleet Visibility",
                    "story_points": 8,
                },
                {
                    "id": "US-FLEET-002",
                    "title": "Assign drivers to optimized routes",
                    "epic": "Route Management",
                    "story_points": 5,
                },
                {
                    "id": "US-FLEET-003",
                    "title": "Monitor hours-of-service compliance",
                    "epic": "Compliance & Safety",
                    "story_points": 5,
                },
                {
                    "id": "US-FLEET-004",
                    "title": "Report delivery exceptions automatically",
                    "epic": "Delivery Operations",
                    "story_points": 3,
                },
                {
                    "id": "US-FLEET-005",
                    "title": "View driver performance scores",
                    "epic": "Fleet Visibility",
                    "story_points": 3,
                },
                {
                    "id": "US-FLEET-006",
                    "title": "Receive predictive maintenance alerts",
                    "epic": "Fleet Visibility",
                    "story_points": 5,
                },
                {
                    "id": "US-FLEET-007",
                    "title": "Get fleet status via AI assistant",
                    "epic": "Fleet Visibility",
                    "story_points": 3,
                },
                {
                    "id": "US-FLEET-008",
                    "title": "Assign routes via AI assistant",
                    "epic": "Route Management",
                    "story_points": 3,
                },
            ],
            "team_size": 3,
            "sprint_length_weeks": 2,
            "sprint_velocity": 40,
            "api_endpoints": [
                "GET /api/v1/vehicles",
                "GET /api/v1/vehicles/:id",
                "POST /api/v1/routes",
                "PATCH /api/v1/routes/:id",
                "GET /api/v1/hos-violations",
            ],
            "data_entities": [
                "vehicles",
                "drivers",
                "routes",
                "deliveries",
                "hos_records",
            ],
            "mcp_tools": [
                "get-fleet-status",
                "assign-route",
                "check-hos-violations",
            ],
            "interaction_ids": [
                "I-001",
                "I-002",
                "I-003",
                "I-004",
            ],
        },
        project_id="fleetops-013",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == Section checks ======================================================
    sections = [
        "Sprint Summary",
        "Story Schema",
        "Sprint Stories",
        "Dependency Graph",
        "Traceability Matrix",
    ]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  MISSING: {missing}")
    else:
        print(f"  All 5 sections present")

    # == S-NNN story IDs =====================================================
    story_ids = set(re.findall(r"S-\d{3}", output))
    print(f"Sprint story IDs (S-NNN unique): {len(story_ids)}")
    if len(story_ids) >= 15:
        print(f"  PASS: >= 15 sprint stories")
    else:
        print(f"  WARNING: Expected >= 15 sprint stories, got {len(story_ids)}")

    # == Sprint assignments ==================================================
    sprint_refs = set(re.findall(r"(?i)sprint\s+(\d+)", output))
    print(f"Sprints referenced: {sorted(sprint_refs)}")
    if "0" in sprint_refs:
        print(f"  PASS: Sprint 0 (infrastructure) present")
    else:
        print(f"  WARNING: Sprint 0 not found — infrastructure stories missing")

    # == Layer tags ===========================================================
    layer_tags = ["infrastructure", "service", "mcp", "rest", "dashboard"]
    layers_found = [l for l in layer_tags if l.lower() in output.lower()]
    layers_missing = [l for l in layer_tags if l.lower() not in output.lower()]
    print(f"Layer tags found: {len(layers_found)}/{len(layer_tags)}  {layers_found}")
    if layers_missing:
        print(f"  MISSING layers: {layers_missing}")
    else:
        print(f"  PASS: All core layer tags present")

    # == Given/When/Then acceptance criteria ==================================
    gwt_given = len(re.findall(r"\bGiven\b", output))
    gwt_when = len(re.findall(r"\bWhen\b", output))
    gwt_then = len(re.findall(r"\bThen\b", output))
    print(f"Given/When/Then ACs: Given={gwt_given}, When={gwt_when}, Then={gwt_then}")
    if gwt_given >= 15 and gwt_when >= 15 and gwt_then >= 15:
        print(f"  PASS: Sufficient GWT acceptance criteria")
    else:
        print(f"  WARNING: Expected >= 15 of each GWT keyword")

    # == F-NNN feature traceability ==========================================
    feature_refs = set(re.findall(r"F-\d{3}", output))
    expected_features = {"F-001", "F-002", "F-003", "F-004", "F-005", "F-006"}
    print(f"F-NNN references (unique): {len(feature_refs)}  {sorted(feature_refs)}")
    feat_missing = expected_features - feature_refs
    if feat_missing:
        print(f"  MISSING features: {feat_missing}")
    else:
        print(f"  PASS: All 6 features traced")

    # == US-DOMAIN-NNN user story traceability ===============================
    us_refs = set(re.findall(r"US-FLEET-\d{3}", output))
    expected_us = {
        "US-FLEET-001", "US-FLEET-002", "US-FLEET-003", "US-FLEET-004",
        "US-FLEET-005", "US-FLEET-006", "US-FLEET-007", "US-FLEET-008",
    }
    print(f"US-FLEET-NNN references (unique): {len(us_refs)}  {sorted(us_refs)}")
    us_missing = expected_us - us_refs
    if us_missing:
        print(f"  MISSING user stories: {us_missing}")
    else:
        print(f"  PASS: All 8 user stories traced")

    # == I-NNN interaction ID references =====================================
    interaction_refs = set(re.findall(r"I-\d{3}", output))
    expected_interactions = {"I-001", "I-002", "I-003", "I-004"}
    print(f"I-NNN references (unique): {len(interaction_refs)}  {sorted(interaction_refs)}")
    int_missing = expected_interactions - interaction_refs
    if int_missing:
        print(f"  MISSING interaction IDs: {int_missing}")
    else:
        print(f"  PASS: All 4 interaction IDs referenced")

    # == API endpoint references in ACs ======================================
    api_endpoints = [
        "/api/v1/vehicles",
        "/api/v1/routes",
        "/api/v1/hos-violations",
    ]
    api_found = [e for e in api_endpoints if e in output]
    api_missing = [e for e in api_endpoints if e not in output]
    print(f"API endpoints in ACs: {len(api_found)}/{len(api_endpoints)}")
    if api_missing:
        print(f"  MISSING endpoints: {api_missing}")
    else:
        print(f"  PASS: All API endpoints referenced in stories")

    # == Data entity references ==============================================
    data_entities = ["vehicles", "drivers", "routes", "deliveries", "hos_records"]
    entity_found = [e for e in data_entities if e.lower() in output.lower()]
    entity_missing = [e for e in data_entities if e.lower() not in output.lower()]
    print(f"Data entities referenced: {len(entity_found)}/{len(data_entities)}")
    if entity_missing:
        print(f"  MISSING entities: {entity_missing}")
    else:
        print(f"  PASS: All data entities referenced")

    # == MCP tool references =================================================
    mcp_tools = ["get-fleet-status", "assign-route", "check-hos-violations"]
    mcp_found = [t for t in mcp_tools if t in output]
    mcp_missing = [t for t in mcp_tools if t not in output]
    print(f"MCP tools referenced: {len(mcp_found)}/{len(mcp_tools)}")
    if mcp_missing:
        print(f"  MISSING MCP tools: {mcp_missing}")
    else:
        print(f"  PASS: All MCP tools referenced")

    # == Dependency graph check ==============================================
    dep_arrows = re.findall(r"S-\d{3}\s*-->\s*S-\d{3}", output)
    print(f"Dependency arrows (S-NNN --> S-NNN): {len(dep_arrows)}")
    if len(dep_arrows) >= 5:
        print(f"  PASS: >= 5 dependency relationships shown")
    else:
        print(f"  WARNING: Expected >= 5 dependency arrows, got {len(dep_arrows)}")

    # == Critical path check =================================================
    critical_path = re.findall(r"(?i)critical\s*path", output)
    print(f"Critical path mentioned: {len(critical_path)} times")
    if len(critical_path) >= 1:
        print(f"  PASS: Critical path identified")
    else:
        print(f"  WARNING: Critical path not found in dependency graph")

    # == Sprint velocity check ===============================================
    # Look for points values in sprint summary table rows
    sprint_points = re.findall(r"\|\s*\d+\s*\|\s*[^|]+\|\s*\d+\s*\|\s*(\d+)\s*\|", output)
    print(f"Sprint point values found: {sprint_points}")
    velocity_exceeded = [int(p) for p in sprint_points if int(p) > 40]
    if velocity_exceeded:
        print(f"  FAIL: Sprints exceed velocity (40): {velocity_exceeded}")
    else:
        print(f"  PASS: No sprint exceeds velocity of 40 points")

    # == depends_on references ===============================================
    depends_on_refs = re.findall(r"depends_on:\s*\[([^\]]*)\]", output)
    print(f"depends_on entries: {len(depends_on_refs)}")
    if len(depends_on_refs) >= 10:
        print(f"  PASS: >= 10 stories have depends_on fields")
    else:
        print(f"  INFO: {len(depends_on_refs)} stories have depends_on fields")

    # == definition_of_done check ============================================
    dod_count = len(re.findall(r"definition_of_done:", output))
    print(f"definition_of_done entries: {dod_count}")
    if dod_count >= 10:
        print(f"  PASS: >= 10 stories have definition_of_done")
    else:
        print(f"  WARNING: Expected >= 10 definition_of_done entries, got {dod_count}")

    # == Traceability matrix check ===========================================
    matrix_rows = re.findall(r"\|\s*F-\d{3}\s*\|", output)
    print(f"Traceability matrix rows (F-NNN): {len(matrix_rows)}")
    if len(matrix_rows) >= 6:
        print(f"  PASS: >= 6 feature rows in traceability matrix")
    else:
        print(f"  WARNING: Expected >= 6 traceability rows, got {len(matrix_rows)}")

    # == integration layer check =============================================
    integration_refs = len(re.findall(r"\bintegration\b", output.lower()))
    print(f"Integration layer mentions: {integration_refs}")
    if integration_refs >= 2:
        print(f"  PASS: Integration stories present")
    else:
        print(f"  INFO: Limited integration layer references")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
