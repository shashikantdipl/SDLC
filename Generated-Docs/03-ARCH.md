# ARCH -- Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 03 of 24 | Status: Draft

---

## Architectural Philosophy: Full-Stack-First

This architecture treats THREE interface layers as equal citizens. No interface is a wrapper around another. All three connect to a single **Shared Service Layer** that owns every piece of business logic.

```
                 +-----------------+
                 |  AI Clients     |
                 |  (Claude Code,  |
                 |   Cursor, etc.) |
                 +-------+---------+
                         |
                    MCP Protocol
                    (stdio / streamable-http)
                         |
                 +-------v---------+
                 |  MCP Servers    |         +------------------+
                 |  (3 servers)    |         |  Browser Users   |
                 +-------+---------+         |  (Anika, David,  |
                         |                   |   Fatima, Jason)  |
                         |                   +--------+---------+
                         |                            |
                         |                       HTTP (port 8501)
                         |                            |
                         |                   +--------v---------+
                         |                   | Streamlit        |
                         |                   | Dashboard        |
                         |                   +--------+---------+
                         |                            |
                         |                     REST API calls
                         |                     (localhost:8080)
                         |                            |
                 +-------v---------+         +--------v---------+
                 |                 |         |                  |
                 |   Shared        <---------+   REST API       |
                 |   Service       |         |   (aiohttp)      |
                 |   Layer         +--------->                  |
                 |                 |         +------------------+
                 +-------+---------+
                         |
              +----------+----------+
              |                     |
     +--------v-------+   +--------v--------+
     |  PostgreSQL     |   |  LLM Providers  |
     |  Database       |   |  (Anthropic /   |
     +----------------+   |   OpenAI /       |
                          |   Ollama)        |
                          +-----------------+
```

**Key Insight:** MCP tool handlers and REST route handlers are thin adapters. They validate input, call a shared service method, and format the response for their protocol. Zero business logic lives in the interface layer.

---

## 1. System Context (C4 Level 1)

```
+-------------------+                                        +-------------------+
| <<Person>>        |                                        | <<Person>>        |
| Priya (Platform)  |   MCP (stdio)                         | Marcus (Delivery) |
| Jason (Tech Lead) +----------+                  +---------+ Jason (Tech Lead)  |
+-------------------+          |                  |         +-------------------+
                               |                  |
                        +------v------------------v------+
                        |                                |
                        |    AGENTIC SDLC PLATFORM       |
                        |                                |
                        |  48 agents | 7 SDLC phases     |
                        |  12-doc pipeline | $25 ceiling  |
                        |  Cost governance | Audit trail  |
                        |  Approval gates | Knowledge DB  |
                        |                                |
                        +--+-----+-----+-----+-----+----+
                           |     |     |     |     |
              +------------+     |     |     |     +------------+
              |                  |     |     |                  |
   +----------v---+    +---------v-+  +v---------+   +---------v--+
   | <<External>> |    |<<External>|  |<<External|   |<<External>>|
   | LLM Providers|    | PostgreSQL|  | Slack    |   | PagerDuty  |
   | (Anthropic / |    | Database  |  | Webhooks |   | Alerts     |
   |  OpenAI /    |    | TCP/SQL   |  | HTTPS    |   | HTTPS      |
   |  Ollama)     |    | All state |  | Notify + |   | Incident   |
   | HTTPS/REST   |    |           |  | Approvals|   | Escalation |
   | LLM calls    |    |           |  |          |   |            |
   +--------------+    +-----------+  | Approvals|   | Escalation |
                                      +----------+   +------------+
              |
   +----------v---+
   | <<Person>>   |     HTTP (browser)
   | Anika (Eng)  +------------------------+
   | David (Ops)  |                        |
   | Fatima (Comp)|         +---+          |
   | Jason (Lead) |         |   |     Dashboard
   +--------------+         +---+     (Streamlit)

   +-------------------+
   | <<External>>      |     HTTP (webhooks, scripts)
   | CI/CD Pipelines   +-----> REST API
   | Webhooks / Scripts|
   +-------------------+
```

**Actors and Interfaces:**

| Actor | Primary Interface | Protocol | Purpose |
|-------|------------------|----------|---------|
| Priya (Platform Engineer) | MCP via Claude Code | stdio / streamable-http | Agent management, fleet diagnostics, cost queries |
| Marcus (Delivery Lead) | MCP via Claude Code | stdio / streamable-http | Pipeline triggering, status checks, output retrieval |
| Anika (Engineering Lead) | Dashboard (Streamlit) | HTTP / browser | Approval reviews, quality monitoring, maturity tracking |
| David (DevOps Engineer) | Dashboard (Streamlit) | HTTP / browser | Fleet health, incident response, agent deployment |
| Fatima (Compliance Officer) | Dashboard (Streamlit) | HTTP / browser | Audit log review, compliance reports, PII verification |
| Jason (Tech Lead) | MCP + Dashboard | Both | Cross-interface: dev tasks via MCP, oversight via dashboard |
| CI/CD / Scripts | REST API | HTTP | Automated triggers, health checks, webhook receivers |

**External Systems:**

| System | Protocol | Data Flow |
|--------|----------|-----------|
| LLM Providers (Anthropic / OpenAI / Ollama) | HTTPS/REST (Anthropic, OpenAI) or HTTP localhost (Ollama) | Outbound: prompts + context. Inbound: completions + token usage. Provider selected via `LLM_PROVIDER` env var; routed through `sdk/llm/` abstraction layer |
| PostgreSQL | TCP/SQL | Bidirectional: all persistent state (agents, runs, audit, cost, sessions) |
| Slack | HTTPS webhooks | Outbound: approval notifications, budget alerts, fleet warnings |
| PagerDuty | HTTPS | Outbound: critical incident escalation (fleet down, budget runaway) |

---

## 2. Container Architecture (C4 Level 2)

