"""Dashboard configuration — API connection and display settings.

All data fetched via REST API. NEVER import services directly.
"""
import os

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8080/api/v1")
API_KEY = os.environ.get("API_KEY", "dev-api-key")

# Polling intervals (seconds)
FLEET_HEALTH_POLL = 30
PIPELINE_STATUS_POLL = 10
MCP_CALLS_POLL = 5
COST_MONITOR_POLL = 60
APPROVAL_QUEUE_POLL = 15

# Display
PAGE_SIZE = 50
COST_CHART_DAYS = 30
SEVERITY_COLORS = {
    "info": "#3B82F6",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "critical": "#991B1B",
}
STATUS_COLORS = {
    "active": "#22C55E",
    "degraded": "#F59E0B",
    "offline": "#EF4444",
    "canary": "#8B5CF6",
    "pending": "#6B7280",
    "running": "#3B82F6",
    "paused": "#F59E0B",
    "completed": "#22C55E",
    "failed": "#EF4444",
    "cancelled": "#6B7280",
}
