### MCP-First Build Order

**Best for:** AI-native platforms, developer tools, agent frameworks, LLM-powered products.
**Philosophy:** MCP tool interfaces drive the design. REST API wraps MCP tools. Dashboard visualizes MCP activity.

| Step | Doc #  | Document           | Inputs (Generated Docs Only)                                           | What It Produces That Others Need                                  |
| ---- | ------ | ------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 1    | **0**  | ROADMAP.md         | *Raw spec*                                                             | Project context → consumed by Doc 3                                |
| 2    | **1**  | PRD.md             | *Raw spec*                                                             | Personas, journeys, capabilities → consumed by Docs 2, 4, 5, 6, 8, 10 |
| 3    | **2**  | ARCH.md            | ← **PRD**                                                              | MCP server architecture, tech decisions → consumed by Docs 3, 4, 5, 6, 7, 8, 9, 12 |
| 4    | **3**  | CLAUDE.md          | ← **ROADMAP** + **ARCH**                                               | Language rules, MCP patterns, commands → consumed by Docs 9, 12    |
| 5    | **4**  | QUALITY.md         | ← **PRD** + **ARCH**                                                   | Q-NNN NFRs (incl. MCP NFRs) → consumed by Docs 6, 7, 10, 11, 12  |
| 6    | **5**  | FEATURE-CATALOG    | ← **PRD** + **ARCH**                                                   | F-NNN features tagged with MCP servers → consumed by Docs 6, 7, 10 |
| 7    | **6**  | MCP-TOOL-SPEC      | ← **PRD** + **ARCH** + **FEATURE-CATALOG** + **QUALITY**               | MCP servers, tools, resources, prompts → consumed by Docs 7, 8, 10, 12 |
| 8    | **7**  | DATA-MODEL.md      | ← **ARCH** + **FEATURE-CATALOG** + **QUALITY** + **MCP-TOOL-SPEC**     | Schemas, indexes for MCP queries → consumed by Docs 8, 12         |
| 9    | **8**  | API-CONTRACTS.md   | ← **ARCH** + **DATA-MODEL** + **PRD** + **MCP-TOOL-SPEC**              | REST endpoints wrapping MCP tools → consumed by Doc 11             |
| 10   | **9**  | CLAUDE-ENFORCEMENT | ← **CLAUDE** + **ARCH**                                                | .claude/ rules + MCP skills → consumed by nobody (terminal)        |
| 11   | **10** | BACKLOG            | ← **FEATURE-CATALOG** + **PRD** + **ARCH** + **QUALITY** + **MCP-TOOL-SPEC** | S-NNN stories → consumed by nobody (terminal)                |
| 12   | **11** | DESIGN-SPEC.md     | ← **PRD** + **API-CONTRACTS** + **QUALITY**                            | Screen specs with MCP panel → consumed by nobody (terminal)        |
| 13   | **12** | TESTING.md         | ← **ARCH** + **QUALITY** + **DATA-MODEL** + **CLAUDE** + **MCP-TOOL-SPEC** | Test strategy with MCP tests → consumed by nobody (terminal)  |