| # | Container | Technology | Responsibility | Deployment | Port |
|---|-----------|-----------|----------------|------------|------|
| 1 | **MCP Server: Agents** (`agentic-sdlc-agents`) | Python 3.12, Claude Agent SDK MCP | Agent execution, pipeline trigger/status/resume, document retrieval | Process (stdio) or HTTP service | stdio or 8090 |
| 2 | **MCP Server: Governance** (`agentic-sdlc-governance`) | Python 3.12, Claude Agent SDK MCP | Cost queries, budget checks, audit log queries, approval gate actions | Process (stdio) or HTTP service | stdio or 8091 |
| 3 | **MCP Server: Knowledge** (`agentic-sdlc-knowledge`) | Python 3.12, Claude Agent SDK MCP | Exception search/create/promote, knowledge base queries | Process (stdio) or HTTP service | stdio or 8092 |
| 4 | **REST API** | Python 3.12, aiohttp | HTTP endpoints for dashboard and external integrations; thin adapter over shared services | Single async process | 8080 |
| 5 | **Streamlit Dashboard** | Python 3.12, Streamlit | Visual monitoring, approval workflows, compliance reports, fleet controls | Streamlit server | 8501 |
| 6 | **Agent Runtime** | Python 3.12, LLMProvider abstraction (`sdk/llm/`), asyncio | Execution environment for 48 agents across 7 SDLC phases; manages agent lifecycle and orchestration levels L0-L4. LLM-agnostic via `sdk/llm/` provider layer (Anthropic, OpenAI, Ollama) | In-process (spawned by services) | N/A |
| 9 | **LLM Provider Layer** (`sdk/llm/`) | Python 3.12, Abstract `LLMProvider` interface | Routes LLM calls to configured provider. Components: `provider.py` (interface), `anthropic_provider.py`, `openai_provider.py`, `ollama_provider.py`, `factory.py` (instantiation). Provider selected via `LLM_PROVIDER` env var | In-process (library) | N/A |
| 7 | **PostgreSQL Database** | PostgreSQL 16 | All persistent state: agent_registry, pipeline_runs, audit_events, cost_events, approval_events, session_store, knowledge_entries | Managed instance | 5432 |
| 8 | **Background Workers** | Python 3.12, asyncio | Pipeline runner (DAG execution), cost aggregation (materialized view refresh), health check poller, knowledge promotion evaluator | Async tasks in event loop | N/A |

```
+------------------------------------------------------------------+
|                    AGENTIC SDLC PLATFORM                         |
|                                                                  |
|  +-----------+ +-----------+ +-----------+                       |
|  | MCP:      | | MCP:      | | MCP:      |                       |
|  | Agents    | | Governance| | Knowledge |                       |
|  | (8090)    | | (8091)    | | (8092)    |                       |
|  +-----+-----+ +-----+-----+ +-----+-----+                       |
|        |              |              |                            |
|        +--------------+--------------+                            |
|                       |                                          |
|                       v                                          |
|  +--------------------------------------------+                  |
|  |         SHARED SERVICE LAYER               |   +-----------+  |
|  |                                            |   | REST API  |  |
|  | PipelineService  | AgentService            |<--+ (aiohttp) |  |
|  | CostService      | AuditService            |   | (8080)    |  |
|  | ApprovalService  | KnowledgeService         |   +-----^-----+  |
|  | HealthService    | SessionService           |         |        |
|  +----------+------------------+--------------+         |        |
|             |                  |                        |        |
|  +----------v------+  +-------v--------+        +------+------+  |
|  | Agent Runtime   |  | Background     |        | Streamlit   |  |
|  | 48 agents       |  | Workers        |        | Dashboard   |  |
|  | L0-L4 orch      |  | (pipeline,     |        | (8501)      |  |
|  +-----------------+  |  cost, health) |        +-------------+  |
|                       +----------------+                         |
|                              |                                   |
+------------------------------+-----------------------------------+
                               |
                      +--------v--------+
                      |   PostgreSQL    |
                      |   (5432)       |
                      +----------------+
```

---

## 3. Shared Service Layer

This is THE central architectural pattern. Every operation flows through a shared service. MCP tool handlers and REST route handlers are thin adapters that:
1. Deserialize input (MCP tool arguments or HTTP request body)
2. Call the shared service method
3. Serialize the response (MCP tool result or HTTP JSON response)

No business logic, validation beyond input parsing, or database access exists in the interface layer.

### 3.1 PipelineService

**Module:** `sdk/services/pipeline_service.py`

| Method | Description | MCP Tool | REST Route |
|--------|-------------|----------|------------|
| `trigger(project_id, pipeline_id, input_data, gates)` | Validate input, create pipeline_run record, enqueue for execution | `trigger_pipeline` | `POST /api/v1/pipelines` |
| `get_status(run_id)` | Return current step, progress, cost, elapsed time | `check_pipeline_status` | `GET /api/v1/pipelines/{run_id}` |
| `list_runs(project_id, status, limit, offset)` | Paginated list of pipeline runs with filters | `list_pipeline_runs` | `GET /api/v1/pipelines` |
| `get_outputs(run_id)` | List generated documents with metadata (confidence, schema status) | `get_pipeline_outputs` | `GET /api/v1/pipelines/{run_id}/outputs` |
| `get_document(run_id, doc_id)` | Fetch a specific generated document's content | `get_document` | `GET /api/v1/pipelines/{run_id}/outputs/{doc_id}` |
| `resume(run_id)` | Resume from last checkpoint after failure | `resume_pipeline` | `POST /api/v1/pipelines/{run_id}/resume` |
| `cancel(run_id)` | Cancel a running pipeline, preserve completed steps | `cancel_pipeline` | `POST /api/v1/pipelines/{run_id}/cancel` |
| `get_logs(run_id, step)` | Detailed execution logs for debugging | `get_pipeline_logs` | `GET /api/v1/pipelines/{run_id}/logs` |

### 3.2 AgentService

**Module:** `sdk/services/agent_service.py`

| Method | Description | MCP Tool | REST Route |
|--------|-------------|----------|------------|
| `list_agents(phase, status, maturity)` | Enumerate agents with filters | `list_agents` | `GET /api/v1/agents` |
| `get_agent(agent_id)` | Full agent detail: config, health, cost, maturity | `query_agent` | `GET /api/v1/agents/{agent_id}` |
| `invoke(agent_id, input_data, project_id)` | Direct single-agent invocation outside pipeline | `invoke_agent` | `POST /api/v1/agents/{agent_id}/invoke` |
| `health_check(agent_id)` | Current health status and diagnostics | `check_agent_health` | `GET /api/v1/agents/{agent_id}/health` |
| `deploy_version(agent_id, version, canary_pct)` | Deploy new version to canary slot | -- | `POST /api/v1/agents/{agent_id}/deploy` |
| `rollback(agent_id)` | Rollback canary to previous stable version | -- | `POST /api/v1/agents/{agent_id}/rollback` |
| `promote(agent_id, maturity_level)` | Promote agent maturity tier | -- | `POST /api/v1/agents/{agent_id}/promote` |

### 3.3 CostService

**Module:** `sdk/services/cost_service.py`

| Method | Description | MCP Tool | REST Route |
|--------|-------------|----------|------------|
| `get_report(scope, scope_id, period)` | Cost breakdown at fleet/project/agent level | `get_cost_summary` | `GET /api/v1/cost/report` |
| `get_forecast(scope, scope_id, period)` | Projected spend based on current trajectory | `get_cost_forecast` | `GET /api/v1/cost/forecast` |
| `check_budget(scope, scope_id)` | Current budget utilization and remaining | `check_budget` | `GET /api/v1/cost/budget` |
| `record_spend(agent_id, project_id, tokens, cost_usd)` | Record a cost event (called internally by agent runtime) | -- | -- |
| `get_budget_alerts(scope, scope_id, period)` | List budget threshold breach events | -- | `GET /api/v1/cost/alerts` |

