"""Costs — Budget tracking, provider stats, per-agent costs."""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Costs — Budget Tracking", layout="wide")
st.title("💰 Cost Tracker")

if "project_data" not in st.session_state:
    st.warning("⚠️ No project loaded. Go to 🏠 Home and scan a project first.")
    st.stop()

agents = st.session_state.project_data.get("agents", [])

# --- Budget Overview ---
st.subheader("📊 Budget Overview")

# Estimated costs based on agent tier
tier_costs = {"fast": 0.023, "balanced": 0.130, "powerful": 0.150, "unknown": 0.050}

total_estimated = 0
by_phase = {}
by_tier = {}
by_autonomy = {}

for agent in agents:
    manifest = agent.get("manifest", {})
    tier = manifest.get("tier", "unknown")
    phase = agent["phase"]
    autonomy = manifest.get("autonomy_tier", "T2")

    cost = tier_costs.get(tier, 0.05)
    total_estimated += cost

    by_phase[phase] = by_phase.get(phase, 0) + cost
    by_tier[tier] = by_tier.get(tier, 0) + cost
    by_autonomy[autonomy] = by_autonomy.get(autonomy, 0) + cost

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Est. Cost (1 run each)", f"${total_estimated:.2f}")
with col2:
    st.metric("Pipeline Ceiling", "$45.00")
with col3:
    st.metric("Total Agents", len(agents))
with col4:
    fast_count = sum(1 for a in agents if a.get("manifest", {}).get("tier") == "fast")
    balanced_count = sum(1 for a in agents if a.get("manifest", {}).get("tier") == "balanced")
    st.metric("Fast / Balanced", f"{fast_count} / {balanced_count}")

# --- Cost by Phase ---
st.markdown("---")
st.subheader("💵 Estimated Cost by Phase")

import pandas as pd

phase_data = []
phase_order = ["govern", "design", "build", "test", "deploy", "operate", "oversight"]
for phase in phase_order:
    cost = by_phase.get(phase, 0)
    count = sum(1 for a in agents if a["phase"] == phase)
    phase_data.append({
        "Phase": phase.upper(),
        "Agents": count,
        "Est. Cost": f"${cost:.2f}",
        "Avg/Agent": f"${cost / count:.3f}" if count > 0 else "$0",
    })

st.dataframe(pd.DataFrame(phase_data), use_container_width=True, hide_index=True)

# Bar chart
st.bar_chart(pd.DataFrame({
    "Phase": [p.upper() for p in phase_order],
    "Cost ($)": [by_phase.get(p, 0) for p in phase_order],
}).set_index("Phase"))

# --- Cost by Tier ---
st.markdown("---")
st.subheader("⚡ Cost by Model Tier")

col1, col2, col3 = st.columns(3)
for tier, col in [("fast", col1), ("balanced", col2), ("powerful", col3)]:
    with col:
        count = sum(1 for a in agents if a.get("manifest", {}).get("tier") == tier)
        cost = by_tier.get(tier, 0)
        st.metric(f"{tier.title()} Tier", f"${cost:.2f}", delta=f"{count} agents")

# --- Cost by Autonomy Tier ---
st.markdown("---")
st.subheader("🔐 Agents by Autonomy Tier")

autonomy_data = []
for tier in ["T0", "T1", "T2", "T3"]:
    count = sum(1 for a in agents if a.get("manifest", {}).get("autonomy_tier") == tier)
    desc = {"T0": "Fully autonomous", "T1": "Light oversight", "T2": "Quality gates", "T3": "HITL every step"}.get(tier, "?")
    autonomy_data.append({"Tier": tier, "Description": desc, "Agents": count})

st.dataframe(pd.DataFrame(autonomy_data), use_container_width=True, hide_index=True)

# --- Per-Agent Cost Table ---
st.markdown("---")
st.subheader("🤖 Per-Agent Cost Estimate")

agent_costs = []
for agent in sorted(agents, key=lambda a: (a["phase"], a["id"])):
    manifest = agent.get("manifest", {})
    tier = manifest.get("tier", "unknown")
    cost = tier_costs.get(tier, 0.05)
    agent_costs.append({
        "Agent": agent["id"],
        "Phase": agent["phase"],
        "Tier": tier,
        "Est. Cost": f"${cost:.3f}",
        "Budget Cap": f"${manifest.get('max_budget_usd', 0.50):.2f}",
        "Autonomy": manifest.get("autonomy_tier", "?"),
    })

st.dataframe(pd.DataFrame(agent_costs), use_container_width=True, hide_index=True, height=400)

# --- Provider Distribution ---
st.markdown("---")
st.subheader("🌐 LLM Provider Configuration")

providers = {}
for agent in agents:
    manifest = agent.get("manifest", {})
    provider = manifest.get("provider", "null (env default)")
    if provider is None:
        provider = "null (env default)"
    providers[provider] = providers.get(provider, 0) + 1

for provider, count in providers.items():
    st.markdown(f"**{provider}**: {count} agents")

st.info("💡 Provider 'null' means the agent uses the LLM_PROVIDER environment variable (default: anthropic). This is the LLM-agnostic pattern — change the env var to switch all agents to OpenAI or Ollama.")
