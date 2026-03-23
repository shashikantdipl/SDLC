# DESIGN-SPEC — Agentic SDLC Platform
**Version:** v1.0 | Full-Stack-First | 2026-03-24
**Document:** 8 of 14 | Status: Draft
**Reads from:** INTERACTION-MAP (Doc 6) — all screen names, data shapes, and interaction IDs are defined there.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Screen Inventory](#2-screen-inventory)
3. [Screen Specifications](#3-screen-specifications)
4. [MCP Monitoring Panel](#4-mcp-monitoring-panel)
5. [Cross-Interface Handoff Screens](#5-cross-interface-handoff-screens)
6. [Component Library](#6-component-library)
7. [Responsive Behavior](#7-responsive-behavior)
8. [Real-Time Update Registry](#8-real-time-update-registry)

---

## Context

In Full-Stack-First, this document is written IN PARALLEL with MCP-TOOL-SPEC (Doc 7). Both read from the INTERACTION-MAP (Doc 6). Every screen references I-NNN interaction IDs and displays the exact data shapes defined in the INTERACTION-MAP.

The dashboard is the TERTIARY interface -- after MCP (for developers) and REST API (for programs). It serves human operators:

| Persona | Role | Primary Pages |
|---------|------|---------------|
| **Anika Patel** | Engineering Lead | Approval Queue, Pipeline Runs |
| **David Okonkwo** | DevOps Engineer | Fleet Health, Cost Monitor |
| **Fatima Al-Rashidi** | Compliance Officer | Audit Log, Cost Monitor |
| **Jason Park** | Tech Lead (both interfaces) | Fleet Health, Approval Queue |

### Quality NFRs Governing This Document

| NFR | Requirement | Impact on Design |
|-----|-------------|-----------------|
| Q-005 | Dashboard page load p95 < 2s | All pages must lazy-load heavy components; skeleton states mandatory |
| Q-006 | Fleet Health page < 1s | Agent grid must render from cached summary data; no detail fetch on load |
| Q-029 | WCAG 2.1 AA compliance | All components must pass axe-core automated checks |
| Q-030 | Keyboard navigation for all interactive elements | Tab order defined per screen; focus traps in modals |
| Q-031 | Screen reader support with ARIA labels | Every dynamic element has `aria-label`, `aria-live`, `role` attributes |
| Q-032 | Color contrast ratio >= 4.5:1 | All text/background combinations validated; status colors have text labels |

### Technology Stack

- **Framework:** Streamlit (Python)
- **Data fetching:** REST API calls to `/api/v1/*` endpoints (which delegate to shared service layer)
- **Real-time updates:** Polling via `st.experimental_rerun` with configurable intervals
- **State management:** Streamlit session state (`st.session_state`)
- **Charts:** Plotly (via `st.plotly_chart`)
- **Styling:** Custom CSS injected via `st.markdown` with `unsafe_allow_html=True`

---

## 1. Design Principles

### DP-1: MCP Awareness

The dashboard makes AI client activity VISIBLE to human operators. Every page that shows agent or pipeline data also shows the MCP context: who triggered it (human via MCP or system), which MCP tool was called, and what the AI client's intent was. The MCP Monitoring Panel on Fleet Health is the canonical window into AI behavior. Operators should never wonder "what is the AI doing right now?"

### DP-2: Shared Data Shapes

Every screen renders data shapes EXACTLY as defined in the INTERACTION-MAP (Doc 6). Field names in the UI map 1:1 to data shape field names. No client-side field renaming, no shape transformation in the dashboard layer. The dashboard calls REST endpoints, which call shared service methods, which return canonical shapes. If the shape changes, it changes everywhere simultaneously.

### DP-3: Operator-First

The dashboard is designed for non-developer operator personas: Anika (reviews approvals), David (monitors fleet health and cost), and Fatima (audits compliance). Every design decision prioritizes their workflows. Technical details (JSON payloads, API endpoints, agent manifest YAML) are hidden behind summary views with expand-on-demand detail panels. Jargon is replaced with plain language labels. Actions require at most 2 clicks from the landing page.

### DP-4: Glanceable

Key information is visible without scrolling. Each page opens with a summary bar of MetricCards showing the most critical numbers. Health states use color-coded StatusBadges visible at a glance. The Fleet Health page answers "is everything OK?" within 1 second of page load (Q-006). Cost Monitor shows budget utilization gauges that communicate status through size and color. Anomalies and urgent items surface at the top of every relevant page.

### DP-5: Actionable

Every data point leads to an action. A degraded agent badge links to rollback. A cost anomaly row links to investigation. A pending approval links to the approve/reject workflow. Data without actions is moved to detail panels; the primary view shows only information that enables a decision. Dead-end screens are prohibited -- every view has a "next step" affordance.

### DP-6: Cross-Interface Continuity

Workflows that span MCP and Dashboard maintain context. When Priya triggers a pipeline via MCP and it reaches an approval gate, Anika sees the full pipeline context on the Dashboard without asking Priya for details. Deep links enable direct navigation to specific pipeline runs, agents, or approvals. The `triggered_by` field on every entity indicates the origin interface. The dashboard never shows data that contradicts what MCP shows -- both read from the same service methods.

### DP-7: Graceful Degradation

Every screen defines four states: loading (skeleton), empty (no data), error (API unavailable), and populated (normal). Stale data is shown with a visible "Last updated: X ago" indicator rather than a blank screen. Polling failures show a warning banner but preserve the last-known data. Offline indicators appear within 5 seconds of connectivity loss.

---

## 2. Screen Inventory

| Screen ID | Name | Page | Primary Persona | Interaction IDs | Priority |
|-----------|------|------|-----------------|-----------------|----------|
| S-001 | Fleet Health Overview | Fleet Health | David, Jason | I-080 | P0 |
| S-002 | Agent Grid | Fleet Health | David, Jason | I-020 | P0 |
| S-003 | Agent Detail Panel | Fleet Health | David, Jason | I-021 | P0 |
| S-004 | Health Badges | Fleet Health | David | I-023 | P0 |
| S-005 | Version Management | Fleet Health | Jason, David | I-024, I-025, I-026 | P0 |
| S-006 | Maturity Badges | Fleet Health | Anika, Jason | I-027 | P1 |
| S-007 | MCP Monitoring Panel | Fleet Health | David, Jason | I-081, I-082 | P0 |
| S-010 | Cost Charts | Cost Monitor | David, Fatima | I-040 | P0 |
| S-011 | Budget Gauges | Cost Monitor | David, Fatima | I-041 | P0 |
| S-012 | Anomaly Alerts | Cost Monitor | David | I-048 | P0 |
| S-013 | Budget Settings | Cost Monitor | David | I-049 | P1 |
| S-014 | Period Selector | Cost Monitor | David, Fatima | -- (UI-only) | P0 |
| S-020 | Pipeline Trigger Form | Pipeline Runs | Anika | I-001, I-009 | P0 |
| S-021 | Pipeline Runs Table | Pipeline Runs | Anika | I-003 | P0 |
| S-022 | Pipeline Run Detail | Pipeline Runs | Anika, Jason | I-002 | P0 |
| S-023 | Document Viewer | Pipeline Runs | Anika | I-006 | P0 |
| S-024 | Pipeline Actions (Resume/Cancel) | Pipeline Runs | Anika, Jason | I-004, I-005, I-007 | P0 |
| S-030 | Audit Event Table | Audit Log | Fatima | I-042 | P0 |
| S-031 | Audit Summary Cards | Audit Log | Fatima | I-043 | P0 |
| S-032 | Audit Export Button | Audit Log | Fatima | I-044 | P0 |
| S-040 | Approval Queue Table | Approval Queue | Anika | I-045 | P0 |
| S-041 | Approval Detail Panel | Approval Queue | Anika | I-045, I-046, I-047 | P0 |
| S-042 | Approval History Tab | Approval Queue | Anika, Fatima | I-045 | P1 |

### Page-to-Screen Mapping

| Page | Route | Screens | Load SLA |
|------|-------|---------|----------|
| Fleet Health | `/fleet-health` | S-001, S-002, S-003, S-004, S-005, S-006, S-007 | < 1s (Q-006) |
| Cost Monitor | `/cost-monitor` | S-010, S-011, S-012, S-013, S-014 | < 2s (Q-005) |
| Pipeline Runs | `/pipeline-runs` | S-020, S-021, S-022, S-023, S-024 | < 2s (Q-005) |
| Audit Log | `/audit-log` | S-030, S-031, S-032 | < 2s (Q-005) |
| Approval Queue | `/approval-queue` | S-040, S-041, S-042 | < 2s (Q-005) |

---

## 3. Screen Specifications

---

### Page 1: Fleet Health (`/fleet-health`)

**Primary personas:** David (DevOps), Jason (Tech Lead)
**Load SLA:** < 1s at p95 (Q-006)
**Data sources:** `GET /api/v1/fleet/health` (I-080), `GET /api/v1/agents` (I-020), `GET /api/v1/mcp/status` (I-081), `GET /api/v1/audit/mcp-calls` (I-082)

#### ASCII Wireframe

```
+==============================================================================+
|  AGENTIC SDLC PLATFORM        [Fleet Health] [Cost] [Pipelines] [Audit] [Q]  |
+==============================================================================+
|                                                                              |
|  +-- S-001: Fleet Health Overview (I-080, FleetHealth) --------------------+ |
|  | [48/48 Healthy]  [0 Circuit Breakers]  [34ms Avg Resp]  [$142 Today]   | |
|  | [3 Active Pipes]  [2 Pending Approvals]  [Updated: 10s ago]            | |
|  +------------------------------------------------------------------------+ |
|                                                                              |
|  +-- S-002: Agent Grid (I-020, AgentSummary[]) --+  +-- S-007: MCP ------+ |
|  |                                                |  | Monitoring Panel   | |
|  |  Filter: [Phase v] [Status v] [Search___]      |  | (I-081, I-082)     | |
|  |                                                |  |                    | |
|  |  +------+ +------+ +------+ +------+ +------+ |  | MCP Server Health  | |
|  |  |Agent | |Agent | |Agent | |Agent | |Agent | |  | +----------------+ | |
|  |  |PRD   | |Arch  | |API   | |Test  | |Deploy| |  | |agents-srv  [OK]| | |
|  |  |Writer| |Draft | |Gen   | |Strat | |Orch  | |  | |gov-srv     [OK]| | |
|  |  |[OK]  | |[OK]  | |[DEG] | |[OK]  | |[CAN] | |  | |know-srv    [OK]| | |
|  |  |v1.2  | |v2.0  | |v1.1  | |v1.0  | |v0.9c | |  | +----------------+ | |
|  |  |$2.40 | |$1.80 | |$5.10 | |$0.90 | |$0.20 | |  |                    | |
|  |  +------+ +------+ +------+ +------+ +------+ |  | Connected Clients  | |
|  |  +------+ +------+ +------+ +------+ +------+ |  | Claude Code x 3    | |
|  |  |...   | |...   | |...   | |...   | |...   | |  | API Client x 1     | |
|  |  +------+ +------+ +------+ +------+ +------+ |  |                    | |
|  |  (48 agents in 5x10 grid, colored by status)  |  | Recent MCP Calls   | |
|  |                                                |  | +----------------+ | |
|  +------------------------------------------------+  | |10:42 trigger.. | | |
|                                                       | |10:41 list_ag.. | | |
|  +-- S-003: Agent Detail Panel (slide-out) --------+  | |10:40 get_cos.. | | |
|  | (shown when agent tile is clicked)              |  | |10:39 check_b..| | |
|  | Agent: PRD Writer  |  Status: [Active]          |  | |10:38 get_fle..| | |
|  | Phase: plan  |  Archetype: writer                |  | +----------------+ | |
|  | Version: v1.2.0  |  Model: claude-opus-4-6       |  +--------------------+ |
|  | Maturity: [Assisted] (S-006)                    |                          |
|  | Cost Today: $2.40  |  Invocations: 12            |                          |
|  | Health: OK 34ms  |  Circuit Breaker: closed      |                          |
|  |                                                  |                          |
|  | [Promote v1.3c] [Rollback to v1.1] [Canary: 0%] | (S-005)                 |
|  +--------------------------------------------------+                         |
+==============================================================================+
```

#### S-001: Fleet Health Overview

**Interaction:** I-080 (get_fleet_health)
**Data shape:** `FleetHealth`
**Data source:** `GET /api/v1/fleet/health` wraps `HealthService.get_fleet_health()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Healthy agent count | `healthy_agents` / `total_agents` | MetricCard | Green if all healthy, amber if < 90%, red if < 80% |
| Circuit breakers open | `circuit_breakers_open` | MetricCard | Green if 0, red if > 0 |
| Average response time | `avg_response_ms` | MetricCard | Green < 200ms, amber < 500ms, red >= 500ms |
| Fleet cost today | `fleet_cost_today_usd` | MetricCard | Formatted as currency |
| Active pipelines | `active_pipelines` | MetricCard | Clickable, navigates to Pipeline Runs page |
| Pending approvals | `pending_approvals` | MetricCard | Clickable, navigates to Approval Queue page; red badge if > 0 |
| Last updated | `last_updated_at` | Timestamp | Shows "Xs ago" format; amber if > 60s stale |

**States:**
- **Loading:** Six skeleton MetricCard placeholders with pulsing animation
- **Empty:** N/A (fleet health always returns data; zero agents = all counts zero)
- **Error:** Red banner "Fleet health data unavailable -- last known: X ago" with retry button; preserves last cached values
- **Populated:** Six MetricCards in a single row

**Accessibility:**
- MetricCards have `aria-label="Healthy agents: 48 of 48"` format
- Color indicators supplemented with text labels (never color-only)
- Tab order: left-to-right across MetricCards

---

#### S-002: Agent Grid

**Interaction:** I-020 (list_agents)
**Data shape:** `AgentSummary[]`
**Data source:** `GET /api/v1/agents` wraps `AgentService.list_agents()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Agent tile name | `name` | Text | Truncated to 20 chars with tooltip for full name |
| Agent phase | `phase` | Text | plan / design / build / verify / deploy |
| Agent archetype | `archetype` | Text | writer / reviewer / orchestrator / validator |
| Status badge | `status` | StatusBadge | active=green, degraded=amber, offline=red, canary=blue |
| Active version | `active_version` | Text | Semver display |
| Cost today | `cost_today_usd` | Text | Formatted as "$X.XX" |
| Last invocation | `last_invocation_at` | Text | Relative time "Xm ago" |

**Filters (top bar):**
- Phase dropdown: all / plan / design / build / verify / deploy
- Status dropdown: all / active / degraded / offline / canary
- Text search: filters by `name` or `agent_id`

**Interactions:**
- Click agent tile --> opens S-003 Agent Detail Panel (slide-out from right)
- Keyboard: Enter/Space on focused tile opens detail panel
- Filter changes trigger re-render without full page reload

**States:**
- **Loading:** 48 skeleton tiles in grid layout with pulsing animation
- **Empty:** "No agents registered. Contact platform team." message with link to documentation
- **Error:** "Unable to load agent list" banner with retry button; grid shows last cached data if available
- **Populated:** 5-column grid of agent tiles, scrollable vertically

**Accessibility:**
- Grid uses `role="grid"` with `role="gridcell"` per tile
- Arrow keys navigate between tiles
- Status badge has `aria-label="Status: active"` (not color-dependent)
- Agent count announced: `aria-live="polite"` region shows "Showing 48 agents"

---

#### S-003: Agent Detail Panel

**Interaction:** I-021 (get_agent)
**Data shape:** `AgentDetail` (extends `AgentSummary`)
**Data source:** `GET /api/v1/agents/{agent_id}` wraps `AgentService.get_agent()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Agent name | `name` | Header (h3) | Full name, no truncation |
| Agent ID | `agent_id` | Monospace text | Copyable |
| Phase | `phase` | Text | |
| Archetype | `archetype` | Text | |
| Status | `status` | StatusBadge | |
| Active version | `active_version` | Text | |
| Canary version | `canary_version` | Text | null shows "--" |
| Canary traffic | `canary_traffic_pct` | Text + slider (S-005) | "0%" when no canary |
| Model | `model` | Text | e.g., "claude-opus-4-6" |
| Max tokens | `max_tokens` | Text | |
| Temperature | `temperature` | Text | |
| Tools | `tools` | Chip list | Each tool name as a chip |
| Prompt preview | `prompt_preview` | Collapsible text | First 500 chars, expand for full |
| Maturity level | `maturity.current_level` | StatusBadge (S-006) | supervised/assisted/autonomous/fully_autonomous |
| Override rate | `maturity.override_rate` | Text | Formatted as "X%" |
| Confidence avg | `maturity.confidence_avg` | Text | Formatted as "0.XX" |
| Promotion eligible | `maturity.promotion_eligible` | Badge | Green "Eligible" or gray "Not yet" |
| Health status | `health.healthy` | StatusBadge | |
| Response time | `health.response_time_ms` | Text | "Xms" |
| Circuit breaker | `health.circuit_breaker_open` | StatusBadge | Green "Closed" or red "Open" |
| Consecutive failures | `health.consecutive_failures` | Text | Red if > 0 |

**Interactions:**
- Slide-out panel from right side, 400px wide
- Close via X button, Escape key, or click outside panel
- Focus trapped within panel when open
- Promote / Rollback / Canary buttons at bottom (S-005)

**States:**
- **Loading:** Panel opens immediately with skeleton layout; data fills in on API response
- **Error:** "Unable to load agent details" message inside panel with retry button
- **Populated:** Full detail view

**Accessibility:**
- Panel has `role="dialog"` and `aria-labelledby` referencing agent name
- Focus moves to panel on open; returns to triggering tile on close
- All fields have associated labels

---

#### S-004: Health Badges

**Interaction:** I-023 (check_agent_health)
**Data shape:** `AgentHealth`
**Data source:** Embedded in `AgentDetail.health` from `GET /api/v1/agents/{agent_id}` or individually via `GET /api/v1/agents/{agent_id}/health` wrapping `AgentService.health_check()`

| Visual | Condition | ARIA Label |
|--------|-----------|------------|
| Green circle + "Healthy" | `healthy` = true, `circuit_breaker_open` = false | "Agent {name}: healthy, response time {response_time_ms}ms" |
| Amber triangle + "Degraded" | `healthy` = true, `consecutive_failures` > 0 | "Agent {name}: degraded, {consecutive_failures} recent failures" |
| Red circle + "Offline" | `healthy` = false | "Agent {name}: offline, error: {error_message}" |
| Blue diamond + "Canary" | Agent status = "canary" | "Agent {name}: canary deployment at {canary_traffic_pct}%" |

Badges appear on agent tiles (S-002) and in the agent detail panel (S-003). Color is always accompanied by shape and text label for accessibility.

---

#### S-005: Version Management

**Interactions:** I-024 (promote_agent_version), I-025 (rollback_agent_version), I-026 (set_canary_traffic)
**Data shape:** `AgentVersion`
**Data source:** `POST /api/v1/agents/{agent_id}/promote`, `POST /api/v1/agents/{agent_id}/rollback`, `PUT /api/v1/agents/{agent_id}/canary` wrapping `AgentService.promote_version()`, `.rollback_version()`, `.set_canary()`

| Element | Action | Confirmation | Notes |
|---------|--------|-------------|-------|
| Promote button | POST promote | ConfirmationDialog: "Promote {canary_version} to active? This replaces {active_version}." | Disabled if `canary_version` is null |
| Rollback button | POST rollback | ConfirmationDialog: "Rollback to {previous_version}? Current version {active_version} will be deactivated." | Disabled if `previous_version` is null |
| Canary slider | PUT canary | Immediate on slider release; debounced 500ms | Range 0-100 in steps of 5; shows "{canary_traffic_pct}%" label |

**Accessibility:**
- Buttons have `aria-label="Promote agent {name} from version {canary_version}"` format
- Canary slider has `aria-valuemin="0"`, `aria-valuemax="100"`, `aria-valuenow="{pct}"`
- Confirmation dialogs trap focus; Escape cancels

---

#### S-006: Maturity Badges

**Interaction:** I-027 (get_agent_maturity)
**Data shape:** `AgentMaturity`
**Data source:** Embedded in `AgentDetail.maturity` or via `GET /api/v1/agents/{agent_id}/maturity` wrapping `AgentService.get_maturity()`

| Level | Badge Color | Icon | ARIA Label |
|-------|-------------|------|------------|
| `supervised` | Gray | Shield with eye | "Maturity: supervised -- human reviews all outputs" |
| `assisted` | Blue | Shield with checkmark | "Maturity: assisted -- human reviews flagged outputs" |
| `autonomous` | Green | Shield with star | "Maturity: autonomous -- human reviews exceptions only" |
| `fully_autonomous` | Gold | Shield with crown | "Maturity: fully autonomous -- no human review required" |

Additional fields shown in S-003 detail panel:
- `override_rate` as percentage bar
- `confidence_avg` as numeric display
- `consecutive_days` as "X days at current level"
- `promotion_eligible` as green "Eligible for {next_level}" or gray "Not yet eligible"
- `promotion_criteria` as tooltip on eligibility badge

---

#### S-007: MCP Monitoring Panel

*Fully specified in Section 4.*

---

### Page 2: Cost Monitor (`/cost-monitor`)

**Primary personas:** David (DevOps), Fatima (Compliance)
**Load SLA:** < 2s at p95 (Q-005)
**Data sources:** `GET /api/v1/costs/report` (I-040), `GET /api/v1/costs/budget` (I-041), `GET /api/v1/costs/anomalies` (I-048), `PUT /api/v1/costs/thresholds` (I-049)

#### ASCII Wireframe

```
+==============================================================================+
|  AGENTIC SDLC PLATFORM        [Fleet] [Cost Monitor] [Pipelines] [Audit] [Q] |
+==============================================================================+
|                                                                              |
|  +-- S-014: Period Selector ---+                                             |
|  | [7d] [30d] [90d] Custom    |                                              |
|  +-----------------------------+                                             |
|                                                                              |
|  +-- S-011: Budget Gauges (I-041, BudgetStatus) -------------------------+  |
|  |                                                                        |  |
|  |  Fleet Budget         Project: Acme       Project: Beta                |  |
|  |  +-----------+        +-----------+        +-----------+               |  |
|  |  |    72%    |        |    91%    |        |    45%    |               |  |
|  |  |  $7,200   |        |  $4,550   |        |  $2,250   |               |  |
|  |  | of $10,000|        | of $5,000 |        | of $5,000 |               |  |
|  |  +-----------+        +-----------+        +-----------+               |  |
|  |   [OK]                 [AT RISK]            [OK]                       |  |
|  +------------------------------------------------------------------------+  |
|                                                                              |
|  +-- S-010: Cost Charts (I-040, CostReport) ---+  +-- S-012: Anomaly ---+  |
|  |                                              |  | Alerts (I-048)      |  |
|  |  Cost by Day (Line Chart)                    |  | CostAnomaly[]       |  |
|  |  $800 |          ___                         |  |                     |  |
|  |  $600 |    ___--/   \___                     |  | [!] agent-api-gen   |  |
|  |  $400 |___/              \___                |  |  $340 vs $120 exp   |  |
|  |  $200 |                      \               |  |  +183% HIGH         |  |
|  |       +--+--+--+--+--+--+--+                 |  |  10:30 today        |  |
|  |        M  T  W  T  F  S  S                   |  |                     |  |
|  |                                              |  | [!] proj-acme       |  |
|  |  Cost by Agent (Bar Chart)                   |  |  $4,550 vs $3,800   |  |
|  |  agent-prd     |========= $420               |  |  +20% MEDIUM        |  |
|  |  agent-arch    |======= $340                 |  |  09:15 today        |  |
|  |  agent-api     |============== $680          |  |                     |  |
|  |  agent-test    |==== $210                    |  | [Acknowledge All]   |  |
|  |  agent-deploy  |=== $150                     |  +---------------------+  |
|  +----------------------------------------------+                           |
|                                                                              |
|  +-- S-013: Budget Settings (I-049) -- (collapsible) --------------------+  |
|  |  Entity          Budget    Alert At   Current    Action                |  |
|  |  Fleet            $10,000   80%        72%       [Edit]               |  |
|  |  proj-acme        $5,000    80%        91%       [Edit]               |  |
|  |  proj-beta        $5,000    80%        45%       [Edit]               |  |
|  +------------------------------------------------------------------------+  |
+==============================================================================+
```

#### S-010: Cost Charts

**Interaction:** I-040 (get_cost_report)
**Data shape:** `CostReport`
**Data source:** `GET /api/v1/costs/report?scope={scope}&period_days={period}` wraps `CostService.get_report()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Total cost | `total_usd` | MetricCard | With `trend_pct` arrow (up=red, down=green) |
| Cost by day (line chart) | `breakdown[]` | Plotly line chart | X-axis: dates, Y-axis: `cost_usd` |
| Cost by entity (bar chart) | `breakdown[]` | Plotly horizontal bar | Sorted descending by `cost_usd`; shows `entity_name` and `cost_usd` |
| Token breakdown | `breakdown[].tokens_total` | Tooltip on bars | "X tokens, Y invocations, $Z avg/invocation" |
| Report timestamp | `generated_at` | Footnote text | "Report generated at: {timestamp}" |

**Scope switching:** Three tabs -- Fleet / Project / Agent. Fleet shows all entities in breakdown. Project groups by project_id. Agent shows individual agents. Scope maps to `CostReport.scope`.

**Interactions:**
- Hover on chart data points shows tooltip with `entity_name`, `cost_usd`, `invocation_count`, `avg_cost_per_invocation`
- Click bar segment navigates to drill-down (fleet -> project list, project -> agent list)
- Period selector (S-014) changes `period_days` parameter

**States:**
- **Loading:** Chart area shows skeleton rectangle; MetricCard shows "--"
- **Empty:** "No cost data for selected period" with suggestion to expand date range
- **Error:** "Cost data unavailable" banner with retry; shows last cached chart if available
- **Populated:** Line chart + bar chart with hover tooltips

**Accessibility:**
- Charts have `aria-label="Cost by day line chart for {period_days} day period, total ${total_usd}"`
- Data table alternative available via "View as table" toggle below each chart
- Color-blind safe palette: use patterns (dashed, dotted) in addition to colors

---

#### S-011: Budget Gauges

**Interaction:** I-041 (check_budget)
**Data shape:** `BudgetStatus`
**Data source:** `GET /api/v1/costs/budget?scope={scope}&entity_id={id}` wraps `CostService.check_budget()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Gauge fill | `utilization_pct` | CostGauge | Circular or semicircular gauge |
| Spent amount | `spent_usd` | Text | Center of gauge |
| Budget total | `budget_usd` | Text | Below gauge: "of ${budget_usd}" |
| Remaining | `remaining_usd` | Text | Tooltip |
| At-risk indicator | `at_risk` | StatusBadge | Red "AT RISK" if true; green "OK" if false |
| Projected overrun | `projected_overrun_date` | Text | "Projected overrun: {date}" if not null |
| Alert threshold | `alert_threshold_pct` | CostGauge marker | Visual line on gauge at threshold percentage |

**Color thresholds for CostGauge:**
- 0-60%: Green
- 61-80%: Amber
- 81-100%: Red
- > 100%: Red with pulsing animation

**Interactions:**
- Click gauge opens S-013 Budget Settings for that entity
- Hover shows remaining amount and projected overrun date

**States:**
- **Loading:** Three skeleton gauge circles
- **Empty:** "No budgets configured" with link to S-013 to set up budgets
- **Error:** Gauge shows last known value with stale indicator
- **Populated:** Row of gauges, one per entity at the selected scope

**Accessibility:**
- Each gauge has `aria-label="Fleet budget: 72% utilized, $7,200 of $10,000 spent, status OK"`
- Text alternative always visible alongside gauge (not hidden behind hover)

---

#### S-012: Anomaly Alerts

**Interaction:** I-048 (get_cost_anomalies)
**Data shape:** `CostAnomaly[]`
**Data source:** `GET /api/v1/costs/anomalies` wraps `CostService.get_anomalies()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Entity name | `entity_name` | Text (bold) | |
| Entity type | `entity_type` | Badge | agent / project / pipeline |
| Actual cost | `actual_usd` | Text | Red text |
| Expected cost | `expected_usd` | Text | Gray text: "vs ${expected_usd} expected" |
| Deviation | `deviation_pct` | Text | "+{deviation_pct}%" |
| Severity | `severity` | StatusBadge | low=gray, medium=amber, high=orange, critical=red |
| Detected time | `detected_at` | Relative timestamp | "Xm ago" |
| Acknowledged | `acknowledged` | Checkbox / badge | Green "ACK" or pending |
| Acknowledged by | `acknowledged_by` | Text | Shown when acknowledged |

**Sorting:** Unacknowledged first, then by severity (critical > high > medium > low), then by `detected_at` descending.

**Interactions:**
- Click anomaly row expands to show cost breakdown context
- "Acknowledge" button marks anomaly as acknowledged (sets `acknowledged` = true, `acknowledged_by` = current user)
- "Investigate" button navigates to Cost Charts (S-010) filtered to that entity
- "Acknowledge All" button with confirmation dialog

**States:**
- **Loading:** Three skeleton rows
- **Empty:** Green banner "No cost anomalies detected" with checkmark
- **Error:** "Unable to check for anomalies" warning; shows stale data if available
- **Populated:** Scrollable list of anomaly rows, max 20 visible

**Accessibility:**
- Anomaly list uses `role="alert"` for critical severity items
- Each row has `aria-label` combining entity name, severity, and deviation
- Acknowledge button has `aria-label="Acknowledge anomaly for {entity_name}"`

---

#### S-013: Budget Settings

**Interaction:** I-049 (set_budget_threshold)
**Data shape:** `BudgetStatus` (input and output)
**Data source:** `PUT /api/v1/costs/thresholds` wraps `CostService.set_threshold()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Entity ID | `entity_id` | Text (read-only) | |
| Budget amount | `budget_usd` | Number input | Min $0, step $100 |
| Alert threshold | `alert_threshold_pct` | Slider | Range 50-100, step 5 |
| Current utilization | `utilization_pct` | Text (read-only) | For context |
| Save button | -- | Button | Calls PUT endpoint; ConfirmationDialog on save |

**Collapsible section** at the bottom of Cost Monitor page. Opens expanded when clicking a gauge in S-011.

---

#### S-014: Period Selector

**UI-only component** that controls the `period_days` parameter for S-010 and S-012.

| Option | Value | Notes |
|--------|-------|-------|
| 7d | `period_days=7` | Default selection |
| 30d | `period_days=30` | |
| 90d | `period_days=90` | |
| Custom | Date picker | Start date and end date pickers |

**Accessibility:** Radio button group with `aria-label="Select time period for cost data"`

---

### Page 3: Pipeline Runs (`/pipeline-runs`)

**Primary personas:** Anika (Engineering Lead), Jason (Tech Lead)
**Load SLA:** < 2s at p95 (Q-005)
**Data sources:** `POST /api/v1/pipelines/trigger` (I-001), `GET /api/v1/pipelines/{id}` (I-002), `GET /api/v1/pipelines` (I-003), `POST /api/v1/pipelines/{id}/resume` (I-004), `POST /api/v1/pipelines/{id}/cancel` (I-005), `GET /api/v1/pipelines/{id}/documents` (I-006), `POST /api/v1/pipelines/{id}/steps/{step}/retry` (I-007)

#### ASCII Wireframe

```
+==============================================================================+
|  AGENTIC SDLC PLATFORM        [Fleet] [Cost] [Pipeline Runs] [Audit] [Q]    |
+==============================================================================+
|                                                                              |
|  +-- S-020: Pipeline Trigger Form (I-001, I-009) ---------+                 |
|  |  Project: [Select project_____v]                        |                 |
|  |  Pipeline: [full-stack-first-14-doc v]                  |                 |
|  |  Brief: [                                           ]   |                 |
|  |         [                                           ]   |                 |
|  |  [Validate] [Trigger Pipeline]                          |                 |
|  |  Validation: [OK] All fields valid                      |                 |
|  +----------------------------------------------------------+                |
|                                                                              |
|  +-- S-021: Pipeline Runs Table (I-003, PipelineRun[]) -------------------+  |
|  |  Filter: [Status v] [Project v] [Triggered By___] [Date range]         |  |
|  |                                                                        |  |
|  |  Run ID            | Project     | Status    | Step    | Cost  | Time  |  |
|  |  +---------------------------------------------------------------------------+
|  |  | run-20260324-042 | proj-acme   | [RUNNING] | 7/14   | $14.2 | 12m   |  |
|  |  | run-20260324-041 | proj-beta   | [PAUSED]  | 6/14   | $11.8 | 18m   |  |
|  |  | run-20260323-040 | proj-acme   | [DONE]    | 14/14  | $22.1 | 28m   |  |
|  |  | run-20260323-039 | proj-gamma  | [FAILED]  | 9/14   | $15.6 | 20m   |  |
|  |  | run-20260322-038 | proj-beta   | [DONE]    | 14/14  | $19.8 | 25m   |  |
|  |  +----------------------------------------------------------------------+  |
|  |  [< Prev] Page 1 of 5 [Next >]                                         |  |
|  +-------------------------------------------------------------------------+  |
|                                                                              |
|  +-- S-022: Pipeline Run Detail (slide-out) (I-002, PipelineRun) --------+  |
|  |                                                                        |  |
|  |  Run: run-20260324-042  |  Project: proj-acme  |  Triggered by: Priya  |  |
|  |  Status: [RUNNING]  |  Cost: $14.20  |  Started: 10:30 today           |  |
|  |                                                                        |  |
|  |  +-- S-024: TimelineBar (pipeline step progress) -------------------+  |  |
|  |  | [OK] 01-PRD  [OK] 02-ARCH  [OK] 03-CLAUDE  ... [>>] 07-MCP  [ ] |  |  |
|  |  +------------------------------------------------------------------+  |  |
|  |                                                                        |  |
|  |  Step 7: MCP-TOOL-SPEC  |  Agent: D7-mcp-spec-writer  |  Running...   |  |
|  |  Confidence: --  |  Est. cost for step: $1.80                          |  |
|  |                                                                        |  |
|  |  [Resume] [Cancel] [Retry Step]   (S-024)                              |  |
|  |                                                                        |  |
|  |  +-- S-023: Document Viewer (I-006, PipelineDocument[]) -----------+   |  |
|  |  | Doc | Name              | Quality | Tokens | Agent              |   |  |
|  |  | 1   | PRD               | 0.92    | 4,200  | agent-prd-writer   |   |  |
|  |  | 2   | ARCH              | 0.88    | 5,100  | agent-arch-drafter |   |  |
|  |  | 3   | CLAUDE            | 0.95    | 3,800  | agent-claude-spec  |   |  |
|  |  | ... (click row to preview document content)                     |   |  |
|  |  +----------------------------------------------------------------+   |  |
|  +------------------------------------------------------------------------+  |
+==============================================================================+
```

#### S-020: Pipeline Trigger Form

**Interactions:** I-001 (trigger_pipeline), I-009 (validate_project_input)
**Data shapes:** `PipelineRun` (output of trigger), `ValidationResult` (output of validate)
**Data source:** `POST /api/v1/pipelines/trigger` wraps `PipelineService.trigger()`, `POST /api/v1/pipelines/validate` wraps `PipelineService.validate_input()`

| Element | Type | Validation | Notes |
|---------|------|-----------|-------|
| Project selector | Dropdown | Required; loads from project list | Shows `project_id` and project name |
| Pipeline selector | Dropdown | Required; loads from pipeline configs (I-008) | Default: "full-stack-first-14-doc" |
| Brief textarea | Multi-line text | Required; min 50 chars | Client brief or requirement description |
| Validate button | Button | -- | Calls I-009; shows ValidationResult inline |
| Trigger button | Button | Disabled until validation passes | Calls I-001; ConfirmationDialog showing estimated cost |
| Validation result | Inline panel | -- | Shows `valid` status, `errors[]`, `warnings[]` |

**Interactions:**
- "Validate" button calls validate endpoint; results show inline below form
- Green checkmark if `valid` = true; red error list if `valid` = false
- Warnings show as amber items (non-blocking)
- "Trigger Pipeline" enabled only after successful validation
- After trigger, form collapses and new run appears at top of S-021

**States:**
- **Loading:** Dropdowns show skeleton; form disabled
- **Empty:** Form ready for input (default state)
- **Error:** Red banner above form if trigger fails; preserves form input
- **Populated:** N/A (form resets after successful trigger)

**Accessibility:**
- All form fields have associated `<label>` elements
- Error messages linked to fields via `aria-describedby`
- Form submission announces result via `aria-live="assertive"` region

---

#### S-021: Pipeline Runs Table

**Interaction:** I-003 (list_pipeline_runs)
**Data shape:** `PipelineRun[]`
**Data source:** `GET /api/v1/pipelines?status={status}&project_id={project}&page={page}` wraps `PipelineService.list_runs()`

| Column | Field | Sortable | Notes |
|--------|-------|----------|-------|
| Run ID | `run_id` | No | Clickable, opens S-022 |
| Project | `project_id` | Yes | Shows project name |
| Status | `status` | Yes | StatusBadge: pending=gray, running=blue, paused=amber, completed=green, failed=red, cancelled=gray-strikethrough |
| Progress | `current_step` / `total_steps` | Yes | "7/14" format with mini progress bar |
| Cost | `cost_usd` | Yes | Formatted "$XX.XX"; red if approaching budget |
| Elapsed | computed from `started_at` | Yes | "Xm" or "Xh Ym" format |
| Triggered by | `triggered_by` | Yes | Shows persona name; MCP icon if triggered via MCP |
| Error | `error_message` | No | Truncated; tooltip for full message; only shown for failed runs |

**Filters:**
- Status: multi-select (pending, running, paused, completed, failed, cancelled)
- Project: dropdown from project list
- Triggered by: text search
- Date range: start and end date pickers

**Pagination:** 20 rows per page, server-side pagination.

**Interactions:**
- Click row opens S-022 Pipeline Run Detail panel
- Column header click toggles sort direction
- Filter changes re-fetch from API

**States:**
- **Loading:** Table header with 5 skeleton rows
- **Empty:** "No pipeline runs found. Trigger a pipeline using the form above." with arrow pointing to S-020
- **Error:** "Unable to load pipeline runs" with retry button
- **Populated:** Sortable, filterable table with pagination

**Accessibility:**
- Table uses `role="table"` with proper `role="row"` and `role="cell"`
- Sort indicators announced: `aria-sort="ascending"` or `"descending"`
- Status badges have text labels, not just color
- Pagination controls have `aria-label="Page navigation"`

---

#### S-022: Pipeline Run Detail

**Interaction:** I-002 (get_pipeline_status)
**Data shape:** `PipelineRun`
**Data source:** `GET /api/v1/pipelines/{run_id}` wraps `PipelineService.get_status()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Run ID | `run_id` | Header text | Monospace, copyable |
| Project | `project_id` | Text | With project name |
| Status | `status` | StatusBadge | Same colors as table |
| Triggered by | `triggered_by` | Text | With interface indicator (MCP / Dashboard / REST) |
| Started at | `started_at` | Timestamp | Absolute + relative |
| Completed at | `completed_at` | Timestamp | null shows "--" |
| Cost | `cost_usd` | Text | Running total, updates on poll |
| Error | `error_message` | Expandable text | Red box if present |
| Checkpoint | `checkpoint_step` | Text | "Can resume from step {checkpoint_step}" if failed |
| Step timeline | `current_step`, `total_steps`, `current_step_name` | TimelineBar | Visual progress through all 14 steps |

**Timeline bar** shows each step as a segment:
- Completed steps: green with checkmark
- Current step: blue with spinner
- Failed step: red with X
- Pending steps: gray with circle

**Interactions:**
- Real-time: polls every 10s for running pipelines (see Section 8)
- Click on a completed step in timeline opens that step's document in S-023
- Resume / Cancel / Retry buttons (S-024) appear contextually based on status

---

#### S-023: Document Viewer

**Interaction:** I-006 (get_pipeline_documents)
**Data shape:** `PipelineDocument[]`
**Data source:** `GET /api/v1/pipelines/{run_id}/documents` wraps `PipelineService.get_documents()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Document number | `doc_number` | Text | 1-14 |
| Document name | `doc_name` | Text (clickable) | e.g., "INTERACTION-MAP" |
| Document type | `doc_type` | Badge | "markdown" |
| Quality score | `quality_score` | Progress bar | 0.0-1.0; green > 0.8, amber > 0.6, red <= 0.6; null shows "--" |
| Token count | `token_count` | Text | Formatted with commas |
| Agent | `agent_id` | Text | Agent that generated the document |
| Content preview | `content` | Markdown renderer | Rendered markdown in a scrollable panel |
| Generated at | `generated_at` | Timestamp | |

**Interactions:**
- Click document row expands to show full `content` rendered as markdown
- "Copy content" button copies raw markdown to clipboard
- "Open in new tab" button opens document in full-screen view

**States:**
- **Loading:** Table with skeleton rows
- **Empty:** "No documents generated yet" (pipeline still running)
- **Error:** "Unable to load documents" with retry
- **Populated:** Table of documents; click to expand content

---

#### S-024: Pipeline Actions

**Interactions:** I-004 (resume_pipeline), I-005 (cancel_pipeline), I-007 (retry_pipeline_step)
**Data shape:** `PipelineRun` (returned after each action)
**Data source:** `POST /api/v1/pipelines/{run_id}/resume`, `POST /api/v1/pipelines/{run_id}/cancel`, `POST /api/v1/pipelines/{run_id}/steps/{step}/retry`

| Button | Visible When | Confirmation | API Call |
|--------|-------------|-------------|----------|
| Resume | `status` = "paused" or "failed", `checkpoint_step` not null | "Resume pipeline from step {checkpoint_step + 1}?" | PipelineService.resume() |
| Cancel | `status` = "running" or "paused" | "Cancel pipeline run-{run_id}? This cannot be undone." | PipelineService.cancel() |
| Retry Step | `status` = "failed" | "Retry step {current_step_name}? Cost will increase." | PipelineService.retry_step() |

After action: slide-out panel refreshes to show updated `PipelineRun` state.

---

### Page 4: Audit Log (`/audit-log`)

**Primary persona:** Fatima (Compliance Officer)
**Load SLA:** < 2s at p95 (Q-005)
**Data sources:** `GET /api/v1/audit/events` (I-042), `GET /api/v1/audit/summary` (I-043), `POST /api/v1/audit/export` (I-044)

#### ASCII Wireframe

```
+==============================================================================+
|  AGENTIC SDLC PLATFORM        [Fleet] [Cost] [Pipelines] [Audit Log] [Q]    |
+==============================================================================+
|                                                                              |
|  +-- S-031: Audit Summary Cards (I-043, AuditSummary) -------------------+  |
|  |                                                                        |  |
|  | [1,247 Total]  [15 Warning]  [3 Error]  [0 Critical]  [$847 Cost]    |  |
|  | [2 PII Det.]   Period: Last 7 days                                    |  |
|  +------------------------------------------------------------------------+  |
|                                                                              |
|  +-- Filters -----------------------------------------------------------------+
|  | Severity: [All v]  Agent: [All v]  Project: [All v]  Action: [All v]      |
|  | Date: [2026-03-17] to [2026-03-24]   PII Only: [ ]   [Apply] [Reset]     |
|  +----------------------------------------------------------------------------+
|                                                                              |
|  +-- S-030: Audit Event Table (I-042, AuditEvent[]) ---------------------+  |
|  |                                                                        |  |
|  |  Timestamp       | Agent         | Action           | Sev  | Cost    |  |
|  |  +----------------------------------------------------------------------+  |
|  |  | 10:42:15      | agent-prd     | pipeline.trigger | INFO | $0.00   |  |
|  |  | 10:41:03      | agent-arch    | agent.invoke     | INFO | $1.20   |  |
|  |  | 10:39:47      | agent-api     | agent.invoke     | WARN | $2.80   |  |
|  |  | 10:38:22      | --            | approval.approve | INFO | $0.00   |  |
|  |  | 10:35:11      | agent-test    | agent.invoke     | ERR  | $0.90   |  |
|  |  | ...                                                                 |  |
|  |  +----------------------------------------------------------------------+  |
|  |  [< Prev] Page 1 of 63 [Next >]    Showing 1,247 events              |  |
|  +------------------------------------------------------------------------+  |
|                                                                              |
|  +-- S-032: Export Controls (I-044, AuditReport) --------+                  |
|  |  Format: [PDF v]  [Export Report]                      |                  |
|  |  Last export: 2026-03-22 by Fatima  [Download again]  |                  |
|  +--------------------------------------------------------+                  |
+==============================================================================+
```

#### S-030: Audit Event Table

**Interaction:** I-042 (query_audit_events)
**Data shape:** `AuditEvent[]`
**Data source:** `GET /api/v1/audit/events?severity={sev}&agent_id={agent}&project_id={proj}&start={date}&end={date}&page={page}` wraps `AuditService.query_events()`

| Column | Field | Sortable | Notes |
|--------|-------|----------|-------|
| Timestamp | `timestamp` | Yes (default desc) | ISO 8601 formatted to local time |
| Agent | `agent_id` | Yes | "--" if null (system events) |
| Session | `session_id` | No | Truncated UUID, copyable on click |
| Project | `project_id` | Yes | "--" if null |
| Action | `action` | Yes | e.g., "pipeline.trigger", "agent.invoke" |
| Severity | `severity` | Yes | StatusBadge: info=blue, warning=amber, error=red, critical=red-pulsing |
| Cost | `cost_usd` | Yes | "$X.XX" format |
| Duration | `duration_ms` | Yes | "Xms" or "Xs" format |
| Tokens | `tokens_in` + `tokens_out` | Yes | "In: X / Out: Y" |
| PII | `pii_detected` | Yes | Red flag icon if true |

**Expandable row detail (click to expand):**
- `details` (JSON object): formatted as syntax-highlighted JSON
- `source_ip`: shown if not null
- `user_id`: shown if not null
- Full `session_id` (not truncated)

**Filters:**
- Severity: multi-select dropdown (info, warning, error, critical)
- Agent: dropdown of all known agents
- Project: dropdown of all known projects
- Action: dropdown of all known action types
- Date range: start date and end date pickers
- PII only: checkbox to filter `pii_detected` = true

**Pagination:** 25 rows per page, server-side.

**States:**
- **Loading:** Table header with 10 skeleton rows
- **Empty:** "No audit events match the selected filters" with suggestion to adjust filters
- **Error:** "Audit service unavailable" with retry; compliance alert
- **Populated:** Sortable, filterable, expandable table

**Accessibility:**
- Table uses standard `<table>` semantics
- Severity icons have text labels: `aria-label="Severity: warning"`
- PII flag has `aria-label="PII detected in this event"`
- Expand/collapse announced via `aria-expanded`
- Filter changes announce result count via `aria-live="polite"`

---

#### S-031: Audit Summary Cards

**Interaction:** I-043 (get_audit_summary)
**Data shape:** `AuditSummary`
**Data source:** `GET /api/v1/audit/summary?period={ISO interval}` wraps `AuditService.get_summary()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Total events | `total_events` | MetricCard | Plain count |
| Warning count | `by_severity["warning"]` | MetricCard | Amber if > 0 |
| Error count | `by_severity["error"]` | MetricCard | Red if > 0 |
| Critical count | `by_severity["critical"]` | MetricCard | Red pulsing if > 0 |
| Total cost | `total_cost_usd` | MetricCard | "$XXX.XX" format |
| PII detections | `pii_detections` | MetricCard | Red flag if > 0 |
| Period | `period` | Text | Formatted date range |

**Additional breakdowns (collapsible sections):**
- By agent: `by_agent` record rendered as horizontal bar chart
- By project: `by_project` record rendered as horizontal bar chart
- By action: `by_action` record rendered as horizontal bar chart

**States:**
- **Loading:** Six skeleton MetricCards
- **Empty:** All counts show 0 (valid state -- no events in period)
- **Error:** "Summary unavailable" with retry
- **Populated:** Six MetricCards in a row with optional breakdown charts below

---

#### S-032: Audit Export Button

**Interaction:** I-044 (export_audit_report)
**Data shape:** `AuditReport`
**Data source:** `POST /api/v1/audit/export` wraps `AuditService.export_report()`

| Element | Field | Notes |
|---------|-------|-------|
| Format selector | Dropdown: PDF / CSV / JSON | Maps to `AuditReport.format` |
| Export button | "Export Report" | Posts with current filter state; shows spinner while generating |
| Download link | `download_url` | Presigned URL, expires in 1 hour |
| Report metadata | `generated_at`, `record_count`, `size_bytes` | "Generated at X, Y records, Z KB" |
| Filters applied | `filters_applied` | Shows which filters were active at export time |

**Interactions:**
- Click "Export Report" sends current filter state to API
- Loading spinner while report generates (may take 5-15 seconds for large date ranges)
- Download link appears on completion; auto-download initiated
- Previous export shown as "Download again" link

**States:**
- **Loading:** Button disabled with spinner
- **Error:** "Export failed" with retry; shows error reason
- **Populated:** Download link with metadata

**Accessibility:**
- Export button has `aria-label="Export audit report as {format}"`
- Loading state announced: `aria-live="assertive"` "Generating report..."
- Download link announced: `aria-live="assertive"` "Report ready for download"

---

### Page 5: Approval Queue (`/approval-queue`)

**Primary persona:** Anika (Engineering Lead)
**Load SLA:** < 2s at p95 (Q-005)
**Data sources:** `GET /api/v1/approvals/pending` (I-045), `POST /api/v1/approvals/{id}/approve` (I-046), `POST /api/v1/approvals/{id}/reject` (I-047)

#### ASCII Wireframe

```
+==============================================================================+
|  AGENTIC SDLC PLATFORM        [Fleet] [Cost] [Pipelines] [Audit] [Approvals]|
+==============================================================================+
|                                                                              |
|  +-- Pending Count Banner ---------------------------------------------------+
|  |  [!] 2 approvals pending  |  Oldest: 12 minutes ago  |  1 expiring soon  |
|  +----------------------------------------------------------------------------+
|                                                                              |
|  [Pending (2)] [History]    <-- Tab selector (S-042)                         |
|                                                                              |
|  +-- S-040: Approval Queue Table (I-045, ApprovalRequest[]) -------------+  |
|  |                                                                        |  |
|  |  ID            | Pipeline       | Step        | Risk  | Expires | Age  |  |
|  |  +----------------------------------------------------------------------+  |
|  |  | appr-042    | full-stack-14  | 06-INTERACT | [MED] | 45m     | 12m  |  |
|  |  | appr-041    | full-stack-14  | 02-ARCH     | [HIGH]| 22m     | 38m  |  |
|  |  +----------------------------------------------------------------------+  |
|  +------------------------------------------------------------------------+  |
|                                                                              |
|  +-- S-041: Approval Detail Panel (slide-out) ----------------------------+  |
|  |                                                                        |  |
|  |  Approval: appr-042                                                    |  |
|  |  Pipeline: full-stack-first-14-doc  |  Run: run-20260324-042           |  |
|  |  Step: 06-INTERACTION-MAP  |  Agent: D6-interaction-mapper             |  |
|  |  Risk: [MEDIUM]  |  Requested: 12m ago  |  Expires in: 45m             |  |
|  |                                                                        |  |
|  |  Summary:                                                              |  |
|  |  "INTERACTION-MAP generated with 34 interactions covering 5 domains.    |  |
|  |   All data shapes validated. 2 warnings on naming consistency."        |  |
|  |                                                                        |  |
|  |  Context:                                                              |  |
|  |  +-- Pipeline context (from ApprovalRequest.context) ---------------+  |  |
|  |  | Project: proj-acme-2026                                          |  |  |
|  |  | Triggered by: Priya (via MCP trigger_pipeline)                   |  |  |
|  |  | Steps completed: 5/14  |  Cost so far: $11.80                   |  |  |
|  |  | Previous gate: 02-ARCH approved by Anika (2h ago)                |  |  |
|  |  +------------------------------------------------------------------+  |  |
|  |                                                                        |  |
|  |  Document Preview:                                                     |  |
|  |  +-- (rendered markdown of generated document) --------------------+   |  |
|  |  | # INTERACTION-MAP -- Agentic SDLC Platform                      |   |  |
|  |  | **Version:** v1.0 | Full-Stack-First | 2026-03-24               |   |  |
|  |  | ...                                                             |   |  |
|  |  +----------------------------------------------------------------+   |  |
|  |                                                                        |  |
|  |  +-- Actions -------------------------------------------------------+  |  |
|  |  | [Approve]                  [Reject]                               |  |  |
|  |  |                                                                   |  |  |
|  |  | Rejection comment (required if rejecting):                        |  |  |
|  |  | [____________________________________________________________]   |  |  |
|  |  | [____________________________________________________________]   |  |  |
|  |  +-------------------------------------------------------------------+  |  |
|  +------------------------------------------------------------------------+  |
+==============================================================================+
```

#### S-040: Approval Queue Table

**Interaction:** I-045 (list_pending_approvals)
**Data shape:** `ApprovalRequest[]`
**Data source:** `GET /api/v1/approvals/pending` wraps `ApprovalService.list_pending()`

| Column | Field | Sortable | Notes |
|--------|-------|----------|-------|
| Approval ID | `approval_id` | No | Truncated, clickable opens S-041 |
| Pipeline | `pipeline_name` | Yes | |
| Step | `step_name` | Yes | Step number and name: "06-INTERACTION-MAP" |
| Summary | `summary` | No | Truncated to 60 chars; tooltip for full text |
| Risk | `risk_level` | Yes | StatusBadge: low=green, medium=amber, high=orange, critical=red |
| Expires | `expires_at` | Yes (default asc) | Countdown timer: "Xm remaining"; red if < 15m |
| Age | computed from `requested_at` | Yes | "Xm ago" relative time |
| Run ID | `run_id` | No | Clickable, navigates to Pipeline Run Detail (S-022) |

**Default sort:** `expires_at` ascending (most urgent first).

**Interactions:**
- Click row opens S-041 Approval Detail Panel
- Expiring approvals (< 15m) highlighted with amber background
- Expired approvals removed from pending tab, appear in history tab

**States:**
- **Loading:** Table header with 3 skeleton rows
- **Empty:** Green banner "No pending approvals -- all caught up!" with checkmark
- **Error:** "Approval service unavailable" with retry; red alert (approval delays have SLA impact)
- **Populated:** Table sorted by urgency

**Accessibility:**
- Urgency communicated via text, not just color: "Expires in 22 minutes" vs "Expires in 3 minutes (URGENT)"
- Table row has `aria-label` combining step name, risk level, and expiry
- Countdown timers update `aria-live="polite"` every minute

---

#### S-041: Approval Detail Panel

**Interactions:** I-045 (context), I-046 (approve_gate), I-047 (reject_gate)
**Data shapes:** `ApprovalRequest` (display), `ApprovalResult` (action output)
**Data source:** `POST /api/v1/approvals/{approval_id}/approve` wraps `ApprovalService.approve()`, `POST /api/v1/approvals/{approval_id}/reject` wraps `ApprovalService.reject()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Approval ID | `approval_id` | Header text | |
| Pipeline name | `pipeline_name` | Text | |
| Run ID | `run_id` | Text (clickable) | Links to Pipeline Run Detail |
| Step | `step_number`, `step_name` | Text | "Step 6: INTERACTION-MAP" |
| Summary | `summary` | Text block | Full summary, not truncated |
| Risk level | `risk_level` | StatusBadge | With explanation text |
| Requested at | `requested_at` | Timestamp | Absolute + relative |
| Expires at | `expires_at` | Countdown | Red if < 15m; pulsing if < 5m |
| Pipeline context | `context` | Structured panel | Shows project, triggered_by, steps completed, cost, previous gate decisions |
| Document preview | Fetched via I-006 | Markdown renderer | Shows the document that needs approval |
| Approve button | -- | Primary button (green) | ConfirmationDialog: "Approve step {step_name}? Pipeline will resume." |
| Reject button | -- | Danger button (red) | Requires comment field below |
| Rejection comment | -- | Textarea | Mandatory when rejecting; min 10 chars |

**Approve flow (I-046):**
1. Click "Approve"
2. ConfirmationDialog appears: "Approve step {step_name} for pipeline {pipeline_name}?"
3. Confirm sends POST to approve endpoint
4. Returns `ApprovalResult` with `pipeline_resumed` = true
5. Success toast: "Approved. Pipeline resumed at step {step_number + 1}."
6. Approval removed from queue table; moves to history

**Reject flow (I-047):**
1. Enter comment in textarea (mandatory, min 10 chars)
2. Click "Reject"
3. ConfirmationDialog appears: "Reject step {step_name}? Your comment will be sent to the pipeline."
4. Confirm sends POST with `decision_comment`
5. Returns `ApprovalResult` with `pipeline_resumed` = false
6. Success toast: "Rejected with comment. Pipeline paused for revision."
7. Approval removed from queue; moves to history

**States:**
- **Loading:** Panel open with skeleton content
- **Error:** "Unable to load approval details" with retry
- **Populated:** Full detail view with action buttons

**Accessibility:**
- Panel has `role="dialog"` with `aria-labelledby` referencing approval ID
- Approve/Reject buttons have descriptive `aria-label` including step name
- Rejection comment field has `aria-required="true"` and `aria-describedby` pointing to helper text
- Focus trapped within panel; Escape closes (with confirmation if comment has been typed)

---

#### S-042: Approval History Tab

**Interaction:** I-045 (list_pending_approvals with status filter expanded to include all statuses)
**Data shape:** `ApprovalRequest[]` (with `status` in approved/rejected/expired/escalated)
**Data source:** `GET /api/v1/approvals?status=approved,rejected,expired,escalated&page={page}` wraps `ApprovalService.list_pending()` with expanded status filter

| Column | Field | Sortable | Notes |
|--------|-------|----------|-------|
| Approval ID | `approval_id` | No | |
| Pipeline | `pipeline_name` | Yes | |
| Step | `step_name` | Yes | |
| Decision | `status` | Yes | StatusBadge: approved=green, rejected=red, expired=gray, escalated=amber |
| Decided by | `decision_by` | Yes | "--" if expired |
| Decided at | `decided_at` | Yes (default desc) | "--" if expired |
| Comment | `decision_comment` | No | Truncated; click to expand |
| Response time | computed `decided_at` - `requested_at` | Yes | "Xm" format; red if > 15m (SLA breach) |

**Pagination:** 25 rows per page.

**Interactions:**
- Click row opens read-only detail panel (no approve/reject buttons)
- Filter by decision type (approved/rejected/expired)
- Date range filter

**States:**
- **Loading:** Table header with skeleton rows
- **Empty:** "No approval history yet"
- **Populated:** Historical table sorted by recency

---

## 4. MCP Monitoring Panel

**Screen ID:** S-007
**Location:** Right side of Fleet Health page (`/fleet-health`)
**Purpose:** Give operators VISIBILITY into what AI clients are doing via MCP. This is a first-class feature unique to Full-Stack-First -- operators should never wonder "what is the AI doing right now?"

### MCP Server Health

**Interaction:** I-081 (get_mcp_status)
**Data shape:** `McpServerStatus[]`
**Data source:** `GET /api/v1/mcp/status` wraps `HealthService.get_mcp_status()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Server name | `server_name` | Text | "agents-server", "governance-server", "knowledge-server" |
| Health indicator | `healthy` | StatusBadge | Green circle "Healthy" or red circle "Down" |
| Uptime | `uptime_seconds` | Text | Formatted as "Xd Xh Xm" |
| Tool count | `tool_count` | Text | Number of registered tools |
| Active connections | `active_connections` | Text | Current client connections |
| Requests/min | `requests_per_minute` | Text | Rolling 5-min average |
| Error rate | `error_rate_pct` | Text | Red if > 5% |
| Version | `version` | Text | Server version string |
| Last restart | `last_restart_at` | Relative timestamp | "Xd ago" or "Xh ago" |

**Layout:** Three rows (one per MCP server), each showing server name, health badge, and key metrics inline.

### Connected Clients

Derived from `McpServerStatus[].active_connections` and MCP call metadata.

| Element | Source | Notes |
|---------|--------|-------|
| Client count | Sum of `active_connections` across servers | Total active AI client connections |
| Client list | Derived from recent `McpCallEvent[].caller` | Distinct callers in last 5 minutes |
| Client type | Parsed from `caller` field | "Claude Code", "API Client", "CI/CD" |

### Recent MCP Calls Feed

**Interaction:** I-082 (list_recent_mcp_calls)
**Data shape:** `McpCallEvent[]`
**Data source:** `GET /api/v1/audit/mcp-calls?limit=20` wraps `AuditService.list_mcp_calls()`

| Element | Field | Component | Notes |
|---------|-------|-----------|-------|
| Timestamp | `timestamp` | Relative time | "Xs ago" format; updates live |
| Tool name | `tool_name` | Monospace text | e.g., "trigger_pipeline" |
| Server | `server_name` | Text | Abbreviated: "agents", "gov", "know" |
| Caller | `caller` | Text | AI client identifier |
| Project | `project_id` | Text | "--" if null |
| Duration | `duration_ms` | Text | "Xms"; amber if > 500ms, red if > 2s |
| Status | `status` | StatusBadge | success=green, error=red, timeout=amber |
| Cost | `cost_usd` | Text | "$X.XX" |
| Error | `error_message` | Tooltip | Only shown on hover for error/timeout status |

**Layout:** Scrollable feed of the 20 most recent MCP calls, newest at top. New calls appear at top with a brief highlight animation.

**Interactions:**
- Click call row expands to show full details (error message, tokens used)
- Filter by server, caller, or status (inline filter icons)
- "View all" link navigates to Audit Log page (S-030) pre-filtered for MCP calls

**Real-time:** Polls every 5 seconds (see Section 8). New calls animate in at top.

**States:**
- **Loading:** Three skeleton feed items
- **Empty:** "No MCP calls in the last hour" -- informational, not an error
- **Error:** "MCP call feed unavailable" with last-updated timestamp
- **Populated:** Scrollable feed with live updates

**Accessibility:**
- Feed has `role="log"` with `aria-live="polite"` (new items announced)
- Each entry has `aria-label` combining timestamp, tool name, and status
- Error entries have `aria-label` including "error" keyword for screen readers

### Panel Wireframe (Detail)

```
+-- S-007: MCP Monitoring Panel -------------------+
|                                                   |
|  MCP Server Health                                |
|  +---------------------------------------------+ |
|  | agents-server    [OK] 14d uptime  17 tools   | |
|  |   4 connections  42 req/min  0.2% errors     | |
|  +---------------------------------------------+ |
|  | governance-server [OK] 14d uptime  10 tools  | |
|  |   2 connections  28 req/min  0.0% errors     | |
|  +---------------------------------------------+ |
|  | knowledge-server  [OK] 14d uptime  4 tools   | |
|  |   1 connections  8 req/min   0.1% errors     | |
|  +---------------------------------------------+ |
|                                                   |
|  Connected Clients (7)                            |
|  Claude Code: Priya, Marcus, Jason                |
|  API Client: CI Pipeline                          |
|                                                   |
|  Recent MCP Calls          [View all -->]         |
|  +---------------------------------------------+ |
|  | 2s ago  trigger_pipeline   agents  [OK] $0.2 | |
|  | 15s ago list_agents        agents  [OK] $0.0 | |
|  | 22s ago get_cost_report    gov     [OK] $0.0 | |
|  | 34s ago check_budget       gov     [OK] $0.0 | |
|  | 41s ago get_fleet_health   agents  [OK] $0.0 | |
|  | 55s ago invoke_agent       agents  [OK] $1.8 | |
|  | 1m ago  list_pending_appr  gov     [OK] $0.0 | |
|  | 1m ago  get_agent          agents  [OK] $0.0 | |
|  | 2m ago  check_agent_health agents  [OK] $0.0 | |
|  | 2m ago  get_mcp_status     agents  [OK] $0.0 | |
|  +---------------------------------------------+ |
|  Last updated: 3s ago                             |
+---------------------------------------------------+
```

---

## 5. Cross-Interface Handoff Screens

These screens participate in workflows that begin on MCP and complete on the Dashboard (or vice versa). Each screen shows WHERE the workflow came from, the current state, and what happens NEXT.

### 5.1 Approval Queue -- Cross-Interface Handoff (Journey 1)

**Scenario:** Priya triggers a pipeline via MCP (`trigger_pipeline`, I-001). The pipeline reaches an approval gate. Anika sees the pending approval on the Dashboard and approves.

**What S-041 (Approval Detail Panel) shows for cross-interface context:**

| Element | Source | Display |
|---------|--------|---------|
| Origin interface | `ApprovalRequest.context.triggered_via` | Icon + text: "Triggered via MCP by Priya" |
| MCP tool used | `ApprovalRequest.context.trigger_tool` | Monospace: `trigger_pipeline` |
| Pipeline trigger time | `PipelineRun.started_at` | "Started 18m ago" |
| Steps before gate | `PipelineRun.current_step` | "5 of 14 steps completed before this gate" |
| Cost at gate | `PipelineRun.cost_usd` | "$11.80 spent so far" |
| Previous approvals | `ApprovalRequest.context.previous_gates` | List of prior gate decisions with timestamps |
| What happens after approval | Static text based on pipeline config | "Pipeline will resume at step 7 (MCP-TOOL-SPEC). Priya will see status change via MCP `get_pipeline_status`." |

**Cross-interface indicator:** A banner at the top of the approval detail panel:

```
+-- Cross-Interface Context -----------------------------------------+
| [MCP icon] This pipeline was triggered via MCP by Priya (10:30).   |
| After your decision, Priya will see the update via MCP status call.|
+--------------------------------------------------------------------+
```

### 5.2 Pipeline Monitor -- Cross-Interface Handoff (Journey 1 continued)

**Scenario:** David watches a pipeline on the Dashboard that Marcus triggered via MCP.

**What S-022 (Pipeline Run Detail) shows for cross-interface context:**

| Element | Source | Display |
|---------|--------|---------|
| Triggered by | `PipelineRun.triggered_by` | "Marcus Chen" with MCP icon |
| Trigger interface | Derived from audit trail | "via MCP `trigger_pipeline`" |
| MCP monitoring link | -- | "View MCP call history for this run" links to S-007 filtered by `run_id` |

**Cross-interface indicator on Pipeline Runs Table (S-021):**

| `triggered_by` value | Display |
|----------------------|---------|
| Contains "MCP" context | MCP icon next to persona name |
| Contains "Dashboard" context | Dashboard icon next to persona name |
| Contains "REST" context | API icon next to persona name |

### 5.3 Cost Alert Investigation -- Cross-Interface Handoff (Journey 2)

**Scenario:** System detects a cost anomaly. David investigates on the Dashboard. Priya takes corrective action via MCP.

**What S-012 (Anomaly Alerts) shows for cross-interface handoff:**

| Element | Source | Display |
|---------|--------|---------|
| Anomaly entity | `CostAnomaly.entity_name` | Agent or project name |
| Root cause hint | `CostAnomaly.entity_type` + related audit events | "Agent invoked 47 times today (avg: 12). Check via MCP: `get_agent agent_id={entity_id}`" |
| Escalation action | -- | "Escalate to Platform Engineer" button opens pre-formatted Slack message |
| MCP diagnostic commands | Static, contextual | Suggested MCP commands: `check_agent_health`, `get_agent`, `set_budget_threshold` |

**Cross-interface helper panel (shown when anomaly is expanded):**

```
+-- Investigate This Anomaly ----------------------------------------+
| Dashboard actions:                                                  |
|   [View cost breakdown] [Check fleet health] [View audit trail]     |
|                                                                     |
| MCP commands for platform engineers:                                |
|   check_agent_health agent_id="agent-api-gen"                       |
|   get_agent agent_id="agent-api-gen"                                |
|   set_budget_threshold entity_id="agent-api-gen" budget_usd=100     |
|                                                                     |
| [Copy MCP commands]  [Escalate to Priya via Slack]                  |
+---------------------------------------------------------------------+
```

### 5.4 Canary Deployment Monitoring -- Cross-Interface Handoff (Journey 3)

**Scenario:** Priya sets canary traffic via MCP. Jason monitors canary health on the Dashboard.

**What S-003 (Agent Detail Panel) shows for canary cross-interface context:**

| Element | Source | Display |
|---------|--------|---------|
| Canary initiated by | Audit trail for I-026 event | "Canary started by Priya via MCP (2h ago)" |
| Traffic split | `AgentDetail.canary_traffic_pct` | "10% canary / 90% active" with visual split bar |
| Canary version | `AgentDetail.canary_version` | Version number with comparison to `active_version` |
| Health comparison | `AgentDetail.health` vs canary health | Side-by-side health metrics for active vs canary |
| Promote action | I-024 | "Promote canary to active" button (requires confirmation) |
| MCP promotion command | Static | "Or promote via MCP: `promote_agent_version agent_id={agent_id}`" |

### 5.5 Compliance Audit -- Cross-Interface Handoff (Journey 4)

**Scenario:** Fatima audits agent behavior on the Dashboard. She cross-references MCP call history.

**What S-030 (Audit Event Table) shows for cross-interface context:**

| Element | Source | Display |
|---------|--------|---------|
| Source interface | Derived from `AuditEvent.action` prefix + `source_ip` | Column showing "MCP", "Dashboard", "REST", or "System" |
| MCP call correlation | `AuditEvent.details.mcp_call_id` if present | Link to MCP call detail in S-007 |
| User identity | `AuditEvent.user_id` | Persona name with interface icon |

**Audit export (S-032) includes cross-interface metadata:**
- Reports include a "Cross-Interface Activity" section
- Shows which actions originated from MCP vs Dashboard vs REST
- Fatima can filter exports to MCP-only activity for AI governance review

---

## 6. Component Library

All reusable Streamlit components for the dashboard. Each component is implemented as a Python function returning Streamlit elements.

### 6.1 StatusBadge

**Purpose:** Display health/status state with color, shape, and text.

```python
def status_badge(status: str, size: str = "medium") -> None:
    """
    Renders a colored badge with icon and text.

    Args:
        status: One of "healthy", "degraded", "offline", "canary",
                "active", "pending", "running", "paused", "completed",
                "failed", "cancelled", "approved", "rejected", "expired",
                "info", "warning", "error", "critical",
                "low", "medium", "high"
        size: "small" (inline), "medium" (standard), "large" (hero)
    """
```

| Status | Color | Shape | Text |
|--------|-------|-------|------|
| healthy / active / completed / approved | Green (#22C55E) | Circle | "Healthy" / "Active" / etc. |
| degraded / paused / canary / pending | Amber (#F59E0B) | Triangle / Diamond | "Degraded" / "Paused" / etc. |
| offline / failed / rejected / error / critical | Red (#EF4444) | Circle / X | "Offline" / "Failed" / etc. |
| cancelled / expired / info | Gray (#6B7280) | Circle / Dash | "Cancelled" / "Expired" / etc. |

**Accessibility:** Always renders both icon/shape AND text. Color alone never conveys meaning. Includes `aria-label` with full status description.

### 6.2 CostGauge

**Purpose:** Display budget utilization as a visual gauge.

```python
def cost_gauge(
    spent_usd: float,
    budget_usd: float,
    utilization_pct: float,
    alert_threshold_pct: float,
    label: str,
    at_risk: bool = False
) -> None:
    """
    Renders a semicircular gauge showing budget utilization.

    Color thresholds:
        0-60%:   Green (#22C55E)
        61-80%:  Amber (#F59E0B)
        81-100%: Red (#EF4444)
        >100%:   Red with pulse animation

    Shows: percentage, spent amount, budget total, alert threshold marker.
    """
```

**Accessibility:** `aria-label="{label} budget: {utilization_pct}% utilized, ${spent_usd} of ${budget_usd} spent"`. Text values always visible alongside gauge visual.

### 6.3 DataTable

**Purpose:** Sortable, filterable, paginated data table.

```python
def data_table(
    data: list[dict],
    columns: list[ColumnConfig],
    page_size: int = 20,
    sortable: bool = True,
    filterable: bool = True,
    on_row_click: callable = None,
    empty_message: str = "No data available",
    loading: bool = False
) -> dict | None:
    """
    Renders a data table with sort, filter, and pagination.

    ColumnConfig:
        name: str           - field name from data dict
        label: str          - display header
        sortable: bool      - allow sorting on this column
        width: str          - CSS width (e.g., "120px", "20%")
        render: callable    - custom renderer (e.g., status_badge)
        aria_label: str     - template for row cell aria-label

    Returns: selected row dict if on_row_click is set, else None.
    """
```

**Accessibility:** Standard `<table>` semantics. Sort headers use `aria-sort`. Row count announced via `aria-live="polite"`.

### 6.4 DetailPanel

**Purpose:** Slide-out panel for drill-down views.

```python
def detail_panel(
    title: str,
    content: callable,
    width: str = "400px",
    on_close: callable = None
) -> None:
    """
    Renders a slide-out panel from the right side of the page.

    Features:
        - Slide-in animation (200ms)
        - Close via X button, Escape key, or click outside
        - Focus trapped within panel when open
        - Returns focus to trigger element on close
    """
```

**Accessibility:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` points to title. Focus trap implemented with JavaScript injection.

### 6.5 TimelineBar

**Purpose:** Display pipeline step progress.

```python
def timeline_bar(
    current_step: int,
    total_steps: int,
    step_statuses: list[dict],  # [{step_number, step_name, status}]
    on_step_click: callable = None
) -> int | None:
    """
    Renders a horizontal timeline showing pipeline progress.

    Step statuses:
        completed:  Green segment with checkmark
        running:    Blue segment with spinner
        failed:     Red segment with X
        pending:    Gray segment with circle
        paused:     Amber segment with pause icon

    Returns: clicked step number if on_step_click is set.
    """
```

**Accessibility:** `role="progressbar"` with `aria-valuemin="0"`, `aria-valuemax="{total_steps}"`, `aria-valuenow="{current_step}"`. Each step has `aria-label="Step {n}: {name} - {status}"`. Clickable steps are focusable.

### 6.6 ConfirmationDialog

**Purpose:** Modal dialog for destructive or significant actions.

```python
def confirmation_dialog(
    title: str,
    message: str,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    danger: bool = False,
    requires_comment: bool = False,
    comment_min_length: int = 0
) -> dict | None:
    """
    Renders a modal confirmation dialog.

    Args:
        danger: If True, confirm button is red
        requires_comment: If True, shows textarea that must be filled
        comment_min_length: Minimum characters for comment

    Returns: {"confirmed": True, "comment": "..."} or None if cancelled.
    """
```

**Accessibility:** `role="alertdialog"`, `aria-modal="true"`, `aria-describedby` points to message. Focus moves to dialog on open. Escape cancels. Focus returns to trigger on close.

### 6.7 MetricCard

**Purpose:** Display a single key metric with optional trend indicator.

```python
def metric_card(
    label: str,
    value: str | int | float,
    trend_pct: float = None,
    trend_direction: str = None,  # "up" | "down" | None
    color: str = "default",       # "default" | "success" | "warning" | "danger"
    clickable: bool = False,
    on_click: callable = None,
    icon: str = None
) -> None:
    """
    Renders a card showing a single metric value.

    Trend arrow:
        Up + positive context (e.g., healthy agents): Green arrow up
        Up + negative context (e.g., cost): Red arrow up
        Down + positive context: Red arrow down
        Down + negative context: Green arrow down

    Size: 160px wide x 100px tall.
    """
```

**Accessibility:** `aria-label="{label}: {value}"`. If trend present: `aria-label="{label}: {value}, {trend_direction} {trend_pct}%"`. If clickable: `role="button"`, `tabindex="0"`.

### 6.8 MarkdownRenderer

**Purpose:** Render markdown content for document preview.

```python
def markdown_renderer(
    content: str,
    max_height: str = "600px",
    show_copy_button: bool = True,
    show_fullscreen_button: bool = True
) -> None:
    """
    Renders markdown content in a scrollable, styled container.

    Features:
        - Syntax highlighting for code blocks
        - Table rendering
        - Heading anchors for navigation
        - Copy raw markdown button
        - Open in full-screen button
    """
```

### 6.9 LoadingSkeleton

**Purpose:** Placeholder content shown during data loading.

```python
def loading_skeleton(
    variant: str,  # "metric_card" | "table_row" | "chart" | "panel" | "feed_item"
    count: int = 1
) -> None:
    """
    Renders animated skeleton placeholders matching the target component's layout.
    Uses pulsing gray rectangles matching the dimensions of the real component.
    """
```

### 6.10 StaleDataIndicator

**Purpose:** Show when displayed data may be outdated.

```python
def stale_data_indicator(
    last_updated_at: str,  # ISO 8601
    threshold_seconds: int = 60,
    on_refresh: callable = None
) -> None:
    """
    Shows "Last updated: Xs ago" with visual warning when data exceeds threshold.

    States:
        Fresh (< threshold): Green text "Updated Xs ago"
        Stale (>= threshold): Amber text "Data may be stale (Xs ago)" + refresh button
        Error (no update): Red text "Unable to refresh" + manual refresh button
    """
```

---

## 7. Responsive Behavior

Streamlit is primarily a desktop framework. The dashboard targets desktop viewports (1280px+) as the primary experience. Tablet and mobile are graceful degradation targets, not primary design targets.

### 7.1 Viewport Breakpoints

| Breakpoint | Width | Target | Behavior |
|------------|-------|--------|----------|
| Desktop (large) | >= 1440px | Primary | Full layout: side-by-side panels, all columns visible |
| Desktop (standard) | 1280-1439px | Primary | Slightly condensed: smaller margins, abbreviate some labels |
| Tablet | 768-1279px | Secondary | Single-column layout: detail panels stack below, tables scroll horizontally |
| Mobile | < 768px | Tertiary | Simplified view: MetricCards stack vertically, tables show critical columns only |

### 7.2 Page-Specific Responsive Rules

#### Fleet Health (`/fleet-health`)

| Viewport | Agent Grid | MCP Panel | Detail Panel |
|----------|-----------|-----------|--------------|
| >= 1440px | 6-column grid + MCP panel side-by-side | Right sidebar (320px) | Slide-out overlay |
| 1280-1439px | 5-column grid + MCP panel side-by-side | Right sidebar (280px) | Slide-out overlay |
| 768-1279px | 3-column grid, MCP panel below grid | Full-width below grid | Full-width below grid |
| < 768px | 2-column grid, MCP panel below | Full-width, collapsed by default | Full-width overlay |

#### Cost Monitor (`/cost-monitor`)

| Viewport | Charts + Anomalies | Budget Gauges |
|----------|-------------------|---------------|
| >= 1440px | Charts (70%) + Anomalies (30%) side-by-side | 3-4 gauges in a row |
| 1280-1439px | Charts (65%) + Anomalies (35%) side-by-side | 3 gauges in a row |
| 768-1279px | Charts full-width, Anomalies below | 2 gauges per row |
| < 768px | Charts full-width (simplified), Anomalies below | 1 gauge per row |

#### Pipeline Runs (`/pipeline-runs`)

| Viewport | Trigger Form | Runs Table | Detail Panel |
|----------|-------------|-----------|--------------|
| >= 1280px | Collapsible top section | Full-width table, all columns | Slide-out overlay (500px) |
| 768-1279px | Collapsible top section | Table with horizontal scroll | Full-width below table |
| < 768px | Full-width form | Card layout (one card per run) | Full-screen overlay |

#### Audit Log (`/audit-log`)

| Viewport | Summary Cards | Event Table | Export |
|----------|--------------|------------|--------|
| >= 1280px | 6 cards in a row | Full table, all columns | Inline at bottom |
| 768-1279px | 3 cards per row (2 rows) | Table with horizontal scroll | Inline at bottom |
| < 768px | 2 cards per row (3 rows) | Card layout per event | Fixed bottom button |

#### Approval Queue (`/approval-queue`)

| Viewport | Queue Table | Detail Panel |
|----------|-----------|--------------|
| >= 1280px | Table (60%) + Detail panel (40%) side-by-side | Persistent right panel |
| 768-1279px | Full-width table | Full-width below, expanded on click |
| < 768px | Card layout per approval | Full-screen overlay |

### 7.3 Streamlit-Specific Implementation Notes

- Use `st.columns()` with dynamic ratios based on viewport detection via JavaScript injection
- Use `st.expander()` for collapsible sections on smaller viewports
- Inject CSS media queries via `st.markdown(unsafe_allow_html=True)` for fine-grained responsive control
- Tables on mobile switch to card layout using CSS `display: block` on table cells
- Chart sizes adapt via Plotly's `responsive=True` configuration

---

## 8. Real-Time Update Registry

Every dynamic element in the dashboard has a defined update strategy, polling interval, latency SLA, and fallback behavior.

### 8.1 Update Strategy Definitions

| Strategy | Description | Implementation |
|----------|-------------|----------------|
| **Polling** | Periodic HTTP GET requests at fixed interval | `st.experimental_rerun` with timer in `st.session_state` |
| **Manual** | User-initiated refresh via button click | Refresh button calls API and updates state |
| **Event** | Update triggered by user action (approve, trigger) | Action handler refreshes affected components |

### 8.2 Real-Time Update Table

| Screen ID | Element | Strategy | Endpoint | Interval | Latency SLA | Fallback | Notes |
|-----------|---------|----------|----------|----------|-------------|----------|-------|
| S-001 | Fleet health MetricCards | Polling | `GET /api/v1/fleet/health` | 30s | < 1s (Q-006) | Show stale indicator + last cached values | Lightweight aggregation endpoint |
| S-002 | Agent grid status badges | Polling | `GET /api/v1/agents` | 30s | < 2s (Q-005) | Show stale indicator; preserve last grid | Returns AgentSummary[] (lightweight) |
| S-003 | Agent detail panel | Event | `GET /api/v1/agents/{id}` | On open + on action | < 2s | Show stale indicator in panel | Fetches on panel open; refreshes after promote/rollback |
| S-004 | Health badges | Polling | Embedded in S-002 response | 30s | < 2s | Badge shows "unknown" state | Health data included in AgentSummary |
| S-005 | Version management state | Event | `GET /api/v1/agents/{id}` | After promote/rollback/canary action | < 2s | Retry button; show last known version | Refreshes S-003 detail panel after action |
| S-006 | Maturity badges | Polling | Embedded in S-002 response | 30s | < 2s | Show current level without eligibility | Maturity changes are infrequent |
| S-007 | MCP server health | Polling | `GET /api/v1/mcp/status` | 15s | < 1s | Show last known status + stale time | Critical for operator visibility |
| S-007 | MCP call feed | Polling | `GET /api/v1/audit/mcp-calls?limit=20` | 5s | < 1s | Show last-updated timestamp; freeze feed | Aggressive polling for live feel |
| S-007 | Connected clients | Polling | Derived from MCP status + call feed | 15s | < 1s | Show "unknown" count | Computed client-side from recent callers |
| S-010 | Cost charts | Manual | `GET /api/v1/costs/report` | On period change or manual refresh | < 2s | Show cached chart + stale indicator | Cost data is not real-time critical |
| S-011 | Budget gauges | Polling | `GET /api/v1/costs/budget` | 60s | < 2s | Show last known gauge + stale indicator | Budget changes slowly |
| S-012 | Anomaly alerts | Polling | `GET /api/v1/costs/anomalies` | 30s | < 2s | Show last known anomalies | New anomalies need timely surfacing |
| S-013 | Budget settings | Event | `PUT /api/v1/costs/thresholds` | After save action | < 2s | Retry on failure; revert form | User-initiated only |
| S-020 | Pipeline trigger form | Event | `POST /api/v1/pipelines/trigger` | On trigger action | < 2s | Show error; preserve form input | One-time action |
| S-021 | Pipeline runs table | Polling | `GET /api/v1/pipelines` | 15s | < 2s | Show stale indicator; preserve table | Active pipelines need timely status |
| S-022 | Pipeline run detail | Polling | `GET /api/v1/pipelines/{id}` | 10s (running), 30s (other) | < 2s | Show last known state + stale time | Aggressive polling for running pipelines |
| S-023 | Document viewer | Event | `GET /api/v1/pipelines/{id}/documents` | On open + after step completion | < 2s | Show last known doc list | Documents only change on step completion |
| S-024 | Pipeline action buttons | Event | POST endpoints | After action | < 2s | Retry on failure | State changes trigger S-022 refresh |
| S-030 | Audit event table | Manual | `GET /api/v1/audit/events` | On filter change or manual refresh | < 2s | Show cached results + stale indicator | Audit data is archival; real-time not required |
| S-031 | Audit summary cards | Manual | `GET /api/v1/audit/summary` | On period change or manual refresh | < 2s | Show cached summary | Summary computation may be slow for large ranges |
| S-032 | Audit export | Event | `POST /api/v1/audit/export` | On export action | < 15s (report gen) | Retry on failure; show progress bar | Export is a long-running operation |
| S-040 | Approval queue table | Polling | `GET /api/v1/approvals/pending` | 15s | < 2s | Show stale indicator; preserve table | Time-sensitive: approvals have expiry |
| S-041 | Approval detail panel | Event | Loaded from S-040 data + `GET /api/v1/pipelines/{id}/documents` | On open | < 2s | Show stale indicator in panel | Fetches document preview on demand |
| S-041 | Approve/Reject actions | Event | `POST /api/v1/approvals/{id}/approve` or `/reject` | On action | < 2s | Retry on failure; show error | Action triggers S-040 table refresh |
| S-042 | Approval history | Manual | `GET /api/v1/approvals?status=approved,rejected,expired` | On tab switch or manual refresh | < 2s | Show cached history | Historical data; no real-time need |

### 8.3 Polling Optimization Rules

1. **Adaptive polling:** When a page is in the background (browser tab not visible), reduce all polling intervals to 120s to minimize server load.
2. **Exponential backoff on error:** If a polling request fails, double the interval (up to 120s max). Reset to normal interval on success.
3. **Deduplication:** If the response payload is identical to the previous response (compared by hash), skip UI re-render.
4. **Request coalescing:** Fleet Health page batches S-001 + S-002 into a single API call cycle (30s) rather than making separate requests.
5. **Conditional requests:** Use `If-Modified-Since` or `ETag` headers where supported to reduce payload size for unchanged data.

### 8.4 Stale Data Visualization Rules

| Staleness Duration | Visual Indicator | Behavior |
|-------------------|-----------------|----------|
| 0 - 30s | Green "Updated Xs ago" text | Normal operation |
| 31 - 60s | Amber "Updated Xs ago" text | Informational warning |
| 61 - 120s | Amber banner "Data may be stale" + manual refresh button | User attention needed |
| > 120s | Red banner "Data is stale (Xm ago). Attempting to reconnect..." | Auto-retry with backoff |
| API confirmed down | Red banner "Service unavailable. Showing cached data from {timestamp}." | Cached data preserved; manual retry available |

---

## Appendix A: Data Shape Quick Reference

All data shapes are defined in INTERACTION-MAP (Doc 6), Section 2. This appendix provides a quick lookup for dashboard implementers.

| Data Shape | Key Fields Used in Dashboard | Primary Screens |
|-----------|------------------------------|-----------------|
| `FleetHealth` | `healthy_agents`, `total_agents`, `circuit_breakers_open`, `avg_response_ms`, `fleet_cost_today_usd`, `active_pipelines`, `pending_approvals`, `last_updated_at` | S-001 |
| `AgentSummary` | `agent_id`, `name`, `phase`, `archetype`, `status`, `active_version`, `cost_today_usd`, `last_invocation_at`, `invocation_count_today` | S-002 |
| `AgentDetail` | All `AgentSummary` fields + `manifest`, `prompt_preview`, `maturity`, `canary_version`, `canary_traffic_pct`, `health`, `model`, `max_tokens`, `temperature`, `tools` | S-003 |
| `AgentHealth` | `healthy`, `last_check_at`, `response_time_ms`, `error_message`, `consecutive_failures`, `circuit_breaker_open` | S-004 |
| `AgentVersion` | `active_version`, `canary_version`, `canary_traffic_pct`, `previous_version`, `promoted_at`, `rolled_back_at` | S-005 |
| `AgentMaturity` | `current_level`, `override_rate`, `confidence_avg`, `consecutive_days`, `next_level`, `promotion_eligible`, `promotion_criteria` | S-006 |
| `McpServerStatus` | `server_name`, `healthy`, `uptime_seconds`, `tool_count`, `active_connections`, `requests_per_minute`, `error_rate_pct`, `version`, `last_restart_at` | S-007 |
| `McpCallEvent` | `timestamp`, `tool_name`, `server_name`, `caller`, `project_id`, `duration_ms`, `status`, `error_message`, `cost_usd` | S-007 |
| `CostReport` | `scope`, `total_usd`, `breakdown[]`, `trend_pct`, `generated_at` | S-010 |
| `BudgetStatus` | `scope`, `entity_id`, `budget_usd`, `spent_usd`, `remaining_usd`, `utilization_pct`, `at_risk`, `alert_threshold_pct`, `projected_overrun_date` | S-011, S-013 |
| `CostAnomaly` | `anomaly_id`, `entity_name`, `entity_type`, `expected_usd`, `actual_usd`, `deviation_pct`, `severity`, `detected_at`, `acknowledged`, `acknowledged_by` | S-012 |
| `PipelineRun` | `run_id`, `project_id`, `pipeline_name`, `status`, `current_step`, `total_steps`, `current_step_name`, `started_at`, `completed_at`, `cost_usd`, `triggered_by`, `error_message`, `checkpoint_step` | S-021, S-022 |
| `PipelineDocument` | `document_id`, `run_id`, `doc_number`, `doc_name`, `doc_type`, `content`, `generated_at`, `quality_score`, `token_count`, `agent_id` | S-023 |
| `ValidationResult` | `valid`, `errors[]`, `warnings[]`, `project_id` | S-020 |
| `AuditEvent` | `event_id`, `timestamp`, `agent_id`, `session_id`, `project_id`, `action`, `severity`, `details`, `cost_usd`, `tokens_in`, `tokens_out`, `duration_ms`, `pii_detected`, `source_ip`, `user_id` | S-030 |
| `AuditSummary` | `period`, `total_events`, `by_severity`, `by_agent`, `by_project`, `by_action`, `total_cost_usd`, `pii_detections` | S-031 |
| `AuditReport` | `report_id`, `format`, `period`, `filters_applied`, `generated_at`, `download_url`, `size_bytes`, `record_count` | S-032 |
| `ApprovalRequest` | `approval_id`, `session_id`, `run_id`, `pipeline_name`, `step_number`, `step_name`, `summary`, `risk_level`, `status`, `requested_at`, `expires_at`, `decided_at`, `decision_by`, `decision_comment`, `context` | S-040, S-041, S-042 |
| `ApprovalResult` | `approval_id`, `status`, `decided_at`, `decision_by`, `decision_comment`, `pipeline_resumed` | S-041 |

---

## Appendix B: Persona-Screen Coverage Matrix

| Screen | Anika (Eng Lead) | David (DevOps) | Fatima (Compliance) | Jason (Tech Lead) |
|--------|:-:|:-:|:-:|:-:|
| S-001 Fleet Health Overview | | PRIMARY | | PRIMARY |
| S-002 Agent Grid | | PRIMARY | | PRIMARY |
| S-003 Agent Detail Panel | | PRIMARY | | PRIMARY |
| S-004 Health Badges | | PRIMARY | | SECONDARY |
| S-005 Version Management | | PRIMARY | | PRIMARY |
| S-006 Maturity Badges | SECONDARY | | | PRIMARY |
| S-007 MCP Monitoring Panel | | PRIMARY | | PRIMARY |
| S-010 Cost Charts | | PRIMARY | PRIMARY | |
| S-011 Budget Gauges | | PRIMARY | PRIMARY | |
| S-012 Anomaly Alerts | | PRIMARY | SECONDARY | |
| S-013 Budget Settings | | PRIMARY | | |
| S-020 Pipeline Trigger Form | PRIMARY | | | SECONDARY |
| S-021 Pipeline Runs Table | PRIMARY | SECONDARY | | SECONDARY |
| S-022 Pipeline Run Detail | PRIMARY | SECONDARY | | SECONDARY |
| S-023 Document Viewer | PRIMARY | | | SECONDARY |
| S-024 Pipeline Actions | PRIMARY | | | SECONDARY |
| S-030 Audit Event Table | | | PRIMARY | |
| S-031 Audit Summary Cards | | | PRIMARY | |
| S-032 Audit Export Button | | | PRIMARY | |
| S-040 Approval Queue Table | PRIMARY | | | SECONDARY |
| S-041 Approval Detail Panel | PRIMARY | | | |
| S-042 Approval History Tab | SECONDARY | | PRIMARY | |

---

## Appendix C: Interaction ID to Screen ID Traceability

| Interaction ID | Interaction Name | Screen ID(s) |
|---------------|-----------------|--------------|
| I-001 | Trigger pipeline | S-020 |
| I-002 | Get pipeline status | S-022 |
| I-003 | List pipeline runs | S-021 |
| I-004 | Resume pipeline | S-024 |
| I-005 | Cancel pipeline | S-024 |
| I-006 | Get pipeline documents | S-023 |
| I-007 | Retry pipeline step | S-024 |
| I-008 | Get pipeline config | S-020 (pipeline selector) |
| I-009 | Validate project input | S-020 (validate button) |
| I-020 | List agents | S-002 |
| I-021 | Get agent detail | S-003 |
| I-023 | Check agent health | S-004 |
| I-024 | Promote agent version | S-005 |
| I-025 | Rollback agent version | S-005 |
| I-026 | Set canary traffic | S-005 |
| I-027 | Get agent maturity | S-006 |
| I-040 | Get cost report | S-010 |
| I-041 | Check budget | S-011 |
| I-042 | Query audit events | S-030 |
| I-043 | Get audit summary | S-031 |
| I-044 | Export audit report | S-032 |
| I-045 | List pending approvals | S-040, S-041, S-042 |
| I-046 | Approve gate | S-041 |
| I-047 | Reject gate | S-041 |
| I-048 | Get cost anomalies | S-012 |
| I-049 | Set budget threshold | S-013 |
| I-080 | Get fleet health | S-001 |
| I-081 | Get MCP server status | S-007 |
| I-082 | List recent MCP calls | S-007 |

**Coverage:** 29 of 34 interactions have Dashboard screens. The 5 interactions without Dashboard coverage (I-022, I-060-I-063) are justified in the INTERACTION-MAP Parity Matrix as developer/MCP-only workflows.

---

*End of DESIGN-SPEC (Doc 8 of 14)*
