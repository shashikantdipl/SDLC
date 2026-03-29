# Agent Interaction Diagram — Full-Stack-First Pipeline

## How to Read This Document

This is the visual companion to AGENT-HANDOFF-PROTOCOL.md (Doc 22). It shows:
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
                                         ▼
                              ┌──────────────────┐
                              │ D0               │
                              │ BRD Agent        │
                              └────────┬─────────┘
                                       │
                                 [brd_doc]
                                       │
                                  ═══QG═══
                                       │
                          ┌────────────┼────────────┐
                          │ PARALLEL   │            │
                          ▼            ▼            │
                   ┌──────────┐  ┌──────────┐      │
                   │ D1       │  │ D2       │      │
                   │ ROADMAP  │  │ PRD      │      │
                   │ Agent    │  │ Agent    │      │
                   └────┬─────┘  └────┬─────┘      │
                        │             │            │
                  [roadmap_doc]  [prd_doc]          │
                        │             │            │
                   ═══QG═══     ═══QG═══           │
                        │             │            │
                        │             ▼            │
                        │      ┌──────────┐        │
                        │      │ D3       │        │
                        │      │ ARCH     │        │
                        │      │ Agent    │        │
                        │      └────┬─────┘        │
                        │           │              │
                        │     [arch_doc]           │
                        │           │              │
                        │      ═══QG═══            │
                        │           │              │
                        │           ▼              │
                        │    ┌──────────┐          │
                        │    │ D4       │          │
                        │    │ FEATURES │          │
                        │    │ Agent    │          │
                        │    └────┬─────┘          │
                        │         │                │
                        │  [feature_catalog]       │
                        │         │                │
                        │    ═══QG═══              │
                        │         │                │
                        │         ▼                │
                        │    ┌──────────┐          │
                        │    │ D5       │          │
                        │    │ QUALITY  │          │
                        │    │ Agent    │          │
                        │    └────┬─────┘          │
                        │         │                │
                        │   [quality_doc]          │
                        │         │                │
                        │    ═══QG═══              │
                        │         │                │
                        │         ▼                │
                        │    ┌──────────┐          │
                        │    │ D6       │          │
                        │    │ SECURITY │          │
                        │    │ Agent    │          │
                        │    └────┬─────┘          │
                        │         │                │
                        │   [security_arch]        │
                        │         │                │
                        │    ═══QG═══              │
                        │         │                │
                        │         ▼                │
                        │  ┌──────────┐            │
                        │  │ D7       │            │
                        │  │ INTERACT │            │
                        │  │ MAP Agent│            │
                        │  └────┬─────┘            │
                        │       │                  │
                        │ [interaction_map]        │
                        │       │                  │
                        │  ═══QG═══                │
                        │       │                  │
                        │  ┌────┴────┐             │
                        │  │PARALLEL │             │
                        │  ▼         ▼             │
                        │┌──────────┐┌──────────┐  │
                        ││ D8       ││ D9       │  │
                        ││ MCP-TOOL ││ DESIGN   │  │
                        ││ Agent    ││ Agent    │  │
                        │└────┬─────┘└────┬─────┘  │
                        │     │           │        │
                        │[mcp_tool_spec][design_spec]
                        │     │           │        │
                        │═══QG═══    ═══QG═══      │
                        │     └─────┬─────┘        │
                        │           ▼              │
                        │    ┌──────────┐          │
                        │    │ D10      │          │
                        │    │ DATA     │          │
                        │    │ MODEL    │          │
                        │    └────┬─────┘          │
                        │         │                │
                        │   [data_model]           │
                        │         │                │
                        │    ═══QG═══              │
                        │         ▼                │
                        │    ┌──────────┐          │
                        │    │ D11      │          │
                        │    │ API      │          │
                        │    │ CONTRACT │          │
                        │    └────┬─────┘          │
                        │         │                │
                        │   [api_contracts]        │
                        │         │                │
                        │    ═══QG═══              │
                        │         ▼                │
                        │    ┌──────────┐          │
                        │    │ D12      │          │
                        │    │ USER     │          │
                        │    │ STORIES  │          │
                        │    └────┬─────┘          │
                        │         │                │
                        │   [user_stories]         │
                        │         │                │
                        │    ═══QG═══              │
                        │         │                │
               ┌────────┼─────────┤                │
               │PARALLEL│         │                │
               ▼        ▼         ▼                │
        ┌──────────┐┌──────────┐                   │
        │ D13      ││ D14      │                   │
        │ BACKLOG  ││ CLAUDE   │                   │
        │ Agent    ││ Agent    │                   │
        └────┬─────┘└────┬─────┘                   │
             │           │                         │
        [backlog]  [claude_doc]                    │
             │           │                         │
        ═══QG═══    ═══QG═══                       │
             │           │                         │
             │           ▼                         │
             │    ┌──────────┐                     │
             │    │ D15      │                     │
             │    │ ENFORCE  │                     │
             │    │ Agent    │                     │
             │    └────┬─────┘                     │
             │         │                           │
             │  [enforcement_rules]                │
             │         │                           │
             │    ═══QG═══                         │
             │         │                           │
             │         ▼                           │
             │    ┌──────────┐                     │
             │    │ D16      │                     │
             │    │ INFRA    │                     │
             │    │ Agent    │                     │
             │    └────┬─────┘                     │
             │         │                           │
             │   [infra_design]                    │
             │         │                           │
             │    ═══QG═══                         │
             │         │                           │
             │    ┌────┴────┐                      │
             │    │PARALLEL │                      │
             │    ▼         ▼                      │
             │┌──────────┐┌──────────┐             │
             ││ D17      ││ D18      │             │
             ││ MIGRATION││ TESTING  │             │
             ││ Agent    ││ Agent    │             │
             │└────┬─────┘└────┬─────┘             │
             │     │           │                   │
             │[migration] [test_strategy]          │
             │     │           │                   │
             │═══QG═══    ═══QG═══                 │
             │     │           │                   │
             │     └─────┬─────┘                   │
             │           ▼                         │
             │    ┌──────────┐                     │
             │    │ D19      │                     │
             │    │ FAULT-TOL│                     │
             │    │ Agent    │                     │
             │    └────┬─────┘                     │
             │         │                           │
             │  [fault_tolerance]                  │
             │         │                           │
             │    ═══QG═══                         │
             │         ▼                           │
             │    ┌──────────┐                     │
             │    │ D20      │                     │
             │    │GUARDRAILS│                     │
             │    │ Agent    │                     │
             │    └────┬─────┘                     │
             │         │                           │
             │  [guardrails_spec]                  │
             │         │                           │
             │    ═══QG═══                         │
             │         ▼                           │
             │    ┌──────────┐                     │
             │    │ D21      │                     │
             │    │COMPLIANCE│                     │
             │    │ Agent    │                     │
             │    └────┬─────┘                     │
             │         │                           │
             │  [compliance_matrix]                │
             │         │                           │
             │    ═══QG═══                         │
             │         │                           │
             └─────────┼───────────────────────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │   PIPELINE COMPLETE  │
            │   24 documents in    │
            │   SessionStore       │
            └──────────────────────┘

