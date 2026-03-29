# MCP-TOOL-SPEC --- Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 08 of 24 | Status: Draft
**Reads from:** INTERACTION-MAP (Doc 07) --- all tool names, data shapes, and interaction IDs are defined there.

---

## Table of Contents

1. [MCP Server Inventory](#1-mcp-server-inventory)
2. [Server Specifications](#2-server-specifications)
   - 2.1 [agentic-sdlc-agents](#21-agentic-sdlc-agents)
   - 2.2 [agentic-sdlc-governance](#22-agentic-sdlc-governance)
   - 2.3 [agentic-sdlc-knowledge](#23-agentic-sdlc-knowledge)
   - 2.4 [System Tools](#24-system-tools)
3. [MCP Resources](#3-mcp-resources)
4. [MCP Prompt Templates](#4-mcp-prompt-templates)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [Error Handling](#6-error-handling)
7. [Rate Limiting](#7-rate-limiting)
8. [REST API Derivation Table](#8-rest-api-derivation-table)
9. [Testing MCP Tools](#9-testing-mcp-tools)

---

## 1. MCP Server Inventory

| Server Name | Domain | Transport (Dev) | Transport (Prod) | Auth Method | Tool Count | Resource Count | Prompt Count |
|---|---|---|---|---|---|---|---|
| `agentic-sdlc-agents` | Pipeline + Agent Operations | stdio | streamable-http (port 3100) | API Key (`ANTHROPIC_API_KEY`) | 18 | 4 | 2 |
| `agentic-sdlc-governance` | Cost + Audit + Approvals | stdio | streamable-http (port 3101) | API Key (`ANTHROPIC_API_KEY`) | 10 | 3 | 2 |
| `agentic-sdlc-knowledge` | Exception Knowledge Base | stdio | streamable-http (port 3102) | API Key (`ANTHROPIC_API_KEY`) | 4 | 2 | 1 |
| *(cross-server)* | System Observability | stdio | streamable-http (port 3100) | API Key (`ANTHROPIC_API_KEY`) | 3 | 1 | 1 |
| **Totals** | | | | | **35** | **10** | **6** |

### Connection Configuration

**Local development (`stdio`):**
```json
{
  "mcpServers": {
    "agentic-sdlc-agents": {
      "command": "node",
      "args": ["./dist/mcp-servers/agents/index.js"],
      "env": { "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}" }
    },
    "agentic-sdlc-governance": {
      "command": "node",
      "args": ["./dist/mcp-servers/governance/index.js"],
      "env": { "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}" }
    },
    "agentic-sdlc-knowledge": {
      "command": "node",
      "args": ["./dist/mcp-servers/knowledge/index.js"],
      "env": { "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}" }
    }
  }
}
```

**Production (`streamable-http`):**
```json
{
  "mcpServers": {
    "agentic-sdlc-agents": {
      "url": "https://mcp.agentic-sdlc.example.com:3100/mcp",
      "headers": { "Authorization": "Bearer ${ANTHROPIC_API_KEY}" }
    },
    "agentic-sdlc-governance": {
      "url": "https://mcp.agentic-sdlc.example.com:3101/mcp",
      "headers": { "Authorization": "Bearer ${ANTHROPIC_API_KEY}" }
    },
    "agentic-sdlc-knowledge": {
      "url": "https://mcp.agentic-sdlc.example.com:3102/mcp",
      "headers": { "Authorization": "Bearer ${ANTHROPIC_API_KEY}" }
    }
  }
}
```

---

## 2. Server Specifications

---

### 2.1 agentic-sdlc-agents

**Domain:** Pipeline orchestration and agent lifecycle management
**Port:** 3100
**Tool count:** 18 (I-001 through I-009, I-020 through I-027, plus I-080 through I-082 as system tools)

---

#### Tool: `trigger_pipeline`

| Field | Value |
|---|---|
| **Interaction ID** | I-001 |
| **Description** | Triggers a new pipeline run for a given project, creating all document-generation stages and returning the run ID. |
| **Shared Service** | `PipelineService.trigger()` |
| **Side Effects** | Creates a `PipelineRun` record in the database; enqueues stage-0 (requirements) job; emits `pipeline.triggered` event; charges initial cost estimate against project budget. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["project_id", "brief"],
  "properties": {
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Unique project identifier (e.g., proj_abc123def456)"
    },
    "brief": {
      "type": "string",
      "minLength": 20,
      "maxLength": 5000,
      "description": "Natural-language project brief describing what the system should do"
    },
    "template": {
      "type": "string",
      "enum": ["full-stack-first", "api-first", "data-pipeline", "mobile-first"],
      "default": "full-stack-first",
      "description": "Pipeline template that determines document order and agent assignments"
    },
    "options": {
      "type": "object",
      "properties": {
        "skip_stages": {
          "type": "array",
          "items": { "type": "integer", "minimum": 0, "maximum": 13 },
          "description": "Stage indices to skip (use with caution)"
        },
        "cost_ceiling_usd": {
          "type": "number",
          "minimum": 1.0,
          "maximum": 500.0,
          "default": 25.0,
          "description": "Maximum total cost in USD for the entire pipeline run"
        },
        "priority": {
          "type": "string",
          "enum": ["low", "normal", "high"],
          "default": "normal",
          "description": "Scheduling priority for this pipeline run"
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

**Output:** `PipelineRun` --- Contains run_id, project_id, status, created_at, estimated_cost, and stage manifest.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |
| `BUDGET_EXCEEDED` | Pipeline cost ceiling of ${ceiling} would be exceeded | Estimated cost exceeds budget or ceiling |
| `PIPELINE_ALREADY_RUNNING` | Project `{project_id}` already has an active pipeline run | Concurrent run not allowed |
| `INVALID_TEMPLATE` | Template `{template}` is not recognized | Unknown template value |
| `BRIEF_TOO_SHORT` | Brief must be at least 20 characters | brief length < 20 |

**Example Prompt:**
> "Start a new full-stack-first pipeline for project proj_abc123def456 with the brief: Build a multi-tenant SaaS billing dashboard with Stripe integration."

---

#### Tool: `get_pipeline_status`

| Field | Value |
|---|---|
| **Interaction ID** | I-002 |
| **Description** | Returns the current status, progress, and stage breakdown of a specific pipeline run. |
| **Shared Service** | `PipelineService.getStatus()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["run_id"],
  "properties": {
    "run_id": {
      "type": "string",
      "pattern": "^run_[a-z0-9]{16}$",
      "description": "Pipeline run identifier returned by trigger_pipeline"
    },
    "include_stage_details": {
      "type": "boolean",
      "default": false,
      "description": "When true, includes per-stage timing, cost, and agent assignment details"
    }
  },
  "additionalProperties": false
}
```

**Output:** `PipelineRun` --- Full run object with status (queued | running | paused | completed | failed | cancelled), progress percentage, current stage, and optionally per-stage details.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | Pipeline run `{run_id}` not found | run_id does not exist |

**Example Prompt:**
> "What is the status of pipeline run run_a1b2c3d4e5f6g7h8?"

---

#### Tool: `list_pipeline_runs`

| Field | Value |
|---|---|
| **Interaction ID** | I-003 |
| **Description** | Lists pipeline runs with optional filtering by project, status, and date range. |
| **Shared Service** | `PipelineService.list()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Filter by project (omit for all projects)"
    },
    "status": {
      "type": "string",
      "enum": ["queued", "running", "paused", "completed", "failed", "cancelled"],
      "description": "Filter by pipeline status"
    },
    "since": {
      "type": "string",
      "format": "date-time",
      "description": "Return only runs created after this ISO-8601 timestamp"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 20,
      "description": "Maximum number of runs to return"
    },
    "offset": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Pagination offset"
    }
  },
  "additionalProperties": false
}
```

**Output:** `PipelineRun[]` --- Array of pipeline run summaries, sorted by created_at descending, with total count for pagination.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id filter references non-existent project |
| `INVALID_DATE_RANGE` | `since` must be a valid ISO-8601 timestamp | Malformed date |

**Example Prompt:**
> "Show me all running pipelines for project proj_abc123def456."

---

#### Tool: `resume_pipeline`

| Field | Value |
|---|---|
| **Interaction ID** | I-004 |
| **Description** | Resumes a paused pipeline run from its current stage, typically after a gate approval or manual intervention. |
| **Shared Service** | `PipelineService.resume()` |
| **Side Effects** | Updates run status from `paused` to `running`; re-enqueues the blocked stage job; emits `pipeline.resumed` event. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["run_id"],
  "properties": {
    "run_id": {
      "type": "string",
      "pattern": "^run_[a-z0-9]{16}$",
      "description": "Pipeline run identifier"
    },
    "override_context": {
      "type": "object",
      "description": "Optional additional context to inject into the next stage (e.g., reviewer feedback)",
      "additionalProperties": { "type": "string" }
    }
  },
  "additionalProperties": false
}
```

**Output:** `PipelineRun` --- Updated run object with status `running`.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | Pipeline run `{run_id}` not found | run_id does not exist |
| `PIPELINE_NOT_PAUSED` | Pipeline run `{run_id}` is not paused (current status: {status}) | Run is not in paused state |
| `APPROVAL_PENDING` | Pipeline run `{run_id}` has a pending gate approval at stage {stage} | Gate must be approved first |

**Example Prompt:**
> "Resume pipeline run run_a1b2c3d4e5f6g7h8 after the architecture review."

---

#### Tool: `cancel_pipeline`

| Field | Value |
|---|---|
| **Interaction ID** | I-005 |
| **Description** | Cancels an active pipeline run, stopping all in-progress stages and releasing reserved budget. |
| **Shared Service** | `PipelineService.cancel()` |
| **Side Effects** | Sets run status to `cancelled`; aborts any running agent invocations; releases budget hold; emits `pipeline.cancelled` event; records cancellation in audit log. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["run_id"],
  "properties": {
    "run_id": {
      "type": "string",
      "pattern": "^run_[a-z0-9]{16}$",
      "description": "Pipeline run identifier"
    },
    "reason": {
      "type": "string",
      "maxLength": 500,
      "description": "Human-readable cancellation reason (recorded in audit log)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `PipelineRun` --- Updated run object with status `cancelled` and final cost tally.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | Pipeline run `{run_id}` not found | run_id does not exist |
| `PIPELINE_ALREADY_TERMINAL` | Pipeline run `{run_id}` is already in terminal state: {status} | Run is completed, failed, or cancelled |

**Example Prompt:**
> "Cancel pipeline run_a1b2c3d4e5f6g7h8 because the requirements changed."

---

#### Tool: `get_pipeline_documents`

| Field | Value |
|---|---|
| **Interaction ID** | I-006 |
| **Description** | Retrieves the generated documents from a pipeline run, optionally filtered by document type or stage index. |
| **Shared Service** | `PipelineService.getDocuments()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["run_id"],
  "properties": {
    "run_id": {
      "type": "string",
      "pattern": "^run_[a-z0-9]{16}$",
      "description": "Pipeline run identifier"
    },
    "doc_type": {
      "type": "string",
      "enum": [
        "requirements", "arch-design", "interaction-map", "mcp-tool-spec",
        "design-spec", "test-strategy", "schema-spec", "api-spec",
        "environment-config", "cicd-pipeline", "code-review", "deploy-runbook",
        "monitoring-plan", "project-summary"
      ],
      "description": "Filter by specific document type"
    },
    "stage_index": {
      "type": "integer",
      "minimum": 0,
      "maximum": 13,
      "description": "Filter by pipeline stage index"
    },
    "format": {
      "type": "string",
      "enum": ["markdown", "json", "html"],
      "default": "markdown",
      "description": "Output format for the document content"
    }
  },
  "additionalProperties": false
}
```

**Output:** `PipelineDocument[]` --- Array of document objects containing doc_type, stage_index, content, generated_at, agent_id, token_count, and quality_score.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | Pipeline run `{run_id}` not found | run_id does not exist |
| `NO_DOCUMENTS_YET` | Pipeline run `{run_id}` has not produced any documents yet | Run is still queued |

**Example Prompt:**
> "Get the architecture design document from pipeline run run_a1b2c3d4e5f6g7h8."

---

#### Tool: `retry_pipeline_step`

| Field | Value |
|---|---|
| **Interaction ID** | I-007 |
| **Description** | Retries a specific failed stage within a pipeline run using the same or modified input context. |
| **Shared Service** | `PipelineService.retryStep()` |
| **Side Effects** | Resets stage status to `queued`; re-enqueues the stage job; increments retry counter; emits `pipeline.stage.retried` event; charges additional cost against budget. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["run_id", "stage_index"],
  "properties": {
    "run_id": {
      "type": "string",
      "pattern": "^run_[a-z0-9]{16}$",
      "description": "Pipeline run identifier"
    },
    "stage_index": {
      "type": "integer",
      "minimum": 0,
      "maximum": 13,
      "description": "Zero-based index of the stage to retry"
    },
    "modified_context": {
      "type": "object",
      "description": "Optional overrides to inject into the retry (e.g., additional instructions)",
      "additionalProperties": { "type": "string" }
    }
  },
  "additionalProperties": false
}
```

**Output:** `PipelineRun` --- Updated run object with the retried stage reset.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `PIPELINE_NOT_FOUND` | Pipeline run `{run_id}` not found | run_id does not exist |
| `STAGE_NOT_FAILED` | Stage {stage_index} is not in failed state (current: {status}) | Stage did not fail |
| `MAX_RETRIES_EXCEEDED` | Stage {stage_index} has exceeded maximum retry count of {max} | Too many retries |
| `BUDGET_EXCEEDED` | Retry would exceed pipeline cost ceiling | Insufficient budget |

**Example Prompt:**
> "Retry stage 3 of pipeline run run_a1b2c3d4e5f6g7h8 with additional context about the API design."

---

#### Tool: `get_pipeline_config`

| Field | Value |
|---|---|
| **Interaction ID** | I-008 |
| **Description** | Returns the pipeline configuration for a given template, including stage definitions, agent assignments, and gate rules. |
| **Shared Service** | `PipelineService.getConfig()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["template"],
  "properties": {
    "template": {
      "type": "string",
      "enum": ["full-stack-first", "api-first", "data-pipeline", "mobile-first"],
      "description": "Pipeline template name"
    }
  },
  "additionalProperties": false
}
```

**Output:** `PipelineConfig` --- Contains template name, stage definitions (name, agent_id, gate_type, estimated_cost_usd), total estimated cost, and supported options.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_TEMPLATE` | Template `{template}` is not recognized | Unknown template |

**Example Prompt:**
> "Show me the pipeline configuration for the full-stack-first template."

---

#### Tool: `validate_pipeline_input`

| Field | Value |
|---|---|
| **Interaction ID** | I-009 |
| **Description** | Validates a project brief and options against pipeline requirements without actually triggering a run. Returns validation warnings and estimated cost. |
| **Shared Service** | `PipelineService.validate()` |
| **Side Effects** | None (read-only, dry-run validation). |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["brief"],
  "properties": {
    "brief": {
      "type": "string",
      "description": "Project brief to validate"
    },
    "template": {
      "type": "string",
      "enum": ["full-stack-first", "api-first", "data-pipeline", "mobile-first"],
      "default": "full-stack-first",
      "description": "Pipeline template to validate against"
    },
    "options": {
      "type": "object",
      "properties": {
        "skip_stages": {
          "type": "array",
          "items": { "type": "integer" }
        },
        "cost_ceiling_usd": {
          "type": "number"
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

**Output:** `ValidationResult` --- Contains is_valid (boolean), warnings (string[]), errors (string[]), estimated_cost_usd, and estimated_duration_minutes.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_TEMPLATE` | Template `{template}` is not recognized | Unknown template |

**Example Prompt:**
> "Validate this brief before starting the pipeline: Build a real-time chat application with WebSocket support."

---

#### Tool: `list_agents`

| Field | Value |
|---|---|
| **Interaction ID** | I-020 |
| **Description** | Lists all registered agents in the fleet with optional filtering by role, maturity level, or health status. |
| **Shared Service** | `AgentService.list()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "role": {
      "type": "string",
      "enum": [
        "requirements-analyst", "architect", "interaction-mapper",
        "tool-spec-writer", "ui-designer", "test-strategist",
        "schema-designer", "api-designer", "env-configurator",
        "cicd-engineer", "code-reviewer", "deploy-engineer",
        "monitoring-engineer", "project-summarizer"
      ],
      "description": "Filter by agent role"
    },
    "maturity": {
      "type": "string",
      "enum": ["experimental", "beta", "ga", "deprecated"],
      "description": "Filter by maturity level"
    },
    "health": {
      "type": "string",
      "enum": ["healthy", "degraded", "unhealthy", "unknown"],
      "description": "Filter by current health status"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50,
      "default": 20,
      "description": "Maximum agents to return"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AgentSummary[]` --- Array of agent summaries containing agent_id, name, role, version, maturity, health_status, and last_invoked_at.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_ROLE` | Agent role `{role}` is not recognized | Unknown role value |

**Example Prompt:**
> "List all GA-maturity agents that are currently healthy."

---

#### Tool: `get_agent`

| Field | Value |
|---|---|
| **Interaction ID** | I-021 |
| **Description** | Returns full details for a specific agent, including its manifest, prompt template, version history, and performance metrics. |
| **Shared Service** | `AgentService.get()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["agent_id"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[A-Z][0-9]+-[a-z-]+$",
      "description": "Agent identifier (e.g., B1-code-reviewer, A2-architect)"
    },
    "include_metrics": {
      "type": "boolean",
      "default": false,
      "description": "Include performance metrics (avg latency, success rate, cost per invocation)"
    },
    "include_version_history": {
      "type": "boolean",
      "default": false,
      "description": "Include full version history"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AgentDetail` --- Full agent object with agent_id, name, role, description, model, version, maturity, manifest, prompt_template, performance_metrics, and version_history.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | Agent `{agent_id}` not found | agent_id does not exist |

**Example Prompt:**
> "Show me the full details of agent B1-code-reviewer including its performance metrics."

---

#### Tool: `invoke_agent`

| Field | Value |
|---|---|
| **Interaction ID** | I-022 |
| **Description** | Directly invokes an agent with a given input payload, outside of the normal pipeline flow. Useful for testing, one-off tasks, or interactive workflows. |
| **Shared Service** | `AgentService.invoke()` |
| **Side Effects** | Creates an invocation record; charges cost against the specified project budget; emits `agent.invoked` event; records token usage. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["agent_id", "project_id", "input"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[A-Z][0-9]+-[a-z-]+$",
      "description": "Agent identifier to invoke"
    },
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Project to bill this invocation against"
    },
    "input": {
      "type": "object",
      "required": ["content"],
      "properties": {
        "content": {
          "type": "string",
          "maxLength": 100000,
          "description": "The primary input content for the agent"
        },
        "context": {
          "type": "object",
          "description": "Additional structured context for the agent",
          "additionalProperties": true
        },
        "upstream_documents": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["doc_type", "content"],
            "properties": {
              "doc_type": { "type": "string" },
              "content": { "type": "string" }
            }
          },
          "description": "Previously generated documents to feed as context"
        }
      },
      "additionalProperties": false
    },
    "options": {
      "type": "object",
      "properties": {
        "max_tokens": {
          "type": "integer",
          "minimum": 100,
          "maximum": 200000,
          "default": 16000,
          "description": "Maximum output tokens"
        },
        "temperature": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.3,
          "description": "Model temperature"
        },
        "timeout_seconds": {
          "type": "integer",
          "minimum": 10,
          "maximum": 600,
          "default": 120,
          "description": "Maximum execution time in seconds"
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

**Output:** `AgentInvocationResult` --- Contains invocation_id, agent_id, status (success | error), output_content, token_usage (input_tokens, output_tokens), cost_usd, latency_ms, and model_used.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | Agent `{agent_id}` not found | agent_id does not exist |
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |
| `BUDGET_EXCEEDED` | Project `{project_id}` budget has been exceeded | Insufficient budget |
| `AGENT_UNHEALTHY` | Agent `{agent_id}` is currently unhealthy | Agent health check failing |
| `INVOCATION_TIMEOUT` | Agent invocation timed out after {timeout}s | Exceeded timeout |
| `AGENT_VERSION_DEPRECATED` | Agent `{agent_id}` version {version} is deprecated | Deprecated agent |

**Example Prompt:**
> "Invoke the B1-code-reviewer agent on project proj_abc123def456 to review the auth module code."

---

#### Tool: `check_agent_health`

| Field | Value |
|---|---|
| **Interaction ID** | I-023 |
| **Description** | Performs a health check on a specific agent or all agents, returning latency, error rates, and availability status. |
| **Shared Service** | `AgentService.checkHealth()` |
| **Side Effects** | Executes a lightweight probe invocation; updates the cached health status. |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[A-Z][0-9]+-[a-z-]+$",
      "description": "Specific agent to check (omit for all agents)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AgentHealth` or `AgentHealth[]` --- Contains agent_id, status (healthy | degraded | unhealthy), latency_ms, error_rate_percent, last_success_at, last_failure_at, and consecutive_failures.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | Agent `{agent_id}` not found | agent_id does not exist |

**Example Prompt:**
> "Check the health of all agents in the fleet."

---

#### Tool: `promote_agent_version`

| Field | Value |
|---|---|
| **Interaction ID** | I-024 |
| **Description** | Promotes an agent to a higher maturity level (experimental -> beta -> ga), after validating that promotion criteria are met. |
| **Shared Service** | `AgentService.promote()` |
| **Side Effects** | Updates agent maturity level; records promotion in audit log; emits `agent.promoted` event; notifies fleet administrators. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["agent_id", "target_maturity"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[A-Z][0-9]+-[a-z-]+$",
      "description": "Agent identifier to promote"
    },
    "target_maturity": {
      "type": "string",
      "enum": ["beta", "ga"],
      "description": "Target maturity level"
    },
    "justification": {
      "type": "string",
      "maxLength": 1000,
      "description": "Reason for the promotion (recorded in audit log)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AgentVersion` --- Contains agent_id, previous_maturity, new_maturity, promoted_at, promoted_by, and version.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | Agent `{agent_id}` not found | agent_id does not exist |
| `INVALID_PROMOTION_PATH` | Cannot promote from `{current}` to `{target}` | Invalid maturity transition |
| `PROMOTION_CRITERIA_NOT_MET` | Agent does not meet promotion criteria: {details} | Insufficient success rate, too few invocations, etc. |

**Example Prompt:**
> "Promote agent B1-code-reviewer from beta to GA maturity."

---

#### Tool: `rollback_agent_version`

| Field | Value |
|---|---|
| **Interaction ID** | I-025 |
| **Description** | Rolls back an agent to its previous version, restoring the prior prompt template and configuration. |
| **Shared Service** | `AgentService.rollback()` |
| **Side Effects** | Swaps active version to previous; records rollback in audit log; emits `agent.rolledback` event; resets health metrics for the new active version. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["agent_id"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[A-Z][0-9]+-[a-z-]+$",
      "description": "Agent identifier to roll back"
    },
    "target_version": {
      "type": "string",
      "pattern": "^v[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "Specific version to roll back to (omit for previous version)"
    },
    "reason": {
      "type": "string",
      "maxLength": 1000,
      "description": "Reason for the rollback (recorded in audit log)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AgentVersion` --- Contains agent_id, previous_version, new_version, rolled_back_at, and rolled_back_by.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | Agent `{agent_id}` not found | agent_id does not exist |
| `NO_PREVIOUS_VERSION` | Agent `{agent_id}` has no previous version to roll back to | First version |
| `VERSION_NOT_FOUND` | Version `{target_version}` not found for agent `{agent_id}` | target_version does not exist |

**Example Prompt:**
> "Roll back agent A2-architect to its previous version because the new prompt is generating incomplete designs."

---

#### Tool: `set_canary_traffic`

| Field | Value |
|---|---|
| **Interaction ID** | I-026 |
| **Description** | Sets the canary traffic split percentage for an agent, routing a fraction of requests to the canary version for safe testing. |
| **Shared Service** | `AgentService.setCanaryTraffic()` |
| **Side Effects** | Updates traffic routing configuration; emits `agent.canary.updated` event; records in audit log. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["agent_id", "canary_percent"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[A-Z][0-9]+-[a-z-]+$",
      "description": "Agent identifier"
    },
    "canary_percent": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "description": "Percentage of traffic to route to canary version (0 disables canary)"
    },
    "canary_version": {
      "type": "string",
      "pattern": "^v[0-9]+\\.[0-9]+\\.[0-9]+$",
      "description": "Version to use as canary (required if canary_percent > 0)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AgentVersion` --- Contains agent_id, stable_version, canary_version, canary_percent, and updated_at.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | Agent `{agent_id}` not found | agent_id does not exist |
| `VERSION_NOT_FOUND` | Version `{canary_version}` not found for agent `{agent_id}` | Invalid canary version |
| `CANARY_VERSION_REQUIRED` | `canary_version` is required when `canary_percent` > 0 | Missing canary version |

**Example Prompt:**
> "Set 10% canary traffic for agent B1-code-reviewer using version v2.1.0."

---

#### Tool: `get_agent_maturity`

| Field | Value |
|---|---|
| **Interaction ID** | I-027 |
| **Description** | Returns the maturity assessment for an agent, including promotion readiness score and criteria checklist. |
| **Shared Service** | `AgentService.getMaturity()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["agent_id"],
  "properties": {
    "agent_id": {
      "type": "string",
      "pattern": "^[A-Z][0-9]+-[a-z-]+$",
      "description": "Agent identifier"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AgentMaturity` --- Contains agent_id, current_maturity, promotion_readiness_score (0-100), criteria (array of {name, met, value, threshold}), total_invocations, success_rate, avg_latency_ms, and days_at_current_level.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | Agent `{agent_id}` not found | agent_id does not exist |

**Example Prompt:**
> "Is agent A2-architect ready to be promoted to GA?"

---

### 2.2 agentic-sdlc-governance

**Domain:** Cost management, audit logging, and approval gates
**Port:** 3101
**Tool count:** 10 (I-040 through I-049)

---

#### Tool: `get_cost_report`

| Field | Value |
|---|---|
| **Interaction ID** | I-040 |
| **Description** | Generates a cost report for a given scope (project, fleet, or agent) over a specified time period, broken down by agent, model, and stage. |
| **Shared Service** | `CostService.getReport()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["scope"],
  "properties": {
    "scope": {
      "type": "string",
      "enum": ["project", "fleet", "agent"],
      "description": "Report scope level"
    },
    "scope_id": {
      "type": "string",
      "description": "project_id or agent_id (required for project/agent scope, omit for fleet)"
    },
    "period": {
      "type": "object",
      "required": ["start", "end"],
      "properties": {
        "start": {
          "type": "string",
          "format": "date-time",
          "description": "Period start (ISO-8601)"
        },
        "end": {
          "type": "string",
          "format": "date-time",
          "description": "Period end (ISO-8601)"
        }
      }
    },
    "group_by": {
      "type": "string",
      "enum": ["agent", "model", "stage", "day", "project"],
      "default": "agent",
      "description": "How to break down the cost data"
    },
    "days": {
      "type": "integer",
      "minimum": 1,
      "maximum": 365,
      "default": 7,
      "description": "Shorthand for period: last N days (ignored if period is specified)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `CostReport` --- Contains scope, period, total_cost_usd, breakdown (array of {group_key, cost_usd, token_count, invocation_count}), daily_trend (array of {date, cost_usd}), and comparison_to_previous_period.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{scope_id}` not found | scope is project but scope_id is invalid |
| `AGENT_NOT_FOUND` | Agent `{scope_id}` not found | scope is agent but scope_id is invalid |
| `INVALID_DATE_RANGE` | Start date must be before end date | Malformed period |
| `SCOPE_ID_REQUIRED` | `scope_id` is required when scope is `{scope}` | Missing scope_id for project/agent scope |

**Example Prompt:**
> "Show me the cost report for the fleet over the last 30 days, grouped by agent."

---

#### Tool: `check_budget`

| Field | Value |
|---|---|
| **Interaction ID** | I-041 |
| **Description** | Returns the current budget status for a project or the fleet, including spend-to-date, remaining budget, and projected overage. |
| **Shared Service** | `CostService.checkBudget()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Project to check (omit for fleet-wide budget)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `BudgetStatus` --- Contains scope, budget_usd, spent_usd, remaining_usd, utilization_percent, projected_monthly_spend_usd, alert_threshold_percent, and is_over_budget (boolean).

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |
| `NO_BUDGET_SET` | No budget has been configured for `{scope}` | Budget not configured |

**Example Prompt:**
> "What is the remaining budget for project proj_abc123def456?"

---

#### Tool: `query_audit_events`

| Field | Value |
|---|---|
| **Interaction ID** | I-042 |
| **Description** | Queries the audit event log with rich filtering by actor, action type, resource, and time range. |
| **Shared Service** | `AuditService.query()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "actor": {
      "type": "string",
      "description": "Filter by actor ID (user or agent ID)"
    },
    "action": {
      "type": "string",
      "enum": [
        "pipeline.triggered", "pipeline.completed", "pipeline.failed", "pipeline.cancelled",
        "pipeline.resumed", "pipeline.stage.retried",
        "agent.invoked", "agent.promoted", "agent.rolledback", "agent.canary.updated",
        "gate.approved", "gate.rejected",
        "budget.threshold.updated", "budget.exceeded",
        "exception.created", "exception.promoted"
      ],
      "description": "Filter by action type"
    },
    "resource_type": {
      "type": "string",
      "enum": ["pipeline", "agent", "gate", "budget", "exception"],
      "description": "Filter by resource type"
    },
    "resource_id": {
      "type": "string",
      "description": "Filter by specific resource ID"
    },
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Filter by project"
    },
    "since": {
      "type": "string",
      "format": "date-time",
      "description": "Return events after this timestamp"
    },
    "until": {
      "type": "string",
      "format": "date-time",
      "description": "Return events before this timestamp"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 500,
      "default": 50,
      "description": "Maximum events to return"
    },
    "offset": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Pagination offset"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AuditEvent[]` --- Array of event objects containing event_id, timestamp, actor, action, resource_type, resource_id, project_id, details (object), and ip_address.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_DATE_RANGE` | `since` must be before `until` | Malformed date range |
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |

**Example Prompt:**
> "Show me all gate approval events for project proj_abc123def456 in the last 24 hours."

---

#### Tool: `get_audit_summary`

| Field | Value |
|---|---|
| **Interaction ID** | I-043 |
| **Description** | Returns an aggregated summary of audit events, including event counts by type, top actors, and trend data. |
| **Shared Service** | `AuditService.getSummary()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Scope to a specific project (omit for fleet-wide)"
    },
    "days": {
      "type": "integer",
      "minimum": 1,
      "maximum": 90,
      "default": 7,
      "description": "Number of days to summarize"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AuditSummary` --- Contains total_events, events_by_action (map), events_by_resource_type (map), top_actors (array), daily_trend (array), and notable_events (array of high-severity items).

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |

**Example Prompt:**
> "Give me an audit summary for the last 30 days."

---

#### Tool: `export_audit_report`

| Field | Value |
|---|---|
| **Interaction ID** | I-044 |
| **Description** | Exports a formatted audit report for compliance purposes, supporting CSV, JSON, and PDF output formats. |
| **Shared Service** | `AuditService.export()` |
| **Side Effects** | Creates a temporary export file; records export event in audit log. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["format"],
  "properties": {
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Scope to a specific project (omit for fleet-wide)"
    },
    "format": {
      "type": "string",
      "enum": ["csv", "json", "pdf"],
      "description": "Export file format"
    },
    "period": {
      "type": "object",
      "required": ["start", "end"],
      "properties": {
        "start": { "type": "string", "format": "date-time" },
        "end": { "type": "string", "format": "date-time" }
      }
    },
    "include_details": {
      "type": "boolean",
      "default": true,
      "description": "Include full event details in the export"
    }
  },
  "additionalProperties": false
}
```

**Output:** `AuditReport` --- Contains report_id, format, download_url, size_bytes, event_count, generated_at, and expires_at.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |
| `INVALID_DATE_RANGE` | Start date must be before end date | Malformed period |
| `EXPORT_TOO_LARGE` | Export would contain more than 100,000 events; narrow the filter | Too many events |

**Example Prompt:**
> "Export a PDF audit report for project proj_abc123def456 covering the last quarter."

---

#### Tool: `list_pending_approvals`

| Field | Value |
|---|---|
| **Interaction ID** | I-045 |
| **Description** | Lists all pending gate approval requests, optionally filtered by project or gate type. |
| **Shared Service** | `ApprovalService.listPending()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Filter by project"
    },
    "gate_type": {
      "type": "string",
      "enum": ["quality", "architecture", "security", "cost", "deployment"],
      "description": "Filter by gate type"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 20,
      "description": "Maximum approvals to return"
    }
  },
  "additionalProperties": false
}
```

**Output:** `ApprovalRequest[]` --- Array of pending approvals containing approval_id, run_id, project_id, gate_type, stage_index, requested_at, requested_by (agent_id), context (summary of what needs approval), and timeout_at.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |

**Example Prompt:**
> "Show me all pending approvals for quality gates."

---

#### Tool: `approve_gate`

| Field | Value |
|---|---|
| **Interaction ID** | I-046 |
| **Description** | Approves a pending gate, allowing the associated pipeline to proceed to the next stage. |
| **Shared Service** | `ApprovalService.approve()` |
| **Side Effects** | Updates approval status to `approved`; resumes the paused pipeline; records approval in audit log; emits `gate.approved` event. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["approval_id"],
  "properties": {
    "approval_id": {
      "type": "string",
      "pattern": "^appr_[a-z0-9]{16}$",
      "description": "Approval request identifier"
    },
    "comment": {
      "type": "string",
      "maxLength": 2000,
      "description": "Optional reviewer comment"
    },
    "conditions": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Conditions attached to the approval (e.g., 'fix naming conventions before deploy')"
    }
  },
  "additionalProperties": false
}
```

**Output:** `ApprovalResult` --- Contains approval_id, status (`approved`), approved_by, approved_at, comment, conditions, and run_id.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `APPROVAL_NOT_FOUND` | Approval `{approval_id}` not found | approval_id does not exist |
| `APPROVAL_ALREADY_RESOLVED` | Approval `{approval_id}` has already been {status} | Already approved or rejected |
| `APPROVAL_EXPIRED` | Approval `{approval_id}` has expired | Past timeout_at |
| `INSUFFICIENT_PERMISSIONS` | You do not have permission to approve `{gate_type}` gates | Missing role |

**Example Prompt:**
> "Approve gate appr_a1b2c3d4e5f6g7h8 with the comment: Architecture looks solid, proceed."

---

#### Tool: `reject_gate`

| Field | Value |
|---|---|
| **Interaction ID** | I-047 |
| **Description** | Rejects a pending gate, pausing the pipeline and requiring the stage to be revised or the pipeline to be cancelled. |
| **Shared Service** | `ApprovalService.reject()` |
| **Side Effects** | Updates approval status to `rejected`; keeps pipeline paused; records rejection in audit log; emits `gate.rejected` event; notifies the pipeline owner. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["approval_id", "reason"],
  "properties": {
    "approval_id": {
      "type": "string",
      "pattern": "^appr_[a-z0-9]{16}$",
      "description": "Approval request identifier"
    },
    "reason": {
      "type": "string",
      "minLength": 10,
      "maxLength": 2000,
      "description": "Reason for rejection (required, will be shared with the agent for revision)"
    },
    "suggested_changes": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Specific changes requested before re-approval"
    }
  },
  "additionalProperties": false
}
```

**Output:** `ApprovalResult` --- Contains approval_id, status (`rejected`), rejected_by, rejected_at, reason, and suggested_changes.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `APPROVAL_NOT_FOUND` | Approval `{approval_id}` not found | approval_id does not exist |
| `APPROVAL_ALREADY_RESOLVED` | Approval `{approval_id}` has already been {status} | Already approved or rejected |
| `APPROVAL_EXPIRED` | Approval `{approval_id}` has expired | Past timeout_at |
| `REASON_TOO_SHORT` | Rejection reason must be at least 10 characters | reason < 10 chars |

**Example Prompt:**
> "Reject gate appr_a1b2c3d4e5f6g7h8 because the security analysis is missing input validation for the API endpoints."

---

#### Tool: `get_cost_anomalies`

| Field | Value |
|---|---|
| **Interaction ID** | I-048 |
| **Description** | Detects and returns cost anomalies --- invocations or pipelines that cost significantly more than expected based on historical patterns. |
| **Shared Service** | `CostService.getAnomalies()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Filter by project (omit for fleet-wide)"
    },
    "severity": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"],
      "description": "Minimum severity threshold"
    },
    "days": {
      "type": "integer",
      "minimum": 1,
      "maximum": 30,
      "default": 7,
      "description": "Look-back window in days"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50,
      "default": 10,
      "description": "Maximum anomalies to return"
    }
  },
  "additionalProperties": false
}
```

**Output:** `CostAnomaly[]` --- Array of anomaly objects containing anomaly_id, detected_at, severity, resource_type, resource_id, expected_cost_usd, actual_cost_usd, deviation_percent, description, and suggested_action.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |
| `INSUFFICIENT_HISTORY` | Not enough historical data for anomaly detection (minimum 3 days required) | New project with no history |

**Example Prompt:**
> "Are there any high-severity cost anomalies across the fleet in the last 7 days?"

---

#### Tool: `update_budget_threshold`

| Field | Value |
|---|---|
| **Interaction ID** | I-049 |
| **Description** | Updates the budget alert threshold for a project or the fleet, controlling when cost warnings are triggered. |
| **Shared Service** | `CostService.updateThreshold()` |
| **Side Effects** | Updates budget configuration; records change in audit log; emits `budget.threshold.updated` event; may trigger immediate alert if new threshold is already exceeded. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["threshold_percent"],
  "properties": {
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Project to update (omit for fleet-wide threshold)"
    },
    "threshold_percent": {
      "type": "integer",
      "minimum": 50,
      "maximum": 100,
      "description": "Alert threshold as a percentage of budget (e.g., 80 means alert at 80% utilization)"
    },
    "budget_usd": {
      "type": "number",
      "minimum": 1.0,
      "maximum": 10000.0,
      "description": "Optionally update the total budget amount as well"
    },
    "notification_channels": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["email", "slack", "webhook"]
      },
      "description": "Channels to notify when threshold is breached"
    }
  },
  "additionalProperties": false
}
```

**Output:** `BudgetStatus` --- Updated budget status reflecting new threshold.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |
| `INSUFFICIENT_PERMISSIONS` | You do not have permission to modify budget thresholds | Missing admin role |

**Example Prompt:**
> "Set the budget alert threshold for project proj_abc123def456 to 80% and the total budget to $100."

---

### 2.3 agentic-sdlc-knowledge

**Domain:** Exception knowledge base --- capturing, searching, and promoting known patterns, workarounds, and best practices
**Port:** 3102
**Tool count:** 4 (I-060 through I-063)

---

#### Tool: `search_exceptions`

| Field | Value |
|---|---|
| **Interaction ID** | I-060 |
| **Description** | Searches the exception knowledge base using semantic and keyword search, returning matching patterns, workarounds, and best practices. |
| **Shared Service** | `KnowledgeService.search()` |
| **Side Effects** | Records the search query for analytics (what are agents asking about). |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["query"],
  "properties": {
    "query": {
      "type": "string",
      "minLength": 3,
      "maxLength": 1000,
      "description": "Natural-language search query describing the problem or pattern"
    },
    "category": {
      "type": "string",
      "enum": [
        "error-pattern", "workaround", "best-practice",
        "anti-pattern", "architectural-decision", "tool-usage"
      ],
      "description": "Filter by exception category"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Filter by tags (e.g., ['authentication', 'api-design'])"
    },
    "min_confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.7,
      "description": "Minimum semantic similarity score"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20,
      "default": 5,
      "description": "Maximum results to return"
    }
  },
  "additionalProperties": false
}
```

**Output:** `KnowledgeException[]` --- Array of matching exceptions containing exception_id, title, category, description, resolution, tags, confidence_score, created_at, promoted (boolean), and usage_count.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `QUERY_TOO_SHORT` | Search query must be at least 3 characters | query < 3 chars |
| `KNOWLEDGE_BASE_UNAVAILABLE` | Knowledge base is temporarily unavailable | Vector DB down |

**Example Prompt:**
> "Search for known workarounds related to rate limiting in API design."

---

#### Tool: `create_exception`

| Field | Value |
|---|---|
| **Interaction ID** | I-061 |
| **Description** | Creates a new exception entry in the knowledge base, documenting a pattern, workaround, or best practice discovered during pipeline execution. |
| **Shared Service** | `KnowledgeService.create()` |
| **Side Effects** | Creates a knowledge base record; generates embedding for semantic search; emits `exception.created` event; records in audit log. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["title", "category", "description", "resolution", "project_id"],
  "properties": {
    "title": {
      "type": "string",
      "minLength": 10,
      "maxLength": 200,
      "description": "Concise title for the exception"
    },
    "category": {
      "type": "string",
      "enum": [
        "error-pattern", "workaround", "best-practice",
        "anti-pattern", "architectural-decision", "tool-usage"
      ],
      "description": "Exception category"
    },
    "description": {
      "type": "string",
      "minLength": 20,
      "maxLength": 5000,
      "description": "Detailed description of the problem or pattern"
    },
    "resolution": {
      "type": "string",
      "minLength": 20,
      "maxLength": 5000,
      "description": "How to resolve or apply this knowledge"
    },
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Project where this exception was discovered"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string", "maxLength": 50 },
      "maxItems": 10,
      "description": "Searchable tags"
    },
    "related_agent_id": {
      "type": "string",
      "pattern": "^[A-Z][0-9]+-[a-z-]+$",
      "description": "Agent that discovered or is related to this exception"
    },
    "code_example": {
      "type": "string",
      "maxLength": 10000,
      "description": "Optional code example demonstrating the pattern or fix"
    }
  },
  "additionalProperties": false
}
```

**Output:** `KnowledgeException` --- The newly created exception with exception_id, created_at, and status (`draft`).

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |
| `DUPLICATE_EXCEPTION` | A similar exception already exists: `{existing_id}` | Semantic similarity > 0.95 with existing entry |
| `TITLE_TOO_SHORT` | Title must be at least 10 characters | title < 10 chars |

**Example Prompt:**
> "Create a new best-practice exception: Always use parameterized queries when building SQL in API handlers to prevent injection attacks."

---

#### Tool: `promote_exception`

| Field | Value |
|---|---|
| **Interaction ID** | I-062 |
| **Description** | Promotes a draft exception to `promoted` status, making it a verified, high-priority entry that agents actively reference during generation. |
| **Shared Service** | `KnowledgeService.promote()` |
| **Side Effects** | Updates exception status to `promoted`; boosts search ranking; records promotion in audit log; emits `exception.promoted` event. |

**Input Schema:**
```json
{
  "type": "object",
  "required": ["exception_id"],
  "properties": {
    "exception_id": {
      "type": "string",
      "pattern": "^exc_[a-z0-9]{16}$",
      "description": "Exception identifier to promote"
    },
    "justification": {
      "type": "string",
      "maxLength": 1000,
      "description": "Why this exception should be promoted"
    }
  },
  "additionalProperties": false
}
```

**Output:** `KnowledgeException` --- Updated exception with status `promoted` and promoted_at timestamp.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `EXCEPTION_NOT_FOUND` | Exception `{exception_id}` not found | exception_id does not exist |
| `EXCEPTION_ALREADY_PROMOTED` | Exception `{exception_id}` is already promoted | Already promoted |

**Example Prompt:**
> "Promote exception exc_a1b2c3d4e5f6g7h8 because it has been validated across 5 projects."

---

#### Tool: `list_exceptions`

| Field | Value |
|---|---|
| **Interaction ID** | I-063 |
| **Description** | Lists exception entries with filtering by category, status, and tags. |
| **Shared Service** | `KnowledgeService.list()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": [
        "error-pattern", "workaround", "best-practice",
        "anti-pattern", "architectural-decision", "tool-usage"
      ],
      "description": "Filter by category"
    },
    "status": {
      "type": "string",
      "enum": ["draft", "promoted", "deprecated"],
      "description": "Filter by status"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Filter by tags (AND logic)"
    },
    "project_id": {
      "type": "string",
      "pattern": "^proj_[a-z0-9]{12}$",
      "description": "Filter by originating project"
    },
    "sort_by": {
      "type": "string",
      "enum": ["created_at", "usage_count", "confidence_score"],
      "default": "created_at",
      "description": "Sort order"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 20,
      "description": "Maximum entries to return"
    },
    "offset": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Pagination offset"
    }
  },
  "additionalProperties": false
}
```

**Output:** `KnowledgeException[]` --- Array of exception entries, with total count for pagination.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_PROJECT` | Project `{project_id}` not found | project_id does not exist |

**Example Prompt:**
> "List all promoted best-practice exceptions tagged with 'security'."

---

### 2.4 System Tools

**Domain:** Cross-server observability and MCP introspection
**Hosted on:** `agentic-sdlc-agents` server (port 3100)
**Tool count:** 3 (I-080 through I-082)

---

#### Tool: `get_fleet_health`

| Field | Value |
|---|---|
| **Interaction ID** | I-080 |
| **Description** | Returns the overall fleet health dashboard, aggregating agent health, pipeline throughput, and system resource metrics. |
| **Shared Service** | `SystemService.getFleetHealth()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "include_agents": {
      "type": "boolean",
      "default": true,
      "description": "Include per-agent health breakdown"
    },
    "include_pipelines": {
      "type": "boolean",
      "default": true,
      "description": "Include pipeline throughput metrics"
    },
    "include_resources": {
      "type": "boolean",
      "default": false,
      "description": "Include system resource metrics (CPU, memory, disk)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `FleetHealth` --- Contains overall_status (healthy | degraded | unhealthy), agent_summary (total, healthy, degraded, unhealthy), pipeline_summary (active, queued, completed_today, failed_today), cost_summary (today_usd, month_to_date_usd), and optionally per-agent health and system resources.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `FLEET_DATA_STALE` | Fleet health data is stale (last updated {timestamp}) | Monitoring system lag |

**Example Prompt:**
> "Show me the fleet health dashboard."

---

#### Tool: `get_mcp_status`

| Field | Value |
|---|---|
| **Interaction ID** | I-081 |
| **Description** | Returns the status of all MCP servers, including connection state, tool counts, uptime, and version information. |
| **Shared Service** | `SystemService.getMcpStatus()` |
| **Side Effects** | Pings each MCP server to verify connectivity. |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "server_name": {
      "type": "string",
      "enum": ["agentic-sdlc-agents", "agentic-sdlc-governance", "agentic-sdlc-knowledge"],
      "description": "Check a specific server (omit for all servers)"
    }
  },
  "additionalProperties": false
}
```

**Output:** `McpServerStatus` or `McpServerStatus[]` --- Contains server_name, status (connected | disconnected | error), transport, url, tool_count, resource_count, prompt_count, uptime_seconds, version, and last_ping_at.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `SERVER_UNREACHABLE` | MCP server `{server_name}` is unreachable | Cannot connect to server |

**Example Prompt:**
> "What is the status of all MCP servers?"

---

#### Tool: `list_recent_mcp_calls`

| Field | Value |
|---|---|
| **Interaction ID** | I-082 |
| **Description** | Lists recent MCP tool invocations for debugging and observability, showing which tools were called, by whom, and how they performed. |
| **Shared Service** | `SystemService.listRecentCalls()` |
| **Side Effects** | None (read-only). |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "server_name": {
      "type": "string",
      "enum": ["agentic-sdlc-agents", "agentic-sdlc-governance", "agentic-sdlc-knowledge"],
      "description": "Filter by server"
    },
    "tool_name": {
      "type": "string",
      "description": "Filter by specific tool name"
    },
    "status": {
      "type": "string",
      "enum": ["success", "error"],
      "description": "Filter by call result"
    },
    "since": {
      "type": "string",
      "format": "date-time",
      "description": "Return calls after this timestamp"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 200,
      "default": 50,
      "description": "Maximum calls to return"
    }
  },
  "additionalProperties": false
}
```

