"""Metrics collector module for the dashboard."""

import logging

from prometheus_client import CollectorRegistry, Counter, Gauge, start_http_server


class MetricsCollector:
    """Collect and expose project management metrics."""

    def __init__(self, port: int = 8000) -> None:
        """Initialize metrics collector with a custom registry."""
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create a custom registry for this instance
        self.registry = CollectorRegistry()

        # Initialize metrics
        self._init_metrics()

        # Start Prometheus HTTP server
        try:
            start_http_server(port, registry=self.registry)
            self.logger.info(f"Metrics server started on port {port}")
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")

    def _init_metrics(self) -> None:
        """Initialize Prometheus metrics."""
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

    def get_active_tasks_count(self) -> int:
        """Get the current number of active tasks."""
        count = 5  # Simulated value for demonstration
        self.active_tasks.set(count)
        return count

    def get_completed_tasks_count(self) -> int:
        """Get the total number of completed tasks."""
        count = 10  # Simulated value for demonstration
        self.completed_tasks.inc()
        return count

    def get_team_velocity(self) -> float:
        """Get the current team velocity."""
        velocity = 15.5  # Simulated value for demonstration
        self.team_velocity.set(velocity)
        return velocity

    def get_sprint_progress(self) -> float:
        """Get the current sprint progress percentage."""
        progress = 75.0  # Simulated value for demonstration
        self.sprint_progress.set(progress)
        return progress
