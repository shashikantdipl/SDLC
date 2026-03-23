# 08-BACKLOG.md --- Sprint Backlog (BACKLOG.json)

| Field | Value |
|---|---|
| **Document** | BACKLOG-001 |
| **Title** | Agentic SDLC Platform --- Sprint Backlog |
| **Version** | 1.0.0 |
| **Date** | 2026-03-23 |
| **Status** | Draft |
| **Owner** | David Chen (Delivery Lead) |
| **Reviewers** | Priya Mehta (Platform Engineer), Sarah Kim (Engineering Lead), Marcus Johnson (DevOps), Lisa Patel (Compliance Officer) |
| **Capacity** | 40 story points per sprint, 2-week sprints, 2-3 developers |
| **Total Stories** | 82 |
| **Total Story Points** | 327 |

---

## 1. Sprint Plan Summary

| Sprint | Theme | Story Points | Stories |
|---|---|---|---|
| Sprint 1 | Foundation: Migrations, Stores, Validation | 39 | S-001 to S-010 |
| Sprint 2 | Safety: Approvals, Checkpoints, Rate Limiting | 40 | S-011 to S-020 |
| Sprint 3 | Core Agents I: Pipeline DAG, Doc Agents D1-D6 | 39 | S-021 to S-030 |
| Sprint 4 | Core Agents II: Doc Agents D7-D11, Prompt Completion | 38 | S-031 to S-040 |
| Sprint 5 | Build Phase Agents & Quality Scoring | 40 | S-041 to S-052 |
| Sprint 6 | Fleet Testing, Knowledge Base, Remaining Agents | 39 | S-053 to S-063 |
| Sprint 7 | Observability, Dashboard, Multi-Project | 38 | S-064 to S-074 |
| Sprint 8 | Agent Lifecycle, Enhancements, Hardening | 33 | S-075 to S-082 |

---

## 2. Backlog (BACKLOG.json)

