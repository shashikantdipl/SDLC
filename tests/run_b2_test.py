"""Live test of B2-test-writer — generates pytest tests from source code."""

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

# Use a real service as input — simplified version of approval_service
SAMPLE_SOURCE = '''
"""ApprovalService — manages human-in-the-loop approval gates."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import asyncpg

class ApprovalNotFoundError(Exception):
    def __init__(self, approval_id: UUID):
        self.approval_id = approval_id
        super().__init__(f"Approval not found: {approval_id}")

class ApprovalStateError(Exception):
    def __init__(self, approval_id: UUID, current_status: str):
        super().__init__(f"Approval {approval_id} is {current_status}, cannot modify")

class ApprovalService:
    def __init__(self, db: asyncpg.Pool) -> None:
        self._db = db

    async def list_pending(self, project_id: str | None = None) -> list[dict]:
        query = "SELECT * FROM approval_requests WHERE status = 'PENDING'"
        params = []
        if project_id:
            query += " AND project_id = $1"
            params.append(project_id)
        query += " ORDER BY expires_at ASC"
        rows = await self._db.fetch(query, *params)
        return [dict(r) for r in rows]

    async def approve(self, approval_id: UUID, decision_by: str, comment: str | None = None) -> dict:
        row = await self._db.fetchrow(
            "SELECT * FROM approval_requests WHERE approval_id = $1", approval_id
        )
        if not row:
            raise ApprovalNotFoundError(approval_id)
        if row["status"] != "PENDING":
            raise ApprovalStateError(approval_id, row["status"])
        await self._db.execute(
            "UPDATE approval_requests SET status = 'APPROVED', decision_by = $2, decided_at = NOW() WHERE approval_id = $1",
            approval_id, decision_by,
        )
        return {"approval_id": str(approval_id), "status": "APPROVED", "decision_by": decision_by}

    async def reject(self, approval_id: UUID, decision_by: str, reason: str) -> dict:
        row = await self._db.fetchrow(
            "SELECT * FROM approval_requests WHERE approval_id = $1", approval_id
        )
        if not row:
            raise ApprovalNotFoundError(approval_id)
        if row["status"] != "PENDING":
            raise ApprovalStateError(approval_id, row["status"])
        await self._db.execute(
            "UPDATE approval_requests SET status = 'REJECTED', decision_by = $2, decision_comment = $3, decided_at = NOW() WHERE approval_id = $1",
            approval_id, decision_by, reason,
        )
        return {"approval_id": str(approval_id), "status": "REJECTED", "decision_by": decision_by, "reason": reason}
'''


async def main():
    agent = BaseAgent(agent_dir=Path("agents/build/B2-test-writer"))
    print(f"Agent: {agent.agent_id}")
    print(f"Provider: {agent.provider_name} | Tier: {agent._model_tier.value} | Model: {agent.model}")
    print()

    result = await agent.invoke(
        input_data={
            "file_path": "services/approval_service.py",
            "source_code": SAMPLE_SOURCE,
            "language": "python",
            "test_type": "all",
            "acceptance_criteria": [
                "Given a pending approval, When approved by lead, Then status becomes APPROVED",
                "Given a pending approval, When rejected with reason, Then status becomes REJECTED with reason",
                "Given a non-existent approval ID, When approved, Then raises ApprovalNotFoundError",
                "Given an already-approved request, When approved again, Then raises ApprovalStateError",
            ],
            "coverage_target": 90,
            "dependencies": ["asyncpg"],
        },
        project_id="test-001",
    )

    print(f"Cost:     ${result['cost_usd']:.4f}")
    print(f"Tokens:   {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Duration: {result['duration_ms']}ms ({result['duration_ms']/1000:.1f}s)")
    print(f"Provider: {result['provider']} | Tier: {result['model_tier']}")
    print()

    output = result["output"]

    # Check test quality indicators
    checks = {
        "Has pytest import": "import pytest" in output,
        "Has AsyncMock": "AsyncMock" in output,
        "Has @pytest.mark.asyncio": "@pytest.mark.asyncio" in output,
        "Has test classes": "class Test" in output,
        "Has mock_db fixture": "mock_db" in output or "db" in output,
        "Has approve test": "test_approve" in output or "test_approval" in output,
        "Has reject test": "test_reject" in output,
        "Has not_found test": "not_found" in output or "NotFound" in output,
        "Has state_error test": "state_error" in output or "StateError" in output or "already" in output,
        "Has list_pending test": "test_list" in output,
        "Has Arrange/Act/Assert": "assert" in output,
        "Has docstrings": '"""' in output,
    }

    test_count = len(re.findall(r"async def test_|def test_", output))
    class_count = len(re.findall(r"class Test", output))

    print(f"Test functions: {test_count}")
    print(f"Test classes: {class_count}")
    print()
    print("Quality checks:")
    for check, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'}: {check}")

    print()
    print("=== FIRST 2500 CHARS ===")
    print(output[:2500])


if __name__ == "__main__":
    asyncio.run(main())
