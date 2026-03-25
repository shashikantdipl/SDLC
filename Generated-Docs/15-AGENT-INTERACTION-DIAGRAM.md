# AGENT-INTERACTION-DIAGRAM — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 15 of 14+2 | Status: Draft

---

## Purpose

This document is the visual companion to AGENT-HANDOFF-PROTOCOL (Doc 14). It renders every agent-to-agent flow, session key dependency, parallel execution group, data traceability chain, cross-interface journey, error propagation path, and cost breakdown as ASCII diagrams and structured tables. Where Doc 14 defines the rules, this document shows the topology.

### Agents Referenced

| Agent ID | Document Produced | Full-Stack-First Doc # |
|----------|-------------------|------------------------|
| D0 | ROADMAP | 00 |
| D1 | PRD | 01 |
| D2 | ARCH | 02 |
| D3 | CLAUDE | 03 |
| D4 | QUALITY | 04 |
| D5 | FEATURE-CATALOG | 05 |
| D6 | INTERACTION-MAP | 06 |
| D7 | MCP-TOOL-SPEC | 07 |
| D8 | DESIGN-SPEC | 08 |
| D9 | DATA-MODEL | 09 |
| D10 | API-CONTRACTS | 10 |
| D11 | BACKLOG | 11 |
| D12 | ENFORCEMENT | 12 |
| D13 | TESTING | 13 |

---

## 1. Complete Pipeline Flow

The diagram below shows all 14 document-generation agents (D0-D13) connected by session keys. Parallel groups are enclosed in dashed boxes. Quality gates (QG) validate output before the next group can read it.

```
                              [raw_spec]
                                  |
                                  v
          +-----------------------------------------------+
          |              GROUP 1 (parallel)                |
          |                                                |
          |    +--------+                +--------+        |
          |    |   D0   |                |   D1   |        |
          |    |ROADMAP |                |  PRD   |        |
          |    +---+----+                +---+----+        |
          |        |                         |             |
          +-----------------------------------------------+
                   |                         |
            [roadmap_doc]              [prd_doc]
                   |                         |
          =========|=======QG-1==============|=============
                   |                         |
                   v                         v
          +-----------------------------------------------+
          |              GROUP 2 (sequential)              |
          |                                                |
          |                  +--------+                    |
          |                  |   D2   |                    |
          |                  |  ARCH  |                    |
          |                  +---+----+                    |
          |                      |                         |
          +-----------------------------------------------+
                                 |
                           [arch_doc]
                                 |
          =======================|=======QG-2==============
                                 |
                   +-------------+-------------+
                   |             |             |
                   v             v             v
          +-----------------------------------------------+
          |              GROUP 3 (parallel)                |
          |                                                |
          |  +--------+   +--------+   +--------+         |
          |  |   D3   |   |   D4   |   |   D5   |         |
          |  | CLAUDE |   |QUALITY |   |FEATURE |         |
          |  |        |   |        |   |CATALOG |         |
          |  +---+----+   +---+----+   +---+----+         |
          |      |            |            |               |
          +-----------------------------------------------+
                 |            |            |
          [claude_doc]  [quality_doc] [feature_catalog]
                 |            |            |
          =======|============|============|=====QG-3======
                 |            |            |
                 +------+-----+-----+------+
                        |           |
                        v           v
          +-----------------------------------------------+
          |              GROUP 4 (sequential)              |
          |                                                |
          |                  +--------+                    |
          |                  |   D6   |                    |
          |                  |INTERACT|                    |
          |                  |  MAP   |                    |
          |                  +---+----+                    |
          |                      |                         |
          +-----------------------------------------------+
                                 |
                         [interaction_map]
                                 |
          =======================|=======QG-4==============
                                 |
                        +--------+--------+
                        |                 |
                        v                 v
          +-----------------------------------------------+
          |       GROUP 5 — THE PARALLEL SPRINT            |
          |                                                |
          |        +--------+       +--------+             |
          |        |   D7   |       |   D8   |             |
          |        |MCP-TOOL|       |DESIGN  |             |
          |        | SPEC   |       | SPEC   |             |
          |        +---+----+       +---+----+             |
          |            |                |                   |
          +-----------------------------------------------+
                       |                |
                [mcp_tool_spec]   [design_spec]
                       |                |
          =============|================|======QG-5========
                       |                |
                       +-------+--------+
                               |
                               v
          +-----------------------------------------------+
          |              GROUP 6 (sequential)              |
          |                                                |
          |                  +--------+                    |
          |                  |   D9   |                    |
          |                  |  DATA  |                    |
          |                  | MODEL  |                    |
          |                  +---+----+                    |
          |                      |                         |
          +-----------------------------------------------+
                                 |
                           [data_model]
                                 |
          =======================|=======QG-6==============
                                 |
                                 v
          +-----------------------------------------------+
          |              GROUP 7 (sequential)              |
          |                                                |
          |                  +--------+                    |
          |                  |  D10   |                    |
          |                  |  API   |                    |
          |                  |CONTRAC |                    |
          |                  +---+----+                    |
          |                      |                         |
          +-----------------------------------------------+
                                 |
                          [api_contracts]
                                 |
          =======================|=======QG-7==============
                                 |
                   +-------------+-------------+
                   |             |             |
                   v             v             v
          +-----------------------------------------------+
          |              GROUP 8 (parallel)                |
          |                                                |
          |  +--------+   +--------+   +--------+         |
          |  |  D11   |   |  D12   |   |  D13   |         |
          |  |BACKLOG |   |ENFORCE |   |TESTING |         |
          |  |        |   | MENT   |   |        |         |
          |  +---+----+   +---+----+   +---+----+         |
          |      |            |            |               |
          +-----------------------------------------------+
                 |            |            |
            [backlog]  [enforcement_rules] [test_strategy]
                 |            |            |
          =======|============|============|=====QG-8======
                 |            |            |
                 v            v            v
          +-----------------------------------------------+
          |                                                |
          |           *** PIPELINE COMPLETE ***             |
          |                                                |
          |    14 documents generated. Session sealed.     |
          |    Final cost recorded. Audit trail closed.    |
          |    Provider: LLM_PROVIDER (default: anthropic) |
          |                                                |
          +-----------------------------------------------+
```