**Output:** `McpCallEvent[]` --- Array of call events containing call_id, timestamp, server_name, tool_name, caller (agent or user), input_summary, status (success | error), latency_ms, error_code (if failed), and token_count.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `INVALID_DATE_RANGE` | `since` must be a valid ISO-8601 timestamp | Malformed date |

**Example Prompt:**
> "Show me the last 20 failed MCP calls across all servers."

---

#### Tool: `check_provider_health`

| Field | Value |
|---|---|
| **Interaction ID** | I-083 |
| **Description** | Checks health of LLM providers. Returns reachability, latency, model availability, and pricing for each configured provider (Anthropic, OpenAI, Ollama). |
| **Shared Service** | `HealthService.check_provider_health()` |
| **Side Effects** | None (read-only). Sends a minimal health-check prompt to each provider. |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "provider_name": {
      "type": "string",
      "enum": ["anthropic", "openai", "ollama"],
      "description": "Check a specific provider. If omitted, checks all configured providers."
    }
  },
  "additionalProperties": false
}
```

**Output:** `ProviderStatus[]` --- Array of provider status objects containing provider_name, healthy (bool), model_count, default_tier, latency_ms, tier_map, cost_per_1k_input, cost_per_1k_output, last_checked_at.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `PROVIDER_NOT_CONFIGURED` | Provider '{name}' is not configured | Provider not in LLM_PROVIDER or no API key set |
| `PROVIDER_UNREACHABLE` | Provider '{name}' is unreachable | Network or auth failure during health check |

**Example Prompt:**
> "Are all LLM providers healthy? Check their status."

---

#### Tool: `set_agent_provider`

| Field | Value |
|---|---|
| **Interaction ID** | I-084 |
| **Description** | Sets or clears a per-agent LLM provider override. When set, the agent uses this provider instead of the global LLM_PROVIDER. When cleared, the agent reverts to the global default. |
| **Shared Service** | `AgentService.set_provider()` |
| **Side Effects** | Updates agent manifest in registry. Next agent invocation uses new provider. |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "agent_id": {
      "type": "string",
      "description": "Agent identifier (e.g., 'G1-cost-tracker')"
    },
    "provider": {
      "type": "string",
      "enum": ["anthropic", "openai", "ollama", null],
      "description": "Provider name to set. Use null to clear override and revert to global default."
    }
  },
  "required": ["agent_id", "provider"],
  "additionalProperties": false
}
```

