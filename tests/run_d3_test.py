"""Live test of D3-architecture-drafter."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D3-architecture-drafter"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "capabilities": [
                {"id": "C1", "name": "Fleet Monitoring", "description": "Real-time GPS tracking and status visualization for 200 trucks"},
                {"id": "C2", "name": "Route Management", "description": "Dynamic route assignment, reassignment, and optimization"},
                {"id": "C3", "name": "HOS Compliance", "description": "Automated DOT Hours-of-Service tracking and violation alerts"},
                {"id": "C4", "name": "Cost Analytics", "description": "Per-delivery cost calculation, fuel reporting, budget tracking"},
                {"id": "C5", "name": "Exception Handling", "description": "Automated delivery exception detection and escalation"},
                {"id": "C6", "name": "Driver Management", "description": "Driver records, performance scoring, scheduling"},
                {"id": "C7", "name": "Reporting & Audit", "description": "KPI dashboards, compliance reports, audit trail"},
                {"id": "C8", "name": "Integration Layer", "description": "Samsara GPS API, AS/400 migration bridge, fuel card import"},
                {"id": "C9", "name": "MCP Interface", "description": "AI coding assistants can query fleet status, trigger reports via MCP tools"},
                {"id": "C10", "name": "Operator Dashboard", "description": "Web-based visual interface for dispatchers and managers"},
                {"id": "C11", "name": "Notification System", "description": "Real-time alerts via Slack, email, dashboard for exceptions and violations"},
            ],
            "personas": [
                {"name": "Maria Santos", "primary_interface": "dashboard"},
                {"name": "James Park", "primary_interface": "dashboard"},
                {"name": "Sarah Chen", "primary_interface": "mcp"},
                {"name": "Alex Rivera", "primary_interface": "mcp"},
                {"name": "David Kim", "primary_interface": "dashboard"},
                {"name": "Tom Miller", "primary_interface": "dashboard"},
            ],
            "constraints": {
                "budget": "$350,000",
                "timeline": "MVP 6 months",
                "technology": ["Must integrate Samsara GPS API v3.2", "AS/400 parallel run during migration", "US data residency"],
                "regulatory": ["DOT HOS compliance"],
            },
            "integration_points": [
                {"system": "Samsara GPS", "direction": "Inbound", "protocol": "REST API", "frequency": "Real-time 30s"},
                {"system": "AS/400", "direction": "Bidirectional", "protocol": "File transfer then API bridge", "frequency": "Nightly then real-time"},
                {"system": "Fuel Card Provider", "direction": "Inbound", "protocol": "CSV", "frequency": "Daily"},
                {"system": "Slack", "direction": "Outbound", "protocol": "Webhook", "frequency": "Event-driven"},
            ],
            "data_entities": ["Vehicle", "Driver", "Route", "Delivery", "GPSPosition", "HOSRecord", "FuelTransaction", "Exception", "CostRecord"],
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
    sections = ["System Context", "Container", "Shared Service", "MCP Server",
                "Dashboard", "Component", "Tech Stack", "Cross-Cutting",
                "Data Flow", "Parity Matrix", "10x Scale"]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")

    # Key architecture checks
    has_mcp = "MCP" in output
    has_rest = "REST" in output or "aiohttp" in output.lower()
    has_dashboard = "Dashboard" in output or "Streamlit" in output
    has_shared_services = "shared service" in output.lower() or "service layer" in output.lower()
    has_llm_agnostic = "LLM" in output and ("agnostic" in output.lower() or "provider" in output.lower())
    has_memory = "memory" in output.lower() and ("tier" in output.lower() or "episodic" in output.lower())
    has_rag = "RAG" in output or "retrieval" in output.lower()
    has_ascii = "```" in output or "+-" in output or "|-" in output

    print(f"MCP architecture: {has_mcp}")
    print(f"REST API: {has_rest}")
    print(f"Dashboard: {has_dashboard}")
    print(f"Shared service layer: {has_shared_services}")
    print(f"LLM-agnostic: {has_llm_agnostic}")
    print(f"Agent memory: {has_memory}")
    print(f"RAG/Knowledge: {has_rag}")
    print(f"ASCII diagrams: {has_ascii}")

    # Tech decision count
    decision_rows = len(re.findall(r"\|.*\|.*\|.*\|.*\|.*\|", output))
    print(f"Table rows (approx tech decisions): {decision_rows}")

    print()
    print("=== FIRST 2500 CHARS ===")
    print(output[:2500])


if __name__ == "__main__":
    asyncio.run(main())
