"""Home — Load project folder and see overview with modern theme."""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from control_panel.components.scanner import scan_project
from control_panel.theme import apply_theme, gradient_header, metric_card, progress_bar

st.set_page_config(page_title="Home — Load Project", layout="wide")
apply_theme()

gradient_header("Load Project", "Scan your project folder to discover agents, documents, and pipeline status")

# --- Project Loader ---
default_path = str(Path(__file__).parent.parent.parent)
project_path = st.text_input("Enter project folder path:", value=default_path, label_visibility="collapsed")

if st.button("🔍 Scan Project", type="primary", use_container_width=True):
    with st.spinner("Scanning project folder..."):
        data = scan_project(project_path)
        if "error" in data:
            st.error(data["error"])
        else:
            st.session_state.project_path = project_path
            st.session_state.project_data = data
            st.success("✅ Project loaded successfully!")

if "project_data" in st.session_state:
    data = st.session_state.project_data
    agents = data.get("agents", [])
    docs = data.get("documents", [])
    migrations = data.get("migrations", [])
    pipeline = data.get("pipeline_config", {})
    sdk = data.get("sdk", {})

    st.markdown("---")

    # Metrics
    cols = st.columns(5)
    metrics = [
        ("Total Agents", str(len(agents)), "Across 7 phases"),
        ("Documents", str(len(docs)), "24-doc stack"),
        ("Pipeline Steps", str(len(pipeline.get("steps", []))), "Sequential + parallel"),
        ("Migrations", str(len(migrations)), "PostgreSQL DDL"),
        ("SDK Modules", f"{sum(1 for v in sdk.values() if v)}/8", "LLM-agnostic"),
    ]
    for i, (title, value, sub) in enumerate(metrics):
        with cols[i]:
            st.markdown(metric_card(title, value, sub), unsafe_allow_html=True)

    # Phase breakdown
    st.markdown("---")
    phase_order = ["govern", "design", "build", "test", "deploy", "operate", "oversight"]
    phase_colors = {"govern": "#3b82f6", "design": "#8b5cf6", "build": "#4ade80", "test": "#fbbf24", "deploy": "#f87171", "operate": "#2dd4bf", "oversight": "#fb923c"}

    cols = st.columns(len(phase_order))
    for i, phase in enumerate(phase_order):
        phase_agents = [a for a in agents if a["phase"] == phase]
        ready = sum(1 for a in phase_agents if a["status"] == "ready")
        total = len(phase_agents)
        pct = (ready / total * 100) if total > 0 else 0
        color = phase_colors.get(phase, "#64748b")
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h3 style="color: {color};">{phase.upper()}</h3>
                <p class="value">{ready}/{total}</p>
            </div>
            """, unsafe_allow_html=True)
            progress_bar(pct, "Ready")

    # Overall readiness
    total_agents = len(agents)
    ready_agents = sum(1 for a in agents if a["status"] == "ready")
    readiness_pct = (ready_agents / total_agents * 100) if total_agents > 0 else 0

    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; border-radius: 16px; padding: 30px; text-align: center;">
        <h3 style="color: #94a3b8; margin-bottom: 8px;">Overall Platform Readiness</h3>
        <div style="font-size: 3rem; font-weight: 800; color: {'#4ade80' if readiness_pct >= 90 else '#fbbf24'};">{readiness_pct:.0f}%</div>
        <p style="color: #64748b;">{ready_agents} of {total_agents} agents ready</p>
    </div>
    """, unsafe_allow_html=True)

    # SDK
    st.markdown("---")
    gradient_header("SDK Layer", "")
    sdk_items = [
        ("BaseAgent", sdk.get("base_agent", False)),
        ("BaseHooks", sdk.get("base_hooks", False)),
        ("ManifestLoader", sdk.get("manifest_loader", False)),
        ("LLMProvider", sdk.get("llm_provider", False)),
        ("Anthropic", sdk.get("anthropic_provider", False)),
        ("OpenAI", sdk.get("openai_provider", False)),
        ("Ollama", sdk.get("ollama_provider", False)),
        ("Factory", sdk.get("factory", False)),
    ]
    cols = st.columns(4)
    for i, (name, exists) in enumerate(sdk_items):
        with cols[i % 4]:
            st.markdown(f"{'✅' if exists else '❌'} **{name}**")

    # Docs
    st.markdown("---")
    gradient_header("Generated Documents", "")
    if docs:
        import pandas as pd
        df = pd.DataFrame([{
            "#": f"{d['number']:02d}", "Document": d["title"][:50],
            "Lines": d["lines"], "Size": f"{d['size_bytes']/1024:.1f} KB",
        } for d in docs])
        st.dataframe(df, use_container_width=True, hide_index=True, height=400)

    st.caption(f"Last scan: {data.get('scanned_at', 'unknown')[:19]}")
