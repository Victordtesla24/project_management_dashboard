"""Metrics collection module."""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import psutil
from prometheus_client import CollectorRegistry, Gauge

# Initialize Prometheus registry
REGISTRY = CollectorRegistry()

# Define Prometheus metrics
CPU_GAUGE = Gauge("cpu_usage_percent", "CPU usage percentage", registry=REGISTRY)
MEMORY_GAUGE = Gauge("memory_usage_percent", "Memory usage percentage", registry=REGISTRY)
DISK_GAUGE = Gauge("disk_usage_percent", "Disk usage percentage", registry=REGISTRY)


def _get_cpu_frequency() -> float:
    """Get CPU frequency with error handling."""
    try:
        freq = psutil.cpu_freq()
        return freq.current if freq else 0
    except (FileNotFoundError, AttributeError):
        return 0


def collect_system_metrics() -> dict[str, Any]:
    """Collect system metrics and update Prometheus gauges."""
    metrics = {
        "cpu": {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "frequency": _get_cpu_frequency(),
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "total": psutil.disk_usage("/").total,
            "used": psutil.disk_usage("/").used,
            "percent": psutil.disk_usage("/").percent,
        },
    }

    # Update Prometheus metrics
    CPU_GAUGE.set(metrics["cpu"]["percent"])
    MEMORY_GAUGE.set(metrics["memory"]["percent"])
    DISK_GAUGE.set(metrics["disk"]["percent"])

    return metrics


def process_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    """Process and format metrics data."""
    return {
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": psutil.boot_time(),
    }


def setup_logging():
    """Set up logging configuration."""
    # Ensure logs directory exists
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "metrics.log")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
    )
    return logging.getLogger(__name__)


if __name__ == "__main__":
    import time

    logger = setup_logging()
    logger.info("Starting metrics collector...")

    try:
        while True:
            try:
                metrics = collect_system_metrics()
                processed = process_metrics(metrics)
                logger.info(f"Collected metrics: {processed}")
                time.sleep(1)  # Collect metrics every second
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}", exc_info=True)
                time.sleep(5)  # Back off on error
    except KeyboardInterrupt:
        logger.info("Metrics collector stopped by user.")
    except Exception as e:
        logger.error(f"Metrics collector crashed: {e}", exc_info=True)
        sys.exit(1)
