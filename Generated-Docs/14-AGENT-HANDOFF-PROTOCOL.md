# AGENT-HANDOFF-PROTOCOL — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 14 of 14+2 | Status: Draft

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Agent Registry](#2-agent-registry)
3. [Session Context Store](#3-session-context-store)
4. [Message Envelope](#4-message-envelope)
5. [Orchestrator Protocol](#5-orchestrator-protocol)
6. [Quality Gate Protocol](#6-quality-gate-protocol)
7. [Failure & Recovery Modes](#7-failure--recovery-modes)
8. [Audit Trail](#8-audit-trail)
9. [Pipeline Execution Modes](#9-pipeline-execution-modes)
10. [Cross-Reference Matrix](#10-cross-reference-matrix)

---

## 1. Purpose

This document defines the meta-protocol governing how the 14 document-generating agents communicate, pass context, validate outputs, and handle failures within the Full-Stack-First document generation pipeline. It is the operational contract between:

- **The Orchestrator** — the pipeline controller that sequences agent execution
- **The 14 Agents** — each responsible for generating one SDLC document (Docs 00-13)
- **The Session Context Store** — the shared state medium (PostgreSQL `session_context` table, migration 006)
- **The Quality Gate** — the validation layer that runs after every agent output

**Scope:** This protocol governs the document generation pipeline only. It does not govern the 48 runtime agents described in the ARCH (Doc 02). Those runtime agents are a product feature; these 14 agents are the build-time pipeline that produces the specification documents.

---

## 2. Agent Registry

### 2.1 Agent Inventory

| Agent ID | Step | Document Produced | Session Read Keys | Session Write Key | Depends On (Agents) |
|----------|------|-------------------|-------------------|-------------------|----------------------|
| `D0-roadmap` | 1 | 00-ROADMAP.md | `raw_spec` | `roadmap_doc` | None |
| `D1-prd` | 2 | 01-PRD.md | `raw_spec` | `prd_doc` | None |
| `D2-arch` | 3 | 02-ARCH.md | `prd_doc` | `arch_doc` | D1-prd |
| `D3-claude` | 4 | 03-CLAUDE.md | `roadmap_doc`, `arch_doc` | `claude_doc` | D0-roadmap, D2-arch |
| `D4-quality` | 5 | 04-QUALITY.md | `prd_doc`, `arch_doc` | `quality_doc` | D1-prd, D2-arch |
| `D5-features` | 6 | 05-FEATURE-CATALOG.md | `prd_doc`, `arch_doc` | `feature_catalog` | D1-prd, D2-arch |
| `D6-interaction` | 7 | 06-INTERACTION-MAP.md | `prd_doc`, `arch_doc`, `feature_catalog`, `quality_doc` | `interaction_map` | D1-prd, D2-arch, D4-quality, D5-features |
| `D7-mcp` | 8 | 07-MCP-TOOL-SPEC.md | `interaction_map`, `arch_doc`, `feature_catalog`, `quality_doc` | `mcp_tool_spec` | D2-arch, D4-quality, D5-features, D6-interaction |
| `D8-design` | 9 | 08-DESIGN-SPEC.md | `interaction_map`, `prd_doc`, `quality_doc`, `feature_catalog` | `design_spec` | D1-prd, D4-quality, D5-features, D6-interaction |
| `D9-data` | 10 | 09-DATA-MODEL.md | `arch_doc`, `feature_catalog`, `quality_doc`, `mcp_tool_spec`, `design_spec`, `interaction_map` | `data_model` | D2-arch, D4-quality, D5-features, D6-interaction, D7-mcp, D8-design |
| `D10-api` | 11 | 10-API-CONTRACTS.md | `arch_doc`, `data_model`, `prd_doc`, `mcp_tool_spec`, `design_spec`, `interaction_map` | `api_contracts` | D1-prd, D2-arch, D6-interaction, D7-mcp, D8-design, D9-data |
| `D11-backlog` | 12 | 11-BACKLOG.md | `feature_catalog`, `prd_doc`, `arch_doc`, `quality_doc`, `mcp_tool_spec`, `design_spec`, `interaction_map` | `backlog` | D1-prd, D2-arch, D4-quality, D5-features, D6-interaction, D7-mcp, D8-design |
| `D12-enforce` | 13 | 12-ENFORCEMENT.md | `claude_doc`, `arch_doc` | `enforcement_rules` | D2-arch, D3-claude |
| `D13-testing` | 14 | 13-TESTING.md | `arch_doc`, `quality_doc`, `data_model`, `claude_doc`, `mcp_tool_spec`, `design_spec`, `interaction_map` | `test_strategy` | D2-arch, D3-claude, D4-quality, D6-interaction, D7-mcp, D8-design, D9-data |

### 2.2 Session Key Definitions

| Session Key | Data Type | Written By | Read By | Description |
|-------------|-----------|------------|---------|-------------|
| `raw_spec` | `text/markdown` | Orchestrator (pre-loaded) | D0-roadmap, D1-prd | The master build specification (input document) |
| `roadmap_doc` | `text/markdown` | D0-roadmap | D3-claude | Project context, milestones, timeline |
| `prd_doc` | `text/markdown` | D1-prd | D2-arch, D4-quality, D5-features, D6-interaction, D8-design, D10-api, D11-backlog | Personas, journeys, capabilities |
| `arch_doc` | `text/markdown` | D2-arch | D3-claude, D4-quality, D5-features, D6-interaction, D7-mcp, D9-data, D10-api, D11-backlog, D12-enforce, D13-testing | Architecture, service layer, infrastructure |
| `claude_doc` | `text/markdown` | D3-claude | D12-enforce, D13-testing | Coding rules, patterns, conventions |
| `quality_doc` | `text/markdown` | D4-quality | D6-interaction, D7-mcp, D8-design, D9-data, D11-backlog, D13-testing | Q-NNN non-functional requirements |
| `feature_catalog` | `text/markdown` | D5-features | D6-interaction, D7-mcp, D8-design, D9-data, D11-backlog | F-NNN features with interfaces[] |
| `interaction_map` | `text/markdown` | D6-interaction | D7-mcp, D8-design, D9-data, D10-api, D11-backlog, D13-testing | Shared data shapes, interaction IDs, cross-interface journeys |
| `mcp_tool_spec` | `text/markdown` | D7-mcp | D9-data, D10-api, D11-backlog, D13-testing | MCP tools referencing interaction IDs |
| `design_spec` | `text/markdown` | D8-design | D9-data, D10-api, D11-backlog | Screens referencing interaction IDs |
| `data_model` | `text/markdown` | D9-data | D10-api, D13-testing | PostgreSQL schemas, indexes, migrations |
| `api_contracts` | `text/markdown` | D10-api | (terminal) | REST endpoint specifications |
| `backlog` | `text/markdown` | D11-backlog | (terminal) | S-NNN stories with interaction_ids |
| `enforcement_rules` | `text/markdown` | D12-enforce | (terminal) | .claude/ rules and /new-interaction skill |
| `test_strategy` | `text/markdown` | D13-testing | (terminal) | Test strategy with cross-interface tests |

### 2.3 Dependency Graph (Visual)

```
Step 1:  D0-roadmap ──────────────────────────────┐
         D1-prd ──────┬──────────────────────────┐ │  (parallel: D0 || D1)
                       │                          │ │
Step 3:                └──> D2-arch ──────────────┼─┤
                                │                 │ │
Step 4-6:              ┌───────┼────> D3-claude ──┼─┘  (parallel: D3 || D4 || D5)
                       │       ├────> D4-quality  │
                       │       └────> D5-features │
                       │                │    │    │
Step 7:                │       D6-interaction <───┘
                       │           │        │
Step 8-9:              │    D7-mcp ─┤       ├─ D8-design   (parallel: D7 || D8)
                       │           │        │
Step 10:               │       D9-data <────┘
                       │           │
Step 11:               │       D10-api
                       │
Step 12-14:            ├──> D11-backlog                    (parallel: D11 || D12 || D13)
                       ├──> D12-enforce
                       └──> D13-testing
```

---

## 3. Session Context Store

### 3.1 Database Schema

The Session Context Store is backed by the `session_context` table defined in migration 006. This table is BLOCKING — the pipeline cannot run without it.

```sql
CREATE TABLE session_context (
    id              BIGSERIAL PRIMARY KEY,
    session_id      UUID NOT NULL,
    key             VARCHAR(128) NOT NULL,
    value           JSONB NOT NULL,
    written_by      VARCHAR(64) NOT NULL,
    written_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ttl_seconds     INTEGER NOT NULL DEFAULT 86400 CHECK (ttl_seconds > 0),
    expires_at      TIMESTAMPTZ GENERATED ALWAYS AS (
                        written_at + (ttl_seconds || ' seconds')::INTERVAL
                    ) STORED,
    UNIQUE (session_id, key)
);

-- Indexes
CREATE INDEX idx_session_lookup ON session_context(session_id, key);
CREATE INDEX idx_session_expires ON session_context(expires_at) WHERE expires_at IS NOT NULL;
```

### 3.2 Python API — `SessionStore`

```python
"""
Session Context Store — Inter-agent context passing for the document pipeline.
Backed by PostgreSQL session_context table (migration 006).
"""

import json
import uuid
from datetime import datetime
from typing import Any, Optional

import asyncpg


class SessionStore:
    """
    Key-value store for passing document artifacts between pipeline agents.

    Invariants:
      - Each key has exactly ONE writer (enforced by UNIQUE(session_id, key) + ON CONFLICT)
      - All reads/writes are scoped to a run_id (maps to session_id in the DB)
      - Values persist across process restarts (PostgreSQL-backed)
      - Expired rows are cleaned by a background TTL job (hourly)
    """

    def __init__(self, pool: asyncpg.Pool, default_ttl: int = 86400):
        """
        Args:
            pool: asyncpg connection pool to PostgreSQL
            default_ttl: Time-to-live in seconds for stored values (default: 24 hours)
        """
        self._pool = pool
        self._default_ttl = default_ttl

    async def write(
        self,
        run_id: uuid.UUID,
        key: str,
        value: Any,
        written_by: str,
        ttl_seconds: Optional[int] = None,
    ) -> datetime:
        """
        Store a document artifact in the session context.

        Uses INSERT ... ON CONFLICT DO UPDATE (upsert) so that:
          - First write creates the row
          - Subsequent writes by the same agent overwrite (e.g., after retry)

        Args:
            run_id: Pipeline run UUID (maps to session_id)
            key: Session key (e.g., "prd_doc", "arch_doc")
            value: Document content (will be JSON-serialized into JSONB)
            written_by: Agent ID that produced this value (e.g., "D1-prd")
            ttl_seconds: Override default TTL for this entry

        Returns:
            Timestamp when the value was written

        Raises:
            SessionWriteConflictError: If a different agent already wrote this key
        """
        ttl = ttl_seconds or self._default_ttl

        async with self._pool.acquire() as conn:
            # Check for write conflict: different agent already owns this key
            existing = await conn.fetchrow(
                """
                SELECT written_by FROM session_context
                WHERE session_id = $1 AND key = $2
                """,
                run_id, key,
            )
            if existing and existing["written_by"] != written_by:
                raise SessionWriteConflictError(
                    f"Key '{key}' in run {run_id} already written by "
                    f"'{existing['written_by']}', cannot be overwritten by '{written_by}'"
                )

            row = await conn.fetchrow(
                """
                INSERT INTO session_context (session_id, key, value, written_by, ttl_seconds)
                VALUES ($1, $2, $3::jsonb, $4, $5)
                ON CONFLICT (session_id, key)
                DO UPDATE SET
                    value = EXCLUDED.value,
                    written_at = NOW(),
                    ttl_seconds = EXCLUDED.ttl_seconds
                RETURNING written_at
                """,
                run_id, key, json.dumps(value), written_by, ttl,
            )
            return row["written_at"]

    async def read(
        self,
        run_id: uuid.UUID,
        key: str,
    ) -> Optional[Any]:
        """
        Retrieve a single document artifact from the session context.

        Args:
            run_id: Pipeline run UUID
            key: Session key to retrieve

        Returns:
            The stored value (deserialized from JSONB), or None if not found / expired
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT value FROM session_context
                WHERE session_id = $1 AND key = $2 AND expires_at > NOW()
                """,
                run_id, key,
            )
            return json.loads(row["value"]) if row else None

    async def read_many(
        self,
        run_id: uuid.UUID,
        keys: list[str],
    ) -> dict[str, Any]:
        """
        Batch-read multiple document artifacts in a single query.

        Args:
            run_id: Pipeline run UUID
            keys: List of session keys to retrieve

        Returns:
            Dict mapping key -> value for all found (non-expired) keys.
            Missing keys are omitted from the result.
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT key, value FROM session_context
                WHERE session_id = $1 AND key = ANY($2) AND expires_at > NOW()
                """,
                run_id, keys,
            )
            return {row["key"]: json.loads(row["value"]) for row in rows}

    async def exists(
        self,
        run_id: uuid.UUID,
        key: str,
    ) -> bool:
        """
        Check whether a key exists and has not expired.

        Args:
            run_id: Pipeline run UUID
            key: Session key to check

        Returns:
            True if the key exists and is not expired, False otherwise
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchval(
                """
                SELECT COUNT(*) FROM session_context
                WHERE session_id = $1 AND key = $2 AND expires_at > NOW()
                """,
                run_id, key,
            )
            return row > 0

    async def delete(
        self,
        run_id: uuid.UUID,
        key: str,
    ) -> bool:
        """
        Explicitly remove a key (used during regeneration to invalidate downstream).

        Args:
            run_id: Pipeline run UUID
            key: Session key to remove

        Returns:
            True if a row was deleted, False if key did not exist
        """
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM session_context
                WHERE session_id = $1 AND key = $2
                """,
                run_id, key,
            )
            return result == "DELETE 1"

    async def list_keys(
        self,
        run_id: uuid.UUID,
    ) -> list[dict]:
        """
        List all active (non-expired) keys for a run, with metadata.

        Returns:
            List of dicts with key, written_by, written_at fields
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT key, written_by, written_at FROM session_context
                WHERE session_id = $1 AND expires_at > NOW()
                ORDER BY written_at ASC
                """,
                run_id,
            )
            return [dict(row) for row in rows]

    async def cleanup_expired(self) -> int:
        """
        Remove expired rows. Called by hourly background job.

        Returns:
            Number of rows deleted
        """
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM session_context WHERE expires_at < NOW()"
            )
            # result is "DELETE N"
            return int(result.split()[-1])


class SessionWriteConflictError(Exception):
    """Raised when an agent attempts to write a key owned by a different agent."""
    pass
```

### 3.3 Storage Rules

| Rule | Enforcement |
|------|-------------|
| **One writer per key** | `UNIQUE(session_id, key)` constraint + application-level `written_by` check before upsert. A key written by `D1-prd` cannot be overwritten by `D2-arch`. Only the original writer (or the orchestrator during regeneration) may update a key. |
| **Scoped to run_id** | Every query includes `WHERE session_id = $1`. RLS policy `session_context_session_isolation` enforces this at the database level as defense-in-depth. |
| **Persists across restarts** | PostgreSQL-backed. If the orchestrator crashes mid-pipeline, completed steps remain in the store. The `resume` mode reads existing keys to skip completed work. |
| **TTL-based expiration** | Default TTL = 86400 seconds (24 hours). The `expires_at` column is a generated stored column. An hourly background job runs `DELETE FROM session_context WHERE expires_at < NOW()`. |
| **No cross-run leakage** | Each pipeline run gets a fresh `run_id` (UUID v4). Keys from previous runs expire independently. |

---

## 4. Message Envelope

### 4.1 Envelope Schema

Every agent invocation is triggered by a message envelope. The orchestrator builds the envelope, sends it to the agent, and expects a response envelope back.

**Request Envelope (Orchestrator -> Agent):**

```json
{
  "envelope_version": "1.0",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "step": 7,
  "agent_id": "D7-mcp",
  "action": "generate",
  "inputs": {
    "interaction_map": "session://interaction_map",
    "arch_doc": "session://arch_doc",
    "feature_catalog": "session://feature_catalog",
    "quality_doc": "session://quality_doc"
  },
  "output_key": "mcp_tool_spec",
  "config": {
    "model": "claude-sonnet-4-6",
    "max_tokens": 16000,
    "temperature": 0.2,
    "cost_ceiling_usd": 2.00
  },
  "prompt_template": "Base_prompts/Full-Stack-First/07-MCP-TOOL-SPEC.md",
  "metadata": {
    "triggered_by": "orchestrator",
    "triggered_at": "2026-03-24T14:30:00.000Z",
    "retry_count": 0,
    "retry_feedback": null,
    "pipeline_mode": "full",
    "correlation_id": "corr-550e-mcp-001"
  }
}
```

**Response Envelope (Agent -> Orchestrator):**

```json
{
  "envelope_version": "1.0",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "step": 7,
  "agent_id": "D7-mcp",
  "action": "generate_response",
  "output_key": "mcp_tool_spec",
  "output_size_bytes": 42350,
  "output_hash": "sha256:a1b2c3d4e5f6...",
  "status": "completed",
  "timing": {
    "started_at": "2026-03-24T14:30:00.500Z",
    "completed_at": "2026-03-24T14:30:45.200Z",
    "duration_ms": 44700
  },
  "cost": {
    "tokens_in": 12450,
    "tokens_out": 8200,
    "cost_usd": 0.85,
    "model": "claude-sonnet-4-6"
  },
  "error": null
}
```

### 4.2 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `envelope_version` | string | Yes | Always `"1.0"`. Enables future protocol evolution. |
| `run_id` | UUID | Yes | Unique identifier for this pipeline execution. Maps to `session_id` in the database. |
| `step` | integer | Yes | Execution step number (1-14). Determines ordering within the topological sort. |
| `agent_id` | string | Yes | Agent identifier from the Agent Registry (e.g., `"D7-mcp"`). |
| `action` | string | Yes | One of: `generate`, `generate_response`, `validate`, `validate_response`. |
| `inputs` | object | Yes (request) | Map of input key names to `session://` references. The orchestrator resolves these to actual values before invoking the agent. |
| `output_key` | string | Yes | The session key where the agent's output will be stored. |
| `config.model` | string | Yes | LLM model identifier. Default: `claude-sonnet-4-6`. |
| `config.max_tokens` | integer | Yes | Maximum output tokens for the LLM call. |
| `config.temperature` | float | Yes | LLM temperature setting. Recommended: 0.2 for specification generation. |
| `config.cost_ceiling_usd` | float | Yes | Maximum cost for this single agent execution. If exceeded, the agent MUST abort. |
| `prompt_template` | string | Yes (request) | Path to the prompt template file (read-only reference). |
| `metadata.triggered_by` | string | Yes | Always `"orchestrator"` in normal operation. |
| `metadata.triggered_at` | ISO8601 | Yes | Timestamp when the orchestrator dispatched this envelope. |
| `metadata.retry_count` | integer | Yes | Number of previous attempts (0 = first attempt, max 2). |
| `metadata.retry_feedback` | string/null | No | Quality gate failure feedback from the previous attempt. Included in the prompt on retry. |
| `metadata.pipeline_mode` | string | Yes | One of: `full`, `resume`, `regenerate`, `validate-only`, `dry-run`. |
| `metadata.correlation_id` | string | Yes | Unique ID for tracing this specific invocation across logs. |

### 4.3 Input Resolution

The orchestrator resolves `session://` references before invoking the agent:

```python
async def resolve_inputs(
    store: SessionStore,
    run_id: uuid.UUID,
    inputs: dict[str, str],
) -> dict[str, str]:
    """
    Resolve session:// references to actual document content.

    Args:
        store: SessionStore instance
        run_id: Pipeline run UUID
        inputs: Map of input names to session:// URIs

    Returns:
        Map of input names to resolved document content

    Raises:
        MissingInputError: If any required input is not found in the store
    """
    keys = [uri.replace("session://", "") for uri in inputs.values()]
    resolved = await store.read_many(run_id, keys)

    result = {}
    for name, uri in inputs.items():
        key = uri.replace("session://", "")
        if key not in resolved:
            raise MissingInputError(
                f"Required input '{name}' (key='{key}') not found in session store "
                f"for run {run_id}. Upstream agent may have failed."
            )
        result[name] = resolved[key]

    return result
```

---

## 5. Orchestrator Protocol

### 5.1 Pipeline Algorithm

```python
"""
Orchestrator — Pipeline controller for the 14-document Full-Stack-First build.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class PipelineConfig:
    run_id: uuid.UUID
    mode: str  # full | resume | regenerate | validate-only | dry-run
    cost_ceiling_usd: float = 25.00
    per_agent_ceiling_usd: float = 2.00
    max_retries: int = 2
    model: str = "claude-sonnet-4-6"
    regenerate_targets: list[str] | None = None  # agent_ids for regenerate mode


# Dependency graph: agent_id -> list of agent_ids it depends on
DEPENDENCY_GRAPH: dict[str, list[str]] = {
    "D0-roadmap":    [],
    "D1-prd":        [],
    "D2-arch":       ["D1-prd"],
    "D3-claude":     ["D0-roadmap", "D2-arch"],
    "D4-quality":    ["D1-prd", "D2-arch"],
    "D5-features":   ["D1-prd", "D2-arch"],
    "D6-interaction":["D1-prd", "D2-arch", "D4-quality", "D5-features"],
    "D7-mcp":        ["D2-arch", "D4-quality", "D5-features", "D6-interaction"],
    "D8-design":     ["D1-prd", "D4-quality", "D5-features", "D6-interaction"],
    "D9-data":       ["D2-arch", "D4-quality", "D5-features", "D6-interaction", "D7-mcp", "D8-design"],
    "D10-api":       ["D1-prd", "D2-arch", "D6-interaction", "D7-mcp", "D8-design", "D9-data"],
    "D11-backlog":   ["D1-prd", "D2-arch", "D4-quality", "D5-features", "D6-interaction", "D7-mcp", "D8-design"],
    "D12-enforce":   ["D2-arch", "D3-claude"],
    "D13-testing":   ["D2-arch", "D3-claude", "D4-quality", "D6-interaction", "D7-mcp", "D8-design", "D9-data"],
}

# Agent ID -> session write key mapping
AGENT_OUTPUT_KEY: dict[str, str] = {
    "D0-roadmap":    "roadmap_doc",
    "D1-prd":        "prd_doc",
    "D2-arch":       "arch_doc",
    "D3-claude":     "claude_doc",
    "D4-quality":    "quality_doc",
    "D5-features":   "feature_catalog",
    "D6-interaction":"interaction_map",
    "D7-mcp":        "mcp_tool_spec",
    "D8-design":     "design_spec",
    "D9-data":       "data_model",
    "D10-api":       "api_contracts",
    "D11-backlog":   "backlog",
    "D12-enforce":   "enforcement_rules",
    "D13-testing":   "test_strategy",
}


async def run_pipeline(config: PipelineConfig, store: SessionStore) -> PipelineResult:
    """
    Execute the 14-document pipeline.

    Algorithm:
      1. Load dependency graph
      2. Topological sort into execution layers (parallel groups)
      3. For each layer:
         a. For each agent in the layer (parallel):
            i.   Check if deps are satisfied (keys exist in store)
            ii.  In resume mode: skip if output key already exists + quality passed
            iii. Resolve inputs from session store
            iv.  Build message envelope
            v.   Execute agent (LLM call)
            vi.  Run quality gate on output
            vii. If PASS/CONDITIONAL: store output in session store
            viii.If FAIL: retry with feedback (up to max_retries)
            ix.  Log audit event
         b. Wait for all agents in the layer to complete
      4. Check cumulative cost against $25 ceiling
      5. Return pipeline result
    """

    # Step 1-2: Topological sort into parallel execution layers
    layers = topological_sort_layers(DEPENDENCY_GRAPH)
    # Result: [
    #   ["D0-roadmap", "D1-prd"],           # Layer 1: parallel
    #   ["D2-arch"],                          # Layer 2: sequential
    #   ["D3-claude", "D4-quality", "D5-features"],  # Layer 3: parallel
    #   ["D6-interaction"],                   # Layer 4: sequential
    #   ["D7-mcp", "D8-design"],             # Layer 5: parallel (the Full-Stack-First sprint)
    #   ["D9-data"],                          # Layer 6: sequential
    #   ["D10-api"],                          # Layer 7: sequential
    #   ["D11-backlog", "D12-enforce", "D13-testing"],  # Layer 8: parallel
    # ]

    cumulative_cost = 0.0
    results = []

    for layer_index, layer in enumerate(layers):
        # Cost ceiling check before each layer
        if cumulative_cost >= config.cost_ceiling_usd:
            raise CostCeilingBreachedError(
                f"Cumulative cost ${cumulative_cost:.2f} exceeds ceiling "
                f"${config.cost_ceiling_usd:.2f}. Stopping pipeline."
            )

        # Execute all agents in this layer in parallel
        tasks = []
        for agent_id in layer:
            if config.mode == "resume" and await _should_skip(store, config.run_id, agent_id):
                results.append(AgentResult(agent_id=agent_id, status="skipped"))
                continue

            if config.mode == "dry-run":
                results.append(AgentResult(agent_id=agent_id, status="dry-run",
                                           estimated_cost=config.per_agent_ceiling_usd))
                continue

            tasks.append(
                _execute_agent_with_retries(config, store, agent_id)
            )

        layer_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in layer_results:
            if isinstance(result, Exception):
                raise PipelineStepFailedError(f"Layer {layer_index} failed: {result}")
            results.append(result)
            cumulative_cost += result.cost_usd

    return PipelineResult(
        run_id=config.run_id,
        mode=config.mode,
        total_cost_usd=cumulative_cost,
        agent_results=results,
        completed_at=datetime.now(timezone.utc),
    )
```

### 5.2 Topological Sort with Parallel Layers

```python
def topological_sort_layers(graph: dict[str, list[str]]) -> list[list[str]]:
    """
    Kahn's algorithm modified to produce parallel execution layers.

    Returns a list of layers, where each layer contains agents that
    can execute in parallel (all dependencies satisfied by prior layers).
    """
    in_degree = {node: 0 for node in graph}
    for node, deps in graph.items():
        in_degree[node] = len(deps)

    # Reverse adjacency: who depends on me?
    dependents = {node: [] for node in graph}
    for node, deps in graph.items():
        for dep in deps:
            dependents[dep].append(node)

    # Start with nodes that have no dependencies
    current_layer = [node for node, degree in in_degree.items() if degree == 0]
    layers = []

    while current_layer:
        layers.append(sorted(current_layer))  # Sort for deterministic ordering
        next_layer = []
        for node in current_layer:
            for dependent in dependents[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    next_layer.append(dependent)
        current_layer = next_layer

    # Validate: all nodes processed (no circular dependencies)
    processed = sum(len(layer) for layer in layers)
    if processed != len(graph):
        unprocessed = [n for n in graph if n not in
                       [node for layer in layers for node in layer]]
        raise CircularDependencyError(
            f"Circular dependency detected. Unprocessed agents: {unprocessed}"
        )

    return layers
```

### 5.3 Parallel Execution Rules

The dependency graph produces these execution layers:

| Layer | Step(s) | Agents | Parallelism | Rationale |
|-------|---------|--------|-------------|-----------|
| 1 | 1-2 | `D0-roadmap`, `D1-prd` | 2-way parallel | Both read only `raw_spec`, no interdependency |
| 2 | 3 | `D2-arch` | Sequential | Depends on `prd_doc` from Layer 1 |
| 3 | 4-6 | `D3-claude`, `D4-quality`, `D5-features` | 3-way parallel | All depend on Layer 1-2 outputs, none depend on each other |
| 4 | 7 | `D6-interaction` | Sequential | Depends on `quality_doc` + `feature_catalog` from Layer 3 |
| 5 | 8-9 | `D7-mcp`, `D8-design` | **2-way parallel** | **The Full-Stack-First Sprint** — both read from `interaction_map`, neither reads the other |
| 6 | 10 | `D9-data` | Sequential | Depends on both `mcp_tool_spec` and `design_spec` from Layer 5 |
| 7 | 11 | `D10-api` | Sequential | Depends on `data_model` from Layer 6 |
| 8 | 12-14 | `D11-backlog`, `D12-enforce`, `D13-testing` | 3-way parallel | All terminal documents, no downstream consumers |

**Maximum parallelism:** 3 agents (Layers 3 and 8).
**Critical path:** D1-prd -> D2-arch -> D5-features -> D6-interaction -> D7-mcp -> D9-data -> D10-api (7 sequential steps).
**Estimated wall-clock time:** ~5-7 minutes for a full run (14 agent calls, 8 sequential layers).

### 5.4 Cost Governance

| Level | Ceiling | Enforcement | Breach Action |
|-------|---------|-------------|---------------|
| **Per-agent** | $2.00 | `config.cost_ceiling_usd` in envelope | Agent aborts mid-generation. Returns partial output flagged as `cost_breach`. |
| **Per-run** | $25.00 | `cumulative_cost` check before each layer | Pipeline halts. Completed steps preserved in session store. Human notified. |
| **Per-retry** | Counts against per-agent ceiling | Retry cost accumulates | After 2 retries, agent has spent up to $6.00 (3 x $2.00). Escalate to human. |

---

## 6. Quality Gate Protocol

### 6.1 Overview

Every agent output passes through a two-phase quality gate before being stored in the session context. The gate runs synchronously after each agent completes and before the output is written.

```
Agent Output
    │
    ▼
┌──────────────────┐
│ PHASE 1: FORMAT  │  (no LLM, deterministic checks)
│ CHECK            │
└────────┬─────────┘
         │ PASS
         ▼
┌──────────────────┐
│ PHASE 2: RUBRIC  │  (LLM judge, scored evaluation)
│ SCORING          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DECISION:        │
│ PASS / COND /    │
│ FAIL             │
└──────────────────┘
```

### 6.2 Phase 1: Format Check (No LLM)

Deterministic validation that runs in <1 second. No LLM cost incurred.

| Check | What It Validates | Failure Action |
|-------|-------------------|----------------|
| **Version header** | Document starts with `# TITLE — Agentic SDLC Platform` followed by `**Version:** v1.0` | Immediate FAIL — prompt template was ignored |
| **Required sections** | Each document type has a list of mandatory section headings (e.g., PRD must have "Personas", "Journeys", "Capabilities") | FAIL with list of missing sections |
| **ID format** | Feature IDs match `F-NNN`, quality IDs match `Q-NNN`, interaction IDs match `I-NNN`, story IDs match `S-NNN` | FAIL with malformed IDs |
| **Cross-references** | Interaction IDs referenced in the document exist in the `interaction_map` (if interaction_map is an input) | FAIL with orphaned references |
| **Size bounds** | Output is between 2,000 and 200,000 characters | FAIL if outside bounds (too short = incomplete, too long = hallucination) |
| **Valid markdown** | No broken table syntax, no unclosed code blocks | FAIL with parse errors |

```python
@dataclass
class FormatCheckResult:
    passed: bool
    errors: list[str]
    warnings: list[str]

def run_format_check(agent_id: str, output: str, inputs: dict[str, str]) -> FormatCheckResult:
    """
    Deterministic format validation. No LLM call.
    Returns FormatCheckResult with pass/fail and error details.
    """
    errors = []
    warnings = []

    # Version header check
    if not output.startswith("# "):
        errors.append("Missing document title (must start with '# ')")
    if "**Version:**" not in output[:500]:
        errors.append("Missing version header in first 500 characters")

    # Required sections per agent
    required_sections = REQUIRED_SECTIONS.get(agent_id, [])
    for section in required_sections:
        if section.lower() not in output.lower():
            errors.append(f"Missing required section: '{section}'")

    # ID format validation
    _validate_id_formats(output, agent_id, errors)

    # Cross-reference validation (if interaction_map is available)
    if "interaction_map" in inputs:
        _validate_cross_references(output, inputs["interaction_map"], errors, warnings)

    # Size bounds
    if len(output) < 2000:
        errors.append(f"Output too short ({len(output)} chars, minimum 2000)")
    if len(output) > 200000:
        errors.append(f"Output too long ({len(output)} chars, maximum 200000)")

    return FormatCheckResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
```

### 6.3 Phase 2: Rubric Scoring (LLM Judge)

An LLM evaluator scores the output across five dimensions. This costs approximately $0.10-0.20 per evaluation.

| Dimension | Weight | What It Measures | Score Anchors |
|-----------|--------|------------------|---------------|
| **Completeness** | 0.25 | All required sections present and substantive? All features/NFRs covered? | 1.0 = every section filled, 0.5 = major gaps, 0.0 = stub document |
| **Accuracy** | 0.30 | Consistent with input documents? No contradictions? Correct references? | 1.0 = fully consistent, 0.5 = minor contradictions, 0.0 = fabricated content |
| **Format** | 0.15 | Follows document template? Proper markdown? Correct ID formats? | 1.0 = perfect format, 0.5 = minor deviations, 0.0 = unrecognizable |
| **Parity** | 0.15 | MCP and dashboard interfaces treated equally? Data shapes shared? | 1.0 = full parity, 0.5 = one interface favored, 0.0 = single-interface only |
| **Traceability** | 0.15 | Every item traceable to upstream IDs (F-NNN, Q-NNN, I-NNN)? | 1.0 = every item traced, 0.5 = partial tracing, 0.0 = no trace IDs |

**Weighted Score Calculation:**

```
score = (completeness * 0.25) + (accuracy * 0.30) + (format * 0.15)
      + (parity * 0.15) + (traceability * 0.15)
```

**LLM Judge Prompt (abbreviated):**

```
You are a quality evaluator for SDLC specification documents.

DOCUMENT UNDER REVIEW:
{output}

INPUT DOCUMENTS:
{inputs}

Score each dimension from 0.0 to 1.0 with justification.
Return JSON:
{
  "completeness": { "score": 0.95, "justification": "..." },
  "accuracy": { "score": 0.90, "justification": "..." },
  "format": { "score": 1.00, "justification": "..." },
  "parity": { "score": 0.85, "justification": "..." },
  "traceability": { "score": 0.90, "justification": "..." },
  "weighted_score": 0.92,
  "summary": "..."
}
```

### 6.4 Decision Matrix

| Weighted Score | Decision | Action |
|----------------|----------|--------|
| **>= 0.85** | **PASS** | Store output in session context. Log as `status: "pass"`. Proceed to downstream agents. |
| **0.75 - 0.84** | **CONDITIONAL** | Store output in session context WITH a warning annotation. Log as `status: "conditional"`. Proceed to downstream agents. Flag for human review at end of pipeline. |
| **< 0.75** | **FAIL** | Do NOT store output. Log as `status: "fail"`. Trigger retry with quality feedback injected into prompt. |

### 6.5 Retry Protocol

```python
async def _execute_agent_with_retries(
    config: PipelineConfig,
    store: SessionStore,
    agent_id: str,
) -> AgentResult:
    """
    Execute an agent with up to max_retries on quality failure.

    Retry behavior:
      - Include quality gate failure feedback in the retry prompt
      - Each retry is a fresh LLM call (not a continuation)
      - Cost accumulates across retries
      - After max_retries, escalate to human
    """
    retry_feedback = None
    total_cost = 0.0

    for attempt in range(config.max_retries + 1):
        # Build envelope with retry info
        envelope = build_envelope(
            config, agent_id,
            retry_count=attempt,
            retry_feedback=retry_feedback,
        )

        # Execute agent
        response = await execute_agent(envelope, store)
        total_cost += response.cost_usd

        # Phase 1: Format check
        inputs = await resolve_inputs(store, config.run_id, envelope["inputs"])
        format_result = run_format_check(agent_id, response.output, inputs)

        if not format_result.passed:
            retry_feedback = (
                f"FORMAT CHECK FAILED (attempt {attempt + 1}/{config.max_retries + 1}):\n"
                + "\n".join(f"- {e}" for e in format_result.errors)
            )
            if attempt == config.max_retries:
                return AgentResult(
                    agent_id=agent_id, status="failed",
                    cost_usd=total_cost, retry_count=attempt,
                    failure_reason=retry_feedback,
                )
            continue

        # Phase 2: Rubric scoring
        quality_result = await run_rubric_scoring(agent_id, response.output, inputs)

        if quality_result.weighted_score >= 0.85:
            await store.write(config.run_id, AGENT_OUTPUT_KEY[agent_id],
                              response.output, agent_id)
            return AgentResult(
                agent_id=agent_id, status="pass",
                cost_usd=total_cost, quality_score=quality_result.weighted_score,
                retry_count=attempt,
            )
        elif quality_result.weighted_score >= 0.75:
            await store.write(config.run_id, AGENT_OUTPUT_KEY[agent_id],
                              response.output, agent_id)
            return AgentResult(
                agent_id=agent_id, status="conditional",
                cost_usd=total_cost, quality_score=quality_result.weighted_score,
                retry_count=attempt,
                warning=quality_result.summary,
            )
        else:
            retry_feedback = (
                f"QUALITY GATE FAILED (attempt {attempt + 1}/{config.max_retries + 1}):\n"
                f"Score: {quality_result.weighted_score:.2f} (threshold: 0.85)\n"
                f"Dimensions:\n"
                + "\n".join(
                    f"  - {dim}: {score['score']:.2f} — {score['justification']}"
                    for dim, score in quality_result.dimensions.items()
                )
            )
            if attempt == config.max_retries:
                return AgentResult(
                    agent_id=agent_id, status="failed",
                    cost_usd=total_cost, quality_score=quality_result.weighted_score,
                    retry_count=attempt,
                    failure_reason="Exceeded max retries. Escalating to human.",
                )

    # Should not reach here
    raise RuntimeError(f"Unexpected: agent {agent_id} exhausted retries without result")
```

---

## 7. Failure & Recovery Modes

### 7.1 Failure Type Registry

| # | Failure Type | Detection Method | Impact | Recovery Action | Auto-Retry? |
|---|-------------|------------------|--------|-----------------|-------------|
| 1 | **Timeout** | Agent execution exceeds 120 seconds | Single step blocked | Kill the LLM call. Log timeout event. Retry with same inputs (the LLM may have been slow, not wrong). After 2 retries, escalate. | Yes (max 2) |
| 2 | **Quality Gate Fail** | Weighted score < 0.75 | Output rejected, not stored | Retry with quality feedback injected into prompt. Include specific dimension scores and justifications so the agent can self-correct. | Yes (max 2) |
| 3 | **Quality Gate Conditional** | Weighted score 0.75-0.84 | Output stored with warning | No retry. Flag for human review. Pipeline continues. Human can trigger regeneration later. | No |
| 4 | **Missing Input** | `SessionStore.read()` returns `None` for a required key | Agent cannot start | Check if upstream agent failed. If so, the upstream failure is the root cause — do not retry this agent. Report the dependency chain. | No |
| 5 | **API Rate Limit (429)** | HTTP 429 from Anthropic API | Temporary block | Exponential backoff: wait 2^attempt seconds (2s, 4s, 8s). Max 3 retries for rate limits specifically (separate from quality retries). | Yes (max 3) |
| 6 | **API Server Error (500/502/503)** | HTTP 5xx from Anthropic API | Temporary outage | Retry after 5 seconds. Max 3 retries. If persistent, switch to backup model if configured. | Yes (max 3) |
| 7 | **Cost Breach (Per-Agent)** | `response.cost_usd > config.cost_ceiling_usd` | Single agent over budget | Abort the agent. Log the partial output. Do NOT store. Do NOT retry (retrying will cost more). Escalate to human with cost details. | No |
| 8 | **Cost Breach (Pipeline)** | `cumulative_cost >= config.cost_ceiling_usd` | Entire pipeline over budget | Halt pipeline before the next layer. All completed steps remain in session store. Human must approve budget increase to continue. Use `resume` mode after approval. | No |
| 9 | **Circular Dependency** | `topological_sort_layers()` detects unprocessed nodes | Pipeline cannot start | Fail immediately with the cycle details. This is a bug in the dependency graph definition and requires a code fix. | No |
| 10 | **Session Store Unavailable** | PostgreSQL connection error | All reads/writes blocked | Retry connection with exponential backoff (1s, 2s, 4s). Max 5 retries. If persistent, pipeline cannot run — abort with clear error message. | Yes (max 5) |
| 11 | **Write Conflict** | `SessionWriteConflictError` raised | Integrity violation | This should never happen in normal operation (one writer per key). Log as CRITICAL. Abort the pipeline. Investigate manually. | No |
| 12 | **Partial Pipeline (Crash Recovery)** | Orchestrator process restarts | Mid-pipeline interruption | Use `resume` mode. The orchestrator reads existing session keys and skips agents whose output keys exist and passed quality. Resume from the first incomplete layer. | N/A (manual) |

### 7.2 Escalation Protocol

When automated recovery fails, the orchestrator escalates to a human operator:

```json
{
  "event": "human_escalation",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "D7-mcp",
  "failure_type": "quality_gate_fail",
  "attempts": 3,
  "last_score": 0.68,
  "cumulative_cost_usd": 4.50,
  "message": "Agent D7-mcp failed quality gate after 3 attempts. Best score: 0.68 (threshold: 0.75). Dimensions: completeness=0.80, accuracy=0.55, format=0.90, parity=0.60, traceability=0.70. Human review required.",
  "recommended_actions": [
    "Review the last output in session store (key: mcp_tool_spec)",
    "Manually edit and re-upload if close to passing",
    "Adjust prompt template if systemic issue",
    "Run: sdlc-pipeline regenerate --run-id 550e... --step D7-mcp"
  ],
  "escalated_at": "2026-03-24T14:45:00.000Z"
}
```

### 7.3 Recovery State Machine

```
                    ┌─────────┐
                    │ PENDING │
                    └────┬────┘
                         │ start
                         ▼
                    ┌─────────┐
              ┌─────│ RUNNING │─────┐
              │     └────┬────┘     │
              │          │          │
         timeout/     success    quality
         API error               fail
              │          │          │
              ▼          ▼          ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │RETRYING│ │ PASS   │ │RETRYING│
         └───┬────┘ └────────┘ └───┬────┘
             │                     │
        max retries           max retries
        exceeded              exceeded
             │                     │
             ▼                     ▼
        ┌──────────┐         ┌──────────┐
        │ ESCALATED│         │ ESCALATED│
        └──────────┘         └──────────┘
```

---

## 8. Audit Trail

### 8.1 Event Schema

Every agent execution (including retries, skips, and failures) produces an audit event stored in the `audit_events` table (migration 003).

```json
{
  "event": "agent_execution",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "D7-mcp",
  "step": 8,
  "layer": 5,
  "started_at": "2026-03-24T14:30:00.500Z",
  "completed_at": "2026-03-24T14:30:45.200Z",
  "duration_ms": 44700,
  "cost_usd": 0.85,
  "model": "claude-sonnet-4-6",
  "tokens_in": 12450,
  "tokens_out": 8200,
  "output_key": "mcp_tool_spec",
  "output_size_bytes": 42350,
  "output_hash": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
  "quality_score": 0.91,
  "quality_dimensions": {
    "completeness": { "score": 0.95, "justification": "All 22 MCP tools fully specified with schemas and examples" },
    "accuracy": { "score": 0.90, "justification": "Tool names and parameters consistent with interaction map" },
    "format": { "score": 0.95, "justification": "Correct markdown structure, valid JSON schemas" },
    "parity": { "score": 0.85, "justification": "All tools have dashboard counterpart references" },
    "traceability": { "score": 0.88, "justification": "All tools traced to F-NNN and I-NNN IDs" }
  },
  "quality_decision": "pass",
  "status": "completed",
  "retry_count": 0,
  "retry_feedback": null,
  "pipeline_mode": "full",
  "correlation_id": "corr-550e-mcp-001",
  "envelope_hash": "sha256:fedcba0987654321..."
}
```

### 8.2 Pipeline-Level Events

In addition to per-agent events, the orchestrator logs pipeline-level events:

**Pipeline Started:**
```json
{
  "event": "pipeline_started",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "full",
  "cost_ceiling_usd": 25.00,
  "per_agent_ceiling_usd": 2.00,
  "max_retries": 2,
  "model": "claude-sonnet-4-6",
  "total_steps": 14,
  "total_layers": 8,
  "started_at": "2026-03-24T14:25:00.000Z"
}
```

**Pipeline Completed:**
```json
{
  "event": "pipeline_completed",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "full",
  "status": "completed",
  "total_cost_usd": 11.50,
  "total_duration_ms": 380000,
  "agents_passed": 12,
  "agents_conditional": 2,
  "agents_failed": 0,
  "agents_skipped": 0,
  "retries_total": 1,
  "completed_at": "2026-03-24T14:31:20.000Z",
  "conditional_agents": ["D8-design", "D11-backlog"],
  "summary": "14/14 documents generated. 2 conditional (flagged for human review). Total cost: $11.50 / $25.00 ceiling."
}
```

**Layer Completed:**
```json
{
  "event": "layer_completed",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "layer": 5,
  "agents": ["D7-mcp", "D8-design"],
  "layer_cost_usd": 1.70,
  "cumulative_cost_usd": 8.30,
  "layer_duration_ms": 48000,
  "completed_at": "2026-03-24T14:30:48.000Z"
}
```

### 8.3 Audit Query Patterns

| Query | Purpose | SQL |
|-------|---------|-----|
| Full run history | Review all events for a pipeline run | `SELECT * FROM audit_events WHERE project_id = $1 AND payload->>'run_id' = $2 ORDER BY created_at ASC` |
| Cost breakdown | See per-agent costs | `SELECT payload->>'agent_id', payload->>'cost_usd' FROM audit_events WHERE payload->>'run_id' = $1 AND payload->>'event' = 'agent_execution'` |
| Failed agents | Find failures across runs | `SELECT * FROM audit_events WHERE payload->>'quality_decision' = 'fail' ORDER BY created_at DESC LIMIT 50` |
| Retry analysis | Identify agents that frequently need retries | `SELECT payload->>'agent_id', AVG((payload->>'retry_count')::int) FROM audit_events WHERE payload->>'event' = 'agent_execution' GROUP BY payload->>'agent_id' ORDER BY avg DESC` |

---

## 9. Pipeline Execution Modes

### 9.1 Mode Definitions

| Mode | Description | Use Case | Steps Executed | Cost Estimate |
|------|-------------|----------|----------------|---------------|
| `full` | Execute all 14 agents from scratch. Ignores any existing session keys. | First-time generation, clean regeneration after major spec changes. | All 14 | $10-15 (generation) + $1.50-3.00 (quality gates) = **$12-18** |
| `resume` | Skip agents whose output keys already exist in the session store AND whose quality score was >= 0.75. Execute remaining agents. | Crash recovery, resuming after a cost breach, continuing after fixing a failed agent. | Only incomplete steps | Varies (only missing steps) |
| `regenerate` | Re-run a specific agent AND all its downstream dependents. Deletes the target agent's output key and all downstream keys before starting. | Fixing a specific document after human review, updating after prompt template changes. | Target + all downstream | Varies (target + dependents) |
| `validate-only` | Run quality gates on all existing documents without regenerating anything. Does not make LLM generation calls. | Auditing document quality, pre-merge validation, periodic health checks. | Quality gates only | $1.50-3.00 (quality gates only) |
| `dry-run` | Print the execution plan, show which agents would run, estimate costs. No LLM calls, no state changes. | Planning, cost estimation, verifying dependency graph before committing to a run. | None (plan only) | $0.00 |

### 9.2 CLI Interface

```bash
# ─────────────────────────────────────────────────
# MODE: full — Generate all 14 documents from scratch
# ─────────────────────────────────────────────────
sdlc-pipeline run \
  --mode full \
  --spec ./Requirement/MASTER-BUILD-SPEC.md \
  --output-dir ./Generated-Docs/ \
  --model claude-sonnet-4-6 \
  --cost-ceiling 25.00 \
  --per-agent-ceiling 2.00

# Output:
# [14:25:00] Pipeline started (mode=full, run_id=550e8400...)
# [14:25:01] Layer 1: D0-roadmap, D1-prd (parallel)
# [14:25:30] Layer 1 complete ($1.60, 29s)
# [14:25:31] Layer 2: D2-arch
# [14:26:10] Layer 2 complete ($1.20, 39s)
# ...
# [14:31:20] Pipeline complete. 14/14 documents generated.
# Total cost: $11.50 / $25.00 ceiling
# 2 conditional documents flagged for review: D8-design, D11-backlog


# ─────────────────────────────────────────────────
# MODE: resume — Continue a previously interrupted pipeline
# ─────────────────────────────────────────────────
sdlc-pipeline run \
  --mode resume \
  --run-id 550e8400-e29b-41d4-a716-446655440000

# Output:
# [15:00:00] Resuming run 550e8400... (mode=resume)
# [15:00:01] Checking session store for existing outputs...
# [15:00:01] Found 8/14 completed keys: roadmap_doc, prd_doc, arch_doc,
#            claude_doc, quality_doc, feature_catalog, interaction_map, mcp_tool_spec
# [15:00:01] Skipping: D0, D1, D2, D3, D4, D5, D6, D7
# [15:00:02] Layer 5 (partial): D8-design
# ...
# [15:03:45] Pipeline complete. 6 generated, 8 skipped.
# Total cost: $5.20 (this session) + $8.30 (previous) = $13.50


# ─────────────────────────────────────────────────
# MODE: regenerate — Re-run one agent + all downstream
# ─────────────────────────────────────────────────
sdlc-pipeline run \
  --mode regenerate \
  --run-id 550e8400-e29b-41d4-a716-446655440000 \
  --target D6-interaction

# Output:
# [16:00:00] Regenerate mode: target=D6-interaction
# [16:00:00] Computing downstream dependents...
# [16:00:00] Will regenerate: D6-interaction, D7-mcp, D8-design, D9-data,
#            D10-api, D11-backlog, D13-testing (7 agents)
# [16:00:00] Will preserve: D0, D1, D2, D3, D4, D5, D12 (7 agents)
# [16:00:01] Deleting session keys: interaction_map, mcp_tool_spec, design_spec,
#            data_model, api_contracts, backlog, test_strategy
# [16:00:02] Starting regeneration from D6-interaction...
# ...
# [16:05:30] Regeneration complete. 7 regenerated, 7 preserved.
# Total cost: $7.80 (this session)


# ─────────────────────────────────────────────────
# MODE: validate-only — Run quality gates on existing docs
# ─────────────────────────────────────────────────
sdlc-pipeline run \
  --mode validate-only \
  --run-id 550e8400-e29b-41d4-a716-446655440000

# Output:
# [17:00:00] Validate-only mode: checking 14 documents
# [17:00:00] D0-roadmap:    0.92 PASS
# [17:00:01] D1-prd:        0.94 PASS
# [17:00:02] D2-arch:       0.91 PASS
# [17:00:03] D3-claude:     0.88 PASS
# [17:00:04] D4-quality:    0.90 PASS
# [17:00:05] D5-features:   0.93 PASS
# [17:00:06] D6-interaction:0.95 PASS
# [17:00:07] D7-mcp:        0.91 PASS
# [17:00:08] D8-design:     0.82 CONDITIONAL ⚠
# [17:00:09] D9-data:       0.89 PASS
# [17:00:10] D10-api:       0.87 PASS
# [17:00:11] D11-backlog:   0.79 CONDITIONAL ⚠
# [17:00:12] D12-enforce:   0.90 PASS
# [17:00:13] D13-testing:   0.86 PASS
# Validation complete. 12 PASS, 2 CONDITIONAL, 0 FAIL
# Total quality gate cost: $2.10


# ─────────────────────────────────────────────────
# MODE: dry-run — Show execution plan without running
# ─────────────────────────────────────────────────
sdlc-pipeline run \
  --mode dry-run \
  --spec ./Requirement/MASTER-BUILD-SPEC.md

# Output:
# [18:00:00] DRY RUN — No LLM calls will be made
#
# Execution Plan:
# ┌─────────┬──────────────────────────┬───────────┬──────────────┐
# │ Layer   │ Agents                   │ Parallel  │ Est. Cost    │
# ├─────────┼──────────────────────────┼───────────┼──────────────┤
# │ 1       │ D0-roadmap, D1-prd       │ 2-way     │ $1.20-1.80   │
# │ 2       │ D2-arch                  │ —         │ $0.80-1.20   │
# │ 3       │ D3-claude, D4-quality,   │ 3-way     │ $1.80-2.70   │
# │         │ D5-features              │           │              │
# │ 4       │ D6-interaction           │ —         │ $1.00-1.50   │
# │ 5       │ D7-mcp, D8-design       │ 2-way     │ $1.40-2.00   │
# │ 6       │ D9-data                  │ —         │ $0.80-1.20   │
# │ 7       │ D10-api                  │ —         │ $0.80-1.20   │
# │ 8       │ D11-backlog, D12-enforce,│ 3-way     │ $1.80-2.70   │
# │         │ D13-testing              │           │              │
# ├─────────┼──────────────────────────┼───────────┼──────────────┤
# │ TOTAL   │ 14 agents, 8 layers      │           │ $9.60-14.30  │
# │ +QGates │ 14 quality gates          │           │ $1.40-2.80   │
# │ GRAND   │                           │           │ $11.00-17.10 │
# └─────────┴──────────────────────────┴───────────┴──────────────┘
#
# Estimated wall-clock time: 5-7 minutes
# Cost ceiling: $25.00 (budget remaining: $25.00)
# No state changes made.
```

### 9.3 Regeneration Cascade Logic

When regenerating a specific agent, all downstream dependents must also be regenerated to maintain consistency:

```python
def compute_regeneration_cascade(target: str) -> list[str]:
    """
    Given a target agent_id, compute all agents that must be regenerated.
    Uses reverse dependency traversal (BFS).
    """
    # Build reverse graph: who depends on me?
    reverse_graph = {agent: [] for agent in DEPENDENCY_GRAPH}
    for agent, deps in DEPENDENCY_GRAPH.items():
        for dep in deps:
            reverse_graph[dep].append(agent)

    # BFS from target
    cascade = set()
    queue = [target]
    while queue:
        current = queue.pop(0)
        if current not in cascade:
            cascade.add(current)
            queue.extend(reverse_graph.get(current, []))

    return sorted(cascade, key=lambda a: int(a.split("-")[0][1:]))  # Sort by doc number
```

**Regeneration cascade examples:**

| Target | Cascade (all agents that re-run) | Agents Preserved |
|--------|----------------------------------|------------------|
| `D0-roadmap` | D0, D3, D12 | D1, D2, D4, D5, D6, D7, D8, D9, D10, D11, D13 |
| `D1-prd` | D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D13 | D0 |
| `D2-arch` | D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D13 | D0, D1 |
| `D6-interaction` | D6, D7, D8, D9, D10, D11, D13 | D0, D1, D2, D3, D4, D5, D12 |
| `D7-mcp` | D7, D9, D10, D11, D13 | D0, D1, D2, D3, D4, D5, D6, D8, D12 |
| `D8-design` | D8, D9, D10, D11 | D0, D1, D2, D3, D4, D5, D6, D7, D12, D13 |
| `D9-data` | D9, D10, D13 | D0, D1, D2, D3, D4, D5, D6, D7, D8, D11, D12 |
| `D10-api` | D10 | All others (terminal document) |
| `D11-backlog` | D11 | All others (terminal document) |
| `D12-enforce` | D12 | All others (terminal document) |
| `D13-testing` | D13 | All others (terminal document) |

---

## 10. Cross-Reference Matrix

### 10.1 Document Dependencies

This matrix shows which upstream documents each agent reads. Use this to understand the blast radius of changes.

| Agent | raw_spec | roadmap | prd | arch | claude | quality | features | interaction | mcp_tool | design | data_model |
|-------|----------|---------|-----|------|--------|---------|----------|-------------|----------|--------|------------|
| D0-roadmap | R | **W** | | | | | | | | | |
| D1-prd | R | | **W** | | | | | | | | |
| D2-arch | | | R | **W** | | | | | | | |
| D3-claude | | R | | R | **W** | | | | | | |
| D4-quality | | | R | R | | **W** | | | | | |
| D5-features | | | R | R | | | **W** | | | | |
| D6-interaction | | | R | R | | R | R | **W** | | | |
| D7-mcp | | | | R | | R | R | R | **W** | | |
| D8-design | | | R | | | R | R | R | | **W** | |
| D9-data | | | | R | | R | R | R | R | R | **W** |
| D10-api | | | R | R | | | | R | R | R | R |
| D11-backlog | | | R | R | | R | R | R | R | R | |
| D12-enforce | | | | R | R | | | | | | |
| D13-testing | | | | R | R | R | | R | R | R | R |

Legend: **R** = reads, **W** = writes (bold)

### 10.2 Document-to-Generated-File Mapping

| Agent ID | Session Key | Generated File | Doc Number |
|----------|-------------|----------------|------------|
| D0-roadmap | `roadmap_doc` | `Generated-Docs/00-ROADMAP.md` | 00 |
| D1-prd | `prd_doc` | `Generated-Docs/01-PRD.md` | 01 |
| D2-arch | `arch_doc` | `Generated-Docs/02-ARCH.md` | 02 |
| D3-claude | `claude_doc` | `Generated-Docs/03-CLAUDE.md` | 03 |
| D4-quality | `quality_doc` | `Generated-Docs/04-QUALITY.md` | 04 |
| D5-features | `feature_catalog` | `Generated-Docs/05-FEATURE-CATALOG.md` | 05 |
| D6-interaction | `interaction_map` | `Generated-Docs/06-INTERACTION-MAP.md` | 06 |
| D7-mcp | `mcp_tool_spec` | `Generated-Docs/07-MCP-TOOL-SPEC.md` | 07 |
| D8-design | `design_spec` | `Generated-Docs/08-DESIGN-SPEC.md` | 08 |
| D9-data | `data_model` | `Generated-Docs/09-DATA-MODEL.md` | 09 |
| D10-api | `api_contracts` | `Generated-Docs/10-API-CONTRACTS.md` | 10 |
| D11-backlog | `backlog` | `Generated-Docs/11-BACKLOG.md` | 11 |
| D12-enforce | `enforcement_rules` | `Generated-Docs/12-ENFORCEMENT.md` | 12 |
| D13-testing | `test_strategy` | `Generated-Docs/13-TESTING.md` | 13 |

---

## Appendix A: Required Sections Per Agent

This lookup table is used by the Phase 1 format check to validate that each document contains its mandatory sections.

```python
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "D0-roadmap": [
        "Project Overview", "Milestones", "Timeline", "Risk Register"
    ],
    "D1-prd": [
        "Personas", "Journeys", "Capabilities", "Success Metrics"
    ],
    "D2-arch": [
        "System Context", "Container Diagram", "Shared Service Layer",
        "MCP Servers", "Data Layer", "Infrastructure"
    ],
    "D3-claude": [
        "Project Identity", "Architecture Patterns", "Code Standards",
        "File Conventions", "Interaction Protocol"
    ],
    "D4-quality": [
        "Non-Functional Requirements", "Performance", "Security",
        "Reliability", "MCP-Dashboard Parity"
    ],
    "D5-features": [
        "Feature Registry", "Feature Details", "Interface Mapping",
        "Priority Matrix"
    ],
    "D6-interaction": [
        "Interaction Registry", "Data Shapes", "Cross-Interface Journeys",
        "Parity Matrix"
    ],
    "D7-mcp": [
        "Server Registry", "Tool Specifications", "Input Schemas",
        "Output Schemas", "Error Catalog"
    ],
    "D8-design": [
        "Screen Inventory", "Screen Specifications", "Component Library",
        "Navigation", "Responsive Behavior"
    ],
    "D9-data": [
        "Table Summary", "Schema DDL", "Indexes", "Row-Level Security",
        "Migration Strategy"
    ],
    "D10-api": [
        "Endpoint Registry", "Request/Response Schemas", "Authentication",
        "Error Responses", "Rate Limiting"
    ],
    "D11-backlog": [
        "Epic Registry", "Story Details", "Acceptance Criteria",
        "Sprint Plan", "Priority"
    ],
    "D12-enforce": [
        "Rule Registry", "Enforcement Mechanisms", "Violation Handling",
        "Integration Points"
    ],
    "D13-testing": [
        "Test Strategy", "Test Categories", "Coverage Requirements",
        "Cross-Interface Tests", "CI/CD Integration"
    ],
}
```

---

## Appendix B: Configuration Defaults

```yaml
# sdlc-pipeline.yaml — Default pipeline configuration
pipeline:
  model: claude-sonnet-4-6
  max_tokens: 16000
  temperature: 0.2
  cost_ceiling_usd: 25.00
  per_agent_ceiling_usd: 2.00
  max_retries: 2
  timeout_seconds: 120

quality_gate:
  pass_threshold: 0.85
  conditional_threshold: 0.75
  judge_model: claude-sonnet-4-6
  judge_max_tokens: 4000
  judge_temperature: 0.0

session_store:
  default_ttl_seconds: 86400
  cleanup_interval_seconds: 3600

database:
  host: localhost
  port: 5432
  database: agentic_sdlc
  pool_min: 2
  pool_max: 10

output:
  dir: ./Generated-Docs/
  commit_format: "docs: generate {NN}-{DOC} using Full-Stack-First approach"
```

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **Agent** | An LLM-powered document generator that reads input documents and produces one output document following a prompt template. |
| **Envelope** | The JSON message structure used to invoke an agent. Contains run context, input references, output key, and configuration. |
| **Layer** | A group of agents that can execute in parallel because none depend on each other. |
| **Orchestrator** | The pipeline controller that sequences agent execution, manages state, enforces cost ceilings, and runs quality gates. |
| **Quality Gate** | A two-phase validation (format check + rubric scoring) that every agent output must pass before being stored. |
| **Run** | A single execution of the pipeline, identified by a UUID. All session keys and audit events are scoped to a run. |
| **Session Key** | A named slot in the session context store (e.g., `prd_doc`, `arch_doc`). Each key has exactly one writer agent. |
| **Session Store** | The PostgreSQL-backed key-value store (`session_context` table) used for inter-agent context passing. |
| **Cascade** | The set of agents that must be regenerated when a single agent's output changes (the target plus all downstream dependents). |
| **The Full-Stack-First Sprint** | Layer 5, where D7-mcp and D8-design execute in parallel. This is the defining characteristic of the Full-Stack-First approach. |

---

*End of document. This protocol governs the meta-pipeline that generates SDLC specification documents. For the runtime agent protocol (48 agents across 7 SDLC phases), see the ARCH (Doc 02) and MCP-TOOL-SPEC (Doc 07).*
