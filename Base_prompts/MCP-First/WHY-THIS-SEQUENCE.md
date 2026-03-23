# Why This Sequence? — MCP-First Approach

## Who Is This For?

You're a developer building an AI-native platform and wondering: "Why 13 documents? Why MCP before API? What even is MCP-First?"

This page explains everything.

---

## What is MCP?

**MCP (Model Context Protocol)** is Anthropic's open standard for connecting AI models to external tools, data, and services. Think of it as USB-C for AI — a universal connector.

When you build an MCP server, any MCP-compatible AI client can connect to it:
- Claude Code (Anthropic's CLI)
- Claude Desktop
- Cursor
- Windsurf
- Any future MCP-compatible tool

## What Makes This "MCP-First"?

In traditional approaches:
- **API-First:** Design REST endpoints → build backend → add UI → maybe add MCP later
- **Design-First:** Design screens → derive API → build backend → maybe add MCP later
- **MCP-First:** Design MCP tools → derive REST API from MCP → add dashboard for monitoring

MCP-First means your platform is **designed to be used by AI clients natively**. The REST API is a thin wrapper around MCP tool handlers. The dashboard is a monitoring window.

```
Primary:   MCP Servers ← AI clients connect here (Claude Code, Cursor)
     ↓ wraps
Secondary: REST API ← Programs connect here (CI/CD, webhooks, scripts)
     ↓ consumes
Tertiary:  Dashboard ← Humans look here (monitoring, approvals)
```

## Why MCP-First for AI Platforms?

If your product is used BY developers who use AI coding assistants, MCP-First is the natural choice:

1. **Your users already live in Claude Code** — MCP is their native interface
2. **AI agents ARE your product** — MCP is how AI connects to tools
3. **REST API comes free** — MCP tool handlers ARE your business logic; REST just wraps them
4. **Future-proof** — Every new MCP client gets access to your platform automatically
5. **Better AI experience** — MCP tools have descriptions and schemas that help AI clients make the right calls

## The 13 Documents, Explained

### Steps 1-5: Same as API-First and Design-First
ROADMAP, PRD, ARCH, CLAUDE.md, and QUALITY are universal. Every approach needs them. The only difference: ARCH (Step 3) now centers around MCP servers as primary containers, and QUALITY (Step 5) includes MCP-specific NFRs.

### Step 6: FEATURE-CATALOG — Features Tagged with MCP Servers
Same as other approaches, but each feature now indicates which MCP server it belongs to. This creates the mapping from capabilities to MCP interface.

### Step 7: MCP-TOOL-SPEC (THE KEY DOCUMENT)
This is the document that doesn't exist in API-First or Design-First. It defines:
- **MCP Servers** — How many, what domain each covers
- **Tools** — What actions AI clients can take (with JSON Schema inputs)
- **Resources** — What data AI clients can read (with URI patterns)
- **Prompts** — Pre-built prompt templates for common workflows
- **REST derivation** — How each MCP tool maps to a REST endpoint

This document drives everything downstream: DATA-MODEL indexes are optimized for MCP query patterns, API-CONTRACTS wraps MCP tools, BACKLOG stories implement MCP tools first, TESTING includes MCP protocol tests.

### Step 8: DATA-MODEL — Optimized for MCP Queries
Same as other approaches, but with a new section: "MCP Query Patterns" — a table mapping each MCP tool to the database queries it runs. This ensures indexes exist for every MCP tool's access pattern.

### Step 9: API-CONTRACTS — REST Wraps MCP
Here's the key difference: instead of designing REST endpoints from scratch, every endpoint is documented as "wraps MCP tool X." This ensures:
- No capability exists in REST that doesn't exist in MCP
- Error codes are consistent between MCP and REST
- Adding a new MCP tool automatically implies a new REST endpoint

### Steps 10-13: Terminal Documents
ENFORCEMENT adds MCP-specific rules and skills (/new-mcp-tool). BACKLOG priorities MCP stories first. DESIGN-SPEC adds an MCP monitoring panel. TESTING adds MCP protocol compliance tests.

## The Dependency Graph

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
                 │   PRD + ARCH + FEAT + QUALITY  │
                 │       └──→ [6] MCP-TOOL-SPEC ──┤  ← THE KEY
                 │               │               │
                 │   ARCH + FEAT + QUAL + MCP     │
                 │       └──→ [7] DATA-MODEL ─────┤
                 │                               │
                 │   ARCH + DATA + PRD + MCP      │
                 │       └──→ [8] API-CONTRACTS ──┤
                 │                               │
                 │   CLAUDE + ARCH ──→ [9] ENFORCE│
                 │                               │
                 │   FEAT + PRD + ARCH + QUAL + MCP
                 │       └──→ [10] BACKLOG        │
                 │                               │
                 │   PRD + API + QUALITY          │
                 │       └──→ [11] DESIGN-SPEC    │
                 │                               │
                 │   ARCH + QUAL + DATA + CLAUDE + MCP
                 └───────→ [12] TESTING           │
```

## Common Questions

### "How is MCP different from a REST API?"
REST is request/response over HTTP. MCP is a protocol that lets AI models discover and use tools. The key difference: MCP tools have **descriptions and schemas** that AI clients use to decide when and how to call them. REST endpoints don't self-describe to AI.

### "Can I have both MCP and REST?"
Yes — that's exactly what MCP-First does. MCP is the primary interface, REST wraps it for non-AI consumers. Same backend, two interfaces.

### "What if my users don't use Claude Code?"
Then MCP-First might not be the right choice. Use API-First for backend-heavy platforms or Design-First for UI-heavy products.

### "Does MCP replace REST?"
No. MCP and REST coexist. MCP is for AI clients. REST is for everything else (webhooks, CI/CD, scripts, mobile apps). MCP-First just means you design MCP first and derive REST from it.

### "What's the extra effort for MCP-First vs API-First?"
One additional document (MCP-TOOL-SPEC) and MCP-specific sections in ARCH, QUALITY, ENFORCEMENT, and TESTING. The REST API effort actually decreases because it's derived from MCP tools rather than designed from scratch.

## TL;DR

**MCP-First means your AI platform speaks AI natively.** Instead of forcing AI clients to call REST APIs (designed for programs) or scrape dashboards (designed for humans), you give them MCP tools designed specifically for AI. The REST API and dashboard still exist — they just derive from the MCP layer instead of the other way around.
