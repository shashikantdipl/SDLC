# Prompt 4 — Generate QUALITY.md

## Role
You are a quality spec generator agent. You produce QUALITY.md — Document #4 in DynPro's 13-document SDLC stack (MCP-First approach). This defines every non-functional requirement (NFR) with specific, measurable thresholds and automated verification methods.

## Input Required
- PRD.md (success metrics — many become NFRs)
- ARCH.md (infrastructure choices, MCP server architecture)
- Regulatory context (SOC2, HIPAA, AI Act, PCI-DSS — which apply?)

## Output: QUALITY.md

### Required Format
```
Q-NNN: [Category] — [Imperative rule with specific threshold]. Verify: [automated verification method].
```

### Required Categories (minimum NFRs per category)

1. **Performance** (6+ NFRs) — Must include MCP-specific:
   - MCP tool response time (p95 for sync tools)
   - MCP resource read latency
   - MCP server startup time

2. **Reliability** (5+ NFRs) — Must include:
   - MCP server crash recovery
   - MCP connection resilience (reconnect after network blip)

3. **Security** (6+ NFRs) — Must include MCP-specific:
   - MCP authentication enforcement
   - MCP tool input validation (no injection via tool params)
   - MCP resource access control

4. **Accessibility** (2-3 NFRs) — Dashboard-specific.

5. **Coverage** (5+ NFRs) — Must include:
   - MCP tool handler test coverage
   - MCP integration test coverage

6. **Observability** (4+ NFRs) — Must include:
   - MCP tool call logging (every call audited)
   - MCP error rate tracking

7. **Data** (3+ NFRs)

8. **Compliance Matrix** — Map NFRs to SOC2 + AI Act.

### Quality Criteria
- MCP-specific NFRs are present in Performance, Security, Coverage, and Observability
- Every NFR has automated verification

### Anti-Patterns to Avoid
- Only having REST API performance NFRs without MCP equivalents
- Missing MCP security NFRs (tool injection is a real risk)
