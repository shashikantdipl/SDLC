### API-First Build Order

**Best for:** Backend-heavy platforms, API-driven systems, developer tools, microservices.
**Philosophy:** Backend contracts drive the UI. Screens are designed against existing API endpoints.

| Step | Doc #  | Document           | Inputs (Generated Docs Only)                             | What It Produces That Others Need                            |
| ---- | ------ | ------------------ | -------------------------------------------------------- | ------------------------------------------------------------ |
| 1    | **0**  | ROADMAP.md         | *Raw spec*                                               | Project context → consumed by Doc 3                          |
| 2    | **1**  | PRD.md             | *Raw spec*                                               | Personas, journeys, capabilities C1–C7 → consumed by Docs 2, 4, 5, 8, 9, 10 |
| 3    | **2**  | ARCH.md            | ← **PRD**                                                | Tech decisions, containers, components, data flow → consumed by Docs 3, 4, 5, 6, 7, 8, 9, 11 |
| 4    | **3**  | CLAUDE.md          | ← **ROADMAP** + **ARCH**                                 | Language rules, repo structure, commands, forbidden patterns → consumed by Docs 6, 11 |
| 5    | **4**  | QUALITY.md         | ← **PRD** + **ARCH**                                     | Q-NNN NFRs → consumed by Docs 7, 8, 10, 11                   |
| 6    | **5**  | FEATURE-CATALOG    | ← **PRD** + **ARCH**                                     | F-NNN features, epics, dependencies → consumed by Docs 7, 8  |
| 7    | **6**  | CLAUDE-ENFORCEMENT | ← **CLAUDE** + **ARCH**                                  | .claude/ rules and skills → consumed by nobody (terminal)    |
| 8    | **7**  | DATA-MODEL.md      | ← **ARCH** + **FEATURE-CATALOG** + **QUALITY**           | Schemas, mock data structures → consumed by Docs 9, 11       |
| 9    | **8**  | BACKLOG            | ← **FEATURE-CATALOG** + **PRD** + **ARCH** + **QUALITY** | S-NNN stories → consumed by nobody (terminal)                |
| 10   | **9**  | API-CONTRACTS.md   | ← **ARCH** + **DATA-MODEL** + **PRD**                    | Endpoints, payloads, errors → consumed by Doc 10             |
| 11   | **10** | DESIGN-SPEC.md     | ← **PRD** + **API-CONTRACTS** + **QUALITY**              | Screen specs → consumed by nobody (terminal)                 |
| 12   | **11** | TESTING.md         | ← **ARCH** + **QUALITY** + **DATA-MODEL** + **CLAUDE**   | Test strategy → consumed by nobody (terminal)                |
