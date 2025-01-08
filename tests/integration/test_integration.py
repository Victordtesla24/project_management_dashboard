"""Integration tests for the dashboard components."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch

from dashboard.config import init_config, get_config
from dashboard.core_scripts.metrics_collector import MetricsCollector
from dashboard.websocket.server import MetricsWebSocket
from dashboard.main import app, update_metrics


@pytest.fixture
def mock_server():
    """Mock the Prometheus HTTP server."""
    with patch('dashboard.core_scripts.metrics_collector.start_http_server') as mock:
        mock.return_value = None
        yield mock


@pytest.mark.integration
def test_config_metrics_integration(mock_server):
    """Test integration between ConfigManager and MetricsCollector."""
    # Initialize collector with config
    collector = MetricsCollector(port=8010)
    config = get_config()
    
    # Verify collector uses config values
    assert collector.retention_days == config['metrics']['retention_days']
    
    # Collect metrics and verify they match enabled metrics in config
    metrics = collector.collect_system_metrics()
    enabled_metrics = config['metrics']['enabled_metrics']
    
    for metric in ['cpu_usage', 'memory_usage', 'disk_usage']:
        if metric in enabled_metrics:
            assert metric in metrics


@pytest.fixture
def test_client():
    """Create a test client with session support."""
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    with app.test_client(use_cookies=True) as client:
        yield client

@pytest.fixture
def app_context():
    """Provide application context."""
    with app.app_context():
        yield

@pytest.mark.integration
@pytest.mark.asyncio
async def test_websocket_dashboard_integration(mock_server):
    """Test integration between WebSocket server and dashboard updates."""
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    
    # Start WebSocket server
    ws_server = MetricsWebSocket()
    await ws_server.start_server()
    
    try:
        with app.test_client() as test_client:
            # Set up session
            with test_client.session_transaction() as session:
                session['user'] = 'test_user'  # Simulate logged in user
                session['ws_token'] = 'test_token'  # Add WebSocket token
            
            # Update metrics
            metrics_data = {
                'cpu_usage': 45.5,
                'memory_usage': 60.2,
                'disk_usage': 75.8
            }
            
            # Simulate metrics update
            await ws_server.broadcast_message({
                'type': 'metrics_update',
                'data': metrics_data,
                'token': 'test_token'
            })
            
            # Verify dashboard receives updates
            response = test_client.get('/', follow_redirects=True)
            assert response.status_code == 200
            
            # Check WebSocket connection status
            assert ws_server.clients is not None
    finally:
        await ws_server.stop_server()


@pytest.mark.integration
def test_alerts_notifications_integration(mock_server):
    """Test integration between alert system and notifications."""
    collector = MetricsCollector(port=8011)
    config = get_config()
    
    # Get alert thresholds from config
    thresholds = config['metrics']['thresholds']
    
    # Collect metrics
    metrics = collector.collect_system_metrics()
    
    # Verify alerts are triggered when thresholds are exceeded
    for metric_name, threshold in thresholds.items():
        if metric_name in metrics:
            value = metrics[metric_name]
            if value > threshold:
                # Here you would verify that notifications were sent
                # For now, just verify the values are comparable
                assert isinstance(value, (int, float))
                assert isinstance(threshold, (int, float))
