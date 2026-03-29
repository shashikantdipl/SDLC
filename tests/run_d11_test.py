"""Live test of D11-api-contract-generator — REST API Contracts."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D11-api-contract-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps API Contracts",
            "interactions": [
                {
                    "id": "I-001",
                    "name": "View Fleet Status",
                    "mcp_tool": "get-fleet-status",
                    "dashboard_screen": "Fleet Overview",
                    "shared_service": "FleetService.getStatus()",
                },
                {
                    "id": "I-002",
                    "name": "Assign Route",
                    "mcp_tool": "assign-route",
                    "dashboard_screen": "Route Planner",
                    "shared_service": "RouteService.assign()",
                },
                {
                    "id": "I-003",
                    "name": "Check HOS Violations",
                    "mcp_tool": "check-hos-violations",
                    "dashboard_screen": "Compliance Dashboard",
                    "shared_service": "HOSService.getViolations()",
                },
                {
                    "id": "I-004",
                    "name": "Report Delivery Exception",
                    "mcp_tool": "report-delivery-exception",
                    "dashboard_screen": "Delivery Tracking",
                    "shared_service": "DeliveryService.reportException()",
                },
                {
                    "id": "I-005",
                    "name": "Get Driver Details",
                    "mcp_tool": "get-driver-details",
                    "dashboard_screen": "Fleet Overview",
                    "shared_service": "DriverService.getDetails()",
                },
                {
                    "id": "I-006",
                    "name": "Update Vehicle Maintenance",
                    "mcp_tool": "update-vehicle-maintenance",
                    "dashboard_screen": "Fleet Overview",
                    "shared_service": "VehicleService.updateMaintenance()",
                },
            ],
            "data_shapes": [
                {
                    "name": "FleetStatus",
                    "fields": [
                        "vehicle_id: string",
                        "vehicle_name: string",
                        "status: enum(active, idle, maintenance, offline)",
                        "latitude: decimal",
                        "longitude: decimal",
                        "speed_mph: integer",
                        "last_updated: datetime",
                        "driver_id: string",
                    ],
                },
                {
                    "name": "RouteAssignment",
                    "fields": [
                        "route_id: string",
                        "route_name: string",
                        "vehicle_id: string",
                        "driver_id: string",
                        "origin: string",
                        "destination: string",
                        "status: enum(planned, active, completed, cancelled)",
                        "eta: datetime",
                        "stops_remaining: integer",
                    ],
                },
                {
                    "name": "HOSViolation",
                    "fields": [
                        "violation_id: string",
                        "driver_id: string",
                        "driver_name: string",
                        "violation_type: enum(driving_limit, rest_required, cycle_limit)",
                        "severity: enum(warning, critical)",
                        "detected_at: datetime",
                        "hours_driven: decimal",
                        "hours_remaining: decimal",
                    ],
                },
                {
                    "name": "DeliveryException",
                    "fields": [
                        "exception_id: string",
                        "delivery_id: string",
                        "exception_type: enum(late, damaged, refused, missing)",
                        "severity: enum(low, medium, high, critical)",
                        "reported_at: datetime",
                        "vehicle_id: string",
                        "resolution_status: enum(open, investigating, resolved)",
                        "description: string",
                    ],
                },
            ],
            "tables": [
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
                "report-delivery-exception",
                "get-driver-details",
            ],
            "dashboard_screens": [
                "Fleet Overview",
                "Route Planner",
                "Compliance Dashboard",
                "Delivery Tracking",
            ],
            "personas": [
                {"name": "Fleet Manager", "primary_interface": "Dashboard"},
                {"name": "Dispatcher", "primary_interface": "Dashboard"},
                {"name": "Compliance Officer", "primary_interface": "Dashboard"},
                {"name": "Integration Engineer", "primary_interface": "API Key"},
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

    # == Section checks ======================================================
    sections = [
        "Base URL",
        "Dual Role",
        "Standard Response Envelope",
        "Authentication",
        "MCP Parity Table",
        "Dashboard Feed Table",
        "Endpoint Specifications",
        "WebSocket",
        "Error Codes",
        "Rate Limiting",
    ]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")
    else:
        print(f"  All 10 sections present")

    # == Endpoint specifications (HTTP methods) ==============================
    http_methods = ["GET", "POST", "PATCH", "DELETE"]
    methods_found = [m for m in http_methods if re.search(rf"\b{m}\b", output)]
    print(f"HTTP methods found: {methods_found}")
    if len(methods_found) < 3:
        print(f"  WARNING: Expected at least GET, POST, PATCH, DELETE")

    # == MCP Parity Table ====================================================
    mcp_tools = [
        "get-fleet-status",
        "assign-route",
        "check-hos-violations",
        "report-delivery-exception",
        "get-driver-details",
    ]
    mcp_found = [t for t in mcp_tools if t in output]
    mcp_missing = [t for t in mcp_tools if t not in output]
    print(f"MCP tools in parity table: {len(mcp_found)}/{len(mcp_tools)}")
    if mcp_missing:
        print(f"  Missing MCP tools: {mcp_missing}")
    else:
        print(f"  All MCP tools have REST parity")

    # == Dashboard Feed Table ================================================
    screens = ["Fleet Overview", "Route Planner", "Compliance Dashboard", "Delivery Tracking"]
    screens_found = [s for s in screens if s in output]
    screens_missing = [s for s in screens if s not in output]
    print(f"Dashboard screens referenced: {len(screens_found)}/{len(screens)}")
    if screens_missing:
        print(f"  Missing screens: {screens_missing}")
    else:
        print(f"  All dashboard screens covered")

    # == Error codes =========================================================
    error_codes = [
        "VALIDATION_ERROR",
        "UNAUTHORIZED",
        "FORBIDDEN",
        "RESOURCE_NOT_FOUND",
        "RATE_LIMITED",
        "INTERNAL_ERROR",
    ]
    err_found = [e for e in error_codes if e in output]
    err_missing = [e for e in error_codes if e not in output]
    print(f"Error codes found: {len(err_found)}/{len(error_codes)}")
    if err_missing:
        print(f"  Missing error codes: {err_missing}")
    else:
        print(f"  All checked error codes present")

    # == WebSocket / SSE =====================================================
    has_websocket = bool(re.search(r"websocket|wss://", output, re.IGNORECASE))
    has_sse = bool(re.search(r"\bSSE\b", output))
    print(f"WebSocket mentioned: {has_websocket}")
    print(f"SSE mentioned: {has_sse}")
    if not (has_websocket or has_sse):
        print(f"  WARNING: No real-time channel found")

    # == Standard envelope ===================================================
    has_envelope_data = '"data"' in output or "'data'" in output
    has_envelope_meta = '"meta"' in output or "'meta'" in output
    has_request_id = "request_id" in output
    has_pagination = "pagination" in output or "per_page" in output
    print(f"Standard envelope: data={has_envelope_data}, meta={has_envelope_meta}, "
          f"request_id={has_request_id}, pagination={has_pagination}")
    if not all([has_envelope_data, has_envelope_meta, has_request_id, has_pagination]):
        print(f"  WARNING: Standard response envelope may be incomplete")

    # == I-NNN interaction references ========================================
    interaction_refs = re.findall(r"I-\d{3}", output)
    unique_refs = set(interaction_refs)
    expected_refs = {"I-001", "I-002", "I-003", "I-004", "I-005", "I-006"}
    print(f"I-NNN references: {len(interaction_refs)} total, {len(unique_refs)} unique")
    ref_missing = expected_refs - unique_refs
    if ref_missing:
        print(f"  Missing interaction refs: {ref_missing}")
    else:
        print(f"  All 6 interaction IDs referenced")

    # == Data shape references ===============================================
    shape_names = ["FleetStatus", "RouteAssignment", "HOSViolation", "DeliveryException"]
    shapes_found = [s for s in shape_names if s in output]
    shapes_missing = [s for s in shape_names if s not in output]
    print(f"Data shapes referenced: {len(shapes_found)}/{len(shape_names)}")
    if shapes_missing:
        print(f"  Missing shapes: {shapes_missing}")
    else:
        print(f"  All data shapes present")

    # == Shared service references ===========================================
    services = [
        "FleetService",
        "RouteService",
        "HOSService",
        "DeliveryService",
        "DriverService",
    ]
    svc_found = [s for s in services if s in output]
    print(f"Shared services referenced: {len(svc_found)}/{len(services)}  {svc_found}")

    # == Rate limit headers ==================================================
    rate_headers = ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
    rh_found = [h for h in rate_headers if h in output]
    print(f"Rate limit headers: {len(rh_found)}/{len(rate_headers)}  {rh_found}")

    # == /api/v1/ path presence ==============================================
    has_api_v1 = "/api/v1/" in output
    print(f"API versioned path (/api/v1/): {has_api_v1}")

    # == Table references ====================================================
    tables = ["vehicles", "drivers", "routes", "deliveries", "hos_records"]
    tbl_found = [t for t in tables if t.lower() in output.lower()]
    print(f"DB tables referenced: {len(tbl_found)}/{len(tables)}  {tbl_found}")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
