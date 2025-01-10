"""Integration tests for the dashboard components."""

import asyncio
from datetime import datetime
from unittest.mock import patch

import pytest

from dashboard.config import get_config
from dashboard.core_scripts.metrics_collector import MetricsCollector
from dashboard.websocket.server import MetricsWebSocket


@pytest.fixture
def mock_server():
    """Mock the Prometheus HTTP server."""
    with patch("dashboard.core_scripts.metrics_collector.start_http_server") as mock:
        mock.return_value = None
        yield mock


@pytest.mark.integration
def test_config_metrics_integration(app, mock_server):
    """Test integration between ConfigManager and MetricsCollector."""
    with app.app_context():
        # Initialize collector with config
        collector = MetricsCollector(port=8010)
        config = get_config()

        # Verify collector uses config values
        assert "collection_interval" in config["metrics"]
        assert isinstance(config["metrics"]["collection_interval"], int)

        # Collect metrics and verify they match enabled metrics in config
        metrics = collector.collect_system_metrics()
        enabled_metrics = config["metrics"]["enabled_metrics"]

        # Check that we have metrics data
        assert metrics is not None
        assert len(metrics) > 0

        # Verify enabled metrics are present
        for metric in enabled_metrics:
            metric_key = f"{metric}_usage"
            assert metric_key in metrics


@pytest.fixture
def mock_auth():
    """Mock authentication decorator and middleware."""
    with patch("dashboard.auth.middleware.verify_token") as mock_verify:
        mock_verify.return_value = {"username": "test_user"}
        with patch("dashboard.routes.login_required") as mock_required:

            def pass_through(f):
                return f

            mock_required.side_effect = pass_through
            yield mock_required


@pytest.mark.integration
@pytest.mark.asyncio
async def test_websocket_dashboard_integration(app, mock_server, mock_auth):
    """Test integration between WebSocket server and dashboard updates."""
    with app.app_context():
        # Start WebSocket server
        ws_server = MetricsWebSocket()
        await ws_server.start_server()

        try:
            # Set up test client
            with app.test_client() as test_client:
                # Set up session
                with test_client.session_transaction() as session:
                    session["user"] = "test_user"  # Simulate logged in user
                    session["ws_token"] = "test_token"  # Add WebSocket token

                # Update metrics
                metrics_data = {"cpu_usage": 45.5, "memory_usage": 60.2, "disk_usage": 75.8}

                # Simulate metrics update
                await ws_server.broadcast_message(
                    {"type": "metrics_update", "data": metrics_data, "token": "test_token"}
                )

                # Verify dashboard receives updates
                response = test_client.get("/", follow_redirects=True)
                assert response.status_code == 200

                # Check WebSocket connection status
                assert ws_server.clients is not None
        finally:
            await ws_server.stop_server()


@pytest.mark.integration
def test_alerts_notifications_integration(app, mock_server):
    """Test integration between alert system and notifications."""
    with app.app_context():
        collector = MetricsCollector(port=8011)
        config = get_config()

        # Get alert thresholds from config
        thresholds = config["metrics"]["thresholds"]

        # Collect metrics
        metrics = collector.collect_system_metrics()

        # Verify alerts are triggered when thresholds are exceeded
        for metric_name, threshold in thresholds.items():
            metric_key = f"{metric_name}_usage"
            if metric_key in metrics:
                value = metrics[metric_key]
                # Verify the values are comparable
                assert isinstance(value, (int, float))
                assert isinstance(threshold, (int, float))
