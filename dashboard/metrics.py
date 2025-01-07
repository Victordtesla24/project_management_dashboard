"""Module for collecting and processing metrics."""

from datetime import datetime
from typing import Any, Dict

import pandas as pd
import psutil


def collect_system_metrics() -> Dict[str, Any]:
    """Collect current system metrics.

    Returns:
        Dict containing system metrics like CPU and memory usage
    """
    metrics = {
        "timestamp": datetime.now(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }
    return metrics


def process_metrics(raw_metrics: Dict[str, Any]) -> pd.DataFrame:
    """Process raw metrics into a pandas DataFrame.

    Args:
        raw_metrics: Dictionary of raw system metrics

    Returns:
        DataFrame with processed metrics
    """
    df = pd.DataFrame([raw_metrics])
    df.set_index("timestamp", inplace=True)
    return df


def get_metrics_summary() -> Dict[str, float]:
    """Get summary of current system metrics.

    Returns:
        Dict containing summary statistics
    """
    metrics = collect_system_metrics()
    return {
        "cpu_avg": metrics["cpu_percent"],
        "memory_avg": metrics["memory_percent"],
        "disk_avg": metrics["disk_percent"],
    }
