# Prompt 13 — Generate BACKLOG.json

## Role
You are a backlog builder agent. You produce BACKLOG.json — Document #13 in the 24-document SDLC stack (Full-Stack-First approach).

## Input Required
- FEATURE-CATALOG.json
- PRD.md
- ARCH.md
- QUALITY.md
- MCP-TOOL-SPEC.md
- DESIGN-SPEC.md
- INTERACTION-MAP.md

## Output: BACKLOG.json

### Required JSON Structure

```json
{
  "backlog_version": "1.0.0",
  "stories": [
    {
      "id": "S-001",
      "title": "Implement PipelineService.trigger()",
      "feature": "F-001",
      "sprint": 1,
      "story_points": 5,
      "layer": "service",
      "interaction_ids": ["I-001"],
      "mcp_tools": ["trigger_pipeline"],
      "dashboard_screens": [],
      "shared_service": "PipelineService",
      "interfaces": ["service"],
      "acceptance_criteria": [
        {
          "given": "A valid project_id and pipeline_name",
          "when": "PipelineService.trigger() is called",
          "then": "A PipelineRun record is created with status 'pending' and run_id returned"
        },
        {
          "given": "An invalid project_id",
          "when": "PipelineService.trigger() is called",
          "then": "Raises ProjectNotFoundError with project_id in message"
        }
      ],
      "depends_on": [],
      "definition_of_done": [
        "Service method implemented with type hints",
        "Unit tests pass (mocked DB)",
        "Integration tests pass (real DB via testcontainers)",
        "Error cases covered"
      ]
    },
    {
      "id": "S-002",
      "title": "Expose trigger_pipeline via MCP tool",
      "feature": "F-001",
      "sprint": 3,
      "story_points": 3,
      "layer": "mcp",
      "interaction_ids": ["I-001"],
      "mcp_tools": ["trigger_pipeline"],
      "dashboard_screens": [],
      "shared_service": "PipelineService",
      "interfaces": ["mcp"],
      "acceptance_criteria": [
        {
          "given": "A Claude Code session connected to the MCP server",
          "when": "User asks to trigger a pipeline",
          "then": "trigger_pipeline tool is called and returns PipelineRun shape within 5s"
        },
        {
          "given": "Invalid input (missing project_id)",
          "when": "trigger_pipeline tool is called",
          "then": "Returns structured MCP error with code 'VALIDATION_ERROR'"
        }
      ],
      "depends_on": ["S-001"],
      "definition_of_done": [
        "MCP tool handler calls PipelineService.trigger()",
        "Input schema validates all required fields",
        "MCP Inspector shows correct schema",
        "Audit log records tool call",
        "Parity test: MCP response == REST response"
      ]
    },
    {
      "id": "S-003",
      "title": "Pipeline Trigger Form on Dashboard",
      "feature": "F-001",
      "sprint": 4,
      "story_points": 3,
      "layer": "dashboard",
      "interaction_ids": ["I-001"],
      "mcp_tools": [],
      "dashboard_screens": ["Pipeline Trigger Form"],
      "shared_service": "PipelineService",
      "interfaces": ["dashboard"],
      "acceptance_criteria": [
        {
          "given": "Delivery Lead is logged into dashboard",
          "when": "They fill the trigger form and click 'Run Pipeline'",
          "then": "REST POST /api/v1/pipelines is called, form shows success with run_id"
        }
      ],
      "depends_on": ["S-001"],
      "definition_of_done": [
        "Form renders with project selector and pipeline dropdown",
        "Calls REST endpoint (not service directly)",
        "Shows loading, success, and error states",
        "Accessible (WCAG AA)"
      ]
    }
  ]
}
```

### Full-Stack Story Structure
Each story MUST include:
- `id`: S-NNN format
- `title`: What is being built
- `feature`: Which F-NNN feature this implements
- `sprint`: Target sprint number
- `story_points`: Effort estimate
- `layer`: "service" | "mcp" | "rest" | "dashboard" | "integration"
- `interaction_ids`: array of INTERACTION-MAP IDs this story implements
- `mcp_tools`: array of MCP tool names affected
- `dashboard_screens`: array of dashboard screen IDs affected
- `shared_service`: which shared service is being built/modified
- `interfaces`: which interfaces this story touches
- `acceptance_criteria`: array of Given/When/Then objects
- `depends_on`: array of S-NNN IDs
- `definition_of_done`: array of checkable statements

### Sprint Priority (Full-Stack-First)
1. **Sprint 1-2**: Shared services (the foundation everything builds on)
2. **Sprint 3-4**: MCP tools + REST endpoints (interface layer)
3. **Sprint 4-5**: Dashboard views (consumes REST endpoints)
4. **Sprint 5-6**: Cross-interface integration (handoff journeys)
5. **Sprint 6+**: Polish, performance, edge cases

### Full-Stack Acceptance Criteria
Stories that implement an interaction MUST have acceptance criteria for ALL interfaces:
```
Given: PipelineService.trigger() works
When: Called via MCP tool trigger_pipeline
Then: Returns PipelineRun shape within 5s

When: Called via REST POST /api/v1/pipelines
Then: Returns same PipelineRun shape within 5s

When: User clicks "Run Pipeline" on Dashboard
Then: Shows pipeline status with real-time updates
```

### Quality Criteria
- Shared service stories come first (Sprint 1-2)
- Every interaction from INTERACTION-MAP has stories across all its interfaces
- Cross-interface stories exist (MCP trigger → Dashboard approval)
- Acceptance criteria cover all interfaces the story touches

### Anti-Patterns to Avoid
- MCP stories and Dashboard stories as separate tracks with no integration
- No shared service stories (logic ends up in handlers)
- Stories that only test one interface when the feature spans multiple
