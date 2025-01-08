"""Metrics collector module for the dashboard."""

import logging
import time
import psutil
from typing import Dict, Any
from datetime import datetime, timedelta

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, start_http_server
import os
import json

def get_config():
    """Get configuration from config file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'dashboard.json')
    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        return {"retention_days": 30, "metrics_port": 8000}  # Default config


class MetricsCollector:
    """Collect and expose project management metrics."""

    def __init__(self, port: int = 9090, retention_days: int = 30) -> None:
        """Initialize metrics collector with a custom registry."""
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Load configuration
        try:
            self.config = get_config()
            self.retention_days = self.config.get('retention_days', retention_days)
        except Exception as e:
            self.logger.warning(f"Failed to load config, using defaults: {e}")
            self.retention_days = retention_days
        self.last_cleanup = datetime.now()

        # Create a custom registry for this instance
        self.registry = CollectorRegistry()

        # Initialize metrics
        self._init_metrics()

        # Start Prometheus HTTP server
        try:
            metrics_port = self.config.get('metrics_port', port)
            start_http_server(metrics_port, registry=self.registry)
            self.logger.info(f"Metrics server started on port {port}")
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")
            raise

    def _init_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        # Project metrics
        self.active_tasks = Gauge(
            "active_tasks",
            "Number of active tasks",
            registry=self.registry,
        )
        self.completed_tasks = Counter(
            "completed_tasks",
            "Number of completed tasks",
            registry=self.registry,
        )
        self.team_velocity = Gauge(
            "team_velocity",
            "Team velocity in story points",
            registry=self.registry,
        )
        self.sprint_progress = Gauge(
            "sprint_progress",
            "Sprint progress percentage",
            registry=self.registry,
        )

        # System metrics
        self.cpu_usage = Gauge(
            "cpu_usage_percent",
            "CPU usage percentage",
            registry=self.registry,
        )
        self.memory_usage = Gauge(
            "memory_usage_percent",
            "Memory usage percentage",
            registry=self.registry,
        )
        self.disk_usage = Gauge(
            "disk_usage_percent",
            "Disk usage percentage",
            registry=self.registry,
        )

        # Performance metrics
        self.response_time = Histogram(
            "response_time_seconds",
            "Response time in seconds",
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0),
            registry=self.registry,
        )

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.percent)

            # Disk usage
            disk = psutil.disk_usage('/')
            self.disk_usage.set(disk.percent)

            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {}

    def collect_project_metrics(self) -> Dict[str, Any]:
        """Collect project metrics."""
        try:
            # Here you would integrate with your project management system
            # For now using sample data
            active = 5
            completed = 10
            velocity = 15.5
            progress = 75.0

            self.active_tasks.set(active)
            self.completed_tasks.inc()
            self.team_velocity.set(velocity)
            self.sprint_progress.set(progress)

            return {
                'active_tasks': active,
                'completed_tasks': completed,
                'team_velocity': velocity,
                'sprint_progress': progress,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error collecting project metrics: {e}")
            return {}

    def cleanup_old_metrics(self) -> None:
        """Clean up metrics older than retention period."""
        try:
            if (datetime.now() - self.last_cleanup).days >= 1:
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                # Here you would implement cleanup logic for your storage backend
                self.last_cleanup = datetime.now()
                self.logger.info(f"Cleaned up metrics older than {cutoff_date}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}")

    def record_response_time(self, duration: float) -> None:
        """Record response time metric."""
        try:
            self.response_time.observe(duration)
        except Exception as e:
            self.logger.error(f"Error recording response time: {e}")