### 3.4 AuditService

**Module:** `sdk/services/audit_service.py`

| Method | Description | MCP Tool | REST Route |
|--------|-------------|----------|------------|
| `query_events(filters, limit, offset)` | Filtered audit trail query (13-field records) | `get_audit_log` | `GET /api/v1/audit/events` |
| `get_event(event_id)` | Single audit event with full detail | -- | `GET /api/v1/audit/events/{event_id}` |
| `get_summary(project_id, period)` | Aggregated audit statistics | `get_audit_summary` | `GET /api/v1/audit/summary` |
| `verify_integrity(start_date, end_date)` | Validate hash chain integrity over time range | -- | `POST /api/v1/audit/verify` |
| `generate_report(template, period, project_id)` | Generate compliance PDF from template | -- | `POST /api/v1/audit/reports` |
| `record_event(audit_record)` | Write 13-field JSONL audit record (called internally) | -- | -- |

### 3.5 ApprovalService

**Module:** `sdk/services/approval_service.py`

| Method | Description | MCP Tool | REST Route |
|--------|-------------|----------|------------|
| `create_request(run_id, step, agent_id, confidence, assignee)` | Create pending approval gate (called by pipeline runner) | -- | -- |
| `approve(gate_id, approver, note)` | Approve a pending gate with optional structured comment | `approve_gate` | `POST /api/v1/approvals/{gate_id}/approve` |
| `reject(gate_id, approver, comment)` | Reject with structured feedback (category, section, severity) | `reject_gate` | `POST /api/v1/approvals/{gate_id}/reject` |
| `list_pending(assignee, project_id)` | List all pending approval gates | `list_pending_approvals` | `GET /api/v1/approvals?status=pending` |
| `get_gate(gate_id)` | Full gate detail with document preview metadata | -- | `GET /api/v1/approvals/{gate_id}` |
| `escalate(gate_id)` | Escalate to backup reviewer after timeout | -- | `POST /api/v1/approvals/{gate_id}/escalate` |

### 3.6 KnowledgeService

**Module:** `sdk/services/knowledge_service.py`

| Method | Description | MCP Tool | REST Route |
|--------|-------------|----------|------------|
| `search_exceptions(query, tier, project_id)` | Search knowledge base with tier filtering | `search_exceptions` | `GET /api/v1/knowledge/search` |
| `create_exception(exception_data)` | Record a new exception/learning | `create_exception` | `POST /api/v1/knowledge/exceptions` |
| `promote(exception_id, target_tier)` | Promote exception from client to stack or universal | `promote_exception` | `POST /api/v1/knowledge/exceptions/{id}/promote` |
| `list_exceptions(tier, status, limit)` | List exceptions with filters | `list_exceptions` | `GET /api/v1/knowledge/exceptions` |
| `get_resolution(exception_id)` | Get resolution details and applicability assessment | -- | `GET /api/v1/knowledge/exceptions/{id}` |

### 3.7 HealthService

**Module:** `sdk/services/health_service.py`

| Method | Description | MCP Tool | REST Route |
|--------|-------------|----------|------------|
| `get_fleet_health()` | Fleet-wide health summary (agent counts by status, cost, pipelines) | `check_fleet_health` | `GET /api/v1/health/fleet` |
| `get_agent_health(agent_id)` | Individual agent health with diagnostics | `check_agent_health` | `GET /api/v1/health/agents/{agent_id}` |
| `get_system_health()` | System-level health (DB, LLM providers, workers) | -- | `GET /api/v1/health` |

### 3.8 SessionService

**Module:** `sdk/services/session_service.py`

| Method | Description | MCP Tool | REST Route |
|--------|-------------|----------|------------|
| `create_session(project_id, pipeline_id)` | Create namespaced session context | -- | -- |
| `get_context(session_id)` | Retrieve accumulated context for next agent | -- | -- |
| `append_context(session_id, agent_id, output)` | Add agent output to session (context accumulation) | -- | -- |
| `get_session(session_id)` | Session metadata and context summary | -- | `GET /api/v1/sessions/{session_id}` |

### Service Layer Guarantees

1. **Single Source of Truth:** All data reads go through services to PostgreSQL. No interface-specific caches that could drift.
2. **Transaction Boundaries:** Each service method defines its own transaction scope. The interface layer never manages transactions.
3. **Error Uniformity:** Services raise typed exceptions (`BudgetExceededError`, `PipelineNotFoundError`, `GateAlreadyResolvedError`). Each interface layer maps these to its protocol's error format (MCP error codes, HTTP status codes, Streamlit error toasts).
4. **Async-First:** All service methods are `async def`. MCP handlers and aiohttp routes `await` them directly. Streamlit uses `asyncio.run()` bridge.

---

## 4. MCP Server Architecture

### 4.1 Server Layout

Three MCP servers, grouped by domain to keep tool namespaces manageable and allow independent scaling:

| Server | Tools | Domain | Personas |
|--------|-------|--------|----------|
| `agentic-sdlc-agents` | `trigger_pipeline`, `check_pipeline_status`, `get_pipeline_outputs`, `get_document`, `resume_pipeline`, `cancel_pipeline`, `get_pipeline_logs`, `list_agents`, `query_agent`, `invoke_agent`, `check_agent_health` | Agent execution, pipelines, documents | Priya, Marcus, Jason |
| `agentic-sdlc-governance` | `get_cost_summary`, `get_cost_forecast`, `check_budget`, `get_audit_log`, `get_audit_summary`, `approve_gate`, `reject_gate`, `list_pending_approvals`, `check_fleet_health` | Cost, audit, approvals, fleet health | Priya, Marcus, Jason, Anika (via MCP) |
| `agentic-sdlc-knowledge` | `search_exceptions`, `create_exception`, `promote_exception`, `list_exceptions` | Knowledge base, exception flywheel | Priya, Jason |

### 4.2 Transport Configuration

| Environment | Transport | Configuration |
|-------------|-----------|---------------|
| Local development | `stdio` | Claude Code spawns MCP server as child process. Configuration in `.claude/mcp.json` |
| Production / Team | `streamable-http` | MCP servers run as HTTP services on ports 8090-8092. TLS terminated at reverse proxy |
| CI/CD | `stdio` | Test harness spawns MCP server, sends tool calls, asserts responses |

### 4.3 Authentication

- **API key via environment variable:** `AGENTIC_SDLC_API_KEY`
- MCP servers read the key from environment on startup
- For stdio transport: key is set in the shell environment before launching
- For streamable-http transport: key is sent in the `Authorization` header
- All MCP tool calls are logged to `audit_events` with the authenticated identity