### Reading the Diagram

- **Boxes** (`+----+`) are agent execution units. Each agent reads its input session keys and writes exactly one output session key.
- **Dashed Groups** are parallel execution boundaries. Agents within a group run concurrently and have no dependencies on each other.
- **`═══QG═══`** lines are quality gates. The orchestrator validates the output of every agent before making its session key available to downstream consumers.
- **`[session_key]`** labels on arrows identify the session store key that carries the output document.
- **`[raw_spec]`** is the human-provided input that enters at the top and is available to D0 and D1.

---

## 2. Session Key Flow Matrix

```
Session Key         Writer    Readers                                     Reader Count
──────────────────  ────────  ──────────────────────────────────────────   ────────────
raw_spec            [human]   D0, D1                                      2
roadmap_doc         D0        D3                                          1
prd_doc             D1        D2, D4, D5, D6, D8, D10, D11               7
arch_doc            D2        D3, D4, D5, D6, D7, D9, D10, D11, D12, D13 10
claude_doc          D3        D12, D13                                    2
quality_doc         D4        D6, D7, D8, D9, D11, D13                   6
feature_catalog     D5        D6, D7, D8, D9, D11                        5
interaction_map     D6        D7, D8, D9, D10, D11, D13                  6
mcp_tool_spec       D7        D9, D10, D11, D13                          4
design_spec         D8        D9, D10, D11, D13                          4
data_model          D9        D10, D13                                    2
api_contracts       D10       (terminal)                                  0
backlog             D11       (terminal)                                  0
enforcement_rules   D12       (terminal)                                  0
test_strategy       D13       (terminal)                                  0
```

### Key Observations

1. **Most-read key: `arch_doc` (10 readers).** The architecture document is the single most critical artifact in the pipeline. If D2 fails or produces low-quality output, 10 downstream agents are affected. This justifies the strictest quality gate (QG-2) and the highest retry budget for D2.

2. **High fan-out keys:** `prd_doc` (7 readers), `quality_doc` (6 readers), `interaction_map` (6 readers), `feature_catalog` (5 readers). These are "load-bearing" documents where quality issues cascade widely.

3. **Terminal keys:** `api_contracts`, `backlog`, `enforcement_rules`, `test_strategy` are leaf nodes with zero downstream consumers. They can fail and retry without blocking any other agent.

4. **Single-reader key:** `roadmap_doc` is read only by D3 (CLAUDE). It is the narrowest dependency in the pipeline.

5. **Fan-in pattern at D6:** The INTERACTION-MAP agent reads `prd_doc`, `arch_doc`, `quality_doc`, and `feature_catalog` -- four inputs. This makes D6 the highest fan-in node and the most likely bottleneck if any upstream agent is slow.

### Dependency Graph (Adjacency List)

```
D0  --> D3
D1  --> D2, D4, D5, D6, D8, D10, D11
D2  --> D3, D4, D5, D6, D7, D9, D10, D11, D12, D13
D3  --> D12, D13
D4  --> D6, D7, D8, D9, D11, D13
D5  --> D6, D7, D8, D9, D11
D6  --> D7, D8, D9, D10, D11, D13
D7  --> D9, D10, D11, D13
D8  --> D9, D10, D11, D13
D9  --> D10, D13
D10 --> (none)
D11 --> (none)
D12 --> (none)
D13 --> (none)
```

---

## 3. Parallel Execution Groups

### Group Definitions

