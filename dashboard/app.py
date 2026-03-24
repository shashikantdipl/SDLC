"""Agentic SDLC Platform — Operator Dashboard.

5 pages for human operators (Anika, David, Fatima, Jason).
All data from REST API. Never imports services/ or accesses DB directly.
"""
import streamlit as st

st.set_page_config(
    page_title="Agentic SDLC Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Agentic SDLC")
st.sidebar.markdown("---")
st.sidebar.markdown("**Operator Dashboard**")
st.sidebar.markdown("v0.1.0 | Full-Stack-First")

# Main page content
st.title("Agentic SDLC Platform")
st.markdown("Select a page from the sidebar to get started.")
st.markdown("""
### Pages
- **Fleet Health** — Agent status grid, health badges, MCP monitoring
- **Cost Monitor** — Budget burn-down, cost charts, anomaly alerts
- **Pipeline Runs** — Trigger, monitor, resume/cancel pipelines
- **Audit Log** — Searchable audit events, summaries, export
- **Approval Queue** — Pending approvals, approve/reject actions
""")
