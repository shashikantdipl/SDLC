# Prompt 14 — Generate CLAUDE.md

## Role
You are a project configuration agent. You produce CLAUDE.md — Document #14 in the 24-document SDLC stack (Full-Stack-First approach). This file is read by Claude Code before any code is written.

## Input Required
- ROADMAP.md (project context)
- ARCH.md (tech stack, MCP servers, dashboard framework, shared services)

## Output: CLAUDE.md

### Required Sections

1. **Project** — Table with: Name, Purpose, Tagline, Owner, Version, Repo URL.

2. **Architecture** — 3-5 bullet summary covering: MCP servers, REST API, dashboard, shared service layer.

3. **Repo Structure** — Complete directory tree. Must include:
   ```
   project/
   ├── mcp-servers/              # MCP server implementations
   │   ├── agents-server/        # Agent execution MCP server
   │   ├── governance-server/    # Cost & compliance MCP server
   │   └── knowledge-server/     # Knowledge management MCP server
   ├── api/                      # REST API (wraps shared services)
   │   ├── routes/
   │   └── middleware/
   ├── dashboard/                # Human visual interface
   │   ├── views/
   │   └── components/
   ├── services/                 # SHARED service layer (MCP + API both use)
   │   ├── pipeline_service.py
   │   ├── agent_service.py
   │   ├── cost_service.py
   │   └── ...
   ├── sdk/                      # Agent SDK
   ├── agents/                   # Agent implementations
   ├── schemas/                  # Shared schemas (MCP + API + DB)
   ├── migrations/               # Database migrations
   └── tests/
       ├── mcp/                  # MCP tool tests
       ├── api/                  # REST API tests
       ├── dashboard/            # Dashboard tests
       ├── services/             # Shared service tests
       └── integration/          # Cross-interface tests
   ```

4. **Language Rules** — Per language. Imperative, specific, enforceable.

5. **Implementation Patterns** — Must include ALL of these:
   - **Shared Service pattern** — How to add a new service function (the core pattern)
   - **MCP Tool pattern** — How to add a tool that calls a shared service
   - **API Route pattern** — How to add a route that calls the same shared service
   - **Dashboard View pattern** — How to add a view that consumes a REST endpoint
   - **Agent pattern** — How to add a new agent
   - **Migration pattern** — How to add a database migration

   The Shared Service pattern is THE key pattern. MCP tools and API routes are thin wrappers.

6. **Key Reference Tables** — MCP server inventory, API route inventory, dashboard view inventory.

7. **Key Commands** — Must include:
   - Start MCP servers locally
   - Start REST API
   - Start dashboard
   - Start everything (all three)
   - Test MCP tools
   - Test API routes
   - Test dashboard
   - Test shared services
   - Configure Claude Code to connect to MCP servers

8. **Pipelines / Workflows** — Show both flows:
   - MCP: AI Client → MCP Server → Service → DB
   - Dashboard: User → Dashboard → REST API → Service → DB

9. **Cost / Budget**

10. **Forbidden Patterns** — Must include:
    - No business logic in MCP tool handlers (must be in shared services)
    - No business logic in API route handlers (must be in shared services)
    - No direct DB access from dashboard (must go through REST API)
    - No MCP tools without corresponding REST endpoints
    - No REST endpoints without corresponding MCP tools (unless dashboard-only)
    - No blocking I/O in MCP handlers
    - No stubs, no TODOs

### Quality Criteria
- Shared service pattern is documented first and most thoroughly
- Developer can add a feature across all 3 interfaces by following the patterns
- Forbidden patterns enforce the shared service layer

### Anti-Patterns to Avoid
- Documenting MCP and REST as separate systems (they share services)
- Missing the shared service pattern (it's the most important one)
- Commands that start only one interface without mentioning the others
