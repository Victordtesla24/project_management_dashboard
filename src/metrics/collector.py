"""Metrics collection module."""

import time
from datetime import datetime
from typing import Dict

import psutil


class MetricsCollector:
    """Collector for system and application metrics."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.last_collection = None
        self.collection_interval = 60  # seconds

    def collect_system_metrics(self) -> Dict:
        """Collect system-level metrics."""
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
            "network": self._get_network_stats(),
        }

    def _get_network_stats(self) -> Dict:
        """Get network statistics."""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }

    def collect_application_metrics(self) -> Dict:
        """Collect application-specific metrics."""
        return {
            "process_count": len(psutil.Process().children()),
            "thread_count": psutil.Process().num_threads(),
            "open_files": len(psutil.Process().open_files()),
            "connections": len(psutil.Process().connections()),
        }

    def collect_all_metrics(self) -> Dict:
        """Collect all metrics."""
        current_time = time.time()

        # Check collection interval
        if self.last_collection and current_time - self.last_collection < self.collection_interval:
            return {}

        self.last_collection = current_time

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": self.collect_system_metrics(),
            "application": self.collect_application_metrics(),
        }


# Create singleton instance
collector = MetricsCollector()
