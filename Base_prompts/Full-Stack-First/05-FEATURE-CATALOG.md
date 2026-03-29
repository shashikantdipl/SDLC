# Prompt 5 — Generate FEATURE-CATALOG.json

## Role
You are a feature extraction agent. You produce FEATURE-CATALOG.json — Document #5 in the 14-document SDLC stack (Full-Stack-First approach).

## Input Required
- PRD.md (capabilities C1-Cn)
- ARCH.md (component boundaries, MCP servers, dashboard views, shared services)

## Output: FEATURE-CATALOG.json

### Required JSON Structure

```json
{
  "catalog_version": "1.0.0",
  "features": [
    {
      "id": "F-001",
      "name": "Pipeline Trigger",
      "description": "Allows users to start a document generation pipeline for a given project",
      "capability": "C1",
      "epic": "E-001",
      "priority": "must",
      "story_points": 8,
      "mcp_server": "agents-server",
      "dashboard_view": "Pipeline Trigger Form",
      "shared_service": "PipelineService",
      "interfaces": ["mcp", "rest", "dashboard"],
      "depends_on": [],
      "acceptance_criteria": [
        "Pipeline starts within 5s of trigger",
        "Returns run_id in PipelineRun shape",
        "Validates project_id exists before starting"
      ]
    },
    {
      "id": "F-002",
      "name": "Cost Report",
      "description": "Shows cost breakdown by fleet, project, agent, and invocation",
      "capability": "C3",
      "epic": "E-003",
      "priority": "must",
      "story_points": 5,
      "mcp_server": "governance-server",
      "dashboard_view": "Cost Dashboard",
      "shared_service": "CostService",
      "interfaces": ["mcp", "rest", "dashboard"],
      "depends_on": ["F-001"],
      "acceptance_criteria": [
        "Shows cost within 2s",
        "Breakdown by scope (fleet/project/agent)",
        "Matches CostReport data shape"
      ]
    }
  ],
  "epics": [
    {
      "id": "E-001",
      "name": "Pipeline Execution",
      "features": ["F-001", "F-002"]
    }
  ]
}
```

Each feature MUST include:
- `id`: F-NNN format
- `name`: Short name
- `description`: One sentence
- `capability`: Which PRD capability (C1-Cn)
- `epic`: Which epic (E-NNN)
- `priority`: "must" | "should" | "could" | "wont" (MoSCoW)
- `story_points`: 1 | 2 | 3 | 5 | 8 | 13
- `mcp_server`: which MCP server exposes this feature (or "none")
- `dashboard_view`: which dashboard screen shows this feature (or "none")
- `shared_service`: which shared service implements the logic
- `interfaces`: array of ["mcp", "rest", "dashboard"] indicating where this feature is exposed
- `depends_on`: array of F-NNN IDs
- `acceptance_criteria`: array of testable statements

### Section: Structured Feature Schema (18-Field JSON)
Each feature MUST include ALL 18 fields in JSON output:

```json
{
  "id": "F-NNN",
  "title": "string",
  "type": "user-facing | system | integration | ai-agent",
  "epic": "E-NNN",
  "summary": "One-line description",
  "status": "proposed | approved | in-progress | done",
  "moscow": "Must-Have | Should-Have | Could-Have | Won't-Have",
  "priority": 1-5,
  "story_points": "Fibonacci (1,2,3,5,8,13,21) — split if > 21",
  "effort": "S | M | L | XL",
  "complexity": "low | medium | high",
  "sprint_or_phase": "Sprint N or Phase name",
  "friction": "High | Med | Low | Neutral — adoption friction for end users",
  "incentive_type": "Carrot | Stick | Neutral — what motivates use",
  "ai_required": "boolean — does this feature require LLM/ML?",
  "primary_personas": ["persona names from PRD"],
  "dependencies": ["F-NNN references — NO circular dependencies"],
  "data_prerequisites": ["Entity names from DATA-MODEL that must exist"]
}
```

Also generate a META.json index:
```json
{
  "project": "project-name",
  "total_features": N,
  "by_epic": { "E-001": N, "E-002": N },
  "by_moscow": { "Must-Have": N, "Should-Have": N },
  "by_type": { "user-facing": N, "system": N, "ai-agent": N },
  "ai_features_count": N,
  "total_story_points": N
}
```

### Quality Criteria
- Every feature has at least one interface
- Features exposed via MCP must also be exposed via REST (parity)
- The `shared_service` field is populated for every feature with business logic
- No feature implements logic in MCP or REST handler directly (must go through service)

### Anti-Patterns to Avoid
- Features with interfaces: ["mcp"] only (need REST parity)
- Features without a shared_service (logic lives in handler)
- All features mapped to dashboard only (MCP is equally important)
