"""System monitoring module."""
import json
import logging
import time
from pathlib import Path

import psutil  # type: ignore

logger = logging.getLogger(__name__)

def monitor_system():
    """Monitor system resources and processes."""
    processes = []
    for proc in psutil.process_iter():
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return {"processes": processes, "timestamp": time.time()}

def main():
    """Main function to run system monitoring."""
    monitor_dir = Path("metrics")
    monitor_dir.mkdir(exist_ok=True)
    monitor_file = monitor_dir / "process_metrics.json"

    logger.info("Starting system monitoring")
    while True:
        try:
            data = monitor_system()
            monitor_file.write_text(json.dumps(data))
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error monitoring system: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
