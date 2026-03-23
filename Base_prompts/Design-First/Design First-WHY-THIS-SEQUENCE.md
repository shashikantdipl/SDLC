# Why This Sequence? — Design-First Approach

## Who Is This For?

You're probably a developer, designer, or project manager who just got access to this framework and is wondering: **"Why are there 12 documents? Why this specific order? Can't I just start coding?"**

This page explains the reasoning so you can work confidently — even if you've never used an AI-assisted SDLC pipeline before.

---

## The Short Answer

Each document **feeds the next one**. If you skip a step or reorder them, the AI agent producing the next document won't have the information it needs — and will either hallucinate (make things up) or produce vague, unusable output.

Think of it like cooking: you can't frost a cake before you bake it, and you can't bake it before you mix the batter. Same principle.

---

## What Makes This "Design-First"?

In this approach, **screens are designed before the database and API**. The idea is simple:

> Users don't interact with databases. They interact with screens. So design the screens first, then build the backend to serve exactly what the screens need.

This means:
- DESIGN-SPEC comes at step 7 (right after features are cataloged)
- DATA-MODEL reads DESIGN-SPEC to know what data the screens need
- API-CONTRACTS reads DESIGN-SPEC to create endpoints that serve each screen
- BACKLOG references specific screens so developers know what they're building

Compare with API-First (in the other folder), where APIs are designed from the data model and the UI adapts to whatever the API provides.

---

## The 12 Documents, Explained Like You're New

### Step 1: ROADMAP (Doc 0)
**What it answers:** "What's the plan? What exists today? What are we building?"

This is your project's GPS. Without it, nobody knows where they're going. It lists every deliverable as a specific file path (not vague goals), sets timelines, and identifies risks.

**Why first?** Everything else assumes you know the project context. CLAUDE.md (step 4) reads the ROADMAP to understand what repo structure to describe.

---

### Step 2: PRD (Doc 1)
**What it answers:** "What are we building and who is it for?"

The PRD defines the WHAT — not the how. It creates personas (real people with names, not "User A"), user journeys, and capability clusters.

**Why second?** Everything downstream needs to know: Who are the users? What are their goals? What journeys must the product support? The PRD is referenced by almost every other document.

---

### Step 3: ARCH (Doc 2)
**What it answers:** "How is the system structured? What tech stack? What components?"

This is where you decide: React or Vue? PostgreSQL or MongoDB? Monolith or microservices? Every decision includes what was rejected and why.

**Why third?** It only needs the PRD. Everything after this — coding rules, data models, API endpoints, even screen design — depends on knowing the architecture (e.g., "is this a Next.js app or a native mobile app?").

---

### Step 4: CLAUDE.md (Doc 3)
**What it answers:** "What are the coding rules for this project?"

This is the file Claude Code reads before writing any code. It contains: language rules, repo structure, implementation patterns, forbidden patterns, and key commands.

**Why fourth?** It needs both ROADMAP (project context) and ARCH (tech stack). It can't tell Claude Code "use Biome for formatting" if the architecture hasn't decided on TypeScript yet.

---

### Step 5: QUALITY (Doc 4)
**What it answers:** "What are the non-functional requirements? How fast? How reliable? How secure?"

Every NFR gets a Q-NNN ID (like Q-001, Q-002) with a specific measurable threshold and an automated way to verify it. Other documents cite these IDs.

**Why fifth?** It needs PRD (success metrics become NFRs) and ARCH (infrastructure determines realistic targets). DESIGN-SPEC (step 7) needs this for accessibility and performance NFRs. TESTING (step 12) verifies every NFR.

---

### Step 6: FEATURE-CATALOG (Doc 5)
**What it answers:** "What are all the discrete features?"

This is a JSON file (not markdown) that decomposes PRD capabilities into individual features with MoSCoW priority, story points, and dependencies.

**Why sixth?** It needs PRD capabilities and ARCH component boundaries. DESIGN-SPEC (next step) uses this to know which features need screens.

---

### Step 7: DESIGN-SPEC (Doc 6) — THE KEY STEP
**What it answers:** "What does every screen look like? What data does each screen need?"

Every screen is specified: layout, data elements, interactions, loading/empty/error states, and — critically — **what data the screen requires** (entities, fields, relationships).

**Why seventh? This is the defining choice of Design-First.**

At this point we have:
- PRD (who the users are, what journeys they take)
- ARCH (what frontend framework, what deployment model)
- QUALITY (accessibility requirements, load time targets)
- FEATURE-CATALOG (which features need UI representation)

That's everything you need to design screens. You DON'T need API endpoints yet — because **the screens will tell us what APIs to build.**

Each screen specifies a "Data requirements" section instead of "Data source (API endpoint)". This section describes WHAT data the screen needs (e.g., "list of agents with status, cost, and last-run timestamp"), and the DATA-MODEL and API-CONTRACTS that come next will fulfill those requirements.

**When is this the right choice?** When you're building:
- A consumer-facing app where user experience is the product
- A dashboard where operators need to see specific information at a glance
- A SaaS tool where users interact primarily through a web UI
- Any product where the question "what should the user see?" comes before "what data do we have?"

---

### Step 8: DATA-MODEL (Doc 7)
**What it answers:** "What are the database tables, indexes, and storage patterns?"

Complete SQL DDL that developers copy into migration scripts.

**Why eighth?** It needs ARCH (which database), FEATURE-CATALOG (which features need persistence), QUALITY (data retention/encryption NFRs), and now — **DESIGN-SPEC** (what data each screen displays). The schema is designed to support the screens, not the other way around.

**Example:** If DESIGN-SPEC says "Screen S3: Agent Detail shows cost_per_run, total_runs_today, and avg_latency_ms", then DATA-MODEL ensures those fields exist (or can be computed from what exists).

