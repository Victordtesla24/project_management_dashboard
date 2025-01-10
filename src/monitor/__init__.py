"""Monitor system module."""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict

import psutil


class MetricsMonitor:
    """System metrics monitoring class."""

    def __init__(self, config_dir: str) -> None:
        """Initialize monitor with config directory path."""
        self.config_dir = config_dir
        self.process_config = self._load_config("process_metrics.json")
        self.system_config = self._load_config("system_metrics.json")
        self.data_dir = os.path.join(self.config_dir, "data")

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = os.path.join(self.config_dir, filename)
        with open(config_path) as f:
            return json.load(f)

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-wide metrics."""
        return {
            "cpu": {
                "percent": psutil.cpu_percent(),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict(),
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used,
                "free": psutil.virtual_memory().free,
            },
            "disk": {
                "total": psutil.disk_usage("/").total,
                "used": psutil.disk_usage("/").used,
                "free": psutil.disk_usage("/").free,
                "percent": psutil.disk_usage("/").percent,
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv,
            },
            "load": {"load_avg": psutil.getloadavg()},
        }

    def _collect_process_metrics(self) -> Dict[str, Any]:
        """Collect process-specific metrics."""
        metrics = {}

        for process in psutil.process_iter():
            try:
                cmdline = process.cmdline()
                for proc_config in self.process_config.get("processes", []):
                    pattern = proc_config["pattern"]
                    if any(re.search(pattern, cmd) for cmd in cmdline):
                        proc_metrics = {
                            "pid": process.pid,
                            "cpu_percent": process.cpu_percent(),
                            "memory": {
                                "rss": process.memory_info().rss,
                                "vms": process.memory_info().vms,
                            },
                            "num_threads": process.num_threads(),
                        }
                        metrics[proc_config["name"]] = proc_metrics
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return metrics

    def _collect_metrics(self) -> None:
        """Collect and store all metrics."""
        timestamp = datetime.now().isoformat()

        metrics = {
            "timestamp": timestamp,
            "system": self._collect_system_metrics(),
            "processes": self._collect_process_metrics(),
        }

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        # Save metrics to file
        metrics_file = os.path.join(self.data_dir, f"metrics_{timestamp}.json")
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

    def start(self) -> None:
        """Start metrics collection."""
        self._collect_metrics()