### 4.4 MCP Tool Contract Pattern

Every MCP tool handler follows this exact pattern:

```python
# In mcp_agents_server.py
@server.tool("trigger_pipeline")
async def handle_trigger_pipeline(
    project_id: str,
    pipeline_id: str,
    input_data: dict,
    gates: dict | None = None
) -> dict:
    """Trigger a document generation pipeline."""
    # 1. Input is already validated by MCP SDK schema
    # 2. Call shared service
    result = await pipeline_service.trigger(
        project_id=project_id,
        pipeline_id=pipeline_id,
        input_data=input_data,
        gates=gates
    )
    # 3. Return result (MCP SDK serializes to JSON)
    return result
```

No business logic. No database calls. No error handling beyond what the service raises.

### 4.5 Claude Code Configuration

```json
// .claude/mcp.json
{
  "mcpServers": {
    "agentic-sdlc-agents": {
      "command": "python",
      "args": ["-m", "mcp_servers.agents_server"],
      "env": {
        "AGENTIC_SDLC_API_KEY": "${AGENTIC_SDLC_API_KEY}",
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "agentic-sdlc-governance": {
      "command": "python",
      "args": ["-m", "mcp_servers.governance_server"],
      "env": {
        "AGENTIC_SDLC_API_KEY": "${AGENTIC_SDLC_API_KEY}",
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "agentic-sdlc-knowledge": {
      "command": "python",
      "args": ["-m", "mcp_servers.knowledge_server"],
      "env": {
        "AGENTIC_SDLC_API_KEY": "${AGENTIC_SDLC_API_KEY}",
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

---

## 5. Dashboard Architecture

### 5.1 Framework

**Streamlit** -- chosen for rapid development of data-centric operator UIs with Python-native integration. The dashboard is a consumer of the REST API; it makes zero direct database calls and imports zero shared service modules.

### 5.2 Pages

| Page | URL Path | Primary Persona | Key Components | REST Endpoints Consumed |
|------|----------|----------------|----------------|------------------------|
| **Fleet Health** | `/` | David (DevOps) | Agent status grid (green/yellow/red), cost utilization gauges, active pipeline count, pending gate count, system health indicators | `GET /api/v1/health/fleet`, `GET /api/v1/cost/report`, `GET /api/v1/pipelines?status=running` |
| **Cost Monitor** | `/cost` | David, Fatima | Budget utilization bars at fleet/project/agent, trend charts, forecast line, budget alert history | `GET /api/v1/cost/report`, `GET /api/v1/cost/forecast`, `GET /api/v1/cost/alerts` |
| **Pipeline Runs** | `/pipelines` | Marcus, Anika | Run list with status badges, step timeline, cost accumulation graph, document output list, filter by project/status/date | `GET /api/v1/pipelines`, `GET /api/v1/pipelines/{id}`, `GET /api/v1/pipelines/{id}/outputs` |
| **Audit Log** | `/audit` | Fatima | 13-field event table with column filters, drill-down to event detail, hash integrity indicator, PII detection filter, correlation trace | `GET /api/v1/audit/events`, `GET /api/v1/audit/summary`, `POST /api/v1/audit/verify` |
| **Approval Queue** | `/approvals` | Anika | Pending gates list with priority sort, document preview with side panels (input requirements + reasoning chain), approve/reject with structured comments, escalation timer | `GET /api/v1/approvals?status=pending`, `GET /api/v1/approvals/{id}`, `POST /api/v1/approvals/{id}/approve`, `POST /api/v1/approvals/{id}/reject` |

### 5.3 Data Refresh Strategy

| Strategy | Mechanism | Interval |
|----------|-----------|----------|
| Auto-poll | `st.experimental_fragment` with `run_every=30` | Every 30 seconds |
| Manual refresh | "Refresh" button in page header | On-demand |
| Critical pages (Fleet Health) | Shorter polling interval | Every 10 seconds |

### 5.4 Authentication

- **Session-based** via Streamlit's built-in auth (`st.experimental_user`)
- Session stores user identity for audit trail attribution
- Role-based page visibility: Compliance pages visible to all; Fleet Controls restricted to DevOps role

### 5.5 Dashboard Architecture Diagram

```
+-------------------------------------------------------------+
|                   STREAMLIT DASHBOARD                        |
|                                                              |
|  +------------------+  +------------------+                  |
|  | Fleet Health     |  | Cost Monitor     |                  |
|  | - Agent grid     |  | - Budget bars    |                  |
|  | - Cost gauges    |  | - Trend charts   |                  |
|  | - Pipeline count |  | - Forecast line  |                  |
|  +--------+---------+  +--------+---------+                  |
|           |                     |                            |
|  +--------+---------+  +--------+---------+  +-----------+   |
|  | Pipeline Runs    |  | Audit Log        |  | Approval  |   |
|  | - Run timeline   |  | - Event table    |  | Queue     |   |
|  | - Step progress  |  | - Hash verify    |  | - Preview |   |
|  | - Cost graph     |  | - PII filter     |  | - Actions |   |
|  +--------+---------+  +--------+---------+  +-----+-----+   |
|           |                     |                  |         |
|  +--------+---------------------+------------------+-----+   |
|  |              REST API Client (requests/httpx)         |   |
|  |  base_url: http://localhost:8080/api/v1               |   |
|  +---------------------------+---------------------------+   |
+------------------------------+-------------------------------+
                               |
                          HTTP requests
                               |
                      +--------v--------+
                      |    REST API     |
                      |   (aiohttp)    |
                      +--------+--------+
                               |
                      Shared Service Layer
```

---

## 6. Component Diagram (C4 Level 3)

Internal components within the Shared Service Layer and Agent Runtime:

```
+===========================================================================+
|                           SHARED SERVICE LAYER                            |
|                                                                           |
|  +-------------------+  +-------------------+  +--------------------+     |
|  | PipelineService   |  | AgentService      |  | CostService        |     |
|  | - trigger()       |  | - list_agents()   |  | - get_report()     |     |
|  | - get_status()    |  | - invoke()        |  | - check_budget()   |     |
|  | - resume()        |  | - health_check()  |  | - record_spend()   |     |
|  | - cancel()        |  | - deploy_version()|  | - get_forecast()   |     |
|  +--------+----------+  +--------+----------+  +--------+-----------+     |
|           |                      |                       |                |
|  +--------+----------+  +-------+----------+  +---------+----------+     |
|  | ApprovalService   |  | AuditService     |  | KnowledgeService   |     |
|  | - approve()       |  | - query_events() |  | - search()         |     |
|  | - reject()        |  | - record_event() |  | - create()         |     |
|  | - list_pending()  |  | - verify_chain() |  | - promote()        |     |
|  +-------------------+  | - gen_report()   |  +--------------------+     |
|                         +------------------+                              |
|  +-------------------+  +-------------------+                             |
|  | HealthService     |  | SessionService    |                             |
|  | - fleet_health()  |  | - create()        |                             |
|  | - agent_health()  |  | - get_context()   |                             |
|  | - system_health() |  | - append_context()|                             |
|  +-------------------+  +-------------------+                             |
+===========================================================================+

