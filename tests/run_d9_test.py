"""Live test of D9-design-spec-writer — Dashboard Design Specification."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D9-design-spec-writer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "interactions": [
                {"id": "I-001", "name": "Get Fleet Status", "dashboard_screen": "Fleet Overview", "shared_service": "FleetService.getStatus()"},
                {"id": "I-002", "name": "Get Vehicle Detail", "dashboard_screen": "Vehicle Detail", "shared_service": "FleetService.getVehicle()"},
                {"id": "I-005", "name": "Reassign Route", "dashboard_screen": "Route Assignment", "shared_service": "RouteService.reassign()"},
                {"id": "I-008", "name": "View HOS Violations", "dashboard_screen": "HOS Compliance", "shared_service": "ComplianceService.getViolations()"},
                {"id": "I-012", "name": "View Cost Analytics", "dashboard_screen": "Cost Dashboard", "shared_service": "CostService.getAnalytics()"},
                {"id": "I-015", "name": "View Delivery Exceptions", "dashboard_screen": "Exception Monitor", "shared_service": "ExceptionService.getExceptions()"},
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
            "personas": [
                {"name": "Maria Santos", "role": "Fleet Dispatcher", "primary_interface": "dashboard"},
                {"name": "James Park", "role": "Fleet Manager", "primary_interface": "dashboard"},
                {"name": "David Kim", "role": "Compliance Officer", "primary_interface": "dashboard"},
                {"name": "Lisa Chen", "role": "Operations Director", "primary_interface": "dashboard"},
            ],
            "quality_nfrs": [
                "Dashboard page load < 2s (P95)",
                "Real-time updates < 5s latency",
                "WCAG 2.1 AA compliance required",
                "Support 50 concurrent dashboard users",
                "Graceful degradation on real-time connection loss",
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

    # ── Section checks ──────────────────────────────────────────────
    sections = [
        "Design Principles",
        "Screen Inventory",
        "Screen Specification",
        "Cross-Interface Handoff",
        "Component Library",
        "Responsive Behavior",
        "Real-Time Update Registry",
    ]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")

    # ── Screen IDs ──────────────────────────────────────────────────
    scr_ids = set(re.findall(r"SCR-\d{3}", output))
    print(f"Screen IDs: {len(scr_ids)} unique SCR-NNN  {sorted(scr_ids)}")

    # ── Interaction ID references ───────────────────────────────────
    i_ids = set(re.findall(r"I-\d{3}", output))
    expected_i_ids = {"I-001", "I-002", "I-005", "I-008", "I-012", "I-015"}
    print(f"Interaction IDs referenced: {len(i_ids)} unique I-NNN")
    i_missing = expected_i_ids - i_ids
    if i_missing:
        print(f"  WARNING: Missing expected I-NNN refs: {sorted(i_missing)}")
    else:
        print(f"  All expected I-NNN IDs present")

    # ── Data shape references ───────────────────────────────────────
    shape_names = ["FleetStatus", "RouteAssignment", "HOSViolation", "DeliveryException"]
    shapes_found = [s for s in shape_names if s in output]
    shapes_missing = [s for s in shape_names if s not in output]
    print(f"Data shapes referenced: {len(shapes_found)}/{len(shape_names)}")
    if shapes_missing:
        print(f"  Missing shapes: {shapes_missing}")

    # ── ASCII wireframe detection ───────────────────────────────────
    wireframe_markers = re.findall(r"\+[-=]+\+", output)
    print(f"ASCII wireframe markers: {len(wireframe_markers)} border lines found")
    if len(wireframe_markers) < 4:
        print(f"  WARNING: Expected more wireframe art (at least 4 border lines)")

    # ── Accessibility mentions ──────────────────────────────────────
    a11y_terms = ["wcag", "aria-label", "aria-live", "screen reader",
                  "keyboard", "contrast", "focus"]
    a11y_found = [t for t in a11y_terms if t.lower() in output.lower()]
    print(f"Accessibility terms: {len(a11y_found)}/{len(a11y_terms)}  {a11y_found}")

    # ── Component library ───────────────────────────────────────────
    components = ["StatusBadge", "DataTable", "MetricCard", "DetailPanel", "AlertBanner"]
    comp_found = [c for c in components if c in output]
    comp_missing = [c for c in components if c not in output]
    print(f"Components defined: {len(comp_found)}/{len(components)}")
    if comp_missing:
        print(f"  Missing components: {comp_missing}")

    # ── Real-time registry ──────────────────────────────────────────
    rt_strategies = ["SSE", "WebSocket", "Polling"]
    rt_found = [s for s in rt_strategies if s.lower() in output.lower()]
    print(f"Real-time strategies mentioned: {rt_found}")

    # ── Mandatory principles check ──────────────────────────────────
    has_shared_shapes = "shared data shape" in output.lower()
    has_operator_first = "operator-first" in output.lower() or "operator first" in output.lower()
    print(f"Shared Data Shapes principle: {has_shared_shapes}")
    print(f"Operator-First principle: {has_operator_first}")

    # ── States check ────────────────────────────────────────────────
    states = ["loading", "empty", "error", "populated"]
    states_found = [s for s in states if s.lower() in output.lower()]
    print(f"Screen states mentioned: {len(states_found)}/{len(states)}  {states_found}")

    # ── Persona coverage ────────────────────────────────────────────
    personas = ["Maria Santos", "James Park", "David Kim", "Lisa Chen"]
    personas_found = [p for p in personas if p in output]
    print(f"Personas referenced: {len(personas_found)}/{len(personas)}")
    if len(personas_found) < len(personas):
        personas_missing = [p for p in personas if p not in output]
        print(f"  Missing personas: {personas_missing}")

    print()
    print("=== FIRST 2500 CHARS ===")
    print(output[:2500])


if __name__ == "__main__":
    asyncio.run(main())
