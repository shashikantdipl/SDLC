"""Route helpers -- standard response envelope."""
from aiohttp import web
import uuid as _uuid
from datetime import datetime, timezone


def success_response(data, status=200, meta=None):
    """Return a standard JSON envelope with data + meta."""
    body = {
        "data": data,
        "meta": {
            "request_id": str(_uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(meta or {}),
        },
    }
    return web.json_response(body, status=status)