═══QG═══ = Quality Gate (rubric scoring, format check, cross-reference validation)
```

---

## 2. Session Key Flow Matrix

Shows exactly which agent WRITES and which agents READ each session key:

```
Session Key        Writer    Readers
─────────────────  ────────  ────────────────────────────────────
discovery_sessions [human]   D0
raw_spec           [human]   D1, D2
brd_doc            D0        D1, D2, D17
roadmap_doc        D1        D14
prd_doc            D2        D3, D4, D5, D6, D7, D9, D11, D12, D13, D17
arch_doc           D3        D4, D5, D6, D7, D8, D9, D10, D11, D12, D13, D14, D15, D16, D17, D18, D19, D20, D21
feature_catalog    D4        D5, D6, D7, D8, D9, D10, D12, D13, D16
quality_doc        D5        D6, D7, D8, D9, D10, D13, D15, D16, D18, D19, D20, D21
security_arch      D6        D15, D16, D17, D18, D19, D20, D21
interaction_map    D7        D8, D9, D10, D11, D13, D18
mcp_tool_spec      D8        D10, D11, D12, D13, D18
design_spec        D9        D10, D11, D12, D13, D18
data_model         D10       D11, D12, D14, D17, D18, D19, D21
api_contracts      D11       D12, D14, D19
user_stories       D12       D13
backlog            D13       (terminal — no readers)
claude_doc         D14       D15, D18
enforcement_rules  D15       D20
infra_design       D16       D19
migration_plan     D17       (terminal — no readers)
test_strategy      D18       (terminal — no readers)
fault_tolerance    D19       D21
guardrails_spec    D20       D21
compliance_matrix  D21       (terminal — no readers)
handoff_protocol   D22       D23
interaction_diagram D23      (terminal — no readers)
```

### Key Observations:
- **Most-read keys**: `arch_doc` (18 readers), `quality_doc` (12 readers), `prd_doc` (10 readers)
- **Terminal keys**: `backlog`, `migration_plan`, `test_strategy`, `compliance_matrix`, `interaction_diagram` (no downstream consumers)
- **Single-writer guarantee**: Every key has exactly ONE agent that writes it
- **Fan-out pattern**: D3 (ARCH) has the widest fan-out — almost everything reads it

---

## 3. Parallel Execution Groups

```
Group 0 (Sequential): D0                ← BRD from discovery sessions
                         │