+===========================================================================+
|                            AGENT RUNTIME                                  |
|                                                                           |
|  SDK Core:                                                                |
|  +---------------+  +------------------+  +------------------+            |
|  | BaseAgent     |  | ManifestLoader   |  | SchemaValidator  |            |
|  | - query()     |  | - load(path)     |  | - validate()     |            |
|  | - pre_hooks() |  | - resolve_config |  | - validate_input |            |
|  | - post_hooks()|  |   (4-layer)      |  | - validate_output|            |
|  +-------+-------+  +------------------+  +------------------+            |
|          |                                                                |
|  +-------v-------+  +------------------+  +------------------+            |
|  | BaseHooks     |  | SessionStore     |  | CostStore        |            |
|  | - pii_scan()  |  | - read(key)      |  | - record()       |            |
|  | - audit_log() |  | - write(key,val) |  | - check_limit()  |            |
|  | - cost_check()|  | - accumulate()   |  | - get_remaining()|            |
|  +---------------+  +------------------+  +------------------+            |
|                                                                           |
|  Orchestration:                                                           |
|  +------------------+  +------------------+  +------------------+         |
|  | PipelineRunner   |  | TeamOrchestrator |  | ApprovalStore    |         |
|  | - execute_dag()  |  | - run_team()     |  | - create_gate()  |         |
|  | - checkpoint()   |  | - merge_results()|  | - wait_for_      |         |
|  | - resume_from()  |  | - parallel()     |  |   resolution()   |         |
|  +------------------+  +------------------+  +------------------+         |
|                                                                           |
|  +------------------+                                                     |
|  | Checkpoint       |                                                     |
|  | - save_state()   |                                                     |
|  | - load_state()   |                                                     |
|  | - list_checkpts()|                                                     |
|  +------------------+                                                     |
|                                                                           |
|  Enforcement:                                                             |
|  +------------------+  +------------------+  +------------------+         |
|  | RateLimiter      |  | CostController   |  | CircuitBreaker   |         |
|  | - acquire()      |  | - pre_invoke()   |  | - call()         |         |
|  | - release()      |  | - post_invoke()  |  | - record_failure |         |
|  | - configure()    |  | - hard_stop()    |  | - record_success |         |
|  +------------------+  +------------------+  | - is_open()      |         |
|                                              +------------------+         |
|                                                                           |
|  Evaluation:                          Communication:                      |
|  +------------------+                 +------------------+                |
|  | QualityScorer    |                 | Envelope         |                |
|  | - score_rubric() |                 | - 13-field typed |                |
|  | - check_golden() |                 |   message format |                |
|  | - check_advers() |                 | - serialize()    |                |
|  +------------------+                 | - validate()     |                |
|                                       +------------------+                |
|                                       +------------------+                |
|                                       | WebhookSender    |                |
|                                       | - send_slack()   |                |
|                                       | - send_pager()   |                |
|                                       +------------------+                |
+===========================================================================+
```

---

## 7. Tech Stack Decisions

| # | Decision | Choice | Alternatives Considered | Rationale | Trade-offs |
|---|----------|--------|------------------------|-----------|------------|
| 1 | **Language** | Python 3.12 | TypeScript, Go, Rust | Claude Agent SDK is Python-native; entire AI/ML ecosystem is Python; team expertise is Python | GIL limits CPU parallelism (mitigated by asyncio for I/O); runtime type safety weaker than Go/Rust |
| 2 | **REST Framework** | aiohttp | FastAPI, Flask, Django REST | Native asyncio without ASGI adapter; lightweight; matches async-first service layer | Smaller ecosystem than FastAPI; no auto-generated OpenAPI docs (we generate manually); less middleware ecosystem |
| 3 | **MCP SDK** | Claude Agent SDK (built-in MCP) | Custom MCP implementation, mcp-python | Official Anthropic SDK; maintained alongside Claude; tool/resource/prompt primitives built in | Tied to Anthropic's release cadence; fewer community extensions than standalone mcp-python |
| 15 | **LLM Provider Abstraction** | Abstract `LLMProvider` interface (`sdk/llm/provider.py`) + provider implementations + factory | Direct SDK imports in agents, single-provider hardcoding | Agents are LLM-agnostic; provider switch requires only env var change; tier-based model selection (`fast`/`balanced`/`powerful`) decouples agent logic from model names; Ollama enables free local dev | Additional abstraction layer; provider-specific features (e.g., Claude tool_use, GPT function_calling) must be normalized; slight latency overhead from factory dispatch |
| 4 | **MCP Transport** | stdio (dev) + streamable-http (prod) | SSE, WebSocket, gRPC | stdio is zero-config for Claude Code local dev; streamable-http is the MCP standard for networked deployment | stdio requires process-per-connection; streamable-http adds HTTP overhead vs raw TCP |
| 5 | **Dashboard Framework** | Streamlit | Grafana, Retool, React SPA, Dash | Pure Python; rapid prototyping; built-in auth; native charts; team does not need to maintain JS/TS frontend code | Limited customization vs React SPA; polling-based (no WebSocket push); single-threaded per session; harder to build complex interactive UIs |
| 6 | **Database** | PostgreSQL 16 | SQLite, MySQL, MongoDB, DynamoDB | JSONB for flexible audit records; RLS for multi-tenancy; materialized views for cost aggregation; ACID for budget enforcement | Operational overhead vs SQLite; requires managed instance; vertical scaling limits |
| 7 | **Shared Service Pattern** | Async service classes with DI | Repository pattern, CQRS, microservices | Services own all business logic; constructor injection of DB pool and config; testable via mock injection | Monolithic service layer; no independent scaling of read vs write paths |
| 8 | **Agent Orchestration** | asyncio.gather() + DAG runner | Celery, Temporal, Airflow, Prefect | Zero infrastructure dependency; DAG is defined in pipeline YAML; checkpoint/resume via PostgreSQL | No built-in retry/backpressure from a workflow engine; manual DAG implementation; no distributed execution across machines |
| 9 | **Message Format** | Typed Envelope (13-field dataclass) | Protobuf, Avro, plain JSON dict | Dataclass gives runtime validation; JSON-serializable for audit; no code generation step needed | No binary encoding (larger payloads); no cross-language schema; schema evolution requires manual migration |
| 10 | **Auth Strategy** | API key (MCP/REST) + session (dashboard) | OAuth2, JWT, mTLS | API key is simplest for internal tool; session auth is Streamlit-native; no external IdP dependency | No token expiration/rotation built in; API key is a shared secret; no fine-grained scopes |
| 11 | **CI/CD** | GitHub Actions | GitLab CI, Jenkins, CircleCI | Team already uses GitHub; native Python/PostgreSQL service containers; MCP test harness runs in CI | Vendor lock-in to GitHub; limited self-hosted runner control |
| 12 | **Observability** | 13-field JSONL audit + cost_metrics table + Python structlog | OpenTelemetry, Datadog, ELK stack | Self-contained within PostgreSQL; no external observability vendor dependency; audit records ARE the observability layer | No distributed tracing spans; no flame graphs; manual correlation vs automatic trace propagation; query performance degrades at very high audit volumes |
| 13 | **Schema Validation** | JSON Schema 2020-12 | Pydantic-only, Protobuf, Avro | Language-agnostic; MCP tools and REST both validate against same schema files; tooling ecosystem mature | Verbose schema definitions; no code generation; validation at runtime only |
| 14 | **Configuration Resolution** | 4-layer YAML (archetype > mixin > manifest > client) | Single config file, environment variables, etcd | Composable defaults; client-specific overrides without forking manifests; YAML is human-readable | Complex merge logic; 4 layers can be hard to debug; no live config reload |

---

## 8. Cross-Cutting Concerns

### 8.1 Authentication and Authorization

```
MCP Request Flow:
  Client sends tool call
  -> MCP Server reads AGENTIC_SDLC_API_KEY from env (stdio) or Authorization header (http)
  -> Middleware validates key against allowed_keys table
  -> Tool handler executes with authenticated identity
  -> Audit record includes identity

