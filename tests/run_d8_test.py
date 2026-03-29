"""Live test of D8-mcp-tool-spec-writer — MCP Tool Specification."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D8-mcp-tool-spec-writer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "interactions": [
                {
                    "id": "I-001",
                    "name": "Get Fleet Status",
                    "mcp_tool": "get_fleet_status",
                    "shared_service": "FleetService.getStatus()",
                    "data_required": "fleet_id",
                },
                {
                    "id": "I-003",
                    "name": "Get Vehicle Position",
                    "mcp_tool": "get_vehicle_position",
                    "shared_service": "FleetService.getVehiclePosition()",
                    "data_required": "vehicle_id",
                },
                {
                    "id": "I-005",
                    "name": "Reassign Route",
                    "mcp_tool": "reassign_route",
                    "shared_service": "RouteService.reassign()",
                    "data_required": "route_id, driver_id, reason",
                },
                {
                    "id": "I-008",
                    "name": "Get HOS Violations",
                    "mcp_tool": "get_hos_violations",
                    "shared_service": "ComplianceService.getViolations()",
                    "data_required": "driver_id, date_range",
                },
                {
                    "id": "I-012",
                    "name": "Get Cost Per Delivery",
                    "mcp_tool": "get_cost_per_delivery",
                    "shared_service": "CostService.getCostPerDelivery()",
                    "data_required": "delivery_id",
                },
            ],
            "data_shapes": [
                {
                    "name": "FleetStatus",
                    "fields": [
                        "fleet_id: string",
                        "total_vehicles: integer",
                        "active_vehicles: integer",
                        "idle_vehicles: integer",
                        "last_updated: datetime",
                    ],
                },
                {
                    "name": "VehiclePosition",
                    "fields": [
                        "vehicle_id: string",
                        "latitude: decimal",
                        "longitude: decimal",
                        "speed_mph: decimal",
                        "heading: integer",
                        "timestamp: datetime",
                    ],
                },
                {
                    "name": "RouteAssignment",
                    "fields": [
                        "route_id: string",
                        "driver_id: string",
                        "status: enum(assigned, in_progress, completed, cancelled)",
                        "reassignment_reason: string",
                        "assigned_at: datetime",
                    ],
                },
                {
                    "name": "DeliveryCost",
                    "fields": [
                        "delivery_id: string",
                        "fuel_cost: decimal",
                        "labor_cost: decimal",
                        "total_cost: decimal",
                        "currency: string",
                        "calculated_at: datetime",
                    ],
                },
            ],
            "mcp_servers": [
                {"name": "fleet-mcp-server", "domain": "fleet", "port": 8100},
                {"name": "route-mcp-server", "domain": "route", "port": 8101},
                {"name": "compliance-mcp-server", "domain": "compliance", "port": 8102},
            ],
            "quality_nfrs": [
                "Q-001: MCP tool response < 500ms p95",
                "Q-002: MCP resource subscription latency < 200ms",
                "Q-049: Every MCP tool has REST equivalent",
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

    # --- Section checks ---
    sections = [
        "Server Inventory",
        "Tool Specification",
        "Resource",
        "Prompt Template",
        "Authentication",
        "Error Handling",
        "Rate Limit",
        "REST API Derivation",
        "Testing Strategy",
    ]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")

    # --- Tool names ---
    expected_tools = [
        "get_fleet_status",
        "get_vehicle_position",
        "reassign_route",
        "get_hos_violations",
        "get_cost_per_delivery",
    ]
    tools_found = [t for t in expected_tools if t in output]
    tools_missing = [t for t in expected_tools if t not in output]
    print(f"Tool names: {len(tools_found)}/{len(expected_tools)} found")
    if tools_missing:
        print(f"  Missing tools: {tools_missing}")

    # --- Interaction ID references ---
    i_ids = set(re.findall(r"I-\d{3}", output))
    expected_ids = {"I-001", "I-003", "I-005", "I-008", "I-012"}
    ids_found = expected_ids & i_ids
    ids_missing = expected_ids - i_ids
    print(f"Interaction IDs: {len(ids_found)}/{len(expected_ids)} referenced")
    if ids_missing:
        print(f"  Missing IDs: {ids_missing}")

    # --- JSON Schema blocks ---
    json_schema_count = len(re.findall(r'"type"\s*:\s*"object"', output))
    print(f"JSON Schema blocks: {json_schema_count} (expect >= 5)")

    # --- Data shape references ---
    shape_names = ["FleetStatus", "VehiclePosition", "RouteAssignment", "DeliveryCost"]
    shapes_found = [s for s in shape_names if s in output]
    shapes_missing = [s for s in shape_names if s not in output]
    print(f"Data shapes referenced: {len(shapes_found)}/{len(shape_names)}")
    if shapes_missing:
        print(f"  Missing shapes: {shapes_missing}")

    # --- Error codes ---
    error_codes = set(re.findall(r"[A-Z][A-Z_]{3,}", output))
    # Filter to likely error codes (domain-prefixed screaming snake case)
    domain_errors = [c for c in error_codes if "_" in c and len(c) > 6]
    print(f"Error codes (SCREAMING_SNAKE_CASE): {len(domain_errors)}")

    # --- Resource URI patterns ---
    uri_patterns = re.findall(r"\w+://\S+", output)
    print(f"Resource URI patterns: {len(set(uri_patterns))}")

    # --- Prompt templates ---
    prompt_names = re.findall(r"(?:Prompt|prompt)[:\s]+[`\"]?([a-z][\w-]+)", output)
    print(f"Prompt templates found: {len(set(prompt_names))}")

    # --- REST derivation entries ---
    rest_methods = re.findall(r"\b(GET|POST|PATCH|PUT|DELETE)\b", output)
    print(f"REST method references: {len(rest_methods)}")

    # --- MCP server names ---
    server_names = ["fleet-mcp-server", "route-mcp-server", "compliance-mcp-server"]
    servers_found = [s for s in server_names if s in output]
    print(f"MCP servers referenced: {len(servers_found)}/{len(server_names)}")

    print()
    print("=== FIRST 2500 CHARS ===")
    print(output[:2500])


if __name__ == "__main__":
    asyncio.run(main())
