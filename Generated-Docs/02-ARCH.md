# Architecture Document: Agentic SDLC Platform

| Field            | Value                                      |
| ---------------- | ------------------------------------------ |
| Document ID      | ARCH-ASDLC-001                             |
| Version          | 1.0.0                                      |
| Status           | Draft                                      |
| Owner            | Platform Engineering                       |
| Last Updated     | 2026-03-23                                 |
| Target Release   | v1.0.0                                     |
| Tech Stack       | Python 3.12, Claude Agent SDK, PostgreSQL, asyncio, aiohttp, Streamlit |

---

## 1. System Context (C4 Level 1)

This diagram shows the Agentic SDLC Platform as a single box, its five persona-users, and the external systems it integrates with. Every arrow is labeled with protocol and purpose.

```
                                  +------------------+
                                  |   Anthropic      |
                                  |   Claude API     |
                                  | (Foundation LLM) |
                                  +--------+---------+
                                           |
                                           | HTTPS / REST
                                           | Model inference
                                           |
+------------------+              +--------v---------+              +------------------+
|  Priya Mehta     | CLI / API   |                   | SQL / TCP    |   PostgreSQL     |
|  Platform Engr   +------------>+                   +<------------>+   Database       |
+------------------+             |                   |              | (agent_registry, |
                                 |                   |              |  audit_events,   |
+------------------+             |    AGENTIC SDLC   |              |  cost_metrics,   |
|  David Chen      | Streamlit   |      PLATFORM     |              |  pipeline_runs,  |
|  Delivery Lead   +------------>+                   |              |  session_context)|
+------------------+             |  48 agents across |              +------------------+
                                 |  7 SDLC phases    |
+------------------+             |                   |              +------------------+
|  Sarah Kim       | Streamlit / |  12-doc pipeline  | HTTPS        |   Slack          |
|  Engineering Lead+---Slack---->+  Cost governance   +------------->+   (Webhooks)     |
+------------------+             |  Audit & comply   |              | Notifications,   |
                                 |                   |              | approval gates   |
+------------------+             |                   |              +------------------+
|  Marcus Johnson  | Streamlit / |                   |
|  DevOps Engineer +---CLI------>+                   |              +------------------+
+------------------+             |                   | HTTPS        |   PagerDuty      |
                                 |                   +------------->+   (Alerts)       |
+------------------+             |                   |              | Incident         |
|  Lisa Patel      | Streamlit   |                   |              | escalation       |
|  Compliance Offr +------------>+                   |              +------------------+
+------------------+             +---+----------+----+
                                     |          |
                                     |          |              +------------------+
                                     |          +------------->+   Git Repository  |
                                     |            Git push     |   (GitHub)       |
                                     |            Doc commits  | Source + outputs  |
                                     |                         +------------------+
                                     |
                                     |                         +------------------+
                                     +------------------------>+   File System    |
                                       Write reports           |   reports/{pid}/ |
                                                               +------------------+
```

**Actor Descriptions:**

| Actor / System     | Type     | Interaction                                                        |
| ------------------ | -------- | ------------------------------------------------------------------ |
| Priya Mehta        | User     | Develops agents, runs tests, deploys via CLI and API               |
| David Chen         | User     | Triggers pipelines, monitors progress via Streamlit dashboard      |
| Sarah Kim          | User     | Reviews outputs, responds to approval gates via Streamlit/Slack    |
| Marcus Johnson     | User     | Monitors fleet health, investigates cost spikes via dashboard/CLI  |
| Lisa Patel         | User     | Audits agent behavior, exports compliance reports via Streamlit    |
| Anthropic Claude API | External | Foundation model inference for all 48 agents (Haiku/Sonnet/Opus)  |
| PostgreSQL         | External | Persistent storage for registry, audit, cost, pipeline state       |
| Slack              | External | Approval gate notifications, cost alerts, escalation messages      |
| PagerDuty          | External | Incident alerting for ops-agents and fleet health thresholds       |
| GitHub             | External | Source repository, document output commits, CI/CD pipelines        |
| File System        | Internal | Local report output at `reports/{project_id}/`                     |

---

## 2. Container Architecture (C4 Level 2)

Each container is an independently deployable unit. All containers run as Python processes except PostgreSQL and the external message endpoints.

| Container              | Technology                        | Responsibility                                                                                             | Deployment                                                  |
| ---------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **SDK Runtime**        | Python 3.12, claude_agent_sdk     | Core framework: base agent classes, manifest loading, schema validation, config resolution, hooks lifecycle | Library imported by all agent processes; no standalone deploy |
| **Agent Fleet**        | Python 3.12, asyncio              | 48 agent processes across 7 phases (GOVERN, DESIGN, BUILD, TEST, DEPLOY, OPERATE, OVERSIGHT)               | Per-agent Python processes; canary slots for versioned deploy |
| **Pipeline Orchestrator** | Python 3.12, asyncio           | DAG execution engine: sequential/parallel step scheduling, checkpoint/resume, retry with backoff, self-heal | Single long-running asyncio process                         |
| **API Server**         | Python 3.12, aiohttp              | REST API for agent invocation, pipeline triggers, fleet management, health endpoints                        | Single aiohttp server process; port 8080                    |
| **Dashboard**          | Python 3.12, Streamlit            | Web UI for pipeline monitoring, cost dashboards, audit trail browsing, compliance reporting, approval gates  | Streamlit server process; port 8501                         |
| **PostgreSQL**         | PostgreSQL 15+                    | Persistent storage: agent registry, audit events (immutable), cost metrics, pipeline state, session context | Managed instance (RDS or local); single primary + read replica |
| **Message Bus**        | In-process asyncio queues + Slack webhooks | Typed message envelope routing between agents; external notifications via Slack/PagerDuty webhooks  | In-process for agent-to-agent; HTTPS for external           |

