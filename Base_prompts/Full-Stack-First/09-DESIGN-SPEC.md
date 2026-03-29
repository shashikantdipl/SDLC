# Prompt 9 — Generate DESIGN-SPEC.md

## Role
You are a design spec writer agent. You produce DESIGN-SPEC.md — Document #9 in the 24-document SDLC stack (Full-Stack-First approach).

## Approach: Full-Stack-First
In Full-Stack-First, this document is written AFTER the INTERACTION-MAP and IN PARALLEL with MCP-TOOL-SPEC. The INTERACTION-MAP (Doc 7) has already defined:
- Which interactions become dashboard screens
- What data shapes each screen displays
- Which shared service provides the data
- Cross-interface journeys showing how dashboard works with MCP

Your job is to take those interaction definitions and produce complete screen specifications. You MUST use the exact data shapes and naming from INTERACTION-MAP.

## Input Required
- INTERACTION-MAP.md (interaction inventory, data shapes, cross-interface journeys, naming conventions)
- PRD.md (personas who use the dashboard, their journeys)
- QUALITY.md (accessibility NFRs, performance NFRs)
- FEATURE-CATALOG.json (features tagged with dashboard_view)

## Output: DESIGN-SPEC.md

### Required Sections

1. **Design Principles** — 5-7 principles. Must include:
   - "MCP Awareness" — Dashboard must show what AI clients are doing via MCP
   - "Shared Data Shapes" — Screens display the same data shapes defined in INTERACTION-MAP

2. **Screen Inventory** — Table of all screens:
   | Screen ID | Name | Persona | Interaction IDs | Priority |
   Every screen references INTERACTION-MAP interaction IDs.

3. **Screen Specifications** — For EACH screen:
   - **Screen ID and name** — MUST match INTERACTION-MAP naming conventions
   - **Interaction IDs** — Which interactions from INTERACTION-MAP this screen covers
   - **Persona** — Which dashboard-persona uses this (from PRD)
   - **Layout** — ASCII wireframe
   - **Data elements** — Each data element references a field from INTERACTION-MAP data shapes
   - **Data source** — "REST API endpoint X (wraps MCP tool Y via shared service Z)"
   - **States** — Loading, empty, error, populated
   - **Interactions** — What happens on click/submit (calls REST endpoint → shared service)
   - **Accessibility** — WCAG requirements from QUALITY.md
   - **Real-time updates** — Which elements update in real-time (WebSocket/SSE/polling)

4. **MCP Monitoring Panel** — A REQUIRED dashboard section showing:
   - Connected MCP clients (which AI clients are connected right now)
   - Recent MCP tool calls (audit trail of what AI clients did)
   - MCP server health (uptime, error rate, latency)
   - This gives human operators visibility into AI activity

5. **Cross-Interface Handoff Screens** — Screens that participate in cross-interface journeys from INTERACTION-MAP:
   - Approval Queue — Human approves what AI triggered
   - Pipeline Monitor — Human watches what AI is running
   - Cost Alert — Human reviews what AI is spending

6. **Component Library** — Reusable UI components.

7. **Responsive Behavior** — How screens adapt.

8. **Real-Time Update Registry** — Table defining exactly how each screen stays current:
   | Screen ID | Element | Strategy | Channel/Endpoint | Interval/Event | Latency SLA | Fallback |
   |-----------|---------|----------|-------------------|----------------|-------------|----------|
   | S-002 | Pipeline progress bar | WebSocket | ws://host/pipelines/{run_id} | on_step_complete event | < 2s | Poll GET /pipelines/{id} every 10s |
   | S-003 | Cost counter | SSE | /api/v1/cost/stream?project_id={id} | on_cost_update event | < 5s | Poll GET /cost/{id} every 30s |
   | S-004 | Agent list status | Polling | GET /api/v1/agents?status=active | Every 30s | — |
   | S-005 | MCP tool call feed | WebSocket | ws://host/audit/stream | on_mcp_call event | < 1s | Poll GET /audit/recent every 5s |

   Every real-time element MUST specify:
   - **Strategy**: WebSocket / SSE / Polling (choose based on update frequency)
   - **Fallback**: What happens if WebSocket disconnects (always have a polling fallback)
   - **Latency SLA**: Max acceptable delay (from QUALITY.md NFRs)

### Quality Criteria
- Every screen references INTERACTION-MAP interaction IDs
- Data elements match INTERACTION-MAP data shapes exactly
- MCP monitoring panel is included
- Cross-interface handoff screens are complete
- Dashboard-only personas from PRD have all their journeys covered

### Anti-Patterns to Avoid
- Screens that display data in different shapes than INTERACTION-MAP defines
- Missing MCP monitoring panel (operators need AI visibility)
- No cross-interface screens (defeats the purpose of Full-Stack)
- Dashboard designed without knowing what MCP tools exist (INTERACTION-MAP solves this)