**Output:** `AgentDetail` --- Updated agent detail with new provider configuration reflected.

**Error Cases:**

| Code | Message | Condition |
|---|---|---|
| `AGENT_NOT_FOUND` | No agent with ID '{agent_id}' | Invalid agent ID |
| `PROVIDER_NOT_CONFIGURED` | Provider '{provider}' is not configured | Provider not available |
| `PROVIDER_UNHEALTHY` | Provider '{provider}' is currently unhealthy | Provider failed health check |

**Example Prompt:**
> "Switch G1-cost-tracker to use OpenAI instead of Anthropic."

---

## 3. MCP Resources

MCP Resources expose read-only data that AI clients can reference without invoking a tool. Resources use URI templates and return typed content.

### 3.1 agentic-sdlc-agents Resources

| Resource URI | Name | MIME Type | Description |
|---|---|---|---|
| `agent://{agent_id}/manifest` | Agent Manifest | `application/yaml` | The agent's `manifest.yaml` containing role, model, version, prompt reference, and configuration. |
| `agent://{agent_id}/prompt` | Agent Prompt | `text/markdown` | The agent's prompt template (Markdown). Used for inspection and debugging. |
| `agent://{agent_id}/metrics` | Agent Metrics | `application/json` | Real-time performance metrics: success rate, avg latency, cost per invocation, invocation count. |
| `pipeline://{run_id}/output` | Pipeline Output | `application/json` | All deliverables from a completed pipeline run, including generated documents and metadata. |

