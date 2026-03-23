# Feature Catalog — Agentic SDLC Platform

| Field            | Value                                      |
| ---------------- | ------------------------------------------ |
| Document ID      | FC-ASDLC-001                               |
| Version          | 1.0.0                                      |
| Status           | Draft                                      |
| Generated From   | PRD.md + ARCH.md + MASTER-BUILD-SPEC.md    |
| Last Updated     | 2026-03-23                                 |
| Total Features   | 62                                         |

---

## Epics

| Epic | PRD Capability | Name                                |
| ---- | -------------- | ----------------------------------- |
| E1   | C1             | Agent Orchestration                 |
| E2   | C2             | 12-Document Generation Pipeline     |
| E3   | C3             | Cost Control & Governance           |
| E4   | C4             | Human-in-the-Loop                   |
| E5   | C5             | Quality Assurance                   |
| E6   | C6             | Observability & Audit               |
| E7   | C7             | Knowledge Management                |
| E8   | C8             | Pipeline Resilience                 |
| E9   | C9             | Agent Lifecycle                     |
| E10  | C10            | Multi-Project Isolation             |

---

## Feature Catalog

```json
{
  "version": "1.0.0",
  "generated_from": "PRD.md + ARCH.md + MASTER-BUILD-SPEC.md",
  "total_features": 62,
  "epics": {
    "E1": "Agent Orchestration",
    "E2": "12-Document Generation Pipeline",
    "E3": "Cost Control & Governance",
    "E4": "Human-in-the-Loop",
    "E5": "Quality Assurance",
    "E6": "Observability & Audit",
    "E7": "Knowledge Management",
    "E8": "Pipeline Resilience",
    "E9": "Agent Lifecycle",
    "E10": "Multi-Project Isolation"
  },
  "features": [
    {
      "id": "F-001",
      "epic": "E1",
      "name": "Implement BaseAgent abstract class with hooks lifecycle",
      "description": "Create the BaseAgent class that all 48 agents inherit from. Provides pre_invoke, invoke, post_invoke hooks, manifest-driven configuration, and typed input/output contracts. Input: agent manifest YAML. Output: runnable agent instance with lifecycle hooks.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Priya Mehta"],
      "dependencies": [],
      "data_prereqs": ["agent_manifest_schema.yaml", "hooks_interface_spec"],
      "acceptance": "BaseAgent subclass can be instantiated from a manifest YAML and executes pre_invoke, invoke, post_invoke in sequence with typed inputs and outputs."
    },
    {
      "id": "F-002",
      "epic": "E1",
      "name": "Implement ManifestLoader with schema validation",
      "description": "Load agent manifest YAML files, validate against JSON Schema, resolve environment variable references, and return typed configuration objects. Input: path to manifest YAML. Output: validated ManifestConfig dataclass.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Priya Mehta"],
      "dependencies": [],
      "data_prereqs": ["manifest_json_schema.json"],
      "acceptance": "ManifestLoader rejects an invalid manifest with a clear error message listing all validation failures and returns a typed ManifestConfig for valid manifests."
    },
    {
      "id": "F-003",
      "epic": "E1",
      "name": "Implement SchemaValidator for input/output contracts",
      "description": "Validate agent inputs and outputs against JSON Schema definitions declared in each agent's manifest. Raises ValidationError with field-level details on mismatch. Input: data dict + schema ref. Output: validated data or ValidationError.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Priya Mehta", "Sarah Kim"],
      "dependencies": ["F-002"],
      "data_prereqs": ["input_output_schemas per agent manifest"],
      "acceptance": "SchemaValidator raises a ValidationError listing all invalid fields when agent output does not match the declared output schema."
    },
    {
      "id": "F-004",
      "epic": "E1",
      "name": "Implement SessionStore for cross-agent context",
      "description": "Persistent key-value store backed by PostgreSQL session_context table. Agents read/write shared context (e.g., project brief, generated PRD) across pipeline steps. Input: session_id + key. Output: stored value or None. FIX-01 BLOCKING.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Priya Mehta", "David Chen"],
      "dependencies": ["F-046"],
      "data_prereqs": ["migration_005_session_context.sql", "session_context table DDL"],
      "acceptance": "SessionStore.get returns the value previously written by SessionStore.set for the same session_id and key, persisted across process restarts."
    },
    {
      "id": "F-005",
      "epic": "E1",
      "name": "Implement Envelope-based message routing between agents",
      "description": "Typed message envelope system for agent-to-agent communication over asyncio queues. Envelope contains sender, recipient, payload, correlation_id, timestamp. Input: Envelope dataclass. Output: delivery confirmation to recipient agent.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-001"],
      "data_prereqs": ["envelope_schema.json"],
      "acceptance": "An Envelope sent from agent A is received by agent B within 100ms on the same asyncio event loop with all fields intact."
    },
    {
      "id": "F-006",
      "epic": "E1",
      "name": "Build PipelineRunner DAG execution engine",
      "description": "Execute a pipeline defined as a directed acyclic graph of agent steps. Supports sequential, parallel, and fan-out/fan-in patterns. Input: pipeline DAG definition. Output: ordered execution of agent steps with results collected. FIX-06.",
      "priority": "must",
      "story_points": 13,
      "effort": "XL",
      "complexity": "high",
      "personas": ["Priya Mehta", "David Chen"],
      "dependencies": ["F-001", "F-004", "F-005"],
      "data_prereqs": ["pipeline_dag_schema.yaml"],
      "acceptance": "PipelineRunner executes a DAG with 3 sequential steps followed by 2 parallel steps and collects all results within the expected ordering constraints."
    },
    {
      "id": "F-007",
      "epic": "E1",
      "name": "Build TeamOrchestrator for 5 orchestration levels",
      "description": "Orchestrate agents at 5 levels: solo agent, agent pair, team (3-5 agents), cross-team pipeline, and fleet-wide operation. TeamOrchestrator selects strategy based on task complexity. Input: task descriptor + available agents. Output: orchestration plan.",
      "priority": "should",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-006"],
      "data_prereqs": ["team_definitions.yaml", "orchestration_level_config"],
      "acceptance": "TeamOrchestrator routes a cross-team task to the correct orchestration level and produces an execution plan that includes agents from multiple teams."
    },
    {
      "id": "F-008",
      "epic": "E1",
      "name": "Implement 5 missing team pipeline definitions",
      "description": "Define and register the 5 missing team pipelines identified in ADD-10: GOVERN, TEST, DEPLOY, OPERATE, and OVERSIGHT phase pipelines. Each pipeline specifies agent ordering, parallelism, and approval gates. Input: phase spec. Output: registered pipeline DAG.",
      "priority": "should",
      "story_points": 8,
      "effort": "L",
      "complexity": "medium",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-006", "F-007"],
      "data_prereqs": ["phase_agent_mapping.yaml"],
      "acceptance": "All 7 phase pipelines are registered and can be listed via the API, each with a valid DAG containing the correct agents for that phase."
    },
    {
      "id": "F-009",
      "epic": "E2",
      "name": "Build 12-document pipeline DAG definition",
      "description": "Define the full 12-document generation pipeline as a DAG: Roadmap -> CLAUDE.md -> PRD -> Feature Catalog -> Backlog -> Architecture -> (Data Model || API Contracts) -> Enforcement Scaffold -> (Quality Spec || Test Strategy) -> Design Spec. Input: client brief. Output: pipeline run ID.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["David Chen", "Priya Mehta"],
      "dependencies": ["F-006"],
      "data_prereqs": ["twelve_doc_dag.yaml", "agent_manifest per doc type"],
      "acceptance": "Pipeline trigger with a valid client brief creates a pipeline run with 12 steps in the correct dependency order, including 2 parallel pairs."
    },
    {
      "id": "F-010",
      "epic": "E2",
      "name": "Implement Roadmap generation agent",
      "description": "Agent that produces the 00-ROADMAP.md document from a client brief. Extracts milestones, phases, timelines, and dependencies. Input: client brief text. Output: structured roadmap markdown.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["David Chen"],
      "dependencies": ["F-001", "F-004"],
      "data_prereqs": ["roadmap_prompt_template", "roadmap_output_schema.json"],
      "acceptance": "Roadmap agent produces a markdown document with at least 3 milestones, each with a timeline and dependency list, scoring >= 8.0 on the rubric."
    },
    {
      "id": "F-011",
      "epic": "E2",
      "name": "Implement PRD generation agent",
      "description": "Agent that produces the 01-PRD.md document. Reads client brief and roadmap from SessionStore, generates problem statement, personas, capabilities (C1-Cn), success metrics, and user journeys. Input: brief + roadmap. Output: PRD markdown.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["David Chen", "Sarah Kim"],
      "dependencies": ["F-001", "F-004", "F-010"],
      "data_prereqs": ["prd_prompt_template", "prd_output_schema.json"],
      "acceptance": "PRD agent produces a document with problem statement, at least 3 personas, at least 5 capabilities, and success metrics, all traceable to the client brief."
    },
    {
      "id": "F-012",
      "epic": "E2",
      "name": "Implement Architecture document generation agent",
      "description": "Agent that produces the 02-ARCH.md document. Reads PRD capabilities and generates C4 diagrams (context, container, component), technology choices, data flow, and deployment topology. Input: PRD + brief. Output: Architecture markdown.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["David Chen", "Sarah Kim"],
      "dependencies": ["F-001", "F-004", "F-011"],
      "data_prereqs": ["arch_prompt_template", "arch_output_schema.json"],
      "acceptance": "Architecture agent produces a document with C4 context, container, and component diagrams, and every PRD capability maps to at least one architectural component."
    },
    {
      "id": "F-013",
      "epic": "E2",
      "name": "Implement CLAUDE.md generation agent",
      "description": "Agent that produces the 03-CLAUDE.md enforcement scaffold. Defines coding standards, file conventions, testing mandates, and AI-specific constraints for the project. Input: brief + roadmap. Output: CLAUDE.md markdown.",
      "priority": "must",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["David Chen", "Priya Mehta"],
      "dependencies": ["F-001", "F-004", "F-010"],
      "data_prereqs": ["claude_md_prompt_template"],
      "acceptance": "CLAUDE.md agent produces a document with at least 10 enforceable rules covering naming, testing, and file structure conventions."
    },
    {
      "id": "F-014",
      "epic": "E2",
      "name": "Implement Feature Catalog generation agent",
      "description": "Agent that produces the 05-FEATURE-CATALOG.json document. Extracts features from PRD capabilities, assigns story points, priorities, dependencies, and acceptance criteria. Input: PRD. Output: JSON feature catalog.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["David Chen"],
      "dependencies": ["F-001", "F-004", "F-011"],
      "data_prereqs": ["feature_catalog_prompt_template", "feature_catalog_schema.json"],
      "acceptance": "Feature Catalog agent produces valid JSON with at least one feature per PRD capability, all features have all required fields, and IDs are sequential."
    },
    {
      "id": "F-015",
      "epic": "E2",
      "name": "Implement Backlog generation agent",
      "description": "Agent that decomposes features from the Feature Catalog into actionable backlog items with sprint assignments, effort estimates, and dependency ordering. Input: Feature Catalog JSON. Output: Backlog markdown.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["David Chen", "Sarah Kim"],
      "dependencies": ["F-001", "F-004", "F-014"],
      "data_prereqs": ["backlog_prompt_template", "backlog_output_schema.json"],
      "acceptance": "Backlog agent produces items traceable to Feature Catalog IDs, with every feature represented by at least one backlog item."
    },
    {
      "id": "F-016",
      "epic": "E2",
      "name": "Implement Data Model generation agent",
      "description": "Agent that produces the 07-DATA-MODEL.md document. Generates entity-relationship diagrams, table DDLs, index strategies, and migration scripts based on the Architecture document. Input: ARCH + PRD. Output: Data Model markdown.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["David Chen", "Priya Mehta"],
      "dependencies": ["F-001", "F-004", "F-012"],
      "data_prereqs": ["data_model_prompt_template", "data_model_output_schema.json"],
      "acceptance": "Data Model agent produces DDL for all tables referenced in the Architecture document with primary keys, foreign keys, and at least one index per table."
    },
    {
      "id": "F-017",
      "epic": "E2",
      "name": "Implement API Contracts generation agent",
      "description": "Agent that produces the 09-API-CONTRACTS.md document. Generates OpenAPI 3.1 endpoint definitions, request/response schemas, error codes, and authentication requirements. Input: ARCH + PRD. Output: API Contracts markdown with OpenAPI snippets.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["David Chen", "Priya Mehta"],
      "dependencies": ["F-001", "F-004", "F-012"],
      "data_prereqs": ["api_contracts_prompt_template", "openapi_base_schema.json"],
      "acceptance": "API Contracts agent produces OpenAPI 3.1 definitions for all endpoints identified in the Architecture document, each with request schema, response schema, and error codes."
    },
    {
      "id": "F-018",
      "epic": "E2",
      "name": "Implement Quality Spec generation agent",
      "description": "Agent that produces the 04-QUALITY.md document. Defines quality gates, rubric scoring criteria, coverage targets, and test categorization. Input: PRD + CLAUDE.md. Output: Quality Spec markdown.",
      "priority": "should",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["David Chen", "Sarah Kim"],
      "dependencies": ["F-001", "F-004", "F-011", "F-013"],
      "data_prereqs": ["quality_spec_prompt_template"],
      "acceptance": "Quality Spec agent produces a document defining at least 5 quality gates with measurable thresholds and a rubric scoring matrix."
    },
    {
      "id": "F-019",
      "epic": "E2",
      "name": "Implement Test Strategy generation agent",
      "description": "Agent that produces the 11-TESTING.md document. Defines test pyramid, golden test definitions, adversarial test scenarios, coverage requirements, and CI integration. Input: Quality Spec + PRD. Output: Test Strategy markdown.",
      "priority": "should",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["David Chen", "Sarah Kim"],
      "dependencies": ["F-001", "F-004", "F-018"],
      "data_prereqs": ["test_strategy_prompt_template"],
      "acceptance": "Test Strategy agent produces a document with test pyramid definition, at least 3 golden test scenarios, and at least 3 adversarial test scenarios."
    },
    {
      "id": "F-020",
      "epic": "E2",
      "name": "Implement Design Spec generation agent",
      "description": "Agent that produces the 10-DESIGN-SPEC.md document. Generates UI wireframe descriptions, component hierarchy, interaction patterns, and accessibility requirements. Input: PRD + ARCH. Output: Design Spec markdown.",
      "priority": "should",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["David Chen"],
      "dependencies": ["F-001", "F-004", "F-011", "F-012"],
      "data_prereqs": ["design_spec_prompt_template"],
      "acceptance": "Design Spec agent produces a document with component hierarchy, at least 3 wireframe descriptions, and accessibility requirements per WCAG 2.1 AA."
    },
    {
      "id": "F-021",
      "epic": "E2",
      "name": "Implement Enforcement Scaffold generation agent",
      "description": "Agent that produces the 06-CLAUDE-ENFORCEMENT.md document. Translates CLAUDE.md rules into enforceable linter configs, pre-commit hooks, and CI checks. Input: CLAUDE.md + ARCH. Output: Enforcement Scaffold markdown.",
      "priority": "should",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["David Chen", "Priya Mehta"],
      "dependencies": ["F-001", "F-004", "F-013", "F-012"],
      "data_prereqs": ["enforcement_prompt_template"],
      "acceptance": "Enforcement Scaffold agent produces a document mapping each CLAUDE.md rule to at least one enforceable check (linter rule, pre-commit hook, or CI step)."
    },
    {
      "id": "F-022",
      "epic": "E2",
      "name": "Complete all 48 agent prompt files",
      "description": "Author and validate prompt templates for all 48 agents across 7 SDLC phases. Currently 39 exist in dry-run; 9 are missing (ADD-12). Each prompt file defines system prompt, few-shot examples, output schema, and token budget. FIX-10.",
      "priority": "must",
      "story_points": 13,
      "effort": "XL",
      "complexity": "high",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-001", "F-002"],
      "data_prereqs": ["prompt_template_standard.yaml", "agent_registry entries for all 48 agents"],
      "acceptance": "All 48 agents pass dry-run validation with exit code 0 and each prompt file conforms to the prompt template standard schema."
    },
    {
      "id": "F-023",
      "epic": "E2",
      "name": "Build 9 missing agent implementations",
      "description": "Implement the 9 agents identified in ADD-12 that currently lack code: includes remaining GOVERN, TEST, DEPLOY, OPERATE, and OVERSIGHT phase agents. Each agent must extend BaseAgent and pass dry-run. Input: agent manifest. Output: working agent module.",
      "priority": "should",
      "story_points": 13,
      "effort": "XL",
      "complexity": "high",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-001", "F-002", "F-022"],
      "data_prereqs": ["agent_manifests for 9 missing agents"],
      "acceptance": "All 9 missing agents are implemented, registered in agent_registry, and pass dry-run validation with exit code 0."
    },
    {
      "id": "F-024",
      "epic": "E3",
      "name": "Implement PostgresCostStore with fail-safe enforcement",
      "description": "Real-time cost tracking store backed by PostgreSQL cost_metrics table. Records cost per invocation, aggregates by session/project/agent/fleet. Enforces hard ceiling by raising CostLimitExceeded before LLM call if projected cost exceeds budget. FIX-04.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Marcus Johnson", "David Chen"],
      "dependencies": ["F-046"],
      "data_prereqs": ["migration_006_cost_metrics.sql", "cost_metrics table DDL"],
      "acceptance": "PostgresCostStore blocks an agent invocation with CostLimitExceeded when the cumulative session cost plus estimated next-call cost exceeds the configured ceiling."
    },
    {
      "id": "F-025",
      "epic": "E3",
      "name": "Implement CostController with 4-level budget enforcement",
      "description": "Enforce budget limits at 4 levels: per-invocation, per-session, per-project, and fleet-daily. Each level has warn and hard thresholds. Input: cost event. Output: allow/warn/block decision. Integrates with PostgresCostStore.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Marcus Johnson", "David Chen", "Lisa Patel"],
      "dependencies": ["F-024"],
      "data_prereqs": ["cost_thresholds_config.yaml"],
      "acceptance": "CostController blocks execution when any of the 4 budget levels exceeds its hard threshold and emits a warning event when any level exceeds its warn threshold."
    },
    {
      "id": "F-026",
      "epic": "E3",
      "name": "Implement RateLimiter for API and agent calls",
      "description": "Token-bucket rate limiter applied per-agent and per-project. Prevents runaway loops and API abuse. Configurable burst and sustained rates. Input: rate limit config. Output: allow/throttle/reject decision. FIX-09.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Marcus Johnson", "Priya Mehta"],
      "dependencies": [],
      "data_prereqs": ["rate_limit_config.yaml"],
      "acceptance": "RateLimiter rejects the 11th request within 1 second when configured for a burst of 10, returning a RetryAfter response with correct wait time."
    },
    {
      "id": "F-027",
      "epic": "E3",
      "name": "Implement CircuitBreaker for external service calls",
      "description": "Circuit breaker pattern for Claude API, Slack, and PagerDuty calls. Tracks failure rates, opens circuit after threshold, attempts half-open probe after cooldown. Input: service call. Output: pass-through or CircuitOpenError.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Marcus Johnson", "Priya Mehta"],
      "dependencies": [],
      "data_prereqs": ["circuit_breaker_config.yaml"],
      "acceptance": "CircuitBreaker opens after 5 consecutive failures and rejects subsequent calls for 30 seconds, then allows a single probe call to test recovery."
    },
    {
      "id": "F-028",
      "epic": "E3",
      "name": "Build cost alert webhook notifications",
      "description": "Send Slack/PagerDuty notifications when cost thresholds are crossed. Supports configurable alert levels: 50%, 80%, 95%, 100% of budget. Input: cost event exceeding threshold. Output: webhook POST to Slack/PagerDuty. ADD-01.",
      "priority": "should",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["Marcus Johnson"],
      "dependencies": ["F-025", "F-038"],
      "data_prereqs": ["webhook_config.yaml", "slack_webhook_url"],
      "acceptance": "A Slack notification is delivered within 5 seconds when fleet daily spend crosses the 80% threshold."
    },
    {
      "id": "F-029",
      "epic": "E4",
      "name": "Implement ApprovalStore for gate management",
      "description": "Persistent store for approval gate state. Records gate creation, pending status, approver, decision (approve/reject/timeout), timestamp, and comments. Backed by PostgreSQL approvals table. FIX-02.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Sarah Kim", "David Chen"],
      "dependencies": ["F-046"],
      "data_prereqs": ["migration for approvals table", "approvals table DDL"],
      "acceptance": "ApprovalStore persists a gate request and returns the correct decision when queried after an approver submits approve or reject."
    },
    {
      "id": "F-030",
      "epic": "E4",
      "name": "Build approval gate integration in PipelineRunner",
      "description": "PipelineRunner pauses execution at configured approval gate steps, creates an approval request via ApprovalStore, sends notification, and resumes or aborts based on decision. Input: pipeline step marked as gate. Output: pipeline paused/resumed.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Sarah Kim", "David Chen"],
      "dependencies": ["F-006", "F-029"],
      "data_prereqs": ["approval_gate_config per pipeline"],
      "acceptance": "Pipeline pauses at an approval gate step, sends a Slack notification, and resumes within 10 seconds of receiving an approve decision."
    },
    {
      "id": "F-031",
      "epic": "E4",
      "name": "Implement Slack notification for approval gates",
      "description": "Send interactive Slack messages when an approval gate is triggered. Message includes pipeline context, generated artifact summary, and approve/reject buttons. Input: approval request. Output: Slack message with action buttons.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Sarah Kim"],
      "dependencies": ["F-029", "F-038"],
      "data_prereqs": ["slack_bot_token", "slack_channel_config"],
      "acceptance": "Slack message is delivered with approve/reject buttons and clicking approve triggers the ApprovalStore update within 5 seconds."
    },
    {
      "id": "F-032",
      "epic": "E4",
      "name": "Implement autonomy tiers T0-T3",
      "description": "Configure agents with autonomy tiers: T0 (fully autonomous, no gate), T1 (log only), T2 (approval required, auto-approve after timeout), T3 (approval required, block until human). Input: agent manifest tier field. Output: gating behavior per tier.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Sarah Kim", "Priya Mehta", "Lisa Patel"],
      "dependencies": ["F-029", "F-030"],
      "data_prereqs": ["autonomy_tier_config.yaml"],
      "acceptance": "A T3 agent blocks indefinitely at its approval gate until a human responds, while a T0 agent executes without any gate pause."
    },
    {
      "id": "F-033",
      "epic": "E5",
      "name": "Implement QualityScorer with rubric evaluation",
      "description": "Score agent outputs against configurable rubrics. Each rubric defines dimensions (completeness, accuracy, formatting, traceability) with weighted scores 1-10. Input: agent output + rubric definition. Output: score breakdown + aggregate score. ADD-08.",
      "priority": "should",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Sarah Kim", "David Chen"],
      "dependencies": ["F-001"],
      "data_prereqs": ["rubric_definitions per agent type", "quality_scoring_schema.json"],
      "acceptance": "QualityScorer evaluates a PRD agent output against its rubric and returns a score >= 0.0 and <= 10.0 with per-dimension breakdown."
    },
    {
      "id": "F-034",
      "epic": "E5",
      "name": "Build golden test suite for all 48 agents",
      "description": "Create golden test fixtures: known input + expected output pairs for each agent. Test runner compares agent output to golden reference using rubric scoring. Input: golden fixtures. Output: pass/fail per agent with score.",
      "priority": "must",
      "story_points": 13,
      "effort": "XL",
      "complexity": "high",
      "personas": ["Priya Mehta", "Sarah Kim"],
      "dependencies": ["F-001", "F-033"],
      "data_prereqs": ["golden_test_fixtures directory", "golden_inputs and golden_outputs per agent"],
      "acceptance": "All 48 agents have at least one golden test fixture and the test runner reports pass (score >= 8.0) or fail for each."
    },
    {
      "id": "F-035",
      "epic": "E5",
      "name": "Build adversarial test suite for agent robustness",
      "description": "Create adversarial test cases: malformed inputs, prompt injection attempts, excessively large payloads, and edge-case briefs. Verify agents fail gracefully with structured errors. Input: adversarial fixtures. Output: pass/fail per test.",
      "priority": "should",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Priya Mehta", "Sarah Kim"],
      "dependencies": ["F-001", "F-003"],
      "data_prereqs": ["adversarial_test_fixtures directory"],
      "acceptance": "All adversarial tests pass: agents return structured error responses (not stack traces) for every malformed input and no prompt injection produces unintended output."
    },
    {
      "id": "F-036",
      "epic": "E5",
      "name": "Enforce 90% test coverage in CI pipeline",
      "description": "Configure pytest-cov in the CI pipeline to enforce a minimum 90% line coverage threshold across all agent modules. Fail the CI build if coverage drops below threshold. Input: test suite. Output: coverage report + pass/fail gate.",
      "priority": "must",
      "story_points": 3,
      "effort": "S",
      "complexity": "low",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-034"],
      "data_prereqs": ["pytest.ini or pyproject.toml coverage config"],
      "acceptance": "CI pipeline fails with a clear message when any agent module has less than 90% line coverage."
    },
    {
      "id": "F-037",
      "epic": "E6",
      "name": "Implement 13-field JSONL audit event logging",
      "description": "Log every agent invocation as an immutable JSONL event with 13 fields: timestamp, event_id, agent_id, agent_version, session_id, project_id, phase, action, input_hash, output_hash, cost_usd, latency_ms, status. Write to both file and PostgreSQL audit_events table.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Lisa Patel", "Marcus Johnson"],
      "dependencies": ["F-001", "F-046"],
      "data_prereqs": ["audit_event_schema.json", "audit_events table DDL"],
      "acceptance": "Every agent invocation produces a JSONL line and a database row with all 13 fields populated, and rows cannot be updated or deleted (immutable)."
    },
    {
      "id": "F-038",
      "epic": "E6",
      "name": "Implement WebhookNotifier for external event delivery",
      "description": "Deliver audit events, cost alerts, and pipeline status updates to external systems via configurable webhooks (Slack, PagerDuty, custom HTTP). Supports retry with exponential backoff. Input: event + webhook config. Output: HTTP POST with delivery confirmation. ADD-01.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Marcus Johnson"],
      "dependencies": [],
      "data_prereqs": ["webhook_registry_config.yaml"],
      "acceptance": "WebhookNotifier delivers an event to a configured Slack webhook URL and retries up to 3 times with exponential backoff on 5xx responses."
    },
    {
      "id": "F-039",
      "epic": "E6",
      "name": "Implement PII detection in agent inputs and outputs",
      "description": "Scan agent inputs and outputs for personally identifiable information (email, phone, SSN, credit card patterns). Flag detected PII in audit events and optionally redact before storage. Input: text payload. Output: PII detection report with field locations.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Lisa Patel"],
      "dependencies": ["F-037"],
      "data_prereqs": ["pii_patterns_config.yaml", "pii_test_corpus"],
      "acceptance": "PII detector achieves >= 95% recall on the labeled PII test corpus and flags detected PII in the audit event metadata."
    },
    {
      "id": "F-040",
      "epic": "E6",
      "name": "Build real-time cost tracking aggregation queries",
      "description": "Provide SQL views and query functions for real-time cost aggregation: per-invocation, per-session, per-project, per-agent, fleet-daily. Used by dashboard and CostController. Input: query parameters. Output: cost aggregation results.",
      "priority": "must",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["Marcus Johnson", "Lisa Patel"],
      "dependencies": ["F-024"],
      "data_prereqs": ["cost_metrics table populated"],
      "acceptance": "Fleet daily cost query returns the correct sum of cost_usd for the current day within 500ms, matching the sum of individual invocation costs."
    },
    {
      "id": "F-041",
      "epic": "E6",
      "name": "Implement HealthServer with readiness and liveness probes",
      "description": "HTTP health server exposing /health/live (process alive), /health/ready (dependencies connected), and /health/startup (initialization complete) endpoints. Input: HTTP GET. Output: 200 OK with component status JSON.",
      "priority": "should",
      "story_points": 3,
      "effort": "S",
      "complexity": "low",
      "personas": ["Marcus Johnson"],
      "dependencies": [],
      "data_prereqs": [],
      "acceptance": "HealthServer returns 200 with all components healthy when PostgreSQL and Claude API are reachable, and 503 with failing component details when any dependency is down."
    },
    {
      "id": "F-042",
      "epic": "E7",
      "name": "Implement ExceptionPromotionEngine for knowledge flywheel",
      "description": "Capture agent exceptions, classify them, and promote recurring patterns into the 3-tier knowledge base: L1 (local agent memory), L2 (team shared), L3 (fleet-wide). Input: exception event + context. Output: knowledge base entry with promotion tier.",
      "priority": "should",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-001", "F-037"],
      "data_prereqs": ["exception_taxonomy.yaml", "knowledge_base_schema"],
      "acceptance": "An exception occurring 3 times within the same agent is promoted from L1 to L2, and an L2 entry occurring across 3 agents is promoted to L3."
    },
    {
      "id": "F-043",
      "epic": "E7",
      "name": "Build 3-tier knowledge base storage",
      "description": "Persistent storage for the 3-tier knowledge base. L1: per-agent in-memory cache. L2: per-team PostgreSQL table. L3: fleet-wide PostgreSQL table with full-text search. Input: knowledge entry. Output: stored and retrievable entry.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-046"],
      "data_prereqs": ["knowledge_base table DDL", "migration for knowledge tables"],
      "acceptance": "A knowledge entry stored at L3 is retrievable via full-text search by any agent in the fleet within 200ms."
    },
    {
      "id": "F-044",
      "epic": "E7",
      "name": "Integrate knowledge base lookups into BaseAgent pre_invoke",
      "description": "Before each agent invocation, query the knowledge base for relevant entries (matching agent type, error patterns, domain context). Inject relevant knowledge into the agent prompt context. Input: agent type + input context. Output: enriched prompt context.",
      "priority": "could",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-001", "F-043"],
      "data_prereqs": ["knowledge_query_strategy_config"],
      "acceptance": "An agent with a relevant L3 knowledge entry receives that entry in its prompt context and produces improved output compared to baseline without knowledge injection."
    },
    {
      "id": "F-045",
      "epic": "E8",
      "name": "Implement PipelineCheckpoint for resume-after-failure",
      "description": "Persist pipeline execution state after each completed step. On failure, the pipeline can resume from the last successful checkpoint instead of restarting. Stores step results, SessionStore snapshot, and cost accumulator. FIX-03.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["David Chen", "Marcus Johnson"],
      "dependencies": ["F-006", "F-004"],
      "data_prereqs": ["pipeline_runs table DDL", "checkpoint_schema.json"],
      "acceptance": "A 12-step pipeline that fails at step 7 resumes from step 7 (not step 1) after the failure is resolved, with steps 1-6 results loaded from checkpoint."
    },
    {
      "id": "F-046",
      "epic": "E8",
      "name": "Create PostgreSQL migrations 005 and 006",
      "description": "Author and apply database migrations: 005 creates session_context table, 006 creates cost_metrics table. Both migrations are idempotent and include rollback scripts. Input: migration SQL files. Output: tables created in PostgreSQL.",
      "priority": "must",
      "story_points": 3,
      "effort": "S",
      "complexity": "low",
      "personas": ["Priya Mehta"],
      "dependencies": [],
      "data_prereqs": ["existing migrations 001-004 applied"],
      "acceptance": "Migrations 005 and 006 run successfully on a fresh database and on a database with existing tables, creating session_context and cost_metrics tables with correct schemas."
    },
    {
      "id": "F-047",
      "epic": "E8",
      "name": "Implement SelfHealPolicy for automatic failure recovery",
      "description": "Define self-healing policies: retry with backoff, fallback to alternate model (Haiku instead of Sonnet), reduce output scope, skip optional steps. Policy engine evaluates failure type and selects recovery strategy. ADD-06.",
      "priority": "should",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Marcus Johnson", "Priya Mehta"],
      "dependencies": ["F-006", "F-045"],
      "data_prereqs": ["self_heal_policy_config.yaml"],
      "acceptance": "SelfHealPolicy retries a failed step with exponential backoff, and if retry fails, falls back to Haiku model and succeeds, logging the recovery action in audit events."
    },
    {
      "id": "F-048",
      "epic": "E8",
      "name": "Implement parallel DAG execution with fan-out/fan-in",
      "description": "Extend PipelineRunner to execute independent DAG branches in parallel using asyncio.gather. Fan-out distributes work to parallel agents; fan-in collects and merges results. Input: DAG with parallel branches. Output: merged results. FIX-06.",
      "priority": "must",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Priya Mehta", "David Chen"],
      "dependencies": ["F-006"],
      "data_prereqs": ["parallel_execution_config"],
      "acceptance": "Two independent DAG branches execute concurrently (verified by overlapping timestamps) and their results are correctly merged at the fan-in point."
    },
    {
      "id": "F-049",
      "epic": "E9",
      "name": "Implement agent version slots and registry",
      "description": "Each agent supports multiple version slots: production, canary, shadow. agent_registry table stores version metadata, slot assignment, and traffic weight. FIX-05. Input: agent ID + version + slot. Output: registered version slot.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Priya Mehta", "Marcus Johnson"],
      "dependencies": ["F-001", "F-046"],
      "data_prereqs": ["agent_registry table DDL with version columns"],
      "acceptance": "An agent can have production (v1.1) and canary (v1.2) slots simultaneously, and querying the registry returns both with correct traffic weights."
    },
    {
      "id": "F-050",
      "epic": "E9",
      "name": "Implement canary deployment with traffic splitting",
      "description": "Route a configurable percentage of requests to the canary version slot. Compare quality scores, latency, and error rates between production and canary. Auto-promote or rollback based on thresholds. Input: canary config. Output: traffic routing decision.",
      "priority": "should",
      "story_points": 8,
      "effort": "L",
      "complexity": "high",
      "personas": ["Priya Mehta", "Marcus Johnson"],
      "dependencies": ["F-049", "F-033"],
      "data_prereqs": ["canary_config.yaml", "promotion_thresholds"],
      "acceptance": "10% of requests are routed to canary slot and after 50 invocations with quality score delta < 0.5, the canary is auto-promoted to 100% traffic."
    },
    {
      "id": "F-051",
      "epic": "E9",
      "name": "Implement agent maturity progression tracking",
      "description": "Track agent maturity levels: draft, dry-run-passing, golden-test-passing, canary-validated, production. Maturity advances based on test results and deployment history. Input: test/deploy events. Output: updated maturity level.",
      "priority": "could",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-049", "F-034"],
      "data_prereqs": ["maturity_level_definitions"],
      "acceptance": "An agent that passes golden tests automatically advances from dry-run-passing to golden-test-passing maturity level in the registry."
    },
    {
      "id": "F-052",
      "epic": "E9",
      "name": "Implement automatic rollback on quality regression",
      "description": "Monitor canary quality scores in real-time. If canary quality score drops below production baseline by more than a configurable delta, automatically rollback to production version and alert the deployer. Input: quality score stream. Output: rollback action.",
      "priority": "could",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Priya Mehta", "Marcus Johnson"],
      "dependencies": ["F-050", "F-033"],
      "data_prereqs": ["rollback_threshold_config"],
      "acceptance": "Canary is automatically rolled back within 60 seconds when its quality score drops 1.0+ below the production baseline, and a Slack alert is sent."
    },
    {
      "id": "F-053",
      "epic": "E10",
      "name": "Implement per-project namespace isolation",
      "description": "Isolate project data using namespace prefixes on all database queries, file system paths, and session keys. Prevents data leakage between projects. Input: project_id. Output: namespaced access to all stores.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Lisa Patel", "David Chen"],
      "dependencies": ["F-004", "F-024"],
      "data_prereqs": ["project_namespace_config"],
      "acceptance": "An agent running in project A cannot read SessionStore keys belonging to project B, returning None for cross-project lookups."
    },
    {
      "id": "F-054",
      "epic": "E10",
      "name": "Implement per-project budget allocation",
      "description": "Allocate separate budgets per project with independent ceilings and tracking. CostController enforces project-level limits independently of fleet limits. Input: project budget config. Output: per-project cost enforcement.",
      "priority": "must",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["David Chen", "Marcus Johnson"],
      "dependencies": ["F-025", "F-053"],
      "data_prereqs": ["project_budget_config.yaml"],
      "acceptance": "Project A with a $25 ceiling is blocked when its spend reaches $25, even though fleet daily spend is only at $30 of $50."
    },
    {
      "id": "F-055",
      "epic": "E10",
      "name": "Implement per-client profile configuration",
      "description": "Store client-specific configuration profiles: preferred model tier, document templates, approval workflows, and quality thresholds. Input: client_id + profile settings. Output: persisted client profile applied to pipeline runs.",
      "priority": "could",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["David Chen"],
      "dependencies": ["F-053"],
      "data_prereqs": ["client_profile_schema.json"],
      "acceptance": "A pipeline run for client X uses client X's preferred model tier and quality thresholds instead of system defaults."
    },
    {
      "id": "F-056",
      "epic": "E1",
      "name": "Build fleet-wide agent dry-run validator",
      "description": "CLI command that executes dry-run validation for all 48 agents: loads manifest, validates schema, checks prompt file existence, verifies dependency resolution. Input: CLI flag --all. Output: pass/fail report per agent.",
      "priority": "must",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Priya Mehta"],
      "dependencies": ["F-001", "F-002", "F-003"],
      "data_prereqs": ["all agent manifests and prompt files"],
      "acceptance": "Running `agent dry-run --all` reports pass for all 48 agents or lists specific failures with actionable error messages."
    },
    {
      "id": "F-057",
      "epic": "E6",
      "name": "Build Streamlit fleet health dashboard page",
      "description": "Streamlit page displaying real-time fleet status: agent count by maturity, active pipeline runs, error rates (last 1h/24h), and system health indicators. Auto-refreshes every 30 seconds. Dashboard page 1 of 5. FIX-07.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Marcus Johnson"],
      "dependencies": ["F-037", "F-041"],
      "data_prereqs": ["audit_events and agent_registry tables populated"],
      "acceptance": "Fleet health dashboard displays agent count, active pipelines, and error rate, and auto-refreshes without manual browser reload."
    },
    {
      "id": "F-058",
      "epic": "E3",
      "name": "Build Streamlit cost monitor dashboard page",
      "description": "Streamlit page showing cost breakdown: fleet daily spend trend, per-project spend, per-agent spend, and budget utilization gauges. Includes drill-down from fleet to project to individual invocations. Dashboard page 2 of 5. FIX-07.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Marcus Johnson", "David Chen"],
      "dependencies": ["F-024", "F-040"],
      "data_prereqs": ["cost_metrics table populated"],
      "acceptance": "Cost monitor displays correct daily spend total matching the sum of per-project spends, and drill-down from fleet to project to invocation works."
    },
    {
      "id": "F-059",
      "epic": "E2",
      "name": "Build Streamlit pipeline runs dashboard page",
      "description": "Streamlit page showing pipeline run status: DAG visualization with step colors (green=done, blue=active, gray=pending, red=failed), progress percentage, elapsed time, and cost accumulator. Dashboard page 3 of 5. FIX-07.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["David Chen"],
      "dependencies": ["F-006", "F-045"],
      "data_prereqs": ["pipeline_runs table populated"],
      "acceptance": "Pipeline run dashboard shows a DAG with correctly colored step nodes that update in real-time as the pipeline progresses."
    },
    {
      "id": "F-060",
      "epic": "E6",
      "name": "Build Streamlit audit log dashboard page",
      "description": "Streamlit page for browsing audit events: filterable by date range, agent, project, session, and status. Shows 13-field detail view per event. Exportable to CSV. Dashboard page 4 of 5. FIX-07.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Lisa Patel"],
      "dependencies": ["F-037"],
      "data_prereqs": ["audit_events table populated"],
      "acceptance": "Audit log dashboard filters events by date range and agent ID, displays all 13 fields for a selected event, and exports filtered results to CSV."
    },
    {
      "id": "F-061",
      "epic": "E4",
      "name": "Build Streamlit approval queue dashboard page",
      "description": "Streamlit page showing pending approval gates: requester, pipeline context, artifact preview, approve/reject buttons, and history of past decisions. Dashboard page 5 of 5. FIX-07.",
      "priority": "should",
      "story_points": 5,
      "effort": "M",
      "complexity": "medium",
      "personas": ["Sarah Kim"],
      "dependencies": ["F-029", "F-030"],
      "data_prereqs": ["approvals table populated"],
      "acceptance": "Approval queue shows pending gates with artifact preview, and clicking approve updates the gate status and resumes the pipeline within 10 seconds."
    },
    {
      "id": "F-062",
      "epic": "E10",
      "name": "Implement multi-environment configuration management",
      "description": "Support dev, staging, and production environment configurations with isolated database connections, API keys, model tiers, and cost ceilings. Environment resolved from ENV_NAME variable. Input: environment name. Output: resolved config for all components.",
      "priority": "could",
      "story_points": 3,
      "effort": "M",
      "complexity": "low",
      "personas": ["Marcus Johnson", "Priya Mehta"],
      "dependencies": [],
      "data_prereqs": ["env_config_templates for dev/staging/prod"],
      "acceptance": "Setting ENV_NAME=staging resolves all configuration to staging values including database URL, API keys, and cost ceilings, without any production data access."
    }
  ]
}
```