REST Request Flow:
  Client sends HTTP request with X-API-Key header
  -> aiohttp middleware extracts and validates key
  -> Route handler executes with authenticated identity
  -> Audit record includes identity

Dashboard Flow:
  User opens Streamlit app
  -> st.experimental_user provides session identity
  -> Dashboard includes identity in all REST API calls via X-User header
  -> REST API trusts dashboard-originated requests (internal network only)
```

**Authorization Model (v1.0):** Role-based, with three roles:
- `operator`: Full access to all MCP tools and REST endpoints
- `viewer`: Read-only access (GET endpoints, read MCP tools)
- `compliance`: Read access plus audit report generation

### 8.2 Multi-Tenancy (Project Isolation)

- **Scoping:** Every database table includes `project_id`. All service methods accept `project_id` and filter accordingly.
- **Row-Level Security:** PostgreSQL RLS policies enforce that queries scoped to a project cannot access rows from other projects. RLS policies are applied on `pipeline_runs`, `session_store`, `cost_events`, `audit_events`, `knowledge_entries`.
- **Session Isolation:** SessionStore namespaces keys by `project_id`. No cross-project context leakage.
- **Budget Isolation:** Each project has its own budget allocation (`project_budgets` table). Budget exhaustion in project A does not affect project B.
- **Failure Isolation:** Pipeline failures, agent errors, and circuit breaker trips are scoped per project. A runaway pipeline in one project cannot starve another.

### 8.3 Observability

**Audit Trail (13-field JSONL):**
```
{
  "envelope_id": "uuid",
  "correlation_id": "uuid (pipeline run)",
  "session_id": "uuid",
  "project_id": "string",
  "agent_id": "string",
  "timestamp": "ISO 8601",
  "input_hash": "SHA-256",
  "output_hash": "SHA-256",
  "cost_usd": "decimal",
  "latency_ms": "integer",
  "confidence": "float 0-1",
  "model": "string (claude-sonnet-4-20250514, etc.)",
  "status": "enum (success, failure, timeout, budget_exceeded)"
}
```

**Cost Metrics:** `cost_events` table with real-time inserts; `cost_summary_mv` materialized view refreshed every 60 seconds for aggregation queries.

**Structured Logging:** Python `structlog` with JSON output. Fields: `timestamp`, `level`, `service`, `method`, `project_id`, `agent_id`, `duration_ms`, `error`.

**Health Checks:** Background worker polls all 48 agents every 60 seconds. Results written to `agent_health` table. Fleet health endpoint aggregates.

**LLM Provider Selection:** The `sdk/llm/` layer manages provider routing. Configuration via `LLM_PROVIDER` env var (values: `anthropic`, `openai`, `ollama`; default: `anthropic`). Agent manifests use `tier: fast|balanced|powerful` mapped to provider-specific models (e.g., `fast` = Haiku on Anthropic, GPT-4o-mini on OpenAI, llama3 on Ollama). Optional `provider:` override in manifest allows per-agent provider pinning. Cost calculation is provider-aware: Anthropic and OpenAI use their respective token pricing; Ollama reports $0.00. Provider health is monitored alongside agent health — unhealthy providers trigger circuit breakers.

### 8.4 Error Handling and Propagation

Services raise typed exceptions. Each interface layer maps them to protocol-appropriate responses:

| Service Exception | MCP Response | REST Response | Dashboard Display |
|-------------------|-------------|---------------|-------------------|
| `BudgetExceededError` | Tool error with `code: "BUDGET_EXCEEDED"`, `message`, `budget_remaining` | HTTP 402 with JSON body `{"error": "budget_exceeded", "details": {...}}` | Red toast: "Budget exceeded for {scope}" |
| `PipelineNotFoundError` | Tool error with `code: "NOT_FOUND"` | HTTP 404 | Redirect to pipeline list with "Run not found" message |
| `GateAlreadyResolvedError` | Tool error with `code: "CONFLICT"` | HTTP 409 | Toast: "This gate has already been resolved" |
| `ValidationError` | Tool error with `code: "INVALID_INPUT"`, `details: [field errors]` | HTTP 422 with field-level errors | Inline form validation messages |
| `AgentUnavailableError` | Tool error with `code: "UNAVAILABLE"` | HTTP 503 | Yellow warning: "Agent temporarily unavailable" |
| `DatabaseUnavailableError` | Tool error with `code: "INTERNAL"` | HTTP 500 | Red banner: "System error. Try again." |
| `CostTrackingDegradedError` | Tool error with `code: "FAIL_SAFE"`, `message: "Cost tracking unavailable, all invocations blocked"` | HTTP 503 with fail-safe explanation | Red banner: "System in fail-safe mode" |

**Fail-Safe Principle:** If cost tracking or audit logging is unavailable, all agent invocations are blocked. The system fails closed, never open.

### 8.5 Agent Memory Architecture

| Memory Tier | Storage | Retention | Scope | Access Pattern |
|---|---|---|---|---|
| Short-term | LLM context window | Single invocation | Per-call | Automatic (prompt + response) |
| Working | session_context table (PostgreSQL) | Pipeline run duration | Per-pipeline-run | SessionService.get/set |
| Episodic | audit_events table | 1 year | Per-project | AuditService.query |
| Semantic | knowledge_exceptions table | Permanent | Global | KnowledgeService.search |
| Procedural | cost_metrics patterns | 90 days | Per-agent | CostService.get_patterns |

**Isolation:** Each agent reads only its declared `memory.working` / `memory.episodic` / `memory.semantic` from manifest. Cross-agent memory access requires explicit session key declaration.

### 8.6 LLM Provider Routing Layer

**Architecture:** `BaseAgent -> LLMProvider (interface) -> [AnthropicProvider | OpenAIProvider | OllamaProvider]`

| Component | File | Purpose |
|---|---|---|
| LLMProvider | sdk/llm/provider.py | Abstract interface: generate(), calculate_cost(), resolve_model() |
| AnthropicProvider | sdk/llm/anthropic_provider.py | Claude models: Haiku, Sonnet, Opus |
| OpenAIProvider | sdk/llm/openai_provider.py | GPT models: 4o-mini, 4o, 4.5 |
| OllamaProvider | sdk/llm/ollama_provider.py | Local: Llama, Mistral (zero cost) |
| Factory | sdk/llm/factory.py | create_provider(name) from env |

**Tier mapping:** fast -> Haiku/GPT-4o-mini/Llama3.2 | balanced -> Sonnet/GPT-4o/Mistral | powerful -> Opus/GPT-4.5/Llama3.1-405b

**Routing:** Manifest-driven (tier field) -> Environment-driven (LLM_PROVIDER) -> Fallback chain (circuit breaker after 5 failures).

### 8.7 Knowledge Retrieval (RAG) Architecture

- **Vector Store:** Per-project embeddings of Generated-Docs + codebase
- **Chunking:** Document-level for specifications, function-level for code
- **Retrieval:** KnowledgeService.search() -> vector similarity -> re-rank -> inject into agent context
- **Isolation:** Per-project boundary — agents cannot access other projects' knowledge

---

## 9. Data Flow Diagrams

### 9.1 MCP Path: Developer Triggers Pipeline

```
Developer                MCP Server            Shared Service         Database          LLM Provider
(Claude Code)            (agents)              Layer                  (PostgreSQL)      (via sdk/llm/)
    |                        |                      |                      |                 |
    |  trigger_pipeline      |                      |                      |                 |
    |  {project_id,          |                      |                      |                 |
    |   pipeline_id,         |                      |                      |                 |
    |   input_data}          |                      |                      |                 |
    +----------------------->|                      |                      |                 |
    |                        |  pipeline_service    |                      |                 |
    |                        |  .trigger()          |                      |                 |
    |                        +--------------------->|                      |                 |
    |                        |                      |  INSERT pipeline_run |                 |
    |                        |                      +--------------------->|                 |
    |                        |                      |       run_id         |                 |
    |                        |                      |<---------------------+                 |
    |                        |                      |                      |                 |
    |                        |                      |  Enqueue to          |                 |
    |                        |                      |  PipelineRunner      |                 |
    |                        |  {run_id, status:    |                      |                 |
    |                        |   "started",         |                      |                 |
    |   MCP tool result      |   est_cost}          |                      |                 |
    |<-----------------------+<---------------------+                      |                 |
    |                        |                      |                      |                 |
    |                        |        [ASYNC: PipelineRunner executes]     |                 |
    |                        |                      |                      |                 |
    |                        |                      |  For each DAG step:  |                 |
    |                        |                      |  1. Check budget     |                 |
    |                        |                      +--------------------->|                 |
    |                        |                      |  2. Invoke agent     |                 |
    |                        |                      +-------------------------------------------->|
    |                        |                      |       completion + tokens                   |
    |                        |                      |<-------------------------------------------+
    |                        |                      |  3. Record cost      |                 |
    |                        |                      +--------------------->|                 |
    |                        |                      |  4. Record audit     |                 |
    |                        |                      +--------------------->|                 |
    |                        |                      |  5. Checkpoint       |                 |
    |                        |                      +--------------------->|                 |
    |                        |                      |                      |                 |
    |  check_pipeline_status |                      |                      |                 |
    +----------------------->|                      |                      |                 |
    |                        +--------------------->|                      |                 |
    |                        |                      +--------------------->|                 |
    |                        |                      |<---------------------+                 |
    |   {status, progress,   |                      |                      |                 |
    |    cost_so_far, step}  |                      |                      |                 |
    |<-----------------------+<---------------------+                      |                 |
    |                        |                      |                      |                 |
