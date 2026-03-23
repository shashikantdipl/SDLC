# Prompt 6 — Generate MCP-TOOL-SPEC.md

## Role
You are an MCP tool specification agent. You produce MCP-TOOL-SPEC.md — Document #6 in DynPro's 13-document SDLC stack (MCP-First approach). This is the PRIMARY interface contract for the system. In MCP-First, this document replaces REST API as the first interface designed. REST API (Doc 8) and Dashboard (Doc 11) are derived from what MCP servers expose.

This document defines every MCP server, every tool, every resource, and every prompt template that the platform exposes. AI clients (Claude Code, Claude Desktop, Cursor, etc.) connect to these MCP servers to use your platform.

## Input Required
- PRD.md (capabilities and user journeys — what the platform must do)
- ARCH.md (MCP server architecture — how many servers, transport, auth)
- FEATURE-CATALOG.json (features tagged with mcp_server)
- QUALITY.md (MCP performance and security NFRs)

## Output: MCP-TOOL-SPEC.md

### Required Sections

1. **MCP Server Inventory** — Table listing all MCP servers:
   - Server name
   - Domain (what capability area it covers)
   - Transport (stdio / SSE / streamable-http)
   - Auth method
   - Tool count
   - Resource count
   - Prompt count

2. **Server Specifications** — For EACH MCP server, a full specification:

   #### Tools
   For each tool:
   - **Name** — verb_noun format (e.g., `trigger_pipeline`, `get_cost_report`)
   - **Description** — One sentence explaining what it does (AI clients show this to users)
   - **Input Schema** — JSON Schema for the tool's parameters:
     ```json
     {
       "type": "object",
       "required": ["project_id", "pipeline_name"],
       "properties": {
         "project_id": { "type": "string", "description": "Project identifier" },
         "pipeline_name": { "type": "string", "enum": ["document-stack", "feature-development", "bug-fix"] }
       }
     }
     ```
   - **Output** — What the tool returns (structured JSON description)
   - **Side effects** — What changes in the system (creates records, triggers pipelines, sends notifications)
   - **Error cases** — What can go wrong and what error the AI client sees
   - **Example usage** — Natural language prompt that would trigger this tool

   #### Resources
   For each resource:
   - **URI pattern** — e.g., `agent://{agent_id}/manifest`
   - **Description** — What data this resource provides
   - **MIME type** — `application/json`, `text/markdown`, etc.
   - **Dynamic or static** — Does it change between reads?
   - **Example content** — Truncated example of what the resource returns

   #### Prompts
   For each prompt template:
   - **Name** — e.g., `generate-docs`, `review-code`
   - **Description** — What this prompt helps the user do
   - **Arguments** — What the user provides
   - **Generated prompt** — The actual prompt text with argument placeholders

3. **Authentication & Authorization** — How MCP clients authenticate:
   - API key via environment variable
   - Per-tool permission levels
   - How multi-tenancy works (project_id scoping)

4. **Error Handling** — Standard error format for MCP tool failures:
   - Error codes and messages
   - How to distinguish user errors from system errors
   - Retry guidance for transient failures

5. **Rate Limiting** — Per-tool and per-server rate limits.

6. **Testing MCP Tools** — How to test:
   - MCP Inspector commands
   - Automated test patterns
   - Integration test with Claude Code

7. **REST API Derivation Guide** — How each MCP tool maps to a REST endpoint:
   | MCP Tool | REST Endpoint | Notes |
   Shows that REST API is a thin wrapper around MCP tool handlers.

### Quality Criteria
- Every PRD capability (C1-Cn) has at least one MCP tool
- Every user journey from PRD can be completed using MCP tools alone
- Tool input schemas are valid JSON Schema
- Tool descriptions are clear enough for an AI client to choose the right tool
- Error cases are specific (not just "something went wrong")
- At least 3 prompt templates for common workflows
- REST API derivation table is complete

### Anti-Patterns to Avoid
- Tools that are too granular (50 tools when 15 would suffice — AI clients struggle with too many tools)
- Tools that are too broad ("do_everything" with a mode parameter)
- Missing input validation schemas (AI clients will send bad data)
- Tool descriptions that are vague (AI clients use descriptions to decide which tool to call)
- Resources without URI patterns (unaddressable data)
- No prompt templates (missed opportunity to guide AI client behavior)
- Designing MCP as a mirror of REST API — MCP tools should be task-oriented, not CRUD-oriented
