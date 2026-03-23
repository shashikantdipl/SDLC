### Design-First Build Order

**Best for:** Consumer apps, dashboards, UX-driven products, user-facing SaaS.
**Philosophy:** Screens drive the backend. API endpoints and data models are derived from what the UI needs.

| Step | Doc #  | Document           | Inputs (Generated Docs Only)                                    | What It Produces That Others Need                            |
| ---- | ------ | ------------------ | --------------------------------------------------------------- | ------------------------------------------------------------ |
| 1    | **0**  | ROADMAP.md         | *Raw spec*                                                      | Project context → consumed by Doc 3                          |
| 2    | **1**  | PRD.md             | *Raw spec*                                                      | Personas, journeys, capabilities → consumed by Docs 2, 4, 5, 6, 8, 9 |
| 3    | **2**  | ARCH.md            | ← **PRD**                                                       | Tech decisions, components, data flow → consumed by Docs 3, 4, 5, 6, 7, 8, 10, 11 |
| 4    | **3**  | CLAUDE.md          | ← **ROADMAP** + **ARCH**                                        | Language rules, repo structure → consumed by Docs 10, 11     |
| 5    | **4**  | QUALITY.md         | ← **PRD** + **ARCH**                                            | Q-NNN NFRs → consumed by Docs 6, 7, 9, 11                    |
| 6    | **5**  | FEATURE-CATALOG    | ← **PRD** + **ARCH**                                            | F-NNN features, epics → consumed by Docs 6, 7, 9            |
| 7    | **6**  | DESIGN-SPEC.md     | ← **PRD** + **ARCH** + **QUALITY** + **FEATURE-CATALOG**        | Screen specs, data requirements → consumed by Docs 7, 8, 9  |
| 8    | **7**  | DATA-MODEL.md      | ← **ARCH** + **FEATURE-CATALOG** + **QUALITY** + **DESIGN-SPEC** | Schemas, tables → consumed by Docs 8, 11                     |
| 9    | **8**  | API-CONTRACTS.md   | ← **ARCH** + **DATA-MODEL** + **PRD** + **DESIGN-SPEC**         | Endpoints, payloads, errors → consumed by nobody (terminal)  |
| 10   | **9**  | BACKLOG            | ← **FEATURE-CATALOG** + **PRD** + **ARCH** + **QUALITY** + **DESIGN-SPEC** | S-NNN stories → consumed by nobody (terminal) |
| 11   | **10** | CLAUDE-ENFORCEMENT | ← **CLAUDE** + **ARCH**                                         | .claude/ rules and skills → consumed by nobody (terminal)    |
| 12   | **11** | TESTING.md         | ← **ARCH** + **QUALITY** + **DATA-MODEL** + **CLAUDE**          | Test strategy → consumed by nobody (terminal)                |
