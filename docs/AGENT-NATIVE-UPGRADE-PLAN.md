# Agent-Native Upgrade Plan

**Current Score:** 50.7% (36.5/72) — 🟡 Agent-Compatible
**Target Score:** 70%+ (50+/72) — 🟢 Agent-Native
**Reference:** `AI_Ready_Standards_Architect_Commentary 3.md` (11 layers, 90+ standards)
**Status:** PLANNED — Do NOT start until v1 is shipped and in use

---

## Why Not Now

The platform has 61 working agents, 144 passing tests, and a clean 9/9 validation gate. These upgrades require cascading changes across 34 REST routes, 35 MCP tools, test mocks, and 6+ generated docs. Doing this now risks breaking a stable v1 for a score improvement. Ship first, upgrade surgically.

---

## Sprint Plan (3 sprints)

### Sprint A: Context Efficiency (0.5 → 2.0, biggest score jump)

**Score impact: +4.5 weighted points (×3 weight)**

| Task | What to do | Files affected |
|------|-----------|----------------|
| `?fields=` sparse fieldsets | Add field selection to all GET endpoints | api/routes/*.py, middleware, tests |
| `X-Total-Count` header | Return total count on all list endpoints | api/routes/*.py, tests |
| `X-Estimated-Tokens` header | Estimate response token count | api/middleware/ |
| `?representation=summary` | Add summary mode for large entities | api/routes/*.py |
| `Accept: text/markdown` | Markdown response option for agent prompts | api/middleware/ |
| Update docs | API-CONTRACTS (Doc 11), MCP-TOOL-SPEC (Doc 08) | Generated-Docs/ |

### Sprint B: Execution Layer (1.0 → 2.0)

**Score impact: +2 weighted points (×2 weight)**

| Task | What to do | Files affected |
|------|-----------|----------------|
| `Idempotency-Key` header | Server-side key store (Redis/PostgreSQL), enforce on mutations | api/middleware/, new table |
| `?dry_run=true` | Execute validation without committing, return preview | api/routes/*.py, services/*.py |
| Bulk operations | Batch create/update with per-item error reporting | api/routes/*.py, services/*.py |
| `If-Match` / ETag | Optimistic concurrency on mutations | api/middleware/, services/*.py |
| `Retry-After` header | Return on 429 with backoff guidance | api/middleware/ |
| Update docs | API-CONTRACTS, TESTING, QUALITY NFRs | Generated-Docs/ |

### Sprint C: Event Systems (1.0 → 2.0)

**Score impact: +1 weighted point (×1 weight)**

| Task | What to do | Files affected |
|------|-----------|----------------|
| CloudEvents format | Standardize all events to CloudEvents v1.0 spec | services/audit_service.py, schemas/ |
| Event replay endpoint | `GET /events?since=<timestamp>` for catch-up | api/routes/, services/ |
| Before/after snapshots | State change events carry delta | services/*.py |
| SSE with `Last-Event-ID` | Reconnection support for real-time streams | api/routes/, WebSocket handlers |
| Update docs | FAULT-TOLERANCE, TESTING, INFRA-DESIGN | Generated-Docs/ |

---

## Additional Quick Wins (can do anytime, low risk)

| Task | Score impact | Effort |
|------|-------------|--------|
| Add `/capabilities` endpoint listing all MCP tools + REST endpoints | Capability +0.5 | 2 hours |
| Add `X-Correlation-ID` propagation through full chain | Already mostly done | 1 hour |
| Add side-effect declarations to MCP tool schemas | Determinism +0.5 | 3 hours |
| Add `Sunset` header on deprecated endpoints | Evolution +0.5 | 1 hour |
| Add per-capability health at `/health/agent` | Observability +0.5 | 2 hours |

---

## Score Projection

| Phase | Score | Rating |
|-------|-------|--------|
| Current (v1) | 36.5/72 (50.7%) | 🟡 Agent-Compatible |
| After Sprint A | 41/72 (56.9%) | 🟢 Agent-Native |
| After Sprint B | 43/72 (59.7%) | 🟢 Agent-Native |
| After Sprint C | 44/72 (61.1%) | 🟢 Agent-Native |
| After Quick Wins | 46.5/72 (64.6%) | 🟢 Agent-Native (solid) |

---

## Decision Log

| Date | Decision | Reason |
|------|----------|--------|
| 2026-04-06 | Defer to post-v1 | 61 agents working, cascading changes risk stability |
| | | Ship v1 → collect feedback → upgrade surgically |
