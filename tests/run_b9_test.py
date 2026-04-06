"""Live test of B9-migration-writer."""

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
    agent = BaseAgent(agent_dir=Path("agents/build/B9-migration-writer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "change_description": "Add llm_provider column to agent_registry table to track which LLM provider each agent uses",
            "current_schema": [
                {
                    "table": "agent_registry",
                    "columns": [
                        "id",
                        "agent_id",
                        "name",
                        "phase",
                        "status",
                        "active_version",
                        "maturity_level",
                        "created_at",
                        "updated_at",
                    ],
                }
            ],
            "migration_number": 10,
            "existing_migrations": [
                "001_create_agents.sql",
                "002_add_users.sql",
                "003_add_projects.sql",
                "004_agent_registry.sql",
                "005_cost_tracking.sql",
                "006_audit_logs.sql",
                "007_mcp_tools.sql",
                "008_guardrails.sql",
                "009_mcp_call_events.sql",
            ],
            "constraints": {
                "zero_downtime": True,
                "backwards_compatible": True,
                "max_lock_time_seconds": 5,
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

            migration = data.get("migration", {})
            safety_checks = data.get("safety_checks", [])
            warnings = data.get("warnings", [])
            test_commands = data.get("test_commands", [])

            # --- Check migration object ---
            assert "filename" in migration, "MISSING: migration.filename"
            assert "number" in migration, "MISSING: migration.number"
            assert "up_sql" in migration, "MISSING: migration.up_sql"
            assert "down_sql" in migration, "MISSING: migration.down_sql"
            assert "is_destructive" in migration, "MISSING: migration.is_destructive"
            assert "zero_downtime_safe" in migration, "MISSING: migration.zero_downtime_safe"
            assert "backwards_compatible" in migration, "MISSING: migration.backwards_compatible"
            print("PASS: All required migration fields present")

            # --- Filename starts with 010 ---
            fname = migration["filename"]
            assert fname.startswith("010_"), (
                f"FAIL: filename should start with '010_', got '{fname}'"
            )
            assert fname.endswith(".sql"), (
                f"FAIL: filename should end with '.sql', got '{fname}'"
            )
            print(f"PASS: Filename is '{fname}' (starts with 010_, ends with .sql)")

            # --- Number is 10 ---
            assert migration["number"] == 10, (
                f"FAIL: migration number should be 10, got {migration['number']}"
            )
            print("PASS: Migration number is 10")

            # --- UP SQL contains ALTER TABLE and agent_registry ---
            up_sql = migration["up_sql"].upper()
            assert "ALTER TABLE" in up_sql, (
                "FAIL: up_sql should contain ALTER TABLE"
            )
            print("PASS: up_sql contains ALTER TABLE")

            assert "AGENT_REGISTRY" in up_sql, (
                "FAIL: up_sql should reference agent_registry table"
            )
            print("PASS: up_sql references agent_registry")

            assert "ADD COLUMN" in up_sql, (
                "FAIL: up_sql should contain ADD COLUMN"
            )
            print("PASS: up_sql contains ADD COLUMN")

            # --- UP SQL has DEFAULT value ---
            assert "DEFAULT" in up_sql, (
                "FAIL: up_sql should include DEFAULT (required for zero-downtime ADD COLUMN)"
            )
            print("PASS: up_sql includes DEFAULT value")

            # --- DOWN SQL contains DROP COLUMN ---
            down_sql = migration["down_sql"].upper()
            assert "DROP COLUMN" in down_sql or "DROP TABLE" in down_sql, (
                "FAIL: down_sql should contain DROP COLUMN (to reverse the ADD)"
            )
            print("PASS: down_sql contains DROP COLUMN")

            assert "AGENT_REGISTRY" in down_sql, (
                "FAIL: down_sql should reference agent_registry table"
            )
            print("PASS: down_sql references agent_registry")

            # --- Flags ---
            assert migration["is_destructive"] is False, (
                f"FAIL: is_destructive should be False for ADD COLUMN, got {migration['is_destructive']}"
            )
            print("PASS: is_destructive is False")

            assert migration["zero_downtime_safe"] is True, (
                f"FAIL: zero_downtime_safe should be True, got {migration['zero_downtime_safe']}"
            )
            print("PASS: zero_downtime_safe is True")

            assert migration["backwards_compatible"] is True, (
                f"FAIL: backwards_compatible should be True, got {migration['backwards_compatible']}"
            )
            print("PASS: backwards_compatible is True")

            # --- Safety checks ---
            print()
            assert len(safety_checks) >= 5, (
                f"FAIL: Expected at least 5 safety checks, got {len(safety_checks)}"
            )
            print(f"Safety checks ({len(safety_checks)}):")
            all_pass = True
            for sc in safety_checks:
                assert "check" in sc, "MISSING: safety_check.check"
                assert "status" in sc, "MISSING: safety_check.status"
                status = sc["status"]
                print(f"  {sc['check']:40s} => {status.upper()}")
                if status != "pass":
                    all_pass = False

            assert all_pass, (
                "FAIL: All safety checks should pass for a simple ADD COLUMN migration"
            )
            print("PASS: All safety checks passed")

            # --- Warnings should be empty for non-destructive change ---
            print()
            print(f"Warnings: {warnings}")
            # Warnings can be empty or contain informational items; not asserting empty

            # --- Test commands present ---
            assert len(test_commands) > 0, "FAIL: test_commands should not be empty"
            print(f"Test commands: {test_commands}")

            # --- Description present ---
            assert "description" in migration, "MISSING: migration.description"
            assert len(migration["description"]) > 10, (
                "FAIL: description should be meaningful"
            )
            print(f"Description: {migration['description']}")

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