```
+------------------------------------------------------------------+
|                        AGENTIC SDLC PLATFORM                     |
|                                                                  |
|  +------------------+    +-------------------+                   |
|  |   Dashboard      |    |   API Server      |                   |
|  |   (Streamlit)    |    |   (aiohttp)       |                   |
|  |   port 8501      |    |   port 8080       |                   |
|  +--------+---------+    +--------+----------+                   |
|           |                       |                              |
|           +----------+------------+                              |
|                      |                                           |
|            +---------v----------+                                |
|            |   SDK Runtime      |                                |
|            |   (claude_agent_   |                                |
|            |    sdk library)    |                                |
|            +---------+----------+                                |
|                      |                                           |
|     +----------------+----------------+                          |
|     |                |                |                          |
|  +--v-------+  +-----v------+  +-----v--------+                 |
|  | Agent    |  | Pipeline   |  | Message Bus  |                 |
|  | Fleet    |  | Orchestr.  |  | (asyncio Q + |                 |
|  | (48 agts)|  | (DAG eng.) |  |  webhooks)   |                 |
|  +--+-------+  +-----+------+  +-----+--------+                 |
|     |                |                |                          |
|     +----------------+----------------+                          |
|                      |                                           |
|            +---------v----------+                                |
|            |   PostgreSQL       |                                |
|            |   (8 tables)       |                                |
|            +--------------------+                                |
+------------------------------------------------------------------+
         |                    |                    |
    Claude API            Slack API           PagerDuty API
```

---

## 3. Component Diagram (C4 Level 3)

### 3.1 SDK Runtime — Internal Components

```
+==============================================================================+
|                              SDK RUNTIME                                      |
|                                                                              |
|  CORE (existing)                         STORES (to build)                   |
|  +--------------------+                  +-----------------------------+     |
|  | BaseAgent          |                  | SessionStore        [P1]   |     |
|  | BaseStatefulAgent  |                  | PostgresCostStore   [P1]   |     |
|  | BaseHooks          |                  | ApprovalStore       [P2]   |     |
|  | ManifestLoader     |                  | PipelineCheckpoint  [P2]   |     |
|  | SchemaValidator    |                  +-----------------------------+     |
|  +--------------------+                                                      |
|                                          ORCHESTRATION (to build)            |
|  CONFIG RESOLUTION                       +-----------------------------+     |
|  +--------------------+                  | PipelineRunner      [P3]   |     |
|  | ArchetypeResolver  |                  | TeamOrchestrator    [P3]   |     |
|  |  (7 YAML files)    |                  +-----------------------------+     |
|  | MixinMerger        |                                                      |
|  | ManifestMerger     |                  ENFORCEMENT (to build)              |
|  | ClientProfileApply |                  +-----------------------------+     |
|  +--------------------+                  | TokenBucketRateLimiter [P2]|     |
|                                          | ExceptionPromotionEng [P4] |     |
|  COMMUNICATION                           | SelfHealPolicy       [P4] |     |
|  +--------------------+                  +-----------------------------+     |
|  | MessageEnvelope    |                                                      |
|  |  (typed, 7 proto-  |                 EVALUATION (to build)                |
|  |   col patterns)    |                  +-----------------------------+     |
|  | TrustChainValidator|                  | QualityScorer        [P4]  |     |
|  +--------------------+                  +-----------------------------+     |
|                                                                              |
|  OBSERVABILITY (to build)                SERVER (to build)                   |
|  +--------------------+                  +-----------------------------+     |
|  | OtelInstrumentation|                  | HealthServer         [P4]  |     |
|  |   [P5]             |                  | WebhookNotifier      [P4]  |     |
|  +--------------------+                  +-----------------------------+     |
+==============================================================================+
```

### 3.2 Agent Fleet — Internal Components

