"""Tests for metrics module."""

import unittest
from datetime import datetime

from dashboard.metrics import (
    collect_system_metrics,
    get_metrics_summary,
    process_metrics,
)


class TestMetrics(unittest.TestCase):
    """Test cases for metrics module."""

    def test_collect_system_metrics(self):
        """Test collecting system metrics."""
        metrics = collect_system_metrics()

        self.assertIsInstance(metrics["timestamp"], datetime)
        self.assertIsInstance(metrics["cpu_percent"], float)
        self.assertIsInstance(metrics["memory_percent"], float)
        self.assertIsInstance(metrics["disk_percent"], float)

        self.assertGreaterEqual(metrics["cpu_percent"], 0)
        self.assertLessEqual(metrics["cpu_percent"], 100)

    def test_process_metrics(self):
        """Test processing raw metrics."""
        raw_metrics = {
            "timestamp": datetime.now(),
            "cpu_percent": 50.0,
            "memory_percent": 60.0,
            "disk_percent": 70.0,
        }

        df = process_metrics(raw_metrics)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.index.name, "timestamp")

    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        summary = get_metrics_summary()

        self.assertIsInstance(summary["cpu_avg"], float)
        self.assertIsInstance(summary["memory_avg"], float)
        self.assertIsInstance(summary["disk_avg"], float)


if __name__ == "__main__":
    unittest.main()
