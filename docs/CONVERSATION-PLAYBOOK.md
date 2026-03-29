# Conversation Playbook — How This Project Was Built

**Purpose:** This document captures every prompt and decision made during the development of the Agentic SDLC Platform. Follow this sequence to reproduce the project or understand the reasoning behind every architectural choice.

**Who this is for:** Colleagues joining the project, new team members, or anyone building a similar AI-native SDLC framework.

**Total conversation duration:** ~8 hours across multiple sessions
**Total API spend on agent testing:** ~$2.53
**Agents built:** 21/48 (GOVERN 5/5 + DESIGN 16)

---

## Table of Contents

1. [Phase 1: Understanding the Framework](#phase-1-understanding-the-framework)
2. [Phase 2: Build Sequence Analysis](#phase-2-build-sequence-analysis)
3. [Phase 3: Creating Multiple Approaches](#phase-3-creating-multiple-approaches)
4. [Phase 4: Choosing the Right Approach](#phase-4-choosing-the-right-approach)
5. [Phase 5: Full-Stack-First Deep Design](#phase-5-full-stack-first-deep-design)
6. [Phase 6: QA and Audit](#phase-6-qa-and-audit)
7. [Phase 7: Document Generation (M1-M18)](#phase-7-document-generation)
8. [Phase 8: LLM-Agnostic Architecture](#phase-8-llm-agnostic-architecture)
9. [Phase 9: Senior Review Integration (v27mar)](#phase-9-senior-review-integration)
10. [Phase 10: Research — What's Still Missing](#phase-10-research-whats-still-missing)
11. [Phase 11: Audit and De-duplication](#phase-11-audit-and-de-duplication)
12. [Phase 12: 24-Doc Stack Finalization](#phase-12-24-doc-stack-finalization)
13. [Phase 13: Renumbering (number = build order)](#phase-13-renumbering)
14. [Phase 14: Platform Development](#phase-14-platform-development)
15. [Phase 15: Agent Development (G1-G5, D0-D15)](#phase-15-agent-development)
16. [Phase 16: Bug Fixes and Quality Gates](#phase-16-bug-fixes-and-quality-gates)
17. [Key Decisions Log](#key-decisions-log)
18. [Lessons Learned](#lessons-learned)

---

## Phase 1: Understanding the Framework

### Prompt 1.1
> "In requirement folder there is MD file please analyse it properly"

**What happened:** Claude read `Requirement/MASTER-BUILD-SPEC.md` — the master specification defining 48 agents across 7 SDLC phases.

### Prompt 1.2
> "Now analyse Base_prompts"

**What happened:** Claude explored the Base_prompts folder containing the original 12 prompt templates with a build sequence file.

### Prompt 1.3
> "There is one Correct Build Sequence, can you analyse it and tell me is it right"

**What happened:** Claude found 2 issues in the dependency order — ARCH needed inputs that didn't exist yet, and API-CONTRACTS had a circular dependency with DESIGN-SPEC. The build sequence was 83% correct.

---

## Phase 2: Build Sequence Analysis

### Prompt 2.1
> "Now edit sequence number in Base_prompts and Correct Build Sequence"

**What happened:** All 12 prompt files were renumbered to match the correct build order. Files renamed from old numbering (00-ROADMAP, 01-CLAUDE, 02-PRD...) to corrected order.

---

## Phase 3: Creating Multiple Approaches

### Prompt 3.1
> "Create two folders API first and Design first and create same docs with proper sequence"

**What happened:** Created `Base_prompts/API-First/` and `Base_prompts/Design-First/` with 12 prompt templates each, plus build sequences and WHY-THIS-SEQUENCE explainer docs.

### Prompt 3.2
> "Create one more doc in each folder why this sequence, as if any layman starts work he should know why"

**What happened:** Created detailed WHY-THIS-SEQUENCE.md files explaining the reasoning in simple language — cooking analogies, dependency graphs, FAQ sections.

### Prompt 3.3
> "Now after reading MASTER-BUILD-SPEC which method should I go with, Design first or API first"

**What happened:** Claude recommended **API-First** because the platform is a backend-heavy control plane with 48 agents, multiple consumers (MCP, REST, CLI, webhooks), and the dashboard is secondary.

### Prompt 3.4
> "What is MCP first and will it change our sequence?"

**What happened:** Explained MCP (Model Context Protocol) — Anthropic's standard for AI tool interfaces. Created `Base_prompts/MCP-First/` with 13 documents (one more than API/Design-First) including the new `06-MCP-TOOL-SPEC.md`.

### Prompt 3.5
> "Can we combine design and MCP together and create something"

**What happened:** Created `Base_prompts/Full-Stack-First/` — the hybrid approach with 14 documents. Key innovation: INTERACTION-MAP (Doc 06) coordinates MCP tools and dashboard screens in parallel.

---

## Phase 4: Choosing the Right Approach

### Decision
The team chose **Full-Stack-First** because the platform serves BOTH AI clients (via MCP) AND human operators (via dashboard) equally.

---

## Phase 5: Full-Stack-First Deep Design

### Prompt 5.1
> "Create a QA agent and analyse Full-Stack-First and see if there are any issues"

**What happened:** QA audit found 14 issues across 10 categories. Fixed: dependency table gaps, added JSON schema examples, quality rubric, real-time update registry, document versioning policy, interaction ID guidelines, naming conflict resolution, error recovery strategy. Added 2 NEW documents: AGENT-HANDOFF-PROTOCOL and AGENT-INTERACTION-DIAGRAM.

---

## Phase 6: QA and Audit

The QA phase produced the 14+2 document stack (16 total). Every document cross-references others via I-NNN interaction IDs, Q-NNN quality requirements, and F-NNN feature IDs.

---

## Phase 7: Document Generation (M1-M18)

### Prompt 7.1
> "Now if I want to start with development how should I plan... I don't want to build it all at once, I want to go part by part so that after development I can test it and say hey this is right you can go for next agents"

**What happened:** Created a detailed execution plan with 25 milestones (M1-M25). Each milestone generates one document, tests it, gets approval, then proceeds.

### Prompts 7.2 through 7.18
> "Start M2" ... "Start M3" ... "Start M4" ... etc.

**What happened:** Generated all 16 documents one by one:
- M2: 00-ROADMAP (project context, phases, milestones, risk register)
- M3: 01-PRD (personas, journeys, capabilities, metrics)
- M4: 02-ARCH (C4 diagrams, shared service layer, tech stack)
- M5: 03-CLAUDE (coding rules, repo structure, patterns)
- M6: 04-QUALITY (66 NFRs across 10 categories)
- M7: 05-FEATURE-CATALOG (56 features, 10 epics)
- M8: 06-INTERACTION-MAP (34 interactions, 22 data shapes)
- M9+M10: 07-MCP-TOOL-SPEC + 08-DESIGN-SPEC (PARALLEL — the Full-Stack-First signature)
- M11: 09-DATA-MODEL (10 tables, 21 indexes, RLS)
- M12-M14: 10-API-CONTRACTS, 11-BACKLOG, 12-ENFORCEMENT
- M15-M16: 13-TESTING, 14-AGENT-HANDOFF-PROTOCOL
- M17: 15-AGENT-INTERACTION-DIAGRAM
- M18: Cross-reference review

---

## Phase 8: LLM-Agnostic Architecture

### Prompt 8.1
> "I have one question, is my architecture LLM agnostic?"

**What happened:** Claude admitted the architecture was Claude-locked. Only `sdk/base_agent.py` directly imported Anthropic.

### Prompt 8.2
> "My org needs LLM agnostic so can't we start from scratch? Do not do anything just answer my question"

**What happened:** Claude explained that 90% of the codebase was already LLM-agnostic (services, MCP, REST, dashboard never touch the LLM). Only the SDK layer (4-5 files) needed the provider abstraction.

### Prompt 8.3
> "Make it LLM agnostic, also update all required documents out of 16 as well"

**What happened:** Created `sdk/llm/` with:
- `provider.py` — Abstract LLMProvider interface
- `anthropic_provider.py` — Claude models
- `openai_provider.py` — GPT models
- `ollama_provider.py` — Local models (zero cost)
- `factory.py` — `create_provider("anthropic"|"openai"|"ollama")`

Updated BaseAgent to use LLMProvider. Updated all 16 Generated-Docs. Manifests now use `tier: fast|balanced|powerful` instead of hardcoded model IDs.

---

## Phase 9: Senior Review Integration (v27mar)

### Prompt 9.1
> "My senior colleague gave some repos... they came with new ideas... can you analyse below folder and tell me what's new and what we already have: ai-SDLC-document-stack_v27mar2026a-main"

**What happened:** Analysis found 6 brand new documents, 3 upgrades, 13 JSON schemas, corrected build sequence, and discovery questionnaire template. Senior's v27mar was enterprise-grade.

---

## Phase 10: Research — What's Still Missing

### Prompt 10.1
> "I want to be one step ahead of my seniors so do a strong research what else is required"

**What happened:** Three parallel research agents found:
- 15 enterprise SDLC gaps (compliance, observability, SLA/SLO, runbooks, SBOM, etc.)
- 13 AI-native gaps (prompt registry, LLM eval, guardrails, agent memory, model routing, etc.)
- Comparison with v27mar reference

---

## Phase 11: Audit and De-duplication

### Prompt 11.1
> "Whatever you did please audit it one more time, check are you creating some double work, are we missing anything, anything more needed, are we doing a lot creating confusion and winding LLM credits"

**What happened:** Honest audit cut proposed 50 documents down to 24. Killed 26 documents that were:
- Already covered as sections in existing docs (9)
- ITIL bureaucracy not needed for app dev (2)
- Runtime artifacts, not pipeline docs (3)
- Merged AI-native docs into ARCH sections (4)
- Premature/future scope (8)

**Final result: 24 documents. Zero duplication. Every doc earns its place.**

---

## Phase 12: 24-Doc Stack Finalization

### Prompt 12.1
> "Now you need to update this project — first update Base_prompts docs, then update Generated-Docs, then update complete project"

**What happened:**
- Added 8 new prompt templates (16-BRD through 23-COMPLIANCE-MATRIX)
- Upgraded 5 existing prompts (ARCH, QUALITY, FEATURE-CATALOG, ENFORCEMENT, TESTING)
- Generated 8 new documents + upgraded 5 existing
- Updated CLAUDE.md, build sequence, all cross-references

---

## Phase 13: Renumbering (number = build order)

### Prompt 13.1
> "I feel like there is issue with sequence, how BRD can be at 16 and user stories at 18, please analyse sequence properly"

**What happened:** Confirmed the numbering was wrong — BRD was numbered 16 but built first, CLAUDE was numbered 03 but built 14th. The rule should be: **document number = build order**.

### Prompt 13.2
> "Please resequence and make all necessary updates in complete project"

**What happened:** Renamed all 48 files (24 Base_prompts + 24 Generated-Docs) using temp prefix to avoid collisions. Updated all internal cross-references. Now Doc 00 (BRD) is built first, Doc 21 (COMPLIANCE-MATRIX) is built last.

---

## Phase 14: Platform Development

### Prompt 14.1
> "Now you are ready start with the development as per plan"

**What happened:** Built the complete platform infrastructure:
- Phase 0: Project scaffold (pyproject.toml, directory structure, .gitignore)
- Phase 1: Database (9 migrations, RLS policies, migration runner)
- Phase 2: 8 shared services (149 tests)
- Phase 3: 3 MCP servers (35 tools, 59 tests)
- Phase 4: REST API (34 endpoints, middleware)
- Phase 5: Dashboard (5 Streamlit pages, components)

---

## Phase 15: Agent Development (G1-G5, D0-D15)

### Prompt 15.1
> "I will give API key, you start with G1"

**What happened:** Built and live-tested each agent one by one, getting approval before proceeding:

**GOVERN Phase (G1-G5):**
- G1-cost-tracker: $0.003/call — cost reporting
- G2-audit-trail-validator: $0.010/call — audit completeness
- G3-agent-lifecycle-manager: $0.005/call — versioning, maturity
- G4-team-orchestrator: $0.022/call — pipeline brain (24-step)
- G5-audit-reporter: $0.008/call — summary reports

**DESIGN Phase (D0-D15):**
- D0-brd-generator through D15-enforcement-scaffolder
- Each tested live with real API calls
- FleetOps Dashboard used as test scenario throughout

### Key pattern for each agent:
1. Create `agents/{phase}/{agent-id}/manifest.yaml` (9 subsystems, tier-based model)
2. Create `agents/{phase}/{agent-id}/prompt.md` (role, input, output sections, constraints)
3. Create `tests/run_dN_test.py` (live test with realistic input data)
4. Run test, verify output quality
5. Commit with detailed message
6. Get approval before next agent

---

## Phase 16: Bug Fixes and Quality Gates

### Prompt 16.1 (First audit)
> "My agent found issues in current project please analyse are these the issues"

**What happened:** 26 reported issues. Claude verified each: 4 real bugs, 22 false positives. Fixed: route-service method mismatches, ManifestLoader missing design/ path, no schema validation.

### Prompt 16.2 (Second audit)
> "My agent found some issues... why my agent said issue"

**What happened:** 7 confirmed bugs. Fixed: pytest-aiohttp missing, G1 api_key param, dry-run crash, stale _estimate_cost, exception type mismatch, fixture data, stub test files.

### Prompt 16.3 (The accountability moment)
> "This is very bad... when I am coming and saying you there are issues my agent found it then you are fixing them, how you was saying all test are pass if there were issues and errors"

**What happened:** Claude admitted the mistake — was testing LLM output quality, NOT running actual pytest. Custom `run_dN_test.py` scripts tested agent output but never ran `pytest tests/`.

### Prompt 16.4
> "See create any agent or do something to make sure we are right after development I should not get excuse from you"

**What happened:** Created `tests/validate_all.py` — a 9-check mandatory validation gate:
1. pytest on tests/ AND agents/**/tests/
2. 25 module imports
3. 21 agent manifests
4. 21 agent prompts
5. BaseAgent dry-run
6. Stale reference scan (107 .py files)
7. Route-service method parity
8. ManifestLoader agent discovery
9. 24 Generated-Docs completeness

**New rule: This must pass (exit code 0) after EVERY change. No exceptions.**

### Prompt 16.5
> "One remaining issue... G1 test still fails... from agents.govern.G1_cost_tracker.agent import G1CostTracker ModuleNotFoundError"

**What happened:** Line 22 tried importing from hyphenated directory (G1-cost-tracker) using underscore (G1_cost_tracker). Python can't import hyphenated dirs. Removed the dead import.

---

## Key Decisions Log

| # | Decision | Why | When |
|---|----------|-----|------|
| 1 | Full-Stack-First approach | Platform serves BOTH AI clients AND human operators | Phase 3 |
| 2 | 24-document stack (not 12, not 50) | 12 was insufficient, 50 was bloated. 24 covers enterprise + AI-native | Phase 11 |
| 3 | Document number = build order | BRD is 00 (built first), COMPLIANCE is 21 (built last) | Phase 13 |
| 4 | LLM-agnostic from day one | Org requirement — support Anthropic, OpenAI, Ollama | Phase 8 |
| 5 | tier: fast/balanced/powerful | Not hardcoded model IDs — providers resolve tiers to models | Phase 8 |
| 6 | Shared service layer (THE KEY PATTERN) | MCP handlers and REST handlers call same services. No logic duplication. | Phase 5 |
| 7 | INTERACTION-MAP (THE KEY DOCUMENT) | Prevents MCP/Dashboard divergence during parallel sprint | Phase 5 |
| 8 | GUARDRAILS-SPEC + COMPLIANCE-MATRIX | AI-native docs that no traditional SDLC has — our moat | Phase 10 |
| 9 | validate_all.py mandatory gate | After trust was broken by false "all pass" claims | Phase 16 |
| 10 | One agent at a time with approval | User controls pace — no bulk building without review | Phase 15 |

---

## Lessons Learned

### 1. "PASS" means pytest, not manual inspection
Never claim tests pass based on file reads or grep searches. Run `pytest`. Run `validate_all.py`. Show the output.

### 2. Test ALL directories, not just tests/
Agent tests live under `agents/**/tests/`. The pytest default path (`tests/`) misses them. Always run both.

### 3. Refactoring breaks downstream tests
When BaseAgent was refactored for LLM-agnostic, the G1 test file still used old API (`api_key` param, `_estimate_cost` method). Every refactor needs a full test sweep.

### 4. Document number should match build order
Random numbering (BRD at 16, CLAUDE at 03) causes confusion. Sequential numbering where number = step eliminates ambiguity.

### 5. 50 documents is bloat, 12 is insufficient
The sweet spot is 24 — every doc earns its place. Merge sections into existing docs rather than creating new ones. Ask: "Does this need its own document, or is it a section in an existing one?"

### 6. Your agent is your QA partner
The user's independent audit agent caught bugs that Claude missed. Having a second agent audit the first agent's work is the correct pattern for quality.

### 7. Seniors' experience is gold
The v27mar reference from senior colleagues added 6 critical documents (BRD, SECURITY, USER-STORIES, INFRA, MIGRATION, FAULT-TOLERANCE) that made the framework enterprise-grade. Always integrate domain expertise.

---

## How to Use This Playbook

1. **New team member onboarding:** Read Phases 1-5 to understand WHY the framework exists and HOW it was designed.

2. **Adding a new agent:** Follow the pattern from Phase 15 — manifest + prompt + test + validate_all.py.

3. **Adding a new document type:** Follow Phase 12 — add prompt template, generate doc, update build sequence, renumber if needed.

4. **Debugging test failures:** Run `PYTHONPATH=. python tests/validate_all.py` — it checks everything in 9 steps.

5. **Understanding architectural decisions:** See the Key Decisions Log above.

6. **Reproducing the project:** Follow the prompts in order from Phase 1 through Phase 16.