### 3.2 agentic-sdlc-governance Resources

| Resource URI | Name | MIME Type | Description |
|---|---|---|---|
| `cost://fleet/today` | Fleet Daily Spend | `application/json` | Today's fleet-wide cost summary: total spend, per-agent breakdown, top projects. |
| `cost://{project_id}/summary` | Project Cost Summary | `application/json` | Running cost summary for a specific project including budget utilization. |
| `audit://recent` | Recent Audit Events | `application/json` | Last 100 audit events across the fleet (auto-updating). |

### 3.3 agentic-sdlc-knowledge Resources

| Resource URI | Name | MIME Type | Description |
|---|---|---|---|
| `knowledge://promoted` | Promoted Exceptions | `application/json` | All promoted knowledge exceptions, ordered by usage count descending. |
| `knowledge://stats` | Knowledge Base Stats | `application/json` | Statistics: total entries, entries by category, top tags, promotion rate. |

### 3.4 System Resources

| Resource URI | Name | MIME Type | Description |
|---|---|---|---|
| `system://health` | Fleet Health | `application/json` | Aggregated fleet health dashboard (mirrors `get_fleet_health` output). |
| `provider://list` | LLM Provider List | `application/json` | List of all configured LLM providers with health status, supported tiers, model mappings, and pricing. Mirrors `check_provider_health` output for all providers. |

