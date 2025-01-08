"""Unit tests for the dashboard module."""

from datetime import datetime
from unittest.mock import patch, MagicMock

from dashboard.main import display_metrics, update_metrics


def test_update_metrics(mock_metrics, mock_session_state):
    """Test updating metrics in session state."""
    with patch('dashboard.main.collect_system_metrics') as mock_collect:
        with patch('dashboard.main.process_metrics') as mock_process:
            mock_collect.return_value = {
                'cpu': {'percent': 50.0, 'count': 8, 'frequency': 2.4},
                'memory': {'percent': 60.0, 'total': 16000, 'used': 9600},
                'disk': {'percent': 70.0, 'total': 500000, 'used': 350000}
            }
            mock_process.return_value = {
                'metrics': mock_collect.return_value,
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': 12345
            }
            
            update_metrics(mock_session_state)
            
            assert len(mock_session_state.metrics_history) > 0
            assert isinstance(mock_session_state.last_update, datetime)
            mock_collect.assert_called_once()
            mock_process.assert_called_once()


@patch('dashboard.main.st')
@patch('plotly.graph_objects')
@patch('plotly.subplots.make_subplots')
def test_display_metrics(mock_make_subplots, mock_go, mock_st, mock_metrics, mock_session_state):
    """Test metrics display functionality."""
    # Setup mock data
    mock_session_state.metrics_history = [{
        'metrics': {
            'cpu': {'percent': 50.0, 'count': 8, 'frequency': 2.4},
            'memory': {'percent': 60.0, 'total': 16000, 'used': 9600},
            'disk': {'percent': 70.0, 'total': 500000, 'used': 350000}
        },
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': 12345
    }]
    mock_session_state.last_update = datetime.now()
    
    # Setup streamlit mocks
    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_st.columns.return_value = [mock_col1, mock_col2]
    
    # Mock context managers
    mock_col1.__enter__ = MagicMock(return_value=mock_col1)
    mock_col1.__exit__ = MagicMock(return_value=None)
    mock_col2.__enter__ = MagicMock(return_value=mock_col2)
    mock_col2.__exit__ = MagicMock(return_value=None)
    
    # Mock plotly
    mock_fig = MagicMock()
    mock_make_subplots.return_value = mock_fig
    
    # Test display_metrics
    metrics_to_show = ["CPU Usage", "Memory Usage", "Disk Usage"]
    display_metrics(mock_session_state, metrics_to_show)
    
    # Verify streamlit calls
    mock_st.columns.assert_called_once_with(2)
    
    # Verify metrics were displayed
    mock_st.metric.assert_any_call(
        "CPU Usage",
        "50.0%",
        delta=None
    )
    mock_st.metric.assert_any_call(
        "Memory Usage",
        "60.0%",
        delta=None
    )
    mock_st.metric.assert_any_call(
        "Disk Usage",
        "70.0%",
        delta=None
    )
    
    # Verify plot was created
    mock_st.plotly_chart.assert_called_once_with(mock_fig)