```
+==============================================================================+
|                              AGENT FLEET                                      |
|                                                                              |
|  GOVERN PHASE (agents/govern/)                                               |
|  +-------+ +-------+ +-------+ +-------+ +-------+                          |
|  | G1    | | G2    | | G3    | | G4    | | G5    |                          |
|  | Cost  | | Audit | | Comp- | | Team  | | Fleet |                          |
|  | Guard | | Logger| | liance| | Orch. | | Mgr   |                          |
|  +-------+ +-------+ +-------+ +-------+ +-------+                          |
|                                                                              |
|  DESIGN PHASE (agents/claude-cc/)                                            |
|  +-------+ +-------+ +-------+ +-------+                                    |
|  | D1    | | D2    | | D3    | | D4    |                                    |
|  | Road- | | PRD   | | CLAUDE| | Feat  |                                    |
|  | map   | | Gen   | | .md   | | Cat   |                                    |
|  +-------+ +-------+ +-------+ +-------+                                    |
|  +-------+ +-------+ +-------+ +-------+ +-------+ +-------+ +-------+      |
|  | D5    | | D6    | | D7    | | D8    | | D9    | | D10   | | D11   |      |
|  | Arch  | | Data  | | API   | | Enf.  | | Qual  | | Test  | | Design|      |
|  | Gen   | | Model | | Contr.| | Scaff | | Spec  | | Strat | | Spec  |      |
|  +-------+ +-------+ +-------+ +-------+ +-------+ +-------+ +-------+      |
|                                                                              |
|  BUILD PHASE              TEST PHASE              DEPLOY PHASE               |
|  +------+ +------+       +------+ +------+       +------+                   |
|  | B1-B4| | B5-B8|       | T1-T3| | T4   |       | P1-P3|                   |
|  | Code | | CI   |       | Unit | | Integ|       | Deploy|                   |
|  | Rev. | | Gates|       | Test | | Test |       | Agents|                   |
|  +------+ +------+       +------+ +------+       +------+                   |
|                                                                              |
|  OPERATE PHASE            OVERSIGHT PHASE                                    |
|  +------+ +------+       +--------+ +--------+                              |
|  | O1-O3| | O4   |       | OV-U1  | | OV-*   |                              |
|  | Ops  | | Scale|       | Unified| | Phase  |                              |
|  | Resp.| | Agent|       | Orch.  | | Overst.|                              |
|  +------+ +------+       +--------+ +--------+                              |
|                                                                              |
|  AGENT INTERNAL STRUCTURE (per agent):                                       |
|  +-----------------------------------------------------------+              |
|  | {AGENT-ID}/                                                |              |
|  |   manifest.yaml  -- 9 subsystems (declarative config)     |              |
|  |   prompt.md       -- system prompt template                |              |
|  |   agent.py        -- agent logic (extends BaseAgent)       |              |
|  |   hooks.py        -- lifecycle hooks (extends BaseHooks)   |              |
|  |   tools.py        -- tool definitions for Claude SDK       |              |
|  |   rubric.yaml     -- quality evaluation rubric             |              |
|  |   __init__.py     -- module export                         |              |
|  |   requirements.txt-- agent-specific deps                   |              |
|  |   tests/          -- golden + adversarial tests            |              |
|  +-----------------------------------------------------------+              |
+==============================================================================+
```

### 3.3 Pipeline Orchestrator — Internal Components

```
+==============================================================================+
|                         PIPELINE ORCHESTRATOR                                 |
|                                                                              |
|  +-------------------+    +--------------------+    +-------------------+     |
|  | DAGParser         |    | StepScheduler      |    | CheckpointMgr    |     |
|  | Reads team YAML   |    | Sequential +       |    | Save/restore     |     |
|  | Builds exec graph |    | parallel dispatch  |    | pipeline state   |     |
|  +--------+----------+    +--------+-----------+    +--------+----------+    |
|           |                        |                         |               |
|           v                        v                         v               |
|  +-------------------+    +--------------------+    +-------------------+     |
|  | RetryEngine       |    | ApprovalGateMgr    |    | CostEnforcer     |     |
|  | Exp. backoff,     |    | T0-T3 tier check,  |    | Pre-invoke check |     |
|  | max 3 retries     |    | Slack notify, wait |    | 4-level ceiling  |     |
|  +-------------------+    +--------------------+    +-------------------+     |
|           |                        |                         |               |
|           v                        v                         v               |
|  +-------------------+    +--------------------+    +-------------------+     |
|  | SelfHealEngine    |    | BranchRouter       |    | ResultCollector   |     |
|  | Detect failure    |    | Conditional fan-out|    | Aggregate outputs |     |
|  | mode, auto-fix    |    | Parallel branches  |    | Write to reports/ |     |
|  +-------------------+    +--------------------+    +-------------------+     |
+==============================================================================+
```

### 3.4 Orchestration Levels (L0 - L5)

```
+----------------------------------------------------------------------+
|  L5: HUMAN ESCALATION                                                |
|  Approval gates, Slack notifications, manual override                |
+----------------------------------------------------------------------+
        |
+----------------------------------------------------------------------+
|  L4: FLEET (scaling + health)                                        |
|  G5 Fleet Manager, canary slots, health checks, circuit breaker      |
+----------------------------------------------------------------------+
        |
+----------------------------------------------------------------------+
|  L3: TEAM (parallel / conditional)                                   |
|  TeamOrchestrator, 9+5 team YAMLs, fan-out / fan-in                  |
+----------------------------------------------------------------------+
        |
+----------------------------------------------------------------------+
|  L2: PIPELINE (sequential chain)                                     |
|  PipelineRunner, DAG execution, checkpoint/resume                    |
+----------------------------------------------------------------------+
        |
+----------------------------------------------------------------------+
|  L1: SUBAGENT SPAWN                                                  |
|  Parent agent delegates to child agent via SDK                       |
+----------------------------------------------------------------------+
        |
+----------------------------------------------------------------------+
|  L0: AGENT LOOP                                                      |
|  Single agent: SDK query() -> perception -> planning -> tool ->      |
|  output -> safety check -> emit audit event                          |
+----------------------------------------------------------------------+
```

