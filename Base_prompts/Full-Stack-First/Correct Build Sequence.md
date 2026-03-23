### Full-Stack-First Build Order

**Best for:** Products that serve BOTH AI clients (via MCP) AND human operators (via dashboard) equally. Examples: AI agent platforms, developer tools with monitoring dashboards, LLM-powered products with admin panels.

**Philosophy:** Design MCP tools and dashboard screens IN PARALLEL from a shared interaction map, then build a unified backend that serves both equally.

**Key innovation:** Document #6 (INTERACTION-MAP) coordinates the parallel design of MCP and screens, preventing divergence.

| Step | Doc #  | Document           | Inputs (Generated Docs Only)                                                | What It Produces That Others Need                                       | Parallel? |
| ---- | ------ | ------------------ | --------------------------------------------------------------------------- | ----------------------------------------------------------------------- | --------- |
| 1    | **0**  | ROADMAP.md         | *Raw spec*                                                                  | Project context → consumed by Doc 3                                     | —         |
| 2    | **1**  | PRD.md             | *Raw spec*                                                                  | Personas, journeys (MCP + Dashboard), capabilities → consumed by Docs 2, 4, 5, 6, 8, 10 | with Step 1 |
| 3    | **2**  | ARCH.md            | ← **PRD**                                                                   | Shared service layer, MCP servers, dashboard arch → consumed by Docs 3, 4, 5, 6, 7, 8, 9, 10, 12, 13 | — |
| 4    | **3**  | CLAUDE.md          | ← **ROADMAP** + **ARCH**                                                    | Rules, patterns (shared service, MCP, dashboard) → consumed by Docs 12, 13 | —  |
| 5    | **4**  | QUALITY.md         | ← **PRD** + **ARCH**                                                        | Q-NNN NFRs (MCP + dashboard + parity) → consumed by Docs 6, 7, 8, 9, 11, 13 | with Step 4 |
| 6    | **5**  | FEATURE-CATALOG    | ← **PRD** + **ARCH**                                                        | F-NNN features with interfaces[] → consumed by Docs 6, 7, 9, 11        | with Step 4, 5 |
| 7    | **6**  | INTERACTION-MAP    | ← **PRD** + **ARCH** + **FEATURES** + **QUALITY**                           | Shared data shapes, interaction IDs, cross-interface journeys → consumed by Docs 7, 8, 9, 10, 11, 13 | — |
| 8    | **7**  | MCP-TOOL-SPEC      | ← **INTERACTION-MAP** + **ARCH** + **FEATURES** + **QUALITY**                | MCP tools referencing interaction IDs → consumed by Docs 9, 10, 11, 13  | **with Step 9** |
| 9    | **8**  | DESIGN-SPEC        | ← **INTERACTION-MAP** + **PRD** + **QUALITY** + **FEATURES**                 | Screens referencing interaction IDs → consumed by Docs 9, 10, 11        | **with Step 8** |
| 10   | **9**  | DATA-MODEL.md      | ← **ARCH** + **FEATURES** + **QUALITY** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** + **INTERACTION-MAP** | Schemas + indexes for both MCP and dashboard queries → consumed by Docs 10, 13 | — |
| 11   | **10** | API-CONTRACTS.md   | ← **ARCH** + **DATA-MODEL** + **PRD** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** + **INTERACTION-MAP** | REST endpoints (wraps MCP + feeds dashboard) → consumed by nobody (terminal) | — |
| 12   | **11** | BACKLOG            | ← **FEATURES** + **PRD** + **ARCH** + **QUALITY** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** + **INTERACTION-MAP** | S-NNN stories with interaction_ids → consumed by nobody (terminal) | — |
| 13   | **12** | CLAUDE-ENFORCEMENT | ← **CLAUDE** + **ARCH**                                                     | .claude/ rules + /new-interaction skill → consumed by nobody (terminal) | with Step 12 |
| 14   | **13** | TESTING.md         | ← **ARCH** + **QUALITY** + **DATA-MODEL** + **CLAUDE** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** + **INTERACTION-MAP** | Test strategy with cross-interface tests → consumed by nobody (terminal) | with Step 12 |

### The Parallel Sprint (Steps 8-9)

The defining characteristic of Full-Stack-First is that **MCP-TOOL-SPEC and DESIGN-SPEC are written in parallel**. This is safe because:
- Both read from INTERACTION-MAP (shared data shapes, interaction IDs)
- Neither depends on the other
- Both feed into DATA-MODEL and API-CONTRACTS (which come after)
- INTERACTION-MAP prevents them from diverging
