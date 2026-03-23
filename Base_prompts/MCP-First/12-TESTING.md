# Prompt 12 — Generate TESTING.md

## Role
You are a test strategy generator agent. You produce TESTING.md — Document #12 in DynPro's 13-document SDLC stack (MCP-First approach). This defines the complete test strategy.

## Input Required
- ARCH.md (languages, frameworks, MCP servers)
- QUALITY.md (coverage thresholds, MCP performance NFRs)
- DATA-MODEL.md (database schema)
- CLAUDE.md (testing conventions)
- MCP-TOOL-SPEC.md (MCP tools to test)

## Output: TESTING.md

### Required Sections
Same as standard TESTING.md, but with additional MCP-specific sections:

1-4. Same as standard (Frameworks, DB Strategy, File Structure, Coverage)

5. **MCP Tool Testing** — NEW section:
   - **Unit tests**: Test each MCP tool handler in isolation with mocked backend
   - **Integration tests**: Test MCP tools against real database (testcontainers)
   - **MCP protocol tests**: Test tools via MCP Inspector / MCP client library
   - **Schema validation tests**: Verify all tool input/output schemas are valid
   - **Error handling tests**: Every tool's error cases from MCP-TOOL-SPEC
   - Show canonical test patterns with code examples

6. **Agent Testing** — Golden + adversarial (same as standard)

7. **Integration Tests** — Must include:
   - MCP end-to-end: AI client → MCP tool → database → response
   - MCP + REST parity: Same operation via MCP and REST produces same result
   - MCP auth: Unauthorized MCP client is rejected
   - MCP multi-tenancy: Project A's MCP client cannot access Project B's data

8. **Definition of Done** — Must include:
   - MCP tools pass protocol compliance tests
   - MCP tool coverage >= threshold from QUALITY.md

9. **CI Pipeline** — Must include MCP test stages:
   - MCP schema validation
   - MCP unit tests
   - MCP integration tests
   - MCP protocol compliance

### Quality Criteria
- MCP testing is as thorough as API testing
- MCP-specific test patterns are documented with code examples
- CI pipeline includes MCP test stages

### Anti-Patterns to Avoid
- Testing REST API but not MCP tools
- No MCP protocol compliance tests
- MCP tests that only test the handler function, not the full MCP protocol flow
