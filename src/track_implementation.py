"""Implementation tracking module."""
import json
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def load_metrics(filepath):
    """Load metrics from a JSON file."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Metrics file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding metrics file {filepath}: {e}")
        return {}
    except OSError as e:
        logger.error(f"IO error reading metrics file {filepath}: {e}")
        return {}


def save_metrics(metrics, filepath):
    """Save metrics to a JSON file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=4)
        logger.info(f"Metrics saved to {filepath}")
    except OSError as e:
        logger.error(f"Error saving metrics to {filepath}: {e}")


def track_implementation_progress(metrics):
    """Track implementation progress by saving metrics to a file."""
    try:
        timestamp = datetime.now().isoformat()
        metrics_dir = Path("tracking/history")
        metrics_dir.mkdir(parents=True, exist_ok=True)

        # Save current metrics
        current_metrics_file = metrics_dir / f"metrics_{timestamp}.json"
        save_metrics(metrics, current_metrics_file)

        # Update implementation metrics
        implementation_file = Path("tracking/implementation_metrics.json")
        implementation_metrics = load_metrics(implementation_file)

        # Update metrics with timestamp
        metrics["timestamp"] = timestamp
        implementation_metrics["history"] = implementation_metrics.get("history", [])
        implementation_metrics["history"].append(metrics)
        implementation_metrics["latest"] = metrics

        # Save updated implementation metrics
        save_metrics(implementation_metrics, implementation_file)

        logger.info("Implementation progress tracked successfully")
        return True
    except Exception as e:
        logger.error(f"Error tracking implementation progress: {e}")
        return False


def get_implementation_status():
    """Get the current implementation status."""
    try:
        implementation_file = Path("tracking/implementation_metrics.json")
        return load_metrics(implementation_file)
    except Exception as e:
        logger.error(f"Error getting implementation status: {e}")
        return {}
