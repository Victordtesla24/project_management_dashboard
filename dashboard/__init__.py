"""Dashboard package initialization."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Default configuration
    app.config.update(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///dashboard.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
        SESSION_TYPE='filesystem',
        CORS_HEADERS='Content-Type'
    )
    
    # Override config with test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize authentication
    from .auth.middleware import init_auth
    init_auth(app)
    
    # Register blueprints
    from .routes import bp as dashboard_bp, register_health_check
    from .auth.routes import bp as auth_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    
    # Register health check endpoint at app level
    register_health_check(app)
    
    return app
