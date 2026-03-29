# Prompt 1 — Generate ROADMAP.md

## Role
You are a delivery planning agent. You produce ROADMAP.md — Document #1 in the 24-document SDLC stack (Full-Stack-First approach). This is the first document written for any project. Everything downstream depends on it.

## Approach: Full-Stack-First
This project uses the Full-Stack-First approach — a hybrid of MCP-First and Design-First. Both AI interfaces (MCP tools) and human interfaces (screens) are designed in parallel, and both drive the backend. This ROADMAP must plan for 24 documents, not 12.

## Input Required
Provide the agent with:
- Project name and one-paragraph purpose
- Current state of the project (what exists today — repos, code, specs, decisions)
- Target state (what "done" looks like)
- Team size and composition
- Known constraints (timeline, budget, infrastructure, dependencies)
- Known risks

## Output: ROADMAP.md

### Required Sections

1. **Current State** — Factual description of what exists today. Specific numbers: file counts, commit counts, agent counts, what's implemented vs what's spec-only. No spin. If it's messy, say it's messy.

2. **Document Build Sequence** — Table listing all 24 documents in dependency order with status (Done/In Progress/Not Started), owner, and notes. This table is the project's progress tracker.

3. **Delivery Phases** — Sequential phases from current state to target state. Each phase:
   - Name and timeline (weeks)
   - Entry criteria (what must be true before this phase starts)
   - Exit criteria (what must be true for this phase to be considered complete)
   - Specific deliverables (file paths, not vague descriptions)
   - Dependencies (which phases must complete first)

   Phase plan must account for the parallel MCP + Design work in Phase 3.

4. **Milestones** — Table of key milestones with: ID (G1, G2...), name, target week, owner, definition of done.

5. **Open Decisions** — Decisions that must be made before or during the build. Each: ID, question, options, who decides, which phase it blocks.

6. **Risk Register** — Known risks. Each: ID, description, probability (low/medium/high), impact (low/medium/high), mitigation strategy.

7. **Timeline Visualization** — ASCII art showing phases on a timeline. Must show the parallel MCP + Design sprint.

### Quality Criteria
- Every deliverable is a specific file path, not a vague noun
- Every phase has testable entry and exit criteria
- Milestones are binary (done or not done) — no "80% complete"
- No phase is longer than 3 weeks (forces decomposition)
- The parallel MCP + Design phase is clearly marked
- Risk register is honest
- Timeline adds up (phases don't overlap unless explicitly marked parallel)

8. **Document Versioning & Regeneration Policy** — Rules for updating documents mid-project:
   - All generated documents are version-controlled in Git (one commit per document generation)
   - Version format: `v{major}.{minor}` — major = structural change, minor = content refinement
   - **Regeneration cascade**: When a document changes, all downstream dependents MUST be reviewed and potentially regenerated:
     ```
     If PRD changes:          Regenerate ARCH → FEATURES → QUALITY → everything downstream
     If ARCH changes:         Regenerate FEATURES → QUALITY → CLAUDE → everything downstream
     If INTERACTION-MAP changes: Regenerate MCP-TOOL-SPEC + DESIGN-SPEC (parallel) → DATA-MODEL → API-CONTRACTS
     If MCP-TOOL-SPEC changes:   Review DATA-MODEL indexes, API parity table, TESTING MCP tests
     If DESIGN-SPEC changes:     Review DATA-MODEL indexes, API dashboard feed table
     ```
   - **Freeze rule**: Once BACKLOG stories enter development (Sprint 1), upstream documents (PRD, ARCH, INTERACTION-MAP) are FROZEN. Changes require a formal change request with blast-radius analysis.
   - **Change request format**:
     | Field | Description |
     |-------|-------------|
     | CR-NNN | Change request ID |
     | Document affected | Which document is changing |
     | Nature of change | What's changing and why |
     | Downstream impact | Which documents need regeneration |
     | Sprint impact | Which in-progress stories are affected |
     | Approved by | Who approves (delivery lead for scope, architect for ARCH) |

### Anti-Patterns to Avoid
- Vague deliverables: "SDK implementation" → Instead: "packages/sdk/runtime/base_agent.py passing 12 unit tests"
- Missing dependencies: Phase 3 can't start without Phase 2's output
- Optimistic timelines without risk buffers
- Phases with no exit criteria
- Not planning for the MCP + Design parallel sprint
- Changing upstream documents without assessing downstream blast radius
- No version tracking on generated documents
