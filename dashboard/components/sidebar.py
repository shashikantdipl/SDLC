"""Sidebar component — navigation and fleet summary."""
import streamlit as st
from dashboard.components.api_client import api_get


def render_sidebar() -> None:
    """Render sidebar with fleet health summary."""
    st.sidebar.title("Agentic SDLC")
    st.sidebar.markdown("---")

    # Fleet health summary
    result = api_get("/system/health")
    if result.get("data"):
        data = result["data"]
        st.sidebar.metric("Agents", f"{data.get('healthy', 0)}/{data.get('total_agents', 0)} healthy")
        st.sidebar.metric("Fleet Cost Today", f"${data.get('fleet_cost_today_usd', 0):.2f}")
    else:
        st.sidebar.warning("API unavailable")

    st.sidebar.markdown("---")
    st.sidebar.caption("v0.1.0 | Full-Stack-First")
