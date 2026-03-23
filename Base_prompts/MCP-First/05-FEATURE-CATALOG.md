# Prompt 5 — Generate FEATURE-CATALOG.json

## Role
You are a feature extraction agent. You produce FEATURE-CATALOG.json — Document #5 in DynPro's 13-document SDLC stack (MCP-First approach). This is the machine-readable bridge between the PRD and the BACKLOG. The output is JSON — not markdown, not prose.

## Input Required
- PRD.md (especially the Capabilities section C1-Cn)
- ARCH.md (to understand component boundaries, MCP server boundaries — features should align with MCP servers)

## Output: FEATURE-CATALOG.json

### Required JSON Structure

Same as standard Feature Catalog but with additional consideration: features should be organized around MCP server boundaries. Each feature should indicate which MCP server it belongs to (if applicable).

Add a field to each feature:
- `mcp_server`: which MCP server exposes this feature (or "none" for backend-only features)

### Quality Criteria
- Same as standard FEATURE-CATALOG criteria
- Features that map to MCP tools are explicitly tagged
- MCP server features are prioritized as "must" (they're the primary interface)

### Anti-Patterns to Avoid
- Same as standard, plus:
- Features that only think about REST API without considering MCP tool exposure
- MCP features deprioritized as "could" — they should be "must" since MCP is the primary interface
