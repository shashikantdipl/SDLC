"""Pipeline — Trigger, monitor, and view generated documents."""
import streamlit as st
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Pipeline — Run & Monitor", layout="wide")
st.title("🔄 Pipeline Monitor")

if "project_data" not in st.session_state:
    st.warning("⚠️ No project loaded. Go to 🏠 Home and scan a project first.")
    st.stop()

data = st.session_state.project_data
pipeline = data.get("pipeline_config", {})
agents = data.get("agents", [])
docs = data.get("documents", [])

# --- Pipeline Config ---
st.subheader("⚙️ Pipeline Configuration")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Steps", len(pipeline.get("steps", [])))
with col2:
    st.metric("Cost Ceiling", f"${pipeline.get('cost_ceiling_usd', 45):.2f}")
with col3:
    parallel = pipeline.get("parallel_groups", [])
    st.metric("Parallel Groups", len(parallel))

# --- Pipeline Steps Visualization ---
st.markdown("---")
st.subheader("📋 Pipeline Steps")

steps = pipeline.get("steps", [])
if steps:
    # Map steps to agents
    agent_map = {a["id"]: a for a in agents}

    for i, step_name in enumerate(steps):
        # Find matching agent
        agent = None
        for a in agents:
            if a["id"].lower().replace("-", "") in step_name.lower().replace("-", ""):
                agent = a
                break

        # Check if document exists for this step
        doc_exists = any(d["number"] == i for d in docs)

        # Status
        if doc_exists:
            icon = "✅"
            status = "Document generated"
        elif agent and agent["status"] == "ready":
            icon = "⚪"
            status = "Agent ready, not run"
        else:
            icon = "🔴"
            status = "Agent not ready"

        tier = agent["manifest"].get("tier", "?") if agent and agent.get("manifest") else "?"

        col1, col2, col3, col4 = st.columns([0.5, 3, 1.5, 1])
        with col1:
            st.markdown(f"**{i}**")
        with col2:
            st.markdown(f"{icon} `{step_name}`")
        with col3:
            st.markdown(f"{status}")
        with col4:
            st.markdown(f"`{tier}`")
else:
    st.info("No pipeline steps configured.")

# --- Trigger Pipeline ---
st.markdown("---")
st.subheader("🚀 Trigger Pipeline")

with st.form("trigger_form"):
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Project Name", value="my-project")
        provider = st.selectbox("LLM Provider", ["anthropic", "openai", "ollama"])
    with col2:
        brief = st.text_area("Project Brief", placeholder="Describe what to build...", height=100)
        tier_override = st.selectbox("Tier Override", ["Use manifest defaults", "fast", "balanced", "powerful"])

    submitted = st.form_submit_button("🚀 Trigger Pipeline", type="primary")

    if submitted:
        if len(brief.strip()) < 10:
            st.error("Brief must be at least 10 characters.")
        else:
            st.session_state.pipeline_running = True
            st.session_state.pipeline_log = [{
                "timestamp": datetime.now().isoformat(),
                "step": 0,
                "agent": "system",
                "action": "Pipeline triggered",
                "status": "started",
                "detail": f"Project: {project_name}, Provider: {provider}, Brief: {brief[:50]}...",
            }]
            st.success(f"✅ Pipeline triggered for '{project_name}' on {provider}")
            st.info("💡 In production, this would invoke G4-team-orchestrator to run the 24-step pipeline. Currently shows the execution plan.")

# --- Live Pipeline Log ---
if st.session_state.get("pipeline_log"):
    st.markdown("---")
    st.subheader("📜 Pipeline Log")
    for entry in reversed(st.session_state.pipeline_log):
        icon = {"started": "🔄", "completed": "✅", "failed": "❌", "running": "🟢"}.get(entry.get("status"), "⚪")
        st.markdown(f"{icon} `{entry['timestamp'][:19]}` — **Step {entry['step']}** ({entry['agent']}) — {entry['action']}")

# --- Generated Documents Viewer ---
st.markdown("---")
st.subheader("📄 Generated Documents")

if docs:
    doc_names = [f"{d['number']:02d} — {d['title'][:50]}" for d in docs]
    selected_doc = st.selectbox("Select a document to view", doc_names)

    if selected_doc:
        doc_idx = doc_names.index(selected_doc)
        doc = docs[doc_idx]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lines", doc["lines"])
        with col2:
            st.metric("Size", f"{doc['size_bytes'] / 1024:.1f} KB")
        with col3:
            st.metric("Modified", doc["modified"][:10])

        # Read and display document
        try:
            content = Path(doc["path"]).read_text(encoding="utf-8", errors="replace")
            with st.expander("📖 View Document Content", expanded=False):
                st.markdown(content[:5000])
                if len(content) > 5000:
                    st.caption(f"... showing first 5000 of {len(content)} characters")
        except Exception as e:
            st.error(f"Could not read document: {e}")
else:
    st.info("No generated documents found. Trigger the pipeline to generate them.")

# Auto-refresh
if st.session_state.get("pipeline_running"):
    st.caption("🔄 Auto-refreshing every 10 seconds...")
    time.sleep(0.1)  # Don't actually block — Streamlit handles rerun
