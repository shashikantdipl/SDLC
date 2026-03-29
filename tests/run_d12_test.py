"""Live test of D12-user-story-writer — Client-Facing User Stories."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D12-user-story-writer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps User Stories",
            "features": [
                # 4 Must-Have
                {
                    "id": "F-001",
                    "title": "Real-Time Fleet Tracking",
                    "epic": "Fleet Visibility",
                    "moscow": "Must-Have",
                    "story_points": 13,
                    "primary_personas": ["Fleet Manager", "Dispatcher"],
                },
                {
                    "id": "F-002",
                    "title": "Route Assignment & Optimization",
                    "epic": "Route Management",
                    "moscow": "Must-Have",
                    "story_points": 8,
                    "primary_personas": ["Dispatcher"],
                },
                {
                    "id": "F-003",
                    "title": "HOS Compliance Monitoring",
                    "epic": "Compliance & Safety",
                    "moscow": "Must-Have",
                    "story_points": 8,
                    "primary_personas": ["Compliance Officer"],
                },
                {
                    "id": "F-004",
                    "title": "Delivery Exception Reporting",
                    "epic": "Delivery Operations",
                    "moscow": "Must-Have",
                    "story_points": 5,
                    "primary_personas": ["Fleet Manager", "Dispatcher"],
                },
                # 3 Should-Have
                {
                    "id": "F-005",
                    "title": "Driver Performance Scorecards",
                    "epic": "Fleet Visibility",
                    "moscow": "Should-Have",
                    "story_points": 5,
                    "primary_personas": ["Fleet Manager"],
                },
                {
                    "id": "F-006",
                    "title": "Predictive Maintenance Alerts",
                    "epic": "Fleet Visibility",
                    "moscow": "Should-Have",
                    "story_points": 8,
                    "primary_personas": ["Fleet Manager"],
                },
                {
                    "id": "F-007",
                    "title": "Geofence Zone Management",
                    "epic": "Route Management",
                    "moscow": "Should-Have",
                    "story_points": 5,
                    "primary_personas": ["Dispatcher", "Fleet Manager"],
                },
                # 1 Could-Have
                {
                    "id": "F-008",
                    "title": "Customer Delivery Notifications",
                    "epic": "Delivery Operations",
                    "moscow": "Could-Have",
                    "story_points": 3,
                    "primary_personas": ["Fleet Manager"],
                },
            ],
            "personas": [
                {
                    "name": "Fleet Manager",
                    "role": "Operations lead responsible for fleet utilization and cost control",
                    "goals": [
                        "Maximize fleet utilization above 85%",
                        "Reduce unplanned downtime by 30%",
                        "Monitor driver safety compliance",
                    ],
                    "primary_interface": "Dashboard",
                },
                {
                    "name": "Dispatcher",
                    "role": "Day-to-day coordinator assigning drivers to routes",
                    "goals": [
                        "Assign optimal routes within 2 minutes",
                        "Respond to delivery exceptions in real time",
                        "Balance driver workloads fairly",
                    ],
                    "primary_interface": "Both",
                },
                {
                    "name": "Compliance Officer",
                    "role": "Ensures regulatory compliance for hours of service and safety",
                    "goals": [
                        "Zero HOS violations in audits",
                        "Generate compliance reports on demand",
                        "Track violation trends over time",
                    ],
                    "primary_interface": "Dashboard",
                },
                {
                    "name": "AI Fleet Assistant",
                    "role": "AI agent that automates routine fleet operations via MCP tools",
                    "goals": [
                        "Proactively surface fleet anomalies",
                        "Execute routine assignments without human intervention",
                        "Provide natural-language fleet status summaries",
                    ],
                    "primary_interface": "MCP",
                },
            ],
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
            "quality_thresholds": [
                "Q-001: API p95 < 200ms",
                "Q-012: Uptime 99.9%",
                "Q-033: Dashboard load < 3s",
            ],
        },
        project_id="fleetops-012",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == Section checks ======================================================
    sections = [
        "Epic Summary",
        "Human Stories",
        "System Stories",
        "Parking Lot",
        "Assumptions",
        "Glossary",
    ]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  MISSING: {missing}")
    else:
        print(f"  All 6 sections present")

    # == US-DOMAIN-NNN story IDs =============================================
    human_story_ids = re.findall(r"US-[A-Z]+-\d{3}\b", output)
    # Filter out SYS suffixed ones for human count
    human_only = [s for s in human_story_ids if not s.endswith("-SYS") and "-SYS" not in output[output.find(s):output.find(s)+20]]
    # More precise: find US-XXX-NNN that are NOT followed by -SYS
    human_stories = set(re.findall(r"US-[A-Z]+-\d{3}(?!-SYS)", output))
    sys_stories = set(re.findall(r"US-[A-Z]+-\d{3}-SYS", output))
    print(f"Human story IDs (unique): {len(human_stories)}")
    if len(human_stories) >= 25:
        print(f"  PASS: >= 25 human stories")
    else:
        print(f"  WARNING: Expected >= 25 human stories, got {len(human_stories)}")

    # == System story count ==================================================
    print(f"System story IDs (unique): {len(sys_stories)}")
    if len(sys_stories) >= 15:
        print(f"  PASS: >= 15 system stories")
    else:
        print(f"  WARNING: Expected >= 15 system stories, got {len(sys_stories)}")

    # == Given/When/Then acceptance criteria ==================================
    gwt_given = len(re.findall(r"\bGiven\b", output))
    gwt_when = len(re.findall(r"\bWhen\b", output))
    gwt_then = len(re.findall(r"\bThen\b", output))
    print(f"Given/When/Then ACs: Given={gwt_given}, When={gwt_when}, Then={gwt_then}")
    if gwt_given >= 25 and gwt_when >= 25 and gwt_then >= 25:
        print(f"  PASS: Sufficient GWT acceptance criteria")
    else:
        print(f"  WARNING: Expected >= 25 of each GWT keyword")

    # == F-NNN feature traceability ==========================================
    feature_refs = set(re.findall(r"F-\d{3}", output))
    expected_features = {"F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007", "F-008"}
    print(f"F-NNN references (unique): {len(feature_refs)}  {sorted(feature_refs)}")
    feat_missing = expected_features - feature_refs
    if feat_missing:
        print(f"  MISSING features: {feat_missing}")
    else:
        print(f"  PASS: All 8 features traced")

    # == PL-NNN parking lot items ============================================
    parking_lot_ids = set(re.findall(r"PL-\d{3}", output))
    print(f"Parking lot items (PL-NNN): {len(parking_lot_ids)}")
    if len(parking_lot_ids) >= 5:
        print(f"  PASS: >= 5 parking lot items")
    else:
        print(f"  WARNING: Expected >= 5 parking lot items, got {len(parking_lot_ids)}")

    # == Persona name references =============================================
    persona_names = ["Fleet Manager", "Dispatcher", "Compliance Officer", "AI Fleet Assistant"]
    personas_found = [p for p in persona_names if p in output]
    personas_missing = [p for p in persona_names if p not in output]
    print(f"Persona names referenced: {len(personas_found)}/{len(persona_names)}")
    if personas_missing:
        print(f"  MISSING personas: {personas_missing}")
    else:
        print(f"  PASS: All 4 personas referenced")

    # == API endpoint references in SACs =====================================
    api_endpoints = [
        "/api/v1/vehicles",
        "/api/v1/routes",
        "/api/v1/hos-violations",
    ]
    api_found = [e for e in api_endpoints if e in output]
    api_missing = [e for e in api_endpoints if e not in output]
    print(f"API endpoints in SACs: {len(api_found)}/{len(api_endpoints)}")
    if api_missing:
        print(f"  MISSING endpoints: {api_missing}")
    else:
        print(f"  PASS: All API endpoints referenced in system stories")

    # == Data entity references in SACs ======================================
    data_entities = ["vehicles", "drivers", "routes", "deliveries", "hos_records"]
    entity_found = [e for e in data_entities if e.lower() in output.lower()]
    entity_missing = [e for e in data_entities if e.lower() not in output.lower()]
    print(f"Data entities in SACs: {len(entity_found)}/{len(data_entities)}")
    if entity_missing:
        print(f"  MISSING entities: {entity_missing}")
    else:
        print(f"  PASS: All data entities referenced in system stories")

    # == MCP tool references =================================================
    mcp_tools = ["get-fleet-status", "assign-route", "check-hos-violations"]
    mcp_found = [t for t in mcp_tools if t in output]
    mcp_missing = [t for t in mcp_tools if t not in output]
    print(f"MCP tools referenced: {len(mcp_found)}/{len(mcp_tools)}")
    if mcp_missing:
        print(f"  MISSING MCP tools: {mcp_missing}")
    else:
        print(f"  PASS: All MCP tools referenced")

    # == MoSCoW distribution =================================================
    must_count = output.lower().count("must-have")
    should_count = output.lower().count("should-have")
    could_count = output.lower().count("could-have")
    print(f"MoSCoW mentions: Must-Have={must_count}, Should-Have={should_count}, Could-Have={could_count}")
    if must_count > 0 and should_count > 0 and could_count > 0:
        print(f"  PASS: All three MoSCoW priorities present")
    else:
        print(f"  WARNING: Expected all three MoSCoW priorities")

    # == Quality threshold references ========================================
    q_refs = set(re.findall(r"Q-\d{3}", output))
    print(f"Quality thresholds (Q-NNN): {len(q_refs)}  {sorted(q_refs)}")
    expected_q = {"Q-001", "Q-012", "Q-033"}
    q_missing = expected_q - q_refs
    if q_missing:
        print(f"  MISSING thresholds: {q_missing}")
    else:
        print(f"  PASS: All quality thresholds referenced")

    # == SAC format check ====================================================
    sac_count = len(re.findall(r"SAC-\d+", output))
    print(f"SAC entries: {sac_count}")
    if sac_count >= 30:
        print(f"  PASS: >= 30 SAC entries (avg 2+ per system story)")
    else:
        print(f"  INFO: {sac_count} SAC entries found")

    # == Epic table check ====================================================
    epic_ids = set(re.findall(r"E-\d{3}", output))
    print(f"Epic IDs (E-NNN): {len(epic_ids)}  {sorted(epic_ids)}")

    # == Glossary term count =================================================
    # Look for table rows in glossary section (rough heuristic)
    glossary_match = re.search(r"(?i)glossary.*?\n((?:\|.*\n)+)", output)
    if glossary_match:
        glossary_rows = [r for r in glossary_match.group(1).split("\n") if r.strip().startswith("|") and "---" not in r and "Term" not in r]
        print(f"Glossary terms: {len(glossary_rows)}")
        if len(glossary_rows) >= 10:
            print(f"  PASS: >= 10 glossary terms")
        else:
            print(f"  WARNING: Expected >= 10 glossary terms, got {len(glossary_rows)}")
    else:
        print(f"Glossary terms: Could not parse glossary table")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
