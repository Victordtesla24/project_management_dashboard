from dashboard.metrics import collect_metrics


def test_collect_metrics():
    """Test metrics collection."""
    metrics = collect_metrics()
    assert isinstance(metrics, dict)
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics


def test_metrics_format():
    """Test metrics format."""
    metrics = collect_metrics()
    assert all(isinstance(v, dict) for v in metrics.values())
    assert all(isinstance(v, (int, float)) for m in metrics.values() for v in m.values())