```json
{
  "version": "1.0.0",
  "generated_from": "FEATURE-CATALOG.md + QUALITY.md + PRD.md",
  "total_stories": 82,
  "total_story_points": 327,
  "sprint_capacity": 40,
  "sprint_duration_weeks": 2,
  "team_size": "2-3 developers",
  "sprints": {
    "sprint_1": {
      "theme": "Foundation: Migrations, Stores, Validation",
      "target_points": 39,
      "stories": ["S-001","S-002","S-003","S-004","S-005","S-006","S-007","S-008","S-009","S-010"]
    },
    "sprint_2": {
      "theme": "Safety: Approvals, Checkpoints, Rate Limiting",
      "target_points": 40,
      "stories": ["S-011","S-012","S-013","S-014","S-015","S-016","S-017","S-018","S-019","S-020"]
    },
    "sprint_3": {
      "theme": "Core Agents I: Pipeline DAG, Doc Agents D1-D6",
      "target_points": 39,
      "stories": ["S-021","S-022","S-023","S-024","S-025","S-026","S-027","S-028","S-029","S-030"]
    },
    "sprint_4": {
      "theme": "Core Agents II: Doc Agents D7-D11, Prompt Completion",
      "target_points": 38,
      "stories": ["S-031","S-032","S-033","S-034","S-035","S-036","S-037","S-038","S-039","S-040"]
    },
    "sprint_5": {
      "theme": "Build Phase Agents & Quality Scoring",
      "target_points": 40,
      "stories": ["S-041","S-042","S-043","S-044","S-045","S-046","S-047","S-048","S-049","S-050","S-051","S-052"]
    },
    "sprint_6": {
      "theme": "Fleet Testing, Knowledge Base, Remaining Agents",
      "target_points": 39,
      "stories": ["S-053","S-054","S-055","S-056","S-057","S-058","S-059","S-060","S-061","S-062","S-063"]
    },
    "sprint_7": {
      "theme": "Observability, Dashboard, Multi-Project",
      "target_points": 38,
      "stories": ["S-064","S-065","S-066","S-067","S-068","S-069","S-070","S-071","S-072","S-073","S-074"]
    },
    "sprint_8": {
      "theme": "Agent Lifecycle, Enhancements, Hardening",
      "target_points": 33,
      "stories": ["S-075","S-076","S-077","S-078","S-079","S-080","S-081","S-082"]
    }
  },
  "stories": [

    {
      "id": "S-001",
      "feature_ref": "F-046",
      "epic": "E8",
      "sprint": 1,
      "priority": "must",
      "story_points": 3,
      "title": "Create PostgreSQL migrations 005-006 for session_context and cost_metrics tables",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "idempotent database migrations that create the session_context and cost_metrics tables with rollback scripts",
      "so_that": "all downstream stores (SessionStore, CostStore) have a reliable schema foundation and the team can deploy database changes safely across environments",
      "acceptance_criteria": [
        "Given a fresh database with migrations 001-004 applied, When migration 005 runs, Then the session_context table is created with columns: id, session_id, key, value, project_id, created_at, updated_at, expires_at",
        "Given a fresh database with migration 005 applied, When migration 006 runs, Then the cost_metrics table is created with columns: id, invocation_id, agent_id, session_id, project_id, input_tokens, output_tokens, model, unit_cost, cost_usd, created_at",
        "Given a database where migrations 005-006 have already been applied, When the migrations run again, Then they complete without error (idempotent)"
      ],
      "dependencies": []
    },

    {
      "id": "S-002",
      "feature_ref": "F-046",
      "epic": "E8",
      "sprint": 1,
      "priority": "must",
      "story_points": 3,
      "title": "Create PostgreSQL migrations 007-008 for audit_events and approval_requests tables",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "idempotent database migrations that create the audit_events table with an immutability trigger and the approval_requests table",
      "so_that": "the audit trail is immutable from day one and approval workflows have persistent storage",
      "acceptance_criteria": [
        "Given migration 007 is applied, When an UPDATE or DELETE is attempted on audit_events, Then a PostgreSQL trigger raises an exception blocking the operation (Q-033)",
        "Given migration 008 is applied, Then the approval_requests table exists with columns: id, pipeline_run_id, step_name, requester, approver, status, decision, comments, created_at, decided_at",
        "Given migrations 007-008 have already been applied, When they run again, Then they complete without error (idempotent)"
      ],
      "dependencies": []
    },

    {
      "id": "S-003",
      "feature_ref": "F-001",
      "epic": "E1",
      "sprint": 1,
      "priority": "must",
      "story_points": 5,
      "title": "Implement BaseAgent abstract class with lifecycle hooks",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "an abstract BaseAgent class providing pre_invoke, invoke, and post_invoke hooks with manifest-driven configuration and typed input/output contracts",
      "so_that": "all 48 agents inherit a consistent execution lifecycle and I can build new agents rapidly without duplicating boilerplate",
      "acceptance_criteria": [
        "Given a valid agent manifest YAML, When BaseAgent is subclassed and instantiated, Then pre_invoke, invoke, and post_invoke execute in sequence with typed inputs and outputs",
        "Given an agent subclass that raises an exception in invoke, When the agent is called, Then post_invoke still executes for cleanup and the error is propagated with structured context",
        "Given an agent invocation, When execution completes, Then duration_ms is recorded and available for audit logging (Q-028)"
      ],
      "dependencies": ["S-001"]
    },

    {
      "id": "S-004",
      "feature_ref": "F-001",
      "epic": "E1",
      "sprint": 1,
      "priority": "must",
      "story_points": 3,
      "title": "Implement BaseAgent cost metering and audit hooks in post_invoke",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "BaseAgent post_invoke to automatically record cost metrics (input_tokens, output_tokens, cost_usd) and emit a structured audit event",
      "so_that": "every agent invocation is metered and auditable without requiring individual agents to implement cost tracking",
      "acceptance_criteria": [
        "Given an agent invocation that consumes tokens, When post_invoke runs, Then a cost record is emitted with input_tokens, output_tokens, model, and cost_usd fields (Q-029)",
        "Given an agent invocation, When post_invoke runs, Then a 13-field audit event is emitted containing all required fields (Q-028)",
        "Given a BaseAgent with no secrets in output, When the output PII scanner runs in post_invoke, Then it passes with zero detections (Q-013)"
      ],
      "dependencies": ["S-003"]
    },

    {
      "id": "S-005",
      "feature_ref": "F-002",
      "epic": "E1",
      "sprint": 1,
      "priority": "must",
      "story_points": 5,
      "title": "Implement ManifestLoader with JSON Schema validation",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a ManifestLoader that reads agent manifest YAML files, validates them against a JSON Schema, resolves environment variable references, and returns typed ManifestConfig dataclasses",
      "so_that": "agent configuration is validated at load time and manifest drift between code and config is caught before runtime",
      "acceptance_criteria": [
        "Given a valid agent manifest YAML with all required fields, When ManifestLoader.load() is called, Then it returns a typed ManifestConfig dataclass with all fields populated",
        "Given an invalid manifest missing required fields, When ManifestLoader.load() is called, Then it raises a ValidationError listing all missing or invalid fields",
        "Given a manifest with ${ENV_VAR} references, When ManifestLoader.load() is called, Then environment variables are resolved before validation and the resolved values appear in ManifestConfig",
        "Given any single manifest file, When ManifestLoader.validate() is called, Then it completes in less than 200ms (Q-005)"
      ],
      "dependencies": []
    },

    {
      "id": "S-006",
      "feature_ref": "F-003",
      "epic": "E1",
      "sprint": 1,
      "priority": "must",
      "story_points": 5,
      "title": "Implement SchemaValidator for agent input/output contracts",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "a SchemaValidator that validates agent inputs and outputs against JSON Schema definitions declared in each agent's manifest",
      "so_that": "malformed data is caught at agent boundaries rather than propagating through the pipeline and corrupting downstream outputs",
      "acceptance_criteria": [
        "Given an agent output that matches its declared output schema, When SchemaValidator.validate() is called, Then it returns the validated data without error",
        "Given an agent output that violates its declared schema (wrong type, missing field), When SchemaValidator.validate() is called, Then it raises a ValidationError with field-level details listing every violation",
        "Given validation wired into BaseAgent, When an agent returns invalid output, Then the invocation fails with a structured error before the output reaches SessionStore (Q-013)"
      ],
      "dependencies": ["S-005"]
    },

    {
      "id": "S-007",
      "feature_ref": "F-004",
      "epic": "E1",
      "sprint": 1,
      "priority": "must",
      "story_points": 5,
      "title": "Implement SessionStore read/write/delete with asyncpg",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a persistent key-value SessionStore backed by the PostgreSQL session_context table that supports async get, set, and delete operations",
      "so_that": "agents can share context (e.g., generated PRD, client brief) across pipeline steps without losing data on process restarts",
      "acceptance_criteria": [
        "Given a session_id and key, When SessionStore.set(session_id, key, value) is called followed by SessionStore.get(session_id, key), Then the original value is returned",
        "Given a stored key, When SessionStore.delete(session_id, key) is called, Then subsequent get returns None",
        "Given 1000 read/write cycles, When measured at the asyncpg call boundary, Then p95 latency is below 50ms (Q-004)",
        "Given a session_context entry with TTL=1s, When 2 seconds elapse and cleanup runs, Then the entry is deleted (Q-034)"
      ],
      "dependencies": ["S-001"]
    },

    {
      "id": "S-008",
      "feature_ref": "F-004",
      "epic": "E1",
      "sprint": 1,
      "priority": "must",
      "story_points": 3,
      "title": "Implement SessionStore TTL enforcement and batch cleanup",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a scheduled cleanup job that purges expired session_context entries in batches of 1000 rows without locking the table for more than 1 second",
      "so_that": "stale session data does not accumulate and degrade database performance over time",
      "acceptance_criteria": [
        "Given entries with configurable TTL (default 86400s), When the hourly cleanup job runs, Then all expired entries are deleted (Q-034)",
        "Given a batch of 5000 expired entries, When cleanup runs, Then deletions occur in batches of 1000 and the table is not locked for more than 1 second per batch (Q-034)",
        "Given the cleanup job, When it completes, Then it emits metrics session_cleanup_rows_deleted and session_cleanup_duration_ms"
      ],
      "dependencies": ["S-007"]
    },

    {
      "id": "S-009",
      "feature_ref": "F-005",
      "epic": "E1",
      "sprint": 1,
      "priority": "must",
      "story_points": 5,
      "title": "Build Envelope-based message creation and routing between agents",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a typed Envelope dataclass system for agent-to-agent communication over asyncio queues, containing sender, recipient, payload, correlation_id, and timestamp",
      "so_that": "agent communication is traceable via correlation_id and messages are delivered reliably within the pipeline",
      "acceptance_criteria": [
        "Given an Envelope created with sender=agent_A and recipient=agent_B, When it is dispatched, Then agent_B receives the Envelope within 100ms on the same asyncio event loop with all fields intact",
        "Given an Envelope, When it is serialized, Then it contains correlation_id that matches the pipeline run's correlation_id for end-to-end tracing (Q-030)",
        "Given an Envelope routed to a non-existent agent, When dispatch is attempted, Then a RoutingError is raised with the missing agent ID"
      ],
      "dependencies": ["S-003"]
    },

    {
      "id": "S-010",
      "feature_ref": "F-024",
      "epic": "E3",
      "sprint": 1,
      "priority": "must",
      "story_points": 5,
      "title": "Implement PostgresCostStore with fail-safe cost recording",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "a PostgresCostStore that records cost per invocation to the cost_metrics table and blocks invocations when the cost-tracking database is unreachable",
      "so_that": "no agent invocation runs unmetered and cost data is always available for budget enforcement",
      "acceptance_criteria": [
        "Given an agent invocation, When PostgresCostStore.record() is called, Then a row is inserted into cost_metrics with input_tokens, output_tokens, model, unit_cost, and cost_usd",
        "Given the cost-tracking database is unreachable, When an agent invocation is attempted, Then it is blocked with a CostStoreUnavailable error rather than proceeding unmetered",
        "Given recorded cost data, When PostgresCostStore.get_cumulative(session_id) is called, Then it returns the correct sum of cost_usd for that session (Q-029)"
      ],
      "dependencies": ["S-001"]
    },

    {
      "id": "S-011",
      "feature_ref": "F-024",
      "epic": "E3",
      "sprint": 2,
      "priority": "must",
      "story_points": 3,
      "title": "Implement pre-invocation cost projection and ceiling enforcement in CostStore",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "PostgresCostStore to estimate the cost of the next invocation before it executes and raise CostLimitExceeded if the projected cumulative cost exceeds the configured ceiling",
      "so_that": "budget overruns are prevented proactively rather than detected after the money is spent",
      "acceptance_criteria": [
        "Given a session with $24 cumulative spend and a $25 ceiling, When an invocation with estimated cost $2 is attempted, Then CostLimitExceeded is raised before the LLM call",
        "Given a session with $20 cumulative spend and a $25 ceiling, When an invocation with estimated cost $1 is attempted, Then the invocation proceeds normally",
        "Given cost projection, When the estimate is compared against actual post-invocation cost, Then the estimate is accurate to within 20% (Q-029)"
      ],
      "dependencies": ["S-010"]
    },

    {
      "id": "S-012",
      "feature_ref": "F-025",
      "epic": "E3",
      "sprint": 2,
      "priority": "must",
      "story_points": 8,
      "title": "Implement CostController with 4-level budget enforcement",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "a CostController that enforces budget limits at four levels (per-invocation $0.50, per-session/agent $5/day, per-project $20/day, fleet $50/day) with warn and hard thresholds",
      "so_that": "cost spikes are contained at the narrowest scope possible and fleet-wide budget is never exceeded",
      "acceptance_criteria": [
        "Given a single invocation costing $0.60, When CostController evaluates it, Then the invocation is blocked because it exceeds the per-invocation $0.50 hard limit (Q-032)",
        "Given project daily spend at $16 (80% of $20 ceiling), When CostController evaluates, Then a warning event is emitted but the invocation proceeds",
        "Given fleet daily spend at $50, When any invocation is attempted, Then CostController blocks it with a clear message indicating the fleet ceiling is reached (Q-032)",
        "Given any budget threshold breach, When CostController detects it, Then an alert is emitted within 60 seconds (Q-032)"
      ],
      "dependencies": ["S-010", "S-011"]
    },

    {
      "id": "S-013",
      "feature_ref": "F-029",
      "epic": "E4",
      "sprint": 2,
      "priority": "must",
      "story_points": 5,
      "title": "Implement ApprovalStore for gate management",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "a persistent ApprovalStore backed by the PostgreSQL approval_requests table that tracks gate creation, pending status, approver decisions, timestamps, and comments",
      "so_that": "approval gate state is durable across platform restarts and every approval decision is auditable",
      "acceptance_criteria": [
        "Given a pipeline at an approval gate step, When ApprovalStore.create_request() is called, Then a row is inserted with status=pending and a unique request ID is returned",
        "Given a pending approval request, When ApprovalStore.decide(request_id, approve, approver, comment) is called, Then the row is updated with status=approved, the approver name, and the decision timestamp",
        "Given a decided approval request, When the audit log is queried, Then the decision is recorded as an immutable audit event (Q-033)"
      ],
      "dependencies": ["S-002"]
    },

    {
      "id": "S-014",
      "feature_ref": "F-030",
      "epic": "E4",
      "sprint": 2,
      "priority": "must",
      "story_points": 5,
      "title": "Build approval gate integration in PipelineRunner",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "the PipelineRunner to pause execution at configured approval gate steps, create an approval request via ApprovalStore, and resume or abort based on the human decision",
      "so_that": "critical pipeline outputs like architecture documents are reviewed by a human before downstream agents consume them",
      "acceptance_criteria": [
        "Given a pipeline step marked as an approval gate, When the PipelineRunner reaches that step, Then execution pauses and an approval request is created in ApprovalStore",
        "Given a pending approval gate, When the approver submits 'approve', Then the pipeline resumes within 10 seconds of the decision",
        "Given a pending approval gate, When the approver submits 'reject', Then the pipeline is aborted and the rejection reason is recorded in the audit trail (Q-033)"
      ],
      "dependencies": ["S-013"]
    },

    {
      "id": "S-015",
      "feature_ref": "F-031",
      "epic": "E4",
      "sprint": 2,
      "priority": "must",
      "story_points": 5,
      "title": "Implement Slack notification for approval gates",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "interactive Slack messages sent when an approval gate is triggered, containing pipeline context, artifact summary, and approve/reject action buttons",
      "so_that": "I can review and approve agent outputs without leaving Slack and the team gets immediate visibility into pending gates",
      "acceptance_criteria": [
        "Given an approval gate is triggered, When the Slack notification is sent, Then it arrives within 5 seconds and includes pipeline name, step name, artifact summary, and approve/reject buttons",
        "Given a Slack message with approve/reject buttons, When I click approve, Then ApprovalStore is updated and the pipeline resumes within 10 seconds",
        "Given a Slack notification failure (5xx), When delivery fails, Then the system retries up to 3 times with exponential backoff"
      ],
      "dependencies": ["S-013"]
    },

    {
      "id": "S-016",
      "feature_ref": "F-045",
      "epic": "E8",
      "sprint": 2,
      "priority": "must",
      "story_points": 5,
      "title": "Implement PipelineCheckpoint save and load operations",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "the pipeline to save a checkpoint (step results, SessionStore snapshot, cost accumulator) after each completed step so that execution can resume from the last successful step after a failure",
      "so_that": "a pipeline that fails at step 7 does not need to re-run steps 1-6, saving time and money",
      "acceptance_criteria": [
        "Given a 12-step pipeline, When step 5 completes successfully, Then a checkpoint is persisted containing results for steps 1-5, the SessionStore snapshot, and the cumulative cost",
        "Given a persisted checkpoint for steps 1-6, When PipelineCheckpoint.load(pipeline_run_id) is called, Then all 6 step results and the SessionStore snapshot are restored correctly",
        "Given a pipeline failure at step 7, When resume is triggered, Then execution begins at step 7 with steps 1-6 results loaded from checkpoint (Q-008)"
      ],
      "dependencies": ["S-007"]
    },

    {
      "id": "S-017",
      "feature_ref": "F-045",
      "epic": "E8",
      "sprint": 2,
      "priority": "must",
      "story_points": 3,
      "title": "Implement checkpoint resume logic in PipelineRunner",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "the PipelineRunner to detect a failed run with a valid checkpoint and resume from the last successful step within 60 seconds of a platform restart",
      "so_that": "transient failures do not waste the budget and time already spent on completed steps",
      "acceptance_criteria": [
        "Given a pipeline run that failed at step 7 with a valid checkpoint, When PipelineRunner.resume() is called, Then execution starts at step 7 without re-executing steps 1-6 (Q-008)",
        "Given a platform restart with a pending checkpoint, When the orchestrator initializes, Then it detects and resumes the paused pipeline within 60 seconds (Q-008)",
        "Given a resumed pipeline, When it completes, Then no duplicate agent invocations exist in the audit trail"
      ],
      "dependencies": ["S-016"]
    },

    {
      "id": "S-018",
      "feature_ref": "F-026",
      "epic": "E3",
      "sprint": 2,
      "priority": "must",
      "story_points": 5,
      "title": "Build TokenBucketRateLimiter for API and agent calls",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "a token-bucket rate limiter that throttles agent invocations per-agent and per-project with configurable burst and sustained rates",
      "so_that": "runaway retry loops and API abuse are prevented before they cause cost spikes",
      "acceptance_criteria": [
        "Given a rate limiter configured with burst=10 and sustained=5/s, When 11 requests arrive within 1 second, Then the 11th request is rejected with a RetryAfter header",
        "Given a rejected request, When the RetryAfter wait time elapses, Then the next request is accepted",
        "Given per-agent and per-project rate limits, When both apply to the same request, Then the stricter limit takes precedence"
      ],
      "dependencies": []
    },

    {
      "id": "S-019",
      "feature_ref": "F-027",
      "epic": "E3",
      "sprint": 2,
      "priority": "should",
      "story_points": 5,
      "title": "Implement CircuitBreaker for external service calls",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "a circuit breaker that tracks failure rates for Claude API, Slack, and PagerDuty calls, opens after 3 consecutive failures, and attempts half-open probes after a cooldown",
      "so_that": "cascading failures from external service outages are contained and the platform degrades gracefully",
      "acceptance_criteria": [
        "Given 3 consecutive 503 responses from Claude API, When the circuit breaker evaluates, Then it opens within 5 seconds and rejects subsequent calls with CircuitOpenError (Q-009)",
        "Given an open circuit breaker with 30-second cooldown, When 30 seconds elapse, Then a single probe call is allowed through (half-open state) (Q-009)",
        "Given a successful probe call, When the circuit breaker evaluates, Then it closes and normal traffic resumes",
        "Given circuit state transitions, When any transition occurs, Then metric circuit_breaker_state is emitted (Q-009)"
      ],
      "dependencies": []
    },

    {
      "id": "S-020",
      "feature_ref": "F-032",
      "epic": "E4",
      "sprint": 2,
      "priority": "should",
      "story_points": 5,
      "title": "Implement autonomy tiers T0-T3 in agent execution",
      "as_a": "Lisa Patel, Compliance Officer",
      "i_want": "agents to be configurable with autonomy tiers T0 (fully autonomous), T1 (log only), T2 (approval required, auto-approve after timeout), and T3 (approval required, block until human)",
      "so_that": "sensitive operations always require human oversight while routine tasks run without friction",
      "acceptance_criteria": [
        "Given a T0 agent, When invoked, Then it executes without any approval gate pause",
        "Given a T3 agent, When invoked, Then it blocks indefinitely at its approval gate until a human responds",
        "Given a T2 agent with 15-minute timeout, When no human responds within 15 minutes, Then the gate auto-approves and execution continues",
        "Given T0 agent tool permissions, When the agent attempts to invoke Bash or file_write, Then the call is blocked and logged (Q-018)"
      ],
      "dependencies": ["S-013", "S-014"]
    },

    {
      "id": "S-021",
      "feature_ref": "F-006",
      "epic": "E1",
      "sprint": 3,
      "priority": "must",
      "story_points": 8,
      "title": "Build PipelineRunner sequential DAG execution engine",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a PipelineRunner that executes a pipeline defined as a directed acyclic graph of agent steps, supporting sequential ordering with result passing between steps",
      "so_that": "document generation pipelines can execute agents in dependency order with each step receiving upstream outputs as context",
      "acceptance_criteria": [
        "Given a DAG with 5 sequential steps, When PipelineRunner.execute() is called, Then steps execute in dependency order with each step receiving the previous step's output",
        "Given a pipeline execution, When all steps complete, Then pipeline_runs.status is set to 'completed' and step_durations JSONB contains timing for every step (Q-031)",
        "Given a pipeline execution, When it completes, Then total wall-clock time is under 30 minutes for a 12-step pipeline with no human gates (Q-002)"
      ],
      "dependencies": ["S-003", "S-007", "S-009"]
    },

    {
      "id": "S-022",
      "feature_ref": "F-048",
      "epic": "E8",
      "sprint": 3,
      "priority": "must",
      "story_points": 5,
      "title": "Implement parallel DAG execution with fan-out/fan-in",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "PipelineRunner to execute independent DAG branches in parallel using asyncio.gather with fan-out distribution and fan-in result merging",
      "so_that": "pipelines with parallel branches (e.g., Data Model and API Contracts) run concurrently to minimize total pipeline duration",
      "acceptance_criteria": [
        "Given a DAG with two independent branches, When PipelineRunner executes them, Then both branches run concurrently (verified by overlapping timestamps)",
        "Given parallel branches, When both complete, Then their results are correctly merged at the fan-in point before the next sequential step",
        "Given a parallel branch failure, When one branch fails, Then the other branch is allowed to complete and the failure is reported for the failed branch only"
      ],
      "dependencies": ["S-021"]
    },

    {
      "id": "S-023",
      "feature_ref": "F-009",
      "epic": "E2",
      "sprint": 3,
      "priority": "must",
      "story_points": 5,
      "title": "Define the 12-document pipeline DAG with approval gates",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "the full 12-document generation pipeline defined as a DAG: Roadmap -> CLAUDE.md -> PRD -> Feature Catalog -> Backlog -> Architecture -> (Data Model || API Contracts) -> Enforcement Scaffold -> (Quality Spec || Test Strategy) -> Design Spec",
      "so_that": "I can trigger a complete document set generation from a single client brief and get all 12 documents in the correct dependency order",
      "acceptance_criteria": [
        "Given a valid client brief, When the 12-document pipeline is triggered, Then a pipeline_run is created with 12 steps in the correct dependency order including 2 parallel pairs",
        "Given the pipeline DAG, When architecture step completes, Then an approval gate fires before Data Model and API Contracts steps begin",
        "Given the pipeline configuration, When a $25 cost ceiling is set, Then CostController enforces it across all 12 steps (Q-032)"
      ],
      "dependencies": ["S-021", "S-022", "S-014"]
    },

    {
      "id": "S-024",
      "feature_ref": "F-010",
      "epic": "E2",
      "sprint": 3,
      "priority": "must",
      "story_points": 5,
      "title": "Implement Roadmap generation agent (D1)",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "an agent that produces the 00-ROADMAP.md document from a client brief, extracting milestones, phases, timelines, and dependencies",
      "so_that": "the first document in the pipeline establishes the project timeline that all downstream documents reference",
      "acceptance_criteria": [
        "Given a client brief, When the Roadmap agent executes, Then it produces a markdown document with at least 3 milestones each with timeline and dependency list",
        "Given the Roadmap agent output, When scored against its rubric, Then it achieves >= 8.0/10 on completeness, accuracy, and formatting dimensions",
        "Given the Roadmap agent, When invoked, Then its p95 latency is under 30s for haiku-tier or 120s for opus-tier (Q-001)"
      ],
      "dependencies": ["S-003", "S-007"]
    },

    {
      "id": "S-025",
      "feature_ref": "F-013",
      "epic": "E2",
      "sprint": 3,
      "priority": "must",
      "story_points": 3,
      "title": "Implement CLAUDE.md generation agent (D2)",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "an agent that produces the 03-CLAUDE.md enforcement scaffold defining coding standards, file conventions, testing mandates, and AI-specific constraints",
      "so_that": "the project has enforceable AI coding standards from the start that downstream agents and humans follow",
      "acceptance_criteria": [
        "Given brief and roadmap from SessionStore, When the CLAUDE.md agent executes, Then it produces a document with at least 10 enforceable rules covering naming, testing, and file structure",
        "Given the CLAUDE.md agent output, When validated against its output schema, Then all required sections are present",
        "Given the agent output, When PII scanning runs, Then zero secrets or PII are detected (Q-013)"
      ],
      "dependencies": ["S-024"]
    },

    {
      "id": "S-026",
      "feature_ref": "F-011",
      "epic": "E2",
      "sprint": 3,
      "priority": "must",
      "story_points": 5,
      "title": "Implement PRD generation agent (D3)",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "an agent that produces the 01-PRD.md document with problem statement, personas, capabilities, success metrics, and user journeys derived from the client brief and roadmap",
      "so_that": "the product requirements are formally documented and traceable to the original client brief",
      "acceptance_criteria": [
        "Given brief and roadmap from SessionStore, When the PRD agent executes, Then it produces a document with problem statement, at least 3 personas, at least 5 capabilities, and success metrics",
        "Given the PRD agent output, When cross-referenced with the client brief, Then every capability traces back to a stated client need",
        "Given the PRD agent output, When scored against its rubric, Then it achieves >= 8.0/10"
      ],
      "dependencies": ["S-025"]
    },

    {
      "id": "S-027",
      "feature_ref": "F-014",
      "epic": "E2",
      "sprint": 3,
      "priority": "must",
      "story_points": 5,
      "title": "Implement Feature Catalog generation agent (D4)",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "an agent that extracts features from PRD capabilities and produces a JSON feature catalog with story points, priorities, dependencies, and acceptance criteria",
      "so_that": "product capabilities are decomposed into implementable features with clear scope and effort estimates",
      "acceptance_criteria": [
        "Given a PRD from SessionStore, When the Feature Catalog agent executes, Then it produces valid JSON with at least one feature per PRD capability",
        "Given the feature catalog output, When validated, Then all features have required fields: id, epic, name, priority, story_points, dependencies, acceptance",
        "Given the feature IDs, When inspected, Then they are sequential (F-001, F-002, ...) with no gaps"
      ],
      "dependencies": ["S-026"]
    },

    {
      "id": "S-028",
      "feature_ref": "F-015",
      "epic": "E2",
      "sprint": 3,
      "priority": "must",
      "story_points": 3,
      "title": "Implement Backlog generation agent (D5)",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "an agent that decomposes features from the Feature Catalog into actionable backlog items with sprint assignments, effort estimates, and dependency ordering",
      "so_that": "the development team has a ready-to-execute sprint plan traceable to product features",
      "acceptance_criteria": [
        "Given a Feature Catalog from SessionStore, When the Backlog agent executes, Then every feature is represented by at least one backlog item",
        "Given backlog items, When inspected, Then each has: id, feature_ref, sprint, story_points (max 8), title, acceptance_criteria, and dependencies",
        "Given the backlog output, When story points are summed per sprint, Then no sprint exceeds 40 points"
      ],
      "dependencies": ["S-027"]
    },

    {
      "id": "S-029",
      "feature_ref": "F-012",
      "epic": "E2",
      "sprint": 3,
      "priority": "must",
      "story_points": 5,
      "title": "Implement Architecture document generation agent (D6)",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "an agent that produces the 02-ARCH.md document with C4 diagrams (context, container, component), technology choices, data flow, and deployment topology",
      "so_that": "the system architecture is documented at multiple abstraction levels and every PRD capability maps to an architectural component",
      "acceptance_criteria": [
        "Given PRD and brief from SessionStore, When the Architecture agent executes, Then it produces C4 context, container, and component diagrams",
        "Given the architecture output, When cross-referenced with the PRD, Then every capability (C1-Cn) maps to at least one architectural component",
        "Given the architecture output, When scored against its rubric, Then it achieves >= 8.0/10 on completeness and technical accuracy"
      ],
      "dependencies": ["S-026"]
    },

    {
      "id": "S-030",
      "feature_ref": "F-037",
      "epic": "E6",
      "sprint": 3,
      "priority": "must",
      "story_points": 5,
      "title": "Implement 13-field JSONL audit event logging",
      "as_a": "Lisa Patel, Compliance Officer",
      "i_want": "every agent invocation to produce an immutable JSONL audit record with 13 fields written to both a file and the PostgreSQL audit_events table within the same transaction",
      "so_that": "I can reconstruct the complete history of every agent action for quarterly compliance reviews",
      "acceptance_criteria": [
        "Given an agent invocation, When it completes, Then a JSONL line and a database row are written with all 13 fields: timestamp, event_id, agent_id, agent_version, session_id, project_id, phase, action, input_hash, output_hash, cost_usd, latency_ms, status (Q-028)",
        "Given an audit_events row, When an UPDATE or DELETE is attempted, Then the immutability trigger raises an exception (Q-033)",
        "Given a pipeline run of 12 agents, When audited, Then the count of audit_events rows equals the count of invocations (Q-028)"
      ],
      "dependencies": ["S-002", "S-003"]
    },

    {
      "id": "S-031",
      "feature_ref": "F-016",
      "epic": "E2",
      "sprint": 4,
      "priority": "must",
      "story_points": 5,
      "title": "Implement Data Model generation agent (D7)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "an agent that produces the 07-DATA-MODEL.md document with entity-relationship diagrams, table DDLs, index strategies, and migration scripts derived from the Architecture document",
      "so_that": "the database schema is formally documented and implementation-ready with correct relationships and indexes",
      "acceptance_criteria": [
        "Given Architecture and PRD from SessionStore, When the Data Model agent executes, Then it produces DDL for all tables referenced in the Architecture document",
        "Given the DDL output, When inspected, Then every table has primary keys, foreign keys, and at least one index",
        "Given the Data Model output, When run as SQL against a test database, Then all tables are created without error"
      ],
      "dependencies": ["S-029"]
    },

    {
      "id": "S-032",
      "feature_ref": "F-017",
      "epic": "E2",
      "sprint": 4,
      "priority": "must",
      "story_points": 5,
      "title": "Implement API Contracts generation agent (D8)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "an agent that produces the 09-API-CONTRACTS.md document with OpenAPI 3.1 endpoint definitions, request/response schemas, error codes, and authentication requirements",
      "so_that": "API contracts are defined upfront and backend/frontend teams can develop against a shared specification",
      "acceptance_criteria": [
        "Given Architecture and PRD from SessionStore, When the API Contracts agent executes, Then it produces OpenAPI 3.1 definitions for all endpoints identified in the Architecture document",
        "Given each endpoint definition, When inspected, Then it includes request schema, response schema, error codes, and authentication requirement",
        "Given the OpenAPI output, When validated with an OpenAPI 3.1 validator, Then it passes with zero errors"
      ],
      "dependencies": ["S-029"]
    },

    {
      "id": "S-033",
      "feature_ref": "F-021",
      "epic": "E2",
      "sprint": 4,
      "priority": "should",
      "story_points": 3,
      "title": "Implement Enforcement Scaffold generation agent (D9)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "an agent that translates CLAUDE.md rules into enforceable linter configs, pre-commit hooks, and CI checks documented in 06-CLAUDE-ENFORCEMENT.md",
      "so_that": "every coding standard has an automated enforcement mechanism rather than relying on manual code review",
      "acceptance_criteria": [
        "Given CLAUDE.md and Architecture from SessionStore, When the Enforcement agent executes, Then each CLAUDE.md rule maps to at least one enforceable check (linter rule, pre-commit hook, or CI step)",
        "Given the enforcement scaffold output, When a developer violates a rule, Then the corresponding automated check catches the violation"
      ],
      "dependencies": ["S-025", "S-029"]
    },

    {
      "id": "S-034",
      "feature_ref": "F-018",
      "epic": "E2",
      "sprint": 4,
      "priority": "should",
      "story_points": 3,
      "title": "Implement Quality Spec generation agent (D10)",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "an agent that produces the 04-QUALITY.md document defining quality gates, rubric scoring criteria, coverage targets, and test categorization",
      "so_that": "quality standards are formally defined with measurable thresholds before implementation begins",
      "acceptance_criteria": [
        "Given PRD and CLAUDE.md from SessionStore, When the Quality Spec agent executes, Then it produces at least 5 quality gates with measurable thresholds",
        "Given the quality spec output, When inspected, Then it includes a rubric scoring matrix with weighted dimensions"
      ],
      "dependencies": ["S-026", "S-025"]
    },

    {
      "id": "S-035",
      "feature_ref": "F-019",
      "epic": "E2",
      "sprint": 4,
      "priority": "should",
      "story_points": 3,
      "title": "Implement Test Strategy generation agent (D11)",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "an agent that produces the 11-TESTING.md document defining test pyramid, golden test definitions, adversarial test scenarios, coverage requirements, and CI integration",
      "so_that": "the testing approach is standardized across all agents with clear definitions of what golden and adversarial tests look like",
      "acceptance_criteria": [
        "Given Quality Spec and PRD from SessionStore, When the Test Strategy agent executes, Then it produces a test pyramid definition with at least 3 golden and 3 adversarial test scenarios",
        "Given the test strategy output, When inspected, Then coverage requirements reference specific thresholds (Q-022, Q-023, Q-024, Q-025)"
      ],
      "dependencies": ["S-034"]
    },

    {
      "id": "S-036",
      "feature_ref": "F-020",
      "epic": "E2",
      "sprint": 4,
      "priority": "should",
      "story_points": 3,
      "title": "Implement Design Spec generation agent (D12)",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "an agent that produces the 10-DESIGN-SPEC.md document with UI wireframe descriptions, component hierarchy, interaction patterns, and accessibility requirements",
      "so_that": "the dashboard and UI elements are specified upfront with accessibility compliance built in from the design phase",
      "acceptance_criteria": [
        "Given PRD and Architecture from SessionStore, When the Design Spec agent executes, Then it produces a component hierarchy, at least 3 wireframe descriptions, and accessibility requirements",
        "Given the design spec output, When accessibility requirements are inspected, Then they reference WCAG 2.1 AA criteria (Q-019)"
      ],
      "dependencies": ["S-026", "S-029"]
    },

    {
      "id": "S-037",
      "feature_ref": "F-022",
      "epic": "E2",
      "sprint": 4,
      "priority": "must",
      "story_points": 8,
      "title": "Author prompt templates for first 24 agents (GOVERN + DESIGN phases)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "validated prompt template files for all GOVERN and DESIGN phase agents, each defining system prompt, few-shot examples, output schema reference, and token budget",
      "so_that": "the first two phases of the agent fleet are ready for dry-run validation and pipeline execution",
      "acceptance_criteria": [
        "Given each of the 24 GOVERN and DESIGN phase agents, When their prompt file is loaded, Then it conforms to the prompt_template_standard schema",
        "Given each prompt file, When dry-run validation runs, Then it passes with exit code 0",
        "Given each prompt file, When token budget is checked, Then it is within the configured model's context window"
      ],
      "dependencies": ["S-003", "S-005"]
    },

    {
      "id": "S-038",
      "feature_ref": "F-022",
      "epic": "E2",
      "sprint": 4,
      "priority": "must",
      "story_points": 5,
      "title": "Author prompt templates for remaining 24 agents (BUILD through OVERSIGHT phases)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "validated prompt template files for all BUILD, TEST, DEPLOY, OPERATE, and OVERSIGHT phase agents",
      "so_that": "the complete 48-agent fleet has prompt files ready for implementation and dry-run validation",
      "acceptance_criteria": [
        "Given each of the remaining 24 agents, When their prompt file is loaded, Then it conforms to the prompt_template_standard schema",
        "Given all 48 agent prompt files, When dry-run validation runs fleet-wide, Then all 48 pass with exit code 0",
        "Given the prompt file set, When audited, Then all 48 agents are accounted for with no missing files"
      ],
      "dependencies": ["S-037"]
    },

    {
      "id": "S-039",
      "feature_ref": "F-005",
      "epic": "E1",
      "sprint": 4,
      "priority": "must",
      "story_points": 3,
      "title": "Wire input/output validation into BaseAgent pre_invoke and post_invoke",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "SchemaValidator to be automatically called in BaseAgent.pre_invoke (validating input) and post_invoke (validating output) using schemas from the agent's manifest",
      "so_that": "every agent invocation is validated at both boundaries without requiring individual agents to call the validator",
      "acceptance_criteria": [
        "Given an agent receiving input that violates its input schema, When pre_invoke runs, Then a ValidationError is raised before invoke() is called",
        "Given an agent producing output that violates its output schema, When post_invoke runs, Then a ValidationError is raised before the output reaches SessionStore",
        "Given a valid input and output, When the agent executes, Then validation adds less than 10ms overhead per invocation"
      ],
      "dependencies": ["S-003", "S-006"]
    },

    {
      "id": "S-040",
      "feature_ref": "F-039",
      "epic": "E6",
      "sprint": 4,
      "priority": "must",
      "story_points": 5,
      "title": "Implement PII detection scanner for agent inputs and outputs",
      "as_a": "Lisa Patel, Compliance Officer",
      "i_want": "a PII/secret scanner that runs on every agent output before it is persisted, detecting email, phone, SSN, credit card, API key, and JWT patterns",
      "so_that": "personally identifiable information and secrets are caught and flagged before they enter the audit trail or SessionStore",
      "acceptance_criteria": [
        "Given a text payload containing PII patterns (email, phone, SSN, credit card), When the scanner runs, Then it achieves >= 95% recall on the labeled PII test corpus (SM-10)",
        "Given a detected secret, When the scanner flags it, Then the output is rejected, the invocation is flagged in audit_events with reason 'secret_detected', and an alert fires within 30 seconds (Q-013)",
        "Given a clean text payload, When the scanner runs, Then it passes with zero false positives on the golden test corpus"
      ],
      "dependencies": ["S-030"]
    },

    {
      "id": "S-041",
      "feature_ref": "F-023",
      "epic": "E2",
      "sprint": 5,
      "priority": "should",
      "story_points": 5,
      "title": "Implement 5 missing BUILD phase agent modules (B1-B5)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "working agent modules for the first 5 BUILD phase agents, each extending BaseAgent with proper manifest loading, prompt template, and input/output schemas",
      "so_that": "the BUILD pipeline can execute code generation, scaffolding, and implementation tasks",
      "acceptance_criteria": [
        "Given each of the 5 BUILD agents, When instantiated from manifest, Then they extend BaseAgent and execute the full lifecycle (pre_invoke, invoke, post_invoke)",
        "Given each agent, When dry-run validation runs, Then it passes with exit code 0",
        "Given each agent, When invoked with golden test input, Then its output conforms to the declared output schema"
      ],
      "dependencies": ["S-003", "S-038"]
    },

    {
      "id": "S-042",
      "feature_ref": "F-023",
      "epic": "E2",
      "sprint": 5,
      "priority": "should",
      "story_points": 5,
      "title": "Implement 4 remaining missing agent modules (B6-B9: TEST, DEPLOY, OPERATE, OVERSIGHT)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "working agent modules for the remaining 4 missing agents across TEST, DEPLOY, OPERATE, and OVERSIGHT phases",
      "so_that": "all 48 agents in the fleet have working implementations and the complete SDLC is covered",
      "acceptance_criteria": [
        "Given each of the 4 remaining agents, When instantiated from manifest, Then they extend BaseAgent and pass dry-run validation",
        "Given all 48 agents in the fleet, When `agent dry-run --all` runs, Then all 48 report pass (SM-7)",
        "Given each agent, When invoked, Then audit events are emitted with all 13 fields (Q-028)"
      ],
      "dependencies": ["S-041"]
    },

    {
      "id": "S-043",
      "feature_ref": "F-033",
      "epic": "E5",
      "sprint": 5,
      "priority": "should",
      "story_points": 5,
      "title": "Implement QualityScorer rubric engine",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "a QualityScorer that evaluates agent outputs against configurable rubrics with weighted dimensions (completeness, accuracy, formatting, traceability) scoring 1-10",
      "so_that": "I can objectively assess agent output quality and filter low-quality outputs before they reach my review queue",
      "acceptance_criteria": [
        "Given a PRD agent output and its rubric, When QualityScorer.score() is called, Then it returns a score between 0.0 and 10.0 with per-dimension breakdown",
        "Given an output scoring below 6.0, When scored, Then the output is flagged for manual review",
        "Given the quality scoring, When score is recorded, Then it is persisted in the audit event for trend analysis (SM-4)"
      ],
      "dependencies": ["S-003"]
    },

    {
      "id": "S-044",
      "feature_ref": "F-033",
      "epic": "E5",
      "sprint": 5,
      "priority": "should",
      "story_points": 3,
      "title": "Integrate QualityScorer into BaseAgent post_invoke hook",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "QualityScorer to automatically score every agent output in BaseAgent.post_invoke and record the score in the audit event",
      "so_that": "every agent invocation has an objective quality score without requiring manual evaluation",
      "acceptance_criteria": [
        "Given an agent invocation, When post_invoke runs, Then QualityScorer evaluates the output and records confidence_score in the audit event",
        "Given an output with confidence_score < 0.85, When scored, Then a warning is logged indicating below-threshold quality (Q-026)",
        "Given quality scores over time, When queried by agent version, Then regression detection is possible for canary deployments"
      ],
      "dependencies": ["S-043", "S-004"]
    },

    {
      "id": "S-045",
      "feature_ref": "F-040",
      "epic": "E6",
      "sprint": 5,
      "priority": "must",
      "story_points": 3,
      "title": "Build real-time cost tracking aggregation SQL views",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "SQL views and query functions for real-time cost aggregation at five levels: per-invocation, per-session, per-project, per-agent, and fleet-daily",
      "so_that": "the dashboard and CostController can query current spend at any granularity without expensive ad-hoc queries",
      "acceptance_criteria": [
        "Given populated cost_metrics data, When the fleet_daily_cost view is queried, Then it returns the correct sum of cost_usd for the current day within 500ms",
        "Given the per-project view, When queried, Then the sum of all projects equals the fleet daily total",
        "Given cost data, When reconciled against individual invocation costs, Then the aggregation is accurate to within 1% (Q-029)"
      ],
      "dependencies": ["S-010"]
    },

    {
      "id": "S-046",
      "feature_ref": "F-038",
      "epic": "E6",
      "sprint": 5,
      "priority": "should",
      "story_points": 5,
      "title": "Implement WebhookNotifier for external event delivery",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "a WebhookNotifier that delivers audit events, cost alerts, and pipeline status updates to configurable webhook endpoints (Slack, PagerDuty, custom HTTP) with retry logic",
      "so_that": "the operations team receives timely notifications without polling the platform",
      "acceptance_criteria": [
        "Given a cost alert event and a configured Slack webhook URL, When WebhookNotifier.send() is called, Then the event is delivered via HTTP POST within 5 seconds",
        "Given a webhook endpoint returning 503, When delivery fails, Then the notifier retries up to 3 times with exponential backoff (base 2s)",
        "Given webhook delivery, When each attempt completes, Then the delivery status (success/failure/retry) is logged with correlation_id (Q-030)"
      ],
      "dependencies": []
    },

    {
      "id": "S-047",
      "feature_ref": "F-028",
      "epic": "E3",
      "sprint": 5,
      "priority": "should",
      "story_points": 3,
      "title": "Build cost alert webhook notifications at configurable thresholds",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "automated Slack and PagerDuty notifications when cost thresholds are crossed at 50%, 80%, 95%, and 100% of any budget level",
      "so_that": "I can intervene before a budget ceiling is hit rather than discovering overruns after the fact",
      "acceptance_criteria": [
        "Given fleet daily spend crossing the 80% threshold ($40 of $50), When CostController detects the breach, Then a Slack notification is delivered within 60 seconds (Q-032)",
        "Given a threshold breach, When the alert is sent, Then it includes: threshold name, current value, limit, project_id, and recommended action (Q-032)",
        "Given multiple threshold crossings in rapid succession, When alerts fire, Then deduplication prevents more than one alert per threshold per hour"
      ],
      "dependencies": ["S-012", "S-046"]
    },

    {
      "id": "S-048",
      "feature_ref": "F-056",
      "epic": "E1",
      "sprint": 5,
      "priority": "must",
      "story_points": 5,
      "title": "Build fleet-wide agent dry-run validator CLI",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a CLI command `agent dry-run --all` that validates all 48 agents: loads manifest, validates schema, checks prompt file existence, and verifies dependency resolution",
      "so_that": "I can verify the entire agent fleet is configuration-complete before any pipeline execution",
      "acceptance_criteria": [
        "Given all 48 agent manifests and prompt files present, When `agent dry-run --all` runs, Then it reports pass for all 48 agents (SM-7)",
        "Given a missing prompt file for one agent, When dry-run runs, Then it reports a specific failure with the agent ID and missing file path",
        "Given dry-run output, When parsed, Then it provides a summary: X passed, Y failed, with actionable error messages for each failure"
      ],
      "dependencies": ["S-003", "S-005", "S-006"]
    },

    {
      "id": "S-049",
      "feature_ref": "F-007",
      "epic": "E1",
      "sprint": 5,
      "priority": "should",
      "story_points": 5,
      "title": "Build TeamOrchestrator for multi-level agent coordination",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a TeamOrchestrator that coordinates agents at 5 levels (solo, pair, team, cross-team, fleet) and selects the appropriate orchestration strategy based on task complexity",
      "so_that": "complex multi-agent tasks are automatically routed to the right orchestration level without manual configuration",
      "acceptance_criteria": [
        "Given a cross-team task, When TeamOrchestrator evaluates it, Then it produces an execution plan including agents from multiple teams",
        "Given a solo-agent task, When TeamOrchestrator evaluates it, Then it routes directly to the single agent without unnecessary orchestration overhead",
        "Given the execution plan, When executed, Then agent coordination follows the plan ordering and respects team boundaries"
      ],
      "dependencies": ["S-021"]
    },

    {
      "id": "S-050",
      "feature_ref": "F-041",
      "epic": "E6",
      "sprint": 5,
      "priority": "should",
      "story_points": 3,
      "title": "Implement HealthServer with readiness, liveness, and startup probes",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "an HTTP health server exposing /health/live, /health/ready, and /health/startup endpoints with component-level status",
      "so_that": "Kubernetes or monitoring systems can determine if the platform is ready to accept traffic and which dependencies are healthy",
      "acceptance_criteria": [
        "Given all dependencies (PostgreSQL, Claude API) are reachable, When GET /health/ready is called, Then it returns 200 with all components marked healthy",
        "Given PostgreSQL is unreachable, When GET /health/ready is called, Then it returns 503 with the failing component identified (Q-007)",
        "Given all non-LLM health endpoints, When load tested at 100 concurrent requests, Then p95 response time is under 200ms (Q-006)"
      ],
      "dependencies": []
    },

    {
      "id": "S-051",
      "feature_ref": "F-034",
      "epic": "E5",
      "sprint": 5,
      "priority": "must",
      "story_points": 5,
      "title": "Build golden test suite for first 24 agents (GOVERN + DESIGN phases)",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "golden test fixtures (known input + expected output pairs) for all 24 GOVERN and DESIGN phase agents, with a test runner that compares outputs using rubric scoring",
      "so_that": "every agent has a quality baseline and regressions are caught in CI before they reach production",
      "acceptance_criteria": [
        "Given each of the 24 GOVERN and DESIGN agents, When golden tests run, Then at least 3 golden test cases pass with score >= 8.0 (Q-026)",
        "Given each agent, When an adversarial test case runs, Then the agent returns a structured error response rather than a stack trace (Q-026)",
        "Given the golden test suite, When run in CI, Then results are reported per-agent with pass/fail and score"
      ],
      "dependencies": ["S-043", "S-037"]
    },

    {
      "id": "S-052",
      "feature_ref": "F-036",
      "epic": "E5",
      "sprint": 5,
      "priority": "must",
      "story_points": 3,
      "title": "Enforce 90% test coverage CI gate for SDK core modules",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "pytest-cov configured in CI to enforce >= 90% line coverage and >= 85% branch coverage for SDK core modules, failing the build if thresholds are not met",
      "so_that": "code quality is maintained through automated enforcement and coverage regressions are blocked at PR time",
      "acceptance_criteria": [
        "Given the CI pipeline, When tests run, Then `pytest --cov=sdk --cov-branch --cov-fail-under=90` executes and blocks merge if coverage drops below 90% line or 85% branch (Q-022)",
        "Given a PR that reduces SDK coverage below 90%, When CI runs, Then the build fails with a clear message indicating the coverage shortfall",
        "Given coverage reports, When uploaded to Codecov, Then nightly trend reports flag regressions > 1 percentage point (Q-022)"
      ],
      "dependencies": ["S-051"]
    },

    {
      "id": "S-053",
      "feature_ref": "F-034",
      "epic": "E5",
      "sprint": 6,
      "priority": "must",
      "story_points": 5,
      "title": "Build golden test suite for remaining 24 agents (BUILD through OVERSIGHT phases)",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "golden test fixtures for all 24 BUILD, TEST, DEPLOY, OPERATE, and OVERSIGHT phase agents",
      "so_that": "the complete 48-agent fleet has golden test coverage and CI can validate quality across the entire fleet",
      "acceptance_criteria": [
        "Given all 48 agents, When golden tests run fleet-wide, Then each agent has at least 3 golden test cases passing with score >= 8.0 (Q-026)",
        "Given all 48 agents, When adversarial tests run, Then each agent has at least 1 adversarial test case passing (Q-026)",
        "Given the test suite, When scripts/verify_agent_tests.py runs, Then it confirms 48/48 agents meet the minimum test count"
      ],
      "dependencies": ["S-042", "S-051"]
    },

    {
      "id": "S-054",
      "feature_ref": "F-035",
      "epic": "E5",
      "sprint": 6,
      "priority": "should",
      "story_points": 5,
      "title": "Build adversarial test suite for agent robustness",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "adversarial test cases covering malformed inputs, prompt injection attempts, oversized payloads, and edge-case briefs for all 48 agents",
      "so_that": "agents are proven to fail gracefully under attack and no prompt injection produces unintended output",
      "acceptance_criteria": [
        "Given a prompt injection attempt, When an agent processes it, Then the injection is neutralized and the output does not contain unintended instructions",
        "Given a 500KB oversized payload, When submitted to an agent, Then the agent rejects it with a structured error citing the 100KB limit (Q-035)",
        "Given all adversarial test cases, When they run, Then agents return structured error responses (not stack traces) for every malformed input"
      ],
      "dependencies": ["S-053"]
    },

    {
      "id": "S-055",
      "feature_ref": "F-043",
      "epic": "E7",
      "sprint": 6,
      "priority": "should",
      "story_points": 5,
      "title": "Build 3-tier knowledge base storage (L1/L2/L3)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a persistent 3-tier knowledge base: L1 per-agent in-memory cache, L2 per-team PostgreSQL table, L3 fleet-wide PostgreSQL table with full-text search",
      "so_that": "agents can learn from past exceptions and apply accumulated knowledge to improve future outputs",
      "acceptance_criteria": [
        "Given a knowledge entry stored at L3, When any agent queries via full-text search, Then it is retrievable within 200ms",
        "Given an L1 entry, When the agent process restarts, Then the L1 cache is rebuilt from L2/L3",
        "Given knowledge entries, When queried, Then results are ranked by relevance and recency"
      ],
      "dependencies": ["S-001"]
    },

    {
      "id": "S-056",
      "feature_ref": "F-042",
      "epic": "E7",
      "sprint": 6,
      "priority": "should",
      "story_points": 5,
      "title": "Implement ExceptionPromotionEngine for knowledge flywheel",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "an engine that captures agent exceptions, classifies them, and promotes recurring patterns up the knowledge tiers: L1 (3 occurrences in same agent) -> L2 -> L3 (3 occurrences across agents)",
      "so_that": "recurring failure patterns are automatically surfaced to the entire fleet without manual knowledge curation",
      "acceptance_criteria": [
        "Given an exception occurring 3 times in the same agent, When the promotion engine evaluates, Then the pattern is promoted from L1 to L2",
        "Given an L2 entry occurring across 3 different agents, When the promotion engine evaluates, Then it is promoted to L3 (fleet-wide)",
        "Given a promotion event, When it occurs, Then an audit entry records the promotion with source and destination tiers"
      ],
      "dependencies": ["S-055", "S-030"]
    },

    {
      "id": "S-057",
      "feature_ref": "F-044",
      "epic": "E7",
      "sprint": 6,
      "priority": "could",
      "story_points": 5,
      "title": "Integrate knowledge base lookups into BaseAgent pre_invoke",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "BaseAgent.pre_invoke to query the knowledge base for relevant entries matching the agent type and input context, injecting them into the prompt",
      "so_that": "agents benefit from accumulated fleet knowledge without requiring manual prompt engineering for each known issue",
      "acceptance_criteria": [
        "Given an agent with a relevant L3 knowledge entry, When pre_invoke runs, Then the entry is injected into the prompt context",
        "Given knowledge injection, When the agent produces output, Then quality score is improved compared to a baseline without knowledge injection",
        "Given knowledge lookup, When pre_invoke runs, Then the lookup adds less than 50ms overhead"
      ],
      "dependencies": ["S-055", "S-003"]
    },

    {
      "id": "S-058",
      "feature_ref": "F-008",
      "epic": "E1",
      "sprint": 6,
      "priority": "should",
      "story_points": 5,
      "title": "Define and register 5 missing team pipeline DAGs (GOVERN, TEST, DEPLOY, OPERATE, OVERSIGHT)",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "pipeline DAG definitions for the 5 missing SDLC phases, each specifying agent ordering, parallelism, and approval gates",
      "so_that": "all 7 SDLC phases have registered pipelines and the platform can orchestrate the complete lifecycle",
      "acceptance_criteria": [
        "Given all 7 phase definitions, When listed via the API, Then each pipeline has a valid DAG containing the correct agents for that phase",
        "Given each pipeline DAG, When validated, Then it has no circular dependencies and all referenced agents exist in agent_registry",
        "Given each pipeline, When it has approval gates, Then they are placed at the correct decision points per the PRD user journeys (Q-027)"
      ],
      "dependencies": ["S-021", "S-049"]
    },

    {
      "id": "S-059",
      "feature_ref": "F-047",
      "epic": "E8",
      "sprint": 6,
      "priority": "should",
      "story_points": 5,
      "title": "Implement SelfHealPolicy for automatic failure recovery",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "self-healing policies that evaluate failure types and select recovery strategies: retry with backoff, fallback to alternate model, reduce output scope, or skip optional steps",
      "so_that": "transient failures are recovered automatically without human intervention and pipeline resilience improves over time",
      "acceptance_criteria": [
        "Given a failed step due to API timeout, When SelfHealPolicy evaluates, Then it retries with exponential backoff (base 2s, max 60s, jitter)",
        "Given retry exhaustion with opus-tier model, When SelfHealPolicy evaluates, Then it falls back to haiku model and retries",
        "Given a self-heal recovery, When it succeeds, Then the recovery action is logged in audit_events with strategy details"
      ],
      "dependencies": ["S-021", "S-016"]
    },

    {
      "id": "S-060",
      "feature_ref": "F-053",
      "epic": "E10",
      "sprint": 6,
      "priority": "must",
      "story_points": 5,
      "title": "Implement per-project namespace isolation",
      "as_a": "Lisa Patel, Compliance Officer",
      "i_want": "namespace isolation on all database queries, file system paths, and session keys using project_id prefixes",
      "so_that": "client data in one project cannot leak to another project, satisfying data isolation compliance requirements",
      "acceptance_criteria": [
        "Given an agent running in project A, When it queries SessionStore for a key belonging to project B, Then None is returned (no cross-project data access)",
        "Given RLS policies on all multi-tenant tables, When queries run under the application role, Then only rows matching the session's project_id are returned (Q-015)",
        "Given a cost query for project A, When executed, Then it returns only cost_metrics rows for project A"
      ],
      "dependencies": ["S-007", "S-010"]
    },

    {
      "id": "S-061",
      "feature_ref": "F-054",
      "epic": "E10",
      "sprint": 6,
      "priority": "must",
      "story_points": 3,
      "title": "Implement per-project budget allocation and enforcement",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "separate budget allocations per project with independent ceilings enforced by CostController, independent of fleet-level limits",
      "so_that": "each client engagement stays within its agreed budget and one project cannot consume another project's allocation",
      "acceptance_criteria": [
        "Given project A with a $25 ceiling at $25 spend, When an invocation for project A is attempted, Then it is blocked even if fleet daily spend is only $30 of $50",
        "Given project B with a $25 ceiling at $10 spend, When project A is blocked, Then project B invocations continue unaffected",
        "Given budget allocation, When queried per project, Then it shows allocated, spent, and remaining amounts"
      ],
      "dependencies": ["S-012", "S-060"]
    },

    {
      "id": "S-062",
      "feature_ref": "F-036",
      "epic": "E5",
      "sprint": 6,
      "priority": "must",
      "story_points": 3,
      "title": "Enforce coverage CI gates for orchestration and API modules",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "CI coverage gates for orchestration modules (>= 85% line, >= 80% branch) and API endpoint handlers (>= 80% line)",
      "so_that": "coverage standards are enforced across all platform modules, not just the SDK core",
      "acceptance_criteria": [
        "Given orchestration module tests, When CI runs, Then `pytest --cov=orchestration --cov-branch --cov-fail-under=85` blocks merge if thresholds are not met (Q-023)",
        "Given API module tests, When CI runs, Then `pytest --cov=api --cov-fail-under=80` blocks merge if threshold is not met (Q-024)",
        "Given every new API endpoint, When tests are written, Then happy path, 401, 400, and 500 cases are covered (Q-024)"
      ],
      "dependencies": ["S-052"]
    },

    {
      "id": "S-063",
      "feature_ref": "F-036",
      "epic": "E5",
      "sprint": 6,
      "priority": "should",
      "story_points": 3,
      "title": "Enforce coverage CI gate for dashboard code",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "a CI coverage gate for dashboard Python code (>= 70% line) plus visual regression snapshots for all 5 primary pages",
      "so_that": "dashboard code quality is maintained and visual regressions are caught before deployment",
      "acceptance_criteria": [
        "Given dashboard module tests, When CI runs, Then `pytest --cov=dashboard --cov-fail-under=70` blocks merge if threshold is not met (Q-025)",
        "Given Playwright visual regression snapshots, When a dashboard PR is submitted, Then pixel-diff comparison runs against baseline with 0.1% threshold (Q-025)"
      ],
      "dependencies": ["S-052"]
    },

    {
      "id": "S-064",
      "feature_ref": "F-057",
      "epic": "E6",
      "sprint": 7,
      "priority": "should",
      "story_points": 5,
      "title": "Build Streamlit fleet health dashboard page",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "a Streamlit dashboard page showing real-time fleet status: agent count by maturity, active pipeline runs, error rates (1h/24h), and system health indicators with 30-second auto-refresh",
      "so_that": "I can monitor fleet health at a glance and detect anomalies before they escalate",
      "acceptance_criteria": [
        "Given the fleet health page, When loaded, Then it displays agent count, active pipelines, and error rate with correct values",
        "Given the page, When 30 seconds elapse, Then it auto-refreshes without manual browser reload",
        "Given the dashboard, When initial page load is measured, Then DOMContentLoaded completes in less than 3 seconds (Q-003)"
      ],
      "dependencies": ["S-030", "S-050"]
    },

    {
      "id": "S-065",
      "feature_ref": "F-058",
      "epic": "E3",
      "sprint": 7,
      "priority": "should",
      "story_points": 5,
      "title": "Build Streamlit cost monitor dashboard page",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "a Streamlit dashboard page showing fleet daily spend trend, per-project spend, per-agent spend, and budget utilization gauges with drill-down capability",
      "so_that": "I can investigate cost spikes by drilling from fleet level down to individual invocations",
      "acceptance_criteria": [
        "Given the cost monitor page, When loaded, Then it displays correct daily spend total matching the sum of per-project spends",
        "Given the drill-down, When clicking a project, Then per-agent spend for that project is shown, and clicking an agent shows individual invocations",
        "Given the page, When navigated to from another page, Then transition completes in less than 500ms (Q-003)"
      ],
      "dependencies": ["S-045"]
    },

    {
      "id": "S-066",
      "feature_ref": "F-059",
      "epic": "E2",
      "sprint": 7,
      "priority": "should",
      "story_points": 5,
      "title": "Build Streamlit pipeline runs dashboard page",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "a Streamlit dashboard page showing pipeline run status with DAG visualization (color-coded step nodes), progress percentage, elapsed time, and cost accumulator",
      "so_that": "I can monitor pipeline progress in real-time and know immediately when a step fails",
      "acceptance_criteria": [
        "Given an active pipeline run, When the page is viewed, Then a DAG is shown with correctly colored step nodes: green=done, blue=active, gray=pending, red=failed",
        "Given the pipeline dashboard, When a step transitions, Then the color updates in real-time within 5 seconds",
        "Given a completed pipeline, When viewed, Then total elapsed time and total cost are displayed"
      ],
      "dependencies": ["S-021", "S-016"]
    },

    {
      "id": "S-067",
      "feature_ref": "F-060",
      "epic": "E6",
      "sprint": 7,
      "priority": "should",
      "story_points": 5,
      "title": "Build Streamlit audit log dashboard page",
      "as_a": "Lisa Patel, Compliance Officer",
      "i_want": "a Streamlit dashboard page for browsing audit events, filterable by date range, agent, project, session, and status, with 13-field detail view and CSV export",
      "so_that": "I can conduct compliance reviews directly from the dashboard without writing SQL queries",
      "acceptance_criteria": [
        "Given the audit log page, When filtering by date range and agent ID, Then only matching events are displayed",
        "Given a selected audit event, When clicked, Then all 13 fields are shown in a detail view (Q-028)",
        "Given filtered results, When the export button is clicked, Then a CSV file is downloaded containing all filtered events"
      ],
      "dependencies": ["S-030"]
    },

    {
      "id": "S-068",
      "feature_ref": "F-061",
      "epic": "E4",
      "sprint": 7,
      "priority": "should",
      "story_points": 5,
      "title": "Build Streamlit approval queue dashboard page",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "a Streamlit dashboard page showing pending approval gates with pipeline context, artifact preview, approve/reject buttons, and history of past decisions",
      "so_that": "I can review and act on pending approvals from a single dashboard view alongside decision history",
      "acceptance_criteria": [
        "Given pending approval gates, When the page is loaded, Then all pending gates are listed with requester, pipeline context, and artifact preview",
        "Given a pending gate, When I click approve, Then the gate status is updated and the pipeline resumes within 10 seconds",
        "Given the approval queue, When all interactive elements are tabbed through, Then keyboard navigation works with visible focus indicators (Q-020)"
      ],
      "dependencies": ["S-013", "S-014"]
    },

    {
      "id": "S-069",
      "feature_ref": "F-055",
      "epic": "E10",
      "sprint": 7,
      "priority": "could",
      "story_points": 3,
      "title": "Implement per-client profile configuration",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "persistent client-specific configuration profiles storing preferred model tier, document templates, approval workflows, and quality thresholds",
      "so_that": "each client engagement uses tailored settings without requiring per-run manual configuration",
      "acceptance_criteria": [
        "Given a client profile with preferred model tier 'opus', When a pipeline runs for that client, Then all agents use opus unless overridden per-step",
        "Given a client profile with quality threshold 9.0, When agents produce output, Then the threshold is applied instead of the system default 8.0"
      ],
      "dependencies": ["S-060"]
    },

    {
      "id": "S-070",
      "feature_ref": "F-062",
      "epic": "E10",
      "sprint": 7,
      "priority": "could",
      "story_points": 3,
      "title": "Implement multi-environment configuration management",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "support for dev, staging, and production environment configurations with isolated database connections, API keys, model tiers, and cost ceilings resolved from ENV_NAME",
      "so_that": "developers can test locally without risk of accessing production data or consuming production API budget",
      "acceptance_criteria": [
        "Given ENV_NAME=staging, When the platform starts, Then all configuration resolves to staging values including database URL, API keys, and cost ceilings",
        "Given ENV_NAME=dev, When any database query runs, Then it connects to the dev database, not staging or production",
        "Given ENV_NAME=production, When the platform starts, Then no dev or staging configuration is accessible"
      ],
      "dependencies": []
    },

    {
      "id": "S-071",
      "feature_ref": "F-037",
      "epic": "E6",
      "sprint": 7,
      "priority": "must",
      "story_points": 3,
      "title": "Implement structured JSON logging with correlation_id propagation",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "all platform log lines emitted as structured JSON containing timestamp (ISO-8601), level, logger, message, and correlation_id, with correlation_id propagating across all calls within a request",
      "so_that": "I can trace a complete request path across agents, database calls, and API calls using a single correlation_id",
      "acceptance_criteria": [
        "Given any log line emitted by the platform, When captured, Then it parses as valid JSON with all 5 required fields (Q-030)",
        "Given a pipeline step, When it logs across function calls and DB queries, Then all log lines share the same correlation_id (Q-030)",
        "Given the codebase, When CI lint runs, Then zero bare print() statements exist in production code (Q-030)"
      ],
      "dependencies": ["S-030"]
    },

    {
      "id": "S-072",
      "feature_ref": "F-037",
      "epic": "E6",
      "sprint": 7,
      "priority": "must",
      "story_points": 3,
      "title": "Implement data retention enforcement job",
      "as_a": "Lisa Patel, Compliance Officer",
      "i_want": "a nightly retention job that deletes expired data in batches: audit_events after 365 days, session_context after 30 days, cost_metrics after 90 days",
      "so_that": "data retention policies are enforced automatically and configurable retention periods meet regulatory minimums",
      "acceptance_criteria": [
        "Given audit_events records at 366 days old, When the retention job runs, Then they are deleted (Q-036)",
        "Given audit_events records at 364 days old, When the retention job runs, Then they are retained (Q-036)",
        "Given retention periods, When configured via environment variables, Then they cannot be shortened below regulatory minimums (audit: 365 days per SOC2) (Q-036)"
      ],
      "dependencies": ["S-030"]
    },

    {
      "id": "S-073",
      "feature_ref": "F-037",
      "epic": "E6",
      "sprint": 7,
      "priority": "must",
      "story_points": 3,
      "title": "Implement agent output size limit enforcement and overflow storage",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "agent output size enforcement at 100KB (UTF-8 bytes) with truncation marker and overflow storage for full content in the agent_output_overflow table",
      "so_that": "large outputs do not degrade system performance while full content remains retrievable for review",
      "acceptance_criteria": [
        "Given an agent output of 150KB, When post_invoke runs, Then the stored output is <= 100KB with a [TRUNCATED] marker (Q-035)",
        "Given a truncated output, When the overflow table is queried, Then the full 150KB content is available via foreign key to the audit record (Q-035)",
        "Given an output of 80KB, When post_invoke runs, Then it is stored in full without truncation"
      ],
      "dependencies": ["S-003", "S-030"]
    },

    {
      "id": "S-074",
      "feature_ref": "F-053",
      "epic": "E10",
      "sprint": 7,
      "priority": "must",
      "story_points": 5,
      "title": "Enable Row-Level Security on all multi-tenant PostgreSQL tables",
      "as_a": "Lisa Patel, Compliance Officer",
      "i_want": "Row-Level Security (RLS) policies on all 8 multi-tenant tables scoped by project_id and client_id, with the application running under a non-superuser role",
      "so_that": "data isolation is enforced at the database level as a defense-in-depth measure beyond application logic",
      "acceptance_criteria": [
        "Given the application role, When SELECT runs on agent_registry, Then only rows matching the session's project_id/client_id are returned (Q-015)",
        "Given the application role, When INSERT with mismatched tenant IDs is attempted, Then it is rejected by RLS policy (Q-015)",
        "Given pg_policies catalog, When queried in CI, Then policies exist on all 8 multi-tenant tables (Q-015)"
      ],
      "dependencies": ["S-001", "S-002"]
    },

    {
      "id": "S-075",
      "feature_ref": "F-049",
      "epic": "E9",
      "sprint": 8,
      "priority": "should",
      "story_points": 5,
      "title": "Implement agent version slots and registry",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "agent_registry support for multiple version slots (production, canary, shadow) with traffic weight assignment per slot",
      "so_that": "new agent versions can be deployed alongside production versions for safe comparison before full rollout",
      "acceptance_criteria": [
        "Given an agent with production (v1.1) and canary (v1.2) slots, When the registry is queried, Then both versions are returned with correct traffic weights",
        "Given a new version registration, When agent deploy --version 1.2 --slot canary runs, Then the canary slot is created without affecting the production slot",
        "Given version slot changes, When they occur, Then they are recorded in audit_events with before/after version metadata"
      ],
      "dependencies": ["S-003", "S-001"]
    },

    {
      "id": "S-076",
      "feature_ref": "F-050",
      "epic": "E9",
      "sprint": 8,
      "priority": "should",
      "story_points": 8,
      "title": "Implement canary deployment with traffic splitting and auto-promotion",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "canary deployment that routes a configurable percentage of requests to the canary version, compares quality/latency/error metrics, and auto-promotes or rolls back based on thresholds",
      "so_that": "agent version upgrades are validated in production with real traffic before full rollout, preventing quality regressions",
      "acceptance_criteria": [
        "Given a canary configured at 10% traffic, When requests arrive, Then approximately 10% are routed to the canary slot",
        "Given 50 canary invocations with quality score delta < 0.5 from production, When the promotion check runs, Then the canary is auto-promoted to 100% traffic",
        "Given canary quality score dropping 1.0+ below production, When detected, Then auto-rollback occurs within 60 seconds and a Slack alert is sent"
      ],
      "dependencies": ["S-075", "S-043"]
    },

    {
      "id": "S-077",
      "feature_ref": "F-052",
      "epic": "E9",
      "sprint": 8,
      "priority": "could",
      "story_points": 5,
      "title": "Implement automatic rollback on quality regression",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "real-time monitoring of canary quality scores that triggers automatic rollback when the canary drops below a configurable delta from the production baseline",
      "so_that": "quality regressions are contained automatically without waiting for human intervention",
      "acceptance_criteria": [
        "Given a canary with quality score 1.0+ below production, When the monitor detects it, Then rollback to production version occurs within 60 seconds",
        "Given a rollback event, When it occurs, Then a Slack alert is sent with rollback reason, canary score, and production baseline score",
        "Given a rollback, When it completes, Then 100% of traffic is routed to the production version and the canary slot is deactivated"
      ],
      "dependencies": ["S-076"]
    },

    {
      "id": "S-078",
      "feature_ref": "F-051",
      "epic": "E9",
      "sprint": 8,
      "priority": "could",
      "story_points": 3,
      "title": "Implement agent maturity progression tracking",
      "as_a": "Priya Mehta, Platform Engineer",
      "i_want": "automated tracking of agent maturity levels (draft, dry-run-passing, golden-test-passing, canary-validated, production) that advances based on test results and deployment events",
      "so_that": "the fleet dashboard shows agent readiness at a glance and promotion decisions are data-driven",
      "acceptance_criteria": [
        "Given an agent that passes golden tests, When the maturity engine evaluates, Then it automatically advances from dry-run-passing to golden-test-passing",
        "Given an agent that passes canary validation, When promoted, Then its maturity advances to canary-validated",
        "Given maturity levels, When queried fleet-wide, Then a summary shows count of agents at each maturity level"
      ],
      "dependencies": ["S-075", "S-053"]
    },

    {
      "id": "S-079",
      "feature_ref": "F-008",
      "epic": "E1",
      "sprint": 8,
      "priority": "should",
      "story_points": 3,
      "title": "Build end-to-end integration tests for all 7 phase pipelines",
      "as_a": "Sarah Kim, Engineering Lead",
      "i_want": "integration tests that execute each of the 7 phase pipelines against synthetic inputs and assert: all expected documents produced, status=completed, cost within budget, no checkpoint corruption",
      "so_that": "every registered pipeline is proven to work end-to-end before it reaches production users",
      "acceptance_criteria": [
        "Given each of the 7 phase pipelines, When its integration test runs, Then all expected output documents are produced and pipeline_runs.status = 'completed' (Q-027)",
        "Given each pipeline test, When cost is checked, Then it is within the configured budget ceiling (Q-027)",
        "Given pipeline names, When validated against pipeline_registry, Then no registered pipeline is untested (Q-027)"
      ],
      "dependencies": ["S-058", "S-053"]
    },

    {
      "id": "S-080",
      "feature_ref": "F-008",
      "epic": "E1",
      "sprint": 8,
      "priority": "should",
      "story_points": 3,
      "title": "Validate 12-document pipeline end-to-end with golden inputs",
      "as_a": "David Chen, Delivery Lead",
      "i_want": "a full end-to-end test of the 12-document pipeline using a golden client brief that verifies all 12 documents are produced within 30 minutes and $25",
      "so_that": "the flagship pipeline is validated against the primary success metrics before GA release",
      "acceptance_criteria": [
        "Given a golden client brief, When the 12-document pipeline runs, Then all 12 documents are produced with pipeline_runs.status = 'completed' (Q-002)",
        "Given the pipeline run, When wall-clock time is measured, Then it completes in less than 30 minutes (Q-002)",
        "Given the pipeline run, When total cost is summed, Then it is under $25 (SM-2)"
      ],
      "dependencies": ["S-023", "S-053"]
    },

    {
      "id": "S-081",
      "feature_ref": "F-048",
      "epic": "E8",
      "sprint": 8,
      "priority": "must",
      "story_points": 3,
      "title": "Implement graceful degradation when Claude API is unreachable",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "the platform to queue pending invocations in PostgreSQL, activate the circuit breaker, emit structured warnings, return degraded-mode health status, and auto-retry when connectivity restores --- without crashing or losing data",
      "so_that": "external API outages are handled gracefully and no invocation is silently dropped",
      "acceptance_criteria": [
        "Given Claude API is unreachable, When 10 invocations are submitted, Then all 10 are queued in PostgreSQL and none are dropped (Q-011)",
        "Given API unreachability, When /health is queried, Then it returns degraded-mode status (Q-011)",
        "Given connectivity restoration, When queued invocations retry, Then all 10 eventually complete with correct outputs (Q-011)"
      ],
      "dependencies": ["S-019", "S-021"]
    },

    {
      "id": "S-082",
      "feature_ref": "F-048",
      "epic": "E8",
      "sprint": 8,
      "priority": "should",
      "story_points": 3,
      "title": "Implement asyncpg connection pool recovery after database restart",
      "as_a": "Marcus Johnson, DevOps Engineer",
      "i_want": "the asyncpg connection pool to recover from a full database restart within 10 seconds, re-establishing the minimum pool size without manual intervention",
      "so_that": "database maintenance windows do not require platform restarts and in-flight retryable requests succeed after pool recovery",
      "acceptance_criteria": [
        "Given a PostgreSQL restart, When the pool detects the outage, Then it re-establishes the minimum pool size within 10 seconds (Q-012)",
        "Given retryable requests during pool recovery, When the pool recovers, Then those requests succeed",
        "Given non-retryable requests during pool recovery, When the pool is unavailable, Then they return 503 (not 500 or hang) (Q-012)"
      ],
      "dependencies": ["S-007"]
    }
  ]
}
```

