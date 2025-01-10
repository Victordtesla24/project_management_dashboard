"""Unit tests for the monitor module."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from src.monitor import MetricsMonitor


@pytest.fixture
def mock_config_dir(tmp_path):
    """Create a temporary config directory with mock configuration files."""
    config_dir = tmp_path / "metrics"
    config_dir.mkdir()

    # Create mock process metrics config
    process_config = {
        "collection_interval": 60,
        "processes": [
            {
                "name": "test_process",
                "pattern": "python.*test",
                "metrics": ["cpu", "memory", "threads"],
            }
        ],
    }
    with open(config_dir / "process_metrics.json", "w") as f:
        json.dump(process_config, f)

    # Create mock system metrics config
    system_config = {
        "collection_interval": 300,
        "metrics": {"cpu": True, "memory": True, "disk": True, "network": True, "load": True},
        "thresholds": {"cpu_percent": 80, "memory_percent": 85, "disk_percent": 90},
    }
    with open(config_dir / "system_metrics.json", "w") as f:
        json.dump(system_config, f)

    return config_dir


@pytest.fixture
def monitor(mock_config_dir):
    """Create a MetricsMonitor instance with mock configuration."""
    return MetricsMonitor(config_dir=str(mock_config_dir))


def test_load_config(monitor, mock_config_dir):
    """Test loading configuration files."""
    assert monitor.process_config["collection_interval"] == 60
    assert len(monitor.process_config["processes"]) == 1
    assert monitor.system_config["collection_interval"] == 300
    assert all(monitor.system_config["metrics"].values())


@patch("psutil.cpu_percent")
@patch("psutil.cpu_count")
@patch("psutil.cpu_freq")
@patch("psutil.virtual_memory")
@patch("psutil.disk_usage")
@patch("psutil.net_io_counters")
@patch("psutil.getloadavg")
def test_collect_system_metrics(
    mock_loadavg,
    mock_net,
    mock_disk,
    mock_mem,
    mock_cpu_freq,
    mock_cpu_count,
    mock_cpu_percent,
    monitor,
):
    """Test collecting system metrics."""
    # Setup mocks
    mock_cpu_percent.return_value = 50.0
    mock_cpu_count.return_value = 8
    mock_cpu_freq.return_value = MagicMock(current=2.5, min=2.0, max=3.0)
    mock_mem.return_value = MagicMock(
        total=16000000000, available=8000000000, percent=50.0, used=8000000000, free=8000000000
    )
    mock_disk.return_value = MagicMock(
        total=100000000000, used=50000000000, free=50000000000, percent=50.0
    )
    mock_net.return_value = MagicMock(
        bytes_sent=1000000, bytes_recv=2000000, packets_sent=1000, packets_recv=2000
    )
    mock_loadavg.return_value = (1.0, 1.5, 2.0)

    # Call method
    metrics = monitor._collect_system_metrics()

    # Verify results
    assert metrics["cpu"]["percent"] == 50.0
    assert metrics["cpu"]["count"] == 8
    assert metrics["cpu"]["freq"]["current"] == 2.5
    assert metrics["memory"]["total"] == 16000000000
    assert metrics["memory"]["percent"] == 50.0
    assert metrics["disk"]["total"] == 100000000000
    assert metrics["disk"]["percent"] == 50.0
    assert metrics["network"]["bytes_sent"] == 1000000
    assert metrics["network"]["bytes_recv"] == 2000000
    assert metrics["load"]["load_avg"] == (1.0, 1.5, 2.0)


@patch("psutil.process_iter")
def test_collect_process_metrics(mock_process_iter, monitor):
    """Test collecting process metrics."""
    # Setup mock process
    mock_process = MagicMock()
    mock_process.cmdline.return_value = ["python", "test_script.py"]
    mock_process.cpu_percent.return_value = 10.0
    mock_process.memory_info.return_value = MagicMock(rss=1000000, vms=2000000)
    mock_process.num_threads.return_value = 4
    mock_process_iter.return_value = [mock_process]

    # Call method
    metrics = monitor._collect_process_metrics()

    # Verify results
    assert "test_process" in metrics
    assert metrics["test_process"]["cpu_percent"] == 10.0
    assert metrics["test_process"]["memory"]["rss"] == 1000000
    assert metrics["test_process"]["memory"]["vms"] == 2000000
    assert metrics["test_process"]["num_threads"] == 4


@patch("builtins.open")
@patch("json.dump")
@patch("os.makedirs")
def test_collect_metrics(mock_makedirs, mock_json_dump, mock_open, monitor):
    """Test the main metrics collection method."""
    with patch.object(monitor, "_collect_system_metrics") as mock_system_metrics:
        with patch.object(monitor, "_collect_process_metrics") as mock_process_metrics:
            # Setup mocks
            mock_system_metrics.return_value = {"cpu": {"percent": 50.0}}
            mock_process_metrics.return_value = {"test_process": {"cpu_percent": 10.0}}

            # Call method
            monitor._collect_metrics()

            # Verify results
            mock_makedirs.assert_called_once()
            mock_json_dump.assert_called_once()
            args = mock_json_dump.call_args[0][0]
            assert "timestamp" in args
            assert args["system"] == {"cpu": {"percent": 50.0}}
            assert args["processes"] == {"test_process": {"cpu_percent": 10.0}}
