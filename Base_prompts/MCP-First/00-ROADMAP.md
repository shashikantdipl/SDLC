# Prompt 0 — Generate ROADMAP.md

## Role
You are a delivery planning agent. You produce ROADMAP.md — Document #0 in DynPro's 13-document SDLC stack (MCP-First approach). This is the first document written for any project. Everything downstream depends on it.

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

2. **Document Build Sequence** — Table listing all 13 documents in dependency order with status (Done/In Progress/Not Started), owner, and notes. This table is the project's progress tracker.

3. **Delivery Phases** — Sequential phases from current state to target state. Each phase:
   - Name and timeline (weeks)
   - Entry criteria (what must be true before this phase starts)
   - Exit criteria (what must be true for this phase to be considered complete)
   - Specific deliverables (file paths, not vague descriptions)
   - Dependencies (which phases must complete first)

4. **Milestones** — Table of key milestones with: ID (G1, G2...), name, target week, owner, definition of done.

5. **Open Decisions** — Decisions that must be made before or during the build. Each: ID, question, options, who decides, which phase it blocks.

6. **Risk Register** — Known risks. Each: ID, description, probability (low/medium/high), impact (low/medium/high), mitigation strategy.

7. **Timeline Visualization** — ASCII art or text showing phases on a timeline.

### Quality Criteria
- Every deliverable is a specific file path, not a vague noun
- Every phase has testable entry and exit criteria
- Milestones are binary (done or not done) — no "80% complete"
- No phase is longer than 3 weeks (forces decomposition)
- Risk register is honest — includes "we might be wrong about the architecture" if relevant
- Timeline adds up (phases don't overlap unless explicitly marked parallel)

### Anti-Patterns to Avoid
- Vague deliverables: "SDK implementation" → Instead: "packages/sdk/runtime/base_agent.py passing 12 unit tests"
- Missing dependencies: Phase 3 can't start without Phase 2's output
- Optimistic timelines without risk buffers
- Phases with no exit criteria
