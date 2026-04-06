"""Live test of B1-code-reviewer — first BUILD agent."""

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


# Sample code with deliberate issues for the reviewer to find
SAMPLE_CODE = '''
import os
import logging
from anthropic import AsyncAnthropic  # VIOLATION: direct LLM SDK import

DB_PASSWORD = "supersecret123"  # VIOLATION: hardcoded secret

def get_user(user_id):  # VIOLATION: no type hints, not async
    conn = psycopg2.connect(os.environ["DATABASE_URL"])  # VIOLATION: not using pool
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # VIOLATION: SQL injection
    result = cursor.fetchone()
    print(f"Found user: {result}")  # VIOLATION: using print, not structlog
    return result

async def process_items(items):
    for item in items:
        await db.execute("INSERT INTO logs VALUES ($1)", item["id"])  # N+1 in loop

    try:
        risky_operation()
    except:  # VIOLATION: bare except
        pass

class PaymentService:
    """Handles payment logic."""

    async def charge(self, amount, currency="USD"):
        # Good: uses async, has docstring
        if amount <= 0:
            raise ValueError("Amount must be positive")
        result = await self._gateway.charge(amount, currency)
        return result
'''


async def main():
    agent = BaseAgent(agent_dir=Path("agents/build/B1-code-reviewer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "file_path": "services/example_service.py",
            "code_content": SAMPLE_CODE,
            "language": "python",
            "review_focus": ["all"],
            "project_rules": {
                "forbidden_patterns": [
                    "No direct import of anthropic/openai SDK (use sdk.llm.LLMProvider)",
                    "No hardcoded secrets",
                    "No print() (use structlog)",
                    "No bare except",
                    "No SQL string concatenation",
                ],
                "required_patterns": [
                    "All functions have type hints",
                    "All I/O uses async/await",
                    "Use asyncpg pool, not raw connections",
                    "Use structlog for logging",
                ],
                "coverage_threshold": 90,
            },
            "context": {
                "pr_description": "Adding example service for testing code review agent",
                "ticket_id": "SDLC-001",
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

    # Try to parse JSON
    try:
        if "```json" in output:
            json_str = output.split("```json")[1].split("```")[0].strip()
        elif output.strip().startswith("{"):
            json_str = output.strip()
        else:
            json_str = None

        if json_str:
            review = json.loads(json_str)

            # Check verdict
            verdict = review.get("review_summary", {}).get("verdict", "unknown")
            print(f"Verdict: {verdict}")

            # Count findings by severity
            findings = review.get("findings", [])
            print(f"Findings: {len(findings)} total")
            by_severity = {}
            for f in findings:
                sev = f.get("severity", "unknown")
                by_severity[sev] = by_severity.get(sev, 0) + 1
            for sev in ["critical", "high", "medium", "low", "info"]:
                if sev in by_severity:
                    print(f"  {sev}: {by_severity[sev]}")

            # Check key findings detected
            all_titles = " ".join(f.get("title", "") + " " + f.get("description", "") for f in findings).lower()
            checks = {
                "SQL injection": "sql injection" in all_titles or "sql" in all_titles,
                "Hardcoded secret": "hardcoded" in all_titles or "secret" in all_titles or "password" in all_titles,
                "Direct LLM import": "anthropic" in all_titles or "llm" in all_titles or "sdk" in all_titles,
                "Bare except": "bare except" in all_titles or "except:" in all_titles or "generic except" in all_titles,
                "Print statement": "print" in all_titles or "structlog" in all_titles or "logging" in all_titles,
                "Missing type hints": "type hint" in all_titles or "annotation" in all_titles,
            }
            print()
            print("Key issues detected:")
            for check, found in checks.items():
                print(f"  {'FOUND' if found else 'MISSED'}: {check}")

            # Check pattern compliance
            compliance = review.get("pattern_compliance", {})
            if compliance:
                print()
                print("Pattern compliance:")
                for pattern, status in compliance.items():
                    print(f"  {pattern}: {status}")

            # Check positive observations
            positives = review.get("positive_observations", [])
            print(f"\nPositive observations: {len(positives)}")

            # Line references
            findings_with_lines = sum(1 for f in findings if f.get("line"))
            print(f"Findings with line references: {findings_with_lines}/{len(findings)}")

        else:
            print("WARNING: Could not extract JSON from output")
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse error: {e}")

    print()
    print("=== FIRST 2000 CHARS ===")
    print(output[:2000])


if __name__ == "__main__":
    asyncio.run(main())
