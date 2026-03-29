"""Live test of D0-brd-generator — first DESIGN agent."""

import asyncio
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from sdk.base_agent import BaseAgent
from pathlib import Path


async def main():
    agent = BaseAgent(agent_dir=Path("agents/design/D0-brd-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "project_purpose": "A real-time fleet management dashboard for a logistics company with 200 delivery trucks. Dispatchers need to track vehicle locations, manage routes, monitor driver hours, and handle delivery exceptions. The current system is a 15-year-old AS/400 application accessed via terminal emulator.",
            "discovery_sessions": [
                {
                    "persona": "Dispatcher",
                    "name": "Maria Santos",
                    "findings": [
                        "Spends 40% of day switching between 3 screens to find truck status",
                        "Cannot see real-time GPS — relies on drivers calling in",
                        "Route changes require 6 manual steps across 2 systems",
                        "Peak hours (7-9 AM) cause system slowdowns — sometimes 30s per screen load"
                    ],
                    "pain_points": [
                        "No single view of fleet status",
                        "Cannot reassign routes in under 5 minutes",
                        "Delivery exceptions require phone calls to 3 people"
                    ],
                    "goals": [
                        "See all 200 trucks on one screen with status badges",
                        "Reassign a route in under 30 seconds",
                        "Get automatic alerts for delivery exceptions"
                    ]
                },
                {
                    "persona": "Operations Manager",
                    "name": "James Park",
                    "findings": [
                        "Monthly fuel reports take 2 days to compile from AS/400 exports",
                        "Driver hours compliance checked manually — 3 violations missed last quarter",
                        "No cost-per-delivery metric — finance estimates $8.50 but no validation",
                        "Customer SLA breaches discovered 24h after they happen"
                    ],
                    "pain_points": [
                        "No real-time KPI dashboard — relies on end-of-day Excel reports",
                        "Compliance violations discovered after the fact",
                        "Cannot answer 'what did delivery X cost?' without 30 min research"
                    ],
                    "goals": [
                        "Real-time dashboard with fleet KPIs",
                        "Automatic driver hours compliance alerts",
                        "Cost-per-delivery calculated automatically"
                    ]
                },
                {
                    "persona": "IT Director",
                    "name": "Sarah Chen",
                    "findings": [
                        "AS/400 maintenance costs $180K/year — 3 specialists on contract",
                        "Last AS/400 specialist retiring in 18 months",
                        "Integration with GPS provider (Samsara) is via nightly CSV export — not real-time",
                        "Current system has zero automated tests — every change is risky"
                    ],
                    "pain_points": [
                        "AS/400 talent pool shrinking — contractor rates up 40% in 2 years",
                        "No API — every integration is file-based",
                        "Cannot add features without risking regression"
                    ],
                    "goals": [
                        "Modern web stack with API-first architecture",
                        "Real-time GPS integration (not nightly CSV)",
                        "Automated testing to reduce deployment risk"
                    ]
                }
            ],
            "client_documents": [
                "Fleet Operations SLA Agreement (2024)",
                "AS/400 System Documentation (2018, partially outdated)",
                "Samsara GPS API Documentation v3.2"
            ],
            "existing_systems": [
                {
                    "name": "AS/400 Fleet Manager",
                    "technology": "IBM AS/400, RPG, DB2/400",
                    "purpose": "Core fleet management — vehicle tracking, route management, driver records",
                    "pain_points": ["Terminal-only UI", "No API", "Nightly batch processing", "Single point of failure"]
                },
                {
                    "name": "Samsara GPS",
                    "technology": "Cloud SaaS, REST API",
                    "purpose": "GPS tracking for 200 vehicles",
                    "pain_points": ["Integration is CSV-based, not real-time", "Data arrives 12-24h late"]
                },
                {
                    "name": "Excel Reporting",
                    "technology": "Microsoft Excel + VBA macros",
                    "purpose": "KPI reporting, compliance tracking",
                    "pain_points": ["Manual data entry from AS/400 exports", "Macros break frequently", "No audit trail"]
                }
            ],
            "constraints": {
                "budget": "$350,000 total project budget (capital + first year operations)",
                "timeline": "MVP in 6 months, full rollout in 12 months",
                "regulatory": ["DOT driver hours compliance (HOS rules)", "Data residency — US only"],
                "technology": ["Must integrate with Samsara GPS API v3.2", "AS/400 must remain operational during migration (parallel run)"]
            },
            "stakeholders": [
                {"name": "David Kim", "title": "VP Operations", "role": "sponsor", "interest": "high", "influence": "high"},
                {"name": "James Park", "title": "Operations Manager", "role": "decision_maker", "interest": "high", "influence": "medium"},
                {"name": "Sarah Chen", "title": "IT Director", "role": "decision_maker", "interest": "high", "influence": "high"},
                {"name": "Maria Santos", "title": "Lead Dispatcher", "role": "sme", "interest": "high", "influence": "medium"},
                {"name": "Tom Miller", "title": "CFO", "role": "decision_maker", "interest": "medium", "influence": "high"}
            ]
        },
        project_id="fleetops-001",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']} | Model: {result['model']}")
    print()

    # Check output quality
    output = result["output"]
    sections = ["Executive Summary", "Business Case", "Stakeholder Map", "Current State",
                "Business Requirements", "Constraints", "Data Inventory", "Integration Points",
                "Success Criteria", "Open Questions"]
    found = []
    missing = []
    for s in sections:
        if s.lower() in output.lower():
            found.append(s)
        else:
            missing.append(s)

    print(f"Sections found: {len(found)}/{len(sections)}")
    if missing:
        print(f"MISSING sections: {missing}")

    # Check for BR-NNN IDs
    import re
    br_ids = re.findall(r"BR-\w+-\d+|BR-\d+", output)
    print(f"Business Requirements: {len(set(br_ids))} unique BR IDs found")

    oq_ids = re.findall(r"OQ-\d+", output)
    print(f"Open Questions: {len(set(oq_ids))} unique OQ IDs found")

    sc_ids = re.findall(r"SC-\d+", output)
    print(f"Success Criteria: {len(set(sc_ids))} unique SC IDs found")

    print()
    print("=== FIRST 3000 CHARS OF OUTPUT ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
