"""MCP agents-server — Pipeline + Agent operations.

Port: 3100 (stdio for local dev, streamable-http for production)
Tools: 18 (I-001 to I-009 pipeline, I-020 to I-027 agent, I-080 fleet_health)
All tools call shared services — NO business logic here.
"""

from __future__ import annotations

import json
from uuid import UUID

from mcp.server import Server
from mcp.types import TextContent, Tool

from services.pipeline_service import PipelineNotFoundError, PipelineStateError
from services.agent_service import AgentNotFoundError

# Create MCP server
server = Server("agentic-sdlc-agents")

# Services will be injected at startup
_pipeline_service = None
_agent_service = None
_health_service = None


def init_services(pipeline_service, agent_service, health_service):
    """Inject shared service instances (called once at startup)."""
    global _pipeline_service, _agent_service, _health_service
    _pipeline_service = pipeline_service
    _agent_service = agent_service
    _health_service = health_service


# ======================================================================
# Tool Definitions
# ======================================================================

PIPELINE_TOOLS = [
    Tool(
        name="trigger_pipeline",
        description="I-001: Trigger a new pipeline run for a project.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Target project identifier"},
                "pipeline_name": {"type": "string", "description": "Pipeline template name (e.g. document-stack)"},
                "brief": {"type": "string", "description": "Build brief / requirements text"},
                "triggered_by": {"type": "string", "description": "Who triggered this run", "default": "system"},
            },
            "required": ["project_id", "pipeline_name", "brief"],
        },
    ),
    Tool(
        name="get_pipeline_status",
        description="I-002: Get the current status of a pipeline run.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "format": "uuid", "description": "Pipeline run ID"},
            },
            "required": ["run_id"],
        },
    ),
    Tool(
        name="list_pipeline_runs",
        description="I-003: List pipeline runs for a project, optionally filtered by status.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Project identifier"},
                "status": {"type": "string", "description": "Filter by status (pending, running, paused, completed, failed)"},
                "limit": {"type": "integer", "description": "Max results to return", "default": 50},
            },
            "required": ["project_id"],
        },
    ),
    Tool(
        name="resume_pipeline",
        description="I-004: Resume a paused pipeline from its checkpoint.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "format": "uuid", "description": "Pipeline run ID"},
            },
            "required": ["run_id"],
        },
    ),
    Tool(
        name="cancel_pipeline",
        description="I-005: Cancel a running or paused pipeline.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "format": "uuid", "description": "Pipeline run ID"},
            },
            "required": ["run_id"],
        },
    ),
    Tool(
        name="get_pipeline_documents",
        description="I-006: Get all generated documents for a pipeline run.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "format": "uuid", "description": "Pipeline run ID"},
            },
            "required": ["run_id"],
        },
    ),
    Tool(
        name="retry_pipeline_step",
        description="I-007: Retry a specific step in a pipeline run.",
        inputSchema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string", "format": "uuid", "description": "Pipeline run ID"},
                "step_number": {"type": "integer", "description": "Step number to retry"},
            },
            "required": ["run_id", "step_number"],
        },
    ),
    Tool(
        name="get_pipeline_config",
        description="I-008: Get pipeline configuration (steps, parallel groups, gates).",
        inputSchema={
            "type": "object",
            "properties": {
                "pipeline_name": {"type": "string", "description": "Pipeline template name"},
            },
            "required": ["pipeline_name"],
        },
    ),
    Tool(
        name="validate_pipeline_input",
        description="I-009: Validate pipeline input before triggering.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "Target project identifier"},
                "pipeline_name": {"type": "string", "description": "Pipeline template name"},
                "brief": {"type": "string", "description": "Build brief / requirements text"},
            },
            "required": ["project_id", "pipeline_name", "brief"],
        },
    ),
]

