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

### Quality Criteria
- Shared services rule is the FIRST rule file
- /new-interaction skill creates all layers in one command
- Rules enforce that logic never lives in interface handlers

### Anti-Patterns to Avoid
- No shared-services rule (logic will leak into handlers)
- Separate skills for MCP and REST without a unified skill
