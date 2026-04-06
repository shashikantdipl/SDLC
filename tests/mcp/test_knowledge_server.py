# tests/mcp/test_knowledge_server.py — Unit tests for the knowledge MCP server.
# All service calls are mocked with AsyncMock.

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from mcp_servers.knowledge_server.server import (
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
    knowledge = AsyncMock()
    health = AsyncMock()
    init_services(knowledge_service=knowledge, health_service=health)
    yield {"knowledge": knowledge, "health": health}


@pytest.fixture()
def services(_inject_mocks):
    return _inject_mocks


# ---------------------------------------------------------------------------
# list_tools
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_tools_returns_6_tools():
    tools = await handle_list_tools()
    assert len(tools) == 6


@pytest.mark.asyncio
async def test_list_tools_names():
    tools = await handle_list_tools()
    names = {t.name for t in tools}
    expected = {
        "search_exceptions", "create_exception",
        "promote_exception", "list_exceptions",
        "get_mcp_status", "list_recent_mcp_calls",
    }
    assert names == expected


# ---------------------------------------------------------------------------
# KnowledgeService tools
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_search_exceptions_calls_service(services):
    services["knowledge"].search.return_value = [
        {"exception_id": "exc_a1b2c3d4e5f6g7h8", "title": "Rate limit pattern"}
    ]
    result = await handle_call_tool("search_exceptions", {"query": "rate limiting"})
    services["knowledge"].search.assert_awaited_once_with(query="rate limiting", tier=None, limit=20)
    payload = json.loads(result[0].text)
    assert len(payload) == 1
    assert payload[0]["exception_id"] == "exc_a1b2c3d4e5f6g7h8"


@pytest.mark.asyncio
async def test_create_exception_calls_service(services):
    services["knowledge"].create_exception.return_value = {
        "exception_id": "exc_newentry00000000",
        "status": "draft",
    }
    args = {
        "title": "Always use parameterized queries",
        "rule": "Use parameterized queries in all DB calls",
        "severity": "WARNING",
        "tier": "universal",
        "created_by": "test_user",
    }
    result = await handle_call_tool("create_exception", args)
    services["knowledge"].create_exception.assert_awaited_once_with(
        title="Always use parameterized queries",
        rule="Use parameterized queries in all DB calls",
        severity="WARNING",
        tier="universal",
        created_by="test_user",
        metadata={},
    )
    payload = json.loads(result[0].text)
    assert payload["status"] == "draft"


@pytest.mark.asyncio
async def test_promote_exception_calls_service(services):
    services["knowledge"].promote.return_value = {
        "exception_id": "exc_a1b2c3d4e5f6g7h8",
        "status": "promoted",
    }
    result = await handle_call_tool(
        "promote_exception",
        {"exception_id": "exc_a1b2c3d4e5f6g7h8", "target_tier": "universal", "promoted_by": "admin"},
    )
    services["knowledge"].promote.assert_awaited_once_with(
        exception_id="exc_a1b2c3d4e5f6g7h8", target_tier="universal", promoted_by="admin",
    )
    payload = json.loads(result[0].text)
    assert payload["status"] == "promoted"


@pytest.mark.asyncio
async def test_list_exceptions_calls_service(services):
    services["knowledge"].list_exceptions.return_value = {
        "total": 2,
        "items": [
            {"exception_id": "exc_0000000000000001"},
            {"exception_id": "exc_0000000000000002"},
        ],
    }
    result = await handle_call_tool("list_exceptions", {"tier": "universal", "active_only": True, "limit": 10})
    services["knowledge"].list_exceptions.assert_awaited_once_with(tier="universal", active_only=True, limit=10)
    payload = json.loads(result[0].text)
    assert payload["total"] == 2


# ---------------------------------------------------------------------------
# HealthService (system) tools
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_mcp_status_calls_service(services):
    services["health"].get_mcp_status.return_value = [
        {"server_name": "agentic-sdlc-knowledge", "status": "connected"}
    ]
    result = await handle_call_tool("get_mcp_status", {})
    services["health"].get_mcp_status.assert_awaited_once_with()
    payload = json.loads(result[0].text)
    assert payload[0]["status"] == "connected"


@pytest.mark.asyncio
async def test_list_recent_mcp_calls_calls_service(services):
    services["health"].list_recent_mcp_calls.return_value = [
        {"call_id": "call_1", "status": "success"}
    ]
    result = await handle_call_tool("list_recent_mcp_calls", {"limit": 5})
    services["health"].list_recent_mcp_calls.assert_awaited_once_with(limit=5, server_name=None)
    payload = json.loads(result[0].text)
    assert payload[0]["status"] == "success"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_promote_exception_invalid_direction_returns_error(services):
    services["knowledge"].promote.side_effect = ValueError(
        "Cannot promote: exception exc_0000000000000000 is already promoted"
    )
    result = await handle_call_tool(
        "promote_exception",
        {"exception_id": "exc_0000000000000000"},
    )
    payload = json.loads(result[0].text)
    assert payload["error"] == "ValueError"
    assert "already promoted" in payload["message"]


@pytest.mark.asyncio
async def test_search_exceptions_knowledge_base_unavailable(services):
    services["knowledge"].search.side_effect = ConnectionError("Knowledge base is temporarily unavailable")
    result = await handle_call_tool("search_exceptions", {"query": "test query"})
    payload = json.loads(result[0].text)
    assert payload["error"] == "ConnectionError"
    assert "unavailable" in payload["message"]


@pytest.mark.asyncio
async def test_unknown_tool_returns_error(services):
    result = await handle_call_tool("nonexistent_tool", {})
    payload = json.loads(result[0].text)
    assert payload["error"] == "ValueError"
    assert "Unknown tool" in payload["message"]


# ---------------------------------------------------------------------------
# Input schema validation (structural checks on Tool definitions)
# ---------------------------------------------------------------------------
def test_search_exceptions_schema_requires_query():
    tool = next(t for t in TOOLS if t.name == "search_exceptions")
    assert "query" in tool.inputSchema["required"]


def test_create_exception_schema_requires_fields():
    tool = next(t for t in TOOLS if t.name == "create_exception")
    required = set(tool.inputSchema["required"])
    assert {"title", "category", "description", "resolution", "project_id"} == required


def test_promote_exception_schema_requires_exception_id():
    tool = next(t for t in TOOLS if t.name == "promote_exception")
    assert "exception_id" in tool.inputSchema["required"]


def test_list_exceptions_schema_has_no_required_fields():
    tool = next(t for t in TOOLS if t.name == "list_exceptions")
    assert "required" not in tool.inputSchema
