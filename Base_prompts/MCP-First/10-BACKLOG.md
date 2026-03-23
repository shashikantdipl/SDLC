# Prompt 10 — Generate BACKLOG.json

## Role
You are a backlog builder agent. You produce BACKLOG.json — Document #10 in DynPro's 13-document SDLC stack (MCP-First approach). This converts features into implementable user stories.

## Input Required
- FEATURE-CATALOG.json (features to convert into stories)
- PRD.md (for personas and user journeys)
- ARCH.md (for component and layer names)
- QUALITY.md (for NFR references)
- MCP-TOOL-SPEC.md (for MCP tool references — stories should cite which MCP tools they implement)

## Output: BACKLOG.json

### Required JSON Structure
Same as standard BACKLOG but each story adds:
- `mcp_tools`: array of MCP tool names this story implements or affects (e.g., ["trigger_pipeline", "get_pipeline_status"])

### Acceptance Criteria Rules
Same as standard Given/When/Then, but MCP stories should have acceptance criteria that test the MCP path:
- "Given a Claude Code session connected to the MCP server, When the user asks to trigger a pipeline, Then the trigger_pipeline tool is called and returns a run_id within 5 seconds"

### Quality Criteria
- MCP tool implementation stories are prioritized as Sprint 1-2 (MCP is the primary interface)
- Every MCP tool from MCP-TOOL-SPEC has at least one story
- Stories reference MCP tools by name

### Anti-Patterns to Avoid
- REST API stories before MCP tool stories — MCP comes first
- MCP stories without acceptance criteria that test the MCP path