| Group | Agents | Prerequisite Keys | Output Keys | Est. Time |
|-------|--------|--------------------|-------------|-----------|
| G1 | D0 ‖ D1 | `raw_spec` | `roadmap_doc`, `prd_doc` | ~2 min |
| G2 | D2 | `prd_doc` | `arch_doc` | ~3 min |
| G3 | D3 ‖ D4 ‖ D5 | `roadmap_doc`, `prd_doc`, `arch_doc` | `claude_doc`, `quality_doc`, `feature_catalog` | ~3 min |
| G4 | D6 | `prd_doc`, `arch_doc`, `quality_doc`, `feature_catalog` | `interaction_map` | ~4 min |
| G5 | D7 ‖ D8 | `interaction_map`, `quality_doc`, `feature_catalog`, `arch_doc`, `prd_doc` | `mcp_tool_spec`, `design_spec` | ~4 min |
| G6 | D9 | `mcp_tool_spec`, `design_spec`, `interaction_map`, `arch_doc`, `quality_doc`, `feature_catalog` | `data_model` | ~3 min |
| G7 | D10 | `data_model`, `mcp_tool_spec`, `design_spec`, `interaction_map`, `prd_doc`, `arch_doc` | `api_contracts` | ~3 min |
| G8 | D11 ‖ D12 ‖ D13 | All upstream keys | `backlog`, `enforcement_rules`, `test_strategy` | ~3 min |

### ASCII Timeline

```
Time (min)  0         5         10        15        20        25
            |---------|---------|---------|---------|---------|

Sequential: D0--D1--D2--D3--D4--D5--D6--D7--D8--D9--D10--D11--D12--D13
            |████████████████████████████████████████████████████████████|
            0                                                         ~40 min

Parallel:   [G1:D0||D1][G2:D2][G3:D3||D4||D5][G4:D6][G5:D7||D8][G6:D9][G7:D10][G8:D11||D12||D13]
            |██████████|██████|██████████████|████████|████████████|██████|██████|██████████████████|
            0    2     4   7  8      11     12   16  17    20     21  24 25              ~25 min


            Detailed Parallel Timeline:

            min 0          min 2      min 5      min 8      min 12     min 16     min 19     min 22   min 25
            |              |          |          |          |          |          |          |        |
            +--[G1]--------+          |          |          |          |          |          |        |
            | D0 (ROADMAP) |          |          |          |          |          |          |        |
            | D1 (PRD)     |          |          |          |          |          |          |        |
            +--------------+          |          |          |          |          |          |        |
                           +-[QG1]+   |          |          |          |          |          |        |
                           |      |   |          |          |          |          |          |        |
                           +--[G2]+---+          |          |          |          |          |        |
                              D2 (ARCH)          |          |          |          |          |        |
                                      |          |          |          |          |          |        |
                                      +--[QG2]+  |          |          |          |          |        |
                                      |       |  |          |          |          |          |        |
                                      +--[G3]-+--+          |          |          |          |        |
                                      | D3 (CLAUDE)         |          |          |          |        |
                                      | D4 (QUALITY)        |          |          |          |        |
                                      | D5 (FEATURE-CAT)    |          |          |          |        |
                                      +---------------------+          |          |          |        |
                                               |  +--[QG3]+            |          |          |        |
                                               |  |       |            |          |          |        |
                                               |  +--[G4]-+------------+          |          |        |
                                               |     D6 (INTERACTION-MAP)         |          |        |
                                               |                      |           |          |        |
                                               |                      +--[QG4]+   |          |        |
                                               |                      |       |   |          |        |
                                               |                      +--[G5]-+---+          |        |
                                               |                      | D7 (MCP-TOOL-SPEC)   |        |
                                               |                      | D8 (DESIGN-SPEC)     |        |
                                               |                      +----------------------+        |
                                               |                               |  +--[QG5]+          |
                                               |                               |  |       |          |
                                               |                               |  +--[G6]-+----------+
                                               |                               |     D9 (DATA-MODEL) |
                                               |                               |                     |
                                               |                               |          +--[QG6]+  |
                                               |                               |          |       |  |
                                               |                               |          +--[G7]-+--+
                                               |                               |             D10     |
                                               |                               |          (API-CONT) |
                                               |                               |                     |
                                               |                               |          +--[QG7]+  |
                                               |                               |          |       |  |
                                               |                               |          +--[G8]-+--+
                                               |                               |          | D11     ||
                                               |                               |          | D12     ||
                                               |                               |          | D13     ||
                                               |                               |          +---------+|
                                               |                               |                     |
                                               |                               |          +--[QG8]+  |
                                               |                               |          |COMPLETE| |
                                               +-------------------------------+----------+--------+-+
```

### Savings Summary

| Metric | Sequential | Parallel | Savings |
|--------|-----------|----------|---------|
| Total wall-clock time | ~40 min | ~25 min | **15 min (37%)** |
| Total agent compute | ~40 min | ~40 min | 0% (same work) |
| Quality gate overhead | ~14 gates x 10s | ~8 gates x 10s | ~60s saved |
| Parallelism ratio | 1.0x | 1.6x | -- |

