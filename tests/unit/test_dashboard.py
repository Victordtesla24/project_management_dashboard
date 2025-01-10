"""Test dashboard functionality."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture()
def mock_session_state():
    """Create mock session state."""
    return {"metrics_history": [], "last_update": None}


@pytest.fixture()
def mock_metrics():
    """Create mock metrics data."""
    return {
        "system": {"cpu": 50.0, "memory": 60.0, "disk": 70.0},
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": 12345,
    }


def test_update_metrics(mock_metrics, mock_session_state):
    """Test metrics update functionality."""
    from dashboard.main import update_metrics

    # Mock MetricsCollector
    with patch("dashboard.main.MetricsCollector") as MockCollector:
        # Configure mock
        mock_collector = MagicMock()
        mock_collector.get_metrics.return_value = mock_metrics
        MockCollector.return_value = mock_collector

        # Test update
        result = update_metrics(mock_session_state)

        # Verify results
        assert len(mock_session_state["metrics_history"]) == 1
        assert mock_session_state["metrics_history"][0] == mock_metrics
        assert result == mock_metrics
        MockCollector.assert_called_once()
        mock_collector.get_metrics.assert_called_once()


def test_display_metrics(mock_metrics, mock_session_state):
    """Test metrics display functionality."""
    from dashboard.main import display_metrics

    # Setup mock state
    mock_session_state["metrics_history"] = [mock_metrics]

    # Setup streamlit mocks
    with patch("dashboard.main.st") as mock_st:
        # Configure column mocks
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # Configure context manager mocks
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=None)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=None)

        # Test display
        metrics_to_show = ["CPU Usage", "Memory Usage"]
        display_metrics(mock_session_state, metrics_to_show)

        # Verify streamlit calls
        mock_st.columns.assert_called_once_with(2)

        # Verify metric displays
        mock_st.metric.assert_any_call("CPU Usage", "50.0%", delta=None)
        mock_st.metric.assert_any_call("Memory Usage", "60.0%", delta=None)


def test_empty_metrics(mock_session_state):
    """Test handling of empty metrics."""
    from dashboard.main import display_metrics

    # Setup empty state
    mock_session_state["metrics_history"] = []

    # Setup streamlit mock
    with patch("dashboard.main.st") as mock_st:
        # Test display with empty metrics
        metrics_to_show = ["CPU Usage", "Memory Usage"]
        display_metrics(mock_session_state, metrics_to_show)

        # Verify warning displayed
        mock_st.warning.assert_called_once_with("No metrics data available")


def test_invalid_metric_name(mock_metrics, mock_session_state):
    """Test handling of invalid metric names."""
    from dashboard.main import display_metrics

    # Setup state with data
    mock_session_state["metrics_history"] = [mock_metrics]

    # Setup streamlit mock
    with patch("dashboard.main.st") as mock_st:
        # Configure column mocks
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # Configure context manager mocks
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=None)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=None)

        # Test display with invalid metric
        metrics_to_show = ["Invalid Metric"]
        display_metrics(mock_session_state, metrics_to_show)

        # Verify no metrics displayed
        mock_st.metric.assert_not_called()
