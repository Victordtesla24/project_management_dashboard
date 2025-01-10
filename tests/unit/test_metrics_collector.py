"""Test module for metrics collector."""
from unittest.mock import patch

import pytest

from dashboard.core_scripts.metrics_collector import MetricsCollector


@pytest.fixture
def mock_server():
    """Mock server fixture."""
    with patch("dashboard.core_scripts.metrics_collector.start_http_server") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def collector():
    """Metrics collector fixture."""
    return MetricsCollector()


def test_add_metric(mock_server):
    """Test adding metrics."""
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


def test_collect_system_metrics(collector):
    """Test system metrics collection."""
    metrics = collector.collect_system_metrics()
    assert isinstance(metrics, dict)
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics


def test_collect_process_metrics(collector):
    """Test process metrics collection."""
    metrics = collector.collect_process_metrics("python")
    assert isinstance(metrics, dict)
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "threads" in metrics
