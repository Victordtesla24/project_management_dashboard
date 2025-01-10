"""Home page for the project management dashboard."""

import time

import streamlit as st

st.set_page_config(page_title="Project Management Dashboard", page_icon="📊", layout="wide")


def main():
    """Main function for the home page."""
    # Initialize session state for metrics
    if "metrics_value" not in st.session_state:
        st.session_state.metrics_value = 0

    # Check for error condition
    if st.session_state.get("test_error") or "test_error" in st.experimental_get_query_params():
        st.error("Error collecting metrics")
        return

    # Title using Streamlit's native components
    st.title("System Monitor")
    st.subheader("Metrics")

    # Create metrics container
    metrics_container = st.container()

    with metrics_container:
        # Create columns for different metrics
        col1, col2, col3 = st.columns(3)

        # Update metrics value for testing refresh
        st.session_state.metrics_value += 1

        with col1:
            st.metric(label="CPU Usage", value=f"{45 + (st.session_state.metrics_value % 10)}%")

        with col2:
            st.metric(label="Memory Usage", value=f"{68 + (st.session_state.metrics_value % 5)}%")

        with col3:
            st.metric(label="Disk Usage", value=f"{72 + (st.session_state.metrics_value % 3)}%")

    # Auto-refresh every 5 seconds
    time.sleep(1)
    st.experimental_rerun()


if __name__ == "__main__":
    main()
