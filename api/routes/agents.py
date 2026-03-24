"""Agent route handlers (I-020 through I-027)."""
from aiohttp import web

from . import success_response


# ---------------------------------------------------------------------------
# I-020  GET /api/v1/agents  -- list agents
# ---------------------------------------------------------------------------
async def list_agents(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    phase = request.query.get("phase")
    status = request.query.get("status")
    results = await svc.list_agents(phase=phase, status=status)
    return success_response([r.model_dump(mode="json") for r in results])


# ---------------------------------------------------------------------------
# I-021  GET /api/v1/agents/{agent_id}  -- agent detail
# ---------------------------------------------------------------------------
async def get_agent(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    result = await svc.get_agent(agent_id=agent_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-022  POST /api/v1/agents/{agent_id}/invoke  -- invoke agent
# ---------------------------------------------------------------------------
async def invoke_agent(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    body = await request.json()
    result = await svc.invoke_agent(
        agent_id=agent_id,
        action=body["action"],
        params=body.get("params", {}),
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-023  GET /api/v1/agents/{agent_id}/health  -- agent health
# ---------------------------------------------------------------------------
async def get_agent_health(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    result = await svc.get_agent_health(agent_id=agent_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-024  POST /api/v1/agents/{agent_id}/promote  -- promote agent
# ---------------------------------------------------------------------------
async def promote_agent(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    body = await request.json()
    result = await svc.promote_agent(
        agent_id=agent_id,
        target_level=body["target_level"],
        promoted_by=body.get("promoted_by"),
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-025  POST /api/v1/agents/{agent_id}/rollback  -- rollback agent
# ---------------------------------------------------------------------------
async def rollback_agent(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    body = await request.json()
    result = await svc.rollback_agent(
        agent_id=agent_id,
        target_version=body.get("target_version"),
        reason=body.get("reason"),
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-026  PATCH /api/v1/agents/{agent_id}/canary  -- set canary weight
# ---------------------------------------------------------------------------
async def set_canary(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    body = await request.json()
    result = await svc.set_canary(
        agent_id=agent_id,
        weight=body["weight"],
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-027  GET /api/v1/agents/{agent_id}/maturity  -- maturity status
# ---------------------------------------------------------------------------
async def get_agent_maturity(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    result = await svc.get_agent_maturity(agent_id=agent_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
def setup_routes(app: web.Application) -> None:
    app.router.add_get("/api/v1/agents", list_agents)
    app.router.add_get("/api/v1/agents/{agent_id}", get_agent)
    app.router.add_post("/api/v1/agents/{agent_id}/invoke", invoke_agent)
    app.router.add_get("/api/v1/agents/{agent_id}/health", get_agent_health)
    app.router.add_post("/api/v1/agents/{agent_id}/promote", promote_agent)
    app.router.add_post("/api/v1/agents/{agent_id}/rollback", rollback_agent)
    app.router.add_patch("/api/v1/agents/{agent_id}/canary", set_canary)
    app.router.add_get("/api/v1/agents/{agent_id}/maturity", get_agent_maturity)
