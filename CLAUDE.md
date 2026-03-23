# SDLC Specification Workspace

## Project
| Field | Value |
|-------|-------|
| Name | Agentic SDLC Platform |
| Purpose | AI agent control plane — 48 agents across 7 SDLC phases |
| Approach | **Full-Stack-First** (14+2 documents) |
| Raw Spec | `Requirement/MASTER-BUILD-SPEC.md` |
| Generated Output | `Generated-Docs/` |
| Prompt Templates | `Base_prompts/Full-Stack-First/` (read-only reference) |

## What This Workspace Is
This is a **specification workspace**, not a code repo. It contains:
- Prompt templates for generating SDLC documents (4 approaches: API-First, Design-First, MCP-First, Full-Stack-First)
- Generated documents produced by those prompts
- The master build specification that serves as raw input

## Active Approach: Full-Stack-First
We use the Full-Stack-First approach which produces **14 documents + 2 protocol docs**:
- Docs 00-13: ROADMAP, PRD, ARCH, CLAUDE, QUALITY, FEATURE-CATALOG, INTERACTION-MAP, MCP-TOOL-SPEC, DESIGN-SPEC, DATA-MODEL, API-CONTRACTS, BACKLOG, ENFORCEMENT, TESTING
- Doc 14: AGENT-HANDOFF-PROTOCOL
- Doc 15: AGENT-INTERACTION-DIAGRAM

The key innovation is the **INTERACTION-MAP** (Doc 06) which coordinates MCP tools and dashboard screens in parallel, preventing interface divergence.

## Build Sequence
See `Base_prompts/Full-Stack-First/Correct Build Sequence.md` for the dependency graph.

## Rules
- Generated documents go in `Generated-Docs/` only
- Every generated document must have a version header and generation date
- Document numbering follows Full-Stack-First: 00 through 13, plus 14 and 15
- Prompt templates in `Base_prompts/` are read-only references — never modify them during generation
- Always commit each generated document individually with message format: `docs: generate {NN}-{DOC} using Full-Stack-First approach`

## Development Plan
See `.claude/plans/rosy-growing-stream.md` for the 25-milestone execution plan.