**Critical path:** D1 -> D2 -> D4 -> D6 -> D7 -> D9 -> D10 -> D11 (8 sequential steps, ~25 min)

---

## 4. Data Shape Flow (Traceability)

This section traces the `PipelineRun` data shape from its origin in the PRD through every downstream document to final test coverage, demonstrating full-stack traceability.

### PipelineRun End-to-End Trace

```
 PRD (Doc 01)                    FEATURE-CATALOG (Doc 05)
 Capability C2:                  Feature F-001:
 "12-Document                    "Trigger Pipeline"
  Generation Pipeline"           F-002: "Get Pipeline Status"
        |                        F-003: "List Pipeline Runs"
        |                               |
        +---------------+---------------+
                        |
                        v
              INTERACTION-MAP (Doc 06)
              I-001: Trigger pipeline
              I-002: Get pipeline status
              I-003: List pipeline runs
              I-004: Resume pipeline
              I-005: Cancel pipeline
              Data Shape: PipelineRun {
                run_id, project_name, status,
                current_step, total_steps,
                steps[], cost_so_far,
                triggered_at, completed_at
              }
                        |
            +-----------+-----------+
            |                       |
            v                       v
  MCP-TOOL-SPEC (Doc 07)   DESIGN-SPEC (Doc 08)
  Tool: trigger_pipeline    Screen: Pipeline Runs
    returns PipelineRun       Table: PipelineRun[]
  Tool: get_pipeline_status   Card: PipelineRun detail
    returns PipelineRun       Progress bar: steps[]
  Tool: list_pipeline_runs    Status badge: status
    returns PipelineRun[]     Cost display: cost_so_far
            |                       |
            +-----------+-----------+
                        |
                        v
              DATA-MODEL (Doc 09)
              Table: pipeline_runs {
                id UUID PK,
                project_name VARCHAR(200),
                status pipeline_status ENUM,
                current_step INT,
                total_steps INT DEFAULT 14,
                cost_so_far NUMERIC(10,4),
                triggered_at TIMESTAMPTZ,
                completed_at TIMESTAMPTZ
              }
              Table: pipeline_steps {
                id UUID PK,
                run_id UUID FK -> pipeline_runs,
                step_index INT,
                agent_id VARCHAR(20),
                status step_status ENUM,
                started_at TIMESTAMPTZ,
                completed_at TIMESTAMPTZ,
                cost NUMERIC(10,4),
                error_message TEXT
              }
                        |
                        v
              API-CONTRACTS (Doc 10)
              POST /api/v1/pipelines
                Request:  { project_name, raw_spec }
                Response: PipelineRun (201)
              GET  /api/v1/pipelines
                Response: { items: PipelineRun[], total, page }
              GET  /api/v1/pipelines/{run_id}
                Response: PipelineRun (200)
              POST /api/v1/pipelines/{run_id}/resume
                Response: PipelineRun (200)
              POST /api/v1/pipelines/{run_id}/cancel
                Response: PipelineRun (200)
                        |
                        v
              BACKLOG (Doc 11)
              S-001: "As Marcus, I trigger a pipeline via MCP"
                AC: trigger_pipeline returns PipelineRun with status=running
              S-002: "As Anika, I view pipeline progress on Dashboard"
                AC: Pipeline Runs page renders PipelineRun.steps[]
              S-003: "As Priya, I resume a failed pipeline via MCP"
                AC: resume_pipeline returns PipelineRun with status=running
                        |
                        v
              TESTING (Doc 13)
              +-------------------------------------------+
              | Test Layer          | What is verified     |
              |---------------------|----------------------|
              | Unit test           | PipelineService      |
              |                     | .trigger() returns   |
              |                     | valid PipelineRun    |
              | MCP integration     | trigger_pipeline     |
              |                     | tool returns         |
              |                     | PipelineRun via MCP  |
              | REST integration    | POST /pipelines      |
              |                     | returns PipelineRun  |
              |                     | with 201             |
              | Parity test         | MCP PipelineRun ==   |
              |                     | REST PipelineRun     |
              |                     | field-by-field       |
              | Journey test        | MCP trigger -> Dash  |
              |                     | approval -> MCP      |
              |                     | status = completed   |
              +-------------------------------------------+
```

### Additional Data Shape Traces (Summary)

