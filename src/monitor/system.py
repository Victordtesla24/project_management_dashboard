"""System monitoring module."""
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict

import psutil

logger = logging.getLogger(__name__)


class SystemMonitor:
    """System monitor class."""

    def __init__(self) -> None:
        """Initialize system monitor."""
        self.start_time = time.time()
        self.initialized = True

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        return {
            "timestamp": time.time(),
            "metrics": {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "processes": len(list(psutil.process_iter())),
            },
        }

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process collected data.

        Args:
        ----
            data: Raw metrics data.

        Returns:
        -------
            Processed metrics data.
        """
        return {
            "processed_timestamp": time.time(),
            "timestamp": data["timestamp"],
            "metrics": data["metrics"],
        }


def initialize_monitor() -> SystemMonitor:
    """Initialize the system monitor."""
    logger.info("Initializing system monitor")
    return SystemMonitor()


def monitor_system() -> Dict[str, Any]:
    """Monitor system resources and processes."""
    monitor = initialize_monitor()
    return monitor.collect_metrics()


def main() -> None:
    """Main function to run system monitoring."""
    monitor_dir = Path("metrics")
    monitor_dir.mkdir(exist_ok=True)
    monitor_file = monitor_dir / "process_metrics.json"

    logger.info("Starting system monitoring")
    monitor = initialize_monitor()
    while True:
        try:
            data = monitor.collect_metrics()
            processed = monitor.process_data(data)
            monitor_file.write_text(json.dumps(processed))
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error monitoring system: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