### 3.5 Storage Layer — PostgreSQL Tables

```
+==============================================================================+
|                              POSTGRESQL                                       |
|                                                                              |
|  EXISTING TABLES                          TO BUILD                           |
|  +---------------------+                 +-----------------------------+     |
|  | agent_registry      |                 | session_context     [P1]   |     |
|  |   agent_id (PK)     |                 |   session_id (PK)          |     |
|  |   version, status   |                 |   project_id, data (JSONB) |     |
|  |   archetype, phase  |                 |   created_at, expires_at   |     |
|  +---------------------+                 +-----------------------------+     |
|  | cost_metrics        |                 | approval_requests   [P2]   |     |
|  |   agent_id, project |                 |   request_id (PK)          |     |
|  |   tokens_in/out     |                 |   pipeline_run_id          |     |
|  |   cost_usd, ts      |                 |   approver, status         |     |
|  +---------------------+                 |   requested_at, decided_at |     |
|  | audit_events        |                 +-----------------------------+     |
|  |   (IMMUTABLE)       |                 | pipeline_checkpoints [P2]  |     |
|  |   13 fields, JSONL  |                 |   checkpoint_id (PK)       |     |
|  |   INSERT-only       |                 |   pipeline_run_id          |     |
|  +---------------------+                 |   step_index, state (JSONB)|     |
|  | pipeline_runs       |                 +-----------------------------+     |
|  |   run_id (PK)       |                 | knowledge_exceptions [P3]  |     |
|  |   project_id, status|                 |   exception_id (PK)        |     |
|  |   started/completed |                 |   tier (client/stack/univ) |     |
|  +---------------------+                 |   pattern, resolution      |     |
|  | pipeline_steps      |                 |   promoted_from, promoted_to|    |
|  |   step_id, run_id   |                 +-----------------------------+     |
|  |   agent_id, status  |                                                     |
|  |   input/output hash |                                                     |
|  +---------------------+                                                     |
|                                                                              |
|  ROW-LEVEL SECURITY (RLS)                                                    |
|  All tables enforce project_id-based isolation via RLS policies.             |
|  Dashboard queries execute with role = 'app_reader' scoped to project_id.    |
+==============================================================================+
```

### 3.6 Config Resolution Pipeline

```
  +------------------+     +------------------+     +------------------+
  | 1. Archetype     |     | 2. Mixins        |     | 3. Agent         |
  |    YAML          +---->+    (optional)     +---->+    manifest.yaml |
  | (7 base configs) |     | (shared traits)  |     | (per-agent cfg)  |
  +------------------+     +------------------+     +--------+---------+
                                                             |
                                                             v
                                                    +--------+---------+
                                                    | 4. Client        |
                                                    |    Profile YAML  |
                                                    | (per-engagement) |
                                                    +--------+---------+
                                                             |
                                                             v
                                                    +--------+---------+
                                                    | SchemaValidator  |
                                                    | JSON Schema      |
                                                    | 2020-12 check    |
                                                    +--------+---------+
                                                             |
                                                             v
                                                    +--------+---------+
                                                    | ClaudeAgentOpts  |
                                                    | Final resolved   |
                                                    | runtime config   |
                                                    +------------------+
```

---

## 4. Tech Stack Decisions

