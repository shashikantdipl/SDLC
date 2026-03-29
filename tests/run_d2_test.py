"""Live test of D2-prd-generator."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D2-prd-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "project_purpose": "Real-time fleet management dashboard replacing a 15-year-old AS/400 system for a logistics company with 200 delivery trucks. Dispatchers, operations managers, and IT need a modern web platform with real-time GPS, automated compliance alerts, and cost-per-delivery tracking.",
            "brd_summary": {
                "business_requirements": [
                    {"id": "BR-FLEET-001", "text": "Real-time fleet status view with all 200 trucks", "priority": "Must-Have", "acceptance_criteria": "Dashboard loads fleet view in <2s"},
                    {"id": "BR-FLEET-002", "text": "Route reassignment in under 30 seconds", "priority": "Must-Have", "acceptance_criteria": "Drag-drop route reassignment completes in <30s"},
                    {"id": "BR-FLEET-003", "text": "Automatic delivery exception alerts", "priority": "Must-Have", "acceptance_criteria": "Alert triggers within 5min of exception"},
                    {"id": "BR-COST-001", "text": "Real-time cost-per-delivery calculation", "priority": "Must-Have", "acceptance_criteria": "Cost calculated within 1h of delivery completion"},
                    {"id": "BR-COST-002", "text": "Monthly fuel cost reports auto-generated", "priority": "Should-Have", "acceptance_criteria": "Report ready by 1st of month"},
                    {"id": "BR-COMP-001", "text": "DOT Hours-of-Service compliance monitoring", "priority": "Must-Have", "acceptance_criteria": "Violation alert within 5min"},
                    {"id": "BR-COMP-002", "text": "Automated compliance audit trail", "priority": "Must-Have", "acceptance_criteria": "100% of HOS events logged"},
                    {"id": "BR-IT-001", "text": "API-first architecture replacing AS/400", "priority": "Must-Have", "acceptance_criteria": "Zero AS/400 dependencies at decommission"},
                    {"id": "BR-IT-002", "text": "Real-time GPS integration via Samsara API", "priority": "Must-Have", "acceptance_criteria": "GPS updates every 30 seconds"},
                    {"id": "BR-IT-003", "text": "Automated test coverage >80%", "priority": "Must-Have", "acceptance_criteria": "CI pipeline enforces 80% threshold"},
                    {"id": "BR-OPS-001", "text": "KPI dashboard for operations management", "priority": "Must-Have", "acceptance_criteria": "Dashboard shows fleet KPIs updated every 60s"},
                    {"id": "BR-OPS-002", "text": "Driver performance scoring", "priority": "Should-Have", "acceptance_criteria": "Daily driver score calculated by 6AM"},
                ],
                "stakeholders": [
                    {"name": "David Kim", "title": "VP Operations", "role": "sponsor"},
                    {"name": "James Park", "title": "Operations Manager", "role": "decision_maker"},
                    {"name": "Sarah Chen", "title": "IT Director", "role": "decision_maker"},
                    {"name": "Maria Santos", "title": "Lead Dispatcher", "role": "sme"},
                    {"name": "Tom Miller", "title": "CFO", "role": "decision_maker"},
                ],
                "success_criteria": [
                    "SC-001: Fleet dashboard loads in <2s",
                    "SC-002: Route reassignment in <30 seconds",
                    "SC-003: HOS compliance alerts within 5 minutes",
                    "SC-004: Cost-per-delivery calculated within 1 hour",
                    "SC-005: AS/400 decommissioned within 12 months",
                ],
                "constraints": {
                    "budget": "$350,000 total",
                    "timeline": "MVP 6 months, full rollout 12 months",
                    "regulatory": ["DOT HOS compliance", "US data residency"],
                },
                "data_inventory": [
                    {"entity": "Vehicle", "source": "AS/400", "volume": "200 records", "sensitivity": "Internal"},
                    {"entity": "Driver", "source": "AS/400", "volume": "250 records", "sensitivity": "Confidential"},
                    {"entity": "Route", "source": "AS/400", "volume": "500/day", "sensitivity": "Internal"},
                    {"entity": "GPS Position", "source": "Samsara", "volume": "200 every 30s", "sensitivity": "Internal"},
                    {"entity": "Delivery", "source": "AS/400", "volume": "800/day", "sensitivity": "Internal"},
                    {"entity": "HOS Record", "source": "AS/400", "volume": "250/day", "sensitivity": "Confidential"},
                ],
                "integration_points": [
                    {"system": "Samsara GPS", "direction": "Inbound", "protocol": "REST API", "frequency": "Real-time (30s)"},
                    {"system": "AS/400 Fleet Manager", "direction": "Bidirectional", "protocol": "File Transfer (during migration)", "frequency": "Nightly batch → real-time"},
                    {"system": "Fuel Card Provider", "direction": "Inbound", "protocol": "CSV import", "frequency": "Daily"},
                ],
            },
            "target_users": [
                {"role": "Dispatcher", "count": 12, "tech_comfort": "medium"},
                {"role": "Operations Manager", "count": 3, "tech_comfort": "high"},
                {"role": "IT Administrator", "count": 2, "tech_comfort": "very_high"},
                {"role": "Executive (VP/CFO)", "count": 3, "tech_comfort": "low"},
                {"role": "Driver", "count": 200, "tech_comfort": "low"},
            ],
        },
        project_id="fleetops-001",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # Section checks
    sections = ["Problem Statement", "Success Metrics", "Personas", "User Journeys",
                "Capabilities", "Out of Scope"]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")

    # Persona count
    persona_matches = re.findall(r"Persona \d+:", output)
    print(f"Personas: {len(persona_matches)}")

    # Journey count
    journey_matches = re.findall(r"Journey \d+:", output)
    print(f"Journeys: {len(journey_matches)}")

    # Capability count
    cap_matches = set(re.findall(r"\bC\d+:", output))
    print(f"Capabilities: {len(cap_matches)}")

    # Metric count
    metric_matches = set(re.findall(r"M-?\d+|SM-\d+", output))
    print(f"Metrics: {len(metric_matches)}")

    # Interface awareness
    has_mcp = "MCP" in output
    has_dashboard = "Dashboard" in output or "dashboard" in output
    has_cross = "cross" in output.lower() and "interface" in output.lower()
    print(f"MCP mentioned: {has_mcp}")
    print(f"Dashboard mentioned: {has_dashboard}")
    print(f"Cross-interface journey: {has_cross}")

    # BR traceability
    br_refs = set(re.findall(r"BR-\w+-\d+", output))
    print(f"BR references: {len(br_refs)} unique")

    print()
    print("=== FIRST 2500 CHARS ===")
    print(output[:2500])


if __name__ == "__main__":
    asyncio.run(main())