---

## Priority Distribution Summary

| Priority | Count | Percentage |
| -------- | ----- | ---------- |
| must     | 26    | 41.9%      |
| should   | 24    | 38.7%      |
| could    | 8     | 12.9%      |
| wont     | 4     | 6.5%       |

**Note:** The `wont` features are not included in this catalog as they are explicitly excluded from scope. The 62 features above represent the build scope.

---

## Story Point Summary

| Epic | Name                            | Features | Total SP |
| ---- | ------------------------------- | -------- | -------- |
| E1   | Agent Orchestration             | 8        | 52       |
| E2   | 12-Document Generation Pipeline | 14       | 78       |
| E3   | Cost Control & Governance       | 5        | 29       |
| E4   | Human-in-the-Loop               | 5        | 25       |
| E5   | Quality Assurance               | 4        | 32       |
| E6   | Observability & Audit           | 6        | 26       |
| E7   | Knowledge Management            | 3        | 18       |
| E8   | Pipeline Resilience             | 4        | 27       |
| E9   | Agent Lifecycle                 | 4        | 21       |
| E10  | Multi-Project Isolation         | 4        | 14       |
| **Total** |                            | **62**   | **327**  |

---

## Dependency Graph — Critical Path

The critical path through the feature dependency graph:

```
F-046 (migrations)
  -> F-004 (SessionStore)
    -> F-006 (PipelineRunner)
      -> F-009 (12-doc DAG)
        -> F-010..F-021 (12 doc agents)

F-046 (migrations)
  -> F-024 (PostgresCostStore)
    -> F-025 (CostController)
      -> F-028 (cost alerts)

F-046 (migrations)
  -> F-029 (ApprovalStore)
    -> F-030 (approval gates in pipeline)
      -> F-031 (Slack notifications)
```

**Foundation blockers (must build first):** F-046, F-001, F-002, F-003, F-004, F-024

---

## FIX/ADD Traceability

| Gap ID | Feature(s)         | Description                        |
| ------ | ------------------ | ---------------------------------- |
| FIX-01 | F-004              | SessionStore                       |
| FIX-02 | F-029, F-030       | Approval gates                     |
| FIX-03 | F-045              | Pipeline checkpoint/resume         |
| FIX-04 | F-024              | PostgresCostStore fail-safe        |
| FIX-05 | F-049              | Agent versioning                   |
| FIX-06 | F-006, F-048       | Parallel pipeline DAG              |
| FIX-07 | F-057-F-061        | Streamlit dashboard (5 pages)      |
| FIX-08 | F-003              | Input/output validation            |
| FIX-09 | F-026              | Rate limiter                       |
| FIX-10 | F-022              | Complete all 48 prompt files       |
| ADD-01 | F-038, F-028       | Webhook callbacks                  |
| ADD-06 | F-047              | Self-healing pipeline              |
| ADD-08 | F-033              | Quality scoring                    |
| ADD-10 | F-008              | 5 missing team pipelines           |
| ADD-12 | F-023              | 9 missing agents                   |
