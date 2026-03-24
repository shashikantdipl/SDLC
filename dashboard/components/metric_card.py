"""Metric card component — single number with label and optional delta."""
import streamlit as st


def metric_card(label: str, value: str, delta: str | None = None, delta_color: str = "normal") -> None:
    """Render a metric card using st.metric."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
