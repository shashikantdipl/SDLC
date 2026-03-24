"""Audit route handlers (I-042, I-043, I-044, I-082)."""
from aiohttp import web

from . import success_response


# ---------------------------------------------------------------------------
# I-042  GET /api/v1/audit/events  -- query audit events
# ---------------------------------------------------------------------------
async def query_audit_events(request: web.Request) -> web.Response:
    svc = request.app["audit_service"]
    project_id = request.query.get("project_id")
    severity = request.query.get("severity")
    agent_id = request.query.get("agent_id")
    limit = int(request.query.get("limit", 50))
    offset = int(request.query.get("offset", 0))
    results = await svc.query_events(
        project_id=project_id,
        severity=severity,
        agent_id=agent_id,
        limit=limit,
        offset=offset,
    )
    return success_response(
        [r.model_dump(mode="json") for r in results],
        meta={"limit": limit, "offset": offset},
    )


# ---------------------------------------------------------------------------
# I-043  GET /api/v1/audit/summary  -- audit summary
# ---------------------------------------------------------------------------
async def get_audit_summary(request: web.Request) -> web.Response:
    svc = request.app["audit_service"]
    project_id = request.query.get("project_id")
    period_days = int(request.query.get("period_days", 30))
    result = await svc.get_summary(
        project_id=project_id,
        period_days=period_days,
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-044  GET /api/v1/audit/export  -- export audit report
# ---------------------------------------------------------------------------
async def export_audit_report(request: web.Request) -> web.Response:
    svc = request.app["audit_service"]
    project_id = request.query.get("project_id")
    period_days = int(request.query.get("period_days", 30))
    result = await svc.export_report(
        project_id=project_id,
        period_days=period_days,
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-082  GET /api/v1/audit/mcp-calls  -- recent MCP calls
# ---------------------------------------------------------------------------
async def get_recent_mcp_calls(request: web.Request) -> web.Response:
    svc = request.app["audit_service"]
    limit = int(request.query.get("limit", 50))
    server_name = request.query.get("server_name")
    results = await svc.get_recent_mcp_calls(
        limit=limit,
        server_name=server_name,
    )
    return success_response(
        [r.model_dump(mode="json") for r in results],
        meta={"limit": limit},
    )


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
def setup_routes(app: web.Application) -> None:
    app.router.add_get("/api/v1/audit/events", query_audit_events)
    app.router.add_get("/api/v1/audit/summary", get_audit_summary)
    app.router.add_get("/api/v1/audit/export", export_audit_report)
    app.router.add_get("/api/v1/audit/mcp-calls", get_recent_mcp_calls)