| Data Shape | Origin (PRD) | Features | Interactions | MCP Tool(s) | Dashboard Screen | DB Table | API Endpoints | Stories | Test Layers |
|-----------|-------------|----------|-------------|-------------|-----------------|----------|--------------|---------|------------|
| `PipelineRun` | C2 | F-001..F-007 | I-001..I-007 | trigger_pipeline, get_pipeline_status, list_pipeline_runs, resume_pipeline, cancel_pipeline | Pipeline Runs | pipeline_runs, pipeline_steps | POST/GET /pipelines | S-001..S-003 | 5 layers |
| `AgentSummary` | C1 | F-008..F-013 | I-020..I-027 | list_agents, get_agent | Fleet Health | agent_registry | GET /agents | S-010..S-012 | 4 layers |
| `CostReport` | C4 | F-014..F-017 | I-040..I-041 | get_cost_report, check_budget | Cost Monitor | cost_metrics | GET /costs | S-020..S-022 | 4 layers |
| `AuditEvent` | C7 | F-019..F-020 | I-042..I-043 | query_audit_events, get_audit_summary | Audit Log | audit_events | GET /audit | S-030..S-031 | 4 layers |
| `ApprovalRequest` | C5 | F-021..F-023 | I-044..I-046 | list_pending_approvals, resolve_approval | Approval Queue | approval_requests | GET/POST /approvals | S-040..S-042 | 5 layers |

---

## 5. Cross-Interface Journey Flow

### Journey: Pipeline with Approval Gate

This is the canonical cross-interface journey. A developer triggers a pipeline from Claude Code (MCP), the pipeline pauses at an approval gate, an engineering lead approves via the Dashboard, and the developer confirms completion via MCP.

```
 DEVELOPER (Claude Code)                    ENG LEAD (Dashboard Browser)
 ========================                    ============================
         |                                            |
    [1]  |  MCP: trigger_pipeline                     |
         |  { project: "Acme",                        |
         |    raw_spec: "..." }                        |
         |                                            |
         +--------+                                   |
                  |                                   |
                  v                                   |
         +------------------+                         |
         |  MCP Server      |                         |
         |  (agents-server) |                         |
         +--------+---------+                         |
                  |                                   |
                  v                                   |
         +------------------+                         |
         | PipelineService  |                         |
         | .trigger()       |                         |
         +--------+---------+                         |
                  |                                   |
                  v                                   |
         +------------------+                         |
         | SessionStore     |                         |
         | Write: run_id,   |                         |
         | status=running   |                         |
         +--------+---------+                         |
                  |                                   |
    [2]  |  <-- PipelineRun                           |
         |  { run_id: "abc",                          |
         |    status: "running" }                      |
         |                                            |
         |        ... agents D0-D5 execute ...         |
         |        ... quality gates pass ...           |
         |                                            |
                  |                                   |
                  v                                   |
         +------------------+                         |
         | APPROVAL GATE    |                         |
         | Pipeline pauses  |                         |
         | at step D6       |                         |
         +--------+---------+                         |
                  |                                   |
    [3]  |  Pipeline paused.                          |
         |  status=awaiting_approval                   |
         |                                            |
                  |                                   |
                  +------- NOTIFICATION ------+       |
                  |  (webhook / email / SSE)  |       |
                  |                           v       |
                  |                    +------+-------+------+
                  |                    | Dashboard: Approval  |
                  |                    | Queue Page           |
                  |                    |                      |
                  |               [4]  | Anika sees:          |
                  |                    | "Pipeline abc needs  |
                  |                    |  approval at D6"     |
                  |                    |                      |
                  |                    | Reviews:             |
                  |                    | - Documents D0-D5    |
                  |                    | - Cost so far: $8.50 |
                  |                    | - Quality scores     |
                  |                    +------+-------+------+
                  |                           |
                  |                    [5]    | Click: [Approve]
                  |                           |
                  |                           v
                  |                    +------+-------+------+
                  |                    | REST API:            |
                  |                    | POST /approvals/     |
                  |                    |   {request_id}/      |
                  |                    |   resolve            |
                  |                    | { decision:          |
                  |                    |   "approved" }       |
                  |                    +------+-------+------+
                  |                           |
                  |                           v
                  |                    +------+-------+------+
                  |                    | ApprovalService      |
                  |                    | .resolve()           |
                  |                    +------+-------+------+
                  |                           |
                  |                           v
                  |                    +------+-------+------+
                  |                    | PipelineService      |
                  |                    | .resume()            |
                  |                    | (auto-triggered)     |
                  |                    +------+-------+------+
                  |                           |
                  |        ... agents D6-D13 execute ...
                  |        ... quality gates pass ...
                  |                           |
                  |                           v
                  |                    +------+-------+------+
                  |                    | Pipeline completed.  |
                  |                    | status=completed     |
                  |                    +------+-------+------+
                  |                           |
         +--------+---------------------------+
         |
    [6]  |  MCP: get_pipeline_status
         |  { run_id: "abc" }
         |
         +--------+
                  |
                  v
         +------------------+
         | PipelineService  |
         | .get_status()    |
         +--------+---------+
                  |
    [7]  |  <-- PipelineRun
         |  { run_id: "abc",
         |    status: "completed",
         |    cost_so_far: 22.40,
         |    documents: [...14 docs] }
         |
         v
  DEVELOPER SEES: Pipeline complete.
  14 documents generated. Total cost: $22.40
```

### Journey Steps Summary

