"""Unit tests for the metrics collector module."""

from unittest.mock import MagicMock, patch

import pytest

from dashboard.core_scripts.metrics_collector import MetricsCollector
from tests.fixtures.base import mock_metrics


@pytest.fixture
def mock_server():
    """Mock the Prometheus HTTP server."""
    with patch("dashboard.core_scripts.metrics_collector.start_http_server") as mock:
        mock.return_value = None
        yield mock


def test_add_metric(mock_server):
    """Test adding a metric."""
    collector = MetricsCollector(port=8001)
    metrics = collector.collect_system_metrics()
    assert isinstance(metrics, dict)
    assert "cpu_usage" in metrics
    assert "memory_usage" in metrics
    assert "disk_usage" in metrics


def test_collect_metrics(mock_server, mock_metrics):
    """Test collecting metrics."""
    collector = MetricsCollector(port=8002)
    metrics = collector.collect_project_metrics()
    assert isinstance(metrics, dict)
    assert "active_tasks" in metrics
    assert "completed_tasks" in metrics
    assert "team_velocity" in metrics
    assert "sprint_progress" in metrics


def test_get_system_metrics(mock_server):
    """Test getting system metrics."""
    collector = MetricsCollector(port=8003)
    metrics = collector.collect_system_metrics()
    assert isinstance(metrics, dict)
    assert all(key in metrics for key in ["cpu_usage", "memory_usage", "disk_usage", "timestamp"])
