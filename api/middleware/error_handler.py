"""Error handling middleware — standard error envelope.

All errors return:
{
    "error": {"code": "ERROR_CODE", "message": "Human-readable message", "details": {}},
    "meta": {"request_id": "uuid", "timestamp": "ISO8601"}
}
"""
from aiohttp import web
from aiohttp.web import middleware
import json
import uuid
from datetime import datetime, timezone

# Map service exceptions to HTTP status + error codes
ERROR_MAP = {
    "PipelineNotFoundError": (404, "PIPELINE_NOT_FOUND"),
    "PipelineStateError": (409, "PIPELINE_STATE_ERROR"),
    "AgentNotFoundError": (404, "AGENT_NOT_FOUND"),
    "ApprovalNotFoundError": (404, "APPROVAL_NOT_FOUND"),
    "ApprovalStateError": (409, "APPROVAL_STATE_ERROR"),
    "BudgetExceededError": (402, "BUDGET_EXCEEDED"),
    "ValueError": (400, "VALIDATION_ERROR"),
    "KeyError": (400, "MISSING_PARAMETER"),
}

@middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException:
        raise  # Let aiohttp handle its own HTTP exceptions
    except Exception as exc:
        exc_name = type(exc).__name__
        status, code = ERROR_MAP.get(exc_name, (500, "INTERNAL_ERROR"))
        return web.json_response(
            {
                "error": {"code": code, "message": str(exc), "details": {}},
                "meta": {"request_id": str(uuid.uuid4()), "timestamp": datetime.now(timezone.utc).isoformat()},
            },
            status=status,
        )