---

## 3. Story-to-Feature Traceability Matrix

| Feature | Stories | Total SP |
|---|---|---|
| F-001 | S-003, S-004 | 8 |
| F-002 | S-005 | 5 |
| F-003 | S-006 | 5 |
| F-004 | S-007, S-008 | 8 |
| F-005 | S-009, S-039 | 8 |
| F-006 | S-021 | 8 |
| F-007 | S-049 | 5 |
| F-008 | S-058, S-079, S-080 | 11 |
| F-009 | S-023 | 5 |
| F-010 | S-024 | 5 |
| F-011 | S-026 | 5 |
| F-012 | S-029 | 5 |
| F-013 | S-025 | 3 |
| F-014 | S-027 | 5 |
| F-015 | S-028 | 3 |
| F-016 | S-031 | 5 |
| F-017 | S-032 | 5 |
| F-018 | S-034 | 3 |
| F-019 | S-035 | 3 |
| F-020 | S-036 | 3 |
| F-021 | S-033 | 3 |
| F-022 | S-037, S-038 | 13 |
| F-023 | S-041, S-042 | 10 |
| F-024 | S-010, S-011 | 8 |
| F-025 | S-012 | 8 |
| F-026 | S-018 | 5 |
| F-027 | S-019 | 5 |
| F-028 | S-047 | 3 |
| F-029 | S-013 | 5 |
| F-030 | S-014 | 5 |
| F-031 | S-015 | 5 |
| F-032 | S-020 | 5 |
| F-033 | S-043, S-044 | 8 |
| F-034 | S-051, S-053 | 10 |
| F-035 | S-054 | 5 |
| F-036 | S-052, S-062, S-063 | 9 |
| F-037 | S-030, S-071, S-072, S-073 | 14 |
| F-038 | S-046 | 5 |
| F-039 | S-040 | 5 |
| F-040 | S-045 | 3 |
| F-041 | S-050 | 3 |
| F-042 | S-056 | 5 |
| F-043 | S-055 | 5 |
| F-044 | S-057 | 5 |
| F-045 | S-016, S-017 | 8 |
| F-046 | S-001, S-002 | 6 |
| F-047 | S-059 | 5 |
| F-048 | S-022, S-081, S-082 | 11 |
| F-049 | S-075 | 5 |
| F-050 | S-076 | 8 |
| F-051 | S-078 | 3 |
| F-052 | S-077 | 5 |
| F-053 | S-060, S-074 | 10 |
| F-054 | S-061 | 3 |
| F-055 | S-069 | 3 |
| F-056 | S-048 | 5 |
| F-057 | S-064 | 5 |
| F-058 | S-065 | 5 |
| F-059 | S-066 | 5 |
| F-060 | S-067 | 5 |
| F-061 | S-068 | 5 |
| F-062 | S-070 | 3 |