| #  | Decision              | Choice                              | Alternatives Considered                  | Rationale                                                                                                                                                         | Trade-offs Accepted                                                                                          |
| -- | --------------------- | ----------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 1  | Language              | Python 3.12                         | Go, TypeScript, Rust                     | Claude Agent SDK is Python-native. Python dominates the AI/ML ecosystem with mature async support (asyncio). 3.12 brings performance improvements and better typing. | Slower single-thread execution than Go/Rust. GIL limits true parallelism (mitigated by asyncio for I/O-bound agent work). |
| 2  | LLM SDK               | Claude Agent SDK (claude_agent_sdk) | LangChain, LlamaIndex, raw Anthropic API | First-party SDK with native tool use, streaming, and agent lifecycle hooks. No abstraction overhead or version churn from third-party frameworks.                  | Vendor lock-in to Anthropic. No multi-provider fallback. LangChain offers broader model support but adds complexity and abstraction leaks. |
| 3  | Database              | PostgreSQL 15+                      | MongoDB, DynamoDB, SQLite                | ACID transactions for cost enforcement and audit immutability. Row-Level Security for multi-tenant isolation. JSONB for flexible agent state. Battle-tested at scale. | Requires schema migrations. No native horizontal sharding (mitigated: single-instance sufficient at v1 scale). More operational overhead than DynamoDB. |
| 4  | Async Framework       | asyncio (stdlib)                    | threading, Celery, Ray                   | All agent work is I/O-bound (API calls, DB queries). asyncio is stdlib with zero dependency overhead. Celery adds broker complexity (Redis/RabbitMQ) not yet needed. | No built-in distributed task queue. No worker isolation. At scale, Celery or Ray would provide better fault isolation and horizontal scaling. |
| 5  | Dashboard             | Streamlit                           | React SPA, Grafana, Retool               | Rapid prototyping in Python — the team is Python-native. No frontend build pipeline. Sufficient for 5 internal personas at v1 scale.                              | Not suitable for high-concurrency production UI. No fine-grained component control. Will need replacement at 10x scale. No mobile responsiveness. |
| 6  | Config Format         | YAML manifests (declarative)        | JSON, TOML, Pydantic-only models         | YAML is human-readable for the 9-subsystem agent manifest. Supports comments for documentation inline. Anchors and merge keys enable archetype inheritance.       | YAML parsing pitfalls (Norway problem, implicit typing). Mitigated by strict JSON Schema validation layer. Slightly slower to parse than TOML. |
| 7  | Schema Validation     | JSON Schema 2020-12                 | Pydantic v2, protobuf, Zod               | Language-agnostic schema definition. Validates YAML manifests before Python touches them. Reusable by CI, editors, and future non-Python tooling.                 | More verbose than Pydantic. No automatic Python class generation (mitigated: ManifestLoader handles hydration). Less type-safe at runtime than Pydantic. |
| 8  | CI/CD                 | GitHub Actions                      | GitLab CI, Jenkins, CircleCI             | Repository is on GitHub. Native integration with PR checks, matrix builds, and secrets. No self-hosted infrastructure required.                                    | Vendor lock-in to GitHub. YAML-based workflow config can become complex. Less flexible than self-hosted Jenkins for custom build environments. |
| 9  | Infrastructure as Code| AWS CDK (Python)                    | Terraform, Pulumi, CloudFormation        | CDK uses Python — same language as the application. Generates CloudFormation under the hood. Type-safe infrastructure definitions.                                 | AWS-only. Less community adoption than Terraform. CDK constructs can have surprising defaults. Terraform is cloud-agnostic but uses HCL. |
| 10 | Authentication        | JWT with tenant_id claim            | Session cookies, API keys only, OAuth2/OIDC | Stateless auth for API Server. tenant_id claim enables RLS enforcement at the application layer. Standard JWT libraries available in Python.                      | Requires token refresh logic. No built-in revocation without a denylist. Session cookies would be simpler for dashboard-only auth but don't work for API clients. |
| 11 | Message Passing       | Typed envelope (in-process asyncio) | RabbitMQ, Redis Streams, Kafka           | At v1 scale (single process, <50 concurrent agents), an in-process async queue with typed envelopes is sufficient. Zero infrastructure overhead.                  | No persistence of in-flight messages. No cross-process routing. Must migrate to distributed queue at scale. Single point of failure. |
| 12 | Report Output         | File system (reports/{project_id}/) | S3/object storage, database BLOBs        | Simplest option for v1. Agents write Markdown files to disk. Easy to inspect, diff, and commit to Git.                                                            | Not durable across host failures. Not accessible from multiple nodes. Will need object storage migration for multi-instance deployment. |

---

## 5. Cross-Cutting Concerns

### 5.1 Authentication and Authorization

**API Server Authentication:**
- External API clients authenticate via JWT bearer tokens issued by the platform's auth endpoint.
- Each JWT contains a `tenant_id` claim, a `project_id` claim, and a `role` claim (one of: `admin`, `operator`, `viewer`).
- Token lifetime: 1 hour. Refresh tokens: 24 hours. Signing algorithm: RS256 with platform-managed key pair.
- All API endpoints validate the JWT signature, expiry, and claims before processing.

**Agent-to-Agent Authentication:**
- Agents authenticate to the Claude API using a shared `ANTHROPIC_API_KEY` environment variable.
- Agent-to-agent communication uses the `trust_chain` field in the message envelope. Every message carries the full chain of agents that have handled it, from the originating external trigger through every intermediary.
- The `TrustChainValidator` component verifies that the `from_agent` field matches a registered agent in `agent_registry` and that the trust chain is acyclic.

**Dashboard Authentication:**
- Streamlit dashboard uses session-based authentication with JWT tokens stored in browser session state.
- Role-based access: Priya/Marcus (admin) see all projects; David/Sarah (operator) see assigned projects; Lisa (viewer) sees audit data only.

**Authorization Model:**

| Role     | Pipeline Trigger | Agent Deploy | Cost Config | Audit Read | Approval Gate |
| -------- | ---------------- | ------------ | ----------- | ---------- | ------------- |
| admin    | Yes              | Yes          | Yes         | Yes        | Yes           |
| operator | Yes              | No           | No          | Own project| Yes           |
| viewer   | No               | No           | No          | Yes        | No            |

### 5.2 Multi-Tenancy

