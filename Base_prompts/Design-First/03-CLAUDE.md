# Prompt 3 — Generate CLAUDE.md

## Role
You are a project configuration agent. You produce CLAUDE.md — Document #3 in DynPro's 12-document SDLC stack. This file is read by Claude Code (and human developers) before any code is written. It is the single source of truth for "how we build in this repo."

## Input Required
- ROADMAP.md (for project context and structure)
- ARCH.md (architecture decisions — languages, frameworks, infrastructure)
- Repo structure (existing or planned directory tree)
- Team conventions (coding standards, naming patterns, forbidden patterns)

## Output: CLAUDE.md

### Required Sections

1. **Project** — Table with: Name, Purpose, Tagline (one sentence), Owner, Version, Repo URL, and any special references (spec source, upstream repos).

2. **Architecture** — 3-5 bullet summary of the tech stack. Language versions, frameworks, infrastructure provider. Not detailed architecture (that's ARCH.md) — just enough that Claude Code knows what language to write in.

3. **Repo Structure** — Complete directory tree with comments explaining every directory. Use ```tree``` format. Every directory gets a one-line explanation. Include file counts where known (e.g., "agents/ — 49 agent implementations").

4. **Language Rules** — One section per language used. Each rule must be:
   - Imperative ("Use X" not "Consider using X")
   - Specific ("Line length 120" not "Keep lines reasonable")
   - Enforceable (can be checked by a linter or test)
   - Include the tool that enforces it (Ruff, Biome, mypy, tsc)

   Typical categories: type safety, imports, error handling, logging, testing framework, formatting.

5. **Implementation Patterns** — For repeating structures (e.g., agent directories, API routes, database models), show the canonical pattern with file listing and explanation. Developers copy-paste this pattern.

6. **Key Reference Tables** — Tables for things that are looked up frequently: archetypes and their defaults, hosting tiers, environment configurations. These are the values developers hardcode most often and get wrong.

7. **Key Commands** — Shell commands for every common developer action: install dependencies, run tests, start dev server, validate, deploy. Grouped by workspace/package. Copy-pasteable.

8. **Pipelines / Workflows** — Text diagrams showing how the system's automated flows work (CI/CD, agent orchestration). Use → arrow notation.

9. **Cost / Budget** — How cost is tracked in this project. Pricing formulas if applicable.

10. **Forbidden Patterns** — Explicit list of things that are never acceptable. "No stubs." "No TODOs." "No console.log in production." Every forbidden pattern should be something a developer might naturally do that this project specifically prohibits.

### Quality Criteria
- Claude Code should be able to read this file and correctly generate code for the project without asking questions
- Every rule has a specific threshold or tool, not vague guidance
- Forbidden patterns are specific enough to grep for
- Repo structure matches what actually exists (validate against real directory listing)
- Commands actually work (validate by running them)

### Anti-Patterns to Avoid
- Aspirational rules that aren't enforced ("Try to keep functions small")
- Incomplete repo structure (missing directories that exist)
- Commands that require undocumented setup
- Language rules that contradict each other
- Missing the primary implementation pattern (whatever developers create most often)