Group 1 (Parallel):  D1 ║ D2            ← Both read raw_spec + brd_doc
                         ║
Group 2 (Sequential): D3                ← Needs prd_doc from D2
                         │
Group 3 (Sequential): D4                ← FEATURES needs prd_doc + arch_doc
                         │
Group 4 (Sequential): D5                ← QUALITY needs features
                         │
Group 5 (Sequential): D6                ← SECURITY needs quality + features
                         │
Group 6 (Sequential): D7                ← INTERACTION-MAP needs quality + features
                         │
Group 7 (Parallel):  D8 ║ D9            ← THE KEY: Both read interaction_map
                         ║
Group 8 (Sequential): D10               ← Needs mcp_tool_spec + design_spec
                         │
Group 9 (Sequential): D11               ← Needs data_model
                         │
Group 10 (Sequential): D12              ← USER-STORIES needs api_contracts
                         │
Group 11 (Parallel): D13 ║ D14          ← BACKLOG + CLAUDE (independent inputs)
                         ║
Group 12 (Sequential): D15              ← ENFORCEMENT needs claude_doc
                         │
Group 13 (Sequential): D16              ← INFRA needs security_arch
                         │
Group 14 (Parallel): D17 ║ D18          ← MIGRATION + TESTING (independent inputs)
                         ║
Group 15 (Sequential): D19              ← FAULT-TOLERANCE needs infra_design
                         │
Group 16 (Sequential): D20              ← GUARDRAILS needs enforcement
                         │
Group 17 (Sequential): D21              ← COMPLIANCE reads everything
```

### Estimated Timeline (with parallelism):

```
Time ──────────────────────────────────────────────────────────────────────────►
│
│  ┌─D0──┤                                                Group 0 (~2 min)
│        ├──D1──┤
│        ├──D2──┤  Group 1 (~3 min, parallel)
│              └┤
│               ├──D3──┤                                  Group 2 (~3 min)
│                     ├──D4──┤                            Group 3 (~2 min)
│                           ├──D5──┤                      Group 4 (~2 min)
│                                 ├──D6──┤                Group 5 (~2 min)
│                                       ├──D7──┤          Group 6 (~4 min)
│                                             ├──D8──┤
│                                             ├──D9──┤    Group 7 (~4 min) THE PARALLEL SPRINT
│                                                   └┤
│                                                    ├──D10──┤   Group 8 (~3 min)
│                                                           ├──D11──┤  Group 9 (~3 min)
│                                                                  ├──D12──┤  Group 10 (~2 min)
│                                                                        ├──D13──┤
│                                                                        ├──D14──┤  Group 11 (~3 min)
│                                                                               ├──D15──┤  Group 12
│                                                                                      ├──D16──┤
│                                                                                             ├──D17──┤
│                                                                                             ├──D18──┤  Group 14
│                                                                                                    ├──D19──┤
│                                                                                                          ├──D20──┤
│                                                                                                                 ├──D21──┤
│
│  Total: ~45 min (vs ~60 min sequential)
│  Savings: ~25% from parallelism
```

---

## 4. Data Shape Flow (Traceability)

Shows how a data concept flows through the pipeline:

```
Example: "PipelineRun" data shape

PRD (D2)
  │ Defines: Capability C1 "Agent Orchestration"
  │ Defines: Journey "Developer triggers pipeline"
  ▼
FEATURE-CATALOG (D4)
  │ Defines: F-001 "Pipeline Trigger"
  │          shared_service: PipelineService
  │          interfaces: [mcp, rest, dashboard]
  ▼
INTERACTION-MAP (D7)
  │ Defines: I-001 "Trigger Pipeline"
  │ Defines: Shape "PipelineRun" {run_id, status, steps, cost_usd}
  │ Defines: PipelineService.trigger() → PipelineRun
  │
  ├──────────────────────────┐
  ▼                          ▼
