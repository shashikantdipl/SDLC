"""Live test of D17-migration-planner — Migration Plan."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D17-migration-planner"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps",
            "source_systems": [
                {
                    "name": "AS/400 Fleet Management",
                    "technology": "IBM AS/400 RPG + DB2/400",
                    "data_volume": "2.1M records",
                    "pain_points": [
                        "EBCDIC encoding — no Unicode support",
                        "Green-screen UI — no API access",
                        "Batch-only processing — no real-time",
                        "Single-threaded RPG programs",
                    ],
                },
                {
                    "name": "Samsara GPS Telematics",
                    "technology": "Samsara REST API v1",
                    "data_volume": "500K GPS points/day",
                    "pain_points": [
                        "API rate limit 100 req/min",
                        "Data exported as CSV — no streaming",
                        "GPS coordinates in proprietary format",
                        "No historical data beyond 90 days",
                    ],
                },
                {
                    "name": "Excel Maintenance Tracker",
                    "technology": "Microsoft Excel 2019 (.xlsx)",
                    "data_volume": "15K rows across 12 sheets",
                    "pain_points": [
                        "No referential integrity",
                        "Inconsistent date formats (MM/DD/YYYY and YYYY-MM-DD mixed)",
                        "Duplicate vehicle entries",
                        "Manual data entry errors",
                    ],
                },
            ],
            "target_tables": [
                "vehicles",
                "drivers",
                "trips",
                "maintenance_records",
                "gps_events",
                "alerts",
            ],
            "data_entities": [
                {
                    "name": "Vehicle",
                    "source": "AS/400 Fleet Management",
                    "sensitivity": "internal",
                    "volume": "12,000 records",
                },
                {
                    "name": "Driver",
                    "source": "AS/400 Fleet Management",
                    "sensitivity": "PII",
                    "volume": "8,500 records",
                },
                {
                    "name": "Trip",
                    "source": "AS/400 Fleet Management",
                    "sensitivity": "internal",
                    "volume": "2.1M records",
                },
                {
                    "name": "Maintenance Record",
                    "source": "Excel Maintenance Tracker",
                    "sensitivity": "internal",
                    "volume": "15,000 records",
                },
                {
                    "name": "GPS Event",
                    "source": "Samsara GPS Telematics",
                    "sensitivity": "internal",
                    "volume": "45M records (90 days)",
                },
                {
                    "name": "Alert",
                    "source": "Samsara GPS Telematics",
                    "sensitivity": "internal",
                    "volume": "250,000 records",
                },
            ],
            "constraints": {
                "max_downtime": "4 hours",
                "timeline": "8 weeks",
                "compliance": ["SOC 2 Type II audit trail", "PII encryption at rest"],
            },
            "security_classification": [
                "PII fields encrypted at rest (AES-256)",
                "Driver SSN and license masked in non-production",
                "Audit trail for all data mutations",
            ],
        },
        project_id="fleetops-017",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == All 10 sections present ===============================================
    sections = [
        "Source System Profile",
        "Migration Approach",
        "Source-to-Target Mapping",
        "Data Volume",
        "Data Validation Plan",
        "Cutover Runbook",
        "Rollback Plan",
        "Parallel Run Strategy",
        "Dry Run Schedule",
        "Legacy Decommission",
    ]
    found_sections = []
    missing_sections = []
    for s in sections:
        if s.lower() in output.lower():
            found_sections.append(s)
        else:
            missing_sections.append(s)
    print(f"Sections: {len(found_sections)}/{len(sections)}")
    if missing_sections:
        print(f"  MISSING: {missing_sections}")
    else:
        print(f"  PASS: All 10 sections present")

    # == Source-to-Target mapping table =========================================
    mapping_keywords = ["source table", "source column", "target table", "target column", "transformation"]
    mk_found = [k for k in mapping_keywords if k.lower() in output.lower()]
    has_mapping_table = len(re.findall(r"^\|.*\|$", output, re.MULTILINE)) >= 6
    print(f"Mapping table keywords: {len(mk_found)}/{len(mapping_keywords)} ({mk_found})")
    print(f"  Tables present (6+ rows): {'PASS' if has_mapping_table else 'FAIL'}")

    # == All 6 target tables referenced ========================================
    target_tables = ["vehicles", "drivers", "trips", "maintenance_records", "gps_events", "alerts"]
    tt_found = [t for t in target_tables if t.lower() in output.lower()]
    tt_missing = [t for t in target_tables if t.lower() not in output.lower()]
    print(f"Target tables referenced: {len(tt_found)}/{len(target_tables)}")
    if tt_missing:
        print(f"  MISSING: {tt_missing}")
    else:
        print(f"  PASS: All 6 target tables referenced in mapping")

    # == All 3 source systems referenced =======================================
    source_systems = ["as/400", "samsara", "excel"]
    ss_found = [s for s in source_systems if s.lower() in output.lower()]
    ss_missing = [s for s in source_systems if s.lower() not in output.lower()]
    print(f"Source systems referenced: {len(ss_found)}/{len(source_systems)}")
    if ss_missing:
        print(f"  MISSING: {ss_missing}")
    else:
        print(f"  PASS: All 3 source systems referenced")

    # == Cutover time stamps ===================================================
    cutover_timestamps = ["T+0", "T+15", "T+30", "T+45", "T+1h", "T+2h"]
    ct_found = []
    ct_missing = []
    for ts in cutover_timestamps:
        # Flexible matching: T+0, T+15min, T+15 min, T+15m, etc.
        pattern = re.escape(ts).replace(r"\+", r"\+\s*")
        if re.search(pattern, output, re.IGNORECASE):
            ct_found.append(ts)
        else:
            ct_missing.append(ts)
    print(f"Cutover timestamps: {len(ct_found)}/{len(cutover_timestamps)}")
    if ct_missing:
        print(f"  MISSING: {ct_missing}")
    else:
        print(f"  PASS: All cutover timestamps present (T+0 through T+2h)")

    # == Rollback criteria (binary/measurable) =================================
    rollback_terms = ["rollback trigger", "threshold", "row count", "constraint", "encoding"]
    rb_found = [t for t in rollback_terms if t.lower() in output.lower()]
    rb_missing = [t for t in rollback_terms if t.lower() not in output.lower()]
    has_rollback_section = "rollback" in output.lower()
    print(f"Rollback section: {'PASS' if has_rollback_section else 'FAIL'}")
    print(f"  Rollback criteria terms: {len(rb_found)}/{len(rollback_terms)}")
    if rb_missing:
        print(f"  MISSING: {rb_missing}")
    else:
        print(f"  PASS: All rollback criteria terms present")

    # == Validation levels (3 levels) ==========================================
    validation_levels = ["row count", "constraint", "business rule"]
    vl_found = [v for v in validation_levels if v.lower() in output.lower()]
    vl_missing = [v for v in validation_levels if v.lower() not in output.lower()]
    print(f"Validation levels: {len(vl_found)}/{len(validation_levels)}")
    if vl_missing:
        print(f"  MISSING: {vl_missing}")
    else:
        print(f"  PASS: All 3 validation levels present")

    # == 3 interfaces validated ================================================
    interfaces = ["mcp", "rest", "dashboard"]
    if_found = [i for i in interfaces if i.lower() in output.lower()]
    if_missing = [i for i in interfaces if i.lower() not in output.lower()]
    print(f"Interfaces validated: {len(if_found)}/{len(interfaces)}")
    if if_missing:
        print(f"  MISSING: {if_missing}")
    else:
        print(f"  PASS: All 3 interfaces (MCP, REST, Dashboard) validated")

    # == Dry run schedule ======================================================
    dry_run_found = set()
    for i in range(1, 5):
        patterns = [
            rf"Dry\s+Run\s+#{i}",
            rf"Dry\s+Run\s+{i}",
            rf"\|\s*{i}\s*\|",
        ]
        for pattern in patterns:
            if re.search(pattern, output, re.IGNORECASE):
                dry_run_found.add(i)
                break
    print(f"Dry runs scheduled: {len(dry_run_found)}/3")
    if len(dry_run_found) >= 3:
        print(f"  PASS: At least 3 dry runs scheduled")
    else:
        print(f"  WARNING: Expected 3+ dry runs, found {sorted(dry_run_found)}")

    # == Decommission plan =====================================================
    decom_terms = ["decommission", "archival", "dns", "retention"]
    dc_found = [t for t in decom_terms if t.lower() in output.lower()]
    dc_missing = [t for t in decom_terms if t.lower() not in output.lower()]
    print(f"Decommission terms: {len(dc_found)}/{len(decom_terms)}")
    if dc_missing:
        print(f"  MISSING: {dc_missing}")
    else:
        print(f"  PASS: All decommission terms present (decommission, archival, DNS, retention)")

    # == Encoding conversion mentioned =========================================
    has_ebcdic = "ebcdic" in output.lower()
    has_utf8 = "utf-8" in output.lower() or "utf8" in output.lower()
    has_encoding_conversion = has_ebcdic and has_utf8
    print(f"Encoding conversion (EBCDIC to UTF-8): {'PASS' if has_encoding_conversion else 'FAIL'}")
    if not has_ebcdic:
        print(f"  MISSING: EBCDIC not mentioned")
    if not has_utf8:
        print(f"  MISSING: UTF-8 not mentioned")

    # == PII / security handling ===============================================
    security_terms = ["pii", "encrypt", "mask", "audit"]
    sec_found = [t for t in security_terms if t.lower() in output.lower()]
    sec_missing = [t for t in security_terms if t.lower() not in output.lower()]
    print(f"Security terms: {len(sec_found)}/{len(security_terms)}")
    if sec_missing:
        print(f"  MISSING: {sec_missing}")
    else:
        print(f"  PASS: All security terms present (PII, encrypt, mask, audit)")

    # == Parallel run cutover criteria =========================================
    has_parallel_criteria = (
        "cutover criteria" in output.lower()
        or "cut-over criteria" in output.lower()
        or ("parallel" in output.lower() and "criteria" in output.lower())
    )
    print(f"Parallel run cutover criteria: {'PASS' if has_parallel_criteria else 'FAIL'}")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
