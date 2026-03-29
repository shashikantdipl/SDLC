### Full-Stack-First Build Order (v2 — 24-Document Stack)

**Best for:** Products that serve BOTH AI clients (via MCP) AND human operators (via dashboard) equally. Examples: AI agent platforms, developer tools with monitoring dashboards, LLM-powered products with admin panels.

**Philosophy:** Design MCP tools and dashboard screens IN PARALLEL from a shared interaction map, then build a unified backend that serves both equally.

**Key innovations:**
- Document #7 (INTERACTION-MAP) coordinates the parallel design of MCP and screens, preventing divergence
- FEATURE-CATALOG before QUALITY — enables per-module coverage thresholds
- SECURITY-ARCH in Phase B — informs all downstream design decisions
- GUARDRAILS-SPEC and COMPLIANCE-MATRIX — AI-native documents that don't exist in traditional SDLC
- CLAUDE.md delayed to Phase D — written after system design is complete

**Total: 24 documents (16 original + 8 new) across Pre-Phase + Phases A-E**

---

### Pre-Phase — Business Discovery

| Step | Doc #  | Document         | Inputs                           | Produces                                           | Parallel? |
| ---- | ------ | ---------------- | -------------------------------- | -------------------------------------------------- | --------- |
| 0    | **0**  | BRD.md           | *Discovery sessions, client docs* | BR-NNN requirements, stakeholder map, business case, OQ tracker → consumed by Docs 1, 2, 17 | — |

### Phase A — Foundations

| Step | Doc #  | Document         | Inputs                           | Produces                                           | Parallel? |
| ---- | ------ | ---------------- | -------------------------------- | -------------------------------------------------- | --------- |
| 1    | **1**  | ROADMAP.md       | *Raw spec* + **BRD**             | Project context, timeline, risk register → consumed by Doc 14 | — |
| 2    | **2**  | PRD.md           | *Raw spec* + **BRD**             | Personas, journeys (MCP + Dashboard), capabilities → consumed by Docs 3, 4, 5, 6, 7, 9, 11, 12, 13, 17 | with Step 1 |
| 3    | **3**  | ARCH.md ★        | ← **PRD**                        | Shared service layer, MCP servers, dashboard arch, agent memory, LLM routing, RAG → consumed by Docs 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 | — |

### Phase B — Decomposition

| Step | Doc #  | Document         | Inputs                           | Produces                                           | Parallel? |
| ---- | ------ | ---------------- | -------------------------------- | -------------------------------------------------- | --------- |
| 4    | **4**  | FEATURE-CATALOG ★ | ← **PRD** + **ARCH**            | F-NNN features (18-field JSON) with interfaces[], ai_required → consumed by Docs 5, 6, 7, 8, 9, 10, 12, 13, 16 | — |
| 5    | **5**  | QUALITY.md ★     | ← **PRD** + **ARCH** + **FEATURES** | Q-NNN NFRs, per-module thresholds, SLI/SLO → consumed by Docs 6, 7, 8, 9, 10, 13, 15, 16, 18, 19, 20, 21 | — |
| 6    | **6**  | SECURITY-ARCH    | ← **PRD** + **ARCH** + **QUALITY** + **FEATURES** | Auth, RBAC, threat model, data classification, agent perms, data governance, SBOM → consumed by Docs 15, 16, 17, 18, 19, 20, 21 | — |

### Phase C — Interface Design

| Step | Doc #  | Document         | Inputs                           | Produces                                           | Parallel? |
| ---- | ------ | ---------------- | -------------------------------- | -------------------------------------------------- | --------- |
| 7    | **7**  | INTERACTION-MAP  | ← **PRD** + **ARCH** + **FEATURES** + **QUALITY** | Shared data shapes, interaction IDs, cross-interface journeys → consumed by Docs 8, 9, 10, 11, 13, 18 | — |
| 8    | **8**  | MCP-TOOL-SPEC    | ← **INTERACTION-MAP** + **ARCH** + **FEATURES** + **QUALITY** | MCP tools referencing interaction IDs → consumed by Docs 10, 11, 12, 13, 18 | **with Step 9** |
| 9    | **9**  | DESIGN-SPEC      | ← **INTERACTION-MAP** + **PRD** + **QUALITY** + **FEATURES** | Screens referencing interaction IDs → consumed by Docs 10, 11, 12, 13, 18 | **with Step 8** |

### Phase D — Data & Build-Facing

