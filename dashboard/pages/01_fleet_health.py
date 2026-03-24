"""Fleet Health — Agent status grid + MCP monitoring panel.

Primary personas: David Okonkwo (DevOps), Jason Park (Tech Lead)
Interactions: I-020 (list_agents), I-023 (health), I-080 (fleet_health), I-081 (mcp_status), I-082 (mcp_calls)
Data from: GET /api/v1/agents, GET /api/v1/system/health, GET /api/v1/system/mcp, GET /api/v1/audit/mcp-calls
Auto-refresh: 30s
"""
import streamlit as st
import pandas as pd
from dashboard.components.api_client import api_get
from dashboard.components.status_badge import status_badge
from dashboard.components.metric_card import metric_card
from dashboard.config import FLEET_HEALTH_POLL, STATUS_COLORS

st.set_page_config(page_title="Fleet Health", layout="wide")
st.title("Fleet Health Overview")

# Auto-refresh
if "fleet_refresh" not in st.session_state:
    st.session_state.fleet_refresh = 0

# --- Fleet Health Summary (I-080) ---
col1, col2, col3, col4 = st.columns(4)
health_data = api_get("/system/health")
if health_data.get("data"):
    h = health_data["data"]
    with col1: metric_card("Total Agents", str(h.get("total_agents", 0)))
    with col2: metric_card("Healthy", str(h.get("healthy", 0)))
    with col3: metric_card("Degraded", str(h.get("degraded", 0)))
    with col4: metric_card("Fleet Cost Today", f"${h.get('fleet_cost_today_usd', 0):.2f}")
else:
    st.error("Could not load fleet health data")

st.markdown("---")

# --- Agent Grid (I-020) ---
st.subheader("Agent Registry")
# Phase filter
phases = ["all", "govern", "design", "build", "test", "deploy", "operate", "oversight"]
selected_phase = st.selectbox("Filter by Phase", phases)

params = {}
if selected_phase != "all":
    params["phase"] = selected_phase

agents_data = api_get("/agents", params=params)
if agents_data.get("data"):
    agents = agents_data["data"]
    if isinstance(agents, list) and agents:
        df = pd.DataFrame(agents)
        display_cols = ["agent_id", "name", "phase", "status", "active_version", "maturity", "archetype", "model"]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], use_container_width=True, hide_index=True)
    else:
        st.info("No agents found for this filter.")
else:
    st.error("Could not load agent list")

st.markdown("---")

# --- MCP Monitoring Panel (I-081, I-082) ---
st.subheader("MCP Monitoring")
mcol1, mcol2 = st.columns(2)

with mcol1:
    st.markdown("**MCP Server Status**")
    mcp_data = api_get("/system/mcp")
    if mcp_data.get("data"):
        servers = mcp_data["data"]
        if isinstance(servers, list):
            for srv in servers:
                st.markdown(f"**{srv.get('server_name', 'unknown')}** — {srv.get('status', 'unknown')}")
                st.caption(f"Tools: {srv.get('tools_registered', 0)} | Error rate: {srv.get('error_rate_1h', 0):.1%} | Latency: {srv.get('avg_latency_ms', 0):.0f}ms")

with mcol2:
    st.markdown("**Recent MCP Tool Calls**")
    calls_data = api_get("/audit/mcp-calls", params={"limit": 10})
    if calls_data.get("data"):
        calls = calls_data["data"]
        if isinstance(calls, list):
            for call in calls[:10]:
                st.markdown(f"`{call.get('tool_name', '')}` by {call.get('caller', 'unknown')} — {call.get('status', '')}")
    else:
        st.caption("No recent MCP calls")

# Auto-refresh hint
st.caption(f"Auto-refresh: every {FLEET_HEALTH_POLL}s")
