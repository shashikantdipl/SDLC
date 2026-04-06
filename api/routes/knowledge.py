"""Knowledge-base / exceptions route handlers (I-060 through I-063)."""
from aiohttp import web

from . import success_response


# ---------------------------------------------------------------------------
# I-060  GET /api/v1/knowledge/exceptions  -- search exceptions
# ---------------------------------------------------------------------------
async def search_exceptions(request: web.Request) -> web.Response:
    svc = request.app["knowledge_service"]
    query = request.query.get("query", "")
    tier = request.query.get("tier")
    limit = int(request.query.get("limit", 20))
    results = await svc.search(
        query=query,
        tier=tier,
        limit=limit,
    )
    return success_response(
        [r.model_dump(mode="json") for r in results],
        meta={"limit": limit},
    )


# ---------------------------------------------------------------------------
# I-061  POST /api/v1/knowledge/exceptions  -- create exception
# ---------------------------------------------------------------------------
async def create_exception(request: web.Request) -> web.Response:
    svc = request.app["knowledge_service"]
    body = await request.json()
    result = await svc.create_exception(
        title=body["title"],
        rule=body["rule"],
        severity=body["severity"],
        tier=body["tier"],
        created_by=body["created_by"],
        metadata=body.get("metadata", {}),
    )
    return success_response(result.model_dump(mode="json"), status=201)


# ---------------------------------------------------------------------------
# I-062  POST /api/v1/knowledge/exceptions/{exception_id}/promote  -- promote
# ---------------------------------------------------------------------------
async def promote_exception(request: web.Request) -> web.Response:
    svc = request.app["knowledge_service"]
    exception_id = request.match_info["exception_id"]
    body = await request.json()
    result = await svc.promote(
        exception_id=exception_id,
        target_tier=body["target_tier"],
        promoted_by=body["promoted_by"],
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-063  GET /api/v1/knowledge/exceptions/list  -- list by tier
# ---------------------------------------------------------------------------
async def list_exceptions_by_tier(request: web.Request) -> web.Response:
    svc = request.app["knowledge_service"]
    tier = request.query.get("tier")
    active_only = request.query.get("active_only", "true").lower() == "true"
    limit = int(request.query.get("limit", 50))
    results = await svc.list_exceptions(
        tier=tier,
        active_only=active_only,
        limit=limit,
    )
    return success_response(
        [r.model_dump(mode="json") for r in results],
        meta={"limit": limit, "active_only": active_only},
    )


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
def setup_routes(app: web.Application) -> None:
    app.router.add_get("/api/v1/knowledge/exceptions", search_exceptions)
    app.router.add_post("/api/v1/knowledge/exceptions", create_exception)
    app.router.add_post("/api/v1/knowledge/exceptions/{exception_id}/promote", promote_exception)
    app.router.add_get("/api/v1/knowledge/exceptions/list", list_exceptions_by_tier)