**Isolation Strategy: Namespace-based with Row-Level Security**

- Every data record includes `project_id` and `client_id` columns.
- PostgreSQL Row-Level Security (RLS) policies enforce that queries from the application layer can only access rows matching the session's `project_id`.
- The API Server sets `SET LOCAL app.current_project_id = '<project_id>'` on every database connection before executing queries. RLS policies reference `current_setting('app.current_project_id')`.
- Per-client configuration profiles (stored as YAML in `knowledge/client/{client_id}/profile.yaml`) control autonomy tier overrides, approval gate assignments, notification preferences, and budget allocations.
- Pipeline state, session context, and cost metrics are all partitioned by `project_id`.
- File-system outputs are isolated under `reports/{project_id}/`.

**Isolation Guarantees:**
- A cost spike in Project A cannot consume Project B's budget (enforced by `CostEnforcer` checking project-level ceilings).
- A pipeline failure in Project A cannot block Project B's pipeline (separate pipeline_run records, independent DAG execution).
- Audit queries for Project A never return Project B's records (RLS enforcement).

### 5.3 Observability

**Audit Trail (13-field JSONL):**

Every agent invocation produces an immutable audit record in the `audit_events` table:

| Field             | Type      | Description                                    |
| ----------------- | --------- | ---------------------------------------------- |
| timestamp         | ISO 8601  | When the invocation started                    |
| agent_id          | string    | Agent identifier (e.g., `D1-roadmap-generator`)|
| agent_version     | string    | Semantic version of the agent                  |
| project_id        | string    | Project namespace                              |
| invocation_id     | UUID      | Unique identifier for this invocation          |
| input_hash        | SHA-256   | Hash of the input payload (not the raw input)  |
| output_hash       | SHA-256   | Hash of the output payload                     |
| cost_usd          | decimal   | Actual cost of Claude API calls                |
| latency_ms        | integer   | Wall-clock duration of the invocation          |
| quality_score     | float     | Rubric-based quality score (0.0 - 10.0)        |
| autonomy_tier     | enum      | T0, T1, T2, or T3                              |
| approval_status   | enum      | not_required, pending, approved, rejected       |
| error_details     | JSONB     | Null on success; structured error on failure    |

The `audit_events` table is INSERT-only. No UPDATE or DELETE operations are permitted (enforced by database trigger).

**Structured Logging:**
- All components emit structured JSON logs to stdout.
- Log fields: `timestamp`, `level`, `component`, `agent_id`, `project_id`, `correlation_id`, `message`, `extra`.
- Log level configurable via `LOG_LEVEL` environment variable (default: `INFO`).
- Correlation ID propagated through the entire request chain via the message envelope's `correlation_id` field.

**Cost Metrics:**
- Real-time cost tracking in `cost_metrics` table, aggregated by agent, project, and day.
- Dashboard widgets: daily burn rate, per-project spend, per-agent spend, budget utilization percentage.
- Alerting: Slack notification at 80% of any budget ceiling (fleet, project, agent).

**OpenTelemetry (Planned - P5):**
- `OtelInstrumentation` module will add distributed tracing spans to every agent invocation.
- Traces will propagate through pipeline steps, linking parent pipeline span to child agent spans.
- Export to Jaeger or OTLP-compatible backend.

### 5.4 Error Handling

**Envelope-Based Error Propagation:**

Errors are communicated via the message envelope's response format:

```json
{
    "envelope_id": "uuid",
    "correlation_id": "uuid",
    "from_agent": "D5-arch-generator",
    "to_agent": "G4-team-orchestrator",
    "timestamp": "2026-03-23T14:30:00Z",
    "payload": {
        "mode": "error",
        "data": {
            "error_code": "BUDGET_EXCEEDED",
            "error_message": "Agent D5 invocation would exceed project ceiling ($20)",
            "retryable": false,
            "context": {
                "current_spend": 19.85,
                "projected_cost": 0.45,
                "ceiling": 20.00
            }
        }
    }
}
```

**Retry Strategy:**
- Transient errors (API timeout, rate limit, 5xx from Claude API): automatic retry with exponential backoff.
- Backoff formula: `min(base_delay * 2^attempt, max_delay)` where `base_delay=1s`, `max_delay=30s`, `max_attempts=3`.
- Non-transient errors (budget exceeded, schema validation failure, PII detected): no retry; escalate to orchestrator.

**Circuit Breaker:**
- Per-agent circuit breaker with three states: CLOSED (normal), OPEN (failing), HALF-OPEN (testing recovery).
- Threshold: 5 consecutive failures within 60 seconds triggers OPEN state.
- OPEN state duration: 30 seconds. After 30s, transitions to HALF-OPEN and allows one test invocation.
- If HALF-OPEN invocation succeeds: return to CLOSED. If it fails: return to OPEN for another 30s.

**Fail-Safe Budget Enforcement:**
- If the PostgreSQL `cost_metrics` table is unreachable, all agent invocations are BLOCKED (fail-closed, not fail-open).
- Rationale: unmetered execution is worse than halted execution. Budget integrity is non-negotiable.

