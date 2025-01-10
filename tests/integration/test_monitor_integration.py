"""Integration tests for the monitor module."""

import json
import os
import time

import pytest

from src.monitor import MetricsMonitor


@pytest.fixture
def monitor(metrics_dir):
    """Create a MetricsMonitor instance with real configuration."""
    return MetricsMonitor(config_dir=metrics_dir)


def test_monitor_collects_metrics(monitor, test_data_dir):
    """Test that monitor can collect and store metrics."""
    # Create data directory in test location
    data_dir = os.path.join(test_data_dir, "metrics", "data")
    os.makedirs(data_dir, exist_ok=True)

    # Collect metrics
    monitor._collect_metrics()

    # Check that metrics file was created
    files = os.listdir(data_dir)
    assert len(files) > 0

    # Verify metrics file content
    metrics_file = os.path.join(data_dir, files[0])
    with open(metrics_file) as f:
        metrics = json.load(f)

    # Verify structure
    assert "timestamp" in metrics
    assert "system" in metrics
    assert "processes" in metrics

    # Verify system metrics
    system = metrics["system"]
    assert "cpu" in system
    assert "memory" in system
    assert "disk" in system
    assert "network" in system
    assert "load" in system

    # Verify metric values are reasonable
    assert 0 <= system["cpu"]["percent"] <= 100
    assert system["memory"]["total"] > 0
    assert system["disk"]["total"] > 0


def test_monitor_respects_collection_interval(monitor, test_data_dir):
    """Test that monitor respects collection intervals."""
    # Create data directory in test location
    data_dir = os.path.join(test_data_dir, "metrics", "data")
    os.makedirs(data_dir, exist_ok=True)

    # Collect metrics twice with short interval
    monitor._collect_metrics()
    time.sleep(1)
    monitor._collect_metrics()

    # Check number of files created
    files = sorted(os.listdir(data_dir))
    assert len(files) == 2

    # Verify timestamps
    timestamps = []
    for file in files:
        with open(os.path.join(data_dir, file)) as f:
            metrics = json.load(f)
            timestamps.append(metrics["timestamp"])

    # Verify interval between collections
    interval = timestamps[1] - timestamps[0]
    assert 0.5 <= interval <= 2  # Allow some flexibility for test execution time


def test_monitor_handles_missing_processes(monitor, test_data_dir):
    """Test that monitor handles missing monitored processes gracefully."""
    # Create data directory in test location
    data_dir = os.path.join(test_data_dir, "metrics", "data")
    os.makedirs(data_dir, exist_ok=True)

    # Add non-existent process to monitor
    monitor.process_config["processes"].append(
        {
            "name": "nonexistent",
            "pattern": "this_process_does_not_exist",
            "metrics": ["cpu", "memory"],
        }
    )

    # Collect metrics
    monitor._collect_metrics()

    # Verify metrics were collected without error
    files = os.listdir(data_dir)
    assert len(files) > 0

    # Verify metrics file content
    metrics_file = os.path.join(data_dir, files[0])
    with open(metrics_file) as f:
        metrics = json.load(f)

    # Verify system metrics still present
    assert "system" in metrics
    assert all(key in metrics["system"] for key in ["cpu", "memory", "disk", "network", "load"])
