"""Live test of D1-roadmap-generator."""

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


async def main():
    agent = BaseAgent(agent_dir=Path("agents/design/D1-roadmap-generator"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "project_name": "FleetOps Dashboard",
            "project_purpose": "Real-time fleet management dashboard replacing a 15-year-old AS/400 system for a logistics company with 200 trucks.",
            "brd_summary": {
                "requirements_count": 17,
                "must_have_count": 10,
                "stakeholders": [
                    {"name": "David Kim", "title": "VP Operations", "role": "sponsor"},
                    {"name": "James Park", "title": "Ops Manager", "role": "decision_maker"},
                    {"name": "Sarah Chen", "title": "IT Director", "role": "decision_maker"},
                    {"name": "Maria Santos", "title": "Lead Dispatcher", "role": "sme"},
                    {"name": "Tom Miller", "title": "CFO", "role": "decision_maker"},
                ],
                "constraints": {
                    "budget": "$350,000 total",
                    "timeline": "MVP 6 months, full rollout 12 months",
                    "regulatory": ["DOT HOS compliance", "US data residency"],
                    "technology": ["Must integrate Samsara GPS API v3.2", "AS/400 parallel run during migration"],
                },
                "success_criteria": [
                    "SC-001: Fleet dashboard loads in <2s with all 200 trucks",
                    "SC-002: Route reassignment in <30 seconds",
                    "SC-003: Automatic HOS compliance alerts within 5 minutes of violation",
                    "SC-004: Cost-per-delivery calculated automatically within 1h of delivery",
                    "SC-005: AS/400 decommissioned within 12 months",
                ],
                "open_questions": [
                    "OQ-001: Dispatcher headcount for sizing (Maria Santos, blocks PRD)",
                    "OQ-002: Samsara API rate limits for real-time integration (Sarah Chen, blocks ARCH)",
                    "OQ-003: CFO approval on $350K budget (Tom Miller, blocks Phase 2)",
                ],
            },
            "team_size": 3,
            "sprint_length_weeks": 2,
            "known_risks": [
                "AS/400 specialist retiring in 18 months — hard deadline",
                "Samsara GPS integration is currently CSV-based, real-time API untested",
                "No automated tests on current system — regression risk during migration",
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

    # Section checks
    sections = ["Current State", "Document Build Sequence", "Delivery Phases",
                "Milestones", "Open Decisions", "Risk Register", "Timeline", "Versioning"]
    found = [s for s in sections if s.lower() in output.lower()]
    missing = [s for s in sections if s.lower() not in output.lower()]
    print(f"Sections: {len(found)}/{len(sections)}")
    if missing:
        print(f"  Missing: {missing}")

    # ID checks
    milestones = set(re.findall(r"M-\d+", output))
    risks = set(re.findall(r"R-\d+", output))
    decisions = set(re.findall(r"OD-\d+", output))
    phases_found = len(re.findall(r"Phase \d+", output))

    print(f"Milestones: {len(milestones)} (M-NNN IDs)")
    print(f"Risks: {len(risks)} (R-NNN IDs)")
    print(f"Open Decisions: {len(decisions)} (OD-NNN IDs)")
    print(f"Phases referenced: {phases_found}")

    # Check for 24-doc awareness
    has_24 = "24" in output
    has_brd = "BRD" in output or "00-BRD" in output
    print(f"24-doc aware: {has_24}")
    print(f"References BRD (Doc 00): {has_brd}")

    print()
    print("=== FIRST 2500 CHARS ===")
    print(output[:2500])


if __name__ == "__main__":
    asyncio.run(main())
