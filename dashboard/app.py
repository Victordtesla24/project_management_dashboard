"""Main application module."""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    import os
    import secrets

    # Load configuration from environment or generate secure defaults
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL") or "sqlite:///dashboard.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
        SESSION_TYPE="filesystem",
        CORS_HEADERS="Content-Type",
    )

    # Override config with test config if provided
    if test_config:
        app.config.update(test_config)

    # Enable CORS
    CORS(app)

    # Initialize database
    db.init_app(app)

    # Register health check endpoint first
    from .routes import register_health_check

    register_health_check(app)
    app.logger.info("Health check endpoint registered")

    # Then register other blueprints
    from .routes import bp as dashboard_bp

    app.register_blueprint(dashboard_bp)
    app.logger.info("Dashboard blueprint registered")

    return app
