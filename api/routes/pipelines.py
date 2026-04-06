"""Pipeline route handlers (I-001 through I-009).

Thin wrappers around PipelineService. No business logic here.
"""
from uuid import UUID

from aiohttp import web

from . import success_response


# ---------------------------------------------------------------------------
# I-001  POST /api/v1/pipelines  -- trigger a new pipeline run
# ---------------------------------------------------------------------------
async def trigger_pipeline(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    body = await request.json()
    result = await svc.trigger(
        project_id=body["project_id"],
        pipeline_name=body["pipeline_name"],
        brief=body["brief"],
        triggered_by=body.get("triggered_by", "system"),
    )
    return success_response(result.model_dump(mode="json"), status=201)


# ---------------------------------------------------------------------------
# I-003  GET /api/v1/pipelines  -- list pipeline runs
# ---------------------------------------------------------------------------
async def list_pipelines(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    project_id = request.query.get("project_id")
    status_filter = request.query.get("status")
    limit = int(request.query.get("limit", 20))
    offset = int(request.query.get("offset", 0))
    results = await svc.list_runs(
        project_id=project_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return success_response(
        [r.model_dump(mode="json") for r in results],
        meta={"limit": limit, "offset": offset},
    )


# ---------------------------------------------------------------------------
# I-002  GET /api/v1/pipelines/{run_id}  -- get pipeline status
# ---------------------------------------------------------------------------
async def get_pipeline_status(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    run_id = UUID(request.match_info["run_id"])
    result = await svc.get_status(run_id=run_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-004  POST /api/v1/pipelines/{run_id}/resume  -- resume paused run
# ---------------------------------------------------------------------------
async def resume_pipeline(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    run_id = UUID(request.match_info["run_id"])
    result = await svc.resume(run_id=run_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-005  POST /api/v1/pipelines/{run_id}/cancel  -- cancel run
# ---------------------------------------------------------------------------
async def cancel_pipeline(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    run_id = UUID(request.match_info["run_id"])
    result = await svc.cancel(run_id=run_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-006  GET /api/v1/pipelines/{run_id}/documents  -- get documents
# ---------------------------------------------------------------------------
async def get_pipeline_documents(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    run_id = UUID(request.match_info["run_id"])
    results = await svc.get_documents(run_id=run_id)
    return success_response([r.model_dump(mode="json") for r in results])


# ---------------------------------------------------------------------------
# I-007  POST /api/v1/pipelines/{run_id}/steps/{step}/retry  -- retry step
# ---------------------------------------------------------------------------
async def retry_step(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    run_id = UUID(request.match_info["run_id"])
    step = request.match_info["step"]
    # retry_step not a separate method — update step status to pending then return run
    await svc.update_step_status(run_id=run_id, step=step, status="pending")
    result = await svc.get_status(run_id=run_id)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-008  GET /api/v1/pipelines/config/{pipeline_name}  -- get config
# ---------------------------------------------------------------------------
async def get_pipeline_config(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    pipeline_name = request.match_info["pipeline_name"]
    result = await svc.get_config(pipeline_name=pipeline_name)
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# I-009  POST /api/v1/pipelines/validate  -- validate pipeline input
# ---------------------------------------------------------------------------
async def validate_pipeline_input(request: web.Request) -> web.Response:
    svc = request.app["pipeline_service"]
    body = await request.json()
    result = await svc.validate_input(
        project_id=body["project_id"],
        pipeline_name=body["pipeline_name"],
        brief=body["brief"],
    )
    return success_response(result.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
def setup_routes(app: web.Application) -> None:
    app.router.add_post("/api/v1/pipelines", trigger_pipeline)
    app.router.add_get("/api/v1/pipelines", list_pipelines)
    app.router.add_get("/api/v1/pipelines/{run_id}", get_pipeline_status)
    app.router.add_post("/api/v1/pipelines/{run_id}/resume", resume_pipeline)
    app.router.add_post("/api/v1/pipelines/{run_id}/cancel", cancel_pipeline)
    app.router.add_get("/api/v1/pipelines/{run_id}/documents", get_pipeline_documents)
    app.router.add_post("/api/v1/pipelines/{run_id}/steps/{step}/retry", retry_step)
    app.router.add_get("/api/v1/pipelines/config/{pipeline_name}", get_pipeline_config)
    app.router.add_post("/api/v1/pipelines/validate", validate_pipeline_input)