**Total resources: 11**

### Resource Access Example

```typescript
// Reading a resource from Claude Code
const manifest = await mcpClient.readResource("agent://B1-code-reviewer/manifest");
// Returns: { uri: "agent://B1-code-reviewer/manifest", mimeType: "application/yaml", text: "..." }
```

---

## 4. MCP Prompt Templates

Prompt templates provide pre-built, parameterized prompts for common workflows. AI clients can list and use these templates to guide interactions.

### 4.1 `generate-docs`

| Field | Value |
|---|---|
| **Server** | `agentic-sdlc-agents` |
| **Description** | Generate a complete 24-document set for a new software project. |

**Arguments:**
```json
{
  "brief": {
    "type": "string",
    "required": true,
    "description": "A natural-language project brief describing the system to build"
  },
  "template": {
    "type": "string",
    "required": false,
    "description": "Pipeline template (default: full-stack-first)"
  }
}
```

**Generated Prompt:**
```
Generate a complete 24-document set for the following project:

{brief}

Use the {template} pipeline template. Start by validating the brief with validate_pipeline_input, then trigger the pipeline with trigger_pipeline. Monitor progress with get_pipeline_status and retrieve documents with get_pipeline_documents as each stage completes.
```

### 4.2 `review-code`

| Field | Value |
|---|---|
| **Server** | `agentic-sdlc-agents` |
| **Description** | Review a code file or module using the B1-code-reviewer agent. |

**Arguments:**
```json
{
  "file_path": {
    "type": "string",
    "required": true,
    "description": "Path to the file or module to review"
  },
  "focus_areas": {
    "type": "string",
    "required": false,
    "description": "Comma-separated areas to focus on (e.g., security, performance, readability)"
  }
}
```

**Generated Prompt:**
```
Review the following code file using the B1-code-reviewer agent:

File: {file_path}
Focus areas: {focus_areas}

Use invoke_agent to call B1-code-reviewer with the file content. Check search_exceptions for any known patterns relevant to this code before starting the review.
```

### 4.3 `check-compliance`

| Field | Value |
|---|---|
| **Server** | `agentic-sdlc-governance` |
| **Description** | Run a compliance audit on a project, checking gate approvals, cost adherence, and audit trail completeness. |

**Arguments:**
```json
{
  "project_id": {
    "type": "string",
    "required": true,
    "description": "Project identifier to audit"
  }
}
```

**Generated Prompt:**
```
Run a compliance audit on project {project_id}:

1. Use get_audit_summary to get an overview of all events for this project.
2. Use list_pending_approvals to check for any unresolved gates.
3. Use check_budget to verify cost adherence.
4. Use get_cost_anomalies to identify any unusual spending.
5. Generate a compliance report summarizing findings and any action items.
```

### 4.4 `cost-report`

| Field | Value |
|---|---|
| **Server** | `agentic-sdlc-governance` |
| **Description** | Generate a detailed cost report for a scope over a time period. |

**Arguments:**
```json
{
  "scope": {
    "type": "string",
    "required": true,
    "description": "Report scope: project, fleet, or agent"
  },
  "days": {
    "type": "integer",
    "required": false,
    "description": "Number of days to cover (default: 7)"
  }
}
```

**Generated Prompt:**
```
Show me the cost report for {scope} over the last {days} days:

1. Use get_cost_report with scope={scope} and days={days}, grouped by agent.
2. Use check_budget to show remaining budget and projected spend.
3. Use get_cost_anomalies to highlight any unusual patterns.
4. Summarize the top cost drivers and provide recommendations for optimization.
```

### 4.5 `fleet-status`

| Field | Value |
|---|---|
| **Server** | `agentic-sdlc-agents` |
| **Description** | Get a comprehensive status overview of the entire agent fleet and MCP infrastructure. |

**Arguments:**
```json
{
  "verbose": {
    "type": "boolean",
    "required": false,
    "description": "Include detailed per-agent metrics (default: false)"
  }
}
```

**Generated Prompt:**
```
Give me a comprehensive fleet status overview:

1. Use get_fleet_health to get the overall health dashboard.
2. Use get_mcp_status to verify all MCP servers are online.
3. Use list_agents to enumerate all agents and their maturity levels.
4. Use check_budget to show fleet-wide budget status.
{verbose ? "5. Use check_agent_health for each agent to get detailed health metrics." : ""}
Provide a summary highlighting any issues that need attention.
```

### 4.6 `knowledge-review`

| Field | Value |
|---|---|
| **Server** | `agentic-sdlc-knowledge` |
| **Description** | Review and curate the exception knowledge base, identifying entries ready for promotion. |

**Arguments:**
```json
{
  "category": {
    "type": "string",
    "required": false,
    "description": "Focus on a specific category (e.g., best-practice, error-pattern)"
  }
}
```

**Generated Prompt:**
```
Review the exception knowledge base{category ? " focusing on " + category + " entries" : ""}:

1. Use list_exceptions with status=draft to find unpromoted entries.
2. For high-usage entries, use search_exceptions to check for duplicates.
3. Recommend entries that should be promoted based on usage count and relevance.
4. Identify any duplicate or contradictory entries that should be cleaned up.
```

**Total prompt templates: 6**

---

