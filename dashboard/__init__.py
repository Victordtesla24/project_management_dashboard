"""Dashboard application package."""
import logging
import os

from flask import Flask

logger = logging.getLogger(__name__)

def create_app(test_config=None):
    """Create and configure the Flask application.
    
    Args:
        test_config: Configuration dictionary for testing.
        
    Returns:
        Flask application instance.
    """
    app = Flask(__name__)

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprints
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
