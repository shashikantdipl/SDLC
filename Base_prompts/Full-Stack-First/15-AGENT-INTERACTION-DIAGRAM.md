# Agent Interaction Diagram — Full-Stack-First Pipeline

## How to Read This Document

This is the visual companion to AGENT-HANDOFF-PROTOCOL.md (Doc 14). It shows:
- Which agent produces which document
- Which session keys flow between agents
- Which steps run in parallel
- Where quality gates sit
- The complete data flow from raw spec to final deliverables

---

## 1. Complete Pipeline Flow

```
                              ┌─────────────────────────────┐
                              │        RAW SPEC              │
                              │  (Client brief / project     │
                              │   description provided by    │
                              │   human)                     │
                              └──────────┬──────────────────┘
                                         │
                          ┌──────────────┼──────────────┐
                          │ PARALLEL     │              │
                          ▼              ▼              │
                   ┌──────────┐  ┌──────────┐          │
                   │ D0       │  │ D1       │          │
                   │ ROADMAP  │  │ PRD      │          │
                   │ Agent    │  │ Agent    │          │
                   └────┬─────┘  └────┬─────┘          │
                        │             │                │
                  [roadmap_doc]  [prd_doc]              │
                        │             │                │
                   ═══QG═══     ═══QG═══               │
                        │             │                │
                        │             ▼                │
                        │      ┌──────────┐            │
                        │      │ D2       │            │
                        │      │ ARCH     │            │
                        │      │ Agent    │            │
                        │      └────┬─────┘            │
                        │           │                  │
                        │     [arch_doc]               │
                        │           │                  │
                        │      ═══QG═══                │
                        │           │                  │
          ┌─────────────┼───────────┼──────────────┐   │
          │ PARALLEL    │           │              │   │
          ▼             ▼           ▼              │   │
   ┌──────────┐  ┌──────────┐  ┌──────────┐      │   │
   │ D3       │  │ D4       │  │ D5       │      │   │
   │ CLAUDE   │  │ QUALITY  │  │ FEATURES │      │   │
   │ Agent    │  │ Agent    │  │ Agent    │      │   │
   └────┬─────┘  └────┬─────┘  └────┬─────┘      │   │
        │              │             │            │   │
  [claude_doc]   [quality_doc] [feature_catalog]  │   │
        │              │             │            │   │
   ═══QG═══      ═══QG═══     ═══QG═══           │   │
        │              │             │            │   │
        │              └──────┬──────┘            │   │
        │                     │                   │   │
        │                     ▼                   │   │
        │              ┌──────────┐               │   │
        │              │ D6       │               │   │
        │              │ INTERACT │               │   │
        │              │ MAP Agent│               │   │
        │              └────┬─────┘               │   │
        │                   │                     │   │
        │           [interaction_map]              │   │
        │                   │                     │   │
        │              ═══QG═══                   │   │
        │                   │                     │   │
        │     ┌─────────────┼─────────────┐       │   │
        │     │ PARALLEL    │             │       │   │
        │     ▼             ▼             │       │   │
        │ ┌──────────┐ ┌──────────┐       │       │   │
        │ │ D7       │ │ D8       │       │       │   │
        │ │ MCP-TOOL │ │ DESIGN   │       │       │   │
        │ │ Agent    │ │ Agent    │       │       │   │
        │ └────┬─────┘ └────┬─────┘       │       │   │
        │      │             │            │       │   │
        │ [mcp_tool_spec] [design_spec]   │       │   │
        │      │             │            │       │   │
        │ ═══QG═══      ═══QG═══          │       │   │
        │      │             │            │       │   │
        │      └──────┬──────┘            │       │   │
        │             │                   │       │   │
        │             ▼                   │       │   │
        │      ┌──────────┐               │       │   │
        │      │ D9       │               │       │   │
        │      │ DATA     │               │       │   │
        │      │ MODEL    │               │       │   │
        │      │ Agent    │               │       │   │
        │      └────┬─────┘               │       │   │
        │           │                     │       │   │
        │     [data_model]                │       │   │
        │           │                     │       │   │
        │      ═══QG═══                   │       │   │
        │           │                     │       │   │
        │           ▼                     │       │   │
        │      ┌──────────┐               │       │   │
        │      │ D10      │               │       │   │
        │      │ API      │               │       │   │
        │      │ CONTRACT │               │       │   │
        │      │ Agent    │               │       │   │
        │      └────┬─────┘               │       │   │
        │           │                     │       │   │
        │     [api_contracts]             │       │   │
        │           │                     │       │   │
        │      ═══QG═══                   │       │   │
        │           │                     │       │   │
        ├───────────┼─────────────────────┘       │   │
        │           │                             │   │
   ┌────┼───────────┼─────────────────────────┐   │   │
   │ PARALLEL      │                          │   │   │
   ▼    ▼          ▼                          ▼   │   │
┌──────────┐ ┌──────────┐              ┌──────────┐   │
│ D12      │ │ D11      │              │ D13      │   │
│ ENFORCE  │ │ BACKLOG  │              │ TESTING  │   │
│ Agent    │ │ Agent    │              │ Agent    │   │
└────┬─────┘ └────┬─────┘              └────┬─────┘   │
     │             │                        │         │
[enforcement] [backlog]              [test_strategy]  │
     │             │                        │         │
═══QG═══      ═══QG═══                ═══QG═══        │
     │             │                        │         │
     └─────────────┼────────────────────────┘         │
                   │                                  │
                   ▼                                  │
        ┌─────────────────────┐                       │
        │   PIPELINE COMPLETE  │                       │
        │   14 documents in    │                       │
        │   SessionStore       │                       │
        └──────────────────────┘

═══QG═══ = Quality Gate (rubric scoring, format check, cross-reference validation)
```

