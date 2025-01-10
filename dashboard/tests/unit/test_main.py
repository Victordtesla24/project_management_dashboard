from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from dashboard.config import init_config
from dashboard.main import (
    display_metrics,
    initialize_session_state,
    main,
    setup_page,
    setup_sidebar,
    update_metrics,
)


@pytest.fixture(autouse=True)
def setup_config(config_file):
"""\1"""
init_config(config_file)

@pytest.fixture
def mock_streamlit():
"""\1"""
with patch("dashboard.main.st") as mock_st:
# Create a proper session state dict
session_state = {}
mock_st.session_state = session_state

# Mock the plotly chart function
mock_st.plotly_chart = MagicMock()

# Mock columns
col1, col2 = MagicMock(), MagicMock()
mock_st.columns.return_value = [col1, col2]

# Mock metric display
col1.metric = MagicMock()
col2.metric = MagicMock()

return mock_st

@pytest.fixture
def mock_metrics():
"""\1"""
return {
"metrics": {
"cpu": {"percent": 45.5, "count": 8, "frequency": 2.5},
"memory": {"percent": 60.2, "total": 16000000000, "used": 9632000000},
"disk": {"percent": 75.8, "total": 500000000000, "used": 379000000000},
    },
"timestamp": datetime.now().isoformat(),
"uptime": 3600,
    }

def test_initialize_session_state(mock_streamlit):
"""\1"""
initialize_session_state(mock_streamlit.session_state)
assert "metrics_history" in mock_streamlit.session_state
assert isinstance(mock_streamlit.session_state["metrics_history"], list)
assert len(mock_streamlit.session_state["metrics_history"]) == 0

def test_setup_page(mock_streamlit):
"""\1"""
setup_page()
mock_streamlit.set_page_config.assert_called_once_with(
page_title="Project Management Dashboard",
page_icon="📊",
layout="wide",
initial_sidebar_state="expanded",
    )

def test_setup_sidebar(mock_streamlit):
"""\1"""
with patch("dashboard.main.st.sidebar") as mock_sidebar:
mock_sidebar.slider.return_value = 5
mock_sidebar.multiselect.return_value = ["CPU Usage", "Memory Usage"]

update_interval, metrics_to_show = setup_sidebar()

assert update_interval == 5
assert metrics_to_show == ["CPU Usage", "Memory Usage"]
mock_sidebar.title.assert_called_with("Dashboard Controls")

def test_update_metrics(mock_streamlit, mock_metrics):
"""\1"""
with patch("dashboard.main.collect_system_metrics", return_value=mock_metrics):
# Initialize session state
initialize_session_state(mock_streamlit.session_state)

# Update metrics multiple times
for _ in range(60):
current_metrics = update_metrics(mock_streamlit.session_state)

# Verify metrics were updated
assert len(mock_streamlit.session_state["metrics_history"]) == 50  # Max limit
assert current_metrics == mock_metrics

# Verify metrics structure
latest_metrics = mock_streamlit.session_state["metrics_history"][-1]
assert "metrics" in latest_metrics
assert "cpu" in latest_metrics["metrics"]
assert "memory" in latest_metrics["metrics"]
assert "disk" in latest_metrics["metrics"]

def test_display_metrics(mock_streamlit, mock_metrics):
"""\1"""
# Initialize session state with some data
initialize_session_state(mock_streamlit.session_state)
mock_streamlit.session_state["metrics_history"].append(mock_metrics)

metrics_to_show = ["CPU Usage", "Memory Usage"]
display_metrics(mock_streamlit.session_state, metrics_to_show)

# Verify visualizations were created
assert mock_streamlit.plotly_chart.called
assert mock_streamlit.metric.called

# Verify metric values
metric_calls = mock_streamlit.metric.call_args_list
assert len(metric_calls) >= 2  # At least CPU and Memory metrics

# Verify specific metric calls
metrics_called = [call[0][0] for call in metric_calls]  # Get the metric names
assert "CPU Usage" in metrics_called
assert "Memory Usage" in metrics_called

def test_main_function(mock_streamlit, mock_metrics):
"""\1"""
with patch("dashboard.main.collect_system_metrics", return_value=mock_metrics), patch(
"dashboard.main.time.sleep", side_effect=InterruptedError,
    ):  # Break infinite loop
# Mock sidebar controls
mock_streamlit.sidebar.slider.return_value = 1
mock_streamlit.sidebar.multiselect.return_value = ["CPU Usage"]

try:
main()
except InterruptedError:

# Verify initialization
assert mock_streamlit.set_page_config.called
assert "metrics_history" in mock_streamlit.session_state

# Verify metrics collection and display
assert len(mock_streamlit.session_state.metrics_history) > 0
assert mock_streamlit.plotly_chart.called
assert mock_streamlit.metric.called

def test_error_handling(mock_streamlit):
"""\1"""
def mock_error_metrics():
raise Exception("Metrics collection failed")

with patch("dashboard.main.collect_system_metrics", side_effect=mock_error_metrics), patch(
"dashboard.main.st.error",
    ) as mock_error:
# Initialize session state
initialize_session_state(mock_streamlit.session_state)

try:
update_metrics(mock_streamlit.session_state)
except Exception:

# Verify error handling
mock_error.assert_called_with("Error collecting metrics: Metrics collection failed")

def test_dataframe_conversion(mock_streamlit, mock_metrics):
"""\1"""
# Initialize session state with test data
initialize_session_state(mock_streamlit.session_state)
mock_streamlit.session_state.metrics_history.append(mock_metrics)

metrics_to_show = ["CPU Usage"]
display_metrics(mock_streamlit.session_state, metrics_to_show)

# Verify that metric was displayed
mock_streamlit.columns.assert_called_once()
mock_streamlit.columns.return_value[0].metric.assert_called_once_with(
"CPU Usage", "50.0%", delta=None,
    )

# Verify that plotly chart was created
mock_streamlit.plotly_chart.assert_called_once()
