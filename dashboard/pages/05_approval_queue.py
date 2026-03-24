"""Approval Queue — Pending approvals with approve/reject.

Primary persona: Anika Patel (Engineering Lead)
Interactions: I-045 (list_pending), I-046 (approve), I-047 (reject)
Cross-interface: Developer triggers via MCP → Anika approves here.
"""
import streamlit as st
import pandas as pd
from dashboard.components.api_client import api_get, api_post
from dashboard.components.status_badge import status_badge

st.set_page_config(page_title="Approval Queue", layout="wide")
st.title("Approval Queue")

# --- Pending Approvals (I-045) ---
project_id = st.text_input("Project ID", value="default")
pending_data = api_get("/approvals", params={"project_id": project_id})

if pending_data.get("data"):
    approvals = pending_data["data"]
    if isinstance(approvals, list) and approvals:
        st.subheader(f"{len(approvals)} Pending Approval(s)")

        for i, approval in enumerate(approvals):
            with st.expander(f"#{i+1} — {approval.get('pipeline_name', 'unknown')} / Step {approval.get('step_name', '?')}", expanded=(i == 0)):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Pipeline:** {approval.get('pipeline_name', 'unknown')}")
                    st.markdown(f"**Step:** {approval.get('step_name', 'unknown')} (#{approval.get('step_number', '?')})")
                with col2:
                    st.markdown(f"**Risk Level:** {approval.get('risk_level', 'unknown')}")
                    st.markdown(f"**Requested:** {approval.get('requested_at', 'unknown')}")
                with col3:
                    st.markdown(f"**Expires:** {approval.get('expires_at', 'unknown')}")
                    st.markdown(f"**Approval ID:** `{approval.get('approval_id', 'unknown')}`")

                st.markdown(f"**Summary:** {approval.get('summary', 'No summary')}")

                # Approve / Reject actions
                approval_id = approval.get("approval_id")
                acol1, acol2 = st.columns(2)
                with acol1:
                    if st.button(f"Approve", key=f"approve_{approval_id}"):
                        result = api_post(f"/approvals/{approval_id}/approve", {"decision_by": "operator"})
                        if result.get("data"):
                            st.success("Approved!")
                            st.rerun()
                        else:
                            st.error(f"Failed: {result.get('error', {}).get('message', 'Unknown')}")
                with acol2:
                    reject_reason = st.text_input("Rejection reason", key=f"reason_{approval_id}")
                    if st.button(f"Reject", key=f"reject_{approval_id}"):
                        if not reject_reason.strip():
                            st.error("Rejection reason is required.")
                        else:
                            result = api_post(f"/approvals/{approval_id}/reject", {"decision_by": "operator", "reason": reject_reason})
                            if result.get("data"):
                                st.warning("Rejected.")
                                st.rerun()
                            else:
                                st.error(f"Failed: {result.get('error', {}).get('message', 'Unknown')}")
    else:
        st.success("No pending approvals. All caught up!")
else:
    st.error("Could not load approval queue.")