| Step | Actor | Interface | Action | Service Method | Data Shape |
|------|-------|-----------|--------|---------------|------------|
| 1 | Developer | MCP | trigger_pipeline | PipelineService.trigger() | PipelineRun |
| 2 | Developer | MCP | Receives run confirmation | -- | PipelineRun |
| 3 | System | Internal | Pipeline pauses at approval gate | PipelineService.pause() | ApprovalRequest |
| 4 | Eng Lead | Dashboard | Views pending approval | ApprovalService.list_pending() | ApprovalRequest |
| 5 | Eng Lead | Dashboard/REST | Approves gate | ApprovalService.resolve() | ApprovalRequest |
| 6 | Developer | MCP | get_pipeline_status | PipelineService.get_status() | PipelineRun |
| 7 | Developer | MCP | Receives final result | -- | PipelineRun |

### Key Property: Interface Parity

Both MCP and REST return the same `PipelineRun` shape. The developer could also check status via REST (`GET /api/v1/pipelines/abc`) and get an identical response body. The Eng Lead could also approve via MCP (`resolve_approval`). The interfaces are interchangeable -- the journey crosses them for convenience, not necessity.

---

## 6. Error Propagation Flow

### Scenario: D7 (MCP-TOOL-SPEC) Fails Quality Gate

```
  GROUP 5 — THE PARALLEL SPRINT
  D7 and D8 run in parallel. D7 fails. D8 is NOT blocked.

          +--------+                  +--------+
          |   D7   |                  |   D8   |
          |MCP-TOOL|                  |DESIGN  |
          | SPEC   |                  | SPEC   |
          +---+----+                  +---+----+
              |                           |
              v                           v
        ═══QG-5a═══                 ═══QG-5b═══
              |                           |
              | FAIL                      | PASS
              | (missing 3 tools,         | (all checks pass)
              |  schema errors)           |
              v                           v
        +----------+               [design_spec] --> ready
        | RETRY 1  |               for downstream
        | Feedback:|
        | "Missing |
        |  tools:  |
        |  I-044,  |
        |  I-045,  |
        |  I-046.  |
        |  Fix     |
        |  schemas"|
        +----+-----+
             |
             v
          +--------+
          |   D7   |
          | RETRY 1|
          +---+----+
              |
              v
        ═══QG-5a═══
              |
              | FAIL
              | (schema error on
              |  I-046 remains)
              v
        +----------+
        | RETRY 2  |
        | Feedback:|
        | "I-046   |
        |  resolve |
        |  _approv |
        |  al:     |
        |  output  |
        |  missing |
        |  'resol  |
        |  ved_at' |
        |  field"  |
        +----+-----+
             |
             v
          +--------+
          |   D7   |
          | RETRY 2|
          +---+----+
              |
              v
        ═══QG-5a═══
              |
              | PASS
              v
        [mcp_tool_spec] --> ready for downstream
```

### Impact Analysis During D7 Retries

```
  While D7 retries (Groups 5-6 boundary):

  Agent     Status          Reason
  ──────    ─────────────   ──────────────────────────────────────
  D8        COMPLETED       Parallel with D7, no dependency on D7
  D9        BLOCKED         Needs [mcp_tool_spec] from D7
  D10       BLOCKED         Needs [mcp_tool_spec] from D7 (transitive via D9)
  D11       BLOCKED         Needs [mcp_tool_spec] from D7
  D12       NOT BLOCKED     Does not read [mcp_tool_spec]
  D13       BLOCKED         Needs [mcp_tool_spec] from D7

  Timeline with D7 retry:

  Normal:    ...G4..[G5: D7||D8 ~4min]..QG5..[G6: D9]..
  With retry:...G4..[G5: D7(fail,retry1,fail,retry2,pass) ~12min || D8 ~4min]..QG5..[G6: D9]..
                                         ^^^^^^^^^^^^
                                         +8 min added to critical path
```

### Scenario: All Retries Exhausted (Max Retries = 3)

```
          +--------+
          |   D7   |
          | RETRY 3|
          +---+----+
              |
              v
        ═══QG-5a═══
              |
              | FAIL (3rd time)
              v
  +------------------------------+
  | PIPELINE PAUSED              |
  | status: error_paused         |
  | paused_at_step: D7           |
  | retry_count: 3/3             |
  | error: "QG-5a failed after   |
  |  3 retries"                  |
  +-------------+----------------+
                |
                v
  +------------------------------+
  | NOTIFICATION SENT            |
  | To: Pipeline owner (Marcus)  |
  | Channel: MCP + Email         |
  | Message: "Pipeline abc       |
  |  paused at D7 after 3        |
  |  retry failures. Manual      |
  |  intervention required."     |
  +-------------+----------------+
                |
                v
  +------------------------------+
  | HUMAN INTERVENTION           |
  | Options:                     |
  | 1. Fix input, retry D7       |
  |    MCP: retry_pipeline_step  |
  |    { run_id, step: "D7" }   |
  |                              |
  | 2. Skip D7, continue with    |
  |    placeholder (degraded)    |
  |    MCP: resume_pipeline      |
  |    { run_id, skip: ["D7"] } |
  |                              |
  | 3. Cancel pipeline           |
  |    MCP: cancel_pipeline      |
  |    { run_id }               |
  +-------------+----------------+
                |
                v (option 1 chosen)
  +------------------------------+
  | Marcus fixes raw_spec input  |
  | and retries D7               |
  +-------------+----------------+
                |
                v
          +--------+
          |   D7   |
          | MANUAL |
          | RETRY  |
          +---+----+
              |
              v
        ═══QG-5a═══
              |
              | PASS
              v
  +------------------------------+
  | PIPELINE RESUMES             |
  | D9 unblocked, continues...  |
  +------------------------------+
```

