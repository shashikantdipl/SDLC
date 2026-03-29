"""Live test of D10-data-model-designer — Database Schema Design."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D10-data-model-designer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Data Model",
            "data_entities": [
                {
                    "name": "Vehicle",
                    "source": "Fleet registration system",
                    "sensitivity": "Internal",
                    "estimated_volume": "5K rows total, 50 new/month",
                },
                {
                    "name": "Driver",
                    "source": "HR system import",
                    "sensitivity": "Confidential",
                    "estimated_volume": "2K rows total, 20 new/month",
                },
                {
                    "name": "Route",
                    "source": "Dispatch planning module",
                    "sensitivity": "Internal",
                    "estimated_volume": "10K rows/month",
                },
                {
                    "name": "Delivery",
                    "source": "Customer order system",
                    "sensitivity": "Internal",
                    "estimated_volume": "50K rows/month",
                },
                {
                    "name": "GPSPosition",
                    "source": "Vehicle telematics (IoT)",
                    "sensitivity": "Internal",
                    "estimated_volume": "5M rows/month",
                },
                {
                    "name": "HOSRecord",
                    "source": "ELD device integration",
                    "sensitivity": "Restricted",
                    "estimated_volume": "100K rows/month",
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
            "mcp_query_patterns": [
                "SELECT * FROM vehicles WHERE project_id=$1 AND status=$2",
                "SELECT * FROM hos_records WHERE driver_id=$1 AND recorded_at > $2 ORDER BY recorded_at DESC",
                "SELECT * FROM deliveries WHERE route_id=$1 AND status != 'completed'",
            ],
            "dashboard_query_patterns": [
                "SELECT * FROM hos_violations WHERE project_id=$1 ORDER BY detected_at DESC LIMIT 50",
                "SELECT * FROM delivery_exceptions WHERE project_id=$1 AND severity='critical' ORDER BY reported_at DESC",
                "SELECT v.*, gp.latitude, gp.longitude FROM vehicles v JOIN gps_positions gp ON v.id=gp.vehicle_id WHERE v.project_id=$1 AND v.status='active'",
            ],
            "components": [
                {"name": "Primary Database", "technology": "PostgreSQL 15"},
                {"name": "Cache Layer", "technology": "Redis 7"},
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
        "Overview",
        "Data Shape to Table Mapping",
        "Schema DDL",
        "Indexes",
        "Row-Level Security",
        "Query Pattern Registry",
        "Capacity Estimates",
        "Migration Strategy",
        "Supplementary Data Stores",
    ]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")
    else:
        print(f"  All 9 sections present")

    # ── CREATE TABLE detection ──────────────────────────────────────
    create_tables = re.findall(r"CREATE TABLE\s+(\w+)", output, re.IGNORECASE)
    print(f"CREATE TABLE statements: {len(create_tables)}  {create_tables}")
    if len(create_tables) < 4:
        print(f"  WARNING: Expected at least 4 CREATE TABLE statements")

    # ── CREATE INDEX detection ──────────────────────────────────────
    create_indexes = re.findall(r"CREATE INDEX\s+(\w+)", output, re.IGNORECASE)
    print(f"CREATE INDEX statements: {len(create_indexes)}  {create_indexes}")
    if len(create_indexes) < 10:
        print(f"  WARNING: Expected at least 10 indexes (got {len(create_indexes)})")

    # ── RLS detection ───────────────────────────────────────────────
    rls_mentions = len(re.findall(r"ROW LEVEL SECURITY", output, re.IGNORECASE))
    rls_policies = re.findall(r"CREATE POLICY\s+(\w+)", output, re.IGNORECASE)
    print(f"RLS: ENABLE ROW LEVEL SECURITY mentioned {rls_mentions} times")
    print(f"RLS policies: {len(rls_policies)}  {rls_policies}")
    if rls_mentions < 1:
        print(f"  WARNING: No RLS found in output")

    # ── Data shape mapping ──────────────────────────────────────────
    shape_names = ["FleetStatus", "RouteAssignment", "HOSViolation", "DeliveryException"]
    shapes_found = [s for s in shape_names if s in output]
    shapes_missing = [s for s in shape_names if s not in output]
    print(f"Data shapes referenced: {len(shapes_found)}/{len(shape_names)}")
    if shapes_missing:
        print(f"  Missing shapes: {shapes_missing}")
    else:
        print(f"  All data shapes mapped")

    # ── Migration UP/DOWN pattern ───────────────────────────────────
    has_up = bool(re.search(r"--\s*UP", output, re.IGNORECASE))
    has_down = bool(re.search(r"--\s*DOWN", output, re.IGNORECASE))
    has_drop = "DROP TABLE" in output.upper()
    print(f"Migration UP marker: {has_up}")
    print(f"Migration DOWN marker: {has_down}")
    print(f"DROP TABLE present: {has_drop}")
    if not (has_up and has_down):
        print(f"  WARNING: Missing UP/DOWN migration markers")

    # ── Capacity estimates ──────────────────────────────────────────
    capacity_terms = ["rows", "growth", "archival", "partition"]
    cap_found = [t for t in capacity_terms if t.lower() in output.lower()]
    print(f"Capacity terms: {len(cap_found)}/{len(capacity_terms)}  {cap_found}")

    # ── Supplementary stores ────────────────────────────────────────
    supp_stores = ["filesystem", "yaml", "jsonl", "in-memory", "redis"]
    supp_found = [s for s in supp_stores if s.lower() in output.lower()]
    print(f"Supplementary stores mentioned: {len(supp_found)}  {supp_found}")

    # ── Audit columns ──────────────────────────────────────────────
    has_created_at = "created_at" in output
    has_updated_at = "updated_at" in output
    print(f"Audit columns: created_at={has_created_at}, updated_at={has_updated_at}")

    # ── Encryption markers ──────────────────────────────────────────
    encryption_terms = ["pgcrypto", "encrypt", "confidential", "restricted"]
    enc_found = [t for t in encryption_terms if t.lower() in output.lower()]
    print(f"Encryption/sensitivity terms: {len(enc_found)}  {enc_found}")

    # ── Query pattern registry size ─────────────────────────────────
    registry_rows = re.findall(r"\|\s*\d+\s*\|", output)
    print(f"Query pattern registry rows (numbered): {len(registry_rows)}")
    if len(registry_rows) < 15:
        print(f"  WARNING: Expected at least 15 query patterns in registry")

    # ── Entity coverage ─────────────────────────────────────────────
    entities = ["Vehicle", "Driver", "Route", "Delivery", "GPSPosition", "HOSRecord"]
    ent_found = [e for e in entities if e.lower() in output.lower()]
    print(f"Entity coverage: {len(ent_found)}/{len(entities)}  {ent_found}")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
