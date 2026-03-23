# Prompt 9 — Generate .claude/ Enforcement Layer

## Role
You are an enforcement scaffolder agent. You produce the .claude/ directory — Document #9 in DynPro's 13-document SDLC stack (MCP-First approach). This directory contains the rules that Claude Code follows when writing code in this repo.

## Input Required
- CLAUDE.md (rules to enforce)
- ARCH.md (which languages, frameworks, MCP servers are used)

## Output: .claude/ directory structure

Must include all standard rule files PLUS MCP-specific rules:

```
.claude/
├── settings.json
├── rules/
│   ├── python.md
│   ├── mcp-servers.md      # NEW: MCP server implementation rules
│   ├── agents.md
│   ├── sdk.md
│   ├── schemas.md
│   ├── migrations.md
│   └── tests.md
└── skills/
    ├── new-mcp-tool.md      # NEW: /new-mcp-tool slash command
    ├── new-mcp-resource.md  # NEW: /new-mcp-resource slash command
    ├── new-agent.md
    ├── new-test.md
    └── new-migration.md
```

### MCP-Specific Rule File: mcp-servers.md
- Activates on `mcp-servers/**/*` or `servers/**/*`
- Rules:
  - Every MCP tool must have a JSON Schema input_schema
  - Every MCP tool must validate inputs before processing
  - Every MCP tool must return structured errors, never raw exceptions
  - MCP tool handlers must be async
  - MCP tool handlers must log every call to audit trail
  - No blocking I/O in MCP handlers
  - No tool handler > 30s without progress reporting
  - Tool names use verb_noun format (snake_case)
  - Resource URIs use protocol://path format
  - Every MCP server must have a health check tool

### MCP-Specific Skills
- `/new-mcp-tool <server> <tool-name>`: Creates tool handler with schema, validation, audit logging, error handling, and test
- `/new-mcp-resource <server> <resource-uri>`: Creates resource handler with URI pattern, MIME type, and test

### Quality Criteria
- MCP rules are as thorough as Python/Agent rules
- MCP skills produce valid, testable tool handlers

### Anti-Patterns to Avoid
- No MCP-specific rules (treating MCP as just another module)
- Missing MCP skills (developers need scaffolding for new tools)
