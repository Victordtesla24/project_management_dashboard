"""Main application module."""
import contextlib
import logging
import os

from flask import Flask
from flask_cors import CORS

from .extensions import db, migrate
from .routes import bp as routes_bp

logger = logging.getLogger(__name__)


def create_app(config=None):
    """Create and configure the Flask application.

    Args:
    ----
        config: Optional configuration dictionary.

    Returns:
    -------
        Flask application instance.
    """
    app = Flask(__name__)

    # Configure app
    app.config.from_object("dashboard.config.default")
    if config:
        app.config.update(config)

    # Enable CORS
    CORS(app)

    # Ensure instance folder exists
    with contextlib.suppress(OSError):
        os.makedirs(app.instance_path)

    # Register blueprints
    app.register_blueprint(routes_bp)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    return app
