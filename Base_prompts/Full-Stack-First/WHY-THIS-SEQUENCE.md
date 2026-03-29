# Why This Sequence? — Full-Stack-First Approach

## Who Is This For?

You're building a product that serves BOTH AI clients AND human operators. Your developers use Claude Code (MCP), your managers use a dashboard, and your CI/CD uses REST APIs. You need ALL THREE interfaces to work seamlessly together.

This page explains why the 24-document sequence exists and how it prevents the #1 problem with multi-interface products: **divergence**.

---

## The Problem Full-Stack-First Solves

When you build MCP tools and dashboard screens independently, they drift apart:
- MCP returns `agent_status: "active"` but dashboard shows `status: "running"` — different names
- MCP returns 12 fields, dashboard shows 5 — the dashboard silently drops data
- MCP handles errors as `{error: "budget_exceeded"}`, dashboard shows "Something went wrong"
- Developer triggers a pipeline via MCP, but the approval step only works on dashboard — broken handoff

**Full-Stack-First prevents this with one key innovation: the INTERACTION-MAP (Document #7).**

---

## What Makes Full-Stack-First Different?

### Compared to API-First (12 docs)
API-First designs endpoints first, dashboard last. MCP is an afterthought (or absent).
Full-Stack-First designs MCP tools and screens in parallel, unified by shared data shapes.

### Compared to Design-First (12 docs)
Design-First designs screens first, derives API from screen needs. No MCP.
Full-Stack-First includes screens AND MCP tools as equal citizens.

### Compared to MCP-First (13 docs)
MCP-First designs MCP tools first, dashboard last (it's a "monitoring window").
Full-Stack-First treats dashboard as an equal interface, not a monitoring afterthought.

### The Full-Stack-First Innovation
```
API-First:      API → Screens (no MCP)
Design-First:   Screens → API (no MCP)
MCP-First:      MCP → API → Screens
Full-Stack:     INTERACTION-MAP → MCP + Screens (parallel) → API (serves both)
```

---

## The 24 Documents, Explained

### Steps 0-6: Foundation & Decomposition

**[0] BRD** — Captures business requirements before any technical design begins.
**[1] ROADMAP** — Plans for 24 documents, marks the parallel MCP+Design sprint.
**[2] PRD** — Personas declare their primary interface (MCP or Dashboard). Journeys show both paths. At least one cross-interface journey.
**[3] ARCH** — Introduces the Shared Service Layer: MCP handlers and REST handlers call the same service functions. No logic duplication.
**[4] FEATURE-CATALOG** — Each feature tagged with `interfaces: ["mcp", "rest", "dashboard"]` and `shared_service`.
**[5] QUALITY** — NFRs for all 3 interfaces + interface parity requirements.
**[6] SECURITY-ARCH** — Auth, RBAC, threat model, data governance. Informs all downstream design.

### Step 7: INTERACTION-MAP (THE KEY DOCUMENT)

This document doesn't exist in any other approach. It defines:

1. **Interaction Inventory** — Every action the system supports, independent of interface:
   | ID | Interaction | MCP Tool | Dashboard Screen | Shared Service | Data Shape |

2. **Shared Data Shapes** — Canonical data definitions used by BOTH MCP and dashboard:
   ```
   Shape: PipelineRun { run_id, status, steps, cost_usd, ... }
   Used by: MCP trigger_pipeline, Dashboard Pipeline Status View
   ```

3. **Cross-Interface Journeys** — How workflows span MCP and dashboard:
   ```
   Developer (MCP) triggers pipeline → Pipeline hits gate →
   Manager (Dashboard) approves → Pipeline continues →
   Developer (MCP) checks status
   ```

4. **Naming Conventions** — Ensures MCP calls it `trigger_pipeline` and dashboard calls it "Trigger Pipeline" (same noun, different case).

The INTERACTION-MAP is the CONTRACT between the MCP spec and the Design spec. It prevents divergence.

### Steps 8-9: The Parallel Sprint

**[8] MCP-TOOL-SPEC** and **[9] DESIGN-SPEC** are written in parallel:
- Both read from INTERACTION-MAP (shared data shapes, interaction IDs)
- MCP-TOOL-SPEC produces tool schemas referencing interaction IDs
- DESIGN-SPEC produces screen layouts referencing the same interaction IDs
- Neither depends on the other — they depend on INTERACTION-MAP

This parallel sprint is what makes Full-Stack-First efficient. You don't waste time designing MCP first then screens, or screens first then MCP.

### Steps 10-21: Building on both interfaces

**[10] DATA-MODEL** — Indexes optimized for BOTH MCP query patterns AND dashboard query patterns. Query Pattern Registry covers all consumers.
**[11] API-CONTRACTS** — REST API wraps MCP tools AND feeds dashboard screens. Dual-role documented.
**[12] USER-STORIES** — Client-facing stories with acceptance criteria for both MCP and dashboard.
**[13] BACKLOG** — Stories reference interaction IDs, MCP tools, AND dashboard screens. Sprint order: shared services first, then interfaces, then cross-interface integration.
**[14] CLAUDE.md** — Documents the Shared Service pattern as THE core pattern. Forbidden: logic in handlers.
**[15] ENFORCEMENT** — The `/new-interaction` skill scaffolds ALL layers at once: service + MCP tool + REST route + dashboard component + tests.
**[16] INFRA-DESIGN** — Environments, CI/CD, observability, DR, and capacity planning.
**[17] MIGRATION-PLAN** — Cutover runbook, source-to-target mapping for enterprise deployments.
**[18] TESTING** — Cross-interface tests verify MCP and dashboard work together. Parity tests ensure MCP and REST return identical data. LLM evaluation framework.
**[19] FAULT-TOLERANCE** — 5-layer failure scenarios with on-call procedures.
**[20] GUARDRAILS-SPEC** — 4-layer AI safety guardrails (input, processing, output, governance).
**[21] COMPLIANCE-MATRIX** — SOC2/GDPR/EU AI Act/NIST mapping for auditors.

---

## The Dependency Graph

```
Discovery Sessions
  │
  └──→ [0] BRD ──┐
                  │
  Raw Spec ───────┤
                  │
  ├──→ [1] ROADMAP ────────────────────────────────────────────────┐
  │                                                                 │
  └──→ [2] PRD ──┬──→ [3] ARCH ──┬──→ [4] FEATURES                 │
                 │               │       │                          │
                 │               │       └──→ [5] QUALITY           │
                 │               │               │                  │
                 │               │       [6] SECURITY-ARCH          │
                 │               │                                  │
                 │   PRD + ARCH + FEAT + QUALITY                    │
                 │       └──→ [7] INTERACTION-MAP ──────────────────┤  ← THE KEY
                 │               │                                  │
                 │        ┌──────┴──────┐                           │
                 │        ▼             ▼                           │
                 │   [8] MCP-SPEC  [9] DESIGN-SPEC                  │  ← PARALLEL
                 │        │             │                           │
                 │        └──────┬──────┘                           │
                 │               ▼                                  │
                 │          [10] DATA-MODEL                          │
                 │               │                                  │
                 │          [11] API-CONTRACTS                       │
                 │               │                                  │
                 │          [12] USER-STORIES                        │
                 │               │                                  │
                 │   ┌──── [13] BACKLOG    [14] CLAUDE.md ──────────┘
                 │   │                          │
                 │   │                     [15] ENFORCEMENT
                 │   │                          │
                 │   │                     [16] INFRA-DESIGN
                 │   │                          │
                 │   │              ┌──── [17] MIGRATION ──── [18] TESTING  ← PARALLEL
                 │   │              │           │
                 │   │              │      [19] FAULT-TOLERANCE
                 │   │              │           │
                 │   │              │      [20] GUARDRAILS-SPEC
                 │   │              │           │
                 └───┴──────────────┴──── [21] COMPLIANCE-MATRIX
```

---

## When to Use Full-Stack-First

Use Full-Stack-First when your product has:
- **AI users AND human users** who need different interfaces
- **Cross-interface workflows** (AI triggers, human approves)
- **Data parity requirements** (MCP and dashboard must show the same data)
- **Equal investment in both interfaces** (not "dashboard is a nice-to-have")

Examples:
- AI agent control planes with operator dashboards
- Developer tools with management reporting
- LLM-powered workflows with human oversight screens
- Any platform where the question is "both" when asked "MCP or Dashboard?"

## When NOT to Use Full-Stack-First

- **No dashboard needed** → Use MCP-First (13 docs)
- **No AI/MCP users** → Use Design-First (12 docs)
- **Backend-only, no UI or MCP** → Use API-First (12 docs)
- **Very simple product** → Full-Stack adds overhead; pick the simplest approach that fits

---

## TL;DR

**Full-Stack-First designs MCP tools and dashboard screens in parallel, unified by a shared INTERACTION-MAP (Doc 7).** The INTERACTION-MAP defines every interaction, its data shape, and its name — once. Both MCP and dashboard specs reference these shared definitions. The backend (shared service layer, data model, API) is derived from what BOTH interfaces need. Result: no divergence, no wasted effort, and cross-interface workflows that actually work.
