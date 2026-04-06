"""Agents — Registry, status, manifests, prompts for all 61 agents."""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Agents — Registry", layout="wide")
st.title("🤖 Agent Registry")

if "project_data" not in st.session_state:
    st.warning("⚠️ No project loaded. Go to 🏠 Home and scan a project first.")
    st.stop()

agents = st.session_state.project_data.get("agents", [])
if not agents:
    st.info("No agents found in the project.")
    st.stop()

# --- Filters ---
col1, col2, col3 = st.columns(3)
with col1:
    phases = ["all"] + sorted(set(a["phase"] for a in agents))
    phase_filter = st.selectbox("Filter by Phase", phases)
with col2:
    tiers = ["all"] + sorted(set(a["manifest"].get("tier", "unknown") for a in agents if a["manifest"]))
    tier_filter = st.selectbox("Filter by Tier", tiers)
with col3:
    statuses = ["all"] + sorted(set(a["status"] for a in agents))
    status_filter = st.selectbox("Filter by Status", statuses)

# Apply filters
filtered = agents
if phase_filter != "all":
    filtered = [a for a in filtered if a["phase"] == phase_filter]
if tier_filter != "all":
    filtered = [a for a in filtered if a["manifest"].get("tier") == tier_filter]
if status_filter != "all":
    filtered = [a for a in filtered if a["status"] == status_filter]

st.markdown(f"**Showing {len(filtered)} of {len(agents)} agents**")
st.markdown("---")

# --- Agent Grid ---
for agent in filtered:
    manifest = agent.get("manifest", {})
    status_icon = {"ready": "🟢", "no_prompt": "🟡", "incomplete": "🔴", "manifest_error": "❌"}.get(agent["status"], "⚪")
    tier_badge = {"fast": "⚡", "balanced": "⚖️", "powerful": "🧠"}.get(manifest.get("tier", ""), "❓")
    autonomy = manifest.get("autonomy_tier", "?")

    with st.expander(f"{status_icon} **{agent['id']}** — {manifest.get('name', agent['id'])} | {tier_badge} {manifest.get('tier', '?')} | T{autonomy[-1] if autonomy else '?'} | ${manifest.get('max_budget_usd', 0):.2f}/call"):

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(f"**Description:** {manifest.get('description', 'No description')[:200]}")
            st.markdown(f"**Phase:** `{agent['phase']}` | **Extends:** `{manifest.get('extends', '?')}` | **Version:** `{manifest.get('version', '?')}`")
            if manifest.get("tags"):
                st.markdown(f"**Tags:** {', '.join(f'`{t}`' for t in manifest['tags'][:8])}")

        with col2:
            st.markdown("**Files:**")
            st.markdown(f"{'✅' if agent['has_manifest'] else '❌'} manifest.yaml")
            st.markdown(f"{'✅' if agent['has_prompt'] else '❌'} prompt.md ({agent['prompt_length']} chars)")
            st.markdown(f"{'✅' if agent['has_tests'] else '⚪'} tests/")

        with col3:
            st.markdown("**Config:**")
            st.markdown(f"Tier: `{manifest.get('tier', '?')}`")
            st.markdown(f"Temp: `{manifest.get('temperature', '?')}`")
            st.markdown(f"Tokens: `{manifest.get('max_tokens', '?')}`")
            st.markdown(f"Autonomy: `{autonomy}`")

        # Prompt preview
        if agent.get("prompt_preview"):
            st.markdown("**Prompt Preview:**")
            st.code(agent["prompt_preview"], language="markdown")

# --- Summary Stats ---
st.markdown("---")
st.subheader("📊 Summary")

import pandas as pd

summary_data = []
for phase in ["govern", "design", "build", "test", "deploy", "operate", "oversight"]:
    phase_agents = [a for a in agents if a["phase"] == phase]
    ready = sum(1 for a in phase_agents if a["status"] == "ready")
    summary_data.append({
        "Phase": phase.upper(),
        "Total": len(phase_agents),
        "Ready": ready,
        "Status": "✅" if ready == len(phase_agents) else f"⚠️ {len(phase_agents) - ready} issues",
    })

st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
