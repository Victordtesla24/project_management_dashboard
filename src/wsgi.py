"""WSGI application module."""
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/wsgi.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

try:
    logger.info("Creating Flask application...")
    from dashboard import create_app

    # Create Flask application
    application = create_app()
    logger.info("Flask application created successfully")
except Exception as e:
    logger.error(f"Error creating application: {e!s}", exc_info=True)
    raise

# For Flask CLI
app = application
