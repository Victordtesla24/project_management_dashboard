import json
import logging
import time
from pathlib import Path

import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("metrics_collector")


def collect_metrics():
    metrics = {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv,
        },
    }
    return metrics


def main():
    metrics_dir = Path("metrics")
    metrics_dir.mkdir(exist_ok=True)
    metrics_file = metrics_dir / "system_metrics.json"

    logger.info("Starting metrics collection")
    while True:
        try:
            metrics = collect_metrics()
            metrics_file.write_text(json.dumps(metrics))
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
