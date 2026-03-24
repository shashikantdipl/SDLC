"""BaseHooks — Pre/post invocation hooks for all agents.

Every agent invocation runs through these hooks:
- Pre-invoke: audit start, budget check
- Post-invoke: audit complete, cost recording, PII scan

Override for custom behavior. Default implementation logs to structlog.
"""
from __future__ import annotations

import re
from decimal import Decimal
from uuid import UUID
from typing import Any

import structlog

logger = structlog.get_logger()

# Simple PII patterns (emails, phone numbers, SSNs)
PII_PATTERNS = [
    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # email
    re.compile(r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b'),  # SSN
    re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),  # phone
]


class BaseHooks:
    """Default hooks — logging only. Override for DB-backed hooks."""

    async def pre_invoke(
        self,
        agent_id: str,
        invocation_id: UUID,
        session_id: UUID,
        project_id: str,
        input_data: dict[str, Any],
    ) -> None:
        """Called before agent invocation."""
        logger.info(
            "agent.invoke.start",
            agent_id=agent_id,
            invocation_id=str(invocation_id),
            session_id=str(session_id),
            project_id=project_id,
        )

    async def post_invoke(
        self,
        agent_id: str,
        invocation_id: UUID,
        session_id: UUID,
        project_id: str,
        output_text: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: Decimal,
        duration_ms: int,
    ) -> None:
        """Called after agent invocation."""
        pii_detected = self._scan_pii(output_text)

        logger.info(
            "agent.invoke.complete",
            agent_id=agent_id,
            invocation_id=str(invocation_id),
            session_id=str(session_id),
            project_id=project_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=float(cost_usd),
            duration_ms=duration_ms,
            pii_detected=pii_detected,
        )

        if pii_detected:
            logger.warning(
                "agent.pii_detected",
                agent_id=agent_id,
                invocation_id=str(invocation_id),
            )

    @staticmethod
    def _scan_pii(text: str) -> bool:
        """Scan text for PII patterns. Returns True if any found."""
        for pattern in PII_PATTERNS:
            if pattern.search(text):
                return True
        return False
