"""Live audit of all 5 GOVERN agents — tests each with real API call."""

import asyncio
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

from sdk.base_agent import BaseAgent
from pathlib import Path


async def test_agent(agent_dir, input_data):
    agent = BaseAgent(agent_dir=Path(agent_dir))
    result = await agent.invoke(input_data, project_id="proj-001")

    checks = []
    checks.append(("has_output", bool(result.get("output", "").strip())))
    checks.append(("has_cost", result.get("cost_usd", 0) > 0))
    checks.append(("has_tokens", result.get("input_tokens", 0) > 0))
    checks.append(("provider_set", result.get("provider") == "anthropic"))
    checks.append(("tier_set", result.get("model_tier") in ("fast", "balanced")))
    checks.append(("not_dry_run", result.get("dry_run") is False))

    output = result["output"]
    try:
        if "```json" in output:
            json_str = output.split("```json")[1].split("```")[0].strip()
        elif output.strip().startswith("{"):
            json_str = output.strip()
        else:
            json_str = None
        if json_str:
            json.loads(json_str)
            checks.append(("valid_json", True))
        else:
            checks.append(("valid_json", False))
    except Exception:
        checks.append(("valid_json", False))

    passed = sum(1 for _, v in checks if v)
    total = len(checks)
    status = "PASS" if passed == total else f"WARN ({passed}/{total})"

    return {
        "agent": result["agent_id"],
        "status": status,
        "cost": result["cost_usd"],
        "tokens_in": result["input_tokens"],
        "tokens_out": result["output_tokens"],
        "duration_ms": result["duration_ms"],
        "provider": result["provider"],
        "tier": result["model_tier"],
        "model": result["model"],
        "checks": checks,
    }


async def main():
    results = []

    # G1
    print("Testing G1-cost-tracker...")
    r = await test_agent("agents/govern/G1-cost-tracker", {
        "scope": "project", "scope_id": "proj-001", "period_days": 7,
        "cost_data": [{"agent_id": "D2-prd", "cost_usd": 1.20, "invocations": 2}],
        "budget_config": {"budget_usd": 20.00},
    })
    results.append(r)
    print(f"  {r['status']} | ${r['cost']:.4f} | {r['duration_ms']}ms")

    # G2
    print("Testing G2-audit-trail-validator...")
    r = await test_agent("agents/govern/G2-audit-trail-validator", {
        "project_id": "proj-001", "period_days": 7, "check_types": ["completeness"],
        "audit_events": [{"event_id": "e1", "agent_id": "G1-cost-tracker", "project_id": "proj-001",
            "session_id": "s1", "action": "agent.invoke", "severity": "info", "message": "ok",
            "details": {}, "pii_detected": False, "cost_usd": 0.003, "input_tokens": 100,
            "output_tokens": 50, "created_at": "2026-03-29T10:00:00Z"}],
        "agent_registry": [{"agent_id": "G1-cost-tracker", "status": "active", "phase": "govern"}],
        "pipeline_runs": [], "cost_metrics": [],
    })
    results.append(r)
    print(f"  {r['status']} | ${r['cost']:.4f} | {r['duration_ms']}ms")

    # G3
    print("Testing G3-agent-lifecycle-manager...")
    r = await test_agent("agents/govern/G3-agent-lifecycle-manager", {
        "action": "recommend_canary", "agent_id": "D2-prd",
        "agent_detail": {"active_version": "1.0.0", "maturity_level": "professional", "status": "active"},
        "performance_data": {"override_rate": 0.03, "confidence_avg": 0.91, "error_rate": 0.01,
            "cost_avg_usd": 1.20, "invocation_count": 50, "consecutive_success_days": 10},
        "version_history": [],
    })
    results.append(r)
    print(f"  {r['status']} | ${r['cost']:.4f} | {r['duration_ms']}ms")

    # G4
    print("Testing G4-team-orchestrator...")
    r = await test_agent("agents/govern/G4-team-orchestrator", {
        "action": "plan_execution", "pipeline_name": "document-stack",
        "pipeline_config": {
            "steps": ["D0-brd", "D1-roadmap", "D2-prd", "D3-arch", "D4-features", "D5-quality",
                "D6-security", "D7-interaction", "D8-mcp", "D9-design", "D10-data", "D11-api",
                "D12-user-stories", "D13-backlog", "D14-claude", "D15-enforce", "D16-infra",
                "D17-migration", "D18-testing", "D19-fault-tol", "D20-guardrails", "D21-compliance"],
            "parallel_groups": [["D1-roadmap", "D2-prd"], ["D8-mcp", "D9-design"], ["D17-migration", "D18-testing"]],
            "cost_ceiling_usd": 45.00,
        },
        "current_state": {"run_id": "run-test", "completed_steps": [], "failed_steps": [],
            "cumulative_cost_usd": 0, "elapsed_minutes": 0},
    })
    results.append(r)
    print(f"  {r['status']} | ${r['cost']:.4f} | {r['duration_ms']}ms")

    # G5
    print("Testing G5-audit-reporter...")
    r = await test_agent("agents/govern/G5-audit-reporter", {
        "project_id": "proj-001", "report_type": "pipeline_health", "period_days": 7, "audience": "engineering",
        "audit_events": [{"event_id": "e1", "agent_id": "G1-cost-tracker", "action": "agent.invoke",
            "severity": "info", "cost_usd": 0.003, "created_at": "2026-03-29T10:00:00Z"}],
        "cost_metrics": [{"agent_id": "G1-cost-tracker", "cost_usd": 0.45, "invocations": 150, "provider": "anthropic"}],
        "agent_registry": [{"agent_id": "G1-cost-tracker", "status": "active", "maturity": "expert", "phase": "govern"}],
        "pipeline_runs": [{"run_id": "r1", "status": "completed", "total_steps": 22, "cost_usd": 38.50, "duration_min": 28}],
        "approval_requests": [],
    })
    results.append(r)
    print(f"  {r['status']} | ${r['cost']:.4f} | {r['duration_ms']}ms")

    # Summary
    print()
    print("=" * 80)
    print(f"{'Agent':<35} {'Status':<12} {'Cost':>8} {'Tokens':>14} {'Time':>8} {'Provider':>10}")
    print("-" * 80)
    total_cost = 0
    for r in results:
        total_cost += r["cost"]
        tokens = f"{r['tokens_in']}+{r['tokens_out']}"
        print(f"{r['agent']:<35} {r['status']:<12} ${r['cost']:>7.4f} {tokens:>14} {r['duration_ms']:>6}ms {r['provider']:>10}")
    print("-" * 80)
    print(f"{'TOTAL':<35} {'':12} ${total_cost:>7.4f}")
    print()

    # Detail any failures
    any_fail = False
    for r in results:
        failed = [(k, v) for k, v in r["checks"] if not v]
        if failed:
            any_fail = True
            print(f"ISSUES in {r['agent']}:")
            for k, _ in failed:
                print(f"  FAIL: {k}")

    if not any_fail:
        print("ALL 5 GOVERN AGENTS: PASS")


if __name__ == "__main__":
    asyncio.run(main())
