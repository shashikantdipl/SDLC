"""HealthService — Business logic for fleet health and MCP server monitoring.

Implements interactions: I-080, I-081, I-082 from INTERACTION-MAP.
Called by: MCP agents-server tools, REST /api/v1/health/* routes.
Never import from mcp_servers/ or api/.
"""