MCP-TOOL-SPEC (D8)     DESIGN-SPEC (D9)
  │ Tool: trigger_pipeline    │ Screen: Pipeline Status View
  │ Returns: PipelineRun      │ Displays: PipelineRun fields
  │ shape (from I-MAP)        │ shape (from I-MAP)
  │                          │
  ├──────────────────────────┤
  ▼                          ▼
DATA-MODEL (D10)
  │ Table: pipeline_runs
  │ Maps PipelineRun shape → columns
  │ Indexes: by project_id+status (MCP query)
  │          by project_id+started_at DESC (Dashboard query)
  ▼
API-CONTRACTS (D11)
  │ POST /api/v1/pipelines → wraps trigger_pipeline MCP tool
  │ GET  /api/v1/pipelines/{id} → wraps get_pipeline_status MCP tool
  │ Both return PipelineRun JSON shape
  ▼
BACKLOG (D13)
  │ S-001: Implement PipelineService.trigger() (service layer)
  │ S-002: Expose trigger_pipeline via MCP (mcp layer)
  │ S-003: Pipeline Trigger Form on Dashboard (dashboard layer)
  │ S-004: Parity test: MCP vs REST for trigger_pipeline (test layer)
  ▼
TESTING (D18)
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
         │ 1. "Run the 24-doc pipeline for project X"
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
SCENARIO: D8 (MCP-TOOL-SPEC) fails quality gate

D7 (INTERACTION-MAP) ──[interaction_map]──► D8 (MCP-TOOL-SPEC)
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
                    D9 (DESIGN)          D10 (DATA-MODEL)
                    continues...         waits for D9 too...


SCENARIO: D8 fails after all retries

                                         ═══QG═══ FAIL (score: 0.71, retry 2/2)
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ PIPELINE PAUSED  │
                                    │                  │
                                    │ • D9 (DESIGN)    │  ← NOT blocked (parallel, doesn't need D8)
                                    │   continues!     │
                                    │                  │
                                    │ • D10 (DATA-MODEL)│ ← BLOCKED (needs mcp_tool_spec)
                                    │   waiting...     │
                                    │                  │
                                    │ • Human notified │
                                    │   via Slack      │
                                    └─────────────────┘

                    Human reviews D8 output, manually fixes, uploads to SessionStore
                                              │
                                    Pipeline resumes from D10
```

---

## 7. Cost Flow

```
Pipeline Run Cost Breakdown (estimated):

Step  Agent            Est. Cost   Cumulative   Budget Remaining
────  ───────────────  ──────────  ──────────   ────────────────
 0    D0  BRD          $0.60       $0.60        $44.40
 1    D1  ROADMAP      $0.50       $1.10        $43.90
 2    D2  PRD          $0.80       $1.90        $43.10
 3    D3  ARCH         $1.50       $3.40        $41.60
 4    D4  FEATURES     $0.70       $4.10        $40.90
 5    D5  QUALITY      $0.60       $4.70        $40.30
 6    D6  SECURITY     $1.20       $5.90        $39.10
 7    D7  INTERACT-MAP $1.20       $7.10        $37.90
 8    D8  MCP-SPEC     $2.00       $9.10        $35.90
 9    D9  DESIGN-SPEC  $2.50       $11.60       $33.40
10    D10 DATA-MODEL   $1.50       $13.10       $31.90
11    D11 API-CONTR    $1.80       $14.90       $30.10
12    D12 USER-STORIES $1.20       $16.10       $28.90
13    D13 BACKLOG      $2.00       $18.10       $26.90
14    D14 CLAUDE       $0.80       $18.90       $26.10
15    D15 ENFORCE      $0.50       $19.40       $25.60
16    D16 INFRA        $1.50       $20.90       $24.10
17    D17 MIGRATION    $1.20       $22.10       $22.90
18    D18 TESTING      $1.50       $23.60       $21.40
19    D19 FAULT-TOL    $1.20       $24.80       $20.20
20    D20 GUARDRAILS   $1.50       $26.30       $18.70
21    D21 COMPLIANCE   $1.50       $27.80       $17.20
      Quality gates    ~$4.00      $31.80       $13.20
      Retries (est)    ~$5.00      $36.80       $8.20
────  ───────────────  ──────────
      TOTAL            ~$36.80     Budget: $45.00 ✓

Cost ceiling check happens AFTER each step.
If cumulative > $45.00: pipeline pauses, human decides.
```
