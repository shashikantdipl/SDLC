# SDLC Specification Workspace

## Project
| Field | Value |
|-------|-------|
| Name | Agentic SDLC Platform |
| Purpose | AI agent control plane — 48 agents across 7 SDLC phases |
| Approach | **Full-Stack-First** (24 documents) |
| Raw Spec | `Requirement/MASTER-BUILD-SPEC.md` |
| Generated Output | `Generated-Docs/` |
| Prompt Templates | `Base_prompts/Full-Stack-First/` (read-only reference) |

## What This Workspace Is
This is a **specification workspace**, not a code repo. It contains:
- Prompt templates for generating SDLC documents (4 approaches: API-First, Design-First, MCP-First, Full-Stack-First)
- Generated documents produced by those prompts
- The master build specification that serves as raw input
- Agent SDK with LLM-agnostic provider layer (Anthropic, OpenAI, Ollama)
- GOVERN agents (G1-G4) — live, tested with real LLM calls

## Active Approach: Full-Stack-First (v2 — 24-Document Stack)
We use the Full-Stack-First approach which produces **24 documents** across Pre-Phase + Phases A-E:

### Pre-Phase — Business Discovery
- Doc 16: BRD (Business Requirements)

### Phase A — Foundations
- Docs 00-02: ROADMAP, PRD, ARCH ★(upgraded: +memory, +routing, +RAG)

### Phase B — Decomposition
- Doc 05: FEATURE-CATALOG ★(upgraded: 18-field JSON, ai_required)
- Doc 04: QUALITY ★(upgraded: per-module thresholds, SLI/SLO)
- Doc 17: SECURITY-ARCH (NEW: auth, RBAC, threat model, data governance, SBOM)

### Phase C — Interface Design
- Docs 06-08: INTERACTION-MAP, MCP-TOOL-SPEC, DESIGN-SPEC

### Phase D — Data & Build-Facing
- Docs 09-11: DATA-MODEL, API-CONTRACTS, BACKLOG
- Doc 18: USER-STORIES (NEW: client-facing stories with SACs)
- Doc 03: CLAUDE.md (delayed from Phase A — now has full context)
- Doc 12: ENFORCEMENT ★(upgraded: +prompt versioning, +API governance)

### Phase E — Operations, Safety & Compliance
- Doc 19: INFRA-DESIGN (NEW: environments, CI/CD, observability, DR, capacity)
- Doc 20: MIGRATION-PLAN (NEW: cutover runbook, phased approach)
- Doc 13: TESTING ★(upgraded: +LLM eval framework, +go-live checklist)
- Doc 21: FAULT-TOLERANCE (NEW: 5-layer failure scenarios, on-call procedures)
- Doc 22: GUARDRAILS-SPEC (NEW: 4-layer AI safety guardrails — unique to AI-native)
- Doc 23: COMPLIANCE-MATRIX (NEW: SOC2/GDPR/EU AI Act/NIST cross-reference)

### Protocol Documents
- Doc 14: AGENT-HANDOFF-PROTOCOL
- Doc 15: AGENT-INTERACTION-DIAGRAM

### Key Innovations
- **INTERACTION-MAP** (Doc 06) coordinates MCP tools and dashboard screens in parallel
- **FEATURE-CATALOG before QUALITY** — enables per-module coverage thresholds
- **GUARDRAILS-SPEC** — AI safety guardrails that don't exist in traditional SDLC
- **COMPLIANCE-MATRIX** — audit-ready cross-reference for regulated industries
- **LLM-agnostic architecture** — agents work on Anthropic, OpenAI, or Ollama

## Build Sequence
See `Base_prompts/Full-Stack-First/Correct Build Sequence.md` for the v2 dependency graph (22 steps, zero circular dependencies verified).

## Rules
- Generated documents go in `Generated-Docs/` only
- Every generated document must have a version header and generation date
- Document numbering: 00-15 (original), 16-23 (new in v2)
- Prompt templates in `Base_prompts/` are read-only references — never modify them during generation
- Always commit each generated document individually with message format: `docs: generate {NN}-{DOC} using Full-Stack-First approach`
- ★ marks documents upgraded in v2 with new sections

## Development Plan
See `.claude/plans/rosy-growing-stream.md` for the 25-milestone execution plan.
