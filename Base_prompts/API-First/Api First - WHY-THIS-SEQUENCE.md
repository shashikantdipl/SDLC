# Why This Sequence? — API-First Approach

## Who Is This For?

You're probably a developer, designer, or project manager who just got access to this framework and is wondering: **"Why are there 12 documents? Why this specific order? Can't I just start coding?"**

This page explains the reasoning so you can work confidently — even if you've never used an AI-assisted SDLC pipeline before.

---

## The Short Answer

Each document **feeds the next one**. If you skip a step or reorder them, the AI agent producing the next document won't have the information it needs — and will either hallucinate (make things up) or produce vague, unusable output.

Think of it like cooking: you can't frost a cake before you bake it, and you can't bake it before you mix the batter. Same principle.

---

## The 12 Documents, Explained Like You're New

### Step 1: ROADMAP (Doc 0)
**What it answers:** "What's the plan? What exists today? What are we building?"

This is your project's GPS. Without it, nobody knows where they're going. It lists every deliverable as a specific file path (not vague goals), sets timelines, and identifies risks.

**Why first?** Everything else assumes you know the project context. CLAUDE.md (step 4) reads the ROADMAP to understand what repo structure to describe.

---

### Step 2: PRD (Doc 1)
**What it answers:** "What are we building and who is it for?"

The PRD defines the WHAT — not the how. It creates personas (real people with names, not "User A"), user journeys, and capability clusters. Every downstream document references these personas and capabilities.

**Why second?** The architecture (step 3) needs to know WHAT the system does before deciding HOW to build it. Features (step 6) decompose PRD capabilities. Design (step 11) uses PRD personas to decide which screens exist.

---

### Step 3: ARCH (Doc 2)
**What it answers:** "How is the system structured? What tech stack? What components?"

This is where you decide: Python or TypeScript? PostgreSQL or DynamoDB? Monolith or microservices? Every decision includes what was rejected and why.

**Why third?** It only needs the PRD. Everything after this — coding rules, data models, API endpoints — depends on knowing the architecture.

**Why not later?** Almost every document after this reads ARCH.md. If ARCH came after features or data models, those documents would have to guess at the tech stack.

---

### Step 4: CLAUDE.md (Doc 3)
**What it answers:** "What are the coding rules for this project?"

This is the file Claude Code reads before writing any code. It contains: language rules, repo structure, implementation patterns, forbidden patterns, and key commands.

**Why fourth?** It needs both ROADMAP (project context) and ARCH (tech stack). It can't tell Claude Code "use Ruff for linting" if the architecture hasn't decided on Python yet.

---

### Step 5: QUALITY (Doc 4)
**What it answers:** "What are the non-functional requirements? How fast? How reliable? How secure?"

Every NFR gets a Q-NNN ID (like Q-001, Q-002) with a specific measurable threshold and an automated way to verify it. Other documents cite these IDs.

**Why fifth?** It needs PRD (success metrics become NFRs) and ARCH (infrastructure determines what targets are realistic). It must exist before DATA-MODEL (which applies data NFRs) and TESTING (which verifies all NFRs).

---

### Step 6: FEATURE-CATALOG (Doc 5)
**What it answers:** "What are all the discrete features?"

This is a JSON file (not markdown) that decomposes PRD capabilities into individual features with MoSCoW priority, story points, and dependencies.

**Why sixth?** It needs PRD capabilities and ARCH component boundaries. DATA-MODEL (step 8) and BACKLOG (step 9) both consume this.

---

### Step 7: CLAUDE-ENFORCEMENT (Doc 6)
**What it answers:** "How do we automate the coding rules?"

This creates the `.claude/` directory with rule files and skills that enforce CLAUDE.md automatically.

**Why seventh?** It only needs CLAUDE.md and ARCH — both available. It's a terminal document (nothing depends on it), so placing it here keeps the pipeline flowing without blocking anything.

---

### Step 8: DATA-MODEL (Doc 7)
**What it answers:** "What are the database tables, indexes, and storage patterns?"

Complete SQL DDL that developers copy into migration scripts.

