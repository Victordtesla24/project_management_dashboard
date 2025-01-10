from functools import wraps

import jwt
from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from dashboard.auth.middleware import create_token, verify_token

bp = Blueprint("dashboard", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("auth_token")
        if not token:
            return redirect(url_for("auth.login"))
        try:
            verify_token(token)
        except jwt.InvalidTokenError:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/")
@login_required
def index():
    return render_template("index.html")


@bp.route("/metrics")
@login_required
def metrics():
    return render_template("metrics.html")


@bp.route("/api/metrics")
@login_required
def get_metrics():
    try:
        from dashboard.core_scripts.metrics_collector import MetricsCollector

        collector = MetricsCollector()
        system_metrics = collector.collect_system_metrics()
        project_metrics = collector.collect_project_metrics()
        return jsonify({**system_metrics, **project_metrics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


def register_health_check(app):
    """Register health check endpoint with the app."""
    app.register_blueprint(bp)
