"""Dashboard routes module."""
import logging

from flask import Blueprint, jsonify

from .metrics import MetricsCollector

logger = logging.getLogger(__name__)
bp = Blueprint("dashboard", __name__)

@bp.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

@bp.route("/metrics")
def get_metrics():
    """Get system metrics endpoint."""
    try:
        collector = MetricsCollector()
        metrics = collector.get_metrics()
        return jsonify({"status": "success", "data": metrics})
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