---

## 2. Session Key Flow Matrix

Shows exactly which agent WRITES and which agents READ each session key:

```
Session Key        Writer    Readers
─────────────────  ────────  ────────────────────────────────────
raw_spec           [human]   D0, D1
roadmap_doc        D0        D3
prd_doc            D1        D2, D4, D5, D6, D8, D10, D11
arch_doc           D2        D3, D4, D5, D6, D7, D9, D10, D11, D12, D13
claude_doc         D3        D12, D13
quality_doc        D4        D6, D7, D8, D9, D11, D13
feature_catalog    D5        D6, D7, D8, D9, D11
interaction_map    D6        D7, D8, D9, D10, D11, D13
mcp_tool_spec      D7        D9, D10, D11, D13
design_spec        D8        D9, D10, D11, D13
data_model         D9        D10, D13
api_contracts      D10       (terminal — no readers)
backlog            D11       (terminal — no readers)
enforcement_rules  D12       (terminal — no readers)
test_strategy      D13       (terminal — no readers)
```

### Key Observations:
- **Most-read keys**: `arch_doc` (10 readers), `prd_doc` (7 readers), `interaction_map` (6 readers)
- **Terminal keys**: `api_contracts`, `backlog`, `enforcement_rules`, `test_strategy` (no downstream consumers)
- **Single-writer guarantee**: Every key has exactly ONE agent that writes it
- **Fan-out pattern**: D2 (ARCH) has the widest fan-out — almost everything reads it

---

## 3. Parallel Execution Groups

```
Group 1 (Parallel):  D0 ║ D1         ← Both read raw_spec only
                         ║
Group 2 (Sequential): D2             ← Needs prd_doc from D1
                         │
Group 3 (Parallel):  D3 ║ D4 ║ D5   ← All read arch_doc + prd_doc
                         ║    ║
Group 4 (Sequential): D6             ← Needs quality_doc + feature_catalog
                         │
Group 5 (Parallel):  D7 ║ D8        ← THE KEY: Both read interaction_map
                         ║
Group 6 (Sequential): D9             ← Needs mcp_tool_spec + design_spec
                         │
Group 7 (Sequential): D10            ← Needs data_model
                         │
Group 8 (Parallel):  D11 ║ D12 ║ D13 ← All dependencies met
```

### Estimated Timeline (with parallelism):