AGENT_TOOLS = [
    Tool(
        name="list_agents",
        description="I-020: List all agents, optionally filtered by phase and/or status.",
        inputSchema={
            "type": "object",
            "properties": {
                "phase": {"type": "string", "description": "Filter by SDLC phase (govern, design, build, test, deploy, operate, oversight)"},
                "status": {"type": "string", "description": "Filter by status (active, inactive, degraded, error)"},
            },
            "required": [],
        },
    ),
    Tool(
        name="get_agent",
        description="I-021: Get full detail for a single agent.",
        inputSchema={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent identifier"},
            },
            "required": ["agent_id"],
        },
    ),
    Tool(
        name="invoke_agent",
        description="I-022: Invoke an agent with input text and return the result.",
        inputSchema={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent identifier"},
                "input_text": {"type": "string", "description": "Input text for the agent"},
                "project_id": {"type": "string", "description": "Optional project context"},
            },
            "required": ["agent_id", "input_text"],
        },
    ),
    Tool(
        name="check_agent_health",
        description="I-023: Return health status for a single agent.",
        inputSchema={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent identifier"},
            },
            "required": ["agent_id"],
        },
    ),
    Tool(
        name="promote_agent_version",
        description="I-024: Promote an agent to a new version.",
        inputSchema={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent identifier"},
                "new_version": {"type": "string", "description": "Semantic version string (e.g. 1.2.0)"},
            },
            "required": ["agent_id", "new_version"],
        },
    ),
    Tool(
        name="rollback_agent_version",
        description="I-025: Roll back an agent to its previous version.",
        inputSchema={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent identifier"},
            },
            "required": ["agent_id"],
        },
    ),
    Tool(
        name="set_canary_traffic",
        description="I-026: Set canary traffic percentage for an agent (0-100).",
        inputSchema={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent identifier"},
                "percentage": {"type": "integer", "description": "Traffic percentage (0-100)", "minimum": 0, "maximum": 100},
            },
            "required": ["agent_id", "percentage"],
        },
    ),
    Tool(
        name="get_agent_maturity",
        description="I-027: Return the maturity level and stats for an agent.",
        inputSchema={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent identifier"},
            },
            "required": ["agent_id"],
        },
    ),
]

