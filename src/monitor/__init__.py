"""System monitoring module."""
import json
import logging
import os
import time
from typing import Any, Optional

import psutil  # type: ignore

logger = logging.getLogger(__name__)

class MetricsMonitor:
    """Monitor system metrics and process metrics."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the metrics monitor."""
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "config", "monitor.json",
        )
        self.system_config = self._load_config()
        self.process_config = self._load_config("process_monitor.json")
        self.metrics_dir = os.path.join(os.path.dirname(__file__), "metrics")
        os.makedirs(self.metrics_dir, exist_ok=True)

    def _load_config(self, filename: Optional[str] = None) -> dict[str, Any]:
        """Load configuration from a JSON file."""
        config_path = self.config_path
        if filename:
            config_path = os.path.join(os.path.dirname(self.config_path), filename)

        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config {filename}: {e}")
            return {}

    def _collect_system_metrics(self) -> dict:
        """Collect system-wide metrics."""
        metrics = {}
        config = self.system_config.get("metrics", {})

        if config.get("cpu", True):
            try:
                cpu_freq = psutil.cpu_freq()
                freq_info = cpu_freq._asdict() if cpu_freq else {}
            except (AttributeError, FileNotFoundError):
                freq_info = {}

            metrics["cpu"] = {
                "percent": psutil.cpu_percent(interval=None),
                "count": psutil.cpu_count(),
                "freq": freq_info,
            }

        if config.get("memory", True):
            mem = psutil.virtual_memory()
            metrics["memory"] = {
                "total": mem.total,
                "available": mem.available,
                "percent": mem.percent,
                "used": mem.used,
                "free": mem.free,
            }

        if config.get("disk", True):
            disk = psutil.disk_usage("/")
            metrics["disk"] = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            }

        if config.get("network", True):
            net_io = psutil.net_io_counters()
            metrics["network"] = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            }

        if config.get("load", True):
            metrics["load"] = {"load_avg": psutil.getloadavg()}

        return metrics

    def _collect_process_metrics(self) -> dict:
        """Collect process-specific metrics."""
        metrics = {}
        processes = self.process_config.get("processes", [])

        for proc_config in processes:
            name = proc_config["name"]
            pattern = proc_config["pattern"]
            wanted_metrics = proc_config.get("metrics", ["cpu", "memory"])

            for proc in psutil.process_iter(["name", "cmdline"]):
                try:
                    if any(pattern in " ".join(proc.cmdline()) for pattern in [pattern]):
                        proc_metrics = {}

                        if "cpu" in wanted_metrics:
                            proc_metrics["cpu_percent"] = proc.cpu_percent()

                        if "memory" in wanted_metrics:
                            mem_info = proc.memory_info()
                            proc_metrics["memory"] = {
                                "rss": mem_info.rss,
                                "vms": mem_info.vms,
                            }

                        if "threads" in wanted_metrics:
                            proc_metrics["num_threads"] = proc.num_threads()

                        if "connections" in wanted_metrics:
                            try:
                                proc_metrics["connections"] = len(proc.connections())
                            except (psutil.AccessDenied, psutil.NoSuchProcess):
                                proc_metrics["connections"] = None

                        metrics[name] = proc_metrics
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        return metrics

    def _collect_metrics(self) -> None:
        """Collect all metrics and store them."""
        try:
            # Collect metrics
            system_metrics = self._collect_system_metrics()
            process_metrics = self._collect_process_metrics()

            # Check thresholds
            thresholds = self.system_config.get("thresholds", {})

            if system_metrics.get("cpu", {}).get("percent", 0) > thresholds.get("cpu_percent", 80):
                logger.warning("CPU usage above threshold")

            if system_metrics.get("memory", {}).get("percent", 0) > thresholds.get(
                "memory_percent", 85,
            ):
                logger.warning("Memory usage above threshold")

            if system_metrics.get("disk", {}).get("percent", 0) > thresholds.get(
                "disk_percent", 90,
            ):
                logger.warning("Disk usage above threshold")

            # Store metrics
            metrics_data = {
                "timestamp": time.time(),
                "system": system_metrics,
                "processes": process_metrics,
            }

            metrics_file = os.path.join(
                self.metrics_dir, f"metrics_{int(time.time())}.json",
            )

            with open(metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)

            logger.info(f"Metrics collected and stored in {metrics_file}")

        except FileNotFoundError as e:
            if "HW_CPU_FREQ" in str(e):
                # This is an expected error on some systems where CPU frequency info is not available
                logger.debug("CPU frequency information not available on this system")
            else:
                logger.error(f"Failed to collect metrics: {e}")
                raise
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            raise

    def start(self) -> None:
        """Start collecting metrics."""
        logger.info("Starting metrics monitor...")
        try:
            while True:
                try:
                    self._collect_metrics()
                except FileNotFoundError as e:
                    if "HW_CPU_FREQ" in str(e):
                        # This is an expected error on some systems where CPU frequency info is not available
                        logger.debug("CPU frequency information not available on this system")
                    else:
                        logger.error(f"Monitor error: {e}")
                        raise
                except Exception as e:
                    logger.error(f"Monitor error: {e}")
                    raise

                # Sleep for the configured interval
                time.sleep(
                    self.system_config.get("collection_interval", 60),
                )
        except KeyboardInterrupt:
            logger.info("Stopping metrics monitor...")
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            raise


if __name__ == "__main__":
    monitor = MetricsMonitor()
    monitor.start()
