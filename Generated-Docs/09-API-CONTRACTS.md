# 09 - API CONTRACTS

> Agentic SDLC Platform -- Complete HTTP and WebSocket API Reference
>
> Version: 1.0.0 | Last Updated: 2026-03-23

---

## Table of Contents

1. [Base URL and Versioning](#1-base-url-and-versioning)
2. [Standard Response Envelope](#2-standard-response-envelope)
3. [Authentication](#3-authentication)
4. [Endpoints](#4-endpoints)
   - 4.1 [Agents](#41-agents)
   - 4.2 [Agent Lifecycle (Canary)](#42-agent-lifecycle-canary)
   - 4.3 [Pipelines](#43-pipelines)
   - 4.4 [Approvals](#44-approvals)
   - 4.5 [Cost](#45-cost)
   - 4.6 [Audit](#46-audit)
   - 4.7 [Sessions](#47-sessions)
   - 4.8 [Knowledge Exceptions](#48-knowledge-exceptions)
   - 4.9 [Health](#49-health)
5. [WebSocket / SSE Channels](#5-websocket--sse-channels)
6. [Error Codes](#6-error-codes)
7. [Rate Limiting](#7-rate-limiting)
8. [Appendix: Endpoint Summary Matrix](#8-appendix-endpoint-summary-matrix)

---

## 1. Base URL and Versioning

### Versioning Strategy

All API endpoints are versioned using a **URI prefix**. The current version is `v1`. Breaking changes result in a new major version (`v2`). Non-breaking additions (new optional fields, new endpoints) are shipped within the current version.

| Environment | Base URL                                      |
|-------------|-----------------------------------------------|
| Development | `http://localhost:8080/api/v1/`                |
| Staging     | `https://staging.agentic-sdlc.internal/api/v1/`|
| Production  | `https://api.agentic-sdlc.io/api/v1/`         |

### Header Requirements

All requests MUST include:

| Header         | Value                          | Required |
|----------------|--------------------------------|----------|
| `Content-Type` | `application/json`             | For POST/PUT/PATCH |
| `Accept`       | `application/json`             | Recommended |
| `Authorization`| `Bearer <jwt>` or omitted      | See Section 3 |
| `X-API-Key`    | `<api-key>` (programmatic)     | See Section 3 |
| `X-Request-ID` | UUID v4 (client-generated)     | Recommended |

The server echoes `X-Request-ID` in the response and includes it in audit logs for traceability.

---

## 2. Standard Response Envelope

Every endpoint returns a consistent JSON envelope. No endpoint returns a bare object or array.

### Success Response

```json
{
  "data": { },
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-03-23T14:30:00Z"
  },
  "errors": []
}
```

- **`data`** -- The resource or collection. For single-resource endpoints, this is an object. For list endpoints, this is an array.
- **`meta`** -- Pagination fields (`total`, `page`, `per_page`, `total_pages`) are present only on list endpoints. `request_id` and `timestamp` are always present.
- **`errors`** -- Empty array on success.

### Error Response

```json
{
  "data": null,
  "meta": {
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-03-23T14:30:00Z"
  },
  "errors": [
    {
      "code": "validation_error",
      "message": "Field 'name' is required.",
      "field": "name",
      "detail": "Agent name must be 3-128 characters."
    }
  ]
}
```

### Pagination Query Parameters (All List Endpoints)

| Param     | Type | Default | Description                  |
|-----------|------|---------|------------------------------|
| `page`    | int  | 1       | Page number (1-indexed)      |
| `per_page`| int  | 20      | Items per page (max 100)     |
| `sort`    | str  | varies  | Sort field (resource-specific)|
| `order`   | str  | `desc`  | `asc` or `desc`              |

---

## 3. Authentication

### Authentication Methods

The platform supports two authentication mechanisms. Every endpoint except health checks requires one.

| Method       | Header              | Use Case                          |
|--------------|---------------------|-----------------------------------|
| JWT Bearer   | `Authorization: Bearer <token>` | Dashboard UI sessions    |
| API Key      | `X-API-Key: <key>`  | Programmatic / SDK access          |

### JWT Token Claims

```json
{
  "sub": "user_id_uuid",
  "project_id": "proj_abc123",
  "role": "platform_engineer",
  "permissions": ["agents:write", "pipelines:read", "approvals:write"],
  "iat": 1711180200,
  "exp": 1711183800,
  "iss": "agentic-sdlc"
}
```

### Roles and Permissions

| Role               | Persona | Permissions                                              |
|--------------------|---------|----------------------------------------------------------|
| `platform_engineer`| Priya   | `agents:*`, `pipelines:read`, `sessions:*`, `knowledge:*`|
| `delivery_lead`    | David   | `pipelines:*`, `agents:read`, `cost:read`, `sessions:read`|
| `engineering_lead` | Sarah   | `approvals:*`, `pipelines:read`, `agents:read`            |
| `devops`           | Marcus  | `health:*`, `cost:*`, `agents:read`, `pipelines:read`     |
| `compliance`       | Lisa    | `audit:*`, `pipelines:read`, `agents:read`                |
| `admin`            | --      | `*` (all permissions)                                      |

### Public Endpoints (No Auth Required)

| Endpoint               | Purpose              |
|------------------------|----------------------|
| `GET /api/v1/health`   | Liveness check       |
| `GET /api/v1/ready`    | Readiness check      |

### Token Endpoints

**POST /api/v1/auth/token**

Request:
```json
{
  "username": "priya@acme.com",
  "password": "********"
}
```

Response:
```json
{
  "data": {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 3600,
    "refresh_token": "dGhpcyBpcyBh..."
  },
  "meta": {
    "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2026-03-23T14:30:00Z"
  },
  "errors": []
}
```

**POST /api/v1/auth/refresh**

Request:
```json
{
  "refresh_token": "dGhpcyBpcyBh..."
}
```

Response: Same shape as `/auth/token`.

### Security Constraints

- Q-017: No secrets, tokens, passwords, or API keys are ever returned in response bodies (except the auth/token endpoint itself).
- All tokens expire after 1 hour. Refresh tokens expire after 24 hours.
- API keys are shown once at creation time and stored as bcrypt hashes.

---

## 4. Endpoints

---

### 4.1 Agents

**Persona:** Priya (Platform Engineer)
**Permission prefix:** `agents:`

---

#### 4.1.1 List Agents

`GET /api/v1/agents`

Returns a paginated list of registered agents with optional filters.

**Query Parameters:**

| Param    | Type   | Required | Description                          |
|----------|--------|----------|--------------------------------------|
| `phase`  | string | No       | Filter by SDLC phase (e.g., `requirements`, `design`, `code`, `test`) |
| `status` | string | No       | Filter by status: `active`, `inactive`, `degraded`, `circuit_open` |
| `search` | string | No       | Search by agent name (partial match) |
| `page`   | int    | No       | Page number (default: 1)             |
| `per_page`| int   | No       | Items per page (default: 20, max: 100) |

**Response: 200 OK**

```json
{
  "data": [
    {
      "id": "agt_req_analyzer_01",
      "name": "Requirements Analyzer",
      "phase": "requirements",
      "archetype": "analyst",
      "version": "2.4.1",
      "status": "active",
      "model": "claude-opus-4-20250514",
      "active_version": "2.4.1",
      "canary_version": null,
      "canary_traffic_pct": 0,
      "created_at": "2026-01-15T08:00:00Z",
      "updated_at": "2026-03-20T12:30:00Z"
    },
    {
      "id": "agt_code_gen_01",
      "name": "Code Generator",
      "phase": "code",
      "archetype": "generator",
      "version": "3.1.0",
      "status": "active",
      "model": "claude-sonnet-4-20250514",
      "active_version": "3.1.0",
      "canary_version": "3.2.0-rc1",
      "canary_traffic_pct": 10,
      "created_at": "2026-01-15T08:00:00Z",
      "updated_at": "2026-03-22T09:15:00Z"
    }
  ],
  "meta": {
    "total": 12,
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "request_id": "c3d4e5f6-a1b2-7890-cdef-1234567890ab",
    "timestamp": "2026-03-23T14:30:00Z"
  },
  "errors": []
}
```

---

#### 4.1.2 Get Agent

`GET /api/v1/agents/{agent_id}`

Returns a single agent by ID including full configuration detail.

**Path Parameters:**

| Param      | Type   | Description          |
|------------|--------|----------------------|
| `agent_id` | string | Agent identifier      |

**Response: 200 OK**

```json
{
  "data": {
    "id": "agt_req_analyzer_01",
    "name": "Requirements Analyzer",
    "phase": "requirements",
    "archetype": "analyst",
    "version": "2.4.1",
    "status": "active",
    "model": "claude-opus-4-20250514",
    "active_version": "2.4.1",
    "canary_version": null,
    "canary_traffic_pct": 0,
    "circuit_breaker": {
      "state": "closed",
      "failure_count": 0,
      "last_failure_at": null,
      "half_open_at": null
    },
    "health": {
      "last_heartbeat": "2026-03-23T14:29:55Z",
      "avg_response_ms": 145,
      "success_rate_pct": 99.7,
      "active_sessions": 2
    },
    "created_at": "2026-01-15T08:00:00Z",
    "updated_at": "2026-03-20T12:30:00Z"
  },
  "meta": {
    "request_id": "d4e5f6a1-b2c3-7890-def0-234567890abc",
    "timestamp": "2026-03-23T14:30:00Z"
  },
  "errors": []
}
```

---

#### 4.1.3 Create Agent

`POST /api/v1/agents`

Registers a new agent in the fleet.

**Request Body:**

```json
{
  "id": "agt_doc_writer_01",
  "name": "Documentation Writer",
  "phase": "documentation",
  "archetype": "generator",
  "version": "1.0.0",
  "model": "claude-sonnet-4-20250514",
  "status": "inactive"
}
```

**Response: 201 Created**

```json
{
  "data": {
    "id": "agt_doc_writer_01",
    "name": "Documentation Writer",
    "phase": "documentation",
    "archetype": "generator",
    "version": "1.0.0",
    "status": "inactive",
    "model": "claude-sonnet-4-20250514",
    "active_version": "1.0.0",
    "canary_version": null,
    "canary_traffic_pct": 0,
    "created_at": "2026-03-23T14:35:00Z",
    "updated_at": "2026-03-23T14:35:00Z"
  },
  "meta": {
    "request_id": "e5f6a1b2-c3d4-7890-ef01-34567890abcd",
    "timestamp": "2026-03-23T14:35:00Z"
  },
  "errors": []
}
```

**Validation Rules:**

| Field      | Rules                                                   |
|------------|--------------------------------------------------------|
| `id`       | Required. 3-64 chars, alphanumeric + underscores.       |
| `name`     | Required. 3-128 chars.                                  |
| `phase`    | Required. One of: `requirements`, `design`, `code`, `test`, `documentation`, `review`, `deploy`. |
| `archetype`| Required. One of: `analyst`, `generator`, `validator`, `orchestrator`. |
| `version`  | Required. Semver format.                                |
| `model`    | Required. Valid model identifier string.                |
| `status`   | Optional. Default `inactive`. One of: `active`, `inactive`. |

---

#### 4.1.4 Update Agent

`PUT /api/v1/agents/{agent_id}`

Updates an existing agent's configuration. Partial updates are supported via `PATCH` as well.

**Path Parameters:**

| Param      | Type   | Description          |
|------------|--------|----------------------|
| `agent_id` | string | Agent identifier      |

**Request Body:**

```json
{
  "name": "Requirements Analyzer v2",
  "model": "claude-opus-4-20250514",
  "status": "active"
}
```

**Response: 200 OK**

```json
{
  "data": {
    "id": "agt_req_analyzer_01",
    "name": "Requirements Analyzer v2",
    "phase": "requirements",
    "archetype": "analyst",
    "version": "2.4.1",
    "status": "active",
    "model": "claude-opus-4-20250514",
    "active_version": "2.4.1",
    "canary_version": null,
    "canary_traffic_pct": 0,
    "created_at": "2026-01-15T08:00:00Z",
    "updated_at": "2026-03-23T14:40:00Z"
  },
  "meta": {
    "request_id": "f6a1b2c3-d4e5-7890-0123-4567890abcde",
    "timestamp": "2026-03-23T14:40:00Z"
  },
  "errors": []
}
```

---

#### 4.1.5 Delete Agent

`DELETE /api/v1/agents/{agent_id}`

Soft-deletes an agent. Sets status to `decommissioned`. Agent data is retained for audit purposes.

**Path Parameters:**

| Param      | Type   | Description          |
|------------|--------|----------------------|
| `agent_id` | string | Agent identifier      |

**Response: 200 OK**

```json
{
  "data": {
    "id": "agt_doc_writer_01",
    "status": "decommissioned",
    "decommissioned_at": "2026-03-23T14:45:00Z"
  },
  "meta": {
    "request_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "timestamp": "2026-03-23T14:45:00Z"
  },
  "errors": []
}
```

---

#### 4.1.6 Agent Health Check

`GET /api/v1/agents/{agent_id}/health`

Returns real-time health status for a specific agent. Used by the Fleet Health dashboard.

**Path Parameters:**

| Param      | Type   | Description          |
|------------|--------|----------------------|
| `agent_id` | string | Agent identifier      |

**Response: 200 OK**

```json
{
  "data": {
    "agent_id": "agt_req_analyzer_01",
    "status": "active",
    "circuit_breaker": {
      "state": "closed",
      "failure_count": 0,
      "threshold": 5,
      "last_failure_at": null,
      "recovery_timeout_seconds": 30
    },
    "metrics": {
      "last_heartbeat": "2026-03-23T14:29:55Z",
      "uptime_seconds": 5832000,
      "avg_response_ms": 145,
      "p95_response_ms": 192,
      "p99_response_ms": 310,
      "success_rate_pct": 99.7,
      "total_requests_24h": 1842,
      "active_sessions": 2,
      "error_count_24h": 5
    },
    "model": "claude-opus-4-20250514",
    "active_version": "2.4.1",
    "canary_version": null
  },
  "meta": {
    "request_id": "b2c3d4e5-f6a1-7890-2345-67890abcdef0",
    "timestamp": "2026-03-23T14:30:00Z"
  },
  "errors": []
}
```

---

### 4.2 Agent Lifecycle (Canary)

**Persona:** Priya (Platform Engineer)
**Permission prefix:** `agents:`

---

#### 4.2.1 Set Canary

`POST /api/v1/agents/{agent_id}/canary`

Deploys a canary version of an agent with a specified traffic percentage.

**Path Parameters:**

| Param      | Type   | Description          |
|------------|--------|----------------------|
| `agent_id` | string | Agent identifier      |

**Request Body:**

```json
{
  "canary_version": "2.5.0-rc1",
  "traffic_pct": 10,
  "evaluation_duration_minutes": 60,
  "rollback_on_error_rate_pct": 5.0
}
```

**Response: 200 OK**

```json
{
  "data": {
    "agent_id": "agt_req_analyzer_01",
    "active_version": "2.4.1",
    "canary_version": "2.5.0-rc1",
    "canary_traffic_pct": 10,
    "evaluation_started_at": "2026-03-23T15:00:00Z",
    "evaluation_ends_at": "2026-03-23T16:00:00Z",
    "rollback_threshold_error_rate_pct": 5.0,
    "status": "evaluating"
  },
  "meta": {
    "request_id": "c3d4e5f6-a1b2-7890-3456-7890abcdef01",
    "timestamp": "2026-03-23T15:00:00Z"
  },
  "errors": []
}
```

---

#### 4.2.2 Promote Canary

`POST /api/v1/agents/{agent_id}/canary/promote`

Promotes the canary version to become the active version. The previous active version is archived.

**Path Parameters:**

| Param      | Type   | Description          |
|------------|--------|----------------------|
| `agent_id` | string | Agent identifier      |

**Request Body:**

```json
{
  "confirm": true
}
```

**Response: 200 OK**

```json
{
  "data": {
    "agent_id": "agt_req_analyzer_01",
    "previous_version": "2.4.1",
    "active_version": "2.5.0-rc1",
    "canary_version": null,
    "canary_traffic_pct": 0,
    "promoted_at": "2026-03-23T16:05:00Z"
  },
  "meta": {
    "request_id": "d4e5f6a1-b2c3-7890-4567-890abcdef012",
    "timestamp": "2026-03-23T16:05:00Z"
  },
  "errors": []
}
```

---

#### 4.2.3 Rollback Canary

`POST /api/v1/agents/{agent_id}/canary/rollback`

Removes the canary version and routes 100% traffic back to the active version.

**Path Parameters:**

| Param      | Type   | Description          |
|------------|--------|----------------------|
| `agent_id` | string | Agent identifier      |

**Request Body:**

```json
{
  "reason": "Elevated error rate observed during canary evaluation."
}
```

**Response: 200 OK**

```json
{
  "data": {
    "agent_id": "agt_req_analyzer_01",
    "active_version": "2.4.1",
    "canary_version": null,
    "canary_traffic_pct": 0,
    "rolled_back_at": "2026-03-23T15:45:00Z",
    "reason": "Elevated error rate observed during canary evaluation."
  },
  "meta": {
    "request_id": "e5f6a1b2-c3d4-7890-5678-90abcdef0123",
    "timestamp": "2026-03-23T15:45:00Z"
  },
  "errors": []
}
```

---

### 4.3 Pipelines

**Persona:** David (Delivery Lead)
**Permission prefix:** `pipelines:`

---

#### 4.3.1 Trigger Pipeline

`POST /api/v1/pipelines`

Triggers a new pipeline run. The 12-document pipeline is the primary use case.

**Request Body:**

```json
{
  "pipeline_name": "12-doc-generation",
  "project_id": "proj_abc123",
  "parameters": {
    "input_spec": "PRD-2026-Q1-feature-auth",
    "output_format": "markdown",
    "skip_steps": [],
    "parallel_execution": false
  },
  "callback_url": "https://hooks.acme.com/pipeline-complete"
}
```

**Response: 202 Accepted**

```json
{
  "data": {
    "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
    "pipeline_name": "12-doc-generation",
    "project_id": "proj_abc123",
    "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "running",
    "step_count": 12,
    "started_at": "2026-03-23T15:00:00Z",
    "estimated_completion_at": "2026-03-23T15:45:00Z"
  },
  "meta": {
    "request_id": "f6a1b2c3-d4e5-7890-6789-0abcdef01234",
    "timestamp": "2026-03-23T15:00:00Z"
  },
  "errors": []
}
```

---

#### 4.3.2 Get Pipeline Status

`GET /api/v1/pipelines/{run_id}`

Returns the current status and summary of a pipeline run.

**Path Parameters:**

| Param    | Type   | Description             |
|----------|--------|-------------------------|
| `run_id` | string | Pipeline run identifier  |

**Response: 200 OK**

```json
{
  "data": {
    "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
    "pipeline_name": "12-doc-generation",
    "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "project_id": "proj_abc123",
    "status": "running",
    "started_at": "2026-03-23T15:00:00Z",
    "completed_at": null,
    "cost_usd": 1.47,
    "step_count": 12,
    "steps_completed": 7,
    "steps_failed": 0,
    "current_step": {
      "step_id": "step_08",
      "agent_id": "agt_api_designer_01",
      "status": "running",
      "started_at": "2026-03-23T15:28:00Z"
    },
    "progress_pct": 58.3
  },
  "meta": {
    "request_id": "a1b2c3d4-f6e5-7890-7890-1abcdef01234",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.3.3 List Pipeline Runs

`GET /api/v1/pipelines`

Returns a paginated list of pipeline runs with filters.

**Query Parameters:**

| Param           | Type   | Required | Description                                 |
|-----------------|--------|----------|---------------------------------------------|
| `project_id`    | string | No       | Filter by project                           |
| `pipeline_name` | string | No       | Filter by pipeline name                     |
| `status`        | string | No       | Filter: `running`, `completed`, `failed`, `paused`, `cancelled` |
| `started_after` | string | No       | ISO 8601 datetime lower bound               |
| `started_before`| string | No       | ISO 8601 datetime upper bound               |
| `page`          | int    | No       | Page number (default: 1)                    |
| `per_page`      | int    | No       | Items per page (default: 20)                |

**Response: 200 OK**

```json
{
  "data": [
    {
      "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
      "pipeline_name": "12-doc-generation",
      "project_id": "proj_abc123",
      "status": "running",
      "started_at": "2026-03-23T15:00:00Z",
      "completed_at": null,
      "cost_usd": 1.47,
      "step_count": 12,
      "steps_completed": 7,
      "progress_pct": 58.3
    },
    {
      "run_id": "run_8e4b3c2d-f5a6-7890-bcde-f01234567890",
      "pipeline_name": "12-doc-generation",
      "project_id": "proj_xyz789",
      "status": "completed",
      "started_at": "2026-03-22T10:00:00Z",
      "completed_at": "2026-03-22T10:42:00Z",
      "cost_usd": 3.21,
      "step_count": 12,
      "steps_completed": 12,
      "progress_pct": 100.0
    }
  ],
  "meta": {
    "total": 47,
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "request_id": "b2c3d4e5-a1f6-7890-8901-2abcdef01234",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.3.4 Get Run Detail

`GET /api/v1/pipelines/{run_id}/detail`

Returns full detail for a pipeline run including all step information.

**Path Parameters:**

| Param    | Type   | Description             |
|----------|--------|-------------------------|
| `run_id` | string | Pipeline run identifier  |

**Response: 200 OK**

```json
{
  "data": {
    "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
    "pipeline_name": "12-doc-generation",
    "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "project_id": "proj_abc123",
    "status": "completed",
    "started_at": "2026-03-23T15:00:00Z",
    "completed_at": "2026-03-23T15:42:00Z",
    "cost_usd": 3.21,
    "step_count": 12,
    "steps": [
      {
        "step_id": "step_01",
        "agent_id": "agt_req_analyzer_01",
        "name": "Requirements Analysis",
        "status": "completed",
        "started_at": "2026-03-23T15:00:00Z",
        "completed_at": "2026-03-23T15:03:30Z",
        "cost_usd": 0.28,
        "error_message": null
      },
      {
        "step_id": "step_02",
        "agent_id": "agt_arch_designer_01",
        "name": "Architecture Design",
        "status": "completed",
        "started_at": "2026-03-23T15:03:31Z",
        "completed_at": "2026-03-23T15:07:15Z",
        "cost_usd": 0.31,
        "error_message": null
      }
    ],
    "checkpoint": {
      "last_step_id": "step_12",
      "status": "completed"
    }
  },
  "meta": {
    "request_id": "c3d4e5f6-b2a1-7890-9012-3abcdef01234",
    "timestamp": "2026-03-23T15:45:00Z"
  },
  "errors": []
}
```

---

#### 4.3.5 Get Pipeline Steps

`GET /api/v1/pipelines/{run_id}/steps`

Returns the step list for a pipeline run with status and timing.

**Path Parameters:**

| Param    | Type   | Description             |
|----------|--------|-------------------------|
| `run_id` | string | Pipeline run identifier  |

**Query Parameters:**

| Param    | Type   | Required | Description                             |
|----------|--------|----------|-----------------------------------------|
| `status` | string | No       | Filter: `pending`, `running`, `completed`, `failed`, `skipped` |

**Response: 200 OK**

```json
{
  "data": [
    {
      "step_id": "step_01",
      "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
      "agent_id": "agt_req_analyzer_01",
      "name": "Requirements Analysis",
      "status": "completed",
      "started_at": "2026-03-23T15:00:00Z",
      "completed_at": "2026-03-23T15:03:30Z",
      "duration_seconds": 210,
      "cost_usd": 0.28,
      "error_message": null,
      "requires_approval": false
    },
    {
      "step_id": "step_05",
      "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
      "agent_id": "agt_code_gen_01",
      "name": "Code Generation",
      "status": "running",
      "started_at": "2026-03-23T15:15:00Z",
      "completed_at": null,
      "duration_seconds": null,
      "cost_usd": 0.12,
      "error_message": null,
      "requires_approval": true
    }
  ],
  "meta": {
    "total": 12,
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "request_id": "d4e5f6a1-c3b2-7890-0123-4abcdef01234",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.3.6 Resume Pipeline

`POST /api/v1/pipelines/{run_id}/resume`

Resumes a failed or paused pipeline from the last successful checkpoint.

**Path Parameters:**

| Param    | Type   | Description             |
|----------|--------|-------------------------|
| `run_id` | string | Pipeline run identifier  |

**Request Body:**

```json
{
  "from_step": "step_08",
  "override_parameters": {
    "retry_failed_step": true,
    "max_retries": 3
  }
}
```

**Response: 202 Accepted**

```json
{
  "data": {
    "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
    "status": "running",
    "resumed_from_step": "step_08",
    "resumed_at": "2026-03-23T16:00:00Z",
    "remaining_steps": 5,
    "checkpoint": {
      "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "last_completed_step": "step_07",
      "step_results": {
        "step_01": "completed",
        "step_02": "completed",
        "step_03": "completed",
        "step_04": "completed",
        "step_05": "completed",
        "step_06": "completed",
        "step_07": "completed"
      }
    }
  },
  "meta": {
    "request_id": "e5f6a1b2-d4c3-7890-1234-5abcdef01234",
    "timestamp": "2026-03-23T16:00:00Z"
  },
  "errors": []
}
```

---

### 4.4 Approvals

**Persona:** Sarah (Engineering Lead)
**Permission prefix:** `approvals:`

---

#### 4.4.1 List Pending Approvals

`GET /api/v1/approvals`

Returns a paginated list of approval requests. Defaults to pending approvals.

**Query Parameters:**

| Param           | Type   | Required | Description                                   |
|-----------------|--------|----------|-----------------------------------------------|
| `status`        | string | No       | Filter: `pending`, `approved`, `rejected` (default: `pending`) |
| `pipeline_name` | string | No       | Filter by pipeline name                       |
| `project_id`    | string | No       | Filter by project                             |
| `page`          | int    | No       | Page number (default: 1)                      |
| `per_page`      | int    | No       | Items per page (default: 20)                  |

**Response: 200 OK**

```json
{
  "data": [
    {
      "approval_id": "apr_1a2b3c4d-e5f6-7890-abcd-ef0123456789",
      "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "pipeline_name": "12-doc-generation",
      "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
      "step_id": "step_05",
      "step_name": "Code Generation",
      "summary": "Code generation step completed. 14 files generated, 2,847 lines. Test coverage estimated at 89%. Review required before proceeding to integration testing.",
      "status": "pending",
      "requested_at": "2026-03-23T15:20:00Z",
      "project_id": "proj_abc123",
      "decision_by": null,
      "decision_comment": null,
      "decided_at": null
    }
  ],
  "meta": {
    "total": 3,
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "request_id": "f6a1b2c3-e5d4-7890-2345-6abcdef01234",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.4.2 Get Approval Detail

`GET /api/v1/approvals/{approval_id}`

Returns full detail for a specific approval request including the artifacts to review.

**Path Parameters:**

| Param         | Type   | Description               |
|---------------|--------|---------------------------|
| `approval_id` | string | Approval request identifier|

**Response: 200 OK**

```json
{
  "data": {
    "approval_id": "apr_1a2b3c4d-e5f6-7890-abcd-ef0123456789",
    "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "pipeline_name": "12-doc-generation",
    "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
    "step_id": "step_05",
    "step_name": "Code Generation",
    "summary": "Code generation step completed. 14 files generated, 2,847 lines. Test coverage estimated at 89%. Review required before proceeding to integration testing.",
    "status": "pending",
    "requested_at": "2026-03-23T15:20:00Z",
    "project_id": "proj_abc123",
    "artifacts": {
      "files_generated": 14,
      "total_lines": 2847,
      "estimated_test_coverage_pct": 89,
      "quality_score": 8.4,
      "warnings": [
        "Function `parse_config` exceeds 50 lines (62 lines).",
        "Missing docstring in module `auth_handler`."
      ]
    },
    "decision_by": null,
    "decision_comment": null,
    "decided_at": null
  },
  "meta": {
    "request_id": "a1b2c3d4-f6e5-7890-3456-7abcdef01234",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.4.3 Approve

`POST /api/v1/approvals/{approval_id}/approve`

Approves a pending approval request, allowing the pipeline to continue.

**Path Parameters:**

| Param         | Type   | Description               |
|---------------|--------|---------------------------|
| `approval_id` | string | Approval request identifier|

**Request Body:**

```json
{
  "comment": "Code quality looks good. Minor warnings noted but acceptable for this iteration."
}
```

**Response: 200 OK**

```json
{
  "data": {
    "approval_id": "apr_1a2b3c4d-e5f6-7890-abcd-ef0123456789",
    "status": "approved",
    "decision_by": "sarah@acme.com",
    "decision_comment": "Code quality looks good. Minor warnings noted but acceptable for this iteration.",
    "decided_at": "2026-03-23T15:35:00Z",
    "pipeline_resumed": true,
    "next_step": "step_06"
  },
  "meta": {
    "request_id": "b2c3d4e5-a1f6-7890-4567-8abcdef01234",
    "timestamp": "2026-03-23T15:35:00Z"
  },
  "errors": []
}
```

---

#### 4.4.4 Reject

`POST /api/v1/approvals/{approval_id}/reject`

Rejects a pending approval request, pausing the pipeline.

**Path Parameters:**

| Param         | Type   | Description               |
|---------------|--------|---------------------------|
| `approval_id` | string | Approval request identifier|

**Request Body:**

```json
{
  "comment": "Test coverage too low. Please regenerate with minimum 95% coverage target.",
  "action": "pause"
}
```

`action` can be `pause` (default, pipeline waits for retry) or `cancel` (pipeline is terminated).

**Response: 200 OK**

```json
{
  "data": {
    "approval_id": "apr_1a2b3c4d-e5f6-7890-abcd-ef0123456789",
    "status": "rejected",
    "decision_by": "sarah@acme.com",
    "decision_comment": "Test coverage too low. Please regenerate with minimum 95% coverage target.",
    "decided_at": "2026-03-23T15:35:00Z",
    "pipeline_action": "pause",
    "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789"
  },
  "meta": {
    "request_id": "c3d4e5f6-b2a1-7890-5678-9abcdef01234",
    "timestamp": "2026-03-23T15:35:00Z"
  },
  "errors": []
}
```

---

### 4.5 Cost

**Persona:** Marcus (DevOps)
**Permission prefix:** `cost:`

---

#### 4.5.1 Get Fleet Daily Cost

`GET /api/v1/cost/fleet`

Returns aggregated daily cost across the entire agent fleet.

**Query Parameters:**

| Param        | Type   | Required | Description                          |
|--------------|--------|----------|--------------------------------------|
| `start_date` | string | Yes      | ISO 8601 date (e.g., `2026-03-01`)  |
| `end_date`   | string | Yes      | ISO 8601 date (e.g., `2026-03-23`)  |
| `granularity`| string | No       | `daily` (default), `weekly`, `monthly`|

**Response: 200 OK**

```json
{
  "data": {
    "start_date": "2026-03-01",
    "end_date": "2026-03-23",
    "granularity": "daily",
    "total_cost_usd": 487.32,
    "total_input_tokens": 12450000,
    "total_output_tokens": 3890000,
    "series": [
      {
        "date": "2026-03-01",
        "cost_usd": 18.45,
        "input_tokens": 520000,
        "output_tokens": 162000,
        "run_count": 8
      },
      {
        "date": "2026-03-02",
        "cost_usd": 22.10,
        "input_tokens": 610000,
        "output_tokens": 195000,
        "run_count": 11
      }
    ],
    "budget": {
      "monthly_limit_usd": 1000.00,
      "current_month_spend_usd": 487.32,
      "remaining_usd": 512.68,
      "projected_month_end_usd": 689.50,
      "on_track": true
    }
  },
  "meta": {
    "request_id": "d4e5f6a1-c3b2-7890-6789-0abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.5.2 Get Project Daily Cost

`GET /api/v1/cost/projects/{project_id}`

Returns cost breakdown for a specific project.

**Path Parameters:**

| Param        | Type   | Description         |
|--------------|--------|---------------------|
| `project_id` | string | Project identifier   |

**Query Parameters:**

| Param        | Type   | Required | Description                          |
|--------------|--------|----------|--------------------------------------|
| `start_date` | string | Yes      | ISO 8601 date                        |
| `end_date`   | string | Yes      | ISO 8601 date                        |
| `granularity`| string | No       | `daily` (default), `weekly`, `monthly`|

**Response: 200 OK**

```json
{
  "data": {
    "project_id": "proj_abc123",
    "project_name": "Q1 Auth Feature",
    "start_date": "2026-03-01",
    "end_date": "2026-03-23",
    "granularity": "daily",
    "total_cost_usd": 124.56,
    "total_input_tokens": 3200000,
    "total_output_tokens": 980000,
    "series": [
      {
        "date": "2026-03-01",
        "cost_usd": 5.23,
        "input_tokens": 140000,
        "output_tokens": 43000,
        "run_count": 2
      }
    ],
    "by_agent": [
      {
        "agent_id": "agt_code_gen_01",
        "agent_name": "Code Generator",
        "cost_usd": 48.20,
        "pct_of_total": 38.7
      },
      {
        "agent_id": "agt_req_analyzer_01",
        "agent_name": "Requirements Analyzer",
        "cost_usd": 32.10,
        "pct_of_total": 25.8
      }
    ]
  },
  "meta": {
    "request_id": "e5f6a1b2-d4c3-7890-7890-1abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.5.3 Get Agent Daily Cost

`GET /api/v1/cost/agents/{agent_id}`

Returns cost metrics for a specific agent over time.

**Path Parameters:**

| Param      | Type   | Description          |
|------------|--------|----------------------|
| `agent_id` | string | Agent identifier      |

**Query Parameters:**

| Param        | Type   | Required | Description                          |
|--------------|--------|----------|--------------------------------------|
| `start_date` | string | Yes      | ISO 8601 date                        |
| `end_date`   | string | Yes      | ISO 8601 date                        |
| `granularity`| string | No       | `daily` (default), `weekly`, `monthly`|

**Response: 200 OK**

```json
{
  "data": {
    "agent_id": "agt_code_gen_01",
    "agent_name": "Code Generator",
    "model": "claude-sonnet-4-20250514",
    "start_date": "2026-03-01",
    "end_date": "2026-03-23",
    "granularity": "daily",
    "total_cost_usd": 198.45,
    "total_input_tokens": 5100000,
    "total_output_tokens": 1620000,
    "avg_cost_per_run_usd": 2.84,
    "series": [
      {
        "date": "2026-03-01",
        "cost_usd": 7.80,
        "input_tokens": 210000,
        "output_tokens": 68000,
        "run_count": 3
      }
    ]
  },
  "meta": {
    "request_id": "f6a1b2c3-e5d4-7890-8901-2abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.5.4 Get Cost Breakdown

`GET /api/v1/cost/breakdown`

Returns a multi-dimensional cost breakdown by model, agent, and project.

**Query Parameters:**

| Param        | Type   | Required | Description                                          |
|--------------|--------|----------|------------------------------------------------------|
| `start_date` | string | Yes      | ISO 8601 date                                        |
| `end_date`   | string | Yes      | ISO 8601 date                                        |
| `group_by`   | string | No       | `model` (default), `agent`, `project`, `phase`       |

**Response: 200 OK**

```json
{
  "data": {
    "start_date": "2026-03-01",
    "end_date": "2026-03-23",
    "group_by": "model",
    "total_cost_usd": 487.32,
    "breakdown": [
      {
        "key": "claude-opus-4-20250514",
        "cost_usd": 312.50,
        "pct_of_total": 64.1,
        "input_tokens": 8200000,
        "output_tokens": 2500000,
        "request_count": 1240
      },
      {
        "key": "claude-sonnet-4-20250514",
        "cost_usd": 148.20,
        "pct_of_total": 30.4,
        "input_tokens": 3800000,
        "output_tokens": 1200000,
        "request_count": 2180
      },
      {
        "key": "claude-haiku-3-20250514",
        "cost_usd": 26.62,
        "pct_of_total": 5.5,
        "input_tokens": 450000,
        "output_tokens": 190000,
        "request_count": 890
      }
    ]
  },
  "meta": {
    "request_id": "a1b2c3d4-f6e5-7890-9012-3abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

### 4.6 Audit

**Persona:** Lisa (Compliance)
**Permission prefix:** `audit:`

---

#### 4.6.1 Query Audit Events

`GET /api/v1/audit/events`

Returns a paginated, filterable list of immutable audit events.

**Query Parameters:**

| Param            | Type   | Required | Description                                            |
|------------------|--------|----------|--------------------------------------------------------|
| `project_id`     | string | No       | Filter by project                                      |
| `agent_id`       | string | No       | Filter by agent                                        |
| `session_id`     | string | No       | Filter by session                                      |
| `correlation_id` | string | No       | Filter by correlation ID (traces a single workflow)    |
| `event_type`     | string | No       | Filter: `agent_invocation`, `approval_decision`, `pipeline_start`, `pipeline_complete`, `error`, `cost_alert`, `config_change` |
| `severity`       | string | No       | Filter: `info`, `warning`, `error`, `critical`         |
| `start_time`     | string | No       | ISO 8601 datetime lower bound                          |
| `end_time`       | string | No       | ISO 8601 datetime upper bound                          |
| `page`           | int    | No       | Page number (default: 1)                               |
| `per_page`       | int    | No       | Items per page (default: 20, max: 100)                 |
| `sort`           | string | No       | Sort field: `timestamp` (default), `severity`          |
| `order`          | string | No       | `desc` (default), `asc`                                |

**Response: 200 OK**

```json
{
  "data": [
    {
      "event_id": "evt_9a8b7c6d-5e4f-3210-fedc-ba9876543210",
      "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "correlation_id": "cor_1234abcd-5678-efgh-ijkl-mnop90123456",
      "project_id": "proj_abc123",
      "agent_id": "agt_code_gen_01",
      "event_type": "agent_invocation",
      "severity": "info",
      "timestamp": "2026-03-23T15:15:00Z",
      "payload": {
        "action": "generate_code",
        "input_tokens": 4500,
        "output_tokens": 1200,
        "duration_ms": 3420,
        "model": "claude-sonnet-4-20250514",
        "status": "success"
      }
    },
    {
      "event_id": "evt_8b7c6d5e-4f3a-2109-edcb-a98765432109",
      "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "correlation_id": "cor_1234abcd-5678-efgh-ijkl-mnop90123456",
      "project_id": "proj_abc123",
      "agent_id": null,
      "event_type": "approval_decision",
      "severity": "info",
      "timestamp": "2026-03-23T15:35:00Z",
      "payload": {
        "approval_id": "apr_1a2b3c4d-e5f6-7890-abcd-ef0123456789",
        "decision": "approved",
        "decision_by": "sarah@acme.com",
        "step_id": "step_05"
      }
    }
  ],
  "meta": {
    "total": 1247,
    "page": 1,
    "per_page": 20,
    "total_pages": 63,
    "request_id": "b2c3d4e5-a1f6-7890-0123-4abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.6.2 Get Audit Event

`GET /api/v1/audit/events/{event_id}`

Returns a single audit event with full payload detail.

**Path Parameters:**

| Param      | Type   | Description               |
|------------|--------|---------------------------|
| `event_id` | string | Audit event identifier     |

**Response: 200 OK**

```json
{
  "data": {
    "event_id": "evt_9a8b7c6d-5e4f-3210-fedc-ba9876543210",
    "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "correlation_id": "cor_1234abcd-5678-efgh-ijkl-mnop90123456",
    "project_id": "proj_abc123",
    "agent_id": "agt_code_gen_01",
    "event_type": "agent_invocation",
    "severity": "info",
    "timestamp": "2026-03-23T15:15:00Z",
    "payload": {
      "action": "generate_code",
      "input_tokens": 4500,
      "output_tokens": 1200,
      "duration_ms": 3420,
      "model": "claude-sonnet-4-20250514",
      "status": "success",
      "files_generated": [
        "src/auth/handler.py",
        "src/auth/middleware.py",
        "tests/test_auth_handler.py"
      ]
    }
  },
  "meta": {
    "request_id": "c3d4e5f6-b2a1-7890-1234-5abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.6.3 Export Audit Events (CSV)

`GET /api/v1/audit/events/export`

Exports filtered audit events as a CSV download. Uses the same query parameters as the list endpoint. Returns a `202 Accepted` with a download URL for large exports.

**Query Parameters:** Same as [4.6.1 Query Audit Events](#461-query-audit-events), minus `page` and `per_page`.

Additional parameters:

| Param    | Type   | Required | Description                                |
|----------|--------|----------|--------------------------------------------|
| `format` | string | No       | `csv` (default), `json`                    |

**Response: 200 OK** (for small exports, < 10,000 rows)

Returns `Content-Type: text/csv` with the file body directly.

```
event_id,session_id,correlation_id,project_id,agent_id,event_type,severity,timestamp
evt_9a8b7c6d-5e4f-3210-fedc-ba9876543210,ses_a1b2c3d4-...,cor_1234abcd-...,proj_abc123,agt_code_gen_01,agent_invocation,info,2026-03-23T15:15:00Z
```

**Response: 202 Accepted** (for large exports, >= 10,000 rows)

```json
{
  "data": {
    "export_id": "exp_abc123def456",
    "status": "processing",
    "estimated_rows": 45000,
    "download_url": null,
    "expires_at": null
  },
  "meta": {
    "request_id": "d4e5f6a1-c3b2-7890-2345-6abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

Poll `GET /api/v1/audit/events/export/{export_id}` to retrieve the download URL when processing completes.

---

### 4.7 Sessions

**Persona:** Priya (Platform Engineer)
**Permission prefix:** `sessions:`

---

#### 4.7.1 Get Session Context

`GET /api/v1/sessions/{session_id}`

Returns the full session context including all key-value pairs.

**Path Parameters:**

| Param        | Type   | Description            |
|--------------|--------|------------------------|
| `session_id` | string | Session identifier      |

**Response: 200 OK**

```json
{
  "data": {
    "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "created_at": "2026-03-23T15:00:00Z",
    "keys": [
      {
        "key": "project_config",
        "written_by": "agt_req_analyzer_01",
        "ttl_seconds": 86400,
        "expires_at": "2026-03-24T15:00:00Z",
        "updated_at": "2026-03-23T15:03:00Z"
      },
      {
        "key": "requirements_output",
        "written_by": "agt_req_analyzer_01",
        "ttl_seconds": null,
        "expires_at": null,
        "updated_at": "2026-03-23T15:03:30Z"
      },
      {
        "key": "architecture_output",
        "written_by": "agt_arch_designer_01",
        "ttl_seconds": null,
        "expires_at": null,
        "updated_at": "2026-03-23T15:07:15Z"
      }
    ],
    "key_count": 3
  },
  "meta": {
    "request_id": "e5f6a1b2-d4c3-7890-3456-7abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.7.2 List Session Keys

`GET /api/v1/sessions/{session_id}/keys`

Returns all keys in a session with metadata (without values for performance).

**Path Parameters:**

| Param        | Type   | Description            |
|--------------|--------|------------------------|
| `session_id` | string | Session identifier      |

**Response: 200 OK**

```json
{
  "data": [
    {
      "key": "project_config",
      "written_by": "agt_req_analyzer_01",
      "ttl_seconds": 86400,
      "expires_at": "2026-03-24T15:00:00Z",
      "size_bytes": 1240,
      "updated_at": "2026-03-23T15:03:00Z"
    },
    {
      "key": "requirements_output",
      "written_by": "agt_req_analyzer_01",
      "ttl_seconds": null,
      "expires_at": null,
      "size_bytes": 8420,
      "updated_at": "2026-03-23T15:03:30Z"
    }
  ],
  "meta": {
    "total": 3,
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "request_id": "f6a1b2c3-e5d4-7890-4567-8abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.7.3 Get Session Key Value

`GET /api/v1/sessions/{session_id}/keys/{key}`

Returns the value of a specific key within a session context.

**Path Parameters:**

| Param        | Type   | Description            |
|--------------|--------|------------------------|
| `session_id` | string | Session identifier      |
| `key`        | string | Context key name        |

**Response: 200 OK**

```json
{
  "data": {
    "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "key": "requirements_output",
    "value": {
      "functional_requirements": [
        {
          "id": "FR-001",
          "title": "User Authentication",
          "description": "System shall support JWT-based authentication.",
          "priority": "must-have"
        }
      ],
      "non_functional_requirements": [
        {
          "id": "NFR-001",
          "title": "Response Time",
          "description": "API responses must be under 200ms at p95."
        }
      ]
    },
    "written_by": "agt_req_analyzer_01",
    "ttl_seconds": null,
    "updated_at": "2026-03-23T15:03:30Z"
  },
  "meta": {
    "request_id": "a1b2c3d4-f6e5-7890-5678-9abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.7.4 Delete Session Key

`DELETE /api/v1/sessions/{session_id}/keys/{key}`

Deletes a specific key from the session context.

**Path Parameters:**

| Param        | Type   | Description            |
|--------------|--------|------------------------|
| `session_id` | string | Session identifier      |
| `key`        | string | Context key name        |

**Response: 200 OK**

```json
{
  "data": {
    "session_id": "ses_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "key": "project_config",
    "deleted": true,
    "deleted_at": "2026-03-23T15:45:00Z"
  },
  "meta": {
    "request_id": "b2c3d4e5-a1f6-7890-6789-0abcdef12345",
    "timestamp": "2026-03-23T15:45:00Z"
  },
  "errors": []
}
```

---

### 4.8 Knowledge Exceptions

**Persona:** Priya (Platform Engineer)
**Permission prefix:** `knowledge:`

---

#### 4.8.1 List Knowledge Exceptions

`GET /api/v1/knowledge/exceptions`

Returns a paginated list of knowledge exception rules.

**Query Parameters:**

| Param       | Type   | Required | Description                                    |
|-------------|--------|----------|------------------------------------------------|
| `severity`  | string | No       | Filter: `low`, `medium`, `high`, `critical`    |
| `tier`      | string | No       | Filter by tier (e.g., `tier1`, `tier2`)        |
| `stack_name`| string | No       | Filter by technology stack                     |
| `active`    | bool   | No       | Filter by active status (default: `true`)      |
| `search`    | string | No       | Search by title or rule (partial match)        |
| `page`      | int    | No       | Page number (default: 1)                       |
| `per_page`  | int    | No       | Items per page (default: 20)                   |

**Response: 200 OK**

```json
{
  "data": [
    {
      "exception_id": "kex_a1b2c3d4-e5f6-7890-abcd-ef0123456789",
      "title": "Avoid raw SQL in ORM models",
      "rule": "Do not use raw SQL queries when an ORM method exists. Use SQLAlchemy query builder or ORM relationships.",
      "severity": "high",
      "tier": "tier1",
      "stack_name": "python-postgres",
      "client_id": null,
      "active": true,
      "fire_count": 42,
      "created_at": "2026-02-01T10:00:00Z",
      "updated_at": "2026-03-20T14:00:00Z"
    },
    {
      "exception_id": "kex_b2c3d4e5-f6a1-7890-bcde-f01234567890",
      "title": "Require type hints on all public functions",
      "rule": "All public function signatures must include full type annotations for parameters and return types.",
      "severity": "medium",
      "tier": "tier1",
      "stack_name": "python",
      "client_id": null,
      "active": true,
      "fire_count": 128,
      "created_at": "2026-02-05T08:00:00Z",
      "updated_at": "2026-03-15T11:00:00Z"
    }
  ],
  "meta": {
    "total": 24,
    "page": 1,
    "per_page": 20,
    "total_pages": 2,
    "request_id": "c3d4e5f6-b2a1-7890-7890-1abcdef12345",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.8.2 Create Knowledge Exception

`POST /api/v1/knowledge/exceptions`

Creates a new knowledge exception rule.

**Request Body:**

```json
{
  "title": "Enforce async database calls",
  "rule": "All database operations must use async/await patterns via asyncpg or async SQLAlchemy. Synchronous database calls are prohibited in request handlers.",
  "severity": "high",
  "tier": "tier1",
  "stack_name": "python-postgres",
  "client_id": null,
  "active": true
}
```

**Response: 201 Created**

```json
{
  "data": {
    "exception_id": "kex_c3d4e5f6-a1b2-7890-cdef-012345678901",
    "title": "Enforce async database calls",
    "rule": "All database operations must use async/await patterns via asyncpg or async SQLAlchemy. Synchronous database calls are prohibited in request handlers.",
    "severity": "high",
    "tier": "tier1",
    "stack_name": "python-postgres",
    "client_id": null,
    "active": true,
    "fire_count": 0,
    "created_at": "2026-03-23T16:00:00Z",
    "updated_at": "2026-03-23T16:00:00Z"
  },
  "meta": {
    "request_id": "d4e5f6a1-c3b2-7890-8901-2abcdef12345",
    "timestamp": "2026-03-23T16:00:00Z"
  },
  "errors": []
}
```

---

#### 4.8.3 Promote Knowledge Exception

`POST /api/v1/knowledge/exceptions/{exception_id}/promote`

Promotes a knowledge exception to a higher tier, increasing its enforcement priority.

**Path Parameters:**

| Param          | Type   | Description                    |
|----------------|--------|--------------------------------|
| `exception_id` | string | Knowledge exception identifier  |

**Request Body:**

```json
{
  "target_tier": "tier1",
  "reason": "High fire count (128) indicates this is a common violation. Promoting for stricter enforcement."
}
```

**Response: 200 OK**

```json
{
  "data": {
    "exception_id": "kex_b2c3d4e5-f6a1-7890-bcde-f01234567890",
    "title": "Require type hints on all public functions",
    "previous_tier": "tier2",
    "tier": "tier1",
    "promoted_at": "2026-03-23T16:10:00Z",
    "promoted_reason": "High fire count (128) indicates this is a common violation. Promoting for stricter enforcement."
  },
  "meta": {
    "request_id": "e5f6a1b2-d4c3-7890-9012-3abcdef12345",
    "timestamp": "2026-03-23T16:10:00Z"
  },
  "errors": []
}
```

---

#### 4.8.4 Deactivate Knowledge Exception

`POST /api/v1/knowledge/exceptions/{exception_id}/deactivate`

Deactivates a knowledge exception. The rule remains in the database for historical reference but is no longer enforced.

**Path Parameters:**

| Param          | Type   | Description                    |
|----------------|--------|--------------------------------|
| `exception_id` | string | Knowledge exception identifier  |

**Request Body:**

```json
{
  "reason": "Superseded by linter rule PY-042. No longer needed as agent-level enforcement."
}
```

**Response: 200 OK**

```json
{
  "data": {
    "exception_id": "kex_a1b2c3d4-e5f6-7890-abcd-ef0123456789",
    "title": "Avoid raw SQL in ORM models",
    "active": false,
    "deactivated_at": "2026-03-23T16:15:00Z",
    "deactivated_reason": "Superseded by linter rule PY-042. No longer needed as agent-level enforcement."
  },
  "meta": {
    "request_id": "f6a1b2c3-e5d4-7890-0123-4abcdef12345",
    "timestamp": "2026-03-23T16:15:00Z"
  },
  "errors": []
}
```

---

### 4.9 Health

**Persona:** Marcus (DevOps) / Infrastructure
**Permission:** Public (no authentication required)

---

#### 4.9.1 Health Check (Liveness)

`GET /api/v1/health`

Returns basic liveness status. Used by load balancers and container orchestrators. Always responds if the process is running.

**Response: 200 OK**

```json
{
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 5832000,
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "meta": {
    "request_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

---

#### 4.9.2 Readiness Check

`GET /api/v1/ready`

Returns readiness status including dependency health. Used by orchestrators to determine if the service should receive traffic.

**Response: 200 OK** (all dependencies healthy)

```json
{
  "data": {
    "status": "ready",
    "checks": {
      "database": {
        "status": "healthy",
        "latency_ms": 3,
        "details": "PostgreSQL 15.4 - 12 active connections"
      },
      "cache": {
        "status": "healthy",
        "latency_ms": 1,
        "details": "Redis 7.2 - memory usage 45%"
      },
      "agent_fleet": {
        "status": "healthy",
        "active_agents": 10,
        "degraded_agents": 1,
        "circuit_open_agents": 0
      }
    },
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "meta": {
    "request_id": "b2c3d4e5-f6a1-7890-2345-67890abcdef0",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": []
}
```

**Response: 503 Service Unavailable** (dependency unhealthy)

```json
{
  "data": {
    "status": "not_ready",
    "checks": {
      "database": {
        "status": "unhealthy",
        "latency_ms": null,
        "details": "Connection refused - PostgreSQL not reachable"
      },
      "cache": {
        "status": "healthy",
        "latency_ms": 1,
        "details": "Redis 7.2 - memory usage 45%"
      },
      "agent_fleet": {
        "status": "degraded",
        "active_agents": 8,
        "degraded_agents": 2,
        "circuit_open_agents": 2
      }
    },
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "meta": {
    "request_id": "c3d4e5f6-a1b2-7890-3456-7890abcdef01",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": [
    {
      "code": "dependency_unhealthy",
      "message": "Database connection failed.",
      "field": null,
      "detail": "PostgreSQL at db.internal:5432 is not reachable."
    }
  ]
}
```

---

## 5. WebSocket / SSE Channels

All WebSocket connections require authentication via a `token` query parameter: `wss://api.agentic-sdlc.io/ws/pipeline/{run_id}?token=<jwt>`.

### 5.1 Pipeline Progress

**Endpoint:** `ws /ws/pipeline/{run_id}`

Streams real-time step completion updates for a specific pipeline run. The connection closes automatically when the pipeline reaches a terminal state (`completed`, `failed`, `cancelled`).

**Connection:**

```
wss://api.agentic-sdlc.io/ws/pipeline/run_7f3a2b1c-d4e5-6789-abcd-ef0123456789?token=eyJhbGciOi...
```

**Server Messages:**

Step started:
```json
{
  "type": "step_started",
  "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
  "step_id": "step_05",
  "agent_id": "agt_code_gen_01",
  "step_name": "Code Generation",
  "started_at": "2026-03-23T15:15:00Z",
  "progress_pct": 33.3,
  "timestamp": "2026-03-23T15:15:00Z"
}
```

Step completed:
```json
{
  "type": "step_completed",
  "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
  "step_id": "step_05",
  "agent_id": "agt_code_gen_01",
  "step_name": "Code Generation",
  "status": "completed",
  "cost_usd": 0.45,
  "duration_seconds": 210,
  "completed_at": "2026-03-23T15:18:30Z",
  "progress_pct": 41.7,
  "timestamp": "2026-03-23T15:18:30Z"
}
```

Step failed:
```json
{
  "type": "step_failed",
  "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
  "step_id": "step_08",
  "agent_id": "agt_api_designer_01",
  "step_name": "API Contract Generation",
  "status": "failed",
  "error_message": "Agent timeout after 120 seconds.",
  "progress_pct": 58.3,
  "timestamp": "2026-03-23T15:30:00Z"
}
```

Approval required:
```json
{
  "type": "approval_required",
  "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
  "step_id": "step_05",
  "approval_id": "apr_1a2b3c4d-e5f6-7890-abcd-ef0123456789",
  "summary": "Code generation complete. Review required.",
  "timestamp": "2026-03-23T15:18:30Z"
}
```

Pipeline completed:
```json
{
  "type": "pipeline_completed",
  "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
  "status": "completed",
  "total_cost_usd": 3.21,
  "total_duration_seconds": 2520,
  "steps_completed": 12,
  "steps_failed": 0,
  "completed_at": "2026-03-23T15:42:00Z",
  "timestamp": "2026-03-23T15:42:00Z"
}
```

**Client Messages:**

Ping (keepalive):
```json
{
  "type": "ping"
}
```

Server responds with:
```json
{
  "type": "pong",
  "timestamp": "2026-03-23T15:30:00Z"
}
```

---

### 5.2 Cost Alerts

**Endpoint:** `ws /ws/cost-alerts`

Streams real-time budget threshold breach notifications. Remains open for the duration of the client session.

**Connection:**

```
wss://api.agentic-sdlc.io/ws/cost-alerts?token=eyJhbGciOi...
```

**Server Messages:**

Budget threshold warning:
```json
{
  "type": "budget_warning",
  "level": "warning",
  "project_id": "proj_abc123",
  "project_name": "Q1 Auth Feature",
  "current_spend_usd": 850.00,
  "budget_limit_usd": 1000.00,
  "utilization_pct": 85.0,
  "threshold_pct": 80,
  "message": "Project 'Q1 Auth Feature' has reached 85% of its monthly budget.",
  "timestamp": "2026-03-23T15:30:00Z"
}
```

Budget threshold critical:
```json
{
  "type": "budget_critical",
  "level": "critical",
  "project_id": "proj_abc123",
  "project_name": "Q1 Auth Feature",
  "current_spend_usd": 960.00,
  "budget_limit_usd": 1000.00,
  "utilization_pct": 96.0,
  "threshold_pct": 95,
  "message": "Project 'Q1 Auth Feature' has reached 96% of its monthly budget. Pipeline triggering will be blocked at 100%.",
  "timestamp": "2026-03-23T16:00:00Z"
}
```

Budget exceeded:
```json
{
  "type": "budget_exceeded",
  "level": "critical",
  "project_id": "proj_abc123",
  "project_name": "Q1 Auth Feature",
  "current_spend_usd": 1005.30,
  "budget_limit_usd": 1000.00,
  "utilization_pct": 100.5,
  "message": "Project 'Q1 Auth Feature' has exceeded its monthly budget. New pipeline runs are blocked.",
  "blocked": true,
  "timestamp": "2026-03-23T17:00:00Z"
}
```

---

### 5.3 Approval Notifications

**Endpoint:** `ws /ws/approvals`

Streams notifications when new approval requests are created. Used by the Approval Queue dashboard to show real-time updates.

**Connection:**

```
wss://api.agentic-sdlc.io/ws/approvals?token=eyJhbGciOi...
```

**Server Messages:**

New approval request:
```json
{
  "type": "new_approval",
  "approval_id": "apr_1a2b3c4d-e5f6-7890-abcd-ef0123456789",
  "pipeline_name": "12-doc-generation",
  "run_id": "run_7f3a2b1c-d4e5-6789-abcd-ef0123456789",
  "step_id": "step_05",
  "step_name": "Code Generation",
  "project_id": "proj_abc123",
  "summary": "Code generation complete. 14 files generated. Review required before integration testing.",
  "requested_at": "2026-03-23T15:20:00Z",
  "timestamp": "2026-03-23T15:20:00Z"
}
```

Approval resolved (by another user):
```json
{
  "type": "approval_resolved",
  "approval_id": "apr_1a2b3c4d-e5f6-7890-abcd-ef0123456789",
  "status": "approved",
  "decision_by": "sarah@acme.com",
  "decided_at": "2026-03-23T15:35:00Z",
  "timestamp": "2026-03-23T15:35:00Z"
}
```

---

## 6. Error Codes

### HTTP Status Code Mapping

| HTTP Status | Usage                                              |
|-------------|---------------------------------------------------|
| 200         | Successful read, update, or action                 |
| 201         | Successful resource creation                       |
| 202         | Accepted (async processing started)                |
| 400         | Client error (validation, bad request)             |
| 401         | Authentication failed or missing                   |
| 403         | Authenticated but insufficient permissions         |
| 404         | Resource not found                                 |
| 409         | Conflict (duplicate ID, concurrent modification)   |
| 422         | Unprocessable entity (semantic validation failure) |
| 429         | Rate limit exceeded                                |
| 500         | Internal server error                              |
| 503         | Service unavailable (dependency down)              |

### Application Error Codes

| Error Code            | HTTP Status | Description                                           | When It Occurs                                              |
|-----------------------|-------------|-------------------------------------------------------|-------------------------------------------------------------|
| `validation_error`    | 400         | Request body or query parameters fail validation.     | Missing required fields, invalid types, out-of-range values.|
| `auth_failed`         | 401         | Authentication credentials are missing or invalid.    | Expired JWT, invalid API key, missing auth header.          |
| `permission_denied`   | 403         | Authenticated user lacks required permission.         | Role does not include the required permission scope.        |
| `not_found`           | 404         | The requested resource does not exist.                | Invalid ID, deleted resource, wrong path.                   |
| `conflict`            | 409         | Request conflicts with current resource state.        | Duplicate agent ID, approving an already-resolved approval. |
| `rate_limited`        | 429         | Client has exceeded the rate limit.                   | Too many requests within the rate window.                   |
| `budget_exceeded`     | 422         | Project or fleet budget has been exceeded.            | Attempting to trigger a pipeline when budget is exhausted.  |
| `pipeline_failed`     | 422         | Pipeline action cannot be performed in current state. | Resuming a completed pipeline, triggering on a cancelled run.|
| `approval_timeout`    | 422         | Approval request has expired.                         | Attempting to approve/reject after the timeout window.      |
| `canary_conflict`     | 409         | Agent already has an active canary deployment.        | Setting a canary when one is already evaluating.            |
| `export_too_large`    | 422         | Export request exceeds maximum row limit.             | Audit export with > 1,000,000 matching rows.               |
| `internal_error`      | 500         | An unexpected server error occurred.                  | Unhandled exception, infrastructure failure.                |
| `service_unavailable` | 503         | A required dependency is unavailable.                 | Database down, cache unreachable, agent fleet degraded.     |

### Error Response Example

```json
{
  "data": null,
  "meta": {
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": [
    {
      "code": "budget_exceeded",
      "message": "Project budget has been exceeded.",
      "field": null,
      "detail": "Project 'proj_abc123' has spent $1,005.30 of its $1,000.00 monthly budget. New pipeline runs are blocked until the budget is increased or the next billing cycle begins."
    }
  ]
}
```

Multiple errors can be returned in a single response (e.g., multiple validation failures):

```json
{
  "data": null,
  "meta": {
    "request_id": "b2c3d4e5-f6a1-7890-bcde-f01234567890",
    "timestamp": "2026-03-23T15:30:00Z"
  },
  "errors": [
    {
      "code": "validation_error",
      "message": "Field 'name' is required.",
      "field": "name",
      "detail": "Agent name must be 3-128 characters."
    },
    {
      "code": "validation_error",
      "message": "Field 'phase' has invalid value.",
      "field": "phase",
      "detail": "Must be one of: requirements, design, code, test, documentation, review, deploy."
    }
  ]
}
```

---

## 7. Rate Limiting

Rate limits are enforced per authentication principal (user or API key).

| Tier          | Requests / Minute | Burst (per second) | Applied To                |
|---------------|-------------------|---------------------|---------------------------|
| Standard      | 300               | 10                  | Dashboard users (JWT)     |
| Programmatic  | 600               | 20                  | API key access            |
| Export        | 10                | 1                   | CSV export endpoints      |
| WebSocket     | 5 connections     | --                  | Per user, concurrent      |

### Rate Limit Headers

Every response includes rate-limit headers:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 287
X-RateLimit-Reset: 1711180260
```

When rate limited, the response is:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1711180260
```

---

## 8. Appendix: Endpoint Summary Matrix

| #  | Method | Path                                                  | Auth     | Persona      |
|----|--------|-------------------------------------------------------|----------|--------------|
| 1  | POST   | `/api/v1/auth/token`                                  | Public   | All          |
| 2  | POST   | `/api/v1/auth/refresh`                                | Bearer   | All          |
| 3  | GET    | `/api/v1/agents`                                      | Bearer/Key | Priya      |
| 4  | GET    | `/api/v1/agents/{agent_id}`                           | Bearer/Key | Priya      |
| 5  | POST   | `/api/v1/agents`                                      | Bearer/Key | Priya      |
| 6  | PUT    | `/api/v1/agents/{agent_id}`                           | Bearer/Key | Priya      |
| 7  | DELETE | `/api/v1/agents/{agent_id}`                           | Bearer/Key | Priya      |
| 8  | GET    | `/api/v1/agents/{agent_id}/health`                    | Bearer/Key | Priya/Marcus |
| 9  | POST   | `/api/v1/agents/{agent_id}/canary`                    | Bearer/Key | Priya      |
| 10 | POST   | `/api/v1/agents/{agent_id}/canary/promote`            | Bearer/Key | Priya      |
| 11 | POST   | `/api/v1/agents/{agent_id}/canary/rollback`           | Bearer/Key | Priya      |
| 12 | POST   | `/api/v1/pipelines`                                   | Bearer/Key | David      |
| 13 | GET    | `/api/v1/pipelines/{run_id}`                          | Bearer/Key | David      |
| 14 | GET    | `/api/v1/pipelines`                                   | Bearer/Key | David      |
| 15 | GET    | `/api/v1/pipelines/{run_id}/detail`                   | Bearer/Key | David      |
| 16 | GET    | `/api/v1/pipelines/{run_id}/steps`                    | Bearer/Key | David      |
| 17 | POST   | `/api/v1/pipelines/{run_id}/resume`                   | Bearer/Key | David      |
| 18 | GET    | `/api/v1/approvals`                                   | Bearer/Key | Sarah      |
| 19 | GET    | `/api/v1/approvals/{approval_id}`                     | Bearer/Key | Sarah      |
| 20 | POST   | `/api/v1/approvals/{approval_id}/approve`             | Bearer/Key | Sarah      |
| 21 | POST   | `/api/v1/approvals/{approval_id}/reject`              | Bearer/Key | Sarah      |
| 22 | GET    | `/api/v1/cost/fleet`                                  | Bearer/Key | Marcus     |
| 23 | GET    | `/api/v1/cost/projects/{project_id}`                  | Bearer/Key | Marcus     |
| 24 | GET    | `/api/v1/cost/agents/{agent_id}`                      | Bearer/Key | Marcus     |
| 25 | GET    | `/api/v1/cost/breakdown`                              | Bearer/Key | Marcus     |
| 26 | GET    | `/api/v1/audit/events`                                | Bearer/Key | Lisa       |
| 27 | GET    | `/api/v1/audit/events/{event_id}`                     | Bearer/Key | Lisa       |
| 28 | GET    | `/api/v1/audit/events/export`                         | Bearer/Key | Lisa       |
| 29 | GET    | `/api/v1/sessions/{session_id}`                       | Bearer/Key | Priya      |
| 30 | GET    | `/api/v1/sessions/{session_id}/keys`                  | Bearer/Key | Priya      |
| 31 | GET    | `/api/v1/sessions/{session_id}/keys/{key}`            | Bearer/Key | Priya      |
| 32 | DELETE | `/api/v1/sessions/{session_id}/keys/{key}`            | Bearer/Key | Priya      |
| 33 | GET    | `/api/v1/knowledge/exceptions`                        | Bearer/Key | Priya      |
| 34 | POST   | `/api/v1/knowledge/exceptions`                        | Bearer/Key | Priya      |
| 35 | POST   | `/api/v1/knowledge/exceptions/{exception_id}/promote` | Bearer/Key | Priya      |
| 36 | POST   | `/api/v1/knowledge/exceptions/{exception_id}/deactivate` | Bearer/Key | Priya   |
| 37 | GET    | `/api/v1/health`                                      | Public   | Marcus     |
| 38 | GET    | `/api/v1/ready`                                       | Public   | Marcus     |

### WebSocket Channels

| #  | Protocol | Path                          | Auth   | Persona       |
|----|----------|-------------------------------|--------|---------------|
| 39 | WS       | `/ws/pipeline/{run_id}`       | Token  | David         |
| 40 | WS       | `/ws/cost-alerts`             | Token  | Marcus        |
| 41 | WS       | `/ws/approvals`               | Token  | Sarah         |

---

*End of API Contracts -- 41 total endpoints (38 HTTP + 3 WebSocket channels)*
