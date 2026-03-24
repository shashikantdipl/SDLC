"""SessionService — Business logic for session tracking and context management.

Manages agent session lifecycle and context propagation.
Called by: MCP agents-server tools, REST /api/v1/sessions/* routes.
Never import from mcp_servers/ or api/.
"""
