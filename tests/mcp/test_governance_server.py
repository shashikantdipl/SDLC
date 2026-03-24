# tests/mcp/test_governance_server.py — Unit tests for the governance MCP server.
# All service calls are mocked with AsyncMock.

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from mcp_servers.governance_server.server import (
    TOOLS,
    handle_call_tool,
    handle_list_tools,
    init_services,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _inject_mocks():
    """Create AsyncMock services and inject them before every test."""
    cost = AsyncMock()
    audit = AsyncMock()
    approval = AsyncMock()
    init_services(cost_service=cost, audit_service=audit, approval_service=approval)
    yield {"cost": cost, "audit": audit, "approval": approval}


@pytest.fixture()
def services(_inject_mocks):
    return _inject_mocks


# ---------------------------------------------------------------------------
# list_tools
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_tools_returns_10_tools():
    tools = await handle_list_tools()
    assert len(tools) == 10


@pytest.mark.asyncio
async def test_list_tools_names():
    tools = await handle_list_tools()
    names = {t.name for t in tools}
    expected = {
        "get_cost_report", "check_budget",
        "query_audit_events", "get_audit_summary", "export_audit_report",
        "list_pending_approvals", "approve_gate", "reject_gate",
        "get_cost_anomalies", "update_budget_threshold",
    }
    assert names == expected


# ---------------------------------------------------------------------------
# CostService tools
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_cost_report_calls_service(services):
    services["cost"].get_report.return_value = {"total_cost_usd": 42.5}
    result = await handle_call_tool("get_cost_report", {"scope": "fleet", "days": 7})
    services["cost"].get_report.assert_awaited_once_with(scope="fleet", days=7)
    payload = json.loads(result[0].text)
    assert payload["total_cost_usd"] == 42.5


@pytest.mark.asyncio
async def test_check_budget_calls_service(services):
    services["cost"].check_budget.return_value = {"remaining_usd": 100.0}
    result = await handle_call_tool("check_budget", {"project_id": "proj_abc123def456"})
    services["cost"].check_budget.assert_awaited_once_with(project_id="proj_abc123def456")
    payload = json.loads(result[0].text)
    assert payload["remaining_usd"] == 100.0


@pytest.mark.asyncio
async def test_get_cost_anomalies_calls_service(services):
    services["cost"].get_anomalies.return_value = [{"anomaly_id": "a1", "severity": "high"}]
    result = await handle_call_tool("get_cost_anomalies", {"severity": "high", "days": 7})
    services["cost"].get_anomalies.assert_awaited_once_with(severity="high", days=7)
    payload = json.loads(result[0].text)
    assert len(payload) == 1


@pytest.mark.asyncio
async def test_update_budget_threshold_calls_service(services):
    services["cost"].update_budget_threshold.return_value = {"threshold_percent": 80}
    result = await handle_call_tool("update_budget_threshold", {"threshold_percent": 80})
    services["cost"].update_budget_threshold.assert_awaited_once_with(threshold_percent=80)
    payload = json.loads(result[0].text)
    assert payload["threshold_percent"] == 80


# ---------------------------------------------------------------------------
# AuditService tools
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_query_audit_events_calls_service(services):
    services["audit"].query_events.return_value = [{"event_id": "evt_1"}]
    result = await handle_call_tool("query_audit_events", {"limit": 10})
    services["audit"].query_events.assert_awaited_once_with(limit=10)
    payload = json.loads(result[0].text)
    assert payload[0]["event_id"] == "evt_1"


@pytest.mark.asyncio
async def test_get_audit_summary_calls_service(services):
    services["audit"].get_summary.return_value = {"total_events": 150}
    result = await handle_call_tool("get_audit_summary", {"days": 30})
    services["audit"].get_summary.assert_awaited_once_with(days=30)
    payload = json.loads(result[0].text)
    assert payload["total_events"] == 150


@pytest.mark.asyncio
async def test_export_audit_report_calls_service(services):
    services["audit"].export_report.return_value = {"report_id": "rpt_1", "format": "csv"}
    result = await handle_call_tool("export_audit_report", {"format": "csv"})
    services["audit"].export_report.assert_awaited_once_with(format="csv")
    payload = json.loads(result[0].text)
    assert payload["format"] == "csv"


# ---------------------------------------------------------------------------
# ApprovalService tools
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_pending_approvals_calls_service(services):
    services["approval"].list_pending.return_value = [{"approval_id": "appr_a1b2c3d4e5f6g7h8"}]
    result = await handle_call_tool("list_pending_approvals", {})
    services["approval"].list_pending.assert_awaited_once_with()
    payload = json.loads(result[0].text)
    assert len(payload) == 1


@pytest.mark.asyncio
async def test_approve_gate_calls_service(services):
    services["approval"].approve.return_value = {
        "approval_id": "appr_a1b2c3d4e5f6g7h8",
        "status": "approved",
    }
    result = await handle_call_tool(
        "approve_gate",
        {"approval_id": "appr_a1b2c3d4e5f6g7h8", "comment": "LGTM"},
    )
    services["approval"].approve.assert_awaited_once_with(
        approval_id="appr_a1b2c3d4e5f6g7h8", comment="LGTM",
    )
    payload = json.loads(result[0].text)
    assert payload["status"] == "approved"


@pytest.mark.asyncio
async def test_reject_gate_calls_service(services):
    services["approval"].reject.return_value = {
        "approval_id": "appr_a1b2c3d4e5f6g7h8",
        "status": "rejected",
    }
    result = await handle_call_tool(
        "reject_gate",
        {"approval_id": "appr_a1b2c3d4e5f6g7h8", "reason": "Missing security analysis for API endpoints"},
    )
    services["approval"].reject.assert_awaited_once()
    payload = json.loads(result[0].text)
    assert payload["status"] == "rejected"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_approve_gate_not_found_returns_error(services):
    services["approval"].approve.side_effect = ValueError("Approval appr_0000000000000000 not found")
    result = await handle_call_tool(
        "approve_gate",
        {"approval_id": "appr_0000000000000000"},
    )
    payload = json.loads(result[0].text)
    assert payload["error"] == "ValueError"
    assert "not found" in payload["message"]


@pytest.mark.asyncio
async def test_unknown_tool_returns_error(services):
    result = await handle_call_tool("nonexistent_tool", {})
    payload = json.loads(result[0].text)
    assert payload["error"] == "ValueError"
    assert "Unknown tool" in payload["message"]


# ---------------------------------------------------------------------------
# Input schema validation (structural checks on Tool definitions)
# ---------------------------------------------------------------------------
def test_get_cost_report_schema_requires_scope():
    tool = next(t for t in TOOLS if t.name == "get_cost_report")
    assert "scope" in tool.inputSchema["required"]


def test_approve_gate_schema_requires_approval_id():
    tool = next(t for t in TOOLS if t.name == "approve_gate")
    assert "approval_id" in tool.inputSchema["required"]


def test_reject_gate_schema_requires_reason():
    tool = next(t for t in TOOLS if t.name == "reject_gate")
    assert "reason" in tool.inputSchema["required"]


def test_export_audit_report_schema_requires_format():
    tool = next(t for t in TOOLS if t.name == "export_audit_report")
    assert "format" in tool.inputSchema["required"]


def test_update_budget_threshold_schema_requires_threshold_percent():
    tool = next(t for t in TOOLS if t.name == "update_budget_threshold")
    assert "threshold_percent" in tool.inputSchema["required"]
