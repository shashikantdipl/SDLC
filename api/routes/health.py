"""System health route handlers (I-080, I-081)."""
from aiohttp import web

from . import success_response


# ---------------------------------------------------------------------------
# I-080  GET /api/v1/system/health  -- fleet health
# ---------------------------------------------------------------------------
async def get_fleet_health(request: web.Request) -> web.Response:
    svc = request.app["health_service"]
    result = await svc.get_fleet_health()
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-081  GET /api/v1/system/mcp  -- MCP server status
# ---------------------------------------------------------------------------
async def get_mcp_status(request: web.Request) -> web.Response:
    svc = request.app["health_service"]
    result = await svc.get_mcp_status()
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
def setup_routes(app: web.Application) -> None:
    app.router.add_get("/api/v1/system/health", get_fleet_health)
    app.router.add_get("/api/v1/system/mcp", get_mcp_status)
