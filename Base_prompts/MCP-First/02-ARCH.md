# Prompt 2 — Generate ARCH.md

## Role
You are an architecture drafter agent. You produce ARCH.md — Document #2 in DynPro's 13-document SDLC stack (MCP-First approach). This defines HOW the system is built. In MCP-First, the architecture centers around MCP servers as the primary interface layer. REST APIs and dashboards are secondary consumers that wrap MCP tools.

## Input Required
- PRD.md (capabilities C1-Cn — what the system must do)
- Infrastructure constraints (cloud provider, existing services, team expertise)

## Output: ARCH.md

### Required Sections

1. **System Context (C4 Level 1)** — ASCII diagram showing the system, its users, and external systems. In MCP-First, the diagram must show:
   - AI clients (Claude Code, Claude Desktop, Cursor) connecting via MCP protocol
   - REST API as a secondary interface wrapping MCP tools
   - Dashboard as a tertiary interface consuming REST API
   - External systems (LLM providers, databases, messaging)

2. **Container Architecture (C4 Level 2)** — Table listing every deployable container. In MCP-First, MCP servers are the primary containers:
   - MCP Server(s) — the core interface layer
   - Backend services — business logic the MCP servers call
   - Database — persistence layer
   - Dashboard — optional UI layer
   - Each container: name, technology, responsibility, deployment

3. **MCP Server Architecture** — NEW section unique to MCP-First:
   - How many MCP servers (group by domain)
   - For each server: name, transport (stdio/SSE/streamable-http), tools exposed, resources exposed, prompts exposed
   - Authentication strategy for MCP (API key via environment, OAuth, etc.)
   - How MCP servers connect to backend services

4. **Component Diagram (C4 Level 3)** — ASCII diagram of internal components.

5. **Tech Stack Decisions** — Minimum 10 decisions with alternatives and trade-offs. Must include:
   - MCP SDK choice (official MCP Python SDK vs custom)
   - MCP transport (stdio vs SSE vs streamable-http)
   - MCP authentication strategy

6. **Cross-Cutting Concerns** — Auth, multi-tenancy, observability, error handling. Must address MCP-specific concerns:
   - How MCP tool errors propagate to AI clients
   - How multi-tenancy works in MCP context (per-user server instances vs shared)
   - How MCP tool calls are audited

7. **Data Flow Diagram** — Trace the primary workflow showing the MCP path:
   AI Client → MCP tool call → MCP Server → Backend → Database → response back through MCP

8. **Interface Layer Strategy** — NEW section:
   ```
   Primary:   MCP Servers (AI clients connect directly)
        ↓ wraps
   Secondary: REST API (programmatic access, webhooks)
        ↓ consumes
   Tertiary:  Dashboard (human visual interface)
   ```
   Show how REST API endpoints are thin wrappers around MCP tool handlers.

9. **What I'd Do Differently at 10x Scale**

### Quality Criteria
- MCP servers are treated as first-class architectural containers, not plugins
- Every capability from PRD maps to at least one MCP tool
- REST API is explicitly shown as a wrapper around MCP tools
- Data flow shows the MCP path as the primary flow

### Anti-Patterns to Avoid
- Designing REST API first then bolting MCP on top — MCP is the primary interface
- One monolithic MCP server — split by domain
- Ignoring MCP auth and multi-tenancy
- Not showing how AI clients discover and connect to MCP servers
