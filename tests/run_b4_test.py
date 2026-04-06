"""Live test of B4-performance-analyzer."""

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

# Code with deliberate performance issues
SLOW_CODE = '''
"""Fleet status service — queries vehicle positions and status."""
import time
import json
from pathlib import Path

async def get_fleet_overview(db, project_id: str) -> dict:
    """Get overview of all vehicles in the fleet."""
    # N+1: fetches each vehicle separately
    vehicle_ids = await db.fetch("SELECT vehicle_id FROM vehicles WHERE project_id = $1", project_id)

    vehicles = []
    for row in vehicle_ids:
        vehicle = await db.fetchrow(
            "SELECT * FROM vehicles WHERE vehicle_id = $1", row["vehicle_id"]
        )
        # Another N+1: fetches latest GPS for each vehicle
        gps = await db.fetchrow(
            "SELECT * FROM gps_positions WHERE vehicle_id = $1 ORDER BY recorded_at DESC",
            row["vehicle_id"]
        )
        # Blocking sync file read inside async function
        config = json.loads(Path("config/fleet.json").read_text())
        vehicles.append({**dict(vehicle), "gps": dict(gps) if gps else None, "config": config})

    # Unbounded query — no LIMIT
    all_deliveries = await db.fetch(
        "SELECT * FROM deliveries WHERE project_id = $1", project_id
    )

    # Expensive computation repeated every call
    stats = {}
    for d in all_deliveries:
        agent = d["driver_id"]
        if agent not in stats:
            stats[agent] = {"count": 0, "total_cost": 0}
        stats[agent]["count"] += 1
        stats[agent]["total_cost"] += float(d["cost_usd"])

    return {
        "vehicles": vehicles,
        "delivery_count": len(all_deliveries),
        "driver_stats": stats,
    }

async def search_vehicles(db, query: str) -> list:
    """Search vehicles by name — no index on name column."""
    # Missing index + LIKE without index
    rows = await db.fetch(
        f"SELECT * FROM vehicles WHERE name ILIKE '%{query}%'"  # Also SQL injection
    )
    return [dict(r) for r in rows]
'''


async def main():
    agent = BaseAgent(agent_dir=Path("agents/build/B4-performance-analyzer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "file_path": "services/fleet_service.py",
            "code_content": SLOW_CODE,
            "language": "python",
            "performance_nfrs": [
                "Q-001: MCP tool read p95 < 500ms",
                "Q-004: REST API p95 < 500ms",
                "Q-008: Shared service call p95 < 200ms",
            ],
            "database_schema": {
                "tables": ["vehicles", "gps_positions", "deliveries", "drivers"],
                "indexes": [
                    "idx_vehicles_project_status ON vehicles(project_id, status)",
                    "idx_gps_vehicle_recorded ON gps_positions(vehicle_id, recorded_at DESC)",
                    "idx_deliveries_project ON deliveries(project_id)",
                ],
            },
            "expected_load": {
                "requests_per_second": 50,
                "concurrent_users": 20,
                "data_volume": "200 vehicles, 500 deliveries/day",
            },
        },
        project_id="test-001",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    try:
        if "```json" in output:
            json_str = output.split("```json")[1].split("```")[0].strip()
        elif output.strip().startswith("{"):
            json_str = output.strip()
        else:
            json_str = None

        if json_str:
            analysis = json.loads(json_str)

            summary = analysis.get("analysis_summary", {})
            print(f"Risk Level: {summary.get('risk_level', 'unknown')}")
            print(f"Bottlenecks: {summary.get('bottleneck_count', 0)}")
            print(f"Optimization potential: {summary.get('optimization_potential', 'unknown')}")

            findings = analysis.get("findings", [])
            print(f"\nFindings: {len(findings)} total")
            by_cat = {}
            for f in findings:
                c = f.get("category", "?")
                by_cat[c] = by_cat.get(c, 0) + 1
            for c, n in sorted(by_cat.items()):
                print(f"  {c}: {n}")

            all_text = " ".join(f.get("title", "") + " " + f.get("description", "") for f in findings).lower()
            checks = {
                "N+1 query detected": "n+1" in all_text or "n plus" in all_text or "loop" in all_text and "query" in all_text,
                "Unbounded query (no LIMIT)": "unbounded" in all_text or "no limit" in all_text or "limit" in all_text,
                "Blocking I/O in async": "blocking" in all_text or "sync" in all_text and "async" in all_text,
                "Missing index / ILIKE": "index" in all_text or "ilike" in all_text,
                "Config read per request": "config" in all_text or "file" in all_text and "every" in all_text,
            }

            print("\nKey issues detected:")
            for check, found in checks.items():
                print(f"  {'FOUND' if found else 'MISSED'}: {check}")

            recs = analysis.get("recommendations", [])
            print(f"\nRecommendations: {len(recs)}")

        else:
            print("WARNING: Could not extract JSON")
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse error: {e}")

    print()
    print("=== FIRST 2000 CHARS ===")
    print(output[:2000])


if __name__ == "__main__":
    asyncio.run(main())
