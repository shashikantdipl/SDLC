# governance_server/server.py — MCP server for cost, audit, and approval governance.
# Implements tools from MCP-TOOL-SPEC (Doc 07): governance-server group.
# Tools: I-040 through I-049 (10 tools across CostService, AuditService, ApprovalService).

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

server = Server("agentic-sdlc-governance")

# ---------------------------------------------------------------------------
# Service references — populated by init_services()
# ---------------------------------------------------------------------------
_cost_service: Any = None
_audit_service: Any = None
_approval_service: Any = None


def init_services(
    cost_service: Any,
    audit_service: Any,
    approval_service: Any,
) -> None:
    """Dependency-inject shared service instances."""
    global _cost_service, _audit_service, _approval_service
    _cost_service = cost_service
    _audit_service = audit_service
    _approval_service = approval_service


# ---------------------------------------------------------------------------
# Tool catalogue
# ---------------------------------------------------------------------------
TOOLS: list[Tool] = [
    # --- CostService tools ---
    Tool(
        name="get_cost_report",
        description="[I-040] Generates a cost report for a given scope (project, fleet, or agent) over a specified time period.",
        inputSchema={
            "type": "object",
            "required": ["scope"],
            "properties": {
                "scope": {
                    "type": "string",
                    "enum": ["project", "fleet", "agent"],
                    "description": "Report scope level",
                },
                "scope_id": {
                    "type": "string",
                    "description": "project_id or agent_id (required for project/agent scope, omit for fleet)",
                },
                "period": {
                    "type": "object",
                    "required": ["start", "end"],
                    "properties": {
                        "start": {"type": "string", "format": "date-time", "description": "Period start (ISO-8601)"},
                        "end": {"type": "string", "format": "date-time", "description": "Period end (ISO-8601)"},
                    },
                },
                "group_by": {
                    "type": "string",
                    "enum": ["agent", "model", "stage", "day", "project"],
                    "default": "agent",
                    "description": "How to break down the cost data",
                },
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 365,
                    "default": 7,
                    "description": "Shorthand for period: last N days (ignored if period is specified)",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="check_budget",
        description="[I-041] Returns the current budget status for a project or the fleet.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Project to check (omit for fleet-wide budget)",
                },
            },
            "additionalProperties": False,
        },
    ),
    # --- AuditService tools ---
    Tool(
        name="query_audit_events",
        description="[I-042] Queries the audit event log with rich filtering by actor, action type, resource, and time range.",
        inputSchema={
            "type": "object",
            "properties": {
                "actor": {"type": "string", "description": "Filter by actor ID (user or agent ID)"},
                "action": {
                    "type": "string",
                    "enum": [
                        "pipeline.triggered", "pipeline.completed", "pipeline.failed", "pipeline.cancelled",
                        "pipeline.resumed", "pipeline.stage.retried",
                        "agent.invoked", "agent.promoted", "agent.rolledback", "agent.canary.updated",
                        "gate.approved", "gate.rejected",
                        "budget.threshold.updated", "budget.exceeded",
                        "exception.created", "exception.promoted",
                    ],
                    "description": "Filter by action type",
                },
                "resource_type": {
                    "type": "string",
                    "enum": ["pipeline", "agent", "gate", "budget", "exception"],
                    "description": "Filter by resource type",
                },
                "resource_id": {"type": "string", "description": "Filter by specific resource ID"},
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Filter by project",
                },
                "since": {"type": "string", "format": "date-time", "description": "Return events after this timestamp"},
                "until": {"type": "string", "format": "date-time", "description": "Return events before this timestamp"},
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 500,
                    "default": 50,
                    "description": "Maximum events to return",
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
    Tool(
        name="get_audit_summary",
        description="[I-043] Returns an aggregated summary of audit events, including event counts by type, top actors, and trend data.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Scope to a specific project (omit for fleet-wide)",
                },
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 90,
                    "default": 7,
                    "description": "Number of days to summarize",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="export_audit_report",
        description="[I-044] Exports a formatted audit report for compliance purposes (CSV, JSON, PDF).",
        inputSchema={
            "type": "object",
            "required": ["format"],
            "properties": {
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Scope to a specific project (omit for fleet-wide)",
                },
                "format": {
                    "type": "string",
                    "enum": ["csv", "json", "pdf"],
                    "description": "Export file format",
                },
                "period": {
                    "type": "object",
                    "required": ["start", "end"],
                    "properties": {
                        "start": {"type": "string", "format": "date-time"},
                        "end": {"type": "string", "format": "date-time"},
                    },
                },
                "include_details": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include full event details in the export",
                },
            },
            "additionalProperties": False,
        },
    ),
    # --- ApprovalService tools ---
    Tool(
        name="list_pending_approvals",
        description="[I-045] Lists all pending gate approval requests, optionally filtered by project or gate type.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Filter by project",
                },
                "gate_type": {
                    "type": "string",
                    "enum": ["quality", "architecture", "security", "cost", "deployment"],
                    "description": "Filter by gate type",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                    "description": "Maximum approvals to return",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="approve_gate",
        description="[I-046] Approves a pending gate, allowing the associated pipeline to proceed.",
        inputSchema={
            "type": "object",
            "required": ["approval_id"],
            "properties": {
                "approval_id": {
                    "type": "string",
                    "pattern": "^appr_[a-z0-9]{16}$",
                    "description": "Approval request identifier",
                },
                "comment": {
                    "type": "string",
                    "maxLength": 2000,
                    "description": "Optional reviewer comment",
                },
                "conditions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Conditions attached to the approval",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="reject_gate",
        description="[I-047] Rejects a pending gate, pausing the pipeline and requiring revision.",
        inputSchema={
            "type": "object",
            "required": ["approval_id", "reason"],
            "properties": {
                "approval_id": {
                    "type": "string",
                    "pattern": "^appr_[a-z0-9]{16}$",
                    "description": "Approval request identifier",
                },
                "reason": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 2000,
                    "description": "Reason for rejection",
                },
                "suggested_changes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific changes requested before re-approval",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="get_cost_anomalies",
        description="[I-048] Detects and returns cost anomalies based on historical patterns.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Filter by project (omit for fleet-wide)",
                },
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Minimum severity threshold",
                },
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 30,
                    "default": 7,
                    "description": "Look-back window in days",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "Maximum anomalies to return",
                },
            },
            "additionalProperties": False,
        },
    ),
    Tool(
        name="update_budget_threshold",
        description="[I-049] Updates the budget alert threshold for a project or the fleet.",
        inputSchema={
            "type": "object",
            "required": ["threshold_percent"],
            "properties": {
                "project_id": {
                    "type": "string",
                    "pattern": "^proj_[a-z0-9]{12}$",
                    "description": "Project to update (omit for fleet-wide threshold)",
                },
                "threshold_percent": {
                    "type": "integer",
                    "minimum": 50,
                    "maximum": 100,
                    "description": "Alert threshold as percentage of budget",
                },
                "budget_usd": {
                    "type": "number",
                    "minimum": 1.0,
                    "maximum": 10000.0,
                    "description": "Optionally update the total budget amount",
                },
                "notification_channels": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["email", "slack", "webhook"]},
                    "description": "Channels to notify when threshold is breached",
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
    # --- CostService ---
    if name == "get_cost_report":
        return await _cost_service.get_report(**arguments)
    if name == "check_budget":
        return await _cost_service.check_budget(**arguments)
    if name == "get_cost_anomalies":
        return await _cost_service.get_anomalies(**arguments)
    if name == "update_budget_threshold":
        return await _cost_service.update_budget_threshold(**arguments)

    # --- AuditService ---
    if name == "query_audit_events":
        return await _audit_service.query_events(**arguments)
    if name == "get_audit_summary":
        return await _audit_service.get_summary(**arguments)
    if name == "export_audit_report":
        return await _audit_service.export_report(**arguments)

    # --- ApprovalService ---
    if name == "list_pending_approvals":
        return await _approval_service.list_pending(**arguments)
    if name == "approve_gate":
        return await _approval_service.approve(**arguments)
    if name == "reject_gate":
        return await _approval_service.reject(**arguments)

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
