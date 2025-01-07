"""Utility functions for the dashboard."""

import json
import os
from pathlib import Path
from typing import Any, Dict


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file.

    Args:
        config_path: Path to config JSON file

    Returns:
        Dict containing configuration
    """
    with open(config_path) as f:
        return json.load(f)


def get_data_dir() -> Path:
    """Get path to data directory.

    Returns:
        Path object for data directory
    """
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    data_dir.mkdir(exist_ok=True)
    return data_dir


def format_metric(value: float, precision: int = 2) -> str:
    """Format metric value as string.

    Args:
        value: Metric value to format
        precision: Number of decimal places

    Returns:
        Formatted string
    """
    return f"{value:.{precision}f}%"
