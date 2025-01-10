"""Dashboard package initialization."""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    """Create and configure the app."""
    app = Flask(__name__, instance_relative_config=True)

    # Initialize configuration if not already initialized
    from .config import _config_manager, init_config

    if _config_manager is None:
        init_config()  # This will use default config path

    # Default configuration
    app.config.update(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///dashboard.db",
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

    # Register blueprints in order (auth must be registered before dashboard)
    from .auth.routes import bp as auth_bp
    from .routes import bp as dashboard_bp
    from .routes import register_health_check

    # Register health check first
    if "health" not in app.blueprints:
        register_health_check(app)

    # Register auth blueprint before dashboard
    if "auth" not in app.blueprints:
        app.register_blueprint(auth_bp)

    # Register dashboard blueprint last
    if "dashboard" not in app.blueprints:
        app.register_blueprint(dashboard_bp)

    return app