| Step | Doc #  | Document         | Inputs                           | Produces                                           | Parallel? |
| ---- | ------ | ---------------- | -------------------------------- | -------------------------------------------------- | --------- |
| 10   | **10** | DATA-MODEL.md    | ← **ARCH** + **FEATURES** + **QUALITY** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** + **INTERACTION-MAP** | Schemas + indexes for both MCP and dashboard → consumed by Docs 11, 12, 14, 17, 18, 19, 21 | — |
| 11   | **11** | API-CONTRACTS.md | ← **ARCH** + **DATA-MODEL** + **PRD** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** + **INTERACTION-MAP** | REST endpoints (wraps MCP + feeds dashboard) → consumed by Docs 12, 14, 19 | — |
| 12   | **12** | USER-STORIES     | ← **PRD** + **FEATURES** + **QUALITY** + **ARCH** + **DATA-MODEL** + **API-CONTRACTS** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** | US-DOMAIN-NNN stories with SACs → consumed by Doc 13 | — |
| 13   | **13** | BACKLOG          | ← **FEATURES** + **PRD** + **ARCH** + **QUALITY** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** + **INTERACTION-MAP** + **USER-STORIES** | S-NNN sprint stories → terminal | — |
| 14   | **14** | CLAUDE.md        | ← **ROADMAP** + **ARCH** + **DATA-MODEL** + **API-CONTRACTS** | Rules, patterns (shared service, MCP, dashboard) → consumed by Docs 15, 18 | with Step 13 |
| 15   | **15** | ENFORCEMENT ★    | ← **CLAUDE** + **ARCH** + **QUALITY** + **SECURITY-ARCH** | .claude/ rules + prompt versioning + API governance → consumed by Doc 20 | — |

### Phase E — Operations, Safety & Compliance

| Step | Doc #  | Document         | Inputs                           | Produces                                           | Parallel? |
| ---- | ------ | ---------------- | -------------------------------- | -------------------------------------------------- | --------- |
| 16   | **16** | INFRA-DESIGN     | ← **ARCH** + **SECURITY-ARCH** + **QUALITY** + **FEATURES** | Environments, CI/CD, observability, DR, capacity → consumed by Doc 19 | — |
| 17   | **17** | MIGRATION-PLAN   | ← **DATA-MODEL** + **ARCH** + **PRD** + **SECURITY-ARCH** + **BRD** | Cutover runbook, source-to-target mapping → terminal | with Step 18 |
| 18   | **18** | TESTING.md ★     | ← **ARCH** + **QUALITY** + **DATA-MODEL** + **CLAUDE** + **MCP-TOOL-SPEC** + **DESIGN-SPEC** + **INTERACTION-MAP** + **SECURITY-ARCH** | Test strategy + LLM eval + go-live checklist → terminal | with Step 17 |
| 19   | **19** | FAULT-TOLERANCE  | ← **ARCH** + **DATA-MODEL** + **API-CONTRACTS** + **SECURITY-ARCH** + **INFRA-DESIGN** + **QUALITY** | 5-layer failure scenarios + on-call procedures → consumed by Doc 21 | — |
| 20   | **20** | GUARDRAILS-SPEC  | ← **ARCH** + **SECURITY-ARCH** + **ENFORCEMENT** + **QUALITY** + **AGENT-HANDOFF** | 4-layer AI safety guardrails → consumed by Doc 21 | — |
| 21   | **21** | COMPLIANCE-MATRIX | ← **SECURITY-ARCH** + **QUALITY** + **DATA-MODEL** + **ARCH** + **GUARDRAILS-SPEC** + **FAULT-TOLERANCE** | SOC2/GDPR/EU AI Act/NIST mapping → terminal | — |

### Protocol Documents

| Doc #  | Document                     | Inputs                           | Parallel? |
| ------ | ---------------------------- | -------------------------------- | --------- |
| **22** | AGENT-HANDOFF-PROTOCOL.md    | ← **ARCH** + **MCP-TOOL-SPEC** + **DATA-MODEL** + **API-CONTRACTS** | after Step 11 |
| **23** | AGENT-INTERACTION-DIAGRAM.md | ← **AGENT-HANDOFF-PROTOCOL**    | after Doc 22 |

---

### The Parallel Sprints

**Steps 8-9 (MCP + DESIGN parallel):** Both read from INTERACTION-MAP, neither depends on the other.

**Steps 17-18 (MIGRATION + TESTING parallel):** MIGRATION reads DATA-MODEL; TESTING reads ARCH+QUALITY. Independent inputs.

**Steps 1-2 (ROADMAP + PRD parallel):** Both read from raw spec + BRD. Independent outputs.

---

### Key Changes from v1 (14-doc) to v2 (24-doc)

