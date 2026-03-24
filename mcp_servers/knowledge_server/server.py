# knowledge_server/server.py — MCP server for knowledge base and exception management.
# Implements tools from MCP-TOOL-SPEC (Doc 07): knowledge-server group.
# Tools: I-060 through I-063 (4 knowledge tools) + I-081, I-082 (2 system tools).

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

server = Server("agentic-sdlc-knowledge")

# ---------------------------------------------------------------------------
# Service references — populated by init_services()
# ---------------------------------------------------------------------------
_knowledge_service: Any = None
_health_service: Any = None


def init_services(
    knowledge_service: Any,
    health_service: Any,
) -> None:
    """Dependency-inject shared service instances."""
    global _knowledge_service, _health_service
    _knowledge_service = knowledge_service
    _health_service = health_service


# ---------------------------------------------------------------------------
# Tool catalogue
# ---------------------------------------------------------------------------
TOOLS: list[Tool] = [
    # --- KnowledgeService tools ---
    Tool(
        name="search_exceptions",
        description="[I-060] Searches the exception knowledge base using semantic and keyword search.",
        inputSchema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 1000,
                    "description": "Natural-language search query describing the problem or pattern",
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "error-pattern", "workaround", "best-practice",
                        "anti-pattern", "architectural-decision", "tool-usage",
                    ],
                    "description": "Filter by exception category",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by tags",
                },
                "min_confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.7,
                    "description": "Minimum semantic similarity score",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5,
                    "description": "Maximum results to return",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="create_exception",
        description="[I-061] Creates a new exception entry in the knowledge base.",
        inputSchema={
            "type": "object",
            "required": ["title", "category", "description", "resolution", "project_id"],
            "properties": {
                "title": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 200,
                    "description": "Concise title for the exception",
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "error-pattern", "workaround", "best-practice",
                        "anti-pattern", "architectural-decision", "tool-usage",
                    ],
                    "description": "Exception category",
                },
                "description": {
                    "type": "string",
                    "minLength": 20,
                    "maxLength": 5000,
                    "description": "Detailed description of the problem or pattern",
                },
                "resolution": {
                    "type": "string",
                    "minLength": 20,
                    "maxLength": 5000,
                    "description": "How to resolve or apply this knowledge",
                },
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Project where this exception was discovered",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string", "maxLength": 50},
                    "maxItems": 10,
                    "description": "Searchable tags",
                },
                "related_agent_id": {
                    "type": "string",
                    "pattern": "^[A-Z][0-9]+-[a-z-]+$",
                    "description": "Agent that discovered or is related to this exception",
                },
                "code_example": {
                    "type": "string",
                    "maxLength": 10000,
                    "description": "Optional code example demonstrating the pattern or fix",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="promote_exception",
        description="[I-062] Promotes a draft exception to promoted status for active agent reference.",
        inputSchema={
            "type": "object",
            "required": ["exception_id"],
            "properties": {
                "exception_id": {
                    "type": "string",
                    "pattern": "^exc_[a-z0-9]{16}$",
                    "description": "Exception identifier to promote",
                },
                "justification": {
                    "type": "string",
                    "maxLength": 1000,
                    "description": "Why this exception should be promoted",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="list_exceptions",
        description="[I-063] Lists exception entries with filtering by category, status, and tags.",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [
                        "error-pattern", "workaround", "best-practice",
                        "anti-pattern", "architectural-decision", "tool-usage",
                    ],
                    "description": "Filter by category",
                },
                "status": {
                    "type": "string",
                    "enum": ["draft", "promoted", "deprecated"],
                    "description": "Filter by status",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by tags (AND logic)",
                },
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Filter by originating project",
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["created_at", "usage_count", "confidence_score"],
                    "default": "created_at",
                    "description": "Sort order",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                    "description": "Maximum entries to return",
                },
                "offset": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Pagination offset",
                },
            },
            "additionalProperties": False,
        },
    ),
    # --- HealthService (system) tools ---
    Tool(
        name="get_mcp_status",
        description="[I-081] Returns the status of all MCP servers, including connection state and uptime.",
        inputSchema={
            "type": "object",
            "properties": {
                "server_name": {
                    "type": "string",
                    "enum": ["agentic-sdlc-agents", "agentic-sdlc-governance", "agentic-sdlc-knowledge"],
                    "description": "Check a specific server (omit for all servers)",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="list_recent_mcp_calls",
        description="[I-082] Lists recent MCP tool invocations for debugging and observability.",
        inputSchema={
            "type": "object",
            "properties": {
                "server_name": {
                    "type": "string",
                    "enum": ["agentic-sdlc-agents", "agentic-sdlc-governance", "agentic-sdlc-knowledge"],
                    "description": "Filter by server",
                },
                "tool_name": {
                    "type": "string",
                    "description": "Filter by specific tool name",
                },
                "status": {
                    "type": "string",
                    "enum": ["success", "error"],
                    "description": "Filter by call result",
                },
                "since": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Return calls after this timestamp",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 50,
                    "description": "Maximum calls to return",
                },
            },
            "additionalProperties": False,
        },
    ),
]


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    arguments = arguments or {}
    try:
        result = await _dispatch(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, default=str))]
    except Exception as exc:
        error_payload = {"error": type(exc).__name__, "message": str(exc)}
        logger.exception("Tool %s failed", name)
        return [TextContent(type="text", text=json.dumps(error_payload))]


async def _dispatch(name: str, arguments: dict[str, Any]) -> Any:
    # --- KnowledgeService ---
    if name == "search_exceptions":
        return await _knowledge_service.search(**arguments)
    if name == "create_exception":
        return await _knowledge_service.create_exception(**arguments)
    if name == "promote_exception":
        return await _knowledge_service.promote(**arguments)
    if name == "list_exceptions":
        return await _knowledge_service.list_exceptions(**arguments)

    # --- HealthService (system tools) ---
    if name == "get_mcp_status":
        return await _health_service.get_mcp_status(**arguments)
    if name == "list_recent_mcp_calls":
        return await _health_service.list_recent_mcp_calls(**arguments)

    raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
