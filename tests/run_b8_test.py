"""Live test of B8-build-validator."""

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
    agent = BaseAgent(agent_dir=Path("agents/build/B8-build-validator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "agentic-sdlc-platform",
            "build_artifacts": {
                "lint_output": "",
                "typecheck_output": "services/cost_service.py:42: error: Incompatible return value type (got \"str\", expected \"int\")\nservices/cost_service.py:87: error: Missing return statement",
                "test_results": {
                    "passed": 144,
                    "failed": 0,
                    "skipped": 164,
                    "coverage_pct": 82,
                    "coverage_by_module": {
                        "services": 88,
                        "api": 82,
                        "mcp": 79,
                        "models": 91,
                        "agents": 76,
                    },
                },
                "migration_files": [
                    {"name": "001_init_schema.sql", "has_up": True, "has_down": True},
                    {"name": "002_add_users.sql", "has_up": True, "has_down": True},
                    {"name": "003_add_projects.sql", "has_up": True, "has_down": True},
                    {"name": "004_agent_registry.sql", "has_up": True, "has_down": True},
                    {"name": "005_cost_tracking.sql", "has_up": True, "has_down": True},
                    {"name": "006_audit_logs.sql", "has_up": True, "has_down": True},
                    {"name": "007_mcp_tools.sql", "has_up": True, "has_down": True},
                    {"name": "008_guardrails.sql", "has_up": True, "has_down": True},
                    {"name": "009_mcp_call_events.sql", "has_up": True, "has_down": False},
                ],
                "docker_build": {
                    "success": True,
                    "image_size_mb": 245,
                    "build_time_seconds": 38,
                },
                "manifest_validation": {
                    "total": 27,
                    "valid": 27,
                    "invalid": 0,
                },
            },
            "quality_gates": {
                "min_coverage_pct": 85,
                "max_lint_errors": 0,
                "max_type_errors": 0,
                "max_docker_image_mb": 500,
                "require_migration_down": True,
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

            summary = data.get("validation_summary", {})
            gates = data.get("gates", [])
            recommendations = data.get("recommendations", [])

            # --- Check validation_summary ---
            assert "verdict" in summary, "MISSING: validation_summary.verdict"
            assert summary["verdict"] in ("pass", "fail"), (
                f"verdict must be 'pass' or 'fail', got '{summary['verdict']}'"
            )
            print(f"Verdict:        {summary['verdict'].upper()}")
            print(f"Gates checked:  {summary.get('gates_checked', '?')}")
            print(f"Gates passed:   {summary.get('gates_passed', '?')}")
            print(f"Gates failed:   {summary.get('gates_failed', '?')}")
            print(f"Blocking:       {summary.get('blocking_failures', [])}")
            print(f"Timestamp:      {summary.get('build_timestamp', '?')}")
            print()

            # --- Verdict must be FAIL ---
            assert summary["verdict"] == "fail", (
                f"FAIL: Expected verdict 'fail' but got '{summary['verdict']}'. "
                "Input has 2 typecheck errors + 82% coverage (below 85%)."
            )
            print("PASS: Verdict is 'fail' as expected")

            # --- 8 gates checked ---
            assert summary.get("gates_checked") == 8, (
                f"FAIL: Expected 8 gates_checked, got {summary.get('gates_checked')}"
            )
            print("PASS: 8 gates checked")

            # --- blocking_failures includes typecheck and coverage ---
            blocking = summary.get("blocking_failures", [])
            assert any("typecheck" in g for g in blocking), (
                f"FAIL: blocking_failures should include typecheck gate, got {blocking}"
            )
            print("PASS: typecheck_gate in blocking_failures")

            assert any("coverage" in g for g in blocking), (
                f"FAIL: blocking_failures should include coverage gate, got {blocking}"
            )
            print("PASS: coverage_gate in blocking_failures")

            # --- migration_gate should also fail (missing DOWN) ---
            assert any("migration" in g for g in blocking), (
                f"FAIL: blocking_failures should include migration gate, got {blocking}"
            )
            print("PASS: migration_gate in blocking_failures")

            # --- Each gate has required fields ---
            print()
            expected_gates = {
                "lint_gate", "typecheck_gate", "test_gate", "coverage_gate",
                "migration_gate", "docker_gate", "manifest_gate", "schema_gate",
            }
            found_gates = set()
            for g in gates:
                gate_name = g.get("gate", "")
                found_gates.add(gate_name)
                assert "status" in g, f"MISSING: {gate_name}.status"
                assert g["status"] in ("pass", "fail"), (
                    f"{gate_name}.status must be 'pass' or 'fail', got '{g['status']}'"
                )
                assert "threshold" in g, f"MISSING: {gate_name}.threshold"
                assert "actual" in g, f"MISSING: {gate_name}.actual"
                print(f"  {gate_name:20s} => {g['status'].upper():4s}  "
                      f"(threshold: {g['threshold']}, actual: {g['actual']})")

            missing_gates = expected_gates - found_gates
            assert not missing_gates, f"FAIL: Missing gates: {missing_gates}"
            print()
            print("PASS: All 8 gates present with status/threshold/actual")

            # --- Verify specific gate statuses ---
            gate_map = {g["gate"]: g for g in gates}

            assert gate_map.get("lint_gate", {}).get("status") == "pass", (
                "FAIL: lint_gate should pass (clean lint output)"
            )
            print("PASS: lint_gate passes (clean input)")

            assert gate_map.get("typecheck_gate", {}).get("status") == "fail", (
                "FAIL: typecheck_gate should fail (2 mypy errors)"
            )
            print("PASS: typecheck_gate fails (2 errors)")

            assert gate_map.get("test_gate", {}).get("status") == "pass", (
                "FAIL: test_gate should pass (0 failures)"
            )
            print("PASS: test_gate passes (0 failures)")

            assert gate_map.get("coverage_gate", {}).get("status") == "fail", (
                "FAIL: coverage_gate should fail (82% < 85%)"
            )
            print("PASS: coverage_gate fails (82% < 85%)")

            assert gate_map.get("migration_gate", {}).get("status") == "fail", (
                "FAIL: migration_gate should fail (009 missing DOWN)"
            )
            print("PASS: migration_gate fails (missing DOWN)")

            assert gate_map.get("docker_gate", {}).get("status") == "pass", (
                "FAIL: docker_gate should pass (245MB < 500MB, build OK)"
            )
            print("PASS: docker_gate passes (245MB < 500MB)")

            assert gate_map.get("manifest_gate", {}).get("status") == "pass", (
                "FAIL: manifest_gate should pass (27/27 valid)"
            )
            print("PASS: manifest_gate passes (27/27 valid)")

            # --- Recommendations present ---
            print()
            assert len(recommendations) > 0, "FAIL: recommendations should not be empty"
            print(f"Recommendations ({len(recommendations)}):")
            for r in recommendations:
                print(f"  - {r}")

            print()
            print("=" * 60)
            print("ALL CHECKS PASSED")
            print("=" * 60)

        else:
            print("WARNING: Could not extract JSON from output")
            print("Raw output (first 2000 chars):")
            print(output[:2000])

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print("Raw output (first 2000 chars):")
        print(output[:2000])

    except AssertionError as e:
        print(f"\nASSERTION FAILED: {e}")
        print("\nFull output:")
        print(output[:3000])


if __name__ == "__main__":
    asyncio.run(main())
