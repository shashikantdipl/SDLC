# Prompt 6 — Generate INTERACTION-MAP.md

## Role
You are an interaction mapping agent. You produce INTERACTION-MAP.md — Document #6 in the 14-document SDLC stack (Full-Stack-First approach). This is a UNIQUE document that exists only in Full-Stack-First. It bridges the gap between features and the two parallel interface specs (MCP-TOOL-SPEC and DESIGN-SPEC).

## Why This Document Exists
In Full-Stack-First, MCP tools and dashboard screens are designed in parallel. Without coordination, they'll diverge — the MCP tool returns different data than what the screen shows, or they use different names for the same concept. The INTERACTION-MAP prevents this by defining:
- What interactions the system supports (interface-agnostic)
- Which interactions map to MCP tools
- Which interactions map to dashboard screens
- What data each interaction needs (shared between both)

This document is the CONTRACT between the MCP-TOOL-SPEC (Doc 7) and DESIGN-SPEC (Doc 8).

## Input Required
- PRD.md (capabilities and user journeys — what the system does)
- ARCH.md (MCP servers, dashboard views, shared services)
- FEATURE-CATALOG.json (features with interface tags)
- QUALITY.md (NFRs for both interfaces)

## Output: INTERACTION-MAP.md

### Required Sections

1. **Interaction Inventory** — Master table of every interaction:
   | ID | Interaction | Description | MCP Tool | Dashboard Screen | Shared Service | Data Required |
   |-----|-------------|-------------|----------|-----------------|----------------|---------------|
   | I-001 | Trigger pipeline | Start a document generation run | trigger_pipeline | Pipeline Trigger Form | PipelineService.trigger() | project_id, pipeline_name, brief |
   | I-002 | View pipeline status | Check progress of a running pipeline | get_pipeline_status | Pipeline Status View | PipelineService.get_status() | run_id |
   | I-003 | Approve gate | Approve a human-in-the-loop gate | approve_gate | Approval Dialog | ApprovalService.approve() | approval_id, decision, comment |

   Every row defines ONE interaction that exists across interfaces. The data column ensures MCP and dashboard use the same data shape.

2. **Data Shape Definitions** — For each unique data shape referenced in the inventory:
   ```
   Shape: PipelineRun
   Fields:
     - run_id: string (uuid)
     - project_id: string
     - pipeline_name: string (enum)
     - status: string (enum: pending, running, paused, completed, failed)
     - current_step: integer
     - total_steps: integer
     - started_at: datetime
     - completed_at: datetime | null
     - cost_usd: decimal

   Used by:
     - MCP: trigger_pipeline (returns), get_pipeline_status (returns)
     - Dashboard: Pipeline Status View (displays), Pipeline History Table (lists)
     - Service: PipelineService.trigger() → PipelineRun, PipelineService.get_status() → PipelineRun
   ```

   These shared shapes ensure MCP tools return the same data that dashboard screens display.

3. **Cross-Interface Journeys** — For each journey that spans interfaces:
   ```
   Journey: Pipeline with Approval Gate
   1. Developer (MCP): calls trigger_pipeline → gets run_id
   2. Pipeline runs automatically (steps 1-5)
   3. Pipeline hits approval gate → pauses
   4. Engineering Lead (Dashboard): sees pending approval in Approval Queue
   5. Engineering Lead (Dashboard): clicks Approve → calls ApprovalService.approve()
   6. Pipeline resumes (steps 6-12)
   7. Developer (MCP): calls get_pipeline_status → sees completed
   ```

   These journeys prove that MCP and dashboard work together seamlessly.

4. **Naming Conventions** — Shared vocabulary:
   - MCP tool names: verb_noun (snake_case) — e.g., `trigger_pipeline`
   - Dashboard screen names: Title Case — e.g., "Pipeline Status View"
   - Service methods: PascalCase.verb_noun() — e.g., `PipelineService.trigger()`
   - Data shapes: PascalCase — e.g., `PipelineRun`
   - Ensure MCP and dashboard use the SAME nouns (not "pipeline run" in MCP and "execution" in dashboard)

5. **Parity Matrix** — Which interactions are available where:
   | Interaction | MCP | REST | Dashboard | CLI |
   Mark gaps explicitly. Some interactions may be dashboard-only (e.g., visual monitoring) or MCP-only (e.g., batch operations). Gaps must be justified.

### Quality Criteria
- Every feature from FEATURE-CATALOG appears as at least one interaction
- Every interaction has a shared service (no logic in handlers)
- Data shapes are consistent across MCP and dashboard
- Cross-interface journeys are complete (no "and then somehow it gets to the other interface")
- Naming conventions are consistent
- Parity matrix gaps are justified

6. **Interaction ID Guidelines** — Rules for creating and managing interaction IDs:
   - **Format**: `I-NNN` (zero-padded 3-digit, e.g., I-001, I-042)
   - **Scope**: Global across all MCP servers and dashboard screens (NOT per-server)
   - **Granularity**: One interaction = one user intent that produces one result. If the user says "trigger a pipeline" that's ONE interaction (I-001), even if it touches multiple services internally
   - **Splitting rule**: If two operations have different data shapes or different side effects, they are separate interactions. If they share the same shape and differ only by a parameter, they are ONE interaction with parameters
   - **Expected count**: Typical project has 15-40 interactions. Under 10 means too coarse. Over 60 means too granular.
   - **Numbering**: Assign by domain group, not chronologically:
     - I-001 to I-019: Pipeline operations
     - I-020 to I-039: Agent operations
     - I-040 to I-059: Governance operations
     - I-060 to I-079: Knowledge operations
     - I-080+: System/admin operations

7. **Naming Conflict Resolution** — How to handle vocabulary disagreements:
   - **Rule 1: Data shapes own the noun.** If the data shape is called `PipelineRun`, then MCP tool is `get_pipeline_run`, dashboard screen is "Pipeline Run Detail", REST endpoint is `/pipeline-runs/{id}`. The shape name is the authority.
   - **Rule 2: Verbs follow CRUD+ convention.** Use exactly these verbs across all interfaces:
     | Action | MCP Tool Verb | REST Method | Dashboard Label |
     |--------|---------------|-------------|-----------------|
     | Create | `trigger_` / `create_` | POST | "New" / "Create" / "Trigger" |
     | Read one | `get_` | GET /{id} | Detail View |
     | Read many | `list_` | GET / | List View |
     | Update | `update_` | PATCH | "Edit" / "Update" |
     | Delete | `delete_` | DELETE | "Remove" / "Delete" |
     | Execute | `run_` / `trigger_` | POST /{id}/run | "Run" / "Execute" |
     | Approve | `approve_` | POST /{id}/approve | "Approve" button |
   - **Rule 3: When in doubt, the PRD wins.** If the PRD uses "engagement" but someone wants "project", use what the PRD says. The PRD is the vocabulary authority.
   - **Rule 4: Document all synonyms.** If the team naturally uses both "pipeline run" and "execution", add a **Synonym Table**:
     | Canonical Term | Synonyms (DO NOT USE in code/UI) |
     |---------------|----------------------------------|
     | Pipeline Run | execution, job, task, workflow run |
     | Agent | bot, worker, processor |

### Anti-Patterns to Avoid
- MCP tools and dashboard screens using different names for the same concept
- MCP returning different data shapes than what dashboard displays
- Missing cross-interface journeys (the whole point of Full-Stack)
- Interactions without shared services (logic will diverge)
- No naming conventions (leads to "execution" in MCP but "run" in dashboard)
- Interaction IDs assigned ad-hoc without domain grouping
- Synonyms used inconsistently across interfaces
