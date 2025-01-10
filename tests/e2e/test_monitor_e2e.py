"""End-to-end tests for the monitor module."""

import json
import os
import subprocess
import time
from pathlib import Path

import pytest


@pytest.fixture
def monitor_process(project_root):
    """Start the monitor process for testing."""
    # Start monitor process
    process = subprocess.Popen(
        ["python", "-m", "src.monitor"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for process to start
    time.sleep(2)

    yield process

    # Cleanup
    process.terminate()
    process.wait(timeout=5)


def test_monitor_service_collects_metrics(monitor_process, project_root):
    """Test that monitor service collects metrics over time."""
    # Get metrics directory
    metrics_dir = Path(project_root) / "metrics" / "data"

    # Wait for metrics collection
    time.sleep(5)

    # Check that metrics files were created
    assert metrics_dir.exists()
    files = list(metrics_dir.glob("metrics_*.json"))
    assert len(files) > 0

    # Verify metrics file content
    with open(files[0]) as f:
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


def test_monitor_service_handles_interruption(monitor_process, project_root):
    """Test that monitor service handles interruption gracefully."""
    # Get metrics directory
    metrics_dir = Path(project_root) / "metrics" / "data"

    # Wait for initial metrics collection
    time.sleep(5)

    # Get initial file count
    initial_files = set(metrics_dir.glob("metrics_*.json"))

    # Interrupt and restart monitor
    monitor_process.terminate()
    monitor_process.wait(timeout=5)

    # Start new monitor process
    new_process = subprocess.Popen(
        ["python", "-m", "src.monitor"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Wait for new metrics collection
        time.sleep(5)

        # Check that new metrics files were created
        current_files = set(metrics_dir.glob("metrics_*.json"))
        new_files = current_files - initial_files
        assert len(new_files) > 0

        # Verify new metrics file content
        latest_file = max(current_files, key=os.path.getctime)
        with open(latest_file) as f:
            metrics = json.load(f)

        # Verify structure maintained
        assert "timestamp" in metrics
        assert "system" in metrics
        assert "processes" in metrics
    finally:
        new_process.terminate()
        new_process.wait(timeout=5)


def test_monitor_service_logs_errors(monitor_process, project_root, caplog):
    """Test that monitor service logs errors appropriately."""
    # Get logs directory
    logs_dir = Path(project_root) / "logs"

    # Wait for potential error logging
    time.sleep(5)

    # Check monitor process status
    assert monitor_process.poll() is None, "Monitor process should still be running"

    # Verify log file exists and contains no critical errors
    log_file = logs_dir / "monitor.log"
    assert log_file.exists()

    with open(log_file) as f:
        log_content = f.read()
        assert "ERROR" not in log_content, "No errors should be logged during normal operation"
        assert "CRITICAL" not in log_content, "No critical errors should be logged"