### Error Propagation Rules

| Rule | Description |
|------|-------------|
| **Parallel isolation** | A failing agent never blocks its parallel sibling. D7 and D8 are independent. |
| **Downstream blocking** | Any agent that reads the failing agent's session key is blocked until the key is written. |
| **Transitive blocking** | If D9 is blocked by D7, then D10 (which reads `data_model` from D9) is transitively blocked. |
| **Retry feedback loop** | Each retry receives the quality gate's structured error feedback as additional input. |
| **Retry budget** | Maximum 3 retries per agent. Each retry adds ~$1.50-2.00 to pipeline cost. |
| **Pause on exhaustion** | After max retries, pipeline pauses (does not fail). Human intervention required. |
| **Partial results preserved** | All successfully completed documents remain in SessionStore. Only the failed step needs re-execution. |
| **Cost continues accruing** | Retry costs are tracked. If retries push total cost near the $25 ceiling, a cost-gate pause triggers before the retry executes. |

---

## 7. Cost Flow

### Per-Step Cost Breakdown

| Step | Agent | Document | Est. Input Tokens | Est. Output Tokens | Est. Cost | Cumulative | Budget Remaining |
|------|-------|----------|-------------------|-------------------|-----------|-----------|-----------------|
| 1 | D0 | ROADMAP | ~2,000 | ~3,000 | $0.30 | $0.30 | $24.70 |
| 2 | D1 | PRD | ~3,000 | ~8,000 | $0.90 | $1.20 | $23.80 |
| 3 | D2 | ARCH | ~8,000 | ~10,000 | $1.40 | $2.60 | $22.40 |
| 4 | D3 | CLAUDE | ~10,000 | ~4,000 | $0.80 | $3.40 | $21.60 |
| 5 | D4 | QUALITY | ~10,000 | ~6,000 | $1.00 | $4.40 | $20.60 |
| 6 | D5 | FEATURE-CATALOG | ~10,000 | ~8,000 | $1.20 | $5.60 | $19.40 |
| 7 | D6 | INTERACTION-MAP | ~15,000 | ~12,000 | $2.00 | $7.60 | $17.40 |
| 8 | D7 | MCP-TOOL-SPEC | ~18,000 | ~10,000 | $1.80 | $9.40 | $15.60 |
| 9 | D8 | DESIGN-SPEC | ~18,000 | ~10,000 | $1.80 | $11.20 | $13.80 |
| 10 | D9 | DATA-MODEL | ~20,000 | ~8,000 | $1.60 | $12.80 | $12.20 |
| 11 | D10 | API-CONTRACTS | ~22,000 | ~10,000 | $2.00 | $14.80 | $10.20 |
| 12 | D11 | BACKLOG | ~25,000 | ~12,000 | $2.40 | $17.20 | $7.80 |
| 13 | D12 | ENFORCEMENT | ~12,000 | ~5,000 | $1.00 | $18.20 | $6.80 |
| 14 | D13 | TESTING | ~25,000 | ~10,000 | $2.00 | $20.20 | $4.80 |
| -- | -- | Quality Gates (x8) | ~8,000 total | ~2,000 total | $0.60 | $20.80 | $4.20 |
| -- | -- | Retry Buffer (est. 1-2 retries) | ~20,000 total | ~10,000 total | $2.10 | $22.90 | $2.10 |
| **Total** | | | **~226,000** | **~128,000** | **$22.90** | **$22.90** | **$2.10** |

### Cost Accumulation Visualization

```
  $25 |.................................................................CEILING
      |
      |
  $23 |                                                          ******* RETRY BUFFER
      |                                                    *****
  $21 |                                              ******  <-- with retries: $22.90
      |                                         *****
  $19 |                                    *****
      |                               *****
  $17 |                          *****
      |                     *****
  $15 |                *****
      |           *****
  $13 |      *****
      |   ****
  $11 | ***
      |**
   $9 |*
      |
   $7 |       Without retries: $20.80
      |
   $5 |
      |
   $3 |
      |
   $1 |*
      |
   $0 +----+----+----+----+----+----+----+----+----+----+----+----+----+----+
       D0   D1   D2   D3   D4   D5   D6   D7   D8   D9  D10  D11  D12  D13
```

