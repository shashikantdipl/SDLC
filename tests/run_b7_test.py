"""Live test of B7-dependency-auditor."""

import asyncio
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from sdk.base_agent import BaseAgent
from pathlib import Path


async def main():
    agent = BaseAgent(agent_dir=Path("agents/build/B7-dependency-auditor"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "agentic-sdlc-platform",
            "dependencies": [
                {"name": "asyncpg", "version": "0.29.0", "type": "runtime"},
                {"name": "aiohttp", "version": "3.9.0", "type": "runtime"},
                {"name": "structlog", "version": "24.1.0", "type": "runtime"},
                {"name": "pydantic", "version": "2.6.0", "type": "runtime"},
                {"name": "anthropic", "version": "0.40.0", "type": "runtime"},
                {"name": "mcp", "version": "1.0.0", "type": "runtime"},
                {"name": "streamlit", "version": "1.31.0", "type": "runtime"},
                {"name": "python-jose", "version": "3.3.0", "type": "runtime"},
                {"name": "httpx", "version": "0.27.0", "type": "runtime"},
                {"name": "pytest", "version": "8.0.0", "type": "dev"},
                {"name": "ruff", "version": "0.3.0", "type": "dev"},
                {"name": "mypy", "version": "1.8.0", "type": "dev"},
            ],
            "lock_file_deps": [],
            "license_policy": {
                "allowed": ["MIT", "Apache-2.0", "BSD"],
                "forbidden": ["GPL", "AGPL"],
            },
            "vulnerability_slas": {
                "critical_hours": 24,
                "high_days": 7,
                "medium_days": 30,
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
            data = json.loads(json_str)

            summary = data.get("audit_summary", {})
            vulns = data.get("vulnerabilities", [])
            license_audit = data.get("license_audit", [])
            freshness = data.get("freshness_check", [])
            sbom = data.get("sbom_inventory", [])
            recs = data.get("recommendations", [])

            # --- Check audit_summary ---
            print("=== AUDIT SUMMARY ===")
            has_summary = bool(summary)
            total_pkg = summary.get("total_packages", 0)
            runtime_count = summary.get("runtime", 0)
            dev_count = summary.get("dev_only", 0)
            vuln_counts = summary.get("vulnerabilities", {})
            license_viol = summary.get("license_violations", 0)
            outdated_count = summary.get("outdated_packages", 0)
            overall_risk = summary.get("overall_risk", "")
            print(f"  Total packages:      {total_pkg}")
            print(f"  Runtime:             {runtime_count}")
            print(f"  Dev only:            {dev_count}")
            print(f"  Vulnerabilities:     {vuln_counts}")
            print(f"  License violations:  {license_viol}")
            print(f"  Outdated packages:   {outdated_count}")
            print(f"  Overall risk:        {overall_risk}")
            has_total = total_pkg >= 12
            has_risk = overall_risk in ("low", "medium", "high", "critical")
            print(f"  [{'PASS' if has_summary else 'FAIL'}] audit_summary present")
            print(f"  [{'PASS' if has_total else 'FAIL'}] Total packages >= 12 ({total_pkg})")
            print(f"  [{'PASS' if has_risk else 'FAIL'}] overall_risk is valid ({overall_risk})")

            # --- Check vulnerabilities ---
            print(f"\n=== VULNERABILITIES ({len(vulns)}) ===")
            for v in vulns:
                print(f"  {v.get('package')} {v.get('version')} | {v.get('cve')} | {v.get('severity')} | fix: {v.get('fix_version')}")
            # Vulnerabilities may or may not be present depending on LLM knowledge; just report

            # --- Check license_audit ---
            print(f"\n=== LICENSE AUDIT ({len(license_audit)}) ===")
            license_pkgs = set()
            for la in license_audit:
                pkg = la.get("package", "")
                license_pkgs.add(pkg)
                status = la.get("status", "")
                lic = la.get("license", "")
                print(f"  {pkg} {la.get('version','')} | {lic} | {status}")

            expected_pkgs = {
                "asyncpg", "aiohttp", "structlog", "pydantic", "anthropic",
                "mcp", "streamlit", "python-jose", "httpx",
                "pytest", "ruff", "mypy",
            }
            covered = expected_pkgs.issubset(license_pkgs)
            has_all_licenses = len(license_audit) >= 12
            print(f"  [{'PASS' if has_all_licenses else 'FAIL'}] License audit covers all 12 packages ({len(license_audit)})")
            print(f"  [{'PASS' if covered else 'FAIL'}] All expected packages present (missing: {expected_pkgs - license_pkgs})")

            # --- Check freshness_check ---
            print(f"\n=== FRESHNESS CHECK ({len(freshness)}) ===")
            has_freshness = len(freshness) >= 1
            for fc in freshness[:6]:
                print(f"  {fc.get('package')} | current: {fc.get('current')} | latest: {fc.get('latest')} | status: {fc.get('status')} | risk: {fc.get('upgrade_risk')}")
            if len(freshness) > 6:
                print(f"  ... and {len(freshness) - 6} more")
            print(f"  [{'PASS' if has_freshness else 'FAIL'}] Freshness check present ({len(freshness)} entries)")

            # --- Check sbom_inventory ---
            print(f"\n=== SBOM INVENTORY ({len(sbom)}) ===")
            has_sbom = len(sbom) >= 12
            sbom_names = {s.get("name") for s in sbom}
            for s in sbom[:6]:
                print(f"  {s.get('name')} {s.get('version')} | {s.get('license')} | {s.get('type')} | direct={s.get('direct')}")
            if len(sbom) > 6:
                print(f"  ... and {len(sbom) - 6} more")
            print(f"  [{'PASS' if has_sbom else 'FAIL'}] SBOM has 12+ packages ({len(sbom)})")

            # --- Check recommendations ---
            print(f"\n=== RECOMMENDATIONS ({len(recs)}) ===")
            has_recs = len(recs) >= 1
            priorities_sorted = True
            prev_priority = 0
            for r in recs:
                p = r.get("priority", 0)
                if p < prev_priority:
                    priorities_sorted = False
                prev_priority = p
                print(f"  P{p}: {r.get('action')} | {r.get('reason')} | effort: {r.get('effort')}")
            print(f"  [{'PASS' if has_recs else 'WARN'}] Recommendations present ({len(recs)})")
            print(f"  [{'PASS' if priorities_sorted else 'FAIL'}] Recommendations sorted by priority")

            # --- Summary ---
            print("\n" + "=" * 50)
            print("=== SUMMARY ===")
            checks = {
                "audit_summary present": has_summary,
                "Total packages >= 12": has_total,
                "overall_risk assessed": has_risk,
                "License audit covers all packages": has_all_licenses,
                "All expected packages in license audit": covered,
                "Freshness check present": has_freshness,
                "SBOM has 12+ packages": has_sbom,
                "Recommendations sorted by priority": priorities_sorted,
            }
            passed = sum(checks.values())
            total = len(checks)
            for name, ok in checks.items():
                print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
            print(f"\n  Result: {passed}/{total} checks passed")
            if passed == total:
                print("  ALL CHECKS PASSED")
            else:
                print(f"  {total - passed} check(s) failed")

        else:
            print("WARNING: Could not extract JSON from output")
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse error: {e}")

    print()
    print("=== FIRST 3000 CHARS OF RAW OUTPUT ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
