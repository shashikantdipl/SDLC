"""Agentic SDLC Control Panel — Real-time dashboard for the 61-agent platform.

Launch: streamlit run control_panel/app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Agentic SDLC Control Panel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🤖 Agentic SDLC")
st.sidebar.markdown("---")

# Project path from session state
if "project_path" not in st.session_state:
    st.session_state.project_path = ""
if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False
if "pipeline_log" not in st.session_state:
    st.session_state.pipeline_log = []

project_path = st.session_state.get("project_path", "")
if project_path:
    st.sidebar.success(f"📁 {project_path}")
else:
    st.sidebar.warning("No project loaded")

st.sidebar.markdown("---")
st.sidebar.markdown("**Pages**")
st.sidebar.markdown("- 🏠 Home — Load project")
st.sidebar.markdown("- 🤖 Agents — Registry & status")
st.sidebar.markdown("- 🔄 Pipeline — Run & monitor")
st.sidebar.markdown("- 💰 Costs — Budget tracking")

st.sidebar.markdown("---")
st.sidebar.caption("v1.0 | 61 agents | 24-doc pipeline")

# Main page
st.title("🤖 Agentic SDLC Control Panel")
st.markdown("Real-time dashboard for the 61-agent, 24-document Full-Stack-First pipeline.")

st.markdown("---")
st.markdown("### 👈 Select a page from the sidebar to get started")
st.markdown("""
**Pages:**
- **🏠 Home** — Load a project folder or upload files
- **🤖 Agents** — View all 61 agents, their status, manifests, and prompts
- **🔄 Pipeline** — Trigger the 24-step pipeline, monitor progress live
- **💰 Costs** — Track spending per agent, per provider, per pipeline run
""")
