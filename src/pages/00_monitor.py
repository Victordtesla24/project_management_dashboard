import streamlit as st
st.set_page_config(layout='wide')

"""System monitoring page."""

import time

import psutil



def get_system_metrics():
    """Get current system metrics."""
    if "error" in st.experimental_get_query_params():
        st.error("Error fetching system metrics")
        return None

    return {"cpu": psutil.cpu_percent(interval=1), "memory": psutil.virtual_memory().percent}


def main():
    """Main function for the monitor page."""
    st.title("System Monitor")

    # Get system metrics
    metrics = get_system_metrics()

    if metrics:
        # Create columns for metrics
        col1, col2 = st.columns(2)

        # Display CPU usage
        with col1:
            st.metric(label="CPU Usage", value=f"{metrics['cpu']}%", delta=None)

        # Display memory usage
        with col2:
            st.metric(label="Memory Usage", value=f"{metrics['memory']}%", delta=None)

        # Auto-refresh every 5 seconds
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    main()