**Pipeline Failure Handling:**
1. Step fails after all retries exhausted.
2. Pipeline Orchestrator saves checkpoint at the last successful step.
3. Self-heal engine inspects the failure mode. If it matches a known pattern (e.g., test failure with fixable assertion), it dispatches an auto-fix agent.
4. If self-heal succeeds, the step is retried one more time.
5. If self-heal fails or is not applicable, the pipeline pauses and notifies the operator via Slack.
6. Operator can resume from checkpoint without re-executing completed steps.

---

## 6. Data Flow Diagram

The following diagram traces the 12-document generation pipeline from client brief to completed document bundle. This is the platform's primary value-delivering workflow.

```
CLIENT BRIEF (pasted by David via Streamlit)
    |
    v
+---+-------------------+
| API Server             |
| POST /pipeline/trigger |
| Validates brief,       |
| creates pipeline_run   |
+---+-------------------+
    |
    v
+---+-------------------+         +---------------------+
| G4 Team Orchestrator   |         | cost_metrics (PG)   |
| Reads team YAML DAG    +-------->+ Pre-check: $25      |
| Resolves agent configs |         | project ceiling OK? |
+---+-------------------+         +----------+----------+
    |                                         |
    | (if budget OK)                          | (if budget exceeded)
    v                                         v
+---+-------------------+               PIPELINE BLOCKED
| PHASE 1: Sequential   |               Notify David via Slack
|                        |
|  Step 1: D1 Roadmap   |
|    Input: client brief |
|    Output: ROADMAP.md  |
|    -> SessionStore     +--------> session_context (PG)
|                        |          {session_id, roadmap_data}
|  Step 2: D3 CLAUDE.md |
|    Input: brief +      |
|           roadmap      |
|    Output: CLAUDE.md   |
|    -> SessionStore     |
|                        |
|  Step 3: D2 PRD        |
|    Input: brief +      |
|      roadmap + claude  |
|    Output: PRD.md      |
|    -> SessionStore     |
|                        |
|  Step 4: D4 Feature    |
|    Catalog             |
|    Input: PRD          |
|    Output: FEAT-CAT.md |
|                        |
|  Step 5: D9 Backlog    |
|    Input: PRD + feat   |
|    Output: BACKLOG.md  |
+---+-------------------+
    |
    v
+---+-------------------+
| PHASE 2: Sequential   |
|                        |
|  Step 6: D5 Arch       |
|    Input: PRD + feat + |
|           backlog      |
|    Output: ARCH.md     |
|                        |
+---+---+---+---+-------+
    |       |
    |       +------- APPROVAL GATE (T2) -------+
    |               Sarah Kim notified          |
    |               via Slack                   |
    |               Waits up to 15 min (P95)    |
    |               If approved: continue       |
    |               If rejected: pipeline halts |
    |               If timeout: escalate        |
    +<--------------+                           |
    |               (approved)                  |
    v                                           |
+---+-------------------+                      |
| PHASE 3: Parallel     |                      |
|                        |                      |
|  +-------+  +-------+ |                      |
|  | D6    |  | D7    | |                      |
|  | Data  |  | API   | |                      |
|  | Model |  | Contr.| |                      |
|  +---+---+  +---+---+ |                      |
|      |          |      |                      |
|      +----+-----+      |                      |
|           |             |                      |
+---+-------+-------------+                     |
    |                                            |
    v                                            |
+---+-------------------+                       |
| PHASE 4: Sequential   |                       |
|                        |                       |
|  Step 9: D8 Enforce-  |                       |
|    ment Scaffold       |                       |
|    Input: all upstream |                       |
|    Output: ENFORCE.md  |                       |
+---+-------------------+                       |
    |                                            |
    v                                            |
+---+-------------------+                       |
| PHASE 5: Parallel     |                       |
|                        |                       |
|  +-------+  +-------+ |                       |
|  | D9    |  | D10   | |                       |
|  | Qual  |  | Test  | |                       |
|  | Spec  |  | Strat | |                       |
|  +---+---+  +---+---+ |                       |
|      |          |      |                       |
|      +----+-----+      |                       |
|           |             |                       |
+---+-------+-------------+                      |
    |                                             |
    v                                             |
+---+-------------------+                        |
| PHASE 6: Sequential   |                        |
|                        |                        |
|  Step 12: D11 Design  |                        |
|    Spec                |                        |
|    Input: all upstream |                        |
|    Output: DESIGN.md   |                        |
+---+-------------------+                        |
    |                                             |
    v                                             |
+---+-------------------+    +-------------------+
| ResultCollector        |    | audit_events (PG) |
| Aggregate 12 docs     +--->+ 12 audit records  |
| Write to reports/      |    | (1 per agent)     |
|   {project_id}/        |    +-------------------+
+---+-------------------+
    |
    v
+---+-------------------+    +-------------------+
| Git Commit             |    | Slack             |
| Commit 12 docs to      +--->+ Notify David:    |
| project repo branch   |    | "Pipeline done,   |
+---+-------------------+    |  12 docs, $18.50, |
    |                         |  28 min"          |
    v                         +-------------------+
+---+-------------------+
| Dashboard Update       |
| Pipeline status: GREEN |
| David downloads bundle |
+------------------------+
```

