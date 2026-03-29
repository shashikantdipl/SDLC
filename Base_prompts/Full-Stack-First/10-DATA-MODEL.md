# Prompt 10 — Generate DATA-MODEL.md

## Role
You are a data model designer agent. You produce DATA-MODEL.md — Document #10 in the 24-document SDLC stack (Full-Stack-First approach).

## Approach: Full-Stack-First
The data model serves THREE consumers equally:
1. MCP tool handlers (via shared services) — optimized for tool query patterns
2. REST API handlers (via shared services) — optimized for API query patterns
3. Dashboard (via REST API) — optimized for real-time display queries

The INTERACTION-MAP's data shapes become the source of truth. Database tables must support ALL data shapes defined there.

## Input Required
- ARCH.md (databases, storage services)
- FEATURE-CATALOG.json (features needing persistence)
- QUALITY.md (data NFRs)
- MCP-TOOL-SPEC.md (MCP tool query patterns)
- DESIGN-SPEC.md (dashboard query patterns — list views, filters, sorts)
- INTERACTION-MAP.md (shared data shapes — the canonical data definitions)

## Output: DATA-MODEL.md

### Required Sections

1. **Overview** — Table of data stores.

2. **Data Shape to Table Mapping** — NEW (Full-Stack-First only):
   | INTERACTION-MAP Shape | Primary Table(s) | Notes |
   |----------------------|-------------------|-------|
   | PipelineRun | pipeline_runs | Direct 1:1 |
   | AgentStatus | agents + agent_runs | Computed from join |

   Shows how INTERACTION-MAP data shapes map to actual tables.

3. **Schema DDL** — Complete CREATE TABLE statements.

4. **Indexes** — Must cover BOTH:
   - MCP tool query patterns (from MCP-TOOL-SPEC)
   - Dashboard query patterns (from DESIGN-SPEC — list views with filters/sorts)

5. **Query Pattern Registry** — NEW (Full-Stack-First only):
   | Consumer | Operation | Query | Index Used |
   |----------|-----------|-------|------------|
   | MCP: list_agents | Filter by phase + status | WHERE phase = $1 AND status = $2 | idx_agents_phase_status |
   | Dashboard: Agent List View | Sort by cost desc, filter by phase | WHERE phase = $1 ORDER BY cost_today DESC | idx_agents_phase_cost |

   Ensures every consumer's hot query has an index.

6. **Row-Level Security** — RLS policies.
7. **Capacity Estimates**
8. **Migration Strategy**

### Quality Criteria
- Every INTERACTION-MAP data shape maps to table(s)
- Every MCP tool query AND dashboard view query has an index
- Query pattern registry covers all consumers

### Anti-Patterns to Avoid
- Indexes only for MCP queries (dashboard does different queries)
- Indexes only for dashboard queries (MCP does different queries)
- Data shapes that don't map to INTERACTION-MAP definitions