**Why eighth?** It needs ARCH (which database), FEATURE-CATALOG (which features need persistence), and QUALITY (data retention/encryption NFRs). API-CONTRACTS (step 10) needs this to know which entities to expose.

---

### Step 9: BACKLOG (Doc 8)
**What it answers:** "What are the user stories in sprint order?"

Converts features into implementable stories with Given/When/Then acceptance criteria.

**Why ninth?** It needs FEATURE-CATALOG, PRD, ARCH, and QUALITY — all available. It's terminal (nothing depends on it), and placing it here lets developers start sprint planning while the remaining docs are generated.

---

### Step 10: API-CONTRACTS (Doc 9)
**What it answers:** "What are the REST endpoints, WebSocket channels, and error codes?"

Every endpoint is fully specified: method, path, request/response schema, which persona uses it.

**Why tenth?** It needs ARCH (API technology), DATA-MODEL (which entities to expose), and PRD (user journeys). In this API-First approach, **endpoints are designed from the data model up** — the backend defines what's available, and the UI adapts to it.

**This is the defining choice of API-First:** APIs are shaped by data and capabilities, not by screen layouts.

---

### Step 11: DESIGN-SPEC (Doc 10)
**What it answers:** "What does every screen look like?"

Every screen is specified: layout, data elements, interactions, loading/empty/error states, and — critically — **which API endpoint supplies its data**.

**Why eleventh (near the end)?** Because in API-First, **screens are designed against existing API endpoints**. The DESIGN-SPEC can reference real endpoints like `GET /api/v1/fleet/health` because API-CONTRACTS already defined them. No phantom data sources. No guessing.

**When is this the right choice?** When you're building:
- A developer platform or internal tool (users care about data, not aesthetics)
- A system with many API consumers (CLI, SDK, webhooks — not just a UI)
- Microservices where APIs are the contract between teams

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
                 │   CLAUDE + ARCH ──→ [6] ENFORCE│
                 │                               │
                 │   ARCH + FEATURES + QUALITY    │
                 │       └──→ [7] DATA-MODEL ─────┤
                 │                               │
                 │   FEATURES + PRD + ARCH + QUAL │
                 │       └──→ [8] BACKLOG         │
                 │                               │
                 │   ARCH + DATA-MODEL + PRD      │
                 │       └──→ [9] API-CONTRACTS ──┤
                 │                               │
                 │   PRD + API-CONTRACTS + QUALITY │
                 │       └──→ [10] DESIGN-SPEC    │
                 │                               │
                 │   ARCH + QUALITY + DATA + CLAUDE│
                 └───────→ [11] TESTING           │
```

---

## Common Questions

### "Can I run some steps in parallel?"
Yes. Steps 4 (QUALITY), 5 (FEATURE-CATALOG), and 3 (CLAUDE.md) can run in parallel — they all depend only on ROADMAP/PRD/ARCH. Steps 8 (BACKLOG) and 7 (DATA-MODEL) can also overlap.

### "What if I already have a PRD?"
Feed it into step 2 instead of generating one. The pipeline continues from step 3.

### "What if my project has no UI?"
Skip step 11 (DESIGN-SPEC). The other 11 documents still apply — APIs, data models, tests, and quality specs are universal.

### "Why not just start coding?"
Because the AI agent writing your code needs context. Without a PRD, it doesn't know who the users are. Without ARCH, it doesn't know which language to use. Without QUALITY, it doesn't know what "good enough" means. The 12 documents give the AI (and your team) complete context to produce correct code on the first try.

### "Why API-First instead of Design-First?"
Use API-First when the backend is the product (APIs, SDKs, platforms, data pipelines). Use Design-First (see the other folder) when the UI is the product (consumer apps, dashboards, SaaS tools).

---

## TL;DR

**Each document exists because the next one needs it.** The order isn't arbitrary — it's a dependency chain. Skip a step and downstream documents produce garbage. Follow the sequence and you get 12 interconnected, consistent deliverables that give any AI agent (or developer) everything they need to build the complete app.