```

### 9.2 Dashboard Path: Operator Reviews Approval Gate

```
Operator                 Streamlit           REST API            Shared Service         Database
(Browser)                Dashboard           (aiohttp)           Layer                  (PostgreSQL)
    |                        |                    |                    |                      |
    |  Open /approvals       |                    |                    |                      |
    +----------------------->|                    |                    |                      |
    |                        |  GET /api/v1/      |                    |                      |
    |                        |  approvals?        |                    |                      |
    |                        |  status=pending    |                    |                      |
    |                        +------------------->|                    |                      |
    |                        |                    | approval_service   |                      |
    |                        |                    | .list_pending()    |                      |
    |                        |                    +------------------->|                      |
    |                        |                    |                    |  SELECT FROM          |
    |                        |                    |                    |  approval_events      |
    |                        |                    |                    |  WHERE status=pending |
    |                        |                    |                    +--------------------->|
    |                        |                    |                    |<---------------------+
    |                        |                    |<-------------------+                      |
    |                        |  JSON response     |                    |                      |
    |                        |<-------------------+                    |                      |
    |   Rendered approval    |                    |                    |                      |
    |   queue page           |                    |                    |                      |
    |<-----------------------+                    |                    |                      |
    |                        |                    |                    |                      |
    |  Click "Approve"       |                    |                    |                      |
    |  {gate_id, note}       |                    |                    |                      |
    +----------------------->|                    |                    |                      |
    |                        |  POST /api/v1/     |                    |                      |
    |                        |  approvals/{id}/   |                    |                      |
    |                        |  approve           |                    |                      |
    |                        +------------------->|                    |                      |
    |                        |                    | approval_service   |                      |
    |                        |                    | .approve()         |                      |
    |                        |                    +------------------->|                      |
    |                        |                    |                    |  UPDATE approval_event|
    |                        |                    |                    |  SET status=approved  |
    |                        |                    |                    +--------------------->|
    |                        |                    |                    |                      |
    |                        |                    |                    |  Notify pipeline      |
    |                        |                    |                    |  runner to resume     |
    |                        |                    |                    |                      |
    |                        |                    |                    |  Send Slack           |
    |                        |                    |                    |  confirmation         |
    |                        |                    |<-------------------+                      |
    |                        |  HTTP 200 OK       |                    |                      |
    |                        |<-------------------+                    |                      |
    |   Success toast +      |                    |                    |                      |
    |   updated queue        |                    |                    |                      |
    |<-----------------------+                    |                    |                      |
    |                        |                    |                    |                      |