---

### Step 9: API-CONTRACTS (Doc 8)
**What it answers:** "What are the REST endpoints, WebSocket channels, and error codes?"

Every endpoint is fully specified: method, path, request/response schema, and **which screens consume it**.

**Why ninth?** It needs ARCH (API technology), DATA-MODEL (entity schemas), PRD (user journeys), and **DESIGN-SPEC** (which screens need which data). In Design-First, **every endpoint exists because a screen needs it**. No orphan APIs. No phantom data sources.

**Example:** If Screen S1 needs a table of all agents with status badges, API-CONTRACTS defines `GET /api/v1/agents?status=active&fields=id,name,status,cost_today` — because the screen told us exactly what it needs.

---

### Step 10: BACKLOG (Doc 9)
**What it answers:** "What are the user stories in sprint order?"

Converts features into implementable stories with Given/When/Then acceptance criteria. In Design-First, every UI story includes a `screens` field referencing which DESIGN-SPEC screens it affects.

**Why tenth?** It needs FEATURE-CATALOG, PRD, ARCH, QUALITY, and **DESIGN-SPEC**. Stories can now say: "Implement Screen S3 — Agent Detail view with cost breakdown chart (references F-012, Q-003)." Developers know exactly what to build and what it should look like.

---

### Step 11: CLAUDE-ENFORCEMENT (Doc 10)
**What it answers:** "How do we automate the coding rules?"

This creates the `.claude/` directory with rule files and skills that enforce CLAUDE.md automatically.

**Why eleventh?** It only needs CLAUDE.md and ARCH — both long available. It's a terminal document (nothing depends on it), so it sits near the end to keep the critical path clear.

---

### Step 12: TESTING (Doc 11)
**What it answers:** "How do we test everything?"

Test frameworks, database strategy (real databases, never mocks), coverage thresholds, CI pipeline.

**Why last?** It references ARCH (test tooling), QUALITY (coverage thresholds), DATA-MODEL (test data strategy), and CLAUDE.md (conventions). It needs the most context.

---

## The Dependency Graph (Visual)

```
Raw Spec
  │
  ├──→ [0] ROADMAP ──────────────────────────────┐
  │                                               │
  └──→ [1] PRD ──┬──→ [2] ARCH ──┬──→ [3] CLAUDE ┤
                 │               │               │
                 ├───────────────┼──→ [4] QUALITY │
                 │               │               │
                 ├───────────────┴──→ [5] FEATURES│
                 │                               │
                 │   PRD + ARCH + QUALITY + FEAT  │
                 │       └──→ [6] DESIGN-SPEC ────┤  ← THIS IS THE KEY
                 │               │               │
                 │   ARCH + FEAT + QUAL + DESIGN  │
                 │       └──→ [7] DATA-MODEL ─────┤
                 │                               │
                 │   ARCH + DATA + PRD + DESIGN   │
                 │       └──→ [8] API-CONTRACTS   │
                 │                               │
                 │   FEAT + PRD + ARCH + QUAL + DESIGN
                 │       └──→ [9] BACKLOG         │
                 │                               │
                 │   CLAUDE + ARCH ──→ [10] ENFORCE
                 │                               │
                 │   ARCH + QUAL + DATA + CLAUDE  │
                 └───────→ [11] TESTING           │
```

Notice how DESIGN-SPEC (Doc 6) feeds into DATA-MODEL, API-CONTRACTS, and BACKLOG — the screens drive what gets built.

---

## Common Questions

### "Can I run some steps in parallel?"
Yes. Steps 3 (CLAUDE.md), 4 (QUALITY), and 5 (FEATURE-CATALOG) can run in parallel — they only depend on ROADMAP/PRD/ARCH. Steps 9 (BACKLOG) and 10 (CLAUDE-ENFORCEMENT) can also overlap since they don't depend on each other.

### "What if I already have mockups or wireframes?"
Feed them into step 7 (DESIGN-SPEC) as additional input alongside PRD and FEATURE-CATALOG. The AI agent will formalize your wireframes into the full spec format with data requirements, states, and accessibility.

### "What if my project has no UI?"
Use the **API-First** approach instead (see the other folder). Design-First only makes sense when screens exist. For pure APIs, CLIs, or data pipelines, API-First is the right sequence.

### "What if I already have a database?"
Feed the existing schema into step 8 (DATA-MODEL) and let the agent reconcile it with what the screens need. It will identify gaps — tables or columns the screens require that don't exist yet.

### "Why not just start coding?"
Because the AI agent writing your code needs context. Without a PRD, it doesn't know who the users are. Without DESIGN-SPEC, it doesn't know what the screens look like. Without QUALITY, it doesn't know what "good enough" means. The 12 documents give the AI (and your team) complete context to produce correct code on the first try.

### "Why Design-First instead of API-First?"
Use Design-First when the **user experience IS the product** — dashboards, consumer apps, SaaS tools. Use API-First (see the other folder) when the **backend IS the product** — developer platforms, microservices, data pipelines.

### "What's the practical difference?"
In API-First: you might build a perfectly functional `GET /api/v1/agents` endpoint that returns 47 fields, but the screen only needs 5 of them. Wasteful, but works.

In Design-First: the screen says "I need agent name, status, and cost_today." So the API returns exactly those 3 fields. No waste. But if a new consumer (CLI, webhook) needs different fields later, you'll need to update the API.

Neither approach is wrong. Pick the one that matches your product.

---

## TL;DR

**Each document exists because the next one needs it.** The order isn't arbitrary — it's a dependency chain. In Design-First, **screens come before APIs and databases** because users interact with screens, not SQL tables. The screens tell us what data to store and what endpoints to build — eliminating guesswork and ensuring the backend serves exactly what the frontend needs.