SYSTEM_TOOLS = [
    Tool(
        name="get_fleet_health",
        description="I-080: Get aggregate fleet health across all agents.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]

ALL_TOOLS = PIPELINE_TOOLS + AGENT_TOOLS + SYSTEM_TOOLS


# ======================================================================
# Tool Registration
# ======================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return all 18 registered tools."""
    return ALL_TOOLS


# ======================================================================
# Tool Dispatch
# ======================================================================

def _error_response(code: str, message: str) -> list[TextContent]:
    """Build a structured error response."""
    return [TextContent(type="text", text=json.dumps({"error": True, "code": code, "message": message}))]


def _json_list_response(items) -> list[TextContent]:
    """Serialize a list of Pydantic models to JSON array."""
    return [TextContent(type="text", text=json.dumps([json.loads(item.model_dump_json()) for item in items]))]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch tool calls to the appropriate service method."""

    # ------------------------------------------------------------------
    # Pipeline Tools (I-001 to I-009)
    # ------------------------------------------------------------------

    if name == "trigger_pipeline":
        try:
            result = await _pipeline_service.trigger(
                project_id=arguments["project_id"],
                pipeline_name=arguments["pipeline_name"],
                brief=arguments["brief"],
                triggered_by=arguments.get("triggered_by", "system"),
            )
            return [TextContent(type="text", text=result.model_dump_json())]
        except ValueError as e:
            return _error_response("INVALID_PIPELINE", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "get_pipeline_status":
        try:
            result = await _pipeline_service.get_status(run_id=UUID(arguments["run_id"]))
            return [TextContent(type="text", text=result.model_dump_json())]
        except PipelineNotFoundError as e:
            return _error_response("PIPELINE_NOT_FOUND", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "list_pipeline_runs":
        try:
            result = await _pipeline_service.list_runs(
                project_id=arguments["project_id"],
                status=arguments.get("status"),
                limit=arguments.get("limit", 50),
            )
            return _json_list_response(result)
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "resume_pipeline":
        try:
            result = await _pipeline_service.resume(run_id=UUID(arguments["run_id"]))
            return [TextContent(type="text", text=result.model_dump_json())]
        except PipelineNotFoundError as e:
            return _error_response("PIPELINE_NOT_FOUND", str(e))
        except PipelineStateError as e:
            return _error_response("PIPELINE_STATE_ERROR", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "cancel_pipeline":
        try:
            result = await _pipeline_service.cancel(run_id=UUID(arguments["run_id"]))
            return [TextContent(type="text", text=result.model_dump_json())]
        except PipelineNotFoundError as e:
            return _error_response("PIPELINE_NOT_FOUND", str(e))
        except PipelineStateError as e:
            return _error_response("PIPELINE_STATE_ERROR", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "get_pipeline_documents":
        try:
            result = await _pipeline_service.get_documents(run_id=UUID(arguments["run_id"]))
            return _json_list_response(result)
        except PipelineNotFoundError as e:
            return _error_response("PIPELINE_NOT_FOUND", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "retry_pipeline_step":
        try:
            # Reset the step status to 'pending' so the orchestrator re-runs it
            run_id = UUID(arguments["run_id"])
            step_number = arguments["step_number"]
            await _pipeline_service.update_step_status(
                run_id=run_id,
                step_number=step_number,
                status="pending",
            )
            result = await _pipeline_service.get_status(run_id=run_id)
            return [TextContent(type="text", text=result.model_dump_json())]
        except PipelineNotFoundError as e:
            return _error_response("PIPELINE_NOT_FOUND", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "get_pipeline_config":
        try:
            result = await _pipeline_service.get_config(pipeline_name=arguments["pipeline_name"])
            return [TextContent(type="text", text=result.model_dump_json())]
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "validate_pipeline_input":
        try:
            result = await _pipeline_service.validate_input(
                project_id=arguments["project_id"],
                pipeline_name=arguments["pipeline_name"],
                brief=arguments["brief"],
            )
            return [TextContent(type="text", text=result.model_dump_json())]
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    # ------------------------------------------------------------------
    # Agent Tools (I-020 to I-027)
    # ------------------------------------------------------------------

    elif name == "list_agents":
        try:
            result = await _agent_service.list_agents(
                phase=arguments.get("phase"),
                status=arguments.get("status"),
            )
            return _json_list_response(result)
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "get_agent":
        try:
            result = await _agent_service.get_agent(agent_id=arguments["agent_id"])
            return [TextContent(type="text", text=result.model_dump_json())]
        except AgentNotFoundError as e:
            return _error_response("AGENT_NOT_FOUND", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "invoke_agent":
        try:
            result = await _agent_service.invoke_agent(
                agent_id=arguments["agent_id"],
                input_text=arguments["input_text"],
            )
            return [TextContent(type="text", text=result.model_dump_json())]
        except AgentNotFoundError as e:
            return _error_response("AGENT_NOT_FOUND", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "check_agent_health":
        try:
            result = await _agent_service.check_health(agent_id=arguments["agent_id"])
            return [TextContent(type="text", text=result.model_dump_json())]
        except AgentNotFoundError as e:
            return _error_response("AGENT_NOT_FOUND", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "promote_agent_version":
        try:
            result = await _agent_service.promote_version(
                agent_id=arguments["agent_id"],
                new_version=arguments["new_version"],
            )
            return [TextContent(type="text", text=result.model_dump_json())]
        except AgentNotFoundError as e:
            return _error_response("AGENT_NOT_FOUND", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "rollback_agent_version":
        try:
            result = await _agent_service.rollback_version(agent_id=arguments["agent_id"])
            return [TextContent(type="text", text=result.model_dump_json())]
        except AgentNotFoundError as e:
            return _error_response("AGENT_NOT_FOUND", str(e))
        except ValueError as e:
            return _error_response("ROLLBACK_ERROR", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "set_canary_traffic":
        try:
            result = await _agent_service.set_canary_traffic(
                agent_id=arguments["agent_id"],
                percentage=arguments["percentage"],
            )
            return [TextContent(type="text", text=result.model_dump_json())]
        except AgentNotFoundError as e:
            return _error_response("AGENT_NOT_FOUND", str(e))
        except ValueError as e:
            return _error_response("INVALID_PERCENTAGE", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    elif name == "get_agent_maturity":
        try:
            result = await _agent_service.get_maturity(agent_id=arguments["agent_id"])
            return [TextContent(type="text", text=result.model_dump_json())]
        except AgentNotFoundError as e:
            return _error_response("AGENT_NOT_FOUND", str(e))
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    # ------------------------------------------------------------------
    # System Tools (I-080)
    # ------------------------------------------------------------------

    elif name == "get_fleet_health":
        try:
            result = await _health_service.get_fleet_health()
            return [TextContent(type="text", text=result.model_dump_json())]
        except Exception as e:
            return _error_response("INTERNAL_ERROR", str(e))

    # ------------------------------------------------------------------
    # Unknown tool
    # ------------------------------------------------------------------

    else:
        return _error_response("UNKNOWN_TOOL", f"Tool '{name}' is not registered on this server.")


# ======================================================================
# Entry Point
# ======================================================================

async def main():
    """Run the MCP server over stdio (local dev)."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
