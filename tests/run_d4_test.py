"""Live test of D4-feature-extractor."""

import asyncio
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from sdk.base_agent import BaseAgent
from pathlib import Path


async def main():
    agent = BaseAgent(agent_dir=Path("agents/design/D4-feature-extractor"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "capabilities": [
                {"id": "C1", "name": "Fleet Monitoring", "description": "Real-time GPS tracking and status for 200 trucks"},
                {"id": "C2", "name": "Route Management", "description": "Dynamic route assignment and optimization"},
                {"id": "C3", "name": "HOS Compliance", "description": "DOT Hours-of-Service tracking and violation alerts"},
                {"id": "C4", "name": "Cost Analytics", "description": "Per-delivery cost, fuel reports, budget tracking"},
                {"id": "C5", "name": "Exception Handling", "description": "Delivery exception detection and escalation"},
                {"id": "C6", "name": "Driver Management", "description": "Driver records, performance scoring"},
                {"id": "C7", "name": "Reporting & Audit", "description": "KPI dashboards, compliance reports, audit trail"},
                {"id": "C8", "name": "Integration Layer", "description": "Samsara GPS, AS/400 bridge, fuel card import"},
                {"id": "C9", "name": "MCP Interface", "description": "AI clients query fleet via MCP tools"},
                {"id": "C10", "name": "Operator Dashboard", "description": "Web UI for dispatchers and managers"},
                {"id": "C11", "name": "Notifications", "description": "Real-time alerts via Slack, email, dashboard"},
            ],
            "components": [
                {"name": "MCP Fleet Server", "technology": "Python MCP SDK", "responsibility": "Fleet query tools for AI clients"},
                {"name": "REST API", "technology": "aiohttp", "responsibility": "HTTP endpoints for dashboard and integrations"},
                {"name": "Dashboard", "technology": "Streamlit", "responsibility": "Operator web interface"},
                {"name": "Fleet Service", "technology": "Python", "responsibility": "Core fleet business logic"},
                {"name": "Route Service", "technology": "Python", "responsibility": "Route optimization and assignment"},
                {"name": "Compliance Service", "technology": "Python", "responsibility": "HOS tracking and alerting"},
                {"name": "Cost Service", "technology": "Python", "responsibility": "Cost calculation and reporting"},
                {"name": "Integration Adapter", "technology": "Python", "responsibility": "Samsara GPS + AS/400 + fuel card connectors"},
                {"name": "PostgreSQL", "technology": "PostgreSQL 15", "responsibility": "Primary data store"},
            ],
            "personas": [
                {"name": "Maria Santos", "primary_interface": "dashboard"},
                {"name": "James Park", "primary_interface": "dashboard"},
                {"name": "Sarah Chen", "primary_interface": "mcp"},
                {"name": "Alex Rivera", "primary_interface": "mcp"},
                {"name": "David Kim", "primary_interface": "dashboard"},
            ],
            "constraints": {
                "budget": "$350,000",
                "timeline": "MVP 6 months",
            },
        },
        project_id="fleetops-001",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # Check for JSON blocks
    json_blocks = re.findall(r"```json\s*(.*?)```", output, re.DOTALL)
    print(f"JSON blocks found: {len(json_blocks)}")

    # Try to parse META
    valid_json = 0
    for block in json_blocks:
        try:
            json.loads(block.strip())
            valid_json += 1
        except Exception:
            pass
    print(f"Valid JSON blocks: {valid_json}/{len(json_blocks)}")

    # Count features
    feature_ids = set(re.findall(r'"id"\s*:\s*"(F-\d+)"', output))
    print(f"Features: {len(feature_ids)} unique F-NNN IDs")

    # Count epics
    epic_ids = set(re.findall(r'"epic"\s*:\s*"(E-\d+)"', output))
    print(f"Epics: {len(epic_ids)} unique E-NNN IDs")

    # Check 18-field compliance (sample first feature)
    required_fields = ["id", "title", "type", "epic", "summary", "status", "moscow",
                       "priority", "story_points", "effort", "complexity", "sprint_or_phase",
                       "friction", "incentive_type", "ai_required", "primary_personas",
                       "dependencies", "data_prerequisites"]
    if json_blocks:
        try:
            first_block = json.loads(json_blocks[1].strip()) if len(json_blocks) > 1 else json.loads(json_blocks[0].strip())
            if isinstance(first_block, list) and first_block:
                sample = first_block[0]
            elif isinstance(first_block, dict) and "features" in first_block:
                sample = first_block["features"][0]
            else:
                sample = first_block
            present = [f for f in required_fields if f in sample]
            missing = [f for f in required_fields if f not in sample]
            print(f"18-field check: {len(present)}/18 fields present")
            if missing:
                print(f"  Missing: {missing}")
        except Exception as e:
            print(f"  Could not parse sample feature: {e}")

    # Check key v2 fields
    has_ai_required = '"ai_required"' in output
    has_friction = '"friction"' in output
    has_incentive = '"incentive_type"' in output
    print(f"ai_required field: {has_ai_required}")
    print(f"friction field: {has_friction}")
    print(f"incentive_type field: {has_incentive}")

    # MoSCoW distribution
    must = output.count('"Must-Have"')
    should = output.count('"Should-Have"')
    could = output.count('"Could-Have"')
    print(f"MoSCoW: Must={must}, Should={should}, Could={could}")

    print()
    print("=== FIRST 2000 CHARS ===")
    print(output[:2000])


if __name__ == "__main__":
    asyncio.run(main())