```
Time ──────────────────────────────────────────────────►
│
│  ┌─D0─┐┌─D1─┐                                        Group 1 (~2 min)
│       └┤
│        ├──D2──┤                                       Group 2 (~3 min)
│               ├──D3──┤
│               ├──D4──┤  Group 3 (~3 min, parallel)
│               ├──D5──┤
│                     └┤
│                      ├──D6──┤                         Group 4 (~4 min)
│                            ├──D7──┤
│                            ├──D8──┤  Group 5 (~4 min) THE PARALLEL SPRINT
│                                  └┤
│                                   ├──D9──┤            Group 6 (~3 min)
│                                         ├──D10──┤     Group 7 (~3 min)
│                                                ├──D11──┤
│                                                ├──D12──┤  Group 8 (~3 min)
│                                                ├──D13──┤
│
│  Total: ~25 min (vs ~40 min sequential)
│  Savings: ~37% from parallelism
```

---

## 4. Data Shape Flow (Traceability)

Shows how a data concept flows through the pipeline:

```
Example: "PipelineRun" data shape

PRD (D1)
  │ Defines: Capability C1 "Agent Orchestration"
  │ Defines: Journey "Developer triggers pipeline"
  ▼
FEATURE-CATALOG (D5)
  │ Defines: F-001 "Pipeline Trigger"
  │          shared_service: PipelineService
  │          interfaces: [mcp, rest, dashboard]
  ▼
INTERACTION-MAP (D6)
  │ Defines: I-001 "Trigger Pipeline"
  │ Defines: Shape "PipelineRun" {run_id, status, steps, cost_usd}
  │ Defines: PipelineService.trigger() → PipelineRun
  │
  ├──────────────────────────┐
  ▼                          ▼
MCP-TOOL-SPEC (D7)     DESIGN-SPEC (D8)
  │ Tool: trigger_pipeline    │ Screen: Pipeline Status View
  │ Returns: PipelineRun      │ Displays: PipelineRun fields
  │ shape (from I-MAP)        │ shape (from I-MAP)
  │                          │
  ├──────────────────────────┤
  ▼                          ▼
DATA-MODEL (D9)
  │ Table: pipeline_runs
  │ Maps PipelineRun shape → columns
  │ Indexes: by project_id+status (MCP query)
  │          by project_id+started_at DESC (Dashboard query)
  ▼
API-CONTRACTS (D10)
  │ POST /api/v1/pipelines → wraps trigger_pipeline MCP tool
  │ GET  /api/v1/pipelines/{id} → wraps get_pipeline_status MCP tool
  │ Both return PipelineRun JSON shape
  ▼
BACKLOG (D11)
  │ S-001: Implement PipelineService.trigger() (service layer)
  │ S-002: Expose trigger_pipeline via MCP (mcp layer)
  │ S-003: Pipeline Trigger Form on Dashboard (dashboard layer)
  │ S-004: Parity test: MCP vs REST for trigger_pipeline (test layer)
  ▼
TESTING (D13)
  │ Service test: PipelineService.trigger() returns PipelineRun
  │ MCP test: trigger_pipeline returns PipelineRun via MCP protocol
  │ API test: POST /pipelines returns PipelineRun via HTTP
  │ Parity test: MCP response == REST response
  │ Dashboard test: Pipeline Status View renders PipelineRun
  │ Cross-interface: MCP trigger → Dashboard approval → MCP status check
```

---

## 5. Cross-Interface Journey Flow

Shows how a single user journey spans MCP and Dashboard:

```
Journey: "Pipeline with Approval Gate"

┌──────────────────┐
│ DEVELOPER         │
│ (Claude Code)     │
│ Primary: MCP      │
└────────┬──────────┘
         │
         │ 1. "Run the 12-doc pipeline for project X"
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ MCP Server       │     │ SessionStore     │
│ agents-server    │────►│                  │
│                  │     │ key: pipeline_run│
│ trigger_pipeline │     │ status: running  │
└────────┬─────────┘     └──────────────────┘
         │
         │ 2. Pipeline runs steps 1-5 autonomously
         │
         │ 3. Step 6 = approval gate → pipeline PAUSES
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ ApprovalService  │────►│ PostgreSQL       │
│                  │     │ approval_requests│
│ create_request() │     │ status: pending  │
└──────────────────┘     └────────┬─────────┘
                                  │
            ┌─────────────────────┘
            │
            │ 4. Notification sent (Slack / email / dashboard badge)
            │
            ▼
┌──────────────────┐
│ ENG LEAD          │
│ (Dashboard)       │
│ Primary: Dashboard│
└────────┬──────────┘
         │
         │ 5. Opens Approval Queue screen
         │ 6. Reviews pipeline output so far
         │ 7. Clicks "Approve"
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ REST API          │────►│ ApprovalService  │
│ POST /approvals/  │     │                  │
│   {id}/approve   │     │ approve()        │
└──────────────────┘     └────────┬─────────┘
                                  │
                                  │ 8. Pipeline RESUMES
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Pipeline steps   │
                         │ 7-12 execute     │
                         │ status: completed│
                         └────────┬─────────┘
                                  │
            ┌─────────────────────┘
            │
            ▼
┌──────────────────┐
│ DEVELOPER         │
│ (Claude Code)     │
└────────┬──────────┘
         │
         │ 9. "What's the status of my pipeline?"
         │
         ▼
┌──────────────────┐
│ MCP Server       │
│ get_pipeline_    │
│ status           │──► Returns: completed, 12/12 steps, $18.50
└──────────────────┘
```

