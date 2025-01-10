"""Dashboard routes module."""
import logging

from flask import Blueprint, jsonify, render_template, request

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


@bp.route("/monitor")
def monitor():
    """System monitor page."""
    try:
        error = request.args.get("error", False)
        if error:
            return render_template("monitor.html", error=True)

        collector = MetricsCollector()
        metrics = collector.get_metrics()
        return render_template("monitor.html", metrics=metrics)
    except Exception as e:
        logger.error(f"Error in monitor view: {e}")
        return render_template("monitor.html", error=True)


@bp.route("/workflow")
def workflow():
    """Workflow page."""
    try:
        error = request.args.get("trigger_error", False)
        if error:
            return render_template("workflow.html", error=True)
        return render_template("workflow.html")
    except Exception as e:
        logger.error(f"Error in workflow view: {e}")
        return render_template("workflow.html", error=True)
