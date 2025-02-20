"""Main entry point for the dashboard application."""
import logging
import os
import time
from typing import Any, Optional, Tuple

import plotly.graph_objects as go  # type: ignore
import streamlit as st
from plotly.subplots import make_subplots  # type: ignore

from .metrics import MetricsCollector

logger = logging.getLogger(__name__)


def load_config() -> Tuple[int, list[str]]:
    """Load dashboard configuration.

    Returns
    -------
        Tuple containing update interval and list of metrics to show.
    """
    try:
        update_interval = int(os.getenv("UPDATE_INTERVAL", "5"))
        metrics_to_show = os.getenv("METRICS_TO_SHOW", "CPU Usage,Memory Usage,Disk Usage").split(
            ",",
        )
        return update_interval, metrics_to_show
    except ValueError as e:
        logger.error(f"Error loading config: {e}")
        return 5, ["CPU Usage", "Memory Usage", "Disk Usage"]


def setup_page() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Project Management Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def update_metrics(session_state: Any, metrics: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Update metrics in session state.

    Args:
    ----
        session_state: Streamlit session state.
        metrics: Optional metrics data to use instead of collecting new metrics.

    Returns:
    -------
        Dictionary containing processed metrics.
    """
    if metrics is None:
        collector = MetricsCollector()
        metrics = collector.get_metrics()

    # Add to history, maintaining max size of 50
    try:
        metrics_history = getattr(session_state, "metrics_history", [])
    except AttributeError:
        metrics_history = session_state.get("metrics_history", [])

    metrics_history.append(metrics)
    if len(metrics_history) > 50:
        metrics_history.pop(0)

    if isinstance(session_state, dict):
        session_state["metrics_history"] = metrics_history
        session_state["last_update"] = time.time()
    else:
        session_state.metrics_history = metrics_history
        session_state.last_update = time.time()

    return metrics


def display_metrics(session_state: Any, metrics_to_show: list[str]) -> None:
    """Display metrics visualization.

    Args:
    ----
        session_state: Streamlit session state.
        metrics_to_show: List of metrics to display.
    """
    if not session_state.get("metrics_history"):
        st.warning("No metrics data available")
        return

    # Get latest metrics
    latest_metrics = session_state["metrics_history"][-1]

    # Create metrics display
    col1, col2 = st.columns(2)

    with col1:
        if "CPU Usage" in metrics_to_show:
            st.metric("CPU Usage", f"{latest_metrics['system']['cpu']:.1f}%", delta=None)

        if "Memory Usage" in metrics_to_show:
            st.metric("Memory Usage", f"{latest_metrics['system']['memory']:.1f}%", delta=None)

    with col2:
        if "Disk Usage" in metrics_to_show:
            st.metric("Disk Usage", f"{latest_metrics['system']['disk']:.1f}%", delta=None)

    # Create time series plot
    fig = make_subplots(rows=1, cols=1)
    metrics_history = session_state["metrics_history"]
    timestamps = list(range(len(metrics_history)))

    for metric in metrics_to_show:
        if metric == "CPU Usage":
            values = [m["system"]["cpu"] for m in metrics_history]
            fig.add_trace(go.Scatter(x=timestamps, y=values, name="CPU Usage"), row=1, col=1)
        elif metric == "Memory Usage":
            values = [m["system"]["memory"] for m in metrics_history]
            fig.add_trace(go.Scatter(x=timestamps, y=values, name="Memory Usage"), row=1, col=1)
        elif metric == "Disk Usage":
            values = [m["system"]["disk"] for m in metrics_history]
            fig.add_trace(go.Scatter(x=timestamps, y=values, name="Disk Usage"), row=1, col=1)

    fig.update_layout(title="System Metrics Over Time", height=400)
    st.plotly_chart(fig)


def main() -> None:
    """Main entry point for the dashboard application."""
    setup_page()
    update_interval, metrics_to_show = load_config()

    # Initialize session state
    if "metrics_history" not in st.session_state:
        st.session_state["metrics_history"] = []

    # Update and display metrics
    update_metrics(st.session_state)
    display_metrics(st.session_state, metrics_to_show)


if __name__ == "__main__":
    main()
