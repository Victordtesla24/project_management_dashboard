import streamlit as st

# Set page config
st.set_page_config(
    page_title="Project Management Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Sidebar
with st.sidebar:
    st.title("Dashboard Controls")
    theme = st.selectbox("Theme", ["light", "dark"])
    time_range = st.selectbox("Time Range", ["Last Hour", "Last Day", "Last Week"])
    metrics = st.multiselect("Metrics", ["CPU Usage", "Memory Usage", "Test Coverage"])

# Main content
st.title("Project Management Dashboard")
col1, col2 = st.columns(2)

with col1:
    st.subheader("System Metrics")
    # System metrics charts will be added here

with col2:
    st.subheader("Project Metrics")
    # Project metrics charts will be added here
