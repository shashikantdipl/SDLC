"""REST API client — all dashboard data fetched through this module.

This is the ONLY module that makes HTTP calls. Dashboard pages
call these functions instead of importing services directly.
"""
import httpx
from dashboard.config import API_BASE, API_KEY

_HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
_TIMEOUT = 10.0


def api_get(path: str, params: dict | None = None) -> dict:
    """GET request to REST API. Returns parsed JSON body."""
    try:
        resp = httpx.get(f"{API_BASE}{path}", headers=_HEADERS, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": {"code": "API_ERROR", "message": str(e)}, "data": None}
    except httpx.ConnectError:
        return {"error": {"code": "API_UNAVAILABLE", "message": "REST API is not reachable"}, "data": None}


def api_post(path: str, body: dict | None = None) -> dict:
    """POST request to REST API."""
    try:
        resp = httpx.post(f"{API_BASE}{path}", headers=_HEADERS, json=body or {}, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": {"code": "API_ERROR", "message": str(e)}, "data": None}
    except httpx.ConnectError:
        return {"error": {"code": "API_UNAVAILABLE", "message": "REST API is not reachable"}, "data": None}


def api_patch(path: str, body: dict | None = None) -> dict:
    """PATCH request to REST API."""
    try:
        resp = httpx.patch(f"{API_BASE}{path}", headers=_HEADERS, json=body or {}, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": {"code": "API_ERROR", "message": str(e)}, "data": None}
    except httpx.ConnectError:
        return {"error": {"code": "API_UNAVAILABLE", "message": "REST API is not reachable"}, "data": None}
