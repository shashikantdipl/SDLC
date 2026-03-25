# API-CONTRACTS — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 10 of 14 | Status: Draft
**Reads from:** INTERACTION-MAP (Doc 6), MCP-TOOL-SPEC (Doc 7), DESIGN-SPEC (Doc 8), ARCH (Doc 2)

---

## Table of Contents

1. [Base URL & Versioning](#1-base-url--versioning)
2. [Dual Role Statement](#2-dual-role-statement)
3. [Standard Response Envelope](#3-standard-response-envelope)
4. [Authentication](#4-authentication)
5. [MCP Parity Table](#5-mcp-parity-table)
6. [Dashboard Feed Table](#6-dashboard-feed-table)
7. [Endpoints](#7-endpoints)
   - 7.1 [Pipelines](#71-pipelines-apiv1pipelines)
   - 7.2 [Agents](#72-agents-apiv1agents)
   - 7.3 [Cost & Budget](#73-cost--budget-apiv1cost-apiv1budget)
   - 7.4 [Audit](#74-audit-apiv1audit)
   - 7.5 [Approvals](#75-approvals-apiv1approvals)
   - 7.6 [Knowledge](#76-knowledge-apiv1knowledge)
   - 7.7 [System](#77-system-apiv1system)
   - 7.8 [Auth](#78-auth-apiv1auth)
8. [WebSocket / SSE Channels](#8-websocket--sse-channels)
9. [Error Codes](#9-error-codes)
10. [Rate Limiting](#10-rate-limiting)

---

## 1. Base URL & Versioning

| Environment | Base URL |
|---|---|
| Production | `https://api.agentic-sdlc.io/api/v1/` |
| Staging | `https://staging-api.agentic-sdlc.io/api/v1/` |
| Development | `http://localhost:8080/api/v1/` |

**Versioning strategy:** URL path prefix. The current version is `/v1/`. When breaking changes are introduced, `/v2/` will be added. Both versions will run in parallel for a minimum of 6 months before `/v1/` is deprecated.

**Content type:** All requests and responses use `application/json` unless otherwise noted (e.g., audit export returns binary files).

**CORS:** Development allows `*`. Production restricts to the Dashboard origin (`https://dashboard.agentic-sdlc.io`) and registered API client origins.

---

## 2. Dual Role Statement

The REST API serves **two consumers equally**:

1. **Wraps MCP tools** — Every one of the 35 MCP tools defined in MCP-TOOL-SPEC (Doc 7) has a REST equivalent. Non-AI consumers (CI/CD pipelines, scripts, third-party integrations) can perform every operation that an AI client performs via MCP, using standard HTTP. This satisfies quality requirement Q-049 (MCP/REST parity).

2. **Feeds the Dashboard** — The Streamlit Dashboard (DESIGN-SPEC, Doc 8) consumes REST endpoints for all five pages: Fleet Health, Cost Monitor, Pipeline Runs, Audit Log, and Approval Queue. Every widget and screen maps to one or more REST calls.

Both consumers call the **same shared service layer**. The REST handler is a thin translation layer:
- Accepts HTTP request, validates auth, extracts parameters
- Calls the same shared service method that the MCP tool handler calls
- Returns the same data shapes defined in INTERACTION-MAP (Doc 6)
- Wraps the response in the standard envelope (Section 3)

There is NO business logic in the REST handler. All logic lives in shared services.

---

## 3. Standard Response Envelope

### Success Response

```json
{
  "data": { },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-03-24T14:30:00.000Z",
    "duration_ms": 42
  },
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 120,
    "total_pages": 3
  }
}
```

- `data` — The payload. For single-object responses, this is the object. For list responses, this is an array.
- `meta` — Always present. `request_id` is a UUID v4 generated per request, used for tracing and support. `duration_ms` is server-side processing time.
- `pagination` — Present only on list endpoints that support pagination. `page` is 1-indexed.

### Error Response

```json
{
  "error": {
    "code": "BUDGET_EXCEEDED",
    "message": "Project proj_abc123def456 budget of $50.00 has been exceeded (current spend: $52.30)",
    "details": {
      "project_id": "proj_abc123def456",
      "budget_usd": 50.00,
      "spent_usd": 52.30
    }
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-24T14:30:00.000Z"
  }
}
```

- `error.code` — Machine-readable error code. Matches MCP error codes (Section 9).
- `error.message` — Human-readable description.
- `error.details` — Optional structured context for the error.
- `meta` — Always present, same structure as success.

### HTTP Status Code Mapping

| Status | Usage |
|---|---|
| 200 | Successful GET, PATCH |
| 201 | Successful POST that creates a resource |
| 204 | Successful DELETE |
| 400 | Validation error, malformed request |
| 401 | Missing or invalid authentication |
| 403 | Authenticated but insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (e.g., pipeline already running) |
| 422 | Semantically invalid request (e.g., invalid promotion path) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service unavailable (MCP server down, circuit breaker open) |

---

## 4. Authentication

### Dashboard Sessions — JWT

Dashboard users authenticate via `POST /api/v1/auth/login` and receive a JWT.

| Header | Value |
|---|---|
| `Authorization` | `Bearer <jwt_token>` |

- **Issued by:** `POST /api/v1/auth/login`
- **Lifetime:** 30 minutes
- **Refresh:** `POST /api/v1/auth/refresh` (accepts expired JWT within 7-day refresh window)
- **JWT payload:** `{ "sub": "user_id", "roles": ["operator", "admin"], "iat": ..., "exp": ... }`
- **Signing:** RS256 with rotating keys

### Programmatic Access — API Key

Scripts, CI/CD, and external integrations authenticate via API key header.

| Header | Value |
|---|---|
| `X-API-Key` | `ask_<64-char-hex>` |

- **Issued by:** Admin panel or CLI provisioning command
- **Lifetime:** Configurable, default 90 days
- **Scope:** Per-key permissions (read-only, operator, admin)
- **MCP parity:** The `X-API-Key` authentication method mirrors the MCP `ANTHROPIC_API_KEY` auth, satisfying Q-049 parity

### Auth Precedence

If both `Authorization` and `X-API-Key` headers are present, `Authorization` (JWT) takes precedence.

### Unauthenticated Endpoints

| Endpoint | Reason |
|---|---|
| `POST /api/v1/auth/login` | Login cannot require auth |
| `GET /api/v1/system/health` | Health checks used by load balancers |

---

## 5. MCP Parity Table

Every MCP tool has a REST equivalent. This table maps all 35 MCP tools (from Doc 7) to REST endpoints (Q-049 compliance).

| # | MCP Tool | Interaction ID | REST Endpoint | Method | Query/Path Params | Notes |
|---|---|---|---|---|---|---|
| 1 | `trigger_pipeline` | I-001 | `/api/v1/pipelines` | POST | — | Request body: project_id, brief, template, options |
| 2 | `get_pipeline_status` | I-002 | `/api/v1/pipelines/{run_id}` | GET | `?include_stage_details=bool` | |
| 3 | `list_pipeline_runs` | I-003 | `/api/v1/pipelines` | GET | `?project_id=&status=&since=&page=&per_page=` | |
| 4 | `resume_pipeline` | I-004 | `/api/v1/pipelines/{run_id}/resume` | POST | — | Optional body: override_context |
| 5 | `cancel_pipeline` | I-005 | `/api/v1/pipelines/{run_id}/cancel` | POST | — | Optional body: reason |
| 6 | `get_pipeline_documents` | I-006 | `/api/v1/pipelines/{run_id}/documents` | GET | `?doc_type=&stage_index=&format=` | |
| 7 | `retry_pipeline_step` | I-007 | `/api/v1/pipelines/{run_id}/steps/{step_index}/retry` | POST | — | Optional body: modified_context |
| 8 | `get_pipeline_config` | I-008 | `/api/v1/pipelines/config` | GET | `?template=` | |
| 9 | `validate_pipeline_input` | I-009 | `/api/v1/pipelines/validate` | POST | — | Request body: brief, template, options |
| 10 | `list_agents` | I-020 | `/api/v1/agents` | GET | `?phase=&status=&role=&maturity=&page=&per_page=` | |
| 11 | `get_agent` | I-021 | `/api/v1/agents/{agent_id}` | GET | `?include_metrics=bool&include_version_history=bool` | |
| 12 | `invoke_agent` | I-022 | `/api/v1/agents/{agent_id}/invoke` | POST | — | Request body: project_id, input, options |
| 13 | `check_agent_health` | I-023 | `/api/v1/agents/{agent_id}/health` | GET | — | Omit agent_id path for fleet-wide: `GET /agents/health` |
| 14 | `promote_agent_version` | I-024 | `/api/v1/agents/{agent_id}/promote` | POST | — | Request body: target_maturity, justification |
| 15 | `rollback_agent_version` | I-025 | `/api/v1/agents/{agent_id}/rollback` | POST | — | Request body: target_version, reason |
| 16 | `set_canary_traffic` | I-026 | `/api/v1/agents/{agent_id}/canary` | PATCH | — | Request body: traffic_pct |
| 17 | `get_agent_maturity` | I-027 | `/api/v1/agents/{agent_id}/maturity` | GET | — | |
| 18 | `get_cost_report` | I-040 | `/api/v1/cost/report` | GET | `?scope=&entity_id=&period_days=` | |
| 19 | `check_budget` | I-041 | `/api/v1/budget/{scope}/{entity_id}` | GET | — | scope: fleet, project, agent |
| 20 | `query_audit_events` | I-042 | `/api/v1/audit/events` | GET | `?agent_id=&severity=&since=&until=&action=&project_id=&page=&per_page=` | |
| 21 | `get_audit_summary` | I-043 | `/api/v1/audit/summary` | GET | `?since=&until=` | |
| 22 | `export_audit_report` | I-044 | `/api/v1/audit/export` | GET | `?format=&since=&until=&agent_id=&severity=` | Returns download URL |
| 23 | `list_pending_approvals` | I-045 | `/api/v1/approvals` | GET | `?status=&risk_level=&page=&per_page=` | Default: status=pending |
| 24 | `approve_gate` | I-046 | `/api/v1/approvals/{approval_id}/approve` | POST | — | Request body: comment |
| 25 | `reject_gate` | I-047 | `/api/v1/approvals/{approval_id}/reject` | POST | — | Request body: comment (required) |
| 26 | `get_cost_anomalies` | I-048 | `/api/v1/cost/anomalies` | GET | `?severity=&acknowledged=&page=&per_page=` | |
| 27 | `update_budget_threshold` | I-049 | `/api/v1/budget/{scope}/{entity_id}/threshold` | PATCH | — | Request body: alert_threshold_pct, budget_usd |
| 28 | `search_exceptions` | I-060 | `/api/v1/knowledge/exceptions/search` | GET | `?q=&tier=&severity=&active=&page=&per_page=` | |
| 29 | `create_exception` | I-061 | `/api/v1/knowledge/exceptions` | POST | — | Request body: title, rule, description, severity, tags |
| 30 | `promote_exception` | I-062 | `/api/v1/knowledge/exceptions/{exception_id}/promote` | POST | — | Request body: target_tier |
| 31 | `list_exceptions` | I-063 | `/api/v1/knowledge/exceptions` | GET | `?tier=&active=&page=&per_page=` | |
| 32 | `get_fleet_health` | I-080 | `/api/v1/system/health` | GET | — | |
| 33 | `get_mcp_status` | I-081 | `/api/v1/system/mcp` | GET | — | |
| 34 | `list_recent_mcp_calls` | I-082 | `/api/v1/audit/mcp-calls` | GET | `?server_name=&tool_name=&status=&limit=` | |
| 35 | *(auth — no MCP equivalent)* | — | `/api/v1/auth/*` | — | — | REST-only: login, refresh, me |

**Parity count: 34 MCP tools mapped to 34 REST endpoints + 1 fleet-wide health variant + 3 auth endpoints = 38 total REST endpoints.**

---

## 6. Dashboard Feed Table

Every Dashboard screen (from DESIGN-SPEC, Doc 8) consumes one or more REST endpoints. This table guarantees all dashboard data needs are met.

| Dashboard Page | Screen ID | Screen Name | REST Endpoints Consumed | Real-time? |
|---|---|---|---|---|
| **Fleet Health** | S-001 | Fleet Health Overview | `GET /system/health` (I-080) | Polling 10s |
| | S-002 | Agent Grid | `GET /agents` (I-020) | Polling 30s |
| | S-003 | Agent Detail Panel | `GET /agents/{id}` (I-021) | On-demand |
| | S-004 | Health Badges | `GET /agents/{id}/health` (I-023) | Polling 30s |
| | S-005 | Version Management | `POST /agents/{id}/promote` (I-024), `POST /agents/{id}/rollback` (I-025), `PATCH /agents/{id}/canary` (I-026) | On-demand |
| | S-006 | Maturity Badges | `GET /agents/{id}/maturity` (I-027) | Polling 60s |
| | S-007 | MCP Monitoring Panel | `GET /system/mcp` (I-081), `GET /audit/mcp-calls` (I-082) | WebSocket `ws://host/ws/mcp-calls` |
| **Cost Monitor** | S-010 | Cost Charts | `GET /cost/report` (I-040) | Polling 60s |
| | S-011 | Budget Gauges | `GET /budget/{scope}/{id}` (I-041) | Polling 60s |
| | S-012 | Anomaly Alerts | `GET /cost/anomalies` (I-048) | Polling 30s |
| | S-013 | Budget Settings | `PATCH /budget/{scope}/{id}/threshold` (I-049) | On-demand |
| **Pipeline Runs** | S-020 | Pipeline Trigger Form | `POST /pipelines` (I-001), `POST /pipelines/validate` (I-009) | — |
| | S-021 | Pipeline Runs Table | `GET /pipelines` (I-003) | Polling 15s |
| | S-022 | Pipeline Run Detail | `GET /pipelines/{run_id}` (I-002) | WebSocket `ws://host/ws/pipelines/{run_id}` |
| | S-023 | Document Viewer | `GET /pipelines/{run_id}/documents` (I-006) | On-demand |
| | S-024 | Pipeline Actions | `POST /pipelines/{run_id}/resume` (I-004), `POST /pipelines/{run_id}/cancel` (I-005), `POST /pipelines/{run_id}/steps/{step}/retry` (I-007) | — |
| **Audit Log** | S-030 | Audit Event Table | `GET /audit/events` (I-042) | Polling 30s |
| | S-031 | Audit Summary Cards | `GET /audit/summary` (I-043) | Polling 60s |
| | S-032 | Audit Export Button | `GET /audit/export` (I-044) | On-demand |
| **Approval Queue** | S-040 | Approval Queue Table | `GET /approvals` (I-045) | WebSocket `ws://host/ws/approvals` |
| | S-041 | Approval Detail Panel | `GET /approvals` (I-045), `POST /approvals/{id}/approve` (I-046), `POST /approvals/{id}/reject` (I-047) | — |
| | S-042 | Approval History Tab | `GET /approvals?status=approved,rejected` (I-045) | On-demand |

---

## 7. Endpoints

All endpoints are prefixed with `/api/v1`. Request and response bodies use the data shapes defined in INTERACTION-MAP (Doc 6). Every endpoint references the interaction ID it implements and the shared service method it delegates to.

---

### 7.1 Pipelines (`/api/v1/pipelines`)

---

#### POST /pipelines — Trigger Pipeline

| Field | Value |
|---|---|
| **Interaction ID** | I-001 |
| **MCP Tool** | `trigger_pipeline` |
| **Dashboard Screen** | S-020 Pipeline Trigger Form |
| **Shared Service** | `PipelineService.trigger()` |
| **Auth** | JWT or API Key (operator role) |

**Request Body:**

```json
{
  "project_id": "proj_abc123def456",
  "brief": "Build a multi-tenant SaaS billing dashboard with Stripe integration",
  "template": "full-stack-first",
  "options": {
    "skip_stages": [],
    "cost_ceiling_usd": 25.0,
    "priority": "normal"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `project_id` | string | Yes | Pattern: `^proj_[a-z0-9]{12}$` |
| `brief` | string | Yes | 20-5000 characters |
| `template` | string | No | `full-stack-first` (default), `api-first`, `data-pipeline`, `mobile-first` |
| `options.skip_stages` | integer[] | No | Stage indices 0-13 to skip |
| `options.cost_ceiling_usd` | number | No | 1.0-500.0, default 25.0 |
| `options.priority` | string | No | `low`, `normal` (default), `high` |

**Response:** `201 Created`

```json
{
  "data": {
    "run_id": "run_a1b2c3d4e5f6g7h8",
    "project_id": "proj_abc123def456",
    "pipeline_name": "full-stack-first-14-doc",
    "status": "pending",
    "current_step": 0,
    "total_steps": 14,
    "current_step_name": "00-ROADMAP",
    "started_at": "2026-03-24T14:30:00.000Z",
    "completed_at": null,
    "cost_usd": 0.00,
    "triggered_by": "user_jpark",
    "error_message": null,
    "checkpoint_step": null
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-03-24T14:30:00.000Z",
    "duration_ms": 156
  }
}
```

**Data shape:** `PipelineRun` (INTERACTION-MAP 2.1)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_PROJECT` | 404 | project_id not found |
| `BUDGET_EXCEEDED` | 422 | Estimated cost exceeds budget or ceiling |
| `PIPELINE_ALREADY_RUNNING` | 409 | Project already has active pipeline |
| `INVALID_TEMPLATE` | 400 | Unknown template value |
| `BRIEF_TOO_SHORT` | 400 | Brief < 20 characters |

---

#### GET /pipelines — List Pipeline Runs

| Field | Value |
|---|---|
| **Interaction ID** | I-003 |
| **MCP Tool** | `list_pipeline_runs` |
| **Dashboard Screen** | S-021 Pipeline Runs Table |
| **Shared Service** | `PipelineService.list_runs()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `project_id` | string | — | Filter by project |
| `status` | string | — | Filter: `pending`, `running`, `paused`, `completed`, `failed`, `cancelled` |
| `since` | ISO 8601 | — | Runs created after this timestamp |
| `page` | integer | 1 | Page number (1-indexed) |
| `per_page` | integer | 20 | Items per page (1-100) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "run_id": "run_a1b2c3d4e5f6g7h8",
      "project_id": "proj_abc123def456",
      "pipeline_name": "full-stack-first-14-doc",
      "status": "running",
      "current_step": 6,
      "total_steps": 14,
      "current_step_name": "06-INTERACTION-MAP",
      "started_at": "2026-03-24T14:30:00.000Z",
      "completed_at": null,
      "cost_usd": 8.42,
      "triggered_by": "user_priya",
      "error_message": null,
      "checkpoint_step": 5
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440002",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 28
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 47,
    "total_pages": 3
  }
}
```

**Data shape:** `PipelineRun[]` (INTERACTION-MAP 2.1)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_PROJECT` | 404 | project_id filter references non-existent project |
| `INVALID_DATE_RANGE` | 400 | Malformed `since` timestamp |

---

#### GET /pipelines/{run_id} — Get Pipeline Status

| Field | Value |
|---|---|
| **Interaction ID** | I-002 |
| **MCP Tool** | `get_pipeline_status` |
| **Dashboard Screen** | S-022 Pipeline Run Detail |
| **Shared Service** | `PipelineService.get_status()` |
| **Auth** | JWT or API Key (read) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `run_id` | string | Pattern: `^run_[a-z0-9]{16}$` |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `include_stage_details` | boolean | false | Include per-stage timing, cost, agent assignment |

**Response:** `200 OK`

```json
{
  "data": {
    "run_id": "run_a1b2c3d4e5f6g7h8",
    "project_id": "proj_abc123def456",
    "pipeline_name": "full-stack-first-14-doc",
    "status": "running",
    "current_step": 6,
    "total_steps": 14,
    "current_step_name": "06-INTERACTION-MAP",
    "started_at": "2026-03-24T14:30:00.000Z",
    "completed_at": null,
    "cost_usd": 8.42,
    "triggered_by": "user_priya",
    "error_message": null,
    "checkpoint_step": 5
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440003",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 12
  }
}
```

**Data shape:** `PipelineRun` (INTERACTION-MAP 2.1)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | 404 | run_id does not exist |

---

#### POST /pipelines/{run_id}/resume — Resume Pipeline

| Field | Value |
|---|---|
| **Interaction ID** | I-004 |
| **MCP Tool** | `resume_pipeline` |
| **Dashboard Screen** | S-024 Pipeline Actions |
| **Shared Service** | `PipelineService.resume()` |
| **Auth** | JWT or API Key (operator role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `run_id` | string | Pattern: `^run_[a-z0-9]{16}$` |

**Request Body (optional):**

```json
{
  "override_context": {
    "reviewer_feedback": "Add more detail on auth flow"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `override_context` | object | No | Key-value pairs injected into the next stage |

**Response:** `200 OK`

```json
{
  "data": {
    "run_id": "run_a1b2c3d4e5f6g7h8",
    "project_id": "proj_abc123def456",
    "pipeline_name": "full-stack-first-14-doc",
    "status": "running",
    "current_step": 6,
    "total_steps": 14,
    "current_step_name": "06-INTERACTION-MAP",
    "started_at": "2026-03-24T14:30:00.000Z",
    "completed_at": null,
    "cost_usd": 8.42,
    "triggered_by": "user_priya",
    "error_message": null,
    "checkpoint_step": 5
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440004",
    "timestamp": "2026-03-24T14:40:00.000Z",
    "duration_ms": 89
  }
}
```

**Data shape:** `PipelineRun` (INTERACTION-MAP 2.1)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | 404 | run_id does not exist |
| `PIPELINE_NOT_PAUSED` | 409 | Run is not in paused state |
| `APPROVAL_PENDING` | 409 | Gate must be approved before resume |

---

#### POST /pipelines/{run_id}/cancel — Cancel Pipeline

| Field | Value |
|---|---|
| **Interaction ID** | I-005 |
| **MCP Tool** | `cancel_pipeline` |
| **Dashboard Screen** | S-024 Pipeline Actions |
| **Shared Service** | `PipelineService.cancel()` |
| **Auth** | JWT or API Key (operator role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `run_id` | string | Pattern: `^run_[a-z0-9]{16}$` |

**Request Body (optional):**

```json
{
  "reason": "Requirements changed, need to restart with updated brief"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | string | No | Max 500 chars. Recorded in audit log |

**Response:** `200 OK`

```json
{
  "data": {
    "run_id": "run_a1b2c3d4e5f6g7h8",
    "project_id": "proj_abc123def456",
    "pipeline_name": "full-stack-first-14-doc",
    "status": "cancelled",
    "current_step": 6,
    "total_steps": 14,
    "current_step_name": "06-INTERACTION-MAP",
    "started_at": "2026-03-24T14:30:00.000Z",
    "completed_at": "2026-03-24T14:42:00.000Z",
    "cost_usd": 8.42,
    "triggered_by": "user_priya",
    "error_message": null,
    "checkpoint_step": 5
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440005",
    "timestamp": "2026-03-24T14:42:00.000Z",
    "duration_ms": 67
  }
}
```

**Data shape:** `PipelineRun` (INTERACTION-MAP 2.1)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | 404 | run_id does not exist |
| `PIPELINE_ALREADY_TERMINAL` | 409 | Run is already completed, failed, or cancelled |

---

#### GET /pipelines/{run_id}/documents — Get Pipeline Documents

| Field | Value |
|---|---|
| **Interaction ID** | I-006 |
| **MCP Tool** | `get_pipeline_documents` |
| **Dashboard Screen** | S-023 Document Viewer |
| **Shared Service** | `PipelineService.get_documents()` |
| **Auth** | JWT or API Key (read) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `run_id` | string | Pattern: `^run_[a-z0-9]{16}$` |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `doc_type` | string | — | Filter by document type |
| `stage_index` | integer | — | Filter by stage (0-13) |
| `format` | string | `markdown` | Output format: `markdown`, `json`, `html` |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "document_id": "660e8400-e29b-41d4-a716-446655440010",
      "run_id": "run_a1b2c3d4e5f6g7h8",
      "doc_number": 6,
      "doc_name": "INTERACTION-MAP",
      "doc_type": "interaction-map",
      "content": "# INTERACTION-MAP ...",
      "generated_at": "2026-03-24T14:38:00.000Z",
      "quality_score": 0.92,
      "token_count": 14500,
      "agent_id": "P3-interaction-mapper"
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440006",
    "timestamp": "2026-03-24T14:42:00.000Z",
    "duration_ms": 35
  }
}
```

**Data shape:** `PipelineDocument[]` (INTERACTION-MAP 2.2)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | 404 | run_id does not exist |
| `NO_DOCUMENTS_YET` | 404 | Pipeline has not produced any documents yet |

---

#### POST /pipelines/{run_id}/steps/{step_index}/retry — Retry Pipeline Step

| Field | Value |
|---|---|
| **Interaction ID** | I-007 |
| **MCP Tool** | `retry_pipeline_step` |
| **Dashboard Screen** | S-024 Pipeline Actions |
| **Shared Service** | `PipelineService.retry_step()` |
| **Auth** | JWT or API Key (operator role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `run_id` | string | Pattern: `^run_[a-z0-9]{16}$` |
| `step_index` | integer | 0-13 |

**Request Body (optional):**

```json
{
  "modified_context": {
    "additional_instructions": "Focus more on security aspects of the API design"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `modified_context` | object | No | Key-value overrides for the retry |

**Response:** `200 OK`

```json
{
  "data": {
    "run_id": "run_a1b2c3d4e5f6g7h8",
    "project_id": "proj_abc123def456",
    "pipeline_name": "full-stack-first-14-doc",
    "status": "running",
    "current_step": 3,
    "total_steps": 14,
    "current_step_name": "03-CLAUDE",
    "started_at": "2026-03-24T14:30:00.000Z",
    "completed_at": null,
    "cost_usd": 9.10,
    "triggered_by": "user_priya",
    "error_message": null,
    "checkpoint_step": 2
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440007",
    "timestamp": "2026-03-24T14:45:00.000Z",
    "duration_ms": 102
  }
}
```

**Data shape:** `PipelineRun` (INTERACTION-MAP 2.1)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | 404 | run_id does not exist |
| `STAGE_NOT_FAILED` | 409 | Stage is not in failed state |
| `MAX_RETRIES_EXCEEDED` | 422 | Maximum retry count reached |
| `BUDGET_EXCEEDED` | 422 | Retry would exceed cost ceiling |

---

#### GET /pipelines/config — Get Pipeline Config

| Field | Value |
|---|---|
| **Interaction ID** | I-008 |
| **MCP Tool** | `get_pipeline_config` |
| **Dashboard Screen** | S-020 Config Panel |
| **Shared Service** | `PipelineService.get_config()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `template` | string | `full-stack-first` | Pipeline template name |

**Response:** `200 OK`

```json
{
  "data": {
    "pipeline_name": "full-stack-first-14-doc",
    "approach": "full-stack-first",
    "steps": [
      {
        "step_number": 0,
        "step_name": "00-ROADMAP",
        "agent_id": "P1-requirements-analyst",
        "timeout_seconds": 120,
        "requires_approval": false,
        "depends_on": []
      },
      {
        "step_number": 6,
        "step_name": "06-INTERACTION-MAP",
        "agent_id": "P3-interaction-mapper",
        "timeout_seconds": 180,
        "requires_approval": true,
        "depends_on": [4, 5]
      }
    ],
    "default_timeout_seconds": 120,
    "approval_gates": ["06-INTERACTION-MAP", "10-API-CONTRACTS"]
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440008",
    "timestamp": "2026-03-24T14:30:00.000Z",
    "duration_ms": 5
  }
}
```

**Data shape:** `PipelineConfig` (INTERACTION-MAP 2.3)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_TEMPLATE` | 400 | Unknown template value |

---

#### POST /pipelines/validate — Validate Pipeline Input

| Field | Value |
|---|---|
| **Interaction ID** | I-009 |
| **MCP Tool** | `validate_pipeline_input` |
| **Dashboard Screen** | S-020 Validation Panel |
| **Shared Service** | `PipelineService.validate_input()` |
| **Auth** | JWT or API Key (read) |

**Request Body:**

```json
{
  "brief": "Build a real-time chat application with WebSocket support and end-to-end encryption",
  "template": "full-stack-first",
  "options": {
    "cost_ceiling_usd": 30.0
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `brief` | string | Yes | Project brief to validate |
| `template` | string | No | Default: `full-stack-first` |
| `options` | object | No | Same options as trigger |

**Response:** `200 OK`

```json
{
  "data": {
    "valid": true,
    "errors": [],
    "warnings": [
      {
        "field": "brief",
        "message": "Brief does not mention target users",
        "suggestion": "Add a section describing primary user personas"
      }
    ],
    "project_id": null
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440009",
    "timestamp": "2026-03-24T14:30:00.000Z",
    "duration_ms": 18
  }
}
```

**Data shape:** `ValidationResult` (INTERACTION-MAP 2.4)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_TEMPLATE` | 400 | Unknown template value |

---

### 7.2 Agents (`/api/v1/agents`)

---

#### GET /agents — List Agents

| Field | Value |
|---|---|
| **Interaction ID** | I-020 |
| **MCP Tool** | `list_agents` |
| **Dashboard Screen** | S-002 Agent Grid |
| **Shared Service** | `AgentService.list_agents()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `phase` | string | — | Filter: `plan`, `design`, `build`, `verify`, `deploy` |
| `status` | string | — | Filter: `active`, `degraded`, `offline`, `canary` |
| `role` | string | — | Filter by agent role |
| `maturity` | string | — | Filter: `supervised`, `assisted`, `autonomous`, `fully_autonomous` |
| `page` | integer | 1 | Page number |
| `per_page` | integer | 50 | Items per page (1-100) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "agent_id": "P1-prd-writer",
      "name": "PRD Writer",
      "phase": "plan",
      "archetype": "writer",
      "status": "active",
      "active_version": "1.2.0",
      "cost_today_usd": 2.40,
      "last_invocation_at": "2026-03-24T14:28:00.000Z",
      "invocation_count_today": 12
    },
    {
      "agent_id": "P3-api-gen",
      "name": "API Generator",
      "phase": "design",
      "archetype": "writer",
      "status": "degraded",
      "active_version": "1.1.0",
      "cost_today_usd": 5.10,
      "last_invocation_at": "2026-03-24T14:25:00.000Z",
      "invocation_count_today": 8
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440020",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 22
  },
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 48,
    "total_pages": 1
  }
}
```

**Data shape:** `AgentSummary[]` (INTERACTION-MAP 2.5)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_ROLE` | 400 | Unknown role value |
| `INVALID_PHASE` | 400 | Unknown phase value |

---

#### GET /agents/{agent_id} — Get Agent Detail

| Field | Value |
|---|---|
| **Interaction ID** | I-021 |
| **MCP Tool** | `get_agent` |
| **Dashboard Screen** | S-003 Agent Detail Panel |
| **Shared Service** | `AgentService.get_agent()` |
| **Auth** | JWT or API Key (read) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `agent_id` | string | e.g., `P1-prd-writer` |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `include_metrics` | boolean | false | Include performance metrics |
| `include_version_history` | boolean | false | Include version history |

**Response:** `200 OK`

```json
{
  "data": {
    "agent_id": "P1-prd-writer",
    "name": "PRD Writer",
    "phase": "plan",
    "archetype": "writer",
    "status": "active",
    "active_version": "1.2.0",
    "cost_today_usd": 2.40,
    "last_invocation_at": "2026-03-24T14:28:00.000Z",
    "invocation_count_today": 12,
    "provider": "anthropic",
    "tier": "powerful",
    "manifest": { "model": "claude-opus-4-6", "max_tokens": 16000 },
    "prompt_preview": "You are the PRD Writer agent. Your task is to generate...",
    "maturity": {
      "agent_id": "P1-prd-writer",
      "current_level": "assisted",
      "override_rate": 0.05,
      "confidence_avg": 0.91,
      "consecutive_days": 14,
      "next_level": "autonomous",
      "promotion_eligible": true,
      "promotion_criteria": "Override rate < 3% for 21 consecutive days"
    },
    "canary_version": null,
    "canary_traffic_pct": 0,
    "health": {
      "agent_id": "P1-prd-writer",
      "healthy": true,
      "last_check_at": "2026-03-24T14:34:00.000Z",
      "response_time_ms": 34,
      "error_message": null,
      "consecutive_failures": 0,
      "circuit_breaker_open": false
    },
    "model": "claude-opus-4-6",
    "max_tokens": 16000,
    "temperature": 0.3,
    "tools": ["search_exceptions", "get_pipeline_config"]
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440021",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 18
  }
}
```

**Data shape:** `AgentDetail` (INTERACTION-MAP 2.6)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | 404 | agent_id does not exist |

---

#### POST /agents/{agent_id}/invoke — Invoke Agent

| Field | Value |
|---|---|
| **Interaction ID** | I-022 |
| **MCP Tool** | `invoke_agent` |
| **Dashboard Screen** | — (MCP/REST only, no dashboard screen) |
| **Shared Service** | `AgentService.invoke()` |
| **Auth** | JWT or API Key (operator role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `agent_id` | string | Agent identifier |

**Request Body:**

```json
{
  "project_id": "proj_abc123def456",
  "input": {
    "content": "Review the authentication module for security best practices",
    "context": {
      "language": "python",
      "framework": "fastapi"
    },
    "upstream_documents": [
      {
        "doc_type": "arch-design",
        "content": "# Architecture..."
      }
    ]
  },
  "options": {
    "max_tokens": 16000,
    "temperature": 0.3,
    "timeout_seconds": 120
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `project_id` | string | Yes | Project to bill against |
| `input.content` | string | Yes | Primary input, max 100000 chars |
| `input.context` | object | No | Additional structured context |
| `input.upstream_documents` | array | No | Previously generated docs |
| `options.max_tokens` | integer | No | 100-200000, default 16000 |
| `options.temperature` | number | No | 0.0-1.0, default 0.3 |
| `options.timeout_seconds` | integer | No | 10-600, default 120 |

**Response:** `201 Created`

```json
{
  "data": {
    "invocation_id": "770e8400-e29b-41d4-a716-446655440030",
    "agent_id": "B1-code-reviewer",
    "mode": "direct",
    "status": "success",
    "confidence": 0.88,
    "output": "## Code Review Results\n\n### Security Issues Found\n1. ...",
    "cost_usd": 0.42,
    "duration_ms": 4520,
    "tokens_in": 3200,
    "tokens_out": 1800,
    "model": "claude-opus-4-6",
    "error_message": null
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440022",
    "timestamp": "2026-03-24T14:36:00.000Z",
    "duration_ms": 4520
  }
}
```

**Data shape:** `AgentInvocationResult` (INTERACTION-MAP 2.10)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | 404 | agent_id does not exist |
| `INVALID_PROJECT` | 404 | project_id does not exist |
| `BUDGET_EXCEEDED` | 422 | Project budget exceeded |
| `AGENT_UNHEALTHY` | 503 | Agent health check failing |
| `INVOCATION_TIMEOUT` | 504 | Exceeded timeout |
| `AGENT_VERSION_DEPRECATED` | 422 | Agent version is deprecated |

---

#### GET /agents/{agent_id}/health — Check Agent Health

| Field | Value |
|---|---|
| **Interaction ID** | I-023 |
| **MCP Tool** | `check_agent_health` |
| **Dashboard Screen** | S-004 Health Badges |
| **Shared Service** | `AgentService.health_check()` |
| **Auth** | JWT or API Key (read) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `agent_id` | string | Agent identifier. Use special value `_all` for fleet-wide check |

**Response:** `200 OK`

Single agent:
```json
{
  "data": {
    "agent_id": "P1-prd-writer",
    "healthy": true,
    "last_check_at": "2026-03-24T14:34:00.000Z",
    "response_time_ms": 34,
    "error_message": null,
    "consecutive_failures": 0,
    "circuit_breaker_open": false
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440023",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 45
  }
}
```

**Data shape:** `AgentHealth` (INTERACTION-MAP 2.7) or `AgentHealth[]` when `agent_id` is `_all`

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | 404 | agent_id does not exist |

---

#### POST /agents/{agent_id}/promote — Promote Agent Version

| Field | Value |
|---|---|
| **Interaction ID** | I-024 |
| **MCP Tool** | `promote_agent_version` |
| **Dashboard Screen** | S-005 Version Management |
| **Shared Service** | `AgentService.promote_version()` |
| **Auth** | JWT or API Key (admin role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `agent_id` | string | Agent identifier |

**Request Body:**

```json
{
  "target_maturity": "ga",
  "justification": "Sustained 98% success rate over 30 days with zero overrides"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `target_maturity` | string | Yes | `beta` or `ga` |
| `justification` | string | No | Max 1000 chars, recorded in audit |

**Response:** `200 OK`

```json
{
  "data": {
    "agent_id": "P1-prd-writer",
    "active_version": "1.2.0",
    "canary_version": null,
    "canary_traffic_pct": 0,
    "previous_version": "1.1.0",
    "promoted_at": "2026-03-24T14:40:00.000Z",
    "rolled_back_at": null
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440024",
    "timestamp": "2026-03-24T14:40:00.000Z",
    "duration_ms": 78
  }
}
```

**Data shape:** `AgentVersion` (INTERACTION-MAP 2.8)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | 404 | agent_id does not exist |
| `INVALID_PROMOTION_PATH` | 422 | Invalid maturity transition |
| `PROMOTION_CRITERIA_NOT_MET` | 422 | Agent does not meet threshold |

---

#### POST /agents/{agent_id}/rollback — Rollback Agent Version

| Field | Value |
|---|---|
| **Interaction ID** | I-025 |
| **MCP Tool** | `rollback_agent_version` |
| **Dashboard Screen** | S-005 Version Management |
| **Shared Service** | `AgentService.rollback_version()` |
| **Auth** | JWT or API Key (admin role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `agent_id` | string | Agent identifier |

**Request Body:**

```json
{
  "target_version": "v1.1.0",
  "reason": "v1.2.0 showing increased error rate in production"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `target_version` | string | No | Semver, omit for previous version |
| `reason` | string | No | Max 1000 chars, recorded in audit |

**Response:** `200 OK`

```json
{
  "data": {
    "agent_id": "P1-prd-writer",
    "active_version": "1.1.0",
    "canary_version": null,
    "canary_traffic_pct": 0,
    "previous_version": "1.2.0",
    "promoted_at": null,
    "rolled_back_at": "2026-03-24T14:42:00.000Z"
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440025",
    "timestamp": "2026-03-24T14:42:00.000Z",
    "duration_ms": 92
  }
}
```

**Data shape:** `AgentVersion` (INTERACTION-MAP 2.8)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | 404 | agent_id does not exist |
| `VERSION_NOT_FOUND` | 404 | target_version does not exist |
| `NO_PREVIOUS_VERSION` | 409 | No previous version to roll back to |

---

#### PATCH /agents/{agent_id}/canary — Set Canary Traffic

| Field | Value |
|---|---|
| **Interaction ID** | I-026 |
| **MCP Tool** | `set_canary_traffic` |
| **Dashboard Screen** | S-005 Version Management |
| **Shared Service** | `AgentService.set_canary()` |
| **Auth** | JWT or API Key (admin role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `agent_id` | string | Agent identifier |

**Request Body:**

```json
{
  "traffic_pct": 25
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `traffic_pct` | integer | Yes | 0-100. 0 disables canary. |

**Response:** `200 OK`

```json
{
  "data": {
    "agent_id": "P1-prd-writer",
    "active_version": "1.2.0",
    "canary_version": "1.3.0-rc1",
    "canary_traffic_pct": 25,
    "previous_version": "1.1.0",
    "promoted_at": null,
    "rolled_back_at": null
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440026",
    "timestamp": "2026-03-24T14:43:00.000Z",
    "duration_ms": 34
  }
}
```

**Data shape:** `AgentVersion` (INTERACTION-MAP 2.8)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | 404 | agent_id does not exist |
| `NO_CANARY_VERSION` | 409 | No canary version deployed |
| `INVALID_TRAFFIC_PCT` | 400 | traffic_pct outside 0-100 range |

---

#### GET /agents/{agent_id}/maturity — Get Agent Maturity

| Field | Value |
|---|---|
| **Interaction ID** | I-027 |
| **MCP Tool** | `get_agent_maturity` |
| **Dashboard Screen** | S-006 Maturity Badges |
| **Shared Service** | `AgentService.get_maturity()` |
| **Auth** | JWT or API Key (read) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `agent_id` | string | Agent identifier |

**Response:** `200 OK`

```json
{
  "data": {
    "agent_id": "P1-prd-writer",
    "current_level": "assisted",
    "override_rate": 0.05,
    "confidence_avg": 0.91,
    "consecutive_days": 14,
    "next_level": "autonomous",
    "promotion_eligible": true,
    "promotion_criteria": "Override rate < 3% for 21 consecutive days"
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440027",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 8
  }
}
```

**Data shape:** `AgentMaturity` (INTERACTION-MAP 2.9)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | 404 | agent_id does not exist |

---

### 7.3 Cost & Budget (`/api/v1/cost`, `/api/v1/budget`)

---

#### GET /cost/report — Get Cost Report

| Field | Value |
|---|---|
| **Interaction ID** | I-040 |
| **MCP Tool** | `get_cost_report` |
| **Dashboard Screen** | S-010 Cost Charts |
| **Shared Service** | `CostService.get_report()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `scope` | string | `fleet` | `fleet`, `project`, `agent` |
| `entity_id` | string | — | Required for `project` and `agent` scope |
| `period_days` | integer | 7 | `1`, `7`, `30`, `90` |

**Response:** `200 OK`

```json
{
  "data": {
    "scope": "fleet",
    "entity_id": null,
    "period_days": 7,
    "total_usd": 142.50,
    "breakdown": [
      {
        "entity_id": "P1-prd-writer",
        "entity_name": "PRD Writer",
        "cost_usd": 16.80,
        "invocation_count": 84,
        "avg_cost_per_invocation": 0.20,
        "tokens_total": 420000
      },
      {
        "entity_id": "B1-code-reviewer",
        "entity_name": "Code Reviewer",
        "cost_usd": 31.20,
        "invocation_count": 52,
        "avg_cost_per_invocation": 0.60,
        "tokens_total": 780000
      }
    ],
    "generated_at": "2026-03-24T14:35:00.000Z",
    "trend_pct": -5.2,
    "by_provider": [
      {
        "provider": "anthropic",
        "cost_usd": 128.70,
        "invocation_count": 620,
        "pct_of_total": 90.3
      },
      {
        "provider": "openai",
        "cost_usd": 13.80,
        "invocation_count": 48,
        "pct_of_total": 9.7
      }
    ]
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440040",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 95
  }
}
```

**Data shape:** `CostReport` (INTERACTION-MAP 2.11)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_SCOPE` | 400 | Unknown scope value |
| `ENTITY_NOT_FOUND` | 404 | entity_id not found for given scope |
| `INVALID_PERIOD` | 400 | period_days not in allowed values |

---

#### GET /budget/{scope}/{entity_id} — Check Budget

| Field | Value |
|---|---|
| **Interaction ID** | I-041 |
| **MCP Tool** | `check_budget` |
| **Dashboard Screen** | S-011 Budget Gauges |
| **Shared Service** | `CostService.check_budget()` |
| **Auth** | JWT or API Key (read) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `scope` | string | `fleet`, `project`, `agent` |
| `entity_id` | string | Entity identifier (use `_fleet` for fleet scope) |

**Response:** `200 OK`

```json
{
  "data": {
    "scope": "project",
    "entity_id": "proj_abc123def456",
    "budget_usd": 50.00,
    "spent_usd": 42.30,
    "remaining_usd": 7.70,
    "utilization_pct": 84.6,
    "at_risk": true,
    "alert_threshold_pct": 80,
    "projected_overrun_date": "2026-03-26T00:00:00.000Z"
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440041",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 15
  }
}
```

**Data shape:** `BudgetStatus` (INTERACTION-MAP 2.12)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_SCOPE` | 400 | Unknown scope value |
| `ENTITY_NOT_FOUND` | 404 | entity_id not found |
| `NO_BUDGET_CONFIGURED` | 404 | No budget set for entity |

---

#### GET /cost/anomalies — Get Cost Anomalies

| Field | Value |
|---|---|
| **Interaction ID** | I-048 |
| **MCP Tool** | `get_cost_anomalies` |
| **Dashboard Screen** | S-012 Anomaly Alerts |
| **Shared Service** | `CostService.get_anomalies()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `severity` | string | — | Filter: `low`, `medium`, `high`, `critical` |
| `acknowledged` | boolean | — | Filter by acknowledgment status |
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (1-50) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "anomaly_id": "880e8400-e29b-41d4-a716-446655440050",
      "entity_id": "B1-code-reviewer",
      "entity_type": "agent",
      "entity_name": "Code Reviewer",
      "expected_usd": 4.20,
      "actual_usd": 12.60,
      "deviation_pct": 200.0,
      "detected_at": "2026-03-24T13:00:00.000Z",
      "severity": "high",
      "acknowledged": false,
      "acknowledged_by": null
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440048",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 22
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 3,
    "total_pages": 1
  }
}
```

**Data shape:** `CostAnomaly[]` (INTERACTION-MAP 2.13)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_SEVERITY` | 400 | Unknown severity value |

---

#### PATCH /budget/{scope}/{entity_id}/threshold — Update Budget Threshold

| Field | Value |
|---|---|
| **Interaction ID** | I-049 |
| **MCP Tool** | `update_budget_threshold` |
| **Dashboard Screen** | S-013 Budget Settings |
| **Shared Service** | `CostService.set_threshold()` |
| **Auth** | JWT or API Key (admin role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `scope` | string | `fleet`, `project`, `agent` |
| `entity_id` | string | Entity identifier |

**Request Body:**

```json
{
  "alert_threshold_pct": 75,
  "budget_usd": 100.00
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `alert_threshold_pct` | integer | No | 1-100, alert when utilization exceeds this |
| `budget_usd` | number | No | New budget amount (must be >= current spend) |

**Response:** `200 OK`

```json
{
  "data": {
    "scope": "project",
    "entity_id": "proj_abc123def456",
    "budget_usd": 100.00,
    "spent_usd": 42.30,
    "remaining_usd": 57.70,
    "utilization_pct": 42.3,
    "at_risk": false,
    "alert_threshold_pct": 75,
    "projected_overrun_date": null
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440049",
    "timestamp": "2026-03-24T14:45:00.000Z",
    "duration_ms": 28
  }
}
```

**Data shape:** `BudgetStatus` (INTERACTION-MAP 2.12)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_SCOPE` | 400 | Unknown scope value |
| `ENTITY_NOT_FOUND` | 404 | entity_id not found |
| `BUDGET_BELOW_SPEND` | 422 | New budget_usd is less than current spent_usd |
| `INVALID_THRESHOLD` | 400 | alert_threshold_pct outside 1-100 |

---

### 7.4 Audit (`/api/v1/audit`)

---

#### GET /audit/events — Query Audit Events

| Field | Value |
|---|---|
| **Interaction ID** | I-042 |
| **MCP Tool** | `query_audit_events` |
| **Dashboard Screen** | S-030 Audit Event Table |
| **Shared Service** | `AuditService.query_events()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `agent_id` | string | — | Filter by agent |
| `severity` | string | — | Filter: `info`, `warning`, `error`, `critical` |
| `action` | string | — | Filter by action type (e.g., `pipeline.trigger`) |
| `project_id` | string | — | Filter by project |
| `since` | ISO 8601 | — | Events after this timestamp |
| `until` | ISO 8601 | — | Events before this timestamp |
| `page` | integer | 1 | Page number |
| `per_page` | integer | 50 | Items per page (1-200) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "event_id": "990e8400-e29b-41d4-a716-446655440060",
      "timestamp": "2026-03-24T14:30:00.000Z",
      "agent_id": "P1-prd-writer",
      "session_id": "sess_abc123",
      "project_id": "proj_abc123def456",
      "action": "pipeline.trigger",
      "severity": "info",
      "details": {
        "template": "full-stack-first",
        "run_id": "run_a1b2c3d4e5f6g7h8"
      },
      "cost_usd": 0.00,
      "tokens_in": 0,
      "tokens_out": 0,
      "duration_ms": 156,
      "pii_detected": false,
      "source_ip": "10.0.1.42",
      "user_id": "user_priya"
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440042",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 48
  },
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 1247,
    "total_pages": 25
  }
}
```

**Data shape:** `AuditEvent[]` (INTERACTION-MAP 2.14)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_DATE_RANGE` | 400 | Malformed since/until timestamps |
| `INVALID_SEVERITY` | 400 | Unknown severity value |

---

#### GET /audit/summary — Get Audit Summary

| Field | Value |
|---|---|
| **Interaction ID** | I-043 |
| **MCP Tool** | `get_audit_summary` |
| **Dashboard Screen** | S-031 Audit Summary Cards |
| **Shared Service** | `AuditService.get_summary()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `since` | ISO 8601 | Start of today | Period start |
| `until` | ISO 8601 | Now | Period end |

**Response:** `200 OK`

```json
{
  "data": {
    "period": "2026-03-24T00:00:00.000Z/2026-03-24T14:35:00.000Z",
    "total_events": 1247,
    "by_severity": {
      "info": 1100,
      "warning": 120,
      "error": 25,
      "critical": 2
    },
    "by_agent": {
      "P1-prd-writer": 180,
      "B1-code-reviewer": 245,
      "P3-api-gen": 92
    },
    "by_project": {
      "proj_abc123def456": 520,
      "proj_xyz789ghijkl": 310
    },
    "by_action": {
      "agent.invoke": 890,
      "pipeline.trigger": 12,
      "approval.approve": 8
    },
    "total_cost_usd": 142.50,
    "pii_detections": 3
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440043",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 120
  }
}
```

**Data shape:** `AuditSummary` (INTERACTION-MAP 2.15)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_DATE_RANGE` | 400 | Malformed since/until or since > until |

---

#### GET /audit/export — Export Audit Report

| Field | Value |
|---|---|
| **Interaction ID** | I-044 |
| **MCP Tool** | `export_audit_report` |
| **Dashboard Screen** | S-032 Audit Export Button |
| **Shared Service** | `AuditService.export_report()` |
| **Auth** | JWT or API Key (operator role) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `format` | string | `pdf` | `pdf`, `csv`, `json` |
| `since` | ISO 8601 | Start of today | Period start |
| `until` | ISO 8601 | Now | Period end |
| `agent_id` | string | — | Filter by agent |
| `severity` | string | — | Minimum severity to include |

**Response:** `200 OK`

```json
{
  "data": {
    "report_id": "aa0e8400-e29b-41d4-a716-446655440070",
    "format": "pdf",
    "period": "2026-03-24T00:00:00.000Z/2026-03-24T14:35:00.000Z",
    "filters_applied": {
      "severity": "warning"
    },
    "generated_at": "2026-03-24T14:35:30.000Z",
    "download_url": "https://storage.agentic-sdlc.io/audit-reports/aa0e8400.pdf?token=xyz&expires=1711291130",
    "size_bytes": 245760,
    "record_count": 147
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440044",
    "timestamp": "2026-03-24T14:35:30.000Z",
    "duration_ms": 3200
  }
}
```

**Data shape:** `AuditReport` (INTERACTION-MAP 2.16)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_DATE_RANGE` | 400 | Malformed since/until |
| `EXPORT_TOO_LARGE` | 422 | Requested period contains > 100000 events |
| `EXPORT_IN_PROGRESS` | 409 | A report is already being generated for this user |

---

#### GET /audit/mcp-calls — List Recent MCP Calls

| Field | Value |
|---|---|
| **Interaction ID** | I-082 |
| **MCP Tool** | `list_recent_mcp_calls` |
| **Dashboard Screen** | S-007 MCP Monitoring Panel |
| **Shared Service** | `AuditService.list_mcp_calls()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `server_name` | string | — | Filter: `agents-server`, `governance-server`, `knowledge-server` |
| `tool_name` | string | — | Filter by specific MCP tool |
| `status` | string | — | Filter: `success`, `error`, `timeout` |
| `limit` | integer | 50 | Max results (1-200) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "call_id": "bb0e8400-e29b-41d4-a716-446655440080",
      "timestamp": "2026-03-24T14:34:42.000Z",
      "server_name": "agents-server",
      "tool_name": "trigger_pipeline",
      "caller": "claude-code-session-abc",
      "project_id": "proj_abc123def456",
      "duration_ms": 156,
      "status": "success",
      "error_message": null,
      "tokens_used": 3200,
      "cost_usd": 0.08
    },
    {
      "call_id": "bb0e8400-e29b-41d4-a716-446655440081",
      "timestamp": "2026-03-24T14:34:38.000Z",
      "server_name": "agents-server",
      "tool_name": "list_agents",
      "caller": "claude-code-session-abc",
      "project_id": null,
      "duration_ms": 22,
      "status": "success",
      "error_message": null,
      "tokens_used": 800,
      "cost_usd": 0.02
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440082",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 18
  }
}
```

**Data shape:** `McpCallEvent[]` (INTERACTION-MAP 2.22)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_SERVER_NAME` | 400 | Unknown MCP server name |

---

### 7.5 Approvals (`/api/v1/approvals`)

---

#### GET /approvals — List Pending Approvals

| Field | Value |
|---|---|
| **Interaction ID** | I-045 |
| **MCP Tool** | `list_pending_approvals` |
| **Dashboard Screen** | S-040 Approval Queue Table, S-041 Approval Detail Panel, S-042 Approval History Tab |
| **Shared Service** | `ApprovalService.list_pending()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `status` | string | `pending` | Filter: `pending`, `approved`, `rejected`, `expired`, `escalated`. Comma-separated for multiple. |
| `risk_level` | string | — | Filter: `low`, `medium`, `high`, `critical` |
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (1-50) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "approval_id": "cc0e8400-e29b-41d4-a716-446655440090",
      "session_id": "sess_abc123",
      "run_id": "run_a1b2c3d4e5f6g7h8",
      "pipeline_name": "full-stack-first-14-doc",
      "step_number": 6,
      "step_name": "06-INTERACTION-MAP",
      "summary": "Pipeline run for proj_abc123def456 has reached the INTERACTION-MAP stage. This is a key coordination document that requires human review before MCP-TOOL-SPEC and DESIGN-SPEC are generated.",
      "risk_level": "high",
      "status": "pending",
      "requested_at": "2026-03-24T14:35:00.000Z",
      "expires_at": "2026-03-24T15:35:00.000Z",
      "decided_at": null,
      "decision_by": null,
      "decision_comment": null,
      "context": {
        "documents_generated": 6,
        "cost_so_far_usd": 8.42,
        "previous_step_quality_score": 0.94
      }
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440045",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 14
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 2,
    "total_pages": 1
  }
}
```

**Data shape:** `ApprovalRequest[]` (INTERACTION-MAP 2.17)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_STATUS` | 400 | Unknown status value |

---

#### POST /approvals/{approval_id}/approve — Approve Gate

| Field | Value |
|---|---|
| **Interaction ID** | I-046 |
| **MCP Tool** | `approve_gate` |
| **Dashboard Screen** | S-041 Approval Detail Panel |
| **Shared Service** | `ApprovalService.approve()` |
| **Auth** | JWT or API Key (operator role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `approval_id` | string | UUID of the approval request |

**Request Body:**

```json
{
  "comment": "INTERACTION-MAP reviewed and approved. Data shapes look consistent with PRD requirements."
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `comment` | string | No | Max 2000 chars. Optional for approvals. |

**Response:** `200 OK`

```json
{
  "data": {
    "approval_id": "cc0e8400-e29b-41d4-a716-446655440090",
    "status": "approved",
    "decided_at": "2026-03-24T14:40:00.000Z",
    "decision_by": "user_anika",
    "decision_comment": "INTERACTION-MAP reviewed and approved. Data shapes look consistent with PRD requirements.",
    "pipeline_resumed": true
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440046",
    "timestamp": "2026-03-24T14:40:00.000Z",
    "duration_ms": 145
  }
}
```

**Data shape:** `ApprovalResult` (INTERACTION-MAP 2.18)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `APPROVAL_NOT_FOUND` | 404 | approval_id does not exist |
| `APPROVAL_ALREADY_DECIDED` | 409 | Approval already approved or rejected |
| `APPROVAL_EXPIRED` | 410 | Approval has expired |

---

#### POST /approvals/{approval_id}/reject — Reject Gate

| Field | Value |
|---|---|
| **Interaction ID** | I-047 |
| **MCP Tool** | `reject_gate` |
| **Dashboard Screen** | S-041 Approval Detail Panel |
| **Shared Service** | `ApprovalService.reject()` |
| **Auth** | JWT or API Key (operator role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `approval_id` | string | UUID of the approval request |

**Request Body:**

```json
{
  "comment": "Data shapes for CostReport are missing the breakdown field. Please regenerate with cost breakdown included."
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `comment` | string | **Yes** | Max 2000 chars. **Required** for rejections. |

**Response:** `200 OK`

```json
{
  "data": {
    "approval_id": "cc0e8400-e29b-41d4-a716-446655440090",
    "status": "rejected",
    "decided_at": "2026-03-24T14:40:00.000Z",
    "decision_by": "user_anika",
    "decision_comment": "Data shapes for CostReport are missing the breakdown field. Please regenerate with cost breakdown included.",
    "pipeline_resumed": false
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440047",
    "timestamp": "2026-03-24T14:40:00.000Z",
    "duration_ms": 67
  }
}
```

**Data shape:** `ApprovalResult` (INTERACTION-MAP 2.18)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `APPROVAL_NOT_FOUND` | 404 | approval_id does not exist |
| `APPROVAL_ALREADY_DECIDED` | 409 | Approval already approved or rejected |
| `APPROVAL_EXPIRED` | 410 | Approval has expired |
| `COMMENT_REQUIRED` | 400 | Rejection requires a comment |

---

### 7.6 Knowledge (`/api/v1/knowledge`)

---

#### GET /knowledge/exceptions/search — Search Exceptions

| Field | Value |
|---|---|
| **Interaction ID** | I-060 |
| **MCP Tool** | `search_exceptions` |
| **Dashboard Screen** | — (MCP/REST only) |
| **Shared Service** | `KnowledgeService.search()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `q` | string | — | Keyword or rule pattern to search for |
| `tier` | string | — | Filter: `client`, `stack`, `universal` |
| `severity` | string | — | Filter: `low`, `medium`, `high`, `critical` |
| `active` | boolean | — | Filter by active status |
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (1-100) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "exception_id": "dd0e8400-e29b-41d4-a716-446655440100",
      "title": "Allow snake_case in REST API paths",
      "rule": "rest-api-naming:allow-snake-case",
      "description": "Exception to the standard kebab-case REST path convention for legacy API compatibility",
      "severity": "low",
      "tier": "client",
      "stack_name": null,
      "client_id": "client_acme",
      "active": true,
      "fire_count": 42,
      "last_fired_at": "2026-03-24T12:00:00.000Z",
      "created_at": "2026-03-01T10:00:00.000Z",
      "created_by": "user_priya",
      "tags": ["rest", "naming", "legacy"]
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440060",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 32
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 8,
    "total_pages": 1
  }
}
```

**Data shape:** `KnowledgeException[]` (INTERACTION-MAP 2.19)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_TIER` | 400 | Unknown tier value |

---

#### POST /knowledge/exceptions — Create Exception

| Field | Value |
|---|---|
| **Interaction ID** | I-061 |
| **MCP Tool** | `create_exception` |
| **Dashboard Screen** | — (MCP/REST only) |
| **Shared Service** | `KnowledgeService.create()` |
| **Auth** | JWT or API Key (operator role) |

**Request Body:**

```json
{
  "title": "Allow inline SQL for reporting queries",
  "rule": "code-quality:no-inline-sql:exception",
  "description": "Reporting module requires complex SQL that is not suitable for ORM abstraction",
  "severity": "medium",
  "client_id": "client_acme",
  "tags": ["sql", "reporting", "performance"]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | Yes | Human-readable title, max 200 chars |
| `rule` | string | Yes | Exception rule pattern |
| `description` | string | Yes | Detailed explanation, max 2000 chars |
| `severity` | string | Yes | `low`, `medium`, `high`, `critical` |
| `client_id` | string | No | Client scoping. Creates at `client` tier. |
| `tags` | string[] | No | Searchable tags |

**Response:** `201 Created`

```json
{
  "data": {
    "exception_id": "dd0e8400-e29b-41d4-a716-446655440101",
    "title": "Allow inline SQL for reporting queries",
    "rule": "code-quality:no-inline-sql:exception",
    "description": "Reporting module requires complex SQL that is not suitable for ORM abstraction",
    "severity": "medium",
    "tier": "client",
    "stack_name": null,
    "client_id": "client_acme",
    "active": true,
    "fire_count": 0,
    "last_fired_at": null,
    "created_at": "2026-03-24T14:45:00.000Z",
    "created_by": "user_priya",
    "tags": ["sql", "reporting", "performance"]
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440061",
    "timestamp": "2026-03-24T14:45:00.000Z",
    "duration_ms": 45
  }
}
```

**Data shape:** `KnowledgeException` (INTERACTION-MAP 2.19)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `DUPLICATE_RULE` | 409 | Rule pattern already exists for this tier/client |
| `INVALID_SEVERITY` | 400 | Unknown severity value |
| `CLIENT_NOT_FOUND` | 404 | client_id does not exist |

---

#### POST /knowledge/exceptions/{exception_id}/promote — Promote Exception

| Field | Value |
|---|---|
| **Interaction ID** | I-062 |
| **MCP Tool** | `promote_exception` |
| **Dashboard Screen** | — (MCP/REST only) |
| **Shared Service** | `KnowledgeService.promote()` |
| **Auth** | JWT or API Key (admin role) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `exception_id` | string | UUID of the exception |

**Request Body:**

```json
{
  "target_tier": "stack",
  "stack_name": "python-fastapi"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `target_tier` | string | Yes | `stack` or `universal` |
| `stack_name` | string | Conditional | Required when target_tier is `stack` |

**Response:** `200 OK`

```json
{
  "data": {
    "exception_id": "dd0e8400-e29b-41d4-a716-446655440101",
    "title": "Allow inline SQL for reporting queries",
    "rule": "code-quality:no-inline-sql:exception",
    "description": "Reporting module requires complex SQL that is not suitable for ORM abstraction",
    "severity": "medium",
    "tier": "stack",
    "stack_name": "python-fastapi",
    "client_id": null,
    "active": true,
    "fire_count": 42,
    "last_fired_at": "2026-03-24T12:00:00.000Z",
    "created_at": "2026-03-01T10:00:00.000Z",
    "created_by": "user_priya",
    "tags": ["sql", "reporting", "performance"]
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440062",
    "timestamp": "2026-03-24T14:46:00.000Z",
    "duration_ms": 38
  }
}
```

**Data shape:** `KnowledgeException` (INTERACTION-MAP 2.19)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `EXCEPTION_NOT_FOUND` | 404 | exception_id does not exist |
| `INVALID_PROMOTION_PATH` | 422 | Cannot promote from current tier to target (e.g., universal cannot be promoted) |
| `STACK_NOT_FOUND` | 404 | stack_name does not exist |

---

#### GET /knowledge/exceptions — List Exceptions by Tier

| Field | Value |
|---|---|
| **Interaction ID** | I-063 |
| **MCP Tool** | `list_exceptions` |
| **Dashboard Screen** | — (MCP/REST only; future Dashboard) |
| **Shared Service** | `KnowledgeService.list_by_tier()` |
| **Auth** | JWT or API Key (read) |

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `tier` | string | — | Filter: `client`, `stack`, `universal` |
| `active` | boolean | true | Filter by active status |
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Items per page (1-100) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "exception_id": "dd0e8400-e29b-41d4-a716-446655440100",
      "title": "Allow snake_case in REST API paths",
      "rule": "rest-api-naming:allow-snake-case",
      "description": "Exception to the standard kebab-case REST path convention for legacy API compatibility",
      "severity": "low",
      "tier": "universal",
      "stack_name": null,
      "client_id": null,
      "active": true,
      "fire_count": 420,
      "last_fired_at": "2026-03-24T14:00:00.000Z",
      "created_at": "2026-01-15T10:00:00.000Z",
      "created_by": "user_admin",
      "tags": ["rest", "naming"]
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440063",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 18
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 15,
    "total_pages": 1
  }
}
```

**Data shape:** `KnowledgeException[]` (INTERACTION-MAP 2.19)

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_TIER` | 400 | Unknown tier value |

---

### 7.7 System (`/api/v1/system`)

---

#### GET /system/health — Get Fleet Health

| Field | Value |
|---|---|
| **Interaction ID** | I-080 |
| **MCP Tool** | `get_fleet_health` |
| **Dashboard Screen** | S-001 Fleet Health Overview |
| **Shared Service** | `HealthService.get_fleet_health()` |
| **Auth** | None (public for load balancer probes) or JWT/API Key |

**Response:** `200 OK`

```json
{
  "data": {
    "healthy_agents": 46,
    "total_agents": 48,
    "by_phase": {
      "plan": { "total": 10, "healthy": 10 },
      "design": { "total": 12, "healthy": 11 },
      "build": { "total": 14, "healthy": 13 },
      "verify": { "total": 8, "healthy": 8 },
      "deploy": { "total": 4, "healthy": 4 }
    },
    "by_status": {
      "active": 44,
      "degraded": 2,
      "offline": 0,
      "canary": 2
    },
    "circuit_breakers_open": 1,
    "avg_response_ms": 34,
    "p95_response_ms": 142,
    "fleet_cost_today_usd": 142.50,
    "active_pipelines": 3,
    "pending_approvals": 2,
    "last_updated_at": "2026-03-24T14:34:50.000Z"
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440080",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 8
  }
}
```

**Data shape:** `FleetHealth` (INTERACTION-MAP 2.20)

**Error Codes:** None (always returns 200; degraded subsystems reflected in the data).

---

#### GET /system/mcp — Get MCP Server Status

| Field | Value |
|---|---|
| **Interaction ID** | I-081 |
| **MCP Tool** | `get_mcp_status` |
| **Dashboard Screen** | S-007 MCP Monitoring Panel |
| **Shared Service** | `HealthService.get_mcp_status()` |
| **Auth** | JWT or API Key (read) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "server_name": "agents-server",
      "healthy": true,
      "uptime_seconds": 864000,
      "tool_count": 18,
      "active_connections": 3,
      "requests_per_minute": 12.5,
      "error_rate_pct": 0.2,
      "version": "1.4.0",
      "last_restart_at": "2026-03-14T06:00:00.000Z"
    },
    {
      "server_name": "governance-server",
      "healthy": true,
      "uptime_seconds": 864000,
      "tool_count": 10,
      "active_connections": 1,
      "requests_per_minute": 4.2,
      "error_rate_pct": 0.0,
      "version": "1.4.0",
      "last_restart_at": "2026-03-14T06:00:00.000Z"
    },
    {
      "server_name": "knowledge-server",
      "healthy": true,
      "uptime_seconds": 864000,
      "tool_count": 4,
      "active_connections": 1,
      "requests_per_minute": 1.8,
      "error_rate_pct": 0.0,
      "version": "1.4.0",
      "last_restart_at": "2026-03-14T06:00:00.000Z"
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440081",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 12
  }
}
```

**Data shape:** `McpServerStatus[]` (INTERACTION-MAP 2.21)

**Error Codes:** None (always returns 200; unhealthy servers reflected in data).

---

#### GET /system/providers — List Available LLM Providers

| Field | Value |
|---|---|
| **Interaction ID** | — (REST-only) |
| **MCP Tool** | — |
| **Dashboard Screen** | S-001 Fleet Health Overview (LLM Provider Status) |
| **Shared Service** | `ProviderService.list_providers()` |
| **Auth** | JWT or API Key (read) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "name": "anthropic",
      "enabled": true,
      "healthy": true,
      "models": ["claude-sonnet-4-6", "claude-haiku-3", "claude-opus-4-6"],
      "tier_mapping": {
        "fast": "claude-haiku-3",
        "balanced": "claude-sonnet-4-6",
        "powerful": "claude-opus-4-6"
      },
      "agent_count": 44
    },
    {
      "name": "openai",
      "enabled": true,
      "healthy": true,
      "models": ["gpt-4o-mini", "gpt-4o", "o3"],
      "tier_mapping": {
        "fast": "gpt-4o-mini",
        "balanced": "gpt-4o",
        "powerful": "o3"
      },
      "agent_count": 4
    },
    {
      "name": "ollama",
      "enabled": false,
      "healthy": null,
      "models": [],
      "tier_mapping": {},
      "agent_count": 0
    }
  ],
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440082",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 5
  }
}
```

**Data shape:** `LLMProviderInfo[]`

**Notes:** The `tier_mapping` shows how abstract tiers (`fast`, `balanced`, `powerful`) resolve to concrete model IDs for each provider. Agents declare a tier in their manifest rather than a hardcoded model ID. The platform resolves the tier to a model at invocation time via `sdk/llm/LLMProvider`.

---

#### GET /system/providers/{name}/health — Check Provider Health

| Field | Value |
|---|---|
| **Interaction ID** | — (REST-only) |
| **MCP Tool** | — |
| **Dashboard Screen** | S-001 Fleet Health Overview (LLM Provider Status) |
| **Shared Service** | `ProviderService.check_health(name)` |
| **Auth** | JWT or API Key (read) |

**Path Parameters:**

| Param | Type | Description |
|---|---|---|
| `name` | string | Provider name: `anthropic`, `openai`, `ollama` |

**Response:** `200 OK`

```json
{
  "data": {
    "name": "anthropic",
    "healthy": true,
    "latency_ms": 120,
    "last_check_at": "2026-03-24T14:34:50.000Z",
    "error_rate_pct": 0.1,
    "models_available": ["claude-sonnet-4-6", "claude-haiku-3", "claude-opus-4-6"],
    "rate_limit_remaining": 850,
    "rate_limit_total": 1000
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440083",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 125
  }
}
```

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `PROVIDER_NOT_FOUND` | 404 | Unknown provider name |

---

### 7.8 Auth (`/api/v1/auth`)

These endpoints are REST-only (no MCP equivalent). They manage dashboard session authentication.

---

#### POST /auth/login — Login

| Field | Value |
|---|---|
| **Interaction ID** | — (REST-only) |
| **MCP Tool** | — |
| **Dashboard Screen** | Login page |
| **Shared Service** | `AuthService.login()` |
| **Auth** | None |

**Request Body:**

```json
{
  "email": "anika@example.com",
  "password": "********"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | Yes | User email address |
| `password` | string | Yes | User password |

**Response:** `200 OK`

```json
{
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "refresh_token": "rt_abc123def456ghi789jkl012mno345pqr678stu901vwx234",
    "user": {
      "user_id": "user_anika",
      "email": "anika@example.com",
      "name": "Anika Patel",
      "roles": ["operator"]
    }
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440090",
    "timestamp": "2026-03-24T14:00:00.000Z",
    "duration_ms": 120
  }
}
```

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `ACCOUNT_LOCKED` | 403 | Too many failed attempts |
| `ACCOUNT_DISABLED` | 403 | Account is disabled |

---

#### POST /auth/refresh — Refresh JWT

| Field | Value |
|---|---|
| **Interaction ID** | — (REST-only) |
| **MCP Tool** | — |
| **Dashboard Screen** | Automatic (background) |
| **Shared Service** | `AuthService.refresh()` |
| **Auth** | Refresh token in body |

**Request Body:**

```json
{
  "refresh_token": "rt_abc123def456ghi789jkl012mno345pqr678stu901vwx234"
}
```

**Response:** `200 OK`

```json
{
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "refresh_token": "rt_new123def456ghi789jkl012mno345pqr678stu901vwx234"
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440091",
    "timestamp": "2026-03-24T14:30:00.000Z",
    "duration_ms": 18
  }
}
```

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `INVALID_REFRESH_TOKEN` | 401 | Refresh token expired or invalid |
| `TOKEN_REVOKED` | 401 | Refresh token has been revoked |

---

#### GET /auth/me — Current User

| Field | Value |
|---|---|
| **Interaction ID** | — (REST-only) |
| **MCP Tool** | — |
| **Dashboard Screen** | User profile dropdown |
| **Shared Service** | `AuthService.get_current_user()` |
| **Auth** | JWT (Bearer token) |

**Response:** `200 OK`

```json
{
  "data": {
    "user_id": "user_anika",
    "email": "anika@example.com",
    "name": "Anika Patel",
    "roles": ["operator"],
    "last_login_at": "2026-03-24T14:00:00.000Z",
    "api_key_count": 2
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440092",
    "timestamp": "2026-03-24T14:35:00.000Z",
    "duration_ms": 5
  }
}
```

**Error Codes:**

| Error Code | HTTP Status | Condition |
|---|---|---|
| `UNAUTHORIZED` | 401 | Missing or invalid JWT |

---

## 8. WebSocket / SSE Channels

Real-time channels provide push updates for dashboard screens that need live data. All channels use WebSocket with JSON messages and fall back to SSE for environments that do not support WebSocket.

### Authentication

All WebSocket connections require authentication via query parameter:
- JWT: `ws://host/ws/pipelines/{run_id}?token=<jwt>`
- API Key: `ws://host/ws/pipelines/{run_id}?api_key=<key>`

### Reconnection Strategy

- Initial reconnect delay: 1 second
- Backoff multiplier: 2x
- Maximum delay: 30 seconds
- Maximum attempts: unlimited (dashboard should always try to reconnect)
- On reconnect, client sends last received event ID for gap recovery

---

### Channel: Pipeline Progress

**URL:** `ws://host/ws/pipelines/{run_id}`

**Dashboard screen:** S-022 Pipeline Run Detail

**Message format:**

```json
{
  "event": "pipeline.step_completed",
  "data": {
    "run_id": "run_a1b2c3d4e5f6g7h8",
    "step_number": 6,
    "step_name": "06-INTERACTION-MAP",
    "status": "completed",
    "cost_usd": 1.20,
    "quality_score": 0.94,
    "next_step": 7,
    "next_step_name": "07-MCP-TOOL-SPEC",
    "pipeline_status": "running",
    "overall_progress_pct": 50
  },
  "timestamp": "2026-03-24T14:38:00.000Z",
  "event_id": "evt_001"
}
```

**Event types:**

| Event | Description | Data Shape Fields |
|---|---|---|
| `pipeline.step_started` | A step has begun execution | run_id, step_number, step_name, agent_id |
| `pipeline.step_completed` | A step completed successfully | run_id, step_number, step_name, cost_usd, quality_score, next_step |
| `pipeline.step_failed` | A step has failed | run_id, step_number, step_name, error_message, retry_count |
| `pipeline.paused` | Pipeline paused at approval gate | run_id, step_number, approval_id |
| `pipeline.resumed` | Pipeline resumed after approval | run_id, step_number, approved_by |
| `pipeline.completed` | Pipeline finished all steps | run_id, total_cost_usd, documents_generated |
| `pipeline.cancelled` | Pipeline was cancelled | run_id, cancelled_by, reason |

---

### Channel: MCP Call Feed

**URL:** `ws://host/ws/mcp-calls`

**Dashboard screen:** S-007 MCP Monitoring Panel

**Message format:**

```json
{
  "event": "mcp.call_completed",
  "data": {
    "call_id": "bb0e8400-e29b-41d4-a716-446655440080",
    "server_name": "agents-server",
    "tool_name": "trigger_pipeline",
    "caller": "claude-code-session-abc",
    "duration_ms": 156,
    "status": "success",
    "cost_usd": 0.08
  },
  "timestamp": "2026-03-24T14:34:42.000Z",
  "event_id": "evt_mcp_001"
}
```

**Event types:**

| Event | Description |
|---|---|
| `mcp.call_started` | MCP tool invocation started |
| `mcp.call_completed` | MCP tool invocation completed (success or error) |
| `mcp.server_health_changed` | MCP server health status changed |

---

### Channel: Approval Notifications

**URL:** `ws://host/ws/approvals`

**Dashboard screen:** S-040 Approval Queue Table

**Message format:**

```json
{
  "event": "approval.created",
  "data": {
    "approval_id": "cc0e8400-e29b-41d4-a716-446655440090",
    "run_id": "run_a1b2c3d4e5f6g7h8",
    "step_name": "06-INTERACTION-MAP",
    "risk_level": "high",
    "summary": "Pipeline run for proj_abc123def456 requires approval at INTERACTION-MAP stage",
    "expires_at": "2026-03-24T15:35:00.000Z"
  },
  "timestamp": "2026-03-24T14:35:00.000Z",
  "event_id": "evt_appr_001"
}
```

**Event types:**

| Event | Description |
|---|---|
| `approval.created` | New approval request created |
| `approval.decided` | Approval was approved or rejected |
| `approval.expired` | Approval expired without decision |
| `approval.escalated` | Approval was escalated due to SLA breach |

---

## 9. Error Codes

Complete error code registry. All error codes are shared between MCP tools and REST endpoints (Q-051 compliance). The `code` field in the error envelope uses these exact strings.

| Error Code | HTTP Status | MCP Error Code | Description |
|---|---|---|---|
| `UNAUTHORIZED` | 401 | -32001 | Missing or invalid authentication credentials |
| `FORBIDDEN` | 403 | -32002 | Authenticated but insufficient role/permissions |
| `INVALID_PROJECT` | 404 | -32010 | Project ID does not exist |
| `PIPELINE_NOT_FOUND` | 404 | -32011 | Pipeline run ID does not exist |
| `AGENT_NOT_FOUND` | 404 | -32012 | Agent ID does not exist |
| `APPROVAL_NOT_FOUND` | 404 | -32013 | Approval ID does not exist |
| `EXCEPTION_NOT_FOUND` | 404 | -32014 | Knowledge exception ID does not exist |
| `VERSION_NOT_FOUND` | 404 | -32015 | Agent version does not exist |
| `ENTITY_NOT_FOUND` | 404 | -32016 | Generic entity not found |
| `NO_BUDGET_CONFIGURED` | 404 | -32017 | No budget configured for entity |
| `BUDGET_EXCEEDED` | 422 | -32020 | Operation would exceed budget |
| `BUDGET_BELOW_SPEND` | 422 | -32021 | New budget is less than current spend |
| `PIPELINE_ALREADY_RUNNING` | 409 | -32030 | Project already has an active pipeline |
| `PIPELINE_NOT_PAUSED` | 409 | -32031 | Pipeline is not in paused state |
| `PIPELINE_ALREADY_TERMINAL` | 409 | -32032 | Pipeline is already completed/failed/cancelled |
| `APPROVAL_PENDING` | 409 | -32033 | Gate approval required before action |
| `APPROVAL_ALREADY_DECIDED` | 409 | -32034 | Approval already approved/rejected |
| `APPROVAL_EXPIRED` | 410 | -32035 | Approval has expired |
| `NO_PREVIOUS_VERSION` | 409 | -32036 | No previous version for rollback |
| `NO_CANARY_VERSION` | 409 | -32037 | No canary version deployed |
| `DUPLICATE_RULE` | 409 | -32038 | Knowledge rule already exists |
| `EXPORT_IN_PROGRESS` | 409 | -32039 | Report export already in progress |
| `STAGE_NOT_FAILED` | 409 | -32040 | Pipeline stage is not in failed state |
| `MAX_RETRIES_EXCEEDED` | 422 | -32041 | Maximum retry count reached |
| `INVALID_PROMOTION_PATH` | 422 | -32042 | Invalid maturity/tier transition |
| `PROMOTION_CRITERIA_NOT_MET` | 422 | -32043 | Agent does not meet promotion criteria |
| `AGENT_VERSION_DEPRECATED` | 422 | -32044 | Agent version is deprecated |
| `EXPORT_TOO_LARGE` | 422 | -32045 | Export period contains too many events |
| `INVALID_TEMPLATE` | 400 | -32050 | Unknown pipeline template |
| `BRIEF_TOO_SHORT` | 400 | -32051 | Brief does not meet minimum length |
| `COMMENT_REQUIRED` | 400 | -32052 | Rejection requires a comment |
| `INVALID_TRAFFIC_PCT` | 400 | -32053 | Canary traffic percentage out of range |
| `INVALID_THRESHOLD` | 400 | -32054 | Alert threshold out of range |
| `INVALID_SCOPE` | 400 | -32055 | Unknown cost/budget scope |
| `INVALID_PERIOD` | 400 | -32056 | Invalid period_days value |
| `INVALID_DATE_RANGE` | 400 | -32057 | Malformed or invalid date range |
| `INVALID_SEVERITY` | 400 | -32058 | Unknown severity value |
| `INVALID_STATUS` | 400 | -32059 | Unknown status filter value |
| `INVALID_ROLE` | 400 | -32060 | Unknown agent role |
| `INVALID_PHASE` | 400 | -32061 | Unknown agent phase |
| `INVALID_TIER` | 400 | -32062 | Unknown knowledge tier |
| `INVALID_SERVER_NAME` | 400 | -32063 | Unknown MCP server name |
| `CLIENT_NOT_FOUND` | 404 | -32064 | Client ID does not exist |
| `STACK_NOT_FOUND` | 404 | -32065 | Stack name does not exist |
| `NO_DOCUMENTS_YET` | 404 | -32066 | Pipeline has not produced documents |
| `AGENT_UNHEALTHY` | 503 | -32070 | Agent is currently unhealthy |
| `INVOCATION_TIMEOUT` | 504 | -32071 | Agent invocation exceeded timeout |
| `MCP_SERVER_UNAVAILABLE` | 503 | -32072 | MCP server is down or unreachable |
| `RATE_LIMIT_EXCEEDED` | 429 | -32080 | Too many requests |
| `INTERNAL_ERROR` | 500 | -32603 | Unexpected internal server error |
| `INVALID_CREDENTIALS` | 401 | — | Wrong email or password (REST-only) |
| `ACCOUNT_LOCKED` | 403 | — | Account locked after failed attempts (REST-only) |
| `ACCOUNT_DISABLED` | 403 | — | Account is disabled (REST-only) |
| `INVALID_REFRESH_TOKEN` | 401 | — | Refresh token expired or invalid (REST-only) |
| `TOKEN_REVOKED` | 401 | — | Refresh token has been revoked (REST-only) |

---

## 10. Rate Limiting

### Per-Endpoint Limits

| Endpoint Category | Limit | Window |
|---|---|---|
| `GET /system/health` | 600 req | 1 minute |
| `GET /agents`, `GET /pipelines`, other list endpoints | 120 req | 1 minute |
| `GET` (single resource) | 300 req | 1 minute |
| `POST /pipelines` (trigger) | 10 req | 1 minute |
| `POST /agents/{id}/invoke` | 30 req | 1 minute |
| `POST` (other mutations) | 60 req | 1 minute |
| `PATCH` (updates) | 60 req | 1 minute |
| `GET /audit/export` | 5 req | 1 minute |
| WebSocket connections | 10 concurrent | per user |

### Rate Limit Headers

Every response includes rate limit headers:

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 117
X-RateLimit-Reset: 1711291200
```

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Maximum requests allowed in the current window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Unix epoch timestamp when the window resets |

### 429 Response

When the rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 32
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1711291200
Content-Type: application/json

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit of 120 requests per minute exceeded. Retry after 32 seconds.",
    "details": {
      "limit": 120,
      "window_seconds": 60,
      "retry_after_seconds": 32
    }
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440099",
    "timestamp": "2026-03-24T14:35:00.000Z"
  }
}
```

### Rate Limit Scoping

- **JWT sessions:** Rate limits are per-user (identified by `sub` claim)
- **API keys:** Rate limits are per-key
- **Unauthenticated:** Rate limits are per-IP address (applies only to `/system/health` and `/auth/login`)

### Burst Allowance

All limits allow a 20% burst above the stated limit for short spikes. The burst tokens refill at the steady-state rate. For example, the 120 req/min list endpoint allows bursts of up to 144 requests, but the sustained rate cannot exceed 120/min.

---

## Appendix A: cURL Examples

### Trigger a Pipeline

```bash
curl -X POST https://api.agentic-sdlc.io/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ask_abc123def456..." \
  -d '{
    "project_id": "proj_abc123def456",
    "brief": "Build a multi-tenant SaaS billing dashboard with Stripe integration",
    "template": "full-stack-first",
    "options": { "cost_ceiling_usd": 25.0 }
  }'
```

### List Running Pipelines

```bash
curl "https://api.agentic-sdlc.io/api/v1/pipelines?status=running&page=1&per_page=10" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiI..."
```

### Check Fleet Health

```bash
curl https://api.agentic-sdlc.io/api/v1/system/health
```

### Approve a Gate

```bash
curl -X POST https://api.agentic-sdlc.io/api/v1/approvals/cc0e8400-e29b-41d4-a716-446655440090/approve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiI..." \
  -d '{ "comment": "Approved after reviewing data shape consistency" }'
```

### Get Cost Report

```bash
curl "https://api.agentic-sdlc.io/api/v1/cost/report?scope=fleet&period_days=7" \
  -H "X-API-Key: ask_abc123def456..."
```

### Connect to Pipeline WebSocket

```bash
wscat -c "ws://localhost:8080/ws/pipelines/run_a1b2c3d4e5f6g7h8?token=eyJhbGciOiJSUzI1NiI..."
```

---

## Appendix B: Parity Verification Checklist

This checklist confirms Q-049 (MCP/REST parity) and Q-051 (error code matching) compliance.

### Q-049: Every MCP Tool Has a REST Endpoint

- [x] Pipeline tools (9/9): trigger, status, list, resume, cancel, documents, retry, config, validate
- [x] Agent tools (8/8): list, detail, invoke, health, promote, rollback, canary, maturity
- [x] Governance tools (10/10): cost report, budget check, audit events, audit summary, audit export, pending approvals, approve, reject, anomalies, budget threshold
- [x] Knowledge tools (4/4): search, create, promote, list
- [x] System tools (3/3): fleet health, MCP status, recent MCP calls
- [x] **Total: 34/34 MCP tools have REST equivalents**

### Q-051: Error Codes Match

- [x] Every MCP error code has a corresponding REST error code
- [x] MCP numeric codes (-32xxx) map to semantic string codes
- [x] REST adds auth-specific codes (INVALID_CREDENTIALS, etc.) that have no MCP equivalent (REST-only operations)

### Dashboard Coverage

- [x] Fleet Health page (7 screens): All data needs met by 7 endpoints
- [x] Cost Monitor page (5 screens): All data needs met by 4 endpoints
- [x] Pipeline Runs page (5 screens): All data needs met by 7 endpoints
- [x] Audit Log page (3 screens): All data needs met by 3 endpoints
- [x] Approval Queue page (3 screens): All data needs met by 3 endpoints
- [x] **Total: 23 screens served by 24 unique endpoints**

### Data Shape Consistency

- [x] All 22 INTERACTION-MAP data shapes are used as-is in REST responses
- [x] No field renaming or shape transformation in the REST layer
- [x] REST responses wrapped in standard envelope; data field contains the canonical shape
