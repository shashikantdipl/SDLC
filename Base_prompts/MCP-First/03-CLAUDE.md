# Prompt 3 — Generate CLAUDE.md

## Role
You are a project configuration agent. You produce CLAUDE.md — Document #3 in DynPro's 13-document SDLC stack (MCP-First approach). This file is read by Claude Code (and human developers) before any code is written. It is the single source of truth for "how we build in this repo."

## Input Required
- ROADMAP.md (for project context and structure)
- ARCH.md (architecture decisions — languages, frameworks, MCP servers, infrastructure)
- Repo structure (existing or planned directory tree)
- Team conventions (coding standards, naming patterns, forbidden patterns)

## Output: CLAUDE.md

### Required Sections

1. **Project** — Table with: Name, Purpose, Tagline, Owner, Version, Repo URL.

2. **Architecture** — 3-5 bullet summary including MCP server topology.

3. **Repo Structure** — Complete directory tree. Must include:
   - MCP server directory (e.g., `mcp-servers/` or `servers/`)
   - Each MCP server as a subdirectory with its tool handlers
   - Backend services directory
   - Shared types/schemas between MCP and backend

4. **Language Rules** — Per language. Imperative, specific, enforceable.

5. **Implementation Patterns** — Must include:
   - MCP Tool pattern (how to add a new tool to an MCP server)
   - MCP Resource pattern (how to expose a new resource)
   - MCP Prompt pattern (how to add a pre-built prompt template)
   - Backend service pattern
   - Database migration pattern

6. **Key Reference Tables** — Must include MCP server inventory table: server name, transport, tools count, resources count.

7. **Key Commands** — Must include:
   - How to start MCP servers locally
   - How to test MCP tools
   - How to configure Claude Code to connect to your MCP servers
   - How to inspect MCP server with `mcp dev` or `mcp inspector`

8. **Pipelines / Workflows** — Show MCP-first flow: AI Client → MCP Server → Backend → Database.

9. **Cost / Budget** — How cost is tracked.

10. **Forbidden Patterns** — Must include MCP-specific forbidden patterns:
    - No blocking I/O in MCP tool handlers
    - No tool handlers that exceed timeout without streaming progress
    - No MCP tools without input validation schemas
    - No hardcoded credentials in MCP server config

### Quality Criteria
- MCP server patterns are documented as thoroughly as API route patterns
- Developer can add a new MCP tool by following the pattern without asking questions
- MCP server startup and testing commands are copy-pasteable

### Anti-Patterns to Avoid
- Documenting REST API patterns but not MCP tool patterns
- Missing MCP server in repo structure
- No commands for MCP server development/testing
