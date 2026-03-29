"""Agent route handlers (I-020 through I-027).

Thin wrappers around AgentService. No business logic here.
"""
from aiohttp import web
import json

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
    # Service expects input_text (string), not action+params
    input_text = json.dumps(body) if not isinstance(body.get("input_text"), str) else body["input_text"]
    result = await svc.invoke_agent(
        agent_id=agent_id,
        input_text=input_text,
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-023  GET /api/v1/agents/{agent_id}/health  -- agent health
# ---------------------------------------------------------------------------
async def get_agent_health(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    result = await svc.check_health(agent_id=agent_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-024  POST /api/v1/agents/{agent_id}/promote  -- promote agent version
# ---------------------------------------------------------------------------
async def promote_agent(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    body = await request.json()
    result = await svc.promote_version(
        agent_id=agent_id,
        new_version=body["new_version"],
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-025  POST /api/v1/agents/{agent_id}/rollback  -- rollback agent version
# ---------------------------------------------------------------------------
async def rollback_agent(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    result = await svc.rollback_version(agent_id=agent_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-026  PATCH /api/v1/agents/{agent_id}/canary  -- set canary traffic
# ---------------------------------------------------------------------------
async def set_canary(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    body = await request.json()
    result = await svc.set_canary_traffic(
        agent_id=agent_id,
        percentage=body["percentage"],
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-027  GET /api/v1/agents/{agent_id}/maturity  -- maturity status
# ---------------------------------------------------------------------------
async def get_agent_maturity(request: web.Request) -> web.Response:
    svc = request.app["agent_service"]
    agent_id = request.match_info["agent_id"]
    result = await svc.get_maturity(agent_id=agent_id)
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