---

## 4. Priority Distribution

| Priority | Story Count | Story Points |
|---|---|---|
| must | 42 | 178 |
| should | 30 | 121 |
| could | 10 | 28 |
| **Total** | **82** | **327** |

---

## 5. Sprint Velocity Projection

| Sprint | Theme | Planned SP | Cumulative SP | % Complete |
|---|---|---|---|---|
| Sprint 1 | Foundation | 39 | 39 | 12% |
| Sprint 2 | Safety | 40 | 79 | 24% |
| Sprint 3 | Core Agents I | 39 | 118 | 36% |
| Sprint 4 | Core Agents II | 38 | 156 | 48% |
| Sprint 5 | Build Agents & Quality | 40 | 196 | 60% |
| Sprint 6 | Fleet Testing & Knowledge | 39 | 235 | 72% |
| Sprint 7 | Observability & Dashboard | 38 | 273 | 83% |
| Sprint 8 | Lifecycle & Hardening | 33 | 306 | 94% |

**Note:** 21 story points of buffer capacity remain across 8 sprints (327 planned vs 320 capacity) to account for estimation variance. Some stories may be pulled forward if velocity exceeds projections.

---

## 6. Critical Path

The longest dependency chain determines the minimum project duration:

```
S-001 (migrations 005-006)
  -> S-007 (SessionStore read/write)
    -> S-021 (PipelineRunner sequential)
      -> S-023 (12-doc pipeline DAG)
        -> S-024 (Roadmap agent)
          -> S-025 (CLAUDE.md agent)
            -> S-026 (PRD agent)
              -> S-029 (Architecture agent)
                -> S-031 (Data Model agent)
```