### LLM Provider Routing

Each agent invocation follows this routing path through the `sdk/llm/` abstraction:

```
  Agent (D0..D13)
       |
       | tier: fast|balanced|powerful
       v
  +-------------------+
  |   BaseAgent       |
  |  self.llm.complete()
  +--------+----------+
           |
           v
  +-------------------+
  |   LLMProvider     |  <-- sdk/llm/ interface
  |  (abstract)       |
  +--------+----------+
           |
     +-----+-----+----------+
     |           |           |
     v           v           v
  Anthropic   OpenAI     Ollama
  Provider    Provider   Provider
     |           |           |
     v           v           v
  claude-*    gpt-4o-*   llama-*
```

**Provider resolution:** `LLM_PROVIDER` env var selects the default. Each agent can override via `llm_provider` in `agent_registry`. The tier (fast/balanced/powerful) is resolved to a concrete model ID by the active provider's `TIER_MAP`.

**Cost flow is provider-aware:** Each provider implementation returns `(input_cost, output_cost)` per-token pricing. `CostService.record()` stores the `provider` column in `cost_metrics`, enabling per-provider cost reporting via `GET /api/v1/cost/report` (see `by_provider` breakdown).

### Cost Governance Triggers

| Threshold | % of Budget | Action |
|-----------|------------|--------|
| $12.50 | 50% | Info log: "Pipeline at 50% budget" |
| $18.75 | 75% | Warning: notify pipeline owner |
| $22.50 | 90% | Alert: cost-gate pause before next agent. Human must approve continuation. |
| $25.00 | 100% | Hard stop: pipeline halted. No further agent invocations. |

### Cost by Execution Group

| Group | Agents | Group Cost | % of Total |
|-------|--------|-----------|------------|
| G1 | D0, D1 | $1.20 | 5.2% |
| G2 | D2 | $1.40 | 6.1% |
| G3 | D3, D4, D5 | $3.00 | 13.1% |
| G4 | D6 | $2.00 | 8.7% |
| G5 | D7, D8 | $3.60 | 15.7% |
| G6 | D9 | $1.60 | 7.0% |
| G7 | D10 | $2.00 | 8.7% |
| G8 | D11, D12, D13 | $5.40 | 23.6% |
| QG | Quality Gates | $0.60 | 2.6% |
| -- | Retry Buffer | $2.10 | 9.2% |
| **Total** | | **$22.90** | **100%** |

**Observation:** Group 8 (the terminal group) is the most expensive at 23.6% because its three agents have the largest input contexts -- they read nearly all upstream documents. This is expected: later agents accumulate more context.

---

## Appendix A: Quick Reference Card

```
+-----------------------------------------------------------------------+
|                  PIPELINE QUICK REFERENCE                              |
+-----------------------------------------------------------------------+
| Agents:      14 (D0-D13)                                              |
| Groups:      8 parallel execution groups                               |
| QG Gates:    8 quality gates                                           |
| Session Keys: 15 (1 input + 14 outputs)                               |
| Critical Path: D1->D2->D4->D6->D7->D9->D10->D11 (8 steps)           |
| Wall Clock:  ~25 min (parallel) / ~40 min (sequential)                |
| Cost:        ~$20.80 base + ~$2.10 retry buffer = ~$22.90             |
| Provider:    LLM_PROVIDER env var (default: anthropic)                 |
| Tiers:       fast / balanced / powerful (resolved per provider)        |
| Budget:      $25.00 hard ceiling                                       |
| Max Retries: 3 per agent                                               |
| Most-Read:   arch_doc (10 downstream readers)                          |
| Bottleneck:  D6 (INTERACTION-MAP) — 4 input keys, 6 output readers    |
+-----------------------------------------------------------------------+
```

## Appendix B: Cross-Reference to Other Documents

| Section in This Doc | References | Referenced By |
|---------------------|-----------|--------------|
| 1. Complete Pipeline Flow | Doc 14 (AGENT-HANDOFF-PROTOCOL) pipeline rules | -- |
| 2. Session Key Flow Matrix | Doc 14 session key definitions | Doc 13 (TESTING) parity tests |
| 3. Parallel Execution Groups | Doc 02 (ARCH) orchestration layer | Doc 11 (BACKLOG) sprint planning |
| 4. Data Shape Flow | Doc 06 (INTERACTION-MAP) data shapes | Doc 13 (TESTING) traceability tests |
| 5. Cross-Interface Journey | Doc 06 Journey J-001, Doc 08 (DESIGN-SPEC) wireframes | Doc 13 (TESTING) journey tests |
| 6. Error Propagation | Doc 04 (QUALITY) retry rules, Doc 12 (ENFORCEMENT) guardrails | Doc 11 (BACKLOG) error-handling stories |
| 7. Cost Flow | Doc 04 (QUALITY) Q-budget rules, PRD M9 ($25 ceiling) | Doc 12 (ENFORCEMENT) cost enforcement |

---

*End of document.*
