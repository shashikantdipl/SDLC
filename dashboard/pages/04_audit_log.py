"""Audit Log — Searchable audit events with export.

Primary persona: Fatima Al-Rashidi (Compliance)
Interactions: I-042 (query), I-043 (summary), I-044 (export)
"""
import streamlit as st
import pandas as pd
from dashboard.components.api_client import api_get
from dashboard.components.metric_card import metric_card
from dashboard.config import SEVERITY_COLORS

st.set_page_config(page_title="Audit Log", layout="wide")
st.title("Audit Log")

# --- Summary (I-043) ---
project_id = st.text_input("Project ID", value="default")
period = st.selectbox("Period (days)", [1, 7, 14, 30], index=1)

summary_data = api_get("/audit/summary", params={"project_id": project_id, "period_days": period})
if summary_data.get("data"):
    s = summary_data["data"]
    col1, col2, col3, col4 = st.columns(4)
    with col1: metric_card("Total Events", str(s.get("total_events", 0)))
    with col2: metric_card("Errors", str(s.get("by_severity", {}).get("error", 0)))
    with col3: metric_card("Criticals", str(s.get("by_severity", {}).get("critical", 0)))
    with col4: metric_card("Total Cost", f"${float(s.get('total_cost_usd', 0)):.2f}")

st.markdown("---")

# --- Event Table (I-042) ---
st.subheader("Events")
severity_filter = st.selectbox("Filter by Severity", ["all", "info", "warning", "error", "critical"])
params = {"project_id": project_id, "limit": 100}
if severity_filter != "all":
    params["severity"] = severity_filter

events_data = api_get("/audit/events", params=params)
if events_data.get("data"):
    events = events_data["data"]
    if isinstance(events, list) and events:
        df = pd.DataFrame(events)
        display_cols = ["created_at", "severity", "agent_id", "action", "message", "cost_usd"]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], use_container_width=True, hide_index=True)
    else:
        st.info("No audit events found.")

# --- Export (I-044) ---
st.markdown("---")
if st.button("Export Audit Report"):
    export = api_get("/audit/export", params={"project_id": project_id, "period_days": period})
    if export.get("data"):
        st.download_button("Download JSON", data=str(export["data"]), file_name="audit_report.json", mime="application/json")
