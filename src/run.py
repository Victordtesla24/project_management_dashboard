"""Main application runner module."""

from pathlib import Path
from typing import Dict

import streamlit as st


def initialize_app() -> None:
    """Initialize the Streamlit application."""
    st.set_page_config(
        page_title="Project Management Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def load_config() -> Dict:
    """Load application configuration."""
    config_path = Path(__file__).parent.parent / "config" / "dashboard.json"
    if not config_path.exists():
        st.error("Configuration file not found!")
        return {}

    try:
        return st.secrets.load_secrets(str(config_path))
    except Exception as e:
        st.error(f"Error loading configuration: {e!s}")
        return {}


def main() -> None:
    """Main application entry point."""
    # Initialize application
    initialize_app()

    # Load configuration
    load_config()

    # Display header
    st.title("Project Management Dashboard")

    # Initialize session state if needed
    if "metrics_history" not in st.session_state:
        st.session_state.metrics_history = []

    # Main content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("System Metrics")
        from src.metrics.collector import collector

        metrics = collector.collect_all_metrics()
        if metrics:
            st.json(metrics)

    with col2:
        st.subheader("Application Status")
        st.write("Status: Active")
        st.write("Last Update:", st.session_state.get("last_update", "Never"))


if __name__ == "__main__":
    main()
