"""Flask application runner."""
import logging
import os
import sys

from dashboard.app import create_app

app = create_app()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/flask.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting Flask application...")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")

    # Import the Flask app from wsgi.py
    logger.info("Successfully imported app from wsgi")
    app.run(host="0.0.0.0", port=8000, debug=True)
except Exception as e:
    logger.error(f"Error starting application: {e!s}", exc_info=True)
    sys.exit(1)
