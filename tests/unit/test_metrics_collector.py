"""Test module for metrics collector."""
import json
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from prometheus_client import CollectorRegistry

from dashboard.core_scripts.metrics_collector import MetricsCollector


@pytest.fixture(autouse=True)
def setup_config():
    """Initialize configuration before each test."""
    config = {"metrics": {"retention": {"days": 30}}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    from dashboard.config import init_config

    init_config(config_path)

    yield

    import os

    os.unlink(config_path)


@pytest.fixture()
def mock_config():
    """Mock configuration fixture."""
    with patch("dashboard.core_scripts.metrics_collector.get_config") as mock:
        mock.return_value = {"metrics": {"retention": {"days": 30}}}
        yield mock


@pytest.fixture()
def mock_psutil():
    """Mock psutil fixture."""
    with patch("dashboard.core_scripts.metrics_collector.psutil") as mock:
        # Configure CPU mock
        mock.cpu_percent.return_value = 45.2

        # Configure memory mock
        memory_mock = Mock()
        memory_mock.percent = 62.3
        mock.virtual_memory.return_value = memory_mock

        # Configure disk mock
        disk_mock = Mock()
        disk_mock.percent = 78.9
        mock.disk_usage.return_value = disk_mock

        yield mock


@pytest.fixture()
def mock_prometheus():
    """Mock Prometheus server fixture."""
    with patch("dashboard.core_scripts.metrics_collector.start_http_server") as server_mock:
        with patch("dashboard.core_scripts.metrics_collector.CollectorRegistry") as registry_mock:
            with patch("dashboard.core_scripts.metrics_collector.Histogram") as histogram_mock:
                registry_mock.return_value = CollectorRegistry()
                server_mock.return_value = None
                histogram_instance = MagicMock()
                histogram_instance.observe = MagicMock()
                histogram_mock.return_value = histogram_instance
                yield server_mock


@pytest.fixture()
def collector(mock_config, mock_prometheus):
    """Metrics collector fixture."""
    return MetricsCollector(port=8000)


def test_collect_system_metrics(collector, mock_psutil):
    """Test system metrics collection."""
    metrics = collector.collect_system_metrics()

    assert isinstance(metrics, dict)
    assert metrics["cpu_usage"] == 45.2
    assert metrics["memory_usage"] == 62.3
    assert metrics["disk_usage"] == 78.9
    assert "timestamp" in metrics
    assert isinstance(datetime.fromisoformat(metrics["timestamp"]), datetime)


def test_collect_project_metrics(collector):
    """Test project metrics collection."""
    metrics = collector.collect_project_metrics()

    assert isinstance(metrics, dict)
    assert isinstance(metrics.get("active_tasks"), (int, float))
    assert isinstance(metrics.get("completed_tasks"), (int, float))
    assert isinstance(metrics.get("team_velocity"), (int, float))
    assert isinstance(metrics.get("sprint_progress"), (int, float))
    assert "timestamp" in metrics
    assert isinstance(datetime.fromisoformat(metrics["timestamp"]), datetime)


def test_record_response_time(collector):
    """Test response time recording."""
    # Should not raise any exceptions
    collector.record_response_time(0.5)
    # Verify observe was called
    collector.response_time.observe.assert_called_once_with(0.5)


def test_cleanup_old_metrics(collector):
    """Test metrics cleanup."""
    # Record initial cleanup time
    initial_cleanup = collector.last_cleanup

    # Run cleanup
    collector.cleanup_old_metrics()

    # Verify cleanup time wasn't updated (since less than a day has passed)
    assert collector.last_cleanup == initial_cleanup


def test_initialization_error():
    """Test initialization with server start failure."""
    with patch("dashboard.core_scripts.metrics_collector.start_http_server") as mock:
        mock.side_effect = Exception("Server start failed")
        with pytest.raises(Exception, match="Server start failed"):
            MetricsCollector(port=8000)


def test_custom_retention(mock_prometheus):
    """Test initialization with custom retention days."""
    collector = MetricsCollector(port=8000, retention_days=60)
    assert collector.retention_days == 60


def test_default_retention(mock_config, mock_prometheus):
    """Test initialization with default retention days."""
    collector = MetricsCollector(port=8000)
    assert collector.retention_days == 30


def test_logging_setup(mock_config, mock_prometheus):
    """Test logging setup."""
    collector = MetricsCollector(port=8000)
    assert collector.logger.level == 20  # INFO level
