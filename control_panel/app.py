"""Agentic SDLC Control Panel — Modern dashboard for the 61-agent platform.

Launch: streamlit run control_panel/app.py
"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from control_panel.theme import apply_theme, gradient_header, metric_card

st.set_page_config(
    page_title="Agentic SDLC Control Panel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

# --- Sidebar ---
st.sidebar.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <div style="font-size: 3rem;">🤖</div>
    <h2 style="color: #f1f5f9; margin: 8px 0 4px 0;">Agentic SDLC</h2>
    <p style="color: #64748b; font-size: 0.85rem;">AI-Native App Builder</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

project_path = st.session_state.get("project_path", "")
if project_path:
    st.sidebar.markdown(f"""
    <div style="background: #052e16; border: 1px solid #166534; border-radius: 8px; padding: 10px; margin: 8px 0;">
        <span style="color: #4ade80;">📁 Project loaded</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"""
    <div style="background: #431407; border: 1px solid #9a3412; border-radius: 8px; padding: 10px; margin: 8px 0;">
        <span style="color: #fdba74;">⚠️ No project loaded</span>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="padding: 0 8px;">
    <p style="color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px;">Navigation</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; padding: 8px;">
    <span style="color: #334155; font-size: 0.7rem;">v1.0 | 61 agents | 24-doc pipeline</span>
</div>
""", unsafe_allow_html=True)

# --- Main Page ---
gradient_header("Agentic SDLC", "Build complete apps with 61 AI agents across 7 SDLC phases")

# Session state
if "project_path" not in st.session_state:
    st.session_state.project_path = ""

# Hero section
st.markdown("""
<div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; border-radius: 16px; padding: 40px; margin: 20px 0; text-align: center;">
    <h2 style="color: #f1f5f9; margin-bottom: 16px;">One Brief → 24 Documents → Complete App</h2>
    <p style="color: #94a3b8; font-size: 1.1rem; max-width: 600px; margin: 0 auto 24px;">
        Write a project brief. 22 AI agents generate your complete specification.
        Claude Code writes all the code. You deploy.
    </p>
    <div style="display: flex; justify-content: center; gap: 24px; flex-wrap: wrap;">
        <div style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #3b82f6;">61</div>
            <div style="color: #64748b; font-size: 0.85rem;">AI Agents</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #8b5cf6;">24</div>
            <div style="color: #64748b; font-size: 0.85rem;">Documents</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #ec4899;">7</div>
            <div style="color: #64748b; font-size: 0.85rem;">SDLC Phases</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #4ade80;">$3</div>
            <div style="color: #64748b; font-size: 0.85rem;">Per Pipeline</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Phase cards
st.markdown("### The 7 Phases")

phases = [
    ("🏛️", "GOVERN", "5 agents", "Cost, audit, lifecycle, orchestration", "#3b82f6"),
    ("📐", "DESIGN", "22 agents", "24-doc pipeline: BRD through compliance", "#8b5cf6"),
    ("🔨", "BUILD", "9 agents", "Code review, tests, security, performance", "#4ade80"),
    ("🧪", "TEST", "5 agents", "Static analysis, coverage, integration", "#fbbf24"),
    ("🚀", "DEPLOY", "5 agents", "Checklist, IaC, release notes, rollback", "#f87171"),
    ("⚙️", "OPERATE", "5 agents", "Incidents, runbooks, SLA, alerts", "#2dd4bf"),
    ("🔍", "OVERSIGHT", "10 agents", "Audits, compliance, quality gates", "#fb923c"),
]

cols = st.columns(len(phases))
for i, (icon, name, count, desc, color) in enumerate(phases):
    with cols[i]:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
            <h3 style="color: {color}; font-size: 0.9rem;">{name}</h3>
            <p class="value" style="font-size: 1.3rem;">{count}</p>
            <p class="subtitle" style="font-size: 0.75rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# Quick start
st.markdown("---")
st.markdown("### 🚀 Quick Start")
st.markdown("""
<div style="display: flex; gap: 16px; flex-wrap: wrap;">
    <div class="metric-card" style="flex: 1; min-width: 250px;">
        <h3>Step 1</h3>
        <p class="value" style="font-size: 1.2rem;">📁 Load Project</p>
        <p class="subtitle">Go to Home page and scan your project folder</p>
    </div>
    <div class="metric-card" style="flex: 1; min-width: 250px;">
        <h3>Step 2</h3>
        <p class="value" style="font-size: 1.2rem;">🎯 Open Lifecycle</p>
        <p class="subtitle">See the complete HITL journey and enter your brief</p>
    </div>
    <div class="metric-card" style="flex: 1; min-width: 250px;">
        <h3>Step 3</h3>
        <p class="value" style="font-size: 1.2rem;">🚀 Run Pipeline</p>
        <p class="subtitle">One command generates all 24 documents</p>
    </div>
</div>
""", unsafe_allow_html=True)
