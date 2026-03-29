# Prompt 12 — Generate .claude/ Enforcement Layer

## Role
You are an enforcement scaffolder agent. You produce the .claude/ directory — Document #12 in the 14-document SDLC stack (Full-Stack-First approach).

## Input Required
- CLAUDE.md (rules to enforce)
- ARCH.md (languages, frameworks, MCP servers, dashboard)

## Output: .claude/ directory structure

```
.claude/
├── settings.json
├── rules/
│   ├── python.md
│   ├── shared-services.md    # NEW: Shared service layer rules
│   ├── mcp-servers.md        # MCP server implementation rules
│   ├── api-routes.md         # REST API route rules
│   ├── dashboard.md          # Dashboard component rules
│   ├── agents.md
│   ├── schemas.md
│   ├── migrations.md
│   └── tests.md
└── skills/
    ├── new-interaction.md     # NEW: /new-interaction (creates service + MCP tool + REST route + dashboard component)
    ├── new-mcp-tool.md        # /new-mcp-tool
    ├── new-api-route.md       # /new-api-route
    ├── new-dashboard-view.md  # /new-dashboard-view
    ├── new-agent.md
    ├── new-test.md
    └── new-migration.md
```

### The Key Rule: shared-services.md
- ALL business logic lives in services/ directory
- MCP tool handlers ONLY call service methods
- REST route handlers ONLY call service methods
- Dashboard ONLY calls REST endpoints
- No logic duplication between MCP and REST handlers
- Every new feature starts with a shared service, then adds interfaces

### The Key Skill: /new-interaction
This is the flagship skill of Full-Stack-First. Running `/new-interaction <name>` scaffolds:
1. `services/<name>_service.py` — Shared service with methods
2. `mcp-servers/<server>/tools/<name>.py` — MCP tool handler calling service
3. `api/routes/<name>.py` — REST route handler calling service
4. `dashboard/views/<name>.py` — Dashboard component consuming REST
5. `tests/services/test_<name>.py` — Service unit tests
6. `tests/mcp/test_<name>.py` — MCP tool tests
7. `tests/api/test_<name>.py` — REST route tests
8. `tests/integration/test_<name>_fullstack.py` — Cross-interface integration test

### Rule: Prompt Versioning (rules/10-prompt-versioning.md)
- Every agent prompt (prompt.md) is versioned alongside its manifest
- Version format: SemVer (MAJOR.MINOR.PATCH)
  - MAJOR: Output schema changes, section additions/removals
  - MINOR: Instruction refinements that may change output quality
  - PATCH: Typo fixes, formatting, comments
- Every prompt change requires:
  1. Update version in manifest.yaml
  2. Run golden tests against new prompt
  3. Compare output quality score vs previous version
  4. If quality drops > 5%, block merge and require review
- Model pinning: Manifests specify tier, not exact model ID — but production deployments pin to specific model version via LLM_MODEL_OVERRIDE
- No prompt changes in production without lifecycle review (G3 agent)

### Rule: API Governance (rules/11-api-governance.md)
- All REST endpoints follow the envelope format from API-CONTRACTS.md
- All MCP tools follow the naming convention from MCP-TOOL-SPEC.md
- Versioning: API version in URL path (/api/v1/) — increment on breaking change
- Deprecation: Minimum 2 sprint warning before removing endpoint
- New endpoints require: OpenAPI spec entry, integration test, MCP parity check
- Rate limits defined per endpoint in API-CONTRACTS — enforced by middleware

### Quality Criteria
- Shared services rule is the FIRST rule file
- /new-interaction skill creates all layers in one command
- Rules enforce that logic never lives in interface handlers

### Anti-Patterns to Avoid
- No shared-services rule (logic will leak into handlers)
- Separate skills for MCP and REST without a unified skill
