"""Live test of D7-interaction-map-generator — THE KEY Full-Stack-First doc."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D7-interaction-map-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "capabilities": [
                {"id": "C1", "name": "Fleet Monitoring"},
                {"id": "C2", "name": "Route Management"},
                {"id": "C3", "name": "HOS Compliance"},
                {"id": "C4", "name": "Cost Analytics"},
                {"id": "C5", "name": "Exception Handling"},
                {"id": "C6", "name": "Driver Management"},
                {"id": "C7", "name": "Reporting & Audit"},
                {"id": "C8", "name": "Integration Layer"},
                {"id": "C9", "name": "MCP Interface"},
                {"id": "C10", "name": "Operator Dashboard"},
                {"id": "C11", "name": "Notifications"},
            ],
            "features": [
                {"id": "F-001", "title": "Real-Time Vehicle Position", "interfaces": ["mcp", "rest", "dashboard"], "shared_service": "FleetService"},
                {"id": "F-002", "title": "Vehicle Status Badges", "interfaces": ["rest", "dashboard"], "shared_service": "FleetService"},
                {"id": "F-005", "title": "Route Reassignment", "interfaces": ["mcp", "rest", "dashboard"], "shared_service": "RouteService"},
                {"id": "F-008", "title": "HOS Violation Alert", "interfaces": ["mcp", "rest", "dashboard"], "shared_service": "ComplianceService"},
                {"id": "F-012", "title": "Cost Per Delivery", "interfaces": ["mcp", "rest", "dashboard"], "shared_service": "CostService"},
                {"id": "F-015", "title": "Delivery Exception Detection", "interfaces": ["mcp", "rest", "dashboard"], "shared_service": "ExceptionService"},
                {"id": "F-020", "title": "Driver Performance Score", "interfaces": ["rest", "dashboard"], "shared_service": "DriverService"},
                {"id": "F-025", "title": "Fleet KPI Dashboard", "interfaces": ["rest", "dashboard"], "shared_service": "ReportingService"},
                {"id": "F-030", "title": "GPS Integration (Samsara)", "interfaces": ["rest"], "shared_service": "IntegrationService"},
                {"id": "F-035", "title": "MCP Fleet Query Tools", "interfaces": ["mcp", "rest"], "shared_service": "FleetService"},
                {"id": "F-040", "title": "Audit Event Export", "interfaces": ["mcp", "rest", "dashboard"], "shared_service": "AuditService"},
                {"id": "F-042", "title": "Slack Alert Notifications", "interfaces": ["rest"], "shared_service": "NotificationService"},
            ],
            "components": [
                {"name": "FleetService", "type": "shared_service"},
                {"name": "RouteService", "type": "shared_service"},
                {"name": "ComplianceService", "type": "shared_service"},
                {"name": "CostService", "type": "shared_service"},
                {"name": "ExceptionService", "type": "shared_service"},
                {"name": "DriverService", "type": "shared_service"},
                {"name": "ReportingService", "type": "shared_service"},
                {"name": "AuditService", "type": "shared_service"},
                {"name": "IntegrationService", "type": "shared_service"},
                {"name": "NotificationService", "type": "shared_service"},
            ],
            "personas": [
                {"name": "Maria Santos", "primary_interface": "dashboard"},
                {"name": "James Park", "primary_interface": "dashboard"},
                {"name": "Sarah Chen", "primary_interface": "mcp"},
                {"name": "Alex Rivera", "primary_interface": "mcp"},
                {"name": "David Kim", "primary_interface": "dashboard"},
            ],
            "data_entities": [
                "Vehicle", "Driver", "Route", "Delivery", "GPSPosition",
                "HOSRecord", "FuelTransaction", "CostRecord", "AuditEvent",
                "DeliveryException", "DriverScore", "FleetKPI",
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
    sections = ["Interaction Inventory", "Data Shape", "Cross-Interface",
                "Naming Convention", "Parity Matrix", "Interaction ID", "Naming Conflict"]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")

    # Interaction IDs
    i_ids = set(re.findall(r"I-\d{3}", output))
    print(f"Interaction IDs: {len(i_ids)} unique I-NNN")

    # Data shapes
    shape_matches = set(re.findall(r"Shape:\s*(\w+)", output))
    print(f"Data shapes defined: {len(shape_matches)}")

    # MCP tool names
    tool_names = set(re.findall(r"`(\w+_\w+)`", output))
    print(f"MCP tool names (snake_case): {len(tool_names)}")

    # Cross-interface journeys
    journey_count = len(re.findall(r"Journey \d+", output))
    print(f"Cross-interface journeys: {journey_count}")

    # Naming checks
    has_synonym_table = "synonym" in output.lower() or "DO NOT USE" in output
    has_verb_table = "verb" in output.lower() and "convention" in output.lower()
    print(f"Synonym table: {has_synonym_table}")
    print(f"Verb convention table: {has_verb_table}")

    # Parity
    has_parity = "parity" in output.lower()
    print(f"Parity matrix: {has_parity}")

    print()
    print("=== FIRST 2500 CHARS ===")
    print(output[:2500])


if __name__ == "__main__":
    asyncio.run(main())
