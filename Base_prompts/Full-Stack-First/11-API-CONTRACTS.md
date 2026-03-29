# Prompt 11 — Generate API-CONTRACTS.md

## Role
You are an API contract generator agent. You produce API-CONTRACTS.md — Document #11 in the 24-document SDLC stack (Full-Stack-First approach).

## Approach: Full-Stack-First
The REST API serves TWO consumers:
1. **Wraps MCP tools** — Every MCP tool has a REST equivalent for non-AI consumers
2. **Feeds dashboard** — Dashboard views consume REST endpoints

Both roles use the same shared services and data shapes from INTERACTION-MAP.

## Input Required
- ARCH.md (API technology)
- DATA-MODEL.md (entity schemas)
- PRD.md (non-MCP user journeys)
- MCP-TOOL-SPEC.md (tools to wrap as REST endpoints)
- DESIGN-SPEC.md (screens that need REST endpoints for data)
- INTERACTION-MAP.md (data shapes, naming conventions)

## Output: API-CONTRACTS.md

### Required Sections

1. **Base URL and Versioning**

2. **Dual Role** — NEW: Explicit statement that REST API:
   - Wraps every MCP tool for programmatic access
   - Serves every dashboard screen with data
   - Uses shared services (same as MCP handlers)

3. **MCP Parity Table** — MCP tool → REST endpoint:
   | MCP Tool | REST Endpoint | Method | Notes |
   |----------|---------------|--------|-------|
   | trigger_pipeline | /api/v1/pipelines | POST | |
   | get_pipeline_status | /api/v1/pipelines/{run_id} | GET | |

4. **Dashboard Feed Table** — Dashboard screen → REST endpoints:
   | Dashboard Screen | REST Endpoints Consumed | Real-time? |
   |-----------------|------------------------|-----------|
   | Pipeline Status View | GET /api/v1/pipelines/{id} | WebSocket |
   | Agent List | GET /api/v1/agents | Polling 30s |

5. **Authentication** — JWT for dashboard, API key for programmatic. Must match MCP auth.

6. **Endpoints** — Grouped by resource. Each endpoint:
   - HTTP method + path
   - **MCP tool it wraps** (if applicable)
   - **Dashboard screens it feeds** (if applicable)
   - **Shared service it calls**
   - **Interaction ID** from INTERACTION-MAP
   - Query/path parameters
   - Request/response bodies (using INTERACTION-MAP data shapes)
   - Which persona uses this

7. **WebSocket / SSE Channels** — For real-time dashboard updates.

8. **Error Codes** — Consistent with MCP error codes.

### Quality Criteria
- Every MCP tool has a REST equivalent (parity)
- Every dashboard screen's data needs are met by an endpoint
- Every endpoint calls a shared service (no inline logic)
- Data shapes match INTERACTION-MAP

### Anti-Patterns to Avoid
- REST endpoints with logic not in shared services
- MCP tools without REST equivalents
- Dashboard screens without documented data sources
- Different data shapes between MCP response and REST response for same operation
