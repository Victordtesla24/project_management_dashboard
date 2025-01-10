"""Default configuration."""
import os

# Flask
SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
DEBUG = True

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = "sqlite:///instance/dashboard.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application
MONITOR_REFRESH_INTERVAL = 5  # seconds
