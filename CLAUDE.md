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

**Document number = build order.** Doc 00 is built first, Doc 21 is built last. Protocol docs (22-23) are built after Step 11.

### Pre-Phase — Business Discovery
- **00** BRD (Business Requirements)

### Phase A — Foundations
- **01** ROADMAP
- **02** PRD
- **03** ARCH ★ (upgraded: +memory, +routing, +RAG)

### Phase B — Decomposition
- **04** FEATURE-CATALOG ★ (upgraded: 18-field JSON, ai_required)
- **05** QUALITY ★ (upgraded: per-module thresholds, SLI/SLO)
- **06** SECURITY-ARCH

### Phase C — Interface Design
- **07** INTERACTION-MAP
- **08** MCP-TOOL-SPEC ‖ parallel with 09
- **09** DESIGN-SPEC ‖ parallel with 08

### Phase D — Data & Build-Facing
- **10** DATA-MODEL
- **11** API-CONTRACTS
- **12** USER-STORIES
- **13** BACKLOG
- **14** CLAUDE.md (delayed from Phase A — now has full context)
- **15** ENFORCEMENT ★ (upgraded: +prompt versioning, +API governance)

### Phase E — Operations, Safety & Compliance
- **16** INFRA-DESIGN
- **17** MIGRATION-PLAN ‖ parallel with 18
- **18** TESTING ★ (upgraded: +LLM eval, +go-live checklist) ‖ parallel with 17
- **19** FAULT-TOLERANCE
- **20** GUARDRAILS-SPEC
- **21** COMPLIANCE-MATRIX

### Protocol Documents
- **22** AGENT-HANDOFF-PROTOCOL
- **23** AGENT-INTERACTION-DIAGRAM

### Key Innovations
- **INTERACTION-MAP** (Doc 07) coordinates MCP tools and dashboard screens in parallel
- **FEATURE-CATALOG (04) before QUALITY (05)** — enables per-module coverage thresholds
- **GUARDRAILS-SPEC (20)** — AI safety guardrails that don't exist in traditional SDLC
- **COMPLIANCE-MATRIX (21)** — audit-ready cross-reference for regulated industries
- **LLM-agnostic architecture** — agents work on Anthropic, OpenAI, or Ollama

## Build Sequence
See `Base_prompts/Full-Stack-First/Correct Build Sequence.md` for the v2 dependency graph (22 steps, zero circular dependencies verified).

## Rules
- Generated documents go in `Generated-Docs/` only
- Every generated document must have a version header and generation date
- **Document number = build order** (00 through 23)
- Prompt templates in `Base_prompts/` are read-only references — never modify them during generation
- Always commit each generated document individually with message format: `docs: generate {NN}-{DOC} using Full-Stack-First approach`
- ★ marks documents upgraded in v2 with new sections

## Development Plan
See `.claude/plans/rosy-growing-stream.md` for the 25-milestone execution plan.