| Change | Why |
|--------|-----|
| BRD added as Pre-Phase (Step 0) | Foundation before any design — seniors' requirement |
| FEATURE-CATALOG moved before QUALITY (Step 4→5) | Enables per-module coverage thresholds |
| SECURITY-ARCH added to Phase B (Step 6) | Informs all downstream: INFRA, MIGRATION, TESTING, FAULT-TOLERANCE |
| CLAUDE.md delayed to Phase D (Step 14) | Written after DATA-MODEL + API-CONTRACTS exist — more useful rules |
| USER-STORIES added to Phase D (Step 12) | Client-facing stories ≠ developer BACKLOG |
| INFRA-DESIGN added to Phase E (Step 16) | Includes observability, DR, capacity — all in one doc |
| MIGRATION-PLAN added to Phase E (Step 17) | Cutover runbook for enterprise clients |
| FAULT-TOLERANCE added to Phase E (Step 19) | 5-layer failure scenarios with on-call procedures |
| GUARDRAILS-SPEC added to Phase E (Step 20) | AI safety — unique to AI-native platforms |
| COMPLIANCE-MATRIX added as final doc (Step 21) | Reads everything, produces audit-ready cross-reference |

### ★ Upgraded Documents

| Doc | What's New |
|-----|-----------|
| 03-ARCH ★ | Agent memory architecture, LLM routing layer, RAG architecture |
| 05-QUALITY ★ | Per-module coverage thresholds, SLI/SLO summary table |
| 04-FEATURE-CATALOG ★ | 18-field JSON schema, ai_required, friction, incentive_type, META.json |
| 15-ENFORCEMENT ★ | Prompt versioning rules, API governance rules |
| 18-TESTING ★ | LLM evaluation framework, prompt regression tests, go-live checklist |

---

### Dependency Verification: Zero Circular References

Every document's inputs are available at its step number:

```
Step 0  BRD           ← discovery sessions (external)           ✓
Step 1  ROADMAP       ← raw_spec + BRD (step 0)                ✓
Step 2  PRD           ← raw_spec + BRD (step 0)                ✓
Step 3  ARCH          ← PRD (step 2)                           ✓
Step 4  FEATURES      ← PRD (2) + ARCH (3)                     ✓
Step 5  QUALITY       ← PRD (2) + ARCH (3) + FEATURES (4)      ✓
Step 6  SECURITY      ← PRD (2) + ARCH (3) + QUALITY (5) + FEATURES (4)  ✓
Step 7  INTERACTION   ← PRD (2) + ARCH (3) + FEATURES (4) + QUALITY (5)  ✓
Step 8  MCP-TOOL      ← INTERACTION (7) + ARCH (3) + FEATURES (4) + QUALITY (5)  ✓
Step 9  DESIGN-SPEC   ← INTERACTION (7) + PRD (2) + QUALITY (5) + FEATURES (4)   ✓
Step 10 DATA-MODEL    ← ARCH (3) + FEATURES (4) + QUALITY (5) + MCP (8) + DESIGN (9) + INTERACTION (7)  ✓
Step 11 API-CONTRACTS ← ARCH (3) + DATA (10) + PRD (2) + MCP (8) + DESIGN (9) + INTERACTION (7)  ✓
Step 12 USER-STORIES  ← PRD (2) + FEATURES (4) + QUALITY (5) + ARCH (3) + DATA (10) + API (11) + MCP (8) + DESIGN (9)  ✓
Step 13 BACKLOG       ← FEATURES (4) + PRD (2) + ARCH (3) + QUALITY (5) + MCP (8) + DESIGN (9) + INTERACTION (7) + USER-STORIES (12)  ✓
Step 14 CLAUDE.md     ← ROADMAP (1) + ARCH (3) + DATA (10) + API (11)  ✓
Step 15 ENFORCEMENT   ← CLAUDE (14) + ARCH (3) + QUALITY (5) + SECURITY (6)  ✓
Step 16 INFRA         ← ARCH (3) + SECURITY (6) + QUALITY (5) + FEATURES (4)  ✓
Step 17 MIGRATION     ← DATA (10) + ARCH (3) + PRD (2) + SECURITY (6) + BRD (0)  ✓
Step 18 TESTING       ← ARCH (3) + QUALITY (5) + DATA (10) + CLAUDE (14) + MCP (8) + DESIGN (9) + INTERACTION (7) + SECURITY (6)  ✓
Step 19 FAULT-TOL     ← ARCH (3) + DATA (10) + API (11) + SECURITY (6) + INFRA (16) + QUALITY (5)  ✓
Step 20 GUARDRAILS    ← ARCH (3) + SECURITY (6) + ENFORCEMENT (15) + QUALITY (5) + HANDOFF (22)  ✓
Step 21 COMPLIANCE    ← SECURITY (6) + QUALITY (5) + DATA (10) + ARCH (3) + GUARDRAILS (20) + FAULT-TOL (19)  ✓
```

**Result: 0 circular dependencies. Every input is available before it's needed.**
