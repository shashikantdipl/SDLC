"""Home — Load project folder and see overview."""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from control_panel.components.scanner import scan_project

st.set_page_config(page_title="Home — Load Project", layout="wide")
st.title("🏠 Load Project")

# --- Project Loader ---
st.subheader("📁 Project Folder")

default_path = str(Path(__file__).parent.parent.parent)
project_path = st.text_input("Enter project folder path:", value=default_path)

if st.button("🔍 Scan Project", type="primary"):
    with st.spinner("Scanning project folder..."):
        data = scan_project(project_path)
        if "error" in data:
            st.error(data["error"])
        else:
            st.session_state.project_path = project_path
            st.session_state.project_data = data
            st.success(f"✅ Project loaded: {project_path}")

# --- Overview ---
if "project_data" in st.session_state:
    data = st.session_state.project_data

    st.markdown("---")
    st.subheader("📊 Project Overview")

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    agents = data.get("agents", [])
    docs = data.get("documents", [])
    migrations = data.get("migrations", [])
    pipeline = data.get("pipeline_config", {})
    sdk = data.get("sdk", {})

    with col1:
        st.metric("Agents", len(agents))
    with col2:
        st.metric("Documents", len(docs))
    with col3:
        st.metric("Pipeline Steps", len(pipeline.get("steps", [])))
    with col4:
        st.metric("Migrations", len(migrations))
    with col5:
        sdk_count = sum(1 for v in sdk.values() if v)
        st.metric("SDK Modules", f"{sdk_count}/8")

    # Agent breakdown by phase
    st.markdown("---")
    st.subheader("🤖 Agents by Phase")

    phase_counts = {}
    for agent in agents:
        phase = agent["phase"]
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

    phase_order = ["govern", "design", "build", "test", "deploy", "operate", "oversight"]
    cols = st.columns(len(phase_order))
    for i, phase in enumerate(phase_order):
        count = phase_counts.get(phase, 0)
        with cols[i]:
            st.metric(phase.upper(), count)

    # Agent status summary
    st.markdown("---")
    st.subheader("✅ Agent Readiness")

    ready = sum(1 for a in agents if a["status"] == "ready")
    incomplete = sum(1 for a in agents if a["status"] != "ready")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ready", ready, delta=f"{ready}/{len(agents)}")
    with col2:
        if incomplete > 0:
            st.metric("Issues", incomplete, delta=f"-{incomplete}", delta_color="inverse")
        else:
            st.metric("Issues", 0)

    # SDK status
    st.markdown("---")
    st.subheader("🧰 SDK Layer")

    sdk_items = {
        "BaseAgent": sdk.get("base_agent", False),
        "BaseHooks": sdk.get("base_hooks", False),
        "ManifestLoader": sdk.get("manifest_loader", False),
        "LLMProvider": sdk.get("llm_provider", False),
        "Anthropic": sdk.get("anthropic_provider", False),
        "OpenAI": sdk.get("openai_provider", False),
        "Ollama": sdk.get("ollama_provider", False),
        "Factory": sdk.get("factory", False),
    }

    cols = st.columns(4)
    for i, (name, exists) in enumerate(sdk_items.items()):
        with cols[i % 4]:
            st.markdown(f"{'✅' if exists else '❌'} {name}")

    # Documents
    st.markdown("---")
    st.subheader("📄 Generated Documents")

    if docs:
        import pandas as pd
        df = pd.DataFrame([{
            "#": d["number"],
            "Document": d["title"][:50],
            "Lines": d["lines"],
            "Size": f"{d['size_bytes'] / 1024:.1f} KB",
            "Modified": d["modified"][:10],
        } for d in docs])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No generated documents found.")

    # Scan timestamp
    st.caption(f"Last scan: {data.get('scanned_at', 'unknown')}")
