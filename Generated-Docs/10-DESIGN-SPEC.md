# 10 - DESIGN SPEC

> Agentic SDLC Platform -- Streamlit Dashboard Design Specification
>
> Version: 1.0.0 | Last Updated: 2026-03-23

| Field          | Value                                                                 |
|----------------|-----------------------------------------------------------------------|
| Document       | DESIGN-SPEC-001                                                       |
| Title          | Agentic SDLC Platform -- Streamlit Dashboard UI Design Specification  |
| Version        | 1.0.0                                                                 |
| Date           | 2026-03-23                                                            |
| Status         | Draft                                                                 |
| Owner          | Priya Mehta (Platform Engineer)                                       |
| Reviewers      | David Chen (Delivery Lead), Sarah Kim (Engineering Lead), Marcus Johnson (DevOps), Lisa Patel (Compliance) |
| Tech Stack     | Streamlit 1.x, Python 3.12, Plotly, `streamlit-autorefresh`          |
| Entry Point    | `dashboard/app.py`                                                    |
| Page Directory | `dashboard/pages/`                                                    |
| API Base URL   | `http://localhost:8080/api/v1/` (dev) / `https://api.agentic-sdlc.io/api/v1/` (prod) |

---

## Table of Contents

1. [Design System](#1-design-system)
2. [Navigation](#2-navigation)
3. [Screen Specifications](#3-screen-specifications)
   - 3.1 [SCR-01: Fleet Health](#31-scr-01-fleet-health)
   - 3.2 [SCR-02: Cost Monitor](#32-scr-02-cost-monitor)
   - 3.3 [SCR-03: Pipeline Runs](#33-scr-03-pipeline-runs)
   - 3.4 [SCR-04: Audit Log](#34-scr-04-audit-log)
   - 3.5 [SCR-05: Approval Queue](#35-scr-05-approval-queue)
4. [Component States](#4-component-states)
5. [Keyboard Navigation](#5-keyboard-navigation)
6. [Accessibility](#6-accessibility)
7. [Cross-Cutting Concerns](#7-cross-cutting-concerns)

---

## 1. Design System

### 1.1 Theme Configuration

The dashboard uses Streamlit's built-in dark theme as the default. The theme is configured in `.streamlit/config.toml`:

```toml
[theme]
base = "dark"
primaryColor = "#6C63FF"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1A1D24"
textColor = "#FAFAFA"
font = "sans serif"
```

### 1.2 Brand Colors

| Token                  | Hex       | Usage                                          |
|------------------------|-----------|-------------------------------------------------|
| `--brand-primary`      | `#6C63FF` | Primary action buttons, active sidebar links, chart accent |
| `--brand-primary-hover`| `#5A52E0` | Primary button hover state                      |
| `--brand-secondary`    | `#00D4AA` | Secondary indicators, success accent             |
| `--bg-page`            | `#0E1117` | Page background (Streamlit default dark)         |
| `--bg-card`            | `#1A1D24` | Card/container background                        |
| `--bg-card-hover`      | `#22262E` | Card hover state                                 |
| `--bg-input`           | `#262B33` | Input field backgrounds                          |
| `--text-primary`       | `#FAFAFA` | Primary body text                                |
| `--text-secondary`     | `#8B949E` | Secondary/muted text, labels                     |
| `--text-tertiary`      | `#6E7681` | Placeholder text, disabled states                |
| `--border-default`     | `#30363D` | Card borders, dividers                           |
| `--border-focus`       | `#6C63FF` | Focus ring on interactive elements               |

### 1.3 Status Colors

All status colors are chosen to meet WCAG 2.1 AA contrast requirements (>= 4.5:1) against the dark background (`#0E1117`).

| Status       | Hex       | Background Tint | Usage                                      | Contrast Ratio vs `#0E1117` |
|--------------|-----------|-----------------|--------------------------------------------|-----------------------------|
| Healthy / Success | `#3FB950` | `#1B3626`  | Agent active, step completed, approval approved | 5.8:1                    |
| Warning / Degraded| `#D29922` | `#3B2E10`  | Agent degraded, budget at 80%, slow response    | 5.2:1                    |
| Error / Failed    | `#F85149` | `#3D1517`  | Agent circuit open, step failed, rejection      | 5.4:1                    |
| Unknown / Neutral | `#8B949E` | `#1F2328`  | Agent unknown, no data, pending                 | 4.6:1                    |
| Info / Active     | `#58A6FF` | `#172238`  | Running step pulse, info badge, active filter   | 5.1:1                    |

### 1.4 Typography

Streamlit renders all text using the system sans-serif font stack. The dashboard applies consistent sizing via Streamlit's native heading and text elements.

| Element           | Streamlit API             | Effective Size | Weight  |
|-------------------|---------------------------|----------------|---------|
| Page Title        | `st.title()`              | 2.0rem (32px)  | 700     |
| Section Header    | `st.header()`             | 1.5rem (24px)  | 700     |
| Subsection Header | `st.subheader()`          | 1.25rem (20px) | 600     |
| Body Text         | `st.write()` / `st.text()`| 1.0rem (16px)  | 400     |
| Caption / Label   | `st.caption()`            | 0.875rem (14px)| 400     |
| Metric Value      | `st.metric()` value       | 2.25rem (36px) | 700     |
| Metric Delta      | `st.metric()` delta       | 0.875rem (14px)| 600     |
| Table Cell        | `st.dataframe()`          | 0.875rem (14px)| 400     |
| Code / Monospace  | `st.code()`               | 0.875rem (14px)| 400     |

### 1.5 Chart Library

All charts use **Plotly** via `st.plotly_chart(fig, use_container_width=True)`. Plotly is chosen for interactivity (hover tooltips, zoom, pan) and accessibility (ARIA labels on SVG elements).

**Chart theme defaults:**

```python
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#1A1D24",
    font=dict(family="sans-serif", size=14, color="#FAFAFA"),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    hoverlabel=dict(bgcolor="#262B33", font_size=13, font_color="#FAFAFA"),
)
```

**Chart color sequence:** `["#6C63FF", "#00D4AA", "#58A6FF", "#D29922", "#F85149", "#A371F7", "#F778BA"]`

### 1.6 Spacing and Layout

| Token        | Value | Usage                                       |
|--------------|-------|---------------------------------------------|
| `space-xs`   | 4px   | Inline element gaps                         |
| `space-sm`   | 8px   | Tight padding within cards                  |
| `space-md`   | 16px  | Standard padding, column gaps               |
| `space-lg`   | 24px  | Section margins                             |
| `space-xl`   | 32px  | Page-level top/bottom padding               |

All pages use `st.set_page_config(layout="wide")` to maximize the horizontal viewport.

### 1.7 Responsive Behavior

Streamlit handles responsive reflow automatically. The following conventions apply:

- **Desktop (>= 1200px):** Stat cards in 4-column rows (`st.columns(4)`), tables full-width, charts full-width.
- **Tablet (768-1199px):** Stat cards in 2-column rows (`st.columns(2)`), tables horizontally scrollable, charts full-width.
- **Mobile (< 768px):** Stat cards stacked vertically, sidebar collapses to hamburger menu, tables horizontally scrollable.

All column layouts use Streamlit's `st.columns()` with explicit ratios to avoid uneven distribution.

---

## 2. Navigation

### 2.1 Sidebar Structure

The sidebar is rendered in `dashboard/app.py` and persists across all pages via Streamlit's multipage architecture.

```
+-------------------------------+
|  [Logo]  Agentic SDLC         |
|  Platform Dashboard            |
+-------------------------------+
|                                |
|  > Fleet Health         [icon] |   <-- default landing
|  > Cost Monitor         [icon] |
|  > Pipeline Runs        [icon] |
|  > Audit Log            [icon] |
|  > Approval Queue       [icon] |
|                                |
+-------------------------------+
|  [Divider]                     |
|                                |
|  User: priya@acme.com         |
|  Role: Platform Engineer       |
|  [Logout]                      |
|                                |
+-------------------------------+
|  Auto-refresh: [ON/OFF]       |
|  Last refreshed: 14:30:05 UTC  |
+-------------------------------+
```

### 2.2 Sidebar Elements

| Element              | Streamlit API                          | Details                                           |
|----------------------|----------------------------------------|---------------------------------------------------|
| Logo / Title         | `st.sidebar.image()` + `st.sidebar.title()` | Platform logo (64x64 PNG), title "Agentic SDLC"  |
| Page Links           | Streamlit multipage (`pages/` directory) | Auto-generated from file names; ordered by numeric prefix |
| User Info            | `st.sidebar.markdown()`               | Displays `user.email` and `user.role` from JWT claims |
| Logout Button        | `st.sidebar.button("Logout")`         | Clears session state, redirects to login           |
| Auto-Refresh Toggle  | `st.sidebar.toggle("Auto-refresh")`   | Default ON; controls `streamlit-autorefresh` component |
| Last Refreshed       | `st.sidebar.caption()`                | Shows UTC timestamp of last data fetch             |

### 2.3 Page File Mapping

| File Name                      | Sidebar Label     | Icon   | Primary Personas    |
|--------------------------------|-------------------|--------|---------------------|
| `pages/01_fleet_health.py`     | Fleet Health      | `"grid_on"` or equivalent emoji indicator | Marcus, Priya |
| `pages/02_cost_monitor.py`     | Cost Monitor      | `"attach_money"` or `$` | Marcus, Lisa, David |
| `pages/03_pipeline_runs.py`    | Pipeline Runs     | `"play_circle"` or pipeline icon | David, Sarah |
| `pages/04_audit_log.py`        | Audit Log         | `"receipt_long"` or log icon | Lisa, Marcus  |
| `pages/05_approval_queue.py`   | Approval Queue    | `"how_to_reg"` or checkmark icon | Sarah, David |

### 2.4 Default Landing Page

When a user navigates to the dashboard root (`/`), Streamlit loads the first page alphabetically from `pages/`. The numeric prefix `01_` ensures **Fleet Health** is the default landing page.

### 2.5 Role-Based Visibility

All five pages are visible to all authenticated users. Data access is enforced at the API layer (see 09-API-CONTRACTS.md Section 3, Roles and Permissions). The sidebar displays the user's role to provide context but does not hide page links.

---

## 3. Screen Specifications

---

### 3.1 SCR-01: Fleet Health

| Field           | Value                                                         |
|-----------------|---------------------------------------------------------------|
| **ID**          | SCR-01                                                        |
| **Name**        | Fleet Health                                                  |
| **File**        | `dashboard/pages/01_fleet_health.py`                          |
| **Purpose**     | Display real-time status of all agents in the fleet, including circuit breaker states and key health metrics, so Marcus and Priya can detect and triage issues at a glance. |
| **Primary Users** | Marcus (DevOps), Priya (Platform Engineer)                  |

#### 3.1.1 Layout

```
+------------------------------------------------------------------+
|  Fleet Health                                    [Refresh] [v]    |
+------------------------------------------------------------------+
|                                                                    |
|  [Stat Card]     [Stat Card]     [Stat Card]      [Stat Card]    |
|  Total Agents    Active          Degraded          Circuit Open   |
|  12              10              1                  1              |
|  --             +2 vs yesterday  +1 vs yesterday   -0 vs yesterday|
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Filters:  [Phase v]  [Status v]  [Search agent name...]         |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Agent Grid (responsive card grid, 3-4 columns)                  |
|  +-------------------+  +-------------------+  +------------------+|
|  | Requirements      |  | Code Generator    |  | API Designer     ||
|  | Analyzer          |  | v3.1.0            |  | v1.4.2           ||
|  | v2.4.1            |  |                   |  |                  ||
|  | [green dot] Active|  | [green dot] Active|  | [red dot] Circuit||
|  |                   |  | Canary: 3.2.0-rc1 |  |   Open           ||
|  | Resp: 145ms avg   |  | (10% traffic)     |  |                  ||
|  | Success: 99.7%    |  | Resp: 210ms avg   |  | Failures: 3      ||
|  | Req/24h: 1,842    |  | Success: 98.2%    |  | Recovery: 28s    ||
|  | Sessions: 2       |  | Req/24h: 2,340    |  | Last fail: 2m ago||
|  +-------------------+  +-------------------+  +------------------+|
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Agent Detail Panel (shown when card is clicked)                  |
|  +--------------------------------------------------------------+ |
|  | Agent: Requirements Analyzer (agt_req_analyzer_01)            | |
|  | Phase: requirements | Archetype: analyst | Model: claude-opus | |
|  |                                                              | |
|  | Circuit Breaker                                              | |
|  | State: closed | Failures: 0/5 | Last Failure: never          | |
|  |                                                              | |
|  | Metrics                                                      | |
|  | Last Heartbeat: 5s ago | Uptime: 67.5 days                   | |
|  | Avg Response: 145ms | P95: 192ms | P99: 310ms                | |
|  | Success Rate: 99.7% | Errors/24h: 5 | Active Sessions: 2     | |
|  | Total Requests/24h: 1,842                                    | |
|  |                                                              | |
|  | Version                                                      | |
|  | Active: 2.4.1 | Canary: -- | Canary Traffic: 0%              | |
|  +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

#### 3.1.2 Data Elements

**Stat Cards (top row, 4 columns via `st.columns(4)`):**

| Card              | Metric Source                              | Value                 | Delta                        |
|-------------------|--------------------------------------------|-----------------------|------------------------------|
| Total Agents      | `len(data)` from `GET /api/v1/agents`      | Integer count         | vs. previous day (cached)    |
| Active            | Count where `status == "active"`           | Integer count         | vs. previous day             |
| Degraded          | Count where `status == "degraded"`         | Integer count, amber  | vs. previous day             |
| Circuit Open      | Count where `status == "circuit_open"`     | Integer count, red    | vs. previous day             |

**Agent Grid Cards (one per agent):**

Each card displays these fields from `GET /api/v1/agents`:

| Field                  | API Source                          | Display Format          |
|------------------------|-------------------------------------|-------------------------|
| Agent Name             | `data[].name`                       | Bold title text         |
| Agent ID               | `data[].id`                         | Caption below name      |
| Version                | `data[].version`                    | `v{version}`            |
| Status                 | `data[].status`                     | Colored dot + label     |
| Phase                  | `data[].phase`                      | Capitalized badge       |
| Archetype              | `data[].archetype`                  | Capitalized badge       |
| Model                  | `data[].model`                      | Truncated model name    |
| Canary Version         | `data[].canary_version`             | Shown only if non-null  |
| Canary Traffic %       | `data[].canary_traffic_pct`         | `{pct}% traffic`        |

**Agent Detail Panel (expanded on card click, data from `GET /api/v1/agents/{id}/health`):**

| Field                  | API Source                                  | Display Format          |
|------------------------|---------------------------------------------|-------------------------|
| Agent ID               | `data.agent_id`                             | Monospace text          |
| Status                 | `data.status`                               | Colored badge           |
| Circuit Breaker State  | `data.circuit_breaker.state`                | `closed` / `open` / `half-open` with color |
| CB Failure Count       | `data.circuit_breaker.failure_count`        | `{count}/{threshold}`   |
| CB Last Failure        | `data.circuit_breaker.last_failure_at`      | Relative time or "never"|
| CB Recovery Timeout    | `data.circuit_breaker.recovery_timeout_seconds` | `{n}s`             |
| Last Heartbeat         | `data.metrics.last_heartbeat`               | Relative time (e.g., "5s ago") |
| Uptime                 | `data.metrics.uptime_seconds`               | Human-readable (e.g., "67.5 days") |
| Avg Response Time      | `data.metrics.avg_response_ms`              | `{n}ms`                 |
| P95 Response Time      | `data.metrics.p95_response_ms`              | `{n}ms`                 |
| P99 Response Time      | `data.metrics.p99_response_ms`              | `{n}ms`                 |
| Success Rate           | `data.metrics.success_rate_pct`             | `{n}%` with color       |
| Total Requests (24h)   | `data.metrics.total_requests_24h`           | Comma-formatted integer |
| Active Sessions        | `data.metrics.active_sessions`              | Integer                 |
| Error Count (24h)      | `data.metrics.error_count_24h`              | Integer, red if > 0     |
| Model                  | `data.model`                                | Full model identifier   |
| Active Version         | `data.active_version`                       | Semver string           |
| Canary Version         | `data.canary_version`                       | Semver or "--"          |

#### 3.1.3 Filters and Controls

| Control            | Type                  | Options                                                     | Default       |
|--------------------|-----------------------|-------------------------------------------------------------|---------------|
| Phase Filter       | `st.selectbox`        | `All`, `requirements`, `design`, `code`, `test`, `documentation`, `review`, `deploy` | `All` |
| Status Filter      | `st.selectbox`        | `All`, `active`, `inactive`, `degraded`, `circuit_open`     | `All`         |
| Search             | `st.text_input`       | Free-text; filters by agent name (client-side substring)    | Empty         |
| Refresh Button     | `st.button("Refresh")`| Triggers immediate data re-fetch                            | --            |

#### 3.1.4 Interactions

| Trigger                       | Action                                                      |
|-------------------------------|-------------------------------------------------------------|
| Click agent card              | Expands inline detail panel below the card; calls `GET /api/v1/agents/{id}/health` |
| Click expanded detail again   | Collapses detail panel                                      |
| Hover agent card              | Card background transitions to `--bg-card-hover`            |
| Change Phase filter           | Grid re-filters (client-side from cached agent list)        |
| Change Status filter          | Grid re-filters (client-side)                               |
| Type in Search                | Grid re-filters on each keystroke (client-side)             |
| Click Refresh button          | Clears `st.session_state` cache, re-fetches from API        |

#### 3.1.5 Data Sources

| Data                    | Endpoint                            | Method | Auth     |
|-------------------------|-------------------------------------|--------|----------|
| Agent list              | `GET /api/v1/agents`                | GET    | Bearer   |
| Agent health (on click) | `GET /api/v1/agents/{agent_id}/health` | GET | Bearer   |
| Cost alerts (banner)    | `WS /ws/cost-alerts`                | WS     | Token QP |

#### 3.1.6 Refresh Strategy

| Mechanism              | Interval / Trigger                    | Details                                  |
|------------------------|---------------------------------------|------------------------------------------|
| Auto-refresh           | 30 seconds (via `streamlit-autorefresh`) | Controlled by sidebar toggle; re-runs page script |
| Manual refresh         | User clicks Refresh button            | Immediate re-fetch; clears cache         |
| WebSocket (cost alerts)| Persistent connection                 | Displays real-time alert banner at top if budget warning received |

#### 3.1.7 States

| State    | Behavior                                                                                   |
|----------|--------------------------------------------------------------------------------------------|
| Loading  | Stat cards show `st.skeleton()` placeholders; grid area shows `st.spinner("Loading fleet data...")` |
| Empty    | Grid area shows `st.info("No agents registered. Register your first agent via the CLI.")` with a documentation link |
| Error    | Red `st.error("Failed to load fleet data: {error_message}. [Retry]")` banner at top; grid is hidden |
| Success  | All stat cards rendered with values; agent grid populates with cards                       |

---

### 3.2 SCR-02: Cost Monitor

| Field           | Value                                                         |
|-----------------|---------------------------------------------------------------|
| **ID**          | SCR-02                                                        |
| **Name**        | Cost Monitor                                                  |
| **File**        | `dashboard/pages/02_cost_monitor.py`                          |
| **Purpose**     | Visualize fleet and project-level spend over time with drill-down by agent, model, and project so Marcus can detect cost spikes and Lisa can verify budget compliance. |
| **Primary Users** | Marcus (DevOps), Lisa (Compliance), David (Delivery Lead)  |

#### 3.2.1 Layout

```
+------------------------------------------------------------------+
|  Cost Monitor                                    [Refresh] [v]    |
+------------------------------------------------------------------+
|                                                                    |
|  [Stat Card]       [Stat Card]       [Stat Card]   [Stat Card]   |
|  Today's Spend     Month-to-Date     Monthly Budget  Projected    |
|  $22.10            $487.32           $1,000.00       $689.50      |
|  +$3.65 vs avg     48.7% used        $512.68 remain  On track    |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Filters: [Date Range Picker] [Granularity: Daily|Weekly|Monthly] |
|           [Project v]  [Group By: Model|Agent|Project|Phase v]    |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Spend Over Time (Plotly area chart)                              |
|  +--------------------------------------------------------------+ |
|  |  $50 |........................................  budget line   | |
|  |      |                                                        | |
|  |  $25 |    /\    /\                                            | |
|  |      |   /  \__/  \___/\                                      | |
|  |   $0 |--/----------------\------>                             | |
|  |      Mar 1   Mar 8   Mar 15   Mar 23                         | |
|  +--------------------------------------------------------------+ |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Cost Breakdown (left half)       |  Top Spenders (right half)    |
|  Plotly donut chart               |  Horizontal bar chart          |
|  Grouped by selected dimension    |  Top 10 agents by cost         |
|                                   |                                |
+------------------------------------------------------------------+
|                                                                    |
|  Cost Details Table                                               |
|  +--------------------------------------------------------------+ |
|  | Key | Cost ($) | % of Total | Input Tokens | Output Tokens | | |
|  |     |          |            |              | Request Count | | |
|  +--------------------------------------------------------------+ |
|                                                                    |
+------------------------------------------------------------------+
```

#### 3.2.2 Data Elements

**Stat Cards (top row, 4 columns via `st.columns(4)`):**

| Card              | API Source                                  | Value Format           | Delta                            |
|-------------------|---------------------------------------------|------------------------|----------------------------------|
| Today's Spend     | Latest entry in `data.series` from `GET /api/v1/cost/fleet` | `${cost_usd:.2f}`    | vs. 7-day average daily spend    |
| Month-to-Date     | `data.budget.current_month_spend_usd`       | `${amount:.2f}`        | `{pct}% used` of monthly budget  |
| Monthly Budget    | `data.budget.monthly_limit_usd`             | `${amount:.2f}`        | `${remaining:.2f} remain`        |
| Projected Month-End | `data.budget.projected_month_end_usd`     | `${amount:.2f}`        | "On track" (green) or "Over budget" (red) based on `data.budget.on_track` |

**Spend Over Time Chart (Plotly area chart):**

- **X-axis:** Date (from `data.series[].date`)
- **Y-axis:** Cost in USD (from `data.series[].cost_usd`)
- **Budget line:** Horizontal dashed line at `data.budget.monthly_limit_usd / days_in_month` (daily budget) or full `monthly_limit_usd` (for monthly granularity)
- **Fill:** Gradient area fill below the line using `--brand-primary`
- **Hover tooltip:** Date, Cost, Input Tokens, Output Tokens, Run Count

Chart data fields per series point (from `GET /api/v1/cost/fleet`):

| Field           | API Source                     | Chart Role      |
|-----------------|--------------------------------|-----------------|
| Date            | `data.series[].date`           | X-axis          |
| Cost (USD)      | `data.series[].cost_usd`       | Y-axis, tooltip |
| Input Tokens    | `data.series[].input_tokens`   | Tooltip only    |
| Output Tokens   | `data.series[].output_tokens`  | Tooltip only    |
| Run Count       | `data.series[].run_count`      | Tooltip only    |

**Cost Breakdown Donut Chart (Plotly pie chart, left column):**

Data from `GET /api/v1/cost/breakdown` grouped by the selected `group_by` dimension:

| Field           | API Source                          | Chart Role      |
|-----------------|-------------------------------------|-----------------|
| Key             | `data.breakdown[].key`              | Segment label   |
| Cost (USD)      | `data.breakdown[].cost_usd`         | Segment size    |
| % of Total      | `data.breakdown[].pct_of_total`     | Segment tooltip |
| Request Count   | `data.breakdown[].request_count`    | Tooltip only    |

**Top Spenders Bar Chart (Plotly horizontal bar, right column):**

Top 10 items from `data.breakdown[]` sorted by `cost_usd` descending:

| Field           | API Source                          | Chart Role      |
|-----------------|-------------------------------------|-----------------|
| Key (name)      | `data.breakdown[].key`              | Y-axis label    |
| Cost (USD)      | `data.breakdown[].cost_usd`         | Bar length      |
| % of Total      | `data.breakdown[].pct_of_total`     | Bar annotation  |

**Cost Details Table (`st.dataframe`):**

| Column         | API Source                          | Width   | Sortable |
|----------------|-------------------------------------|---------|----------|
| Key            | `data.breakdown[].key`              | 200px   | Yes      |
| Cost ($)       | `data.breakdown[].cost_usd`         | 100px   | Yes      |
| % of Total     | `data.breakdown[].pct_of_total`     | 80px    | Yes      |
| Input Tokens   | `data.breakdown[].input_tokens`     | 120px   | Yes      |
| Output Tokens  | `data.breakdown[].output_tokens`    | 120px   | Yes      |
| Request Count  | `data.breakdown[].request_count`    | 100px   | Yes      |

#### 3.2.3 Filters and Controls

| Control            | Type                    | Options                                                 | Default            |
|--------------------|-------------------------|---------------------------------------------------------|--------------------|
| Date Range         | `st.date_input` (two)  | Start date and end date pickers                         | Last 30 days       |
| Granularity        | `st.radio`             | `Daily`, `Weekly`, `Monthly` (horizontal)               | `Daily`            |
| Project Filter     | `st.selectbox`         | `All Projects` + list of project IDs/names              | `All Projects`     |
| Group By           | `st.selectbox`         | `model`, `agent`, `project`, `phase`                    | `model`            |
| Refresh Button     | `st.button("Refresh")` | Triggers re-fetch                                       | --                 |

#### 3.2.4 Interactions

| Trigger                        | Action                                                     |
|--------------------------------|------------------------------------------------------------|
| Change date range              | Re-fetches fleet cost and breakdown data for new range     |
| Change granularity             | Re-fetches fleet cost with new `granularity` param         |
| Select a project               | Switches from `GET /api/v1/cost/fleet` to `GET /api/v1/cost/projects/{project_id}` |
| Change Group By                | Re-fetches breakdown with new `group_by` param             |
| Click donut segment            | Filters the details table to show only that segment        |
| Hover chart element            | Shows Plotly tooltip with full data                        |
| Click table column header      | Sorts table by that column (asc/desc toggle)               |
| Receive WS cost alert          | Shows `st.warning` or `st.error` banner at page top        |

#### 3.2.5 Data Sources

| Data                    | Endpoint                                     | Method | Auth     |
|-------------------------|----------------------------------------------|--------|----------|
| Fleet daily cost        | `GET /api/v1/cost/fleet`                     | GET    | Bearer   |
| Project daily cost      | `GET /api/v1/cost/projects/{project_id}`     | GET    | Bearer   |
| Cost breakdown          | `GET /api/v1/cost/breakdown`                 | GET    | Bearer   |
| Cost alerts             | `WS /ws/cost-alerts`                         | WS     | Token QP |

#### 3.2.6 Refresh Strategy

| Mechanism              | Interval / Trigger                    | Details                                  |
|------------------------|---------------------------------------|------------------------------------------|
| Auto-refresh           | 60 seconds (via `streamlit-autorefresh`) | Longer interval than Fleet Health due to lower volatility |
| Manual refresh         | User clicks Refresh button            | Immediate re-fetch                       |
| WebSocket (cost alerts)| Persistent connection                 | Real-time budget warning/critical banners |

#### 3.2.7 States

| State    | Behavior                                                                                   |
|----------|--------------------------------------------------------------------------------------------|
| Loading  | Stat cards show `st.skeleton()`; chart areas show `st.spinner("Loading cost data...")`     |
| Empty    | Charts show "No cost data for the selected period." message; stat cards show `$0.00`       |
| Error    | Red `st.error("Failed to load cost data: {message}. [Retry]")` banner; charts hidden       |
| Success  | All stat cards, charts, and table rendered with data                                       |

---

### 3.3 SCR-03: Pipeline Runs

| Field           | Value                                                         |
|-----------------|---------------------------------------------------------------|
| **ID**          | SCR-03                                                        |
| **Name**        | Pipeline Runs                                                 |
| **File**        | `dashboard/pages/03_pipeline_runs.py`                         |
| **Purpose**     | Show all pipeline runs with their current status, allow drill-down into step-by-step progress, and provide real-time updates for running pipelines so David can monitor document generation progress. |
| **Primary Users** | David (Delivery Lead), Sarah (Engineering Lead)             |

#### 3.3.1 Layout

```
+------------------------------------------------------------------+
|  Pipeline Runs                                   [Refresh] [v]    |
+------------------------------------------------------------------+
|                                                                    |
|  [Stat Card]      [Stat Card]      [Stat Card]    [Stat Card]    |
|  Total Runs       Running          Completed       Failed         |
|  47               2                41               4              |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Filters: [Status v]  [Pipeline v]  [Project v]                  |
|           [Started After]  [Started Before]                       |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Runs Table                                                       |
|  +--------------------------------------------------------------+ |
|  | Run ID   | Pipeline   | Project  | Status  | Progress |      | |
|  |          |            |          |         |          | Cost  | |
|  |          |            |          |         |          | Start | |
|  |          |            |          |         |          | Dur.  | |
|  |----------|------------|----------|---------|----------|-------| |
|  | run_7f3a | 12-doc-gen | proj_abc | Running | ████░ 58%| $1.47 | |
|  | run_8e4b | 12-doc-gen | proj_xyz | Done    | █████100%| $3.21 | |
|  +--------------------------------------------------------------+ |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Run Detail Panel (shown when row is clicked)                     |
|  +--------------------------------------------------------------+ |
|  | Run: run_7f3a2b1c   Pipeline: 12-doc-generation               | |
|  | Project: proj_abc123  Session: ses_a1b2c3d4                   | |
|  | Status: Running  Cost: $1.47  Progress: 58.3%                 | |
|  |                                                                | |
|  | Step Timeline (vertical step list)                             | |
|  | [1] Requirements Analysis  [green check] 3m 30s  $0.28        | |
|  | [2] Architecture Design    [green check] 3m 45s  $0.31        | |
|  | [3] CLAUDE.md Generation   [green check] 2m 10s  $0.15        | |
|  | [4] PRD Generation         [green check] 4m 20s  $0.22        | |
|  | [5] Code Generation        [blue pulse]  running  $0.12       | |
|  | [6] Test Strategy          [gray]        pending  --           | |
|  | ...                                                            | |
|  +--------------------------------------------------------------+ |
|                                                                    |
+------------------------------------------------------------------+
```

#### 3.3.2 Data Elements

**Stat Cards (top row, 4 columns via `st.columns(4)`):**

| Card           | Source                                           | Value               |
|----------------|--------------------------------------------------|---------------------|
| Total Runs     | `meta.total` from `GET /api/v1/pipelines`        | Integer count       |
| Running        | Count where `status == "running"` in current page | Integer, blue       |
| Completed      | Count where `status == "completed"` in current page | Integer, green    |
| Failed         | Count where `status == "failed"` in current page | Integer, red        |

**Runs Table (`st.dataframe` with row selection):**

| Column         | API Source                          | Width   | Format                    | Sortable |
|----------------|-------------------------------------|---------|---------------------------|----------|
| Run ID         | `data[].run_id`                     | 140px   | Truncated to last 8 chars | No       |
| Pipeline       | `data[].pipeline_name`              | 150px   | Plain text                | Yes      |
| Project        | `data[].project_id`                 | 120px   | Plain text                | Yes      |
| Status         | `data[].status`                     | 100px   | Colored badge (see 1.3)   | Yes      |
| Progress       | `data[].progress_pct`               | 120px   | Progress bar + percentage | Yes      |
| Cost           | `data[].cost_usd`                   | 80px    | `${cost:.2f}`             | Yes      |
| Steps          | `data[].steps_completed` / `data[].step_count` | 80px | `{done}/{total}`   | Yes      |
| Started        | `data[].started_at`                 | 140px   | Relative time + tooltip with full ISO | Yes |
| Duration       | Computed from `started_at` and `completed_at` | 100px | `{m}m {s}s` or "running" | Yes |

**Run Detail Panel (expanded on row click, data from `GET /api/v1/pipelines/{run_id}` + `GET /api/v1/pipelines/{run_id}/steps`):**

**Header fields:**

| Field           | API Source                          | Display Format            |
|-----------------|-------------------------------------|---------------------------|
| Run ID          | `data.run_id`                       | Full ID, monospace        |
| Pipeline Name   | `data.pipeline_name`                | Plain text                |
| Project ID      | `data.project_id`                   | Plain text                |
| Session ID      | `data.session_id`                   | Monospace                 |
| Status          | `data.status`                       | Colored badge             |
| Total Cost      | `data.cost_usd`                     | `${cost:.2f}`             |
| Progress        | `data.progress_pct`                 | `{pct}%` + progress bar   |
| Started At      | `data.started_at`                   | Full ISO datetime         |
| Completed At    | `data.completed_at`                 | Full ISO datetime or "--" |

**Step Timeline (vertical list from `GET /api/v1/pipelines/{run_id}/steps`):**

| Field              | API Source                          | Display Format                  |
|--------------------|-------------------------------------|---------------------------------|
| Step Number        | Derived from position               | `[{n}]` prefix                  |
| Step Name          | `data[].name`                       | Bold text                       |
| Agent ID           | `data[].agent_id`                   | Caption text                    |
| Step Status        | `data[].status`                     | Icon: green check (completed), blue pulse (running), red X (failed), gray circle (pending), skip icon (skipped) |
| Duration           | `data[].duration_seconds`           | `{m}m {s}s` or "running"       |
| Cost               | `data[].cost_usd`                   | `${cost:.2f}` or "--"          |
| Error Message      | `data[].error_message`              | Red text, shown only if non-null |
| Requires Approval  | `data[].requires_approval`          | "Approval gate" badge if true   |

#### 3.3.3 Filters and Controls

| Control              | Type                    | Options                                                     | Default        |
|----------------------|-------------------------|-------------------------------------------------------------|----------------|
| Status Filter        | `st.selectbox`          | `All`, `running`, `completed`, `failed`, `paused`, `cancelled` | `All`        |
| Pipeline Filter      | `st.selectbox`          | `All`, `12-doc-generation`, (other pipeline names)          | `All`          |
| Project Filter       | `st.selectbox`          | `All Projects` + available project IDs                      | `All Projects` |
| Started After        | `st.date_input`         | Date picker                                                 | 7 days ago     |
| Started Before       | `st.date_input`         | Date picker                                                 | Today          |
| Refresh Button       | `st.button("Refresh")`  | Triggers re-fetch                                           | --             |

#### 3.3.4 Interactions

| Trigger                        | Action                                                     |
|--------------------------------|------------------------------------------------------------|
| Click table row                | Expands Run Detail Panel below the table; fetches `GET /api/v1/pipelines/{run_id}` and `GET /api/v1/pipelines/{run_id}/steps` |
| Click expanded detail again    | Collapses detail panel                                     |
| Change any filter              | Re-fetches `GET /api/v1/pipelines` with updated query params |
| Hover table row                | Row highlight                                              |
| Hover step in timeline         | Shows full step metadata as tooltip                        |
| WS step update received        | Updates the step timeline in real-time (status, cost, duration) for the currently expanded run |

#### 3.3.5 Data Sources

| Data                    | Endpoint                                    | Method | Auth     |
|-------------------------|---------------------------------------------|--------|----------|
| Pipeline runs list      | `GET /api/v1/pipelines`                     | GET    | Bearer   |
| Pipeline run detail     | `GET /api/v1/pipelines/{run_id}`            | GET    | Bearer   |
| Pipeline run steps      | `GET /api/v1/pipelines/{run_id}/steps`      | GET    | Bearer   |
| Real-time step updates  | `WS /ws/pipeline/{run_id}`                  | WS     | Token QP |

#### 3.3.6 Refresh Strategy

| Mechanism              | Interval / Trigger                    | Details                                  |
|------------------------|---------------------------------------|------------------------------------------|
| Auto-refresh           | 15 seconds (via `streamlit-autorefresh`) | Faster cadence because running pipelines change frequently |
| Manual refresh         | User clicks Refresh button            | Immediate re-fetch of runs list          |
| WebSocket (pipeline)   | Per-run connection when detail is expanded | Opened when user clicks a running pipeline row; receives `step_started`, `step_completed`, `step_failed`, `approval_required`, `pipeline_completed` messages; auto-closes on terminal state |

#### 3.3.7 States

| State    | Behavior                                                                                   |
|----------|--------------------------------------------------------------------------------------------|
| Loading  | Stat cards show `st.skeleton()`; table shows `st.spinner("Loading pipeline runs...")`      |
| Empty    | Table area shows `st.info("No pipeline runs found for the selected filters. Trigger a new pipeline run via the CLI.")` |
| Error    | Red `st.error("Failed to load pipeline data: {message}. [Retry]")` banner; table hidden    |
| Success  | Stat cards and table rendered; running pipelines show animated progress bars                |

---

### 3.4 SCR-04: Audit Log

| Field           | Value                                                         |
|-----------------|---------------------------------------------------------------|
| **ID**          | SCR-04                                                        |
| **Name**        | Audit Log                                                     |
| **File**        | `dashboard/pages/04_audit_log.py`                             |
| **Purpose**     | Provide a searchable, filterable view of all immutable audit events so Lisa can perform compliance audits and Marcus can investigate operational incidents. |
| **Primary Users** | Lisa (Compliance), Marcus (DevOps)                          |

#### 3.4.1 Layout

```
+------------------------------------------------------------------+
|  Audit Log                                       [Refresh] [v]    |
+------------------------------------------------------------------+
|                                                                    |
|  [Stat Card]      [Stat Card]      [Stat Card]    [Stat Card]    |
|  Total Events     Info             Warning          Error/Critical|
|  1,247            1,180            42               25             |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Filters:                                                         |
|  [Severity v]  [Event Type v]  [Agent v]  [Project v]            |
|  [Start Time (datetime)]  [End Time (datetime)]                   |
|  [Correlation ID input]  [Session ID input]                       |
|                                                  [Export CSV]     |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Events Table                                                     |
|  +--------------------------------------------------------------+ |
|  | Timestamp | Severity | Event Type | Agent | Project |        | |
|  |           |          |            |       |         | Payload | |
|  |-----------|----------|------------|-------|---------|---------|  |
|  | Mar 23    | info     | agent_     | Code  | proj_   | {action | |
|  | 15:15:00  |          | invocation | Gen   | abc123  | : ...}  | |
|  | Mar 23    | info     | approval_  | --    | proj_   | {decis  | |
|  | 15:35:00  |          | decision   |       | abc123  | ion:..} | |
|  +--------------------------------------------------------------+ |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Event Detail Panel (shown when row is clicked)                   |
|  +--------------------------------------------------------------+ |
|  | Event ID: evt_9a8b7c6d-5e4f-3210-fedc-ba9876543210            | |
|  | Session: ses_a1b2c3d4  Correlation: cor_1234abcd               | |
|  | Agent: agt_code_gen_01  Project: proj_abc123                   | |
|  | Severity: info  Type: agent_invocation                        | |
|  | Timestamp: 2026-03-23T15:15:00Z                               | |
|  |                                                                | |
|  | Payload (formatted JSON)                                       | |
|  | {                                                              | |
|  |   "action": "generate_code",                                  | |
|  |   "input_tokens": 4500,                                       | |
|  |   "output_tokens": 1200,                                      | |
|  |   "duration_ms": 3420,                                        | |
|  |   "model": "claude-sonnet-4-20250514",                        | |
|  |   "status": "success"                                         | |
|  | }                                                              | |
|  +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

#### 3.4.2 Data Elements

**Stat Cards (top row, 4 columns via `st.columns(4)`):**

| Card              | Source                                                 | Value             |
|-------------------|--------------------------------------------------------|-------------------|
| Total Events      | `meta.total` from `GET /api/v1/audit/events`           | Comma-formatted   |
| Info              | Count where `severity == "info"` (from current page)   | Comma-formatted   |
| Warning           | Count where `severity == "warning"`                    | Comma-formatted, amber |
| Error / Critical  | Count where `severity in ("error", "critical")`        | Comma-formatted, red |

**Events Table (`st.dataframe` with row selection):**

| Column          | API Source                          | Width   | Format                          | Sortable |
|-----------------|-------------------------------------|---------|---------------------------------|----------|
| Timestamp       | `data[].timestamp`                  | 160px   | `YYYY-MM-DD HH:MM:SS` (UTC)    | Yes      |
| Severity        | `data[].severity`                   | 80px    | Colored badge: info=blue, warning=amber, error=red, critical=red bold | Yes |
| Event Type      | `data[].event_type`                 | 140px   | Snake_case converted to Title Case | Yes   |
| Agent           | `data[].agent_id`                   | 140px   | Agent ID or "--" if null        | Yes      |
| Project         | `data[].project_id`                 | 120px   | Project ID                      | Yes      |
| Session         | `data[].session_id`                 | 120px   | Truncated to last 8 chars       | No       |
| Correlation ID  | `data[].correlation_id`             | 120px   | Truncated to last 8 chars       | No       |

**Event Detail Panel (expanded on row click, data from `GET /api/v1/audit/events/{event_id}`):**

| Field            | API Source                         | Display Format                     |
|------------------|------------------------------------|------------------------------------|
| Event ID         | `data.event_id`                    | Full ID, monospace                 |
| Session ID       | `data.session_id`                  | Full ID, monospace                 |
| Correlation ID   | `data.correlation_id`              | Full ID, monospace                 |
| Project ID       | `data.project_id`                  | Plain text                         |
| Agent ID         | `data.agent_id`                    | Plain text or "--"                 |
| Event Type       | `data.event_type`                  | Badge                              |
| Severity         | `data.severity`                    | Colored badge                      |
| Timestamp        | `data.timestamp`                   | Full ISO 8601                      |
| Payload          | `data.payload`                     | Pretty-printed JSON via `st.json()` |

#### 3.4.3 Filters and Controls

| Control              | Type                    | Options                                                          | Default        |
|----------------------|-------------------------|------------------------------------------------------------------|----------------|
| Severity Filter      | `st.multiselect`        | `info`, `warning`, `error`, `critical`                           | All selected   |
| Event Type Filter    | `st.multiselect`        | `agent_invocation`, `approval_decision`, `pipeline_start`, `pipeline_complete`, `error`, `cost_alert`, `config_change` | All selected |
| Agent Filter         | `st.selectbox`          | `All Agents` + list of agent IDs                                 | `All Agents`   |
| Project Filter       | `st.selectbox`          | `All Projects` + list of project IDs                             | `All Projects` |
| Start Time           | `st.date_input` + `st.time_input` | Datetime picker                                        | 24 hours ago   |
| End Time             | `st.date_input` + `st.time_input` | Datetime picker                                        | Now            |
| Correlation ID       | `st.text_input`         | Free text UUID input                                             | Empty          |
| Session ID           | `st.text_input`         | Free text UUID input                                             | Empty          |
| Export CSV Button     | `st.button("Export CSV")` | Triggers `GET /api/v1/audit/events/export` with current filters | --             |
| Refresh Button       | `st.button("Refresh")`  | Triggers re-fetch                                                | --             |

#### 3.4.4 Interactions

| Trigger                        | Action                                                     |
|--------------------------------|------------------------------------------------------------|
| Click table row                | Expands Event Detail Panel; fetches `GET /api/v1/audit/events/{event_id}` |
| Change any filter              | Re-fetches `GET /api/v1/audit/events` with updated query params |
| Click Export CSV               | Calls `GET /api/v1/audit/events/export` with current filter params; for small exports (< 10K rows) triggers browser download; for large exports shows `st.info("Export processing... check back shortly.")` with polling |
| Click Correlation ID in detail | Populates the Correlation ID filter and re-fetches to show all events in that workflow |
| Click Session ID in detail     | Populates the Session ID filter and re-fetches               |
| Pagination (page controls)     | Fetches next/previous page via `page` query param            |

#### 3.4.5 Data Sources

| Data                    | Endpoint                              | Method | Auth     |
|-------------------------|---------------------------------------|--------|----------|
| Audit events list       | `GET /api/v1/audit/events`            | GET    | Bearer   |
| Audit event detail      | `GET /api/v1/audit/events/{event_id}` | GET    | Bearer   |
| Export audit events     | `GET /api/v1/audit/events/export`     | GET    | Bearer   |

#### 3.4.6 Refresh Strategy

| Mechanism              | Interval / Trigger                    | Details                                  |
|------------------------|---------------------------------------|------------------------------------------|
| Auto-refresh           | 60 seconds (via `streamlit-autorefresh`) | Lower cadence; audit data is append-only and less time-critical |
| Manual refresh         | User clicks Refresh button            | Immediate re-fetch with current filters  |
| Pagination             | User clicks page controls             | Fetches the requested page               |

#### 3.4.7 States

| State    | Behavior                                                                                   |
|----------|--------------------------------------------------------------------------------------------|
| Loading  | Stat cards show `st.skeleton()`; table shows `st.spinner("Loading audit events...")`       |
| Empty    | Table area shows `st.info("No audit events match the selected filters. Try broadening your search criteria.")` |
| Error    | Red `st.error("Failed to load audit events: {message}. [Retry]")` banner; table hidden     |
| Success  | Stat cards and table rendered; severity column uses color coding                           |
| Exporting| `st.info("Exporting {n} events... This may take a moment.")` spinner; button disabled      |

---

### 3.5 SCR-05: Approval Queue

| Field           | Value                                                         |
|-----------------|---------------------------------------------------------------|
| **ID**          | SCR-05                                                        |
| **Name**        | Approval Queue                                                |
| **File**        | `dashboard/pages/05_approval_queue.py`                        |
| **Purpose**     | Display pending approval requests with full context and provide Approve/Reject actions so Sarah can review agent outputs and unblock pipelines efficiently. |
| **Primary Users** | Sarah (Engineering Lead), David (Delivery Lead)             |

#### 3.5.1 Layout

```
+------------------------------------------------------------------+
|  Approval Queue                                  [Refresh] [v]    |
+------------------------------------------------------------------+
|                                                                    |
|  [Stat Card]      [Stat Card]      [Stat Card]    [Stat Card]    |
|  Pending           Approved Today  Rejected Today  Avg Response   |
|  3                 8               2                4m 32s         |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Filters: [Status v]  [Pipeline v]  [Project v]                  |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Approval Cards (vertical list, one per approval)                 |
|  +--------------------------------------------------------------+ |
|  | PENDING  |  Code Generation - Step 5                          | |
|  |          |  Pipeline: 12-doc-generation                       | |
|  |          |  Project: proj_abc123   Run: run_7f3a2b1c          | |
|  |          |  Requested: 10 minutes ago                         | |
|  |          |                                                    | |
|  |          |  Summary:                                          | |
|  |          |  Code generation step completed. 14 files           | |
|  |          |  generated, 2,847 lines. Test coverage estimated    | |
|  |          |  at 89%. Review required before proceeding to       | |
|  |          |  integration testing.                               | |
|  |          |                                                    | |
|  |          |  Artifacts:                                        | |
|  |          |  Files: 14 | Lines: 2,847 | Coverage: 89%          | |
|  |          |  Quality Score: 8.4/10                             | |
|  |          |  Warnings: 2                                       | |
|  |          |                                                    | |
|  |          |  [View Warnings]                                   | |
|  |          |                                                    | |
|  |          |  Comment: [_________________________]               | |
|  |          |                                                    | |
|  |          |  [Approve]            [Reject v]                   | |
|  |          |                       [Reject & Pause]             | |
|  |          |                       [Reject & Cancel]            | |
|  +--------------------------------------------------------------+ |
|  | PENDING  |  Architecture Review - Step 3                     | |
|  |          |  ...                                               | |
|  +--------------------------------------------------------------+ |
|                                                                    |
+------------------------------------------------------------------+
|                                                                    |
|  Recent Decisions (collapsed by default, expandable)              |
|  +--------------------------------------------------------------+ |
|  | Decided    | Step        | Decision | By     | Comment       | |
|  |------------|-------------|----------|--------|---------------| |
|  | 10m ago    | Test Strat. | Approved | Sarah  | LGTM          | |
|  | 25m ago    | Code Gen    | Rejected | Sarah  | Coverage low  | |
|  +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

#### 3.5.2 Data Elements

**Stat Cards (top row, 4 columns via `st.columns(4)`):**

| Card               | Source                                                    | Value             |
|--------------------|-----------------------------------------------------------|-------------------|
| Pending            | `meta.total` from `GET /api/v1/approvals?status=pending`  | Integer, amber if > 0 |
| Approved Today     | Count from `GET /api/v1/approvals?status=approved` (today's date filter) | Integer, green |
| Rejected Today     | Count from `GET /api/v1/approvals?status=rejected` (today's date filter) | Integer, red   |
| Avg Response Time  | Computed from `decided_at - requested_at` across today's resolved approvals | `{m}m {s}s`   |

**Approval Cards (one per pending approval, from `GET /api/v1/approvals?status=pending`):**

| Field                | API Source                               | Display Format                    |
|----------------------|------------------------------------------|-----------------------------------|
| Status Badge         | `data[].status`                          | `PENDING` in amber; `APPROVED` in green; `REJECTED` in red |
| Step Name            | `data[].step_name`                       | Bold title                        |
| Step ID              | `data[].step_id`                         | Caption                           |
| Pipeline Name        | `data[].pipeline_name`                   | Plain text                        |
| Project ID           | `data[].project_id`                      | Plain text                        |
| Run ID               | `data[].run_id`                          | Truncated, monospace              |
| Requested At         | `data[].requested_at`                    | Relative time (e.g., "10 minutes ago") |
| Summary              | `data[].summary`                         | Multi-line text block             |

**Artifact details (from `GET /api/v1/approvals/{approval_id}`, fetched when card renders):**

| Field                   | API Source                                    | Display Format       |
|-------------------------|-----------------------------------------------|----------------------|
| Files Generated         | `data.artifacts.files_generated`              | Integer              |
| Total Lines             | `data.artifacts.total_lines`                  | Comma-formatted      |
| Est. Test Coverage      | `data.artifacts.estimated_test_coverage_pct`  | `{pct}%`             |
| Quality Score           | `data.artifacts.quality_score`                | `{score}/10` with color: green >= 8, amber >= 6, red < 6 |
| Warnings                | `data.artifacts.warnings`                     | Count badge; expandable list on click |

**Action controls per card:**

| Control              | Type                           | Details                                  |
|----------------------|--------------------------------|------------------------------------------|
| Comment Input        | `st.text_area`                 | Optional comment for the approval/rejection decision |
| Approve Button       | `st.button("Approve")`         | Green-styled; calls `POST /api/v1/approvals/{id}/approve` with `{"comment": "..."}` |
| Reject Dropdown      | `st.selectbox` + `st.button`   | Two options: "Reject & Pause" (`action: "pause"`) or "Reject & Cancel" (`action: "cancel"`); calls `POST /api/v1/approvals/{id}/reject` |

**Recent Decisions Table (expandable section via `st.expander("Recent Decisions")`):**

| Column         | API Source                          | Width   | Format                          |
|----------------|-------------------------------------|---------|---------------------------------|
| Decided        | `data[].decided_at`                 | 100px   | Relative time                   |
| Step           | `data[].step_name`                  | 150px   | Plain text                      |
| Pipeline       | `data[].pipeline_name`              | 140px   | Plain text                      |
| Decision       | `data[].status`                     | 80px    | Colored badge (approved/rejected) |
| Decided By     | `data[].decision_by`               | 120px   | Email or username                |
| Comment        | `data[].decision_comment`           | 200px   | Truncated with tooltip           |

#### 3.5.3 Filters and Controls

| Control              | Type                    | Options                                                 | Default        |
|----------------------|-------------------------|---------------------------------------------------------|----------------|
| Status Filter        | `st.selectbox`          | `Pending`, `Approved`, `Rejected`, `All`                | `Pending`      |
| Pipeline Filter      | `st.selectbox`          | `All Pipelines` + pipeline name list                    | `All Pipelines`|
| Project Filter       | `st.selectbox`          | `All Projects` + project ID list                        | `All Projects` |
| Refresh Button       | `st.button("Refresh")`  | Triggers re-fetch                                       | --             |

#### 3.5.4 Interactions

| Trigger                        | Action                                                     |
|--------------------------------|------------------------------------------------------------|
| Click Approve                  | Sends `POST /api/v1/approvals/{id}/approve` with comment; on success shows `st.success("Approved. Pipeline resumed.")` and removes card from pending list; on error shows `st.error()` |
| Click Reject (Pause)           | Sends `POST /api/v1/approvals/{id}/reject` with `{"comment": "...", "action": "pause"}`; on success shows `st.warning("Rejected. Pipeline paused.")` and removes card |
| Click Reject (Cancel)          | Sends `POST /api/v1/approvals/{id}/reject` with `{"comment": "...", "action": "cancel"}`; on success shows `st.warning("Rejected. Pipeline cancelled.")` and removes card |
| Click View Warnings            | Expands warning list inline below the artifacts section     |
| WS new_approval received       | Adds a new card to the top of the pending list with `st.toast("New approval request: {step_name}")` notification |
| WS approval_resolved received  | Removes the resolved card from pending list; updates Recent Decisions table |
| Change filter                  | Re-fetches approval list with updated query params          |

#### 3.5.5 Data Sources

| Data                    | Endpoint                                    | Method | Auth     |
|-------------------------|---------------------------------------------|--------|----------|
| Approval list (pending) | `GET /api/v1/approvals?status=pending`      | GET    | Bearer   |
| Approval list (resolved)| `GET /api/v1/approvals?status=approved` / `rejected` | GET | Bearer |
| Approval detail         | `GET /api/v1/approvals/{approval_id}`       | GET    | Bearer   |
| Approve action          | `POST /api/v1/approvals/{id}/approve`       | POST   | Bearer   |
| Reject action           | `POST /api/v1/approvals/{id}/reject`        | POST   | Bearer   |
| Real-time notifications | `WS /ws/approvals`                          | WS     | Token QP |

#### 3.5.6 Refresh Strategy

| Mechanism              | Interval / Trigger                    | Details                                  |
|------------------------|---------------------------------------|------------------------------------------|
| Auto-refresh           | 15 seconds (via `streamlit-autorefresh`) | Fast cadence because pending approvals block pipelines (SM-6: P95 response < 15 min) |
| Manual refresh         | User clicks Refresh button            | Immediate re-fetch                       |
| WebSocket (approvals)  | Persistent connection                 | Receives `new_approval` and `approval_resolved` messages; updates list in real-time |

#### 3.5.7 States

| State    | Behavior                                                                                   |
|----------|--------------------------------------------------------------------------------------------|
| Loading  | Stat cards show `st.skeleton()`; card list shows `st.spinner("Loading approvals...")`      |
| Empty    | Card area shows `st.success("No pending approvals. All pipelines are unblocked.")` with a green checkmark icon |
| Error    | Red `st.error("Failed to load approvals: {message}. [Retry]")` banner; cards hidden        |
| Success  | Stat cards and approval cards rendered; pending cards show action buttons                   |
| Submitting | After Approve/Reject click: button shows spinner, all buttons on that card disabled, `st.spinner("Submitting decision...")` |

---

## 4. Component States

The following table defines the four global states that apply consistently across all pages and components.

| State     | Visual Treatment                                         | Streamlit Implementation                    | Duration / Trigger                          |
|-----------|----------------------------------------------------------|---------------------------------------------|---------------------------------------------|
| **Loading** | Skeleton placeholders for stat cards; spinner with descriptive message for main content area; all interactive controls disabled | `st.skeleton()` for metric cards; `st.spinner("Loading {resource}...")` for content areas | From page load / refresh trigger until API response received |
| **Empty**   | Informational blue banner with contextual message explaining why there is no data and what action the user can take | `st.info("{context-specific message}")` | When API returns `data: []` or `meta.total: 0` |
| **Error**   | Red error banner at the top of the content area with the error message and a Retry button; all content below the banner is hidden | `st.error("Failed to load {resource}: {error.message}")` followed by `st.button("Retry")` | When API returns HTTP 4xx/5xx or network timeout |
| **Success** | All components rendered with live data; stat cards show values with deltas; charts are interactive; tables are sortable and clickable | Standard Streamlit components with data | When API returns HTTP 200 with non-empty data |

### 4.1 State Transitions

```
[Page Load] --> [Loading]
    |
    +--> API Success, data non-empty --> [Success]
    +--> API Success, data empty    --> [Empty]
    +--> API Error                  --> [Error]
                                          |
                                          +--> User clicks Retry --> [Loading]
    [Success] --> User clicks Refresh --> [Loading]
    [Success] --> Auto-refresh timer  --> [Loading] (with stale data shown until new data arrives)
```

### 4.2 Stale-While-Revalidate

When auto-refresh triggers on a page in the Success state, the existing data remains visible (not replaced by a loading spinner). Only if the re-fetch fails does the page transition to Error. This prevents the "flash of loading" on every auto-refresh cycle and satisfies Q-003 (< 500ms perceived navigation).

---

## 5. Keyboard Navigation

### 5.1 Global Keyboard Shortcuts

All keyboard shortcuts are implemented via Streamlit's `st.components.v1.html()` with a small JavaScript snippet that listens for keydown events and triggers Streamlit reruns via `window.parent.postMessage`.

| Shortcut       | Action                         | Scope          |
|----------------|--------------------------------|----------------|
| `R`            | Refresh current page           | All pages      |
| `1` - `5`      | Navigate to page 1-5           | All pages      |
| `Escape`       | Close expanded detail panel    | All pages      |
| `?`            | Show keyboard shortcut help    | All pages      |

### 5.2 Page-Specific Shortcuts

**SCR-01 Fleet Health:**

| Shortcut  | Action                                     |
|-----------|--------------------------------------------|
| `F`       | Focus the Search input                     |
| Arrow keys| Navigate between agent cards in the grid   |
| `Enter`   | Expand/collapse the focused agent card     |

**SCR-02 Cost Monitor:**

| Shortcut  | Action                                     |
|-----------|--------------------------------------------|
| `D`       | Set granularity to Daily                   |
| `W`       | Set granularity to Weekly                  |
| `M`       | Set granularity to Monthly                 |

**SCR-03 Pipeline Runs:**

| Shortcut       | Action                                |
|----------------|---------------------------------------|
| `Up` / `Down`  | Navigate between runs in the table    |
| `Enter`        | Expand/collapse the focused run       |

**SCR-04 Audit Log:**

| Shortcut       | Action                                |
|----------------|---------------------------------------|
| `E`            | Trigger CSV export with current filters |
| `Up` / `Down`  | Navigate between events in the table  |
| `Enter`        | Expand/collapse the focused event     |

**SCR-05 Approval Queue:**

| Shortcut       | Action                                        |
|----------------|-----------------------------------------------|
| `A`            | Approve the currently focused approval card   |
| `J`            | Reject (Pause) the currently focused card     |
| `K`            | Reject (Cancel) the currently focused card    |
| `Up` / `Down`  | Navigate between approval cards               |
| `Tab`          | Move focus to next interactive element        |

### 5.3 Tab Order Per Page

All pages follow a consistent top-to-bottom, left-to-right tab order:

1. Sidebar navigation links
2. Page-level Refresh button
3. Filter controls (left to right, top to bottom)
4. Action buttons within filter bar (e.g., Export CSV)
5. Main content area (table rows, chart controls, cards)
6. Detail panel controls (when expanded)
7. Pagination controls (when present)

Focus is trapped within modal-like detail panels when expanded. Pressing `Escape` returns focus to the triggering element (the table row or card that was clicked).

---

## 6. Accessibility

### 6.1 WCAG 2.1 AA Compliance (Q-019)

The dashboard targets WCAG 2.1 Level AA conformance across all five pages. The following success criteria are specifically addressed:

| WCAG Criterion       | Requirement                                       | Implementation                                   |
|----------------------|---------------------------------------------------|--------------------------------------------------|
| 1.1.1 Non-text Content | All non-text content has text alternatives      | All chart images have `alt` text via Plotly `title`; status icons use `aria-label` |
| 1.3.1 Info and Relationships | Structure is programmatically determinable | Semantic HTML via Streamlit's heading hierarchy (`st.title` > `st.header` > `st.subheader`) |
| 1.3.2 Meaningful Sequence | Reading order matches visual order            | DOM order follows top-to-bottom layout; no CSS reordering |
| 1.4.1 Use of Color   | Color is not the sole means of conveying info    | All status indicators use both color AND text label (e.g., green dot + "Active") |
| 1.4.3 Contrast (Minimum) | Text contrast >= 4.5:1                        | All color pairs tested (see Section 1.3); `#FAFAFA` on `#0E1117` = 15.3:1 |
| 1.4.11 Non-text Contrast | UI component contrast >= 3:1                  | Focus rings, buttons, and form borders all exceed 3:1 against backgrounds |
| 2.1.1 Keyboard       | All functionality operable via keyboard           | Tab order defined (Section 5.3); shortcuts listed (Section 5.1, 5.2) |
| 2.1.2 No Keyboard Trap | Focus is never trapped                          | Escape key closes all expanded panels; tab cycles through page |
| 2.4.1 Bypass Blocks  | Skip-to-content mechanism available               | Streamlit sidebar provides navigation bypass; skip link added via custom component |
| 2.4.3 Focus Order     | Focus order preserves meaning                    | Tab order follows visual layout (Section 5.3) |
| 2.4.7 Focus Visible   | Focus indicator is visible                       | 2px solid `#6C63FF` outline on all focusable elements |
| 3.1.1 Language of Page | Page language is programmatically determinable   | `<html lang="en">` set via `st.set_page_config` |
| 4.1.2 Name, Role, Value | All UI components have accessible names         | Streamlit widgets include `label` parameter; custom components use ARIA attributes |

### 6.2 Color Contrast Ratios (Q-021)

All text-on-background combinations meet the minimum 4.5:1 ratio required by WCAG 2.1 AA:

| Foreground         | Background         | Ratio  | Pass |
|--------------------|--------------------| -------|------|
| `#FAFAFA` (text)   | `#0E1117` (page)   | 15.3:1 | Yes  |
| `#FAFAFA` (text)   | `#1A1D24` (card)   | 12.8:1 | Yes  |
| `#8B949E` (secondary) | `#0E1117` (page) | 4.6:1  | Yes  |
| `#3FB950` (success)| `#0E1117` (page)   | 5.8:1  | Yes  |
| `#D29922` (warning)| `#0E1117` (page)   | 5.2:1  | Yes  |
| `#F85149` (error)  | `#0E1117` (page)   | 5.4:1  | Yes  |
| `#58A6FF` (info)   | `#0E1117` (page)   | 5.1:1  | Yes  |
| `#6C63FF` (primary)| `#0E1117` (page)   | 4.7:1  | Yes  |

### 6.3 Screen Reader Support

- All `st.metric()` cards include descriptive `label` and `help` parameters so screen readers announce "Total Agents: 12, up 2 from yesterday."
- All `st.dataframe()` tables render as HTML `<table>` elements with proper `<thead>` and `<tbody>` for screen reader table navigation.
- Status badges include `aria-label` text (e.g., `aria-label="Status: Active"`) in addition to visual color.
- Plotly charts include `title` and `meta` properties for screen reader announcement of chart purpose.
- Toast notifications (`st.toast()`) use `role="alert"` for immediate screen reader announcement.
- Error banners (`st.error()`) use `role="alert"` and `aria-live="assertive"`.

### 6.4 Focus Indicators (Q-020)

All interactive elements display a visible focus indicator:

- **Focus ring:** 2px solid `#6C63FF` with 2px offset, applied to buttons, inputs, links, table rows, and cards.
- **High-contrast mode:** The focus ring color changes to `#FFFFFF` (white) when the user has `prefers-contrast: more` set, ensuring visibility in all configurations.
- **Skip link:** A visually hidden "Skip to main content" link appears at the top of every page and becomes visible on focus, allowing keyboard users to bypass the sidebar navigation.

### 6.5 Streamlit-Specific Considerations

| Consideration                     | Mitigation                                                     |
|-----------------------------------|----------------------------------------------------------------|
| Streamlit reruns clear focus      | After rerun, focus is restored to the previously focused element using `st.session_state` tracking |
| Streamlit widgets lack ARIA roles | Custom CSS/JS injected via `st.markdown(unsafe_allow_html=True)` to add `aria-label` and `role` attributes where Streamlit defaults are insufficient |
| Auto-refresh causes rerun         | Stale-while-revalidate pattern (Section 4.2) prevents disorienting full-page flashes; `aria-live="polite"` regions announce data updates without interrupting workflow |
| `st.dataframe` limited keyboard nav | Custom JavaScript component wraps dataframe for arrow-key navigation and Enter-to-expand |
| Dark theme contrast               | All colors verified against dark backgrounds (Section 6.2); no reliance on default Streamlit color tokens that may not meet AA |

---

## 7. Cross-Cutting Concerns

### 7.1 Authentication Flow

1. User navigates to `dashboard/app.py`.
2. If no valid JWT in `st.session_state`, user is redirected to a login form.
3. Login form collects email/password and calls `POST /api/v1/auth/token`.
4. On success, JWT and refresh token are stored in `st.session_state`.
5. All subsequent API calls include `Authorization: Bearer <jwt>` header.
6. Token refresh is handled transparently: if an API call returns 401, the dashboard calls `POST /api/v1/auth/refresh` and retries.
7. If refresh fails, user is redirected to the login form.

### 7.2 API Client Layer

All pages share a common `dashboard/api_client.py` module that:

- Wraps `requests` (or `httpx` for async) with the base URL, auth headers, and retry logic.
- Parses the standard response envelope (`data`, `meta`, `errors`).
- Raises typed exceptions on error responses that pages catch and display via `st.error()`.
- Adds `X-Request-ID` (UUID v4) to every request for traceability.
- Handles pagination via a `fetch_all_pages()` helper for list endpoints.

### 7.3 Session State Management

Streamlit `st.session_state` is used to persist:

| Key                          | Type    | Purpose                                              |
|------------------------------|---------|------------------------------------------------------|
| `auth_token`                 | str     | JWT bearer token                                     |
| `refresh_token`              | str     | Refresh token for silent re-auth                     |
| `user_email`                 | str     | Current user's email for sidebar display             |
| `user_role`                  | str     | Current user's role for sidebar display              |
| `auto_refresh_enabled`       | bool    | Whether auto-refresh is active                       |
| `{page}_selected_id`        | str     | ID of the currently expanded detail row/card per page |
| `{page}_filters`            | dict    | Current filter state per page for persistence across reruns |
| `{page}_cache_timestamp`    | float   | Timestamp of last successful data fetch per page     |
| `{page}_cached_data`        | dict    | Cached API response for stale-while-revalidate       |

### 7.4 Error Handling

| Error Type               | User-Facing Behavior                                        |
|--------------------------|-------------------------------------------------------------|
| Network timeout          | `st.error("Request timed out. Check your connection and retry.")` + Retry button |
| HTTP 401 Unauthorized    | Silent token refresh attempt; if that fails, redirect to login |
| HTTP 403 Forbidden       | `st.warning("You do not have permission to view this data. Contact your administrator.")` |
| HTTP 404 Not Found       | `st.warning("The requested resource was not found. It may have been deleted.")` |
| HTTP 429 Rate Limited    | `st.warning("Too many requests. Retrying in {retry_after} seconds...")` + automatic retry after `Retry-After` header |
| HTTP 500 / 503           | `st.error("Server error: {message}. The team has been notified. [Retry]")` |
| WebSocket disconnect     | Silent reconnect with exponential backoff (1s, 2s, 4s, max 30s); `st.caption("Reconnecting...")` in sidebar |

### 7.5 Performance Budget (Q-003)

| Metric                        | Target        | Measurement                                      |
|-------------------------------|---------------|--------------------------------------------------|
| Initial page load (DOMContentLoaded) | < 3s   | Lighthouse CI in GitHub Actions on every PR touching `dashboard/**` |
| In-app navigation             | < 500ms       | Streamlit rerun time measured by `streamlit-autorefresh` callback |
| API call response (non-LLM)   | < 200ms P95   | `X-Response-Time` header parsing in API client   |
| Chart render time              | < 300ms       | Plotly figure construction profiled in dev mode   |
| Data cache TTL                 | 15-60s        | Per-page auto-refresh intervals (see each screen spec) |

### 7.6 WebSocket Connection Management

All WebSocket connections are managed by a shared `dashboard/ws_client.py` module:

- Connections are established on page load for persistent channels (`/ws/cost-alerts`, `/ws/approvals`).
- Per-run connections (`/ws/pipeline/{run_id}`) are opened only when a running pipeline detail panel is expanded.
- All connections include JWT authentication via `?token=<jwt>` query parameter.
- Reconnection uses exponential backoff: 1s, 2s, 4s, 8s, 16s, 30s (max).
- Connection health is displayed in the sidebar: a green dot for "Connected" or amber dot for "Reconnecting."
- Messages are processed in a background thread and pushed to `st.session_state` for the next rerun cycle.

### 7.7 Data Formatting Utilities

A shared `dashboard/formatters.py` module provides consistent formatting:

| Function                  | Input                | Output                        |
|---------------------------|----------------------|-------------------------------|
| `format_currency(n)`     | `float`              | `$1,234.56`                   |
| `format_relative_time(t)`| `datetime`           | "5s ago", "10m ago", "2h ago" |
| `format_duration(s)`     | `int` (seconds)      | "3m 30s", "1h 12m"           |
| `format_number(n)`       | `int`                | "1,842"                       |
| `format_pct(n)`          | `float`              | "99.7%"                       |
| `truncate_id(id, n=8)`   | `str`                | Last `n` characters           |
| `status_color(status)`   | `str`                | Hex color from Section 1.3    |
| `severity_color(sev)`    | `str`                | Hex color from Section 1.3    |

---

*End of Design Specification*
