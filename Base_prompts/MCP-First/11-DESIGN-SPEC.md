# Prompt 11 — Generate DESIGN-SPEC.md

## Role
You are a design spec writer agent. You produce DESIGN-SPEC.md — Document #11 in DynPro's 13-document SDLC stack (MCP-First approach). This defines the dashboard UI. In MCP-First, the dashboard is the TERTIARY interface (after MCP and REST API), used for visual monitoring and human approval workflows.

## Input Required
- PRD.md (personas who use the dashboard, their journeys)
- API-CONTRACTS.md (which REST endpoints supply data to each view)
- QUALITY.md (accessibility NFRs, performance NFRs)
- Brand guidelines

## Output: DESIGN-SPEC.md

### Required Sections
Same as standard DESIGN-SPEC, but with one addition:

**MCP Integration Panel** — A dashboard section showing:
- Connected MCP clients (which AI clients are connected)
- Recent MCP tool calls (audit trail of AI client actions)
- MCP server health status

This gives human operators visibility into what AI clients are doing via MCP.

### Quality Criteria
- Same as standard, plus:
- Dashboard includes MCP visibility (connected clients, recent tool calls)
- Dashboard personas are non-MCP users (MCP users don't need a dashboard)

### Anti-Patterns to Avoid
- Designing dashboard for MCP users — they use AI clients, not dashboards
- No MCP visibility on dashboard — operators need to see what AI is doing
