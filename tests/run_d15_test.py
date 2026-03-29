"""Live test of D15-enforcement-scaffolder — .claude/ Enforcement Layer."""

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
    agent = BaseAgent(agent_dir=Path("agents/design/D15-enforcement-scaffolder"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps",
            "coding_rules": {
                "languages": ["Python 3.12", "TypeScript 5.x"],
                "forbidden_patterns": [
                    "Business logic in MCP handlers",
                    "Direct DB access from dashboard",
                    "Hardcoded secrets",
                    "print() in production code",
                    "Blocking I/O in async handlers",
                ],
                "implementation_patterns": [
                    "Shared Service",
                    "MCP Tool",
                    "API Route",
                    "Dashboard View",
                    "Agent",
                    "Migration",
                    "LLM Provider",
                ],
            },
            "architecture": {
                "mcp_servers": ["fleet", "route", "compliance"],
                "services": [
                    "fleet_service",
                    "route_service",
                    "compliance_service",
                    "delivery_service",
                    "driver_service",
                    "maintenance_service",
                    "analytics_service",
                    "notification_service",
                ],
                "api_routes": "api/routes/",
                "dashboard": "dashboard/",
                "agents_dir": "agents/",
            },
            "quality_thresholds": {
                "services": 90,
                "handlers": 80,
                "dashboard": 70,
            },
            "security_rules": [
                "No hardcoded secrets — use environment variables",
                "JWT validation on all REST endpoints",
                "Input sanitization on all user inputs",
                "SQL parameterization — no string concatenation in queries",
            ],
        },
        project_id="fleetops-015",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # == All 6 sections present ================================================
    sections = [
        "Directory Structure",
        "settings.json",
        "Rule Files",
        "Skill Files",
        ".cursorrules",
        "Enforcement Summary",
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
        print(f"  PASS: All 6 sections present")

    # == settings.json structure found =========================================
    has_settings_json = '"rules"' in output and '"skills"' in output
    has_permissions = '"permissions"' in output or '"allow"' in output
    has_hooks = "PreToolUse" in output or "PostToolUse" in output or "hook" in output.lower()
    print(f"settings.json structure: {'PASS' if has_settings_json else 'FAIL'}")
    print(f"  Permissions block: {'PASS' if has_permissions else 'FAIL'}")
    print(f"  Hook definitions: {'PASS' if has_hooks else 'FAIL'}")

    # == 11 rule files mentioned ===============================================
    rule_files = [
        "01-python",
        "02-shared-services",
        "03-mcp-servers",
        "04-api-routes",
        "05-dashboard",
        "06-agents",
        "07-schemas",
        "08-migrations",
        "09-tests",
        "10-prompt-versioning",
        "11-api-governance",
    ]
    rf_found = [r for r in rule_files if r in output]
    rf_missing = [r for r in rule_files if r not in output]
    print(f"Rule files mentioned: {len(rf_found)}/{len(rule_files)}")
    if rf_missing:
        print(f"  MISSING: {rf_missing}")
    else:
        print(f"  PASS: All 11 rule files mentioned")

    # == 8 skill files mentioned ===============================================
    skill_files = [
        "new-interaction",
        "new-mcp-tool",
        "new-api-route",
        "new-dashboard-view",
        "new-agent",
        "new-test",
        "new-migration",
        "new-provider",
    ]
    sf_found = [s for s in skill_files if s in output]
    sf_missing = [s for s in skill_files if s not in output]
    print(f"Skill files mentioned: {len(sf_found)}/{len(skill_files)}")
    if sf_missing:
        print(f"  MISSING: {sf_missing}")
    else:
        print(f"  PASS: All 8 skill files mentioned")

    # == Shared-services rule present (THE KEY RULE) ===========================
    shared_services_present = "shared-services" in output.lower() or "shared_services" in output.lower()
    shared_services_detailed = (
        "thin wrapper" in output.lower()
        and "business logic" in output.lower()
        and "services/" in output
    )
    print(f"Shared-services rule present: {'PASS' if shared_services_present else 'FAIL'}")
    print(f"  Detailed enforcement (thin wrapper + business logic + services/): {'PASS' if shared_services_detailed else 'FAIL'}")

    # == New-interaction skill present (THE KEY SKILL) =========================
    new_interaction_present = "new-interaction" in output
    # Check if it mentions creating multiple files (9 files)
    nine_files_pattern = re.search(r"9\s*files?|nine\s*files?", output.lower())
    has_service_template = "service" in output.lower() and "template" in output.lower() or "_service.py" in output
    print(f"New-interaction skill present: {'PASS' if new_interaction_present else 'FAIL'}")
    print(f"  9-file creation mentioned: {'PASS' if nine_files_pattern else 'FAIL'}")
    print(f"  Service template referenced: {'PASS' if has_service_template else 'FAIL'}")

    # == Prompt-versioning rule (v2) ===========================================
    prompt_versioning = "prompt-versioning" in output.lower() or "prompt versioning" in output.lower()
    semver_mentioned = "semver" in output.lower() or "semantic version" in output.lower()
    golden_tests = "golden test" in output.lower() or "golden_test" in output.lower()
    quality_regression = "5%" in output or "regression" in output.lower()
    print(f"Prompt-versioning rule (v2): {'PASS' if prompt_versioning else 'FAIL'}")
    print(f"  SemVer mentioned: {'PASS' if semver_mentioned else 'FAIL'}")
    print(f"  Golden tests gate: {'PASS' if golden_tests else 'FAIL'}")
    print(f"  Quality regression threshold: {'PASS' if quality_regression else 'FAIL'}")

    # == API-governance rule (v2) ==============================================
    api_governance = "api-governance" in output.lower() or "api governance" in output.lower()
    standard_envelope = "envelope" in output.lower()
    deprecation_policy = "deprecat" in output.lower()
    rate_limits = "rate limit" in output.lower() or "rate_limit" in output.lower()
    print(f"API-governance rule (v2): {'PASS' if api_governance else 'FAIL'}")
    print(f"  Standard envelope: {'PASS' if standard_envelope else 'FAIL'}")
    print(f"  Deprecation policy: {'PASS' if deprecation_policy else 'FAIL'}")
    print(f"  Rate limits: {'PASS' if rate_limits else 'FAIL'}")

    # == .cursorrules present ==================================================
    cursorrules_present = ".cursorrules" in output
    # Check for 7 invariants (numbered 1-7)
    invariant_count = len(re.findall(r"^\s*[1-7]\.", output, re.MULTILINE))
    print(f".cursorrules present: {'PASS' if cursorrules_present else 'FAIL'}")
    print(f"  Numbered invariants found: {invariant_count} (expect >= 7)")

    # == Enforcement summary table =============================================
    has_summary_table = (
        "enforcement summary" in output.lower()
        or "summary matrix" in output.lower()
    )
    # Count table rows (lines starting with |)
    table_rows = re.findall(r"^\|.*\|$", output, re.MULTILINE)
    # Subtract header rows (rule | scope | enforced by | severity pattern)
    header_rows = [r for r in table_rows if "Rule" in r and "Scope" in r and "Severity" in r]
    separator_rows = [r for r in table_rows if set(r.replace("|", "").replace("-", "").strip()) == set() or "---" in r]
    data_rows = len(table_rows) - len(header_rows) - len(separator_rows)
    print(f"Enforcement summary table: {'PASS' if has_summary_table else 'FAIL'}")
    print(f"  Table data rows: {data_rows} (expect >= 20)")
    if data_rows >= 20:
        print(f"  PASS: At least 20 enforcement rules in summary")
    else:
        print(f"  WARNING: Fewer than 20 rows in enforcement summary")

    # == Glob patterns found ===================================================
    glob_patterns = [
        "**/*.py",
        "services/**",
        "mcp-servers/**",
        "api/**",
        "dashboard/**",
        "agents/**",
        "schemas/**",
        "migrations/**",
        "tests/**",
    ]
    gp_found = [g for g in glob_patterns if g in output]
    gp_missing = [g for g in glob_patterns if g not in output]
    print(f"Glob patterns found: {len(gp_found)}/{len(glob_patterns)}")
    if gp_missing:
        print(f"  MISSING: {gp_missing}")
    else:
        print(f"  PASS: All glob patterns present")

    # == Security rules referenced =============================================
    security_keywords = ["hardcoded secret", "jwt", "sanitiz", "sql param"]
    sec_found = [k for k in security_keywords if k.lower() in output.lower()]
    sec_missing = [k for k in security_keywords if k.lower() not in output.lower()]
    print(f"Security rules referenced: {len(sec_found)}/{len(security_keywords)}")
    if sec_missing:
        print(f"  MISSING: {sec_missing}")
    else:
        print(f"  PASS: All security rules referenced")

    # == Coverage thresholds referenced ========================================
    has_90 = "90" in output
    has_80 = "80" in output
    print(f"Coverage thresholds: 90%={'PASS' if has_90 else 'FAIL'}, 80%={'PASS' if has_80 else 'FAIL'}")

    # == Forbidden patterns covered ============================================
    forbidden_keywords = [
        "business logic",
        "dashboard",
        "hardcoded",
        "print()",
        "blocking",
    ]
    fb_found = [k for k in forbidden_keywords if k.lower() in output.lower()]
    fb_missing = [k for k in forbidden_keywords if k.lower() not in output.lower()]
    print(f"Forbidden patterns covered: {len(fb_found)}/{len(forbidden_keywords)}")
    if fb_missing:
        print(f"  MISSING: {fb_missing}")
    else:
        print(f"  PASS: All forbidden patterns covered in rule files")

    print()
    print("=== FIRST 3000 CHARS ===")
    print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
