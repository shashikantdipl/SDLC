"""Approval route handlers (I-045, I-046, I-047)."""
from aiohttp import web

from . import success_response


# ---------------------------------------------------------------------------
# I-045  GET /api/v1/approvals  -- list pending approvals
# ---------------------------------------------------------------------------
async def list_pending_approvals(request: web.Request) -> web.Response:
    svc = request.app["approval_service"]
    project_id = request.query.get("project_id")
    results = await svc.list_pending(project_id=project_id)
    return success_response([r.model_dump(mode="json") for r in results])


# ---------------------------------------------------------------------------
# I-046  POST /api/v1/approvals/{approval_id}/approve  -- approve
# ---------------------------------------------------------------------------
async def approve(request: web.Request) -> web.Response:
    svc = request.app["approval_service"]
    approval_id = request.match_info["approval_id"]
    body = await request.json()
    result = await svc.approve(
        approval_id=approval_id,
        decision_by=body["decision_by"],
        comment=body.get("comment"),
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-047  POST /api/v1/approvals/{approval_id}/reject  -- reject
# ---------------------------------------------------------------------------
async def reject(request: web.Request) -> web.Response:
    svc = request.app["approval_service"]
    approval_id = request.match_info["approval_id"]
    body = await request.json()
    result = await svc.reject(
        approval_id=approval_id,
        decision_by=body["decision_by"],
        reason=body["reason"],
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
def setup_routes(app: web.Application) -> None:
    app.router.add_get("/api/v1/approvals", list_pending_approvals)
    app.router.add_post("/api/v1/approvals/{approval_id}/approve", approve)
    app.router.add_post("/api/v1/approvals/{approval_id}/reject", reject)
