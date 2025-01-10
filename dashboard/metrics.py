"""System metrics collection module."""
import json
import logging
import os
from datetime import datetime

import psutil

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and manage system metrics."""

    def __init__(self, config=None) -> None:
        self.config = config or {}
        self.metrics = {
            "system": {"cpu": 0.0, "memory": 0.0, "disk": 0.0},
            "processes": [],
            "timestamp": "",
        }

    def collect_system_metrics(self):
        """Collect system-wide metrics."""
        try:
            self.metrics["system"]["cpu"] = psutil.cpu_percent(interval=1)
            self.metrics["system"]["memory"] = psutil.virtual_memory().percent
            self.metrics["system"]["disk"] = psutil.disk_usage("/").percent
            self.metrics["timestamp"] = datetime.now().isoformat()
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    def collect_process_metrics(self):
        """Collect process-specific metrics."""
        try:
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    pinfo = proc.info
                    processes.append(
                        {
                            "pid": pinfo["pid"],
                            "name": pinfo["name"],
                            "cpu_percent": pinfo["cpu_percent"] or 0.0,
                            "memory_percent": pinfo["memory_percent"] or 0.0,
                        },
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            self.metrics["processes"] = sorted(
                processes,
                key=lambda x: (x["cpu_percent"], x["memory_percent"]),
                reverse=True,
            )[
                :10
            ]  # Keep only top 10 processes
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")

    def get_metrics(self):
        """Get all metrics."""
        self.collect_system_metrics()
        self.collect_process_metrics()
        return self.metrics

    def save_metrics(self, filepath):
        """Save metrics to a file."""
        try:
            with open(filepath, "w") as f:
                json.dump(self.metrics, f, indent=4)
            logger.info(f"Metrics saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving metrics to {filepath}: {e}")

    def load_metrics(self, filepath):
        """Load metrics from a file."""
        try:
            if os.path.exists(filepath):
                with open(filepath) as f:
                    self.metrics = json.load(f)
                logger.info(f"Metrics loaded from {filepath}")
            else:
                logger.warning(f"Metrics file not found: {filepath}")
        except Exception as e:
            logger.error(f"Error loading metrics from {filepath}: {e}")


def collect_metrics(config=None):
    """Collect system and process metrics.

    Args:
    ----
        config: Optional configuration dictionary

    Returns:
    -------
        dict: Collected metrics including system and process information
    """
    collector = MetricsCollector(config)
    return collector.get_metrics()
