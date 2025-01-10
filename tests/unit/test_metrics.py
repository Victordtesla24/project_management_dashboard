"""Test metrics collection functionality."""
from dashboard.metrics import MetricsCollector, collect_metrics


def test_collect_metrics():
    """Test metrics collection."""
    with patch("psutil.cpu_percent", return_value=50.0), patch(
        "psutil.virtual_memory", return_value=type("obj", (object,), {"percent": 75.0})(),
    ), patch("psutil.disk_usage", return_value=type("obj", (object,), {"percent": 80.0})()), patch(
        "psutil.process_iter", return_value=[],
    ):
        metrics = collect_metrics()

    # Check basic structure
    assert isinstance(metrics, dict)
    assert "system" in metrics
    assert "processes" in metrics
    assert "timestamp" in metrics

    # Check system metrics structure
    system_metrics = metrics["system"]
    assert isinstance(system_metrics, dict)
    assert all(key in system_metrics for key in ["cpu", "memory", "disk"])
    assert all(isinstance(value, (int, float)) for value in system_metrics.values())
    # CPU can exceed 100% on multi-core systems, but memory and disk should be 0-100%
    assert 0 <= system_metrics["memory"] <= 100
    assert 0 <= system_metrics["disk"] <= 100
    assert system_metrics["cpu"] >= 0  # CPU can exceed 100% on multi-core systems


def test_metrics_format():
    """Test metrics format."""
    collector = MetricsCollector()
    with patch("psutil.cpu_percent", return_value=50.0), patch(
        "psutil.virtual_memory", return_value=type("obj", (object,), {"percent": 75.0})(),
    ), patch("psutil.disk_usage", return_value=type("obj", (object,), {"percent": 80.0})()), patch(
        "psutil.process_iter", return_value=[],
    ):
        metrics = collector.get_metrics()

    # Check system metrics format
    system_metrics = metrics["system"]
    assert isinstance(system_metrics, dict)
    assert all(isinstance(value, (int, float)) for value in system_metrics.values())

    # Check process metrics format
    processes = metrics["processes"]
    assert isinstance(processes, list)
    assert len(processes) <= 10  # Should only keep top 10 processes

    if processes:  # Only check if there are processes
        process = processes[0]  # Check first process
        assert isinstance(process, dict)
        assert all(key in process for key in ["pid", "name", "cpu_percent", "memory_percent"])
        assert isinstance(process["pid"], int)
        assert isinstance(process["name"], str)
        assert isinstance(process["cpu_percent"], (int, float))
        assert isinstance(process["memory_percent"], (int, float))
        assert process["cpu_percent"] >= 0  # CPU can exceed 100% on multi-core systems
        assert 0 <= process["memory_percent"] <= 100


from unittest.mock import patch


def test_metrics_persistence(tmp_path):
    """Test metrics file operations."""
    collector = MetricsCollector()
    metrics_file = tmp_path / "metrics.json"

    # Mock psutil calls to avoid actual system calls
    with patch("psutil.cpu_percent", return_value=50.0), patch(
        "psutil.virtual_memory", return_value=type("obj", (object,), {"percent": 75.0})(),
    ), patch("psutil.disk_usage", return_value=type("obj", (object,), {"percent": 80.0})()), patch(
        "psutil.process_iter", return_value=[],
    ):
        # Test saving metrics
        collector.collect_system_metrics()
        collector.collect_process_metrics()
    collector.save_metrics(metrics_file)
    assert metrics_file.exists()

    # Test loading metrics
    new_collector = MetricsCollector()
    new_collector.load_metrics(metrics_file)
    loaded_metrics = new_collector.metrics

    assert isinstance(loaded_metrics, dict)
    assert "system" in loaded_metrics
    assert "processes" in loaded_metrics
    assert "timestamp" in loaded_metrics


def test_metrics_collector_initialization():
    """Test MetricsCollector initialization."""
    # Test with default config
    collector = MetricsCollector()
    assert collector.config == {}
    assert isinstance(collector.metrics, dict)
    assert all(key in collector.metrics for key in ["system", "processes", "timestamp"])

    # Test with custom config
    custom_config = {"interval": 5}
    collector = MetricsCollector(custom_config)
    assert collector.config == custom_config