---

## 6. Error Propagation Flow

Shows what happens when things go wrong:

```
SCENARIO: D7 (MCP-TOOL-SPEC) fails quality gate

D6 (INTERACTION-MAP) ──[interaction_map]──► D7 (MCP-TOOL-SPEC)
                                              │
                                         ═══QG═══ FAIL (score: 0.68)
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ RETRY #1         │
                                    │ Include feedback:│
                                    │ "Missing tools   │
                                    │  for I-004,      │
                                    │  I-007, I-012"   │
                                    └────────┬────────┘
                                              │
                                         ═══QG═══ FAIL (score: 0.74)
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ RETRY #2         │
                                    │ Include feedback:│
                                    │ "I-012 tool has  │
                                    │  wrong schema,   │
                                    │  I-004 missing"  │
                                    └────────┬────────┘
                                              │
                                         ═══QG═══ PASS (score: 0.88)
                                              │
                                    [mcp_tool_spec] written to SessionStore
                                              │
                          ┌───────────────────┤
                          ▼                   ▼
                    D8 (DESIGN)          D9 (DATA-MODEL)
                    continues...         waits for D8 too...


SCENARIO: D7 fails after all retries

                                         ═══QG═══ FAIL (score: 0.71, retry 2/2)
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ PIPELINE PAUSED  │
                                    │                  │
                                    │ • D8 (DESIGN)    │  ← NOT blocked (parallel, doesn't need D7)
                                    │   continues!     │
                                    │                  │
                                    │ • D9 (DATA-MODEL)│  ← BLOCKED (needs mcp_tool_spec)
                                    │   waiting...     │
                                    │                  │
                                    │ • Human notified │
                                    │   via Slack      │
                                    └─────────────────┘

                    Human reviews D7 output, manually fixes, uploads to SessionStore
                                              │
                                    Pipeline resumes from D9
```

---

## 7. Cost Flow

```
Pipeline Run Cost Breakdown (estimated):

Step  Agent           Est. Cost   Cumulative   Budget Remaining
────  ──────────────  ──────────  ──────────   ────────────────
 1    D0 ROADMAP      $0.50       $0.50        $24.50
 2    D1 PRD          $0.80       $1.30        $23.70
 3    D2 ARCH         $1.50       $2.80        $22.20
 4    D3 CLAUDE       $0.80       $3.60        $21.40
 5    D4 QUALITY      $0.60       $4.20        $20.80
 6    D5 FEATURES     $0.70       $4.90        $20.10
 7    D6 INTERACT-MAP $1.20       $6.10        $18.90
 8    D7 MCP-SPEC     $2.00       $8.10        $16.90
 9    D8 DESIGN-SPEC  $2.50       $10.60       $14.40
10    D9 DATA-MODEL   $1.50       $12.10       $12.90
11    D10 API-CONTR   $1.80       $13.90       $11.10
12    D11 BACKLOG     $2.00       $15.90       $9.10
13    D12 ENFORCE     $0.50       $16.40       $8.60
14    D13 TESTING     $1.50       $17.90       $7.10
      Quality gates   ~$2.00      $19.90       $5.10
      Retries (est)   ~$3.00      $22.90       $2.10
────  ──────────────  ──────────
      TOTAL           ~$22.90     Budget: $25.00 ✓

Cost ceiling check happens AFTER each step.
If cumulative > $25.00: pipeline pauses, human decides.
```