```

---

## 10. Interface Parity Matrix

This matrix shows which capabilities are accessible through which interface and to what degree.

| # | Capability | MCP | REST API | Dashboard | Notes |
|---|-----------|-----|----------|-----------|-------|
| C1 | Agent Orchestration | Full | Full | Partial | Dashboard shows orchestration status but cannot configure orchestration levels |
| C2 | 12-Document Pipeline | Full | Full | Partial | Dashboard views pipeline runs and outputs; trigger/resume only via MCP/REST |
| C3 | Cost Control & Governance | Full | Full | Full | All three interfaces read from same cost_summary_mv materialized view |
| C4 | Human-in-the-Loop | Full | Full | Full | MCP: approve_gate/reject_gate; Dashboard: visual review + structured comments |
| C5 | Quality Assurance | Partial | Full | Partial | MCP: view scores; REST: trigger test suites; Dashboard: view quality reports |
| C6 | Observability & Audit | Full | Full | Full | MCP: query audit log; REST: full CRUD; Dashboard: visual explorer + reports |
| C7 | Knowledge Management | Full | Full | Partial | MCP: search/create/promote; Dashboard: browse knowledge base (read-only) |
| C8 | Pipeline Resilience | Full | Full | Partial | MCP/REST: checkpoint/resume/cancel; Dashboard: view status, pause button |
| C9 | Agent Lifecycle | Partial | Full | Full | REST: deploy/rollback/promote; Dashboard: full lifecycle UI; MCP: read-only |
| C10 | Multi-Project Isolation | Full | Full | Full | All interfaces scope by project_id; dashboard has project selector |
| C11 | MCP Server Exposure | **Full** | N/A | N/A | This IS the MCP interface -- MCP-native by definition |
| C12 | Dashboard / Operator UI | N/A | Partial | **Full** | REST feeds the dashboard; MCP users get raw data, not visual UI |

**Reading the matrix:**
- **Full**: All operations for this capability are available through this interface
- **Partial**: Read/view operations available; some write/config operations require a different interface
- **N/A**: This capability is not applicable to this interface by design

---

## 11. What I'd Do Differently at 10x Scale

### 11.1 Shared Service Layer Becomes a Bottleneck

**What breaks:** At 10x users (60+ concurrent personas, 480+ agents), the in-process shared service layer running in a single Python process cannot handle the concurrent load. asyncio helps with I/O concurrency but the single event loop becomes the serialization point.

**Why:** Python's GIL + single-process architecture means CPU-bound operations (schema validation, hash computation, quality scoring) block the event loop. At 10x, queue depth grows and p95 latency blows past the 500ms target.

**Replacement:** Extract the shared service layer into a set of independent microservices behind a message broker (NATS or Redis Streams). Each service runs in its own process with horizontal scaling. MCP servers and REST API become thin gRPC/HTTP clients. Service mesh (Linkerd) handles routing, retries, and observability.

### 11.2 PostgreSQL Materialized Views Cannot Keep Up

**What breaks:** At 10x data volume (~130K audit events/day, ~50K cost events/day), the 60-second materialized view refresh for `cost_summary_mv` takes too long and blocks concurrent reads. Dashboard cost page shows stale data; MCP cost queries return inconsistent snapshots.

**Why:** Materialized view refresh is a full table rewrite in PostgreSQL. At high volumes, the refresh takes 10-30 seconds and blocks queries during the swap. Incremental materialized views are not natively supported.

**Replacement:** Move real-time aggregation to a streaming pipeline (Apache Flink or Materialize). Cost events flow through the stream processor, which maintains continuously-updated aggregations. MCP and REST query the stream processor's materialized state instead of PostgreSQL views. PostgreSQL remains the source of truth for raw events.

### 11.3 Streamlit Hits Concurrency Ceiling

**What breaks:** At 10x dashboard users (~50 concurrent sessions), Streamlit's single-threaded-per-session model requires 50 Python processes. Memory usage explodes (each Streamlit session holds page state in memory). The 10-second polling interval from 50 sessions generates 300 REST API requests per minute just for fleet health.

**Why:** Streamlit was designed for data exploration by a few users, not for a production monitoring dashboard serving a team. Each session is an independent Python process with no shared state.

**Replacement:** Migrate to a React SPA frontend with a WebSocket connection for push-based updates. Server-Sent Events (SSE) from the REST API push state changes to connected clients instead of polling. This reduces API load from O(sessions * polling_rate) to O(state_changes). Use a CDN for static assets and a Node.js BFF (Backend For Frontend) for WebSocket management.

### 11.4 Single-Node Agent Runtime Cannot Distribute DAG Execution

**What breaks:** At 10x pipelines (~50 concurrent pipeline runs with 12 steps each), the single-node asyncio DAG runner cannot parallelize across machines. A long-running agent step (e.g., D5-architecture-drafter taking 60 seconds) blocks the event loop's capacity for other pipeline steps.

**Why:** The DAG runner uses `asyncio.gather()` which parallelizes I/O but runs in a single process on a single machine. There is no work distribution, no backpressure, and no independent scaling of agent execution.

**Replacement:** Adopt Temporal or a similar workflow orchestration engine. Each pipeline step becomes a Temporal activity executed by a worker pool. Workers scale horizontally. Temporal handles retries, timeouts, checkpointing, and visibility natively. The PipelineService becomes a Temporal workflow definition; the checkpoint/resume logic is replaced by Temporal's built-in durable execution.

### 11.5 API Key Auth Does Not Scale to Multi-Team

**What breaks:** At 10x teams (~10 independent teams using the platform), a single shared API key provides no per-team identity, no fine-grained permissions, no key rotation without coordinated downtime, and no ability to revoke a compromised team's access without affecting others.

**Why:** API key auth was chosen for simplicity in a single-team internal tool. It has no concept of scopes, expiration, or issuer identity.

**Replacement:** Adopt OAuth2 with short-lived JWTs issued by an internal IdP (Keycloak or Auth0). Each team gets its own client credentials. Tokens carry scopes (`pipelines:write`, `audit:read`, `fleet:admin`). MCP servers validate JWTs via a shared JWKS endpoint. Dashboard uses OIDC authorization code flow. Key rotation is per-team and non-disruptive.

---

*This architecture document defines HOW the Agentic SDLC Platform is structured. It establishes the Shared Service Layer as the central pattern that ensures MCP, REST, and Dashboard interfaces are equal citizens with zero logic duplication. Downstream documents (CLAUDE.md, DATA-MODEL, API-CONTRACTS, DESIGN-SPEC, etc.) should read this document as their structural foundation.*
