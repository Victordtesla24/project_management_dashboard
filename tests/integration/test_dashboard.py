"""Integration tests for dashboard functionality."""

import pytest
from pathlib import Path

def test_dashboard_config(project_root):
    """Test dashboard configuration loading."""
    config_file = Path(project_root) / "config" / "dashboard.json"
    assert config_file.exists(), "Dashboard config file not found"

@pytest.fixture
def mock_metrics():
    """Fixture for mocked metrics data."""
    return {
        "cpu_usage": 45.2,
        "memory_usage": 68.7,
        "disk_usage": 72.1,
        "network_traffic": {
            "incoming": 1024,
            "outgoing": 2048
        }
    }

@pytest.fixture
def mock_session_state():
    """Fixture for mocked Streamlit session state."""
    class MockState:
        def __init__(self):
            self.metrics_history = []
            self.last_update = None
    return MockState()

def test_update_metrics(mock_metrics, mock_session_state):
    """Test metrics update functionality."""
    from dashboard.main import update_metrics
    
    # Update metrics
    update_metrics(mock_session_state, mock_metrics)
    
    # Verify metrics were stored
    assert len(mock_session_state.metrics_history) == 1
    assert mock_session_state.metrics_history[0] == mock_metrics
    assert mock_session_state.last_update is not None

@pytest.mark.parametrize("mock_go,mock_st", [(None, None)], indirect=True)
def test_display_metrics(mock_make_subplots, mock_go, mock_st, mock_metrics, mock_session_state):
    """Test metrics display functionality."""
    from dashboard.main import display_metrics
    
    # Setup mock data
    mock_session_state.metrics_history = [mock_metrics]
    
    # Display metrics
    display_metrics(mock_session_state)
    
    # Verify display calls
    assert mock_st.plotly_chart.called
    assert mock_make_subplots.called
    assert mock_go.Scatter.called
