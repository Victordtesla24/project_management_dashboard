"""Unit tests for the dashboard module."""

from datetime import datetime

from dashboard.main import display_metrics, update_metrics


def test_update_metrics(mock_metrics, mock_session_state):
    """Test updating metrics in session state."""
    update_metrics(mock_session_state)
    assert len(mock_session_state.metrics_data) > 0
    assert isinstance(mock_session_state.last_update, datetime)


def test_display_metrics(mock_metrics, mock_session_state):
    """Test metrics display functionality."""
    mock_session_state.metrics_data = mock_metrics
    mock_session_state.last_update = datetime.now()
    metrics = display_metrics(mock_session_state)
    assert len(metrics) == len(mock_metrics)
    assert all("name" in m and "value" in m for m in metrics)
