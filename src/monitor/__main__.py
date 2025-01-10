"""Main entry point for the monitor module."""
from monitor import MetricsMonitor


def main():
    """Run the metrics monitor."""
    monitor = MetricsMonitor()
    monitor.start()


if __name__ == "__main__":
    main()
