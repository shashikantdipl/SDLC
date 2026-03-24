"""Authentication middleware — API key via X-API-Key header.

Skips auth for health endpoints.
In production, validates against stored API keys.
For development, accepts any non-empty key.
"""
from aiohttp import web
from aiohttp.web import middleware
import os

API_KEY = os.environ.get("API_KEY", "dev-api-key")
SKIP_AUTH_PATHS = {"/api/v1/health", "/api/v1/system/health"}

@middleware
async def auth_middleware(request, handler):
    if request.path in SKIP_AUTH_PATHS or request.path == "/":
        return await handler(request)

    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return web.json_response(
            {"error": {"code": "UNAUTHORIZED", "message": "X-API-Key header required"}},
            status=401,
        )
    if api_key != API_KEY:
        return web.json_response(
            {"error": {"code": "FORBIDDEN", "message": "Invalid API key"}},
            status=403,
        )
    return await handler(request)
