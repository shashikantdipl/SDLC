"""Pipeline Runs — Trigger, monitor, and manage pipelines.

Primary personas: Marcus Chen (Delivery Lead), Anika Patel (Eng Lead)
Interactions: I-001 (trigger), I-002 (status), I-003 (list), I-004 (resume), I-005 (cancel)
"""
import streamlit as st
import pandas as pd
from dashboard.components.api_client import api_get, api_post
from dashboard.components.status_badge import status_badge
from dashboard.config import STATUS_COLORS

st.set_page_config(page_title="Pipeline Runs", layout="wide")
st.title("Pipeline Runs")

# --- Trigger Form (I-001) ---
with st.expander("Trigger New Pipeline", expanded=False):
    with st.form("trigger_form"):
        t_project = st.text_input("Project ID", value="default")
        t_pipeline = st.selectbox("Pipeline", ["document-stack", "feature-development", "bug-fix", "hotfix", "security-patch"])
        t_brief = st.text_area("Brief", placeholder="Describe what to build...")
        t_user = st.text_input("Triggered By", value="operator")
        submitted = st.form_submit_button("Trigger Pipeline")
        if submitted:
            if len(t_brief.strip()) < 10:
                st.error("Brief must be at least 10 characters.")
            else:
                result = api_post("/pipelines", {"project_id": t_project, "pipeline_name": t_pipeline, "brief": t_brief, "triggered_by": t_user})
                if result.get("data"):
                    st.success(f"Pipeline triggered! Run ID: {result['data'].get('run_id', 'unknown')}")
                else:
                    st.error(f"Failed to trigger: {result.get('error', {}).get('message', 'Unknown error')}")

st.markdown("---")

# --- Runs Table (I-003) ---
st.subheader("Pipeline History")
project_id = st.text_input("Filter by Project", value="default", key="list_project")
status_filter = st.selectbox("Filter by Status", ["all", "pending", "running", "paused", "completed", "failed", "cancelled"])

params = {"project_id": project_id, "limit": 50}
if status_filter != "all":
    params["status"] = status_filter

runs_data = api_get("/pipelines", params=params)
if runs_data.get("data"):
    runs = runs_data["data"]
    if isinstance(runs, list) and runs:
        df = pd.DataFrame(runs)
        display_cols = ["run_id", "pipeline_name", "status", "current_step", "total_steps", "triggered_by", "cost_usd", "started_at"]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], use_container_width=True, hide_index=True)

        # Run detail
        selected_run = st.text_input("Enter Run ID for details")
        if selected_run:
            detail = api_get(f"/pipelines/{selected_run}")
            if detail.get("data"):
                d = detail["data"]
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("Status", d.get("status", "unknown"))
                with col2: st.metric("Progress", f"{d.get('current_step', 0)}/{d.get('total_steps', 0)}")
                with col3: st.metric("Cost", f"${float(d.get('cost_usd', 0)):.2f}")

                # Resume/Cancel buttons
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if d.get("status") == "paused" and st.button("Resume"):
                        api_post(f"/pipelines/{selected_run}/resume")
                        st.rerun()
                with bcol2:
                    if d.get("status") in ("running", "paused", "pending") and st.button("Cancel"):
                        api_post(f"/pipelines/{selected_run}/cancel")
                        st.rerun()
    else:
        st.info("No pipeline runs found.")