**Critical path length:** 9 stories spanning Sprints 1-4. Any delay on this path delays the first end-to-end pipeline run.

**Secondary critical path (cost enforcement):**
```
S-001 -> S-010 (CostStore) -> S-011 (projection) -> S-012 (CostController) -> S-047 (alerts)
```

**Foundation blockers (Sprint 1):** S-001, S-002, S-003, S-005, S-007, S-010

---

## 7. NFR Coverage Matrix

| NFR | Stories Referencing | Verified By |
|---|---|---|
| Q-001 | S-024 | Agent latency assertion in golden tests |
| Q-002 | S-021, S-080 | Pipeline duration assertion in e2e test |
| Q-003 | S-064, S-065 | Lighthouse CI on dashboard PRs |
| Q-004 | S-007 | SessionStore latency benchmark |
| Q-005 | S-005 | ManifestLoader performance test |
| Q-006 | S-050 | Locust load test on health endpoints |
| Q-007 | S-050 | Synthetic health checks |
| Q-008 | S-016, S-017 | Checkpoint recovery integration test |
| Q-009 | S-019 | Circuit breaker unit + integration tests |
| Q-010 | S-002 | WAL archiving + monthly restore drill |
| Q-011 | S-081 | Graceful degradation integration test |
| Q-012 | S-082 | DB pool recovery integration test |
| Q-013 | S-004, S-006, S-025, S-040 | PII scanner + detect-secrets in CI |
| Q-015 | S-060, S-074 | RLS enforcement integration test |
| Q-018 | S-020 | T0 tool restriction unit test |
| Q-019 | S-036, S-068 | axe-core accessibility audit |
| Q-020 | S-068 | Playwright keyboard navigation test |
| Q-022 | S-052 | pytest --cov SDK gate |
| Q-023 | S-062 | pytest --cov orchestration gate |
| Q-024 | S-062 | pytest --cov API gate |
| Q-025 | S-063 | pytest --cov dashboard gate |
| Q-026 | S-051, S-053, S-054 | Agent test verification script |
| Q-027 | S-079, S-080 | Pipeline integration test suite |
| Q-028 | S-003, S-004, S-030, S-067 | Audit record schema validation |
| Q-029 | S-010, S-045 | Cost reconciliation job |
| Q-030 | S-009, S-046, S-071 | Structured logging lint + tests |
| Q-031 | S-021 | Step duration tracking test |
| Q-032 | S-012, S-047 | Budget alert integration tests |
| Q-033 | S-002, S-013, S-030 | Immutability trigger test |
| Q-034 | S-007, S-008 | Session TTL enforcement test |
| Q-035 | S-073 | Output size limit test |
| Q-036 | S-072 | Retention job integration test |

---

## 8. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-03-23 | David Chen (Delivery Lead) | Initial backlog with 82 stories across 8 sprints covering all 62 features |

---

*This backlog is machine-parseable. The JSON block contains the complete story set with dependencies, acceptance criteria referencing NFR IDs, and sprint assignments. All 62 features from the Feature Catalog are represented by at least one story. No story exceeds 8 story points.*
