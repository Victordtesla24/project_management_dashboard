"""Integration tests for dashboard functionality."""

from pathlib import Path
from typing import Any, Optional
from unittest.mock import patch

import pytest


def test_dashboard_config(project_root):
    """Test dashboard configuration loading."""
    config_file = Path(project_root) / "config" / "dashboard.json"
    assert config_file.exists(), "Dashboard config file not found"


@pytest.fixture()
def mock_metrics():
    """Fixture for mocked metrics data."""
    return {
        "system": {"cpu": 45.2, "memory": 68.7, "disk": 72.1},
        "network": {"incoming": 1024, "outgoing": 2048},
    }


@pytest.fixture()
def mock_session_state():
    """Fixture for mocked Streamlit session state."""

    class MockState:
        def __init__(self) -> None:
            self.metrics_history: list[dict] = []
            self.last_update: Optional[float] = None

        def get(self, key: str, default: Any = None) -> Any:
            """Get value from state."""
            return getattr(self, key, default)

        def __getitem__(self, key: str) -> Any:
            """Get item by key."""
            return getattr(self, key)

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


@pytest.mark.parametrize(("mock_go", "mock_st"), [(None, None)], indirect=True)
def test_display_metrics(mock_make_subplots, mock_go, mock_st, mock_metrics, mock_session_state):
    """Test metrics display functionality."""
    from dashboard.main import display_metrics

    # Setup mock data
    mock_session_state.metrics_history = [mock_metrics]

    # Mock plotly imports
    with patch("dashboard.main.make_subplots", mock_make_subplots), patch(
        "dashboard.main.go",
        mock_go,
    ):
        # Display metrics
        metrics_to_show = ["CPU Usage", "Memory Usage", "Disk Usage"]
        display_metrics(mock_session_state, metrics_to_show)

        # Verify display calls
        assert mock_st.plotly_chart.called
        assert mock_make_subplots.called
        assert mock_go.Scatter.called
