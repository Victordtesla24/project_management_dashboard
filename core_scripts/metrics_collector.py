"""Metrics collection module."""
import time
from typing import Any

import psutil


class MetricsCollector:
    """Collect system metrics."""
    def __init__(self):
        """Initialize the metrics collector."""
        self.last_collection = 0
        self.collection_interval = 1  # seconds

    async def collect_metrics(self) -> dict[str, Any]:
        """Collect system metrics.

        Returns:
            Dict containing the collected metrics.
        """
        current_time = time.time()
        if current_time - self.last_collection < self.collection_interval:
            return {}

        try:
            metrics = {
                "cpu": self._get_cpu_metrics(),
                "memory": self._get_memory_metrics(),
                "disk": self._get_disk_metrics(),
                "network": self._get_network_metrics(),
                "timestamp": current_time,
            }
            self.last_collection = current_time
            return metrics
        except Exception:
            return {}

    def _get_cpu_metrics(self) -> dict[str, float]:
        """Get CPU metrics.

        Returns:
            Dict containing CPU metrics.
        """
        try:
            return {
                "percent": psutil.cpu_percent(interval=None),
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            }
        except Exception:
            return {"percent": 0, "count": 0, "frequency": 0}

    def _get_memory_metrics(self) -> dict[str, float]:
        """Get memory metrics.

        Returns:
            Dict containing memory metrics.
        """
        try:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
            }
        except Exception:
            return {"total": 0, "available": 0, "percent": 0, "used": 0}

    def _get_disk_metrics(self) -> dict[str, float]:
        """Get disk metrics.

        Returns:
            Dict containing disk metrics.
        """
        try:
            disk = psutil.disk_usage("/")
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            }
        except Exception:
            return {"total": 0, "used": 0, "free": 0, "percent": 0}

    def _get_network_metrics(self) -> dict[str, float]:
        """Get network metrics.

        Returns:
            Dict containing network metrics.
        """
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            }
        except Exception:
            return {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0,
            }
