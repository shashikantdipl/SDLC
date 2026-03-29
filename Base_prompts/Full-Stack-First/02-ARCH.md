# Prompt 2 — Generate ARCH.md

## Role
You are an architecture drafter agent. You produce ARCH.md — Document #2 in the 14-document SDLC stack (Full-Stack-First approach). This defines HOW the system is built.

## Approach: Full-Stack-First
The architecture has THREE interface layers of equal importance:
1. **MCP Servers** — AI clients connect here
2. **REST API** — Programs connect here (also feeds the dashboard)
3. **Dashboard** — Humans look here

All three share the same backend services and database. The key architectural insight is the **shared service layer** — MCP tool handlers and API route handlers call the same service functions.

```
MCP Servers ──┐
              ├──→ Shared Service Layer ──→ Database
REST API ─────┤
              │
Dashboard ────┘ (consumes REST API)
```

## Input Required
- PRD.md (capabilities C1-Cn)
- Infrastructure constraints

## Output: ARCH.md

### Required Sections

1. **System Context (C4 Level 1)** — ASCII diagram showing:
   - AI clients (Claude Code, Cursor) connecting via MCP
   - REST API clients (CI/CD, webhooks, scripts)
   - Dashboard users (operators, managers)
   - External systems (LLM providers, databases, messaging)
   - All connecting to the platform

2. **Container Architecture (C4 Level 2)** — Table listing every container:
   - MCP Server(s) — primary AI interface
   - REST API — programmatic interface + dashboard backend
   - Dashboard — human visual interface
   - Backend services — shared business logic
   - Database — persistence
   - Each: name, technology, responsibility, deployment

3. **Shared Service Layer** — NEW section (unique to Full-Stack-First):
   ```
   ┌─────────────┐  ┌─────────────┐
   │ MCP Server   │  │ REST API     │
   │ Tool Handler │  │ Route Handler│
   └──────┬───────┘  └──────┬───────┘
          │                 │
          ▼                 ▼
   ┌─────────────────────────────────┐
   │     Shared Service Layer         │
   │  PipelineService                 │
   │  AgentService                    │
   │  CostService                     │
   │  AuditService                    │
   │  ApprovalService                 │
   └──────────────┬──────────────────┘
                  ▼
   ┌─────────────────────────────────┐
   │          Database                │
   └──────────────────────────────────┘
   ```
   For each service: name, methods, which MCP tools use it, which API routes use it.
   This ensures MCP and REST never diverge in behavior.

4. **MCP Server Architecture** — Same as MCP-First:
   - How many servers, grouped by domain
   - Transport, auth, tool/resource/prompt counts

5. **Dashboard Architecture** — Same as Design-First:
   - Frontend framework (Streamlit / Next.js / etc.)
   - Key views/screens
   - Real-time update strategy (polling / WebSocket / SSE)
   - How it consumes REST API

6. **Component Diagram (C4 Level 3)** — Internal components.

7. **Tech Stack Decisions** — Minimum 12 decisions including:
   - MCP SDK choice
   - MCP transport
   - Frontend framework
   - REST framework
   - Shared service layer pattern (dependency injection / module imports)

8. **Cross-Cutting Concerns** — Auth, multi-tenancy, observability, error handling.
   Must address:
   - How auth works across MCP, REST, and dashboard (unified or separate?)
   - How errors propagate through MCP vs REST vs dashboard
   - How observability spans all three interfaces

9. **Data Flow Diagrams** — TWO primary flows:
   - MCP path: AI Client → MCP tool → Service → DB → response
   - Dashboard path: User → Dashboard → REST API → Service → DB → render

10. **Interface Parity Matrix** — NEW section:
    Table showing which capabilities are available via which interface:
    | Capability | MCP | REST | Dashboard |
    Ensures nothing is accidentally missing from an interface.

11. **What I'd Do Differently at 10x Scale**

### Section: Agent Memory Architecture
Define the memory tiers for all 48 agents:
- **Short-term memory**: Conversation buffer within a single invocation (context window)
- **Working memory**: Session context shared between agents during a pipeline run (PostgreSQL session_context table)
- **Episodic memory**: Audit trail of past invocations, decisions, and outcomes (audit_events table)
- **Semantic memory**: Domain knowledge accumulated across projects (exception_catalog, cost patterns)
- **Procedural memory**: Learned optimization patterns (prompt effectiveness scores, model tier recommendations)

Define: Storage tier per memory type | Retention policy | Isolation boundaries (per-agent, per-project, global) | Access patterns

### Section: LLM Provider Routing Layer
Define the model routing architecture (references sdk/llm/):
- **Tier mapping**: fast → Haiku/GPT-4o-mini/Llama3.2, balanced → Sonnet/GPT-4o/Mistral, powerful → Opus/GPT-4.5/Llama3.1-405b
- **Routing strategy**: Manifest-driven (each agent declares tier), environment-driven (LLM_PROVIDER env var), fallback chain
- **Circuit breaker**: 5 consecutive failures → mark provider unhealthy → failover to next provider
- **Cost-aware routing**: If budget < 20% remaining, downgrade tier (powerful→balanced, balanced→fast)
- **Provider health check**: Periodic ping, latency tracking, error rate monitoring

### Section: Knowledge Retrieval (RAG) Architecture
If the platform uses retrieval-augmented generation:
- **Vector store**: Per-project vector store for document embeddings
- **Chunking strategy**: Document-level for specifications, semantic segments for code
- **Retrieval pattern**: Query expansion → vector search → re-ranking → context injection
- **Knowledge sources**: Generated-Docs, codebase, audit history, cost patterns
- **Isolation**: Per-project knowledge boundary — agents cannot access other projects' data

### Quality Criteria
- Shared service layer is clearly defined (MCP and REST never implement logic independently)
- Interface parity matrix is complete
- Both MCP and dashboard architecture are equally detailed
- Data flow diagrams show both paths

### Anti-Patterns to Avoid
- MCP handlers and REST handlers implementing the same logic independently (must share services)
- Dashboard making direct DB calls (must go through REST API)
- One interface more detailed than the other
- Missing the shared service layer (leads to divergent behavior)
