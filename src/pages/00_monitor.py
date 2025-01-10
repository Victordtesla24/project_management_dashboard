import streamlit as st
st.set_page_config(layout='wide')

"""System monitoring page."""

import time

import psutil



def get_system_metrics():
    """Get current system metrics."""
    if "error" in st.experimental_get_query_params():
        st.markdown('<div data-testid="error-message">', unsafe_allow_html=True)
        st.error("Error fetching system metrics")
        st.markdown('</div>', unsafe_allow_html=True)
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
            st.markdown('<div class="metric-container" data-testid="cpu-metric">', unsafe_allow_html=True)
            st.metric(label="CPU Usage", value=f"{metrics['cpu']}%", delta=None)
            st.markdown('</div>', unsafe_allow_html=True)

        # Display memory usage
        with col2:
            st.markdown('<div class="metric-container" data-testid="memory-metric">', unsafe_allow_html=True)
            st.metric(label="Memory Usage", value=f"{metrics['memory']}%", delta=None)
            st.markdown('</div>', unsafe_allow_html=True)

        # Add custom CSS
        st.markdown("""
            <style>
            .metric-container {
                padding: 1rem;
                border-radius: 0.5rem;
                background: rgba(255, 255, 255, 0.05);
            }
            </style>
        """, unsafe_allow_html=True)

        # Auto-refresh every 5 seconds
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    main()
