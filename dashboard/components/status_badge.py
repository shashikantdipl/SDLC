"""Status badge component — colored indicator for agent/pipeline status."""
import streamlit as st
from dashboard.config import STATUS_COLORS


def status_badge(status: str, label: str | None = None) -> None:
    """Render a colored status badge."""
    color = STATUS_COLORS.get(status, "#6B7280")
    display = label or status.capitalize()
    st.markdown(
        f'<span style="background-color:{color};color:white;padding:2px 8px;'
        f'border-radius:4px;font-size:0.85em;font-weight:600;">{display}</span>',
        unsafe_allow_html=True,
    )