## 5. Authentication & Authorization

### 5.1 API Key Authentication

All MCP servers authenticate using the `AGENTIC_SDLC_API_KEY` environment variable. LLM provider credentials are configured separately: `ANTHROPIC_API_KEY` for Anthropic, `OPENAI_API_KEY` for OpenAI, and `OLLAMA_HOST` for Ollama (defaults to `http://localhost:11434`). The active provider is selected via `LLM_PROVIDER` env var.

| Transport | Auth Mechanism | Header/Config |
|---|---|---|
| `stdio` | Environment variable | `env: { "AGENTIC_SDLC_API_KEY": "..." }` |
| `streamable-http` | Bearer token | `Authorization: Bearer <api_key>` |

### 5.2 Permission Levels

Tools are classified into permission tiers:

| Level | Description | Tools |
|---|---|---|
| **read** | Read-only operations, no state changes | `get_pipeline_status`, `list_pipeline_runs`, `get_pipeline_documents`, `get_pipeline_config`, `validate_pipeline_input`, `list_agents`, `get_agent`, `check_agent_health`, `get_agent_maturity`, `get_cost_report`, `check_budget`, `query_audit_events`, `get_audit_summary`, `list_pending_approvals`, `get_cost_anomalies`, `search_exceptions`, `list_exceptions`, `get_fleet_health`, `get_mcp_status`, `list_recent_mcp_calls`, `check_provider_health` |
| **write** | Creates or modifies state | `trigger_pipeline`, `resume_pipeline`, `cancel_pipeline`, `retry_pipeline_step`, `invoke_agent`, `set_canary_traffic`, `create_exception`, `promote_exception`, `export_audit_report`, `set_agent_provider` |
| **admin** | Elevated operations affecting fleet-wide configuration | `promote_agent_version`, `rollback_agent_version`, `approve_gate`, `reject_gate`, `update_budget_threshold` |

### 5.3 Project Scoping

All **write** and **admin** operations that affect project data require a `project_id` parameter (either directly or derived from the `run_id`). The server validates that the API key has access to the specified project.

### 5.4 Key Rotation

API keys can be rotated without downtime:

