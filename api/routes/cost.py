"""Cost and budget route handlers (I-040, I-041, I-048, I-049)."""
from aiohttp import web

from . import success_response


# ---------------------------------------------------------------------------
# I-040  GET /api/v1/cost/report  -- cost report
# ---------------------------------------------------------------------------
async def get_cost_report(request: web.Request) -> web.Response:
    svc = request.app["cost_service"]
    scope = request.query.get("scope", "project")
    scope_id = request.query.get("scope_id")
    period_days = int(request.query.get("period_days", 30))
    result = await svc.get_cost_report(
        scope=scope,
        scope_id=scope_id,
        period_days=period_days,
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-041  GET /api/v1/budget/{scope}/{scope_id}  -- check budget
# ---------------------------------------------------------------------------
async def check_budget(request: web.Request) -> web.Response:
    svc = request.app["cost_service"]
    scope = request.match_info["scope"]
    scope_id = request.match_info["scope_id"]
    result = await svc.check_budget(scope=scope, scope_id=scope_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-048  GET /api/v1/cost/anomalies  -- cost anomalies
# ---------------------------------------------------------------------------
async def get_cost_anomalies(request: web.Request) -> web.Response:
    svc = request.app["cost_service"]
    project_id = request.query.get("project_id")
    results = await svc.get_cost_anomalies(project_id=project_id)
    return success_response([r.model_dump(mode="json") for r in results])


# ---------------------------------------------------------------------------
# I-049  PATCH /api/v1/budget/{scope}/{scope_id}/threshold  -- update threshold
# ---------------------------------------------------------------------------
async def update_budget_threshold(request: web.Request) -> web.Response:
    svc = request.app["cost_service"]
    scope = request.match_info["scope"]
    scope_id = request.match_info["scope_id"]
    body = await request.json()
    result = await svc.update_budget_threshold(
        scope=scope,
        scope_id=scope_id,
        threshold=body["threshold"],
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
def setup_routes(app: web.Application) -> None:
    app.router.add_get("/api/v1/cost/report", get_cost_report)
    app.router.add_get("/api/v1/budget/{scope}/{scope_id}", check_budget)
    app.router.add_get("/api/v1/cost/anomalies", get_cost_anomalies)
    app.router.add_patch("/api/v1/budget/{scope}/{scope_id}/threshold", update_budget_threshold)
