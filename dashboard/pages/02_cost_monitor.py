"""Cost Monitor — Budget tracking and anomaly detection.

Primary personas: David Okonkwo (DevOps), Fatima Al-Rashidi (Compliance)
Interactions: I-040 (cost_report), I-041 (budget), I-048 (anomalies)
"""
import streamlit as st
import pandas as pd
from dashboard.components.api_client import api_get
from dashboard.components.metric_card import metric_card
from dashboard.config import COST_CHART_DAYS

st.set_page_config(page_title="Cost Monitor", layout="wide")
st.title("Cost Monitor")

# Controls
col1, col2 = st.columns([1, 3])
with col1:
    project_id = st.text_input("Project ID", value="default")
    period = st.selectbox("Period", [7, 14, 30, 90], index=2)

# --- Budget Status (I-041) ---
st.subheader("Budget Status")
bcol1, bcol2, bcol3 = st.columns(3)
for scope, col in [("fleet", bcol1), ("project", bcol2), ("agent", bcol3)]:
    with col:
        budget_data = api_get(f"/budget/{scope}/{project_id}")
        if budget_data.get("data"):
            b = budget_data["data"]
            spent = float(b.get("spent_usd", 0))
            budget = float(b.get("budget_usd", 1))
            remaining = float(b.get("remaining_usd", 0))
            pct = float(b.get("utilization_pct", 0))
            metric_card(f"{scope.title()} Budget", f"${remaining:.2f} left", f"{pct:.0f}% used")
            st.progress(min(pct / 100, 1.0))

st.markdown("---")

# --- Cost Report (I-040) ---
st.subheader("Cost Breakdown")
report_data = api_get("/cost/report", params={"scope": "project", "scope_id": project_id, "period_days": period})
if report_data.get("data"):
    r = report_data["data"]
    metric_card("Total Cost", f"${float(r.get('total_cost_usd', 0)):.2f}")
    breakdown = r.get("breakdown", [])
    if breakdown:
        df = pd.DataFrame(breakdown)
        st.bar_chart(df.set_index("label")["cost_usd"] if "label" in df.columns else df)
else:
    st.info("No cost data available for this period.")

st.markdown("---")

# --- Anomaly Alerts (I-048) ---
st.subheader("Cost Anomalies")
anomaly_data = api_get("/cost/anomalies", params={"project_id": project_id})
if anomaly_data.get("data"):
    anomalies = anomaly_data["data"]
    if isinstance(anomalies, list) and anomalies:
        for a in anomalies:
            st.warning(f"**{a.get('agent_id')}** — Expected ${float(a.get('expected_cost_usd', 0)):.2f}, Actual ${float(a.get('actual_cost_usd', 0)):.2f} ({float(a.get('deviation_pct', 0)):.0f}% deviation)")
    else:
        st.success("No anomalies detected.")