1. Generate a new key via the admin dashboard.
2. Update the `AGENTIC_SDLC_API_KEY` environment variable (and provider-specific keys as needed: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`).
3. Restart MCP server processes (stdio) or wait for the next health check cycle (streamable-http).
4. Revoke the old key after confirming the new key works.

---

## 6. Error Handling

### 6.1 Standard Error Format

All MCP tool errors follow this structure:

```json
{
  "error": true,
  "code": "ERROR_CODE",
  "message": "Human-readable error description",
  "details": {
    "additional": "context-specific data"
  }
}
```

### 6.2 Error Code Registry

| Code | HTTP Equiv | Description | Returned By |
|---|---|---|---|
| `PIPELINE_NOT_FOUND` | 404 | Pipeline run ID does not exist | `get_pipeline_status`, `resume_pipeline`, `cancel_pipeline`, `get_pipeline_documents`, `retry_pipeline_step` |
| `PIPELINE_NOT_PAUSED` | 409 | Pipeline is not in a paused state | `resume_pipeline` |
| `PIPELINE_ALREADY_RUNNING` | 409 | Project already has an active pipeline | `trigger_pipeline` |
| `PIPELINE_ALREADY_TERMINAL` | 409 | Pipeline is in a terminal state (completed/failed/cancelled) | `cancel_pipeline` |
| `INVALID_PROJECT` | 404 | Project ID does not exist | Multiple tools |
| `INVALID_TEMPLATE` | 400 | Unrecognized pipeline template | `trigger_pipeline`, `get_pipeline_config`, `validate_pipeline_input` |
| `BUDGET_EXCEEDED` | 402 | Operation would exceed budget ceiling | `trigger_pipeline`, `retry_pipeline_step`, `invoke_agent` |
| `AGENT_NOT_FOUND` | 404 | Agent ID does not exist | Multiple agent tools |
| `AGENT_UNHEALTHY` | 503 | Agent is currently unhealthy | `invoke_agent` |
| `AGENT_VERSION_DEPRECATED` | 410 | Agent version is deprecated | `invoke_agent` |
| `INVOCATION_TIMEOUT` | 504 | Agent invocation exceeded timeout | `invoke_agent` |
| `APPROVAL_NOT_FOUND` | 404 | Approval ID does not exist | `approve_gate`, `reject_gate` |
| `APPROVAL_ALREADY_RESOLVED` | 409 | Approval already approved or rejected | `approve_gate`, `reject_gate` |
| `APPROVAL_EXPIRED` | 410 | Approval past its timeout | `approve_gate`, `reject_gate` |
| `APPROVAL_PENDING` | 409 | Gate approval must be resolved before resuming | `resume_pipeline` |
| `INSUFFICIENT_PERMISSIONS` | 403 | Caller lacks required permission level | `approve_gate`, `reject_gate`, `update_budget_threshold` |
| `INVALID_PROMOTION_PATH` | 400 | Invalid maturity transition | `promote_agent_version` |
| `PROMOTION_CRITERIA_NOT_MET` | 422 | Agent does not meet promotion criteria | `promote_agent_version` |
| `NO_PREVIOUS_VERSION` | 404 | No previous version to roll back to | `rollback_agent_version` |
| `VERSION_NOT_FOUND` | 404 | Specified version does not exist | `rollback_agent_version`, `set_canary_traffic` |
| `CANARY_VERSION_REQUIRED` | 400 | canary_version required when percent > 0 | `set_canary_traffic` |
| `EXCEPTION_NOT_FOUND` | 404 | Exception ID does not exist | `promote_exception` |
| `EXCEPTION_ALREADY_PROMOTED` | 409 | Exception already promoted | `promote_exception` |
| `DUPLICATE_EXCEPTION` | 409 | Semantically similar exception exists | `create_exception` |
| `KNOWLEDGE_BASE_UNAVAILABLE` | 503 | Vector database unreachable | `search_exceptions` |
| `EXPORT_TOO_LARGE` | 413 | Export exceeds maximum event count | `export_audit_report` |
| `INVALID_DATE_RANGE` | 400 | Malformed or inverted date range | Multiple tools |
| `NO_BUDGET_SET` | 404 | No budget configured for scope | `check_budget` |
| `INSUFFICIENT_HISTORY` | 422 | Not enough data for anomaly detection | `get_cost_anomalies` |
| `MAX_RETRIES_EXCEEDED` | 429 | Stage retry limit reached | `retry_pipeline_step` |
| `STAGE_NOT_FAILED` | 409 | Stage is not in failed state | `retry_pipeline_step` |
| `NO_DOCUMENTS_YET` | 404 | Pipeline has not produced documents | `get_pipeline_documents` |
| `SERVER_UNREACHABLE` | 503 | MCP server cannot be reached | `get_mcp_status` |
| `FLEET_DATA_STALE` | 503 | Fleet health data is outdated | `get_fleet_health` |
| `BRIEF_TOO_SHORT` | 400 | Pipeline brief is too short | `trigger_pipeline` |
| `QUERY_TOO_SHORT` | 400 | Search query is too short | `search_exceptions` |
| `TITLE_TOO_SHORT` | 400 | Exception title is too short | `create_exception` |
| `REASON_TOO_SHORT` | 400 | Rejection reason is too short | `reject_gate` |
| `INVALID_ROLE` | 400 | Unrecognized agent role | `list_agents` |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | All tools |
| `INTERNAL_ERROR` | 500 | Unexpected server error | All tools |

**Total error codes: 38**

### 6.3 Error Handling Best Practices

1. **Always check for `error: true`** in tool responses before processing output.
2. **Retry on transient errors** (`AGENT_UNHEALTHY`, `KNOWLEDGE_BASE_UNAVAILABLE`, `SERVER_UNREACHABLE`, `FLEET_DATA_STALE`) with exponential backoff.
3. **Do not retry** on validation errors (`INVALID_PROJECT`, `BUDGET_EXCEEDED`, `INSUFFICIENT_PERMISSIONS`).
4. **Log all errors** with the full error object for debugging.

---

## 7. Rate Limiting

### 7.1 Per-Server Limits

| Server | Requests/Minute | Requests/Hour | Burst (max concurrent) |
|---|---|---|---|
| `agentic-sdlc-agents` | 120 | 3,000 | 20 |
| `agentic-sdlc-governance` | 60 | 1,500 | 10 |
| `agentic-sdlc-knowledge` | 60 | 1,500 | 10 |

### 7.2 Per-Tool Limits

High-cost tools have individual rate limits:

| Tool | Requests/Minute | Requests/Hour | Notes |
|---|---|---|---|
| `trigger_pipeline` | 5 | 30 | Pipeline creation is expensive |
| `invoke_agent` | 20 | 200 | Direct agent invocations are costly |
| `retry_pipeline_step` | 10 | 60 | Retries incur additional cost |
| `export_audit_report` | 2 | 10 | Report generation is resource-intensive |
| `promote_agent_version` | 5 | 20 | Administrative action |
| `rollback_agent_version` | 5 | 20 | Administrative action |
| All read-only tools | 60 | 1,500 | Standard read limit |

### 7.3 Rate Limit Response

When rate limited, tools return:

```json
{
  "error": true,
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded for tool trigger_pipeline: 5 requests/minute",
  "details": {
    "tool": "trigger_pipeline",
    "limit": 5,
    "window": "1m",
    "retry_after_seconds": 12
  }
}
```

### 7.4 Rate Limit Headers (streamable-http only)

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Maximum requests per window |
| `X-RateLimit-Remaining` | Remaining requests in current window |
| `X-RateLimit-Reset` | Unix timestamp when the window resets |
| `Retry-After` | Seconds to wait before retrying (only on 429) |

---

## 8. REST API Derivation Table

Every MCP tool is wrapped by a REST endpoint for non-MCP clients. The REST gateway runs on port 3000 and routes to the appropriate MCP server.

| MCP Tool | REST Endpoint | Method | Server | Notes |
|---|---|---|---|---|
| `trigger_pipeline` | `/api/v1/pipelines` | `POST` | agents | Request body = tool input |
| `get_pipeline_status` | `/api/v1/pipelines/{run_id}` | `GET` | agents | `include_stage_details` via query param |
| `list_pipeline_runs` | `/api/v1/pipelines` | `GET` | agents | Filters via query params |
| `resume_pipeline` | `/api/v1/pipelines/{run_id}/resume` | `POST` | agents | |
| `cancel_pipeline` | `/api/v1/pipelines/{run_id}/cancel` | `POST` | agents | |
| `get_pipeline_documents` | `/api/v1/pipelines/{run_id}/documents` | `GET` | agents | `doc_type`, `stage_index` via query params |
| `retry_pipeline_step` | `/api/v1/pipelines/{run_id}/stages/{stage_index}/retry` | `POST` | agents | |
| `get_pipeline_config` | `/api/v1/pipelines/config/{template}` | `GET` | agents | |
| `validate_pipeline_input` | `/api/v1/pipelines/validate` | `POST` | agents | Dry-run validation |
| `list_agents` | `/api/v1/agents` | `GET` | agents | Filters via query params |
| `get_agent` | `/api/v1/agents/{agent_id}` | `GET` | agents | `include_metrics`, `include_version_history` via query params |
| `invoke_agent` | `/api/v1/agents/{agent_id}/invoke` | `POST` | agents | Request body = input + options |
| `check_agent_health` | `/api/v1/agents/{agent_id}/health` | `GET` | agents | Omit `{agent_id}` for all: `/api/v1/agents/health` |
| `promote_agent_version` | `/api/v1/agents/{agent_id}/promote` | `POST` | agents | |
| `rollback_agent_version` | `/api/v1/agents/{agent_id}/rollback` | `POST` | agents | |
| `set_canary_traffic` | `/api/v1/agents/{agent_id}/canary` | `PUT` | agents | |
| `get_agent_maturity` | `/api/v1/agents/{agent_id}/maturity` | `GET` | agents | |
| `get_cost_report` | `/api/v1/costs/report` | `GET` | governance | Params via query string |
| `check_budget` | `/api/v1/costs/budget` | `GET` | governance | `project_id` via query param |
| `get_cost_anomalies` | `/api/v1/costs/anomalies` | `GET` | governance | Filters via query params |
| `update_budget_threshold` | `/api/v1/costs/budget/threshold` | `PUT` | governance | |
| `query_audit_events` | `/api/v1/audit/events` | `GET` | governance | Filters via query params |
| `get_audit_summary` | `/api/v1/audit/summary` | `GET` | governance | |
| `export_audit_report` | `/api/v1/audit/export` | `POST` | governance | Returns download URL |
| `list_pending_approvals` | `/api/v1/approvals` | `GET` | governance | Filters via query params |
| `approve_gate` | `/api/v1/approvals/{approval_id}/approve` | `POST` | governance | |
| `reject_gate` | `/api/v1/approvals/{approval_id}/reject` | `POST` | governance | |
| `search_exceptions` | `/api/v1/knowledge/search` | `POST` | knowledge | POST for complex query body |
| `create_exception` | `/api/v1/knowledge/exceptions` | `POST` | knowledge | |
| `promote_exception` | `/api/v1/knowledge/exceptions/{exception_id}/promote` | `POST` | knowledge | |
| `list_exceptions` | `/api/v1/knowledge/exceptions` | `GET` | knowledge | Filters via query params |
| `get_fleet_health` | `/api/v1/system/health` | `GET` | agents | |
| `get_mcp_status` | `/api/v1/system/mcp` | `GET` | agents | |
| `list_recent_mcp_calls` | `/api/v1/system/mcp/calls` | `GET` | agents | Filters via query params |
| `check_provider_health` | `/api/v1/system/providers` | `GET` | agents | Optional `provider_name` query param |
| `set_agent_provider` | `/api/v1/agents/{agent_id}/provider` | `PUT` | agents | |

### REST Gateway Configuration

```yaml
# gateway-config.yaml
gateway:
  port: 3000
  cors:
    origins: ["http://localhost:5173", "https://app.agentic-sdlc.example.com"]
    methods: ["GET", "POST", "PUT", "DELETE"]
  auth:
    type: bearer
    header: Authorization
  routes:
    - prefix: /api/v1/pipelines
      upstream: http://localhost:3100
    - prefix: /api/v1/agents
      upstream: http://localhost:3100
    - prefix: /api/v1/system
      upstream: http://localhost:3100
    - prefix: /api/v1/costs
      upstream: http://localhost:3101
    - prefix: /api/v1/audit
      upstream: http://localhost:3101
    - prefix: /api/v1/approvals
      upstream: http://localhost:3101
    - prefix: /api/v1/knowledge
      upstream: http://localhost:3102
```

---

## 9. Testing MCP Tools

### 9.1 MCP Inspector (Interactive Testing)

Use the MCP Inspector CLI to test individual tools during development:

```bash
# Start the MCP Inspector connected to the agents server
npx @modelcontextprotocol/inspector node ./dist/mcp-servers/agents/index.js

# Test trigger_pipeline
# In the Inspector UI:
# 1. Select tool: trigger_pipeline
# 2. Provide input:
#    { "project_id": "proj_test12345678", "brief": "Build a task management app with real-time collaboration" }
# 3. Click "Run" and inspect the PipelineRun response
```

```bash
# Test governance server
npx @modelcontextprotocol/inspector node ./dist/mcp-servers/governance/index.js

# Test knowledge server
npx @modelcontextprotocol/inspector node ./dist/mcp-servers/knowledge/index.js
```

### 9.2 Automated Test Patterns (pytest)

```python
# tests/test_mcp_tools.py
import pytest
import json
from mcp_client import MCPClient

@pytest.fixture
def agents_client():
    """Connect to the agents MCP server."""
    client = MCPClient(transport="stdio", command=["node", "./dist/mcp-servers/agents/index.js"])
    client.connect()
    yield client
    client.disconnect()

@pytest.fixture
def governance_client():
    """Connect to the governance MCP server."""
    client = MCPClient(transport="stdio", command=["node", "./dist/mcp-servers/governance/index.js"])
    client.connect()
    yield client
    client.disconnect()

@pytest.fixture
def knowledge_client():
    """Connect to the knowledge MCP server."""
    client = MCPClient(transport="stdio", command=["node", "./dist/mcp-servers/knowledge/index.js"])
    client.connect()
    yield client
    client.disconnect()


class TestPipelineTools:
    """Tests for pipeline-related MCP tools (I-001 through I-009)."""

    def test_validate_pipeline_input_valid(self, agents_client):
        """I-009: Valid brief returns is_valid=true."""
        result = agents_client.call_tool("validate_pipeline_input", {
            "brief": "Build a multi-tenant SaaS billing dashboard with Stripe integration and real-time analytics",
            "template": "full-stack-first"
        })
        data = json.loads(result.content[0].text)
        assert data["is_valid"] is True
        assert data["estimated_cost_usd"] > 0
        assert "errors" not in data or len(data["errors"]) == 0

    def test_validate_pipeline_input_too_short(self, agents_client):
        """I-009: Brief too short returns validation error."""
        result = agents_client.call_tool("validate_pipeline_input", {
            "brief": "Build an app"
        })
        data = json.loads(result.content[0].text)
        assert data["is_valid"] is False

    def test_trigger_pipeline_success(self, agents_client):
        """I-001: Triggering a pipeline returns a run_id."""
        result = agents_client.call_tool("trigger_pipeline", {
            "project_id": "proj_test12345678",
            "brief": "Build a real-time collaborative task management application",
            "template": "full-stack-first",
            "options": {"cost_ceiling_usd": 25.0}
        })
        data = json.loads(result.content[0].text)
        assert "run_id" in data
        assert data["status"] == "queued"
        assert data["run_id"].startswith("run_")

    def test_trigger_pipeline_invalid_project(self, agents_client):
        """I-001: Invalid project returns INVALID_PROJECT error."""
        result = agents_client.call_tool("trigger_pipeline", {
            "project_id": "proj_nonexistent0",
            "brief": "Build something for a project that does not exist in the system"
        })
        data = json.loads(result.content[0].text)
        assert data["error"] is True
        assert data["code"] == "INVALID_PROJECT"

    def test_get_pipeline_status(self, agents_client):
        """I-002: Returns status for an existing run."""
        # First trigger a pipeline
        trigger_result = agents_client.call_tool("trigger_pipeline", {
            "project_id": "proj_test12345678",
            "brief": "Build a task management app with real-time collaboration features"
        })
        run_id = json.loads(trigger_result.content[0].text)["run_id"]

        # Then check its status
        result = agents_client.call_tool("get_pipeline_status", {
            "run_id": run_id,
            "include_stage_details": True
        })
        data = json.loads(result.content[0].text)
        assert data["run_id"] == run_id
        assert data["status"] in ["queued", "running"]

    def test_list_pipeline_runs(self, agents_client):
        """I-003: Returns list of runs with pagination."""
        result = agents_client.call_tool("list_pipeline_runs", {
            "limit": 5,
            "status": "running"
        })
        data = json.loads(result.content[0].text)
        assert isinstance(data["runs"], list)
        assert "total" in data

    def test_cancel_pipeline(self, agents_client):
        """I-005: Cancellation sets status to cancelled."""
        trigger_result = agents_client.call_tool("trigger_pipeline", {
            "project_id": "proj_test12345678",
            "brief": "Build an application that will be cancelled for testing purposes"
        })
        run_id = json.loads(trigger_result.content[0].text)["run_id"]

        result = agents_client.call_tool("cancel_pipeline", {
            "run_id": run_id,
            "reason": "Testing cancellation flow"
        })
        data = json.loads(result.content[0].text)
        assert data["status"] == "cancelled"

    def test_get_pipeline_config(self, agents_client):
        """I-008: Returns config for a valid template."""
        result = agents_client.call_tool("get_pipeline_config", {
            "template": "full-stack-first"
        })
        data = json.loads(result.content[0].text)
        assert data["template"] == "full-stack-first"
        assert len(data["stages"]) > 0


class TestAgentTools:
    """Tests for agent-related MCP tools (I-020 through I-027)."""

    def test_list_agents(self, agents_client):
        """I-020: Returns list of agents."""
        result = agents_client.call_tool("list_agents", {
            "maturity": "ga",
            "limit": 10
        })
        data = json.loads(result.content[0].text)
        assert isinstance(data["agents"], list)

    def test_get_agent(self, agents_client):
        """I-021: Returns agent details."""
        result = agents_client.call_tool("get_agent", {
            "agent_id": "B1-code-reviewer",
            "include_metrics": True
        })
        data = json.loads(result.content[0].text)
        assert data["agent_id"] == "B1-code-reviewer"
        assert "performance_metrics" in data

    def test_get_agent_not_found(self, agents_client):
        """I-021: Non-existent agent returns AGENT_NOT_FOUND."""
        result = agents_client.call_tool("get_agent", {
            "agent_id": "Z9-nonexistent"
        })
        data = json.loads(result.content[0].text)
        assert data["error"] is True
        assert data["code"] == "AGENT_NOT_FOUND"

    def test_check_agent_health(self, agents_client):
        """I-023: Health check returns valid status."""
        result = agents_client.call_tool("check_agent_health", {
            "agent_id": "B1-code-reviewer"
        })
        data = json.loads(result.content[0].text)
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "latency_ms" in data

    def test_get_agent_maturity(self, agents_client):
        """I-027: Returns maturity assessment."""
        result = agents_client.call_tool("get_agent_maturity", {
            "agent_id": "B1-code-reviewer"
        })
        data = json.loads(result.content[0].text)
        assert "current_maturity" in data
        assert "promotion_readiness_score" in data
        assert 0 <= data["promotion_readiness_score"] <= 100


class TestGovernanceTools:
    """Tests for governance MCP tools (I-040 through I-049)."""

    def test_get_cost_report(self, governance_client):
        """I-040: Fleet cost report returns valid data."""
        result = governance_client.call_tool("get_cost_report", {
            "scope": "fleet",
            "days": 7,
            "group_by": "agent"
        })
        data = json.loads(result.content[0].text)
        assert "total_cost_usd" in data
        assert isinstance(data["breakdown"], list)

    def test_check_budget(self, governance_client):
        """I-041: Budget check returns utilization."""
        result = governance_client.call_tool("check_budget", {
            "project_id": "proj_test12345678"
        })
        data = json.loads(result.content[0].text)
        assert "spent_usd" in data
        assert "remaining_usd" in data
        assert isinstance(data["is_over_budget"], bool)

    def test_query_audit_events(self, governance_client):
        """I-042: Returns audit events."""
        result = governance_client.call_tool("query_audit_events", {
            "limit": 10
        })
        data = json.loads(result.content[0].text)
        assert isinstance(data["events"], list)

    def test_get_audit_summary(self, governance_client):
        """I-043: Returns aggregated summary."""
        result = governance_client.call_tool("get_audit_summary", {
            "days": 7
        })
        data = json.loads(result.content[0].text)
        assert "total_events" in data
        assert "events_by_action" in data

    def test_list_pending_approvals(self, governance_client):
        """I-045: Returns pending approvals list."""
        result = governance_client.call_tool("list_pending_approvals", {
            "limit": 10
        })
        data = json.loads(result.content[0].text)
        assert isinstance(data["approvals"], list)


class TestKnowledgeTools:
    """Tests for knowledge MCP tools (I-060 through I-063)."""

    def test_search_exceptions(self, knowledge_client):
        """I-060: Semantic search returns results."""
        result = knowledge_client.call_tool("search_exceptions", {
            "query": "SQL injection prevention in API handlers",
            "min_confidence": 0.5,
            "limit": 5
        })
        data = json.loads(result.content[0].text)
        assert isinstance(data["results"], list)

    def test_create_and_list_exception(self, knowledge_client):
        """I-061 + I-063: Create then list."""
        # Create
        create_result = knowledge_client.call_tool("create_exception", {
            "title": "Always validate JWT expiration in middleware",
            "category": "best-practice",
            "description": "JWT tokens should be validated for expiration in middleware rather than in individual route handlers to ensure consistent security.",
            "resolution": "Add a global middleware that checks token expiration before any route handler executes. Return 401 if the token is expired.",
            "project_id": "proj_test12345678",
            "tags": ["security", "authentication", "jwt"]
        })
        create_data = json.loads(create_result.content[0].text)
        assert "exception_id" in create_data

        # List
        list_result = knowledge_client.call_tool("list_exceptions", {
            "category": "best-practice",
            "tags": ["security"],
            "limit": 10
        })
        list_data = json.loads(list_result.content[0].text)
        assert isinstance(list_data["exceptions"], list)


class TestSystemTools:
    """Tests for system MCP tools (I-080 through I-082)."""

    def test_get_fleet_health(self, agents_client):
        """I-080: Fleet health returns valid structure."""
        result = agents_client.call_tool("get_fleet_health", {
            "include_agents": True,
            "include_pipelines": True
        })
        data = json.loads(result.content[0].text)
        assert data["overall_status"] in ["healthy", "degraded", "unhealthy"]
        assert "agent_summary" in data
        assert "pipeline_summary" in data

    def test_get_mcp_status(self, agents_client):
        """I-081: MCP status returns server info."""
        result = agents_client.call_tool("get_mcp_status", {})
        data = json.loads(result.content[0].text)
        assert isinstance(data["servers"], list)
        assert len(data["servers"]) == 3

    def test_list_recent_mcp_calls(self, agents_client):
        """I-082: Returns recent MCP call log."""
        result = agents_client.call_tool("list_recent_mcp_calls", {
            "limit": 10
        })
        data = json.loads(result.content[0].text)
        assert isinstance(data["calls"], list)
```

### 9.3 Integration Test with Claude Code

Test the full loop from natural-language prompt to MCP tool invocation:

```bash
# 1. Start all MCP servers in development mode
npm run dev:mcp-servers

# 2. Configure Claude Code to use local MCP servers
# (ensure .claude/mcp_config.json points to local stdio servers)

# 3. Test natural-language tool invocation
claude "Show me the fleet health dashboard"
# Expected: Claude calls get_fleet_health and formats the result

claude "Trigger a full-stack-first pipeline for project proj_demo12345678 with brief: Build a todo app with user authentication"
# Expected: Claude calls validate_pipeline_input, then trigger_pipeline

claude "What is the cost breakdown for the fleet over the last 30 days?"
# Expected: Claude calls get_cost_report with scope=fleet, days=30, group_by=agent

claude "Are there any pending gate approvals?"
# Expected: Claude calls list_pending_approvals
```

### 9.4 Load Testing

```bash
# Use k6 for load testing the REST gateway
k6 run --vus 10 --duration 60s tests/load/mcp-tools-load.js
```

```javascript
// tests/load/mcp-tools-load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'http://localhost:3000/api/v1';
const AUTH_HEADER = { 'Authorization': `Bearer ${__ENV.ANTHROPIC_API_KEY}` };

export default function () {
  // Test read-heavy endpoints
  const healthRes = http.get(`${BASE_URL}/system/health`, { headers: AUTH_HEADER });
  check(healthRes, { 'fleet health 200': (r) => r.status === 200 });

  const agentsRes = http.get(`${BASE_URL}/agents?limit=10`, { headers: AUTH_HEADER });
  check(agentsRes, { 'list agents 200': (r) => r.status === 200 });

  const budgetRes = http.get(`${BASE_URL}/costs/budget`, { headers: AUTH_HEADER });
  check(budgetRes, { 'check budget 200': (r) => r.status === 200 });

  sleep(1);
}
```

### 9.5 Test Coverage Matrix

| Tool | Unit Test | Integration Test | Load Test | Notes |
|---|---|---|---|---|
| `trigger_pipeline` | Yes | Yes | Yes | Test budget enforcement |
| `get_pipeline_status` | Yes | Yes | Yes | |
| `list_pipeline_runs` | Yes | Yes | Yes | Test pagination |
| `resume_pipeline` | Yes | Yes | No | Requires paused pipeline |
| `cancel_pipeline` | Yes | Yes | No | |
| `get_pipeline_documents` | Yes | Yes | Yes | |
| `retry_pipeline_step` | Yes | Yes | No | Requires failed stage |
| `get_pipeline_config` | Yes | Yes | Yes | |
| `validate_pipeline_input` | Yes | Yes | Yes | |
| `list_agents` | Yes | Yes | Yes | |
| `get_agent` | Yes | Yes | Yes | |
| `invoke_agent` | Yes | Yes | Yes | Test timeout handling |
| `check_agent_health` | Yes | Yes | Yes | |
| `promote_agent_version` | Yes | Yes | No | Admin action |
| `rollback_agent_version` | Yes | Yes | No | Admin action |
| `set_canary_traffic` | Yes | Yes | No | |
| `get_agent_maturity` | Yes | Yes | Yes | |
| `get_cost_report` | Yes | Yes | Yes | |
| `check_budget` | Yes | Yes | Yes | |
| `query_audit_events` | Yes | Yes | Yes | Test pagination |
| `get_audit_summary` | Yes | Yes | Yes | |
| `export_audit_report` | Yes | Yes | No | Resource intensive |
| `list_pending_approvals` | Yes | Yes | Yes | |
| `approve_gate` | Yes | Yes | No | Requires pending approval |
| `reject_gate` | Yes | Yes | No | Requires pending approval |
| `get_cost_anomalies` | Yes | Yes | Yes | |
| `update_budget_threshold` | Yes | Yes | No | Admin action |
| `search_exceptions` | Yes | Yes | Yes | Test semantic search |
| `create_exception` | Yes | Yes | No | Test deduplication |
| `promote_exception` | Yes | Yes | No | |
| `list_exceptions` | Yes | Yes | Yes | Test pagination |
| `get_fleet_health` | Yes | Yes | Yes | |
| `get_mcp_status` | Yes | Yes | Yes | |
| `list_recent_mcp_calls` | Yes | Yes | Yes | |
| `check_provider_health` | Yes | Yes | Yes | Test all 3 providers |
| `set_agent_provider` | Yes | Yes | No | Test provider switch + revert |

---

## Appendix A: Data Shape Quick Reference

All data shapes are defined in the INTERACTION-MAP (Doc 07). This appendix provides a quick-reference summary for implementers.

| Data Shape | Used By | Key Fields |
|---|---|---|
| `PipelineRun` | I-001, I-002, I-003, I-004, I-005, I-007 | run_id, project_id, status, progress_percent, current_stage, stages[], created_at, estimated_cost_usd |
| `PipelineDocument` | I-006 | doc_type, stage_index, content, generated_at, agent_id, token_count, quality_score |
| `PipelineConfig` | I-008 | template, stages[], total_estimated_cost_usd, supported_options |
| `ValidationResult` | I-009 | is_valid, warnings[], errors[], estimated_cost_usd, estimated_duration_minutes |
| `AgentSummary` | I-020 | agent_id, name, role, version, maturity, health_status, last_invoked_at |
| `AgentDetail` | I-021 | agent_id, name, role, description, model, version, maturity, manifest, prompt_template, performance_metrics, version_history[] |
| `AgentInvocationResult` | I-022 | invocation_id, agent_id, status, output_content, token_usage, cost_usd, latency_ms, model_used |
| `AgentHealth` | I-023 | agent_id, status, latency_ms, error_rate_percent, last_success_at, consecutive_failures |
| `AgentVersion` | I-024, I-025, I-026 | agent_id, version, maturity, promoted_at/rolled_back_at, canary_percent |
| `AgentMaturity` | I-027 | agent_id, current_maturity, promotion_readiness_score, criteria[], total_invocations, success_rate |
| `CostReport` | I-040 | scope, period, total_cost_usd, breakdown[], daily_trend[], comparison_to_previous_period |
| `BudgetStatus` | I-041, I-049 | scope, budget_usd, spent_usd, remaining_usd, utilization_percent, is_over_budget |
| `AuditEvent` | I-042 | event_id, timestamp, actor, action, resource_type, resource_id, project_id, details |
| `AuditSummary` | I-043 | total_events, events_by_action, events_by_resource_type, top_actors[], daily_trend[] |
| `AuditReport` | I-044 | report_id, format, download_url, size_bytes, event_count, generated_at, expires_at |
| `ApprovalRequest` | I-045 | approval_id, run_id, project_id, gate_type, stage_index, requested_at, context, timeout_at |
| `ApprovalResult` | I-046, I-047 | approval_id, status, approved_by/rejected_by, comment/reason, conditions/suggested_changes |
| `CostAnomaly` | I-048 | anomaly_id, severity, resource_type, resource_id, expected_cost_usd, actual_cost_usd, deviation_percent |
| `KnowledgeException` | I-060, I-061, I-062, I-063 | exception_id, title, category, description, resolution, tags[], status, usage_count |
| `FleetHealth` | I-080 | overall_status, agent_summary, pipeline_summary, cost_summary |
| `McpServerStatus` | I-081 | server_name, status, transport, tool_count, resource_count, uptime_seconds, version |
| `McpCallEvent` | I-082 | call_id, timestamp, server_name, tool_name, caller, status, latency_ms, error_code |

---

## Appendix B: Interaction ID Cross-Reference

| ID | Tool Name | Server | Permission |
|---|---|---|---|
| I-001 | `trigger_pipeline` | agents | write |
| I-002 | `get_pipeline_status` | agents | read |
| I-003 | `list_pipeline_runs` | agents | read |
| I-004 | `resume_pipeline` | agents | write |
| I-005 | `cancel_pipeline` | agents | write |
| I-006 | `get_pipeline_documents` | agents | read |
| I-007 | `retry_pipeline_step` | agents | write |
| I-008 | `get_pipeline_config` | agents | read |
| I-009 | `validate_pipeline_input` | agents | read |
| I-020 | `list_agents` | agents | read |
| I-021 | `get_agent` | agents | read |
| I-022 | `invoke_agent` | agents | write |
| I-023 | `check_agent_health` | agents | read |
| I-024 | `promote_agent_version` | agents | admin |
| I-025 | `rollback_agent_version` | agents | admin |
| I-026 | `set_canary_traffic` | agents | write |
| I-027 | `get_agent_maturity` | agents | read |
| I-040 | `get_cost_report` | governance | read |
| I-041 | `check_budget` | governance | read |
| I-042 | `query_audit_events` | governance | read |
| I-043 | `get_audit_summary` | governance | read |
| I-044 | `export_audit_report` | governance | write |
| I-045 | `list_pending_approvals` | governance | read |
| I-046 | `approve_gate` | governance | admin |
| I-047 | `reject_gate` | governance | admin |
| I-048 | `get_cost_anomalies` | governance | read |
| I-049 | `update_budget_threshold` | governance | admin |
| I-060 | `search_exceptions` | knowledge | read |
| I-061 | `create_exception` | knowledge | write |
| I-062 | `promote_exception` | knowledge | write |
| I-063 | `list_exceptions` | knowledge | read |
| I-080 | `get_fleet_health` | agents | read |
| I-081 | `get_mcp_status` | agents | read |
| I-082 | `list_recent_mcp_calls` | agents | read |
| I-083 | `check_provider_health` | agents | read |
| I-084 | `set_agent_provider` | agents | write |

---

*End of MCP-TOOL-SPEC --- Document 08 of 24*