**Data Format at Each Stage:**

| Stage           | Format                 | Storage                           |
| --------------- | ---------------------- | --------------------------------- |
| Client Brief    | Raw text (Markdown)    | Pipeline input, session_context   |
| Agent Input     | Message envelope (JSON)| In-memory (asyncio queue)         |
| Agent Output    | Message envelope (JSON)| session_context (JSONB), reports/ |
| Audit Record    | 13-field JSONL         | audit_events (immutable)          |
| Cost Record     | Decimal USD            | cost_metrics                      |
| Final Documents | Markdown files         | reports/{project_id}/, Git repo   |

**Human Gates in the Pipeline:**

| Gate          | Location        | Tier | Approver        | Timeout  | Escalation          |
| ------------- | --------------- | ---- | --------------- | -------- | ------------------- |
| Architecture  | After Step 6    | T2   | Sarah Kim       | 15 min   | David Chen          |
| Deployment    | Before deploy   | T2   | Priya Mehta     | 15 min   | Marcus Johnson      |

---

## 7. What I'd Do Differently at 10x Scale

The following architectural decisions are correct for v1.0 (single-team, <50 concurrent agents, <10 projects) but would need replacement at 10x scale (500 agents, 100 projects, 50 concurrent users).

### 7.1 Single PostgreSQL Instance --> Sharded PostgreSQL or Aurora

**What breaks:** A single PostgreSQL instance handles all reads and writes: audit events, cost metrics, session context, pipeline state. At 10x scale, the `audit_events` table alone would see ~500K INSERTs/day. Cost enforcement queries (which run before every agent invocation) would contend with audit writes.

**Why:** PostgreSQL vertical scaling has a ceiling. Write amplification from JSONB columns and immutable audit table bloat will degrade performance.

**Replace with:** Amazon Aurora PostgreSQL with read replicas for dashboard queries. Partition `audit_events` by month. Consider Aurora Serverless v2 for auto-scaling. For extreme write throughput, offload audit events to a write-optimized store (TimescaleDB or ClickHouse) with async replication from the primary.

### 7.2 In-Process Pipeline Orchestrator --> Distributed Task Queue

**What breaks:** The Pipeline Orchestrator runs as a single asyncio process. At 10x, 100 concurrent pipelines with parallel branches would exhaust the event loop. A crash kills all in-flight pipelines. No horizontal scaling.

**Why:** asyncio queues are in-memory with no persistence. If the process dies, all in-flight messages and pipeline state are lost (checkpoints survive in PostgreSQL, but the orchestration state does not).

**Replace with:** Celery with Redis broker or Temporal.io for workflow orchestration. Temporal provides durable execution, automatic retry, and visibility into running workflows. Each pipeline step becomes a Temporal activity with built-in checkpoint semantics, eliminating the custom `PipelineCheckpoint` store.

### 7.3 Streamlit Dashboard --> React SPA with API Backend

**What breaks:** Streamlit re-runs the entire script on every interaction. At 10x users (50 concurrent dashboard sessions), Streamlit's single-threaded execution model creates contention. No fine-grained state management, no optimistic updates, no WebSocket push for real-time pipeline progress.

**Why:** Streamlit is designed for data exploration prototypes, not production multi-user dashboards. It lacks authentication middleware, route-level caching, and component-level rendering control.

**Replace with:** React SPA (Next.js or Vite) backed by the existing aiohttp API Server. WebSocket connection for real-time pipeline progress. Role-based route guards. Server-side rendering for audit reports. Component library (shadcn/ui or similar) for consistent UI.

### 7.4 File-Based Report Output --> Object Storage (S3)

**What breaks:** Reports are written to the local filesystem at `reports/{project_id}/`. At 10x, multiple pipeline orchestrator instances cannot share a local filesystem. No durability guarantees against disk failure. No CDN for client access. No versioning.

**Why:** Local filesystem is a single-host constraint. It prevents horizontal scaling of the pipeline orchestrator and dashboard.

**Replace with:** Amazon S3 with per-project prefixes (`s3://asdlc-reports/{client_id}/{project_id}/`). Enable S3 versioning for audit trail of document revisions. Serve via CloudFront presigned URLs for client access. Lifecycle policies to archive old reports to Glacier.

### 7.5 Single-Region Deployment --> Multi-Region Active-Passive

**What breaks:** All infrastructure runs in a single AWS region. A regional outage (which has happened historically) takes down the entire platform. No geographic locality for clients in different regions.

**Why:** Multi-region adds complexity: database replication lag, split-brain risk, global load balancing, and cross-region cost. At v1 scale with a single team, this complexity is not justified.

**Replace with:** Active-passive multi-region with Aurora Global Database for PostgreSQL replication. API Server behind Route 53 with health-check failover. S3 Cross-Region Replication for reports. Stateless API servers in the passive region can serve reads immediately; writes failover requires Aurora global failover (typically <1 minute). Accept eventual consistency on reads during failover.

---

*End of document.*
