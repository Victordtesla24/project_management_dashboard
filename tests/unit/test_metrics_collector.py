"""Unit tests for the metrics collector module."""


from core_scripts.metrics_collector import MetricsCollector
from tests.fixtures.base import mock_metrics


def test_add_metric():
    """Test adding a metric."""
    collector = MetricsCollector()
    metric = mock_metrics[0]
    collector.add_metric(metric["name"], metric["value"], metric["tags"])
    assert metric["name"] in collector.points


def test_collect_metrics(mock_metrics):
    """Test collecting metrics."""
    collector = MetricsCollector()
    for metric in mock_metrics:
        collector.add_metric(metric["name"], metric["value"], metric["tags"])
    collector.collect()
    assert len(collector.points) == 0


def test_get_system_metrics():
    """Test getting system metrics."""
    collector = MetricsCollector()
    metrics = collector.get_system_metrics()
    assert isinstance(metrics, list)
    assert all(isinstance(m, dict) for m in metrics)
    assert all("name" in m and "value" in m and "tags" in m for m in metrics)
