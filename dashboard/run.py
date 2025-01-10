"""Server startup script."""

import logging
import os
import sys

# Debug information
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print(
    "Environment variables:",
    {k: v for k, v in os.environ.items() if k.startswith("PYTHON") or k == "PATH"},
)

try:
    print("Attempting to import dashboard module...")
    from dashboard import create_app

    print("Successfully imported dashboard module")
except ImportError as e:
    print("Import error:", str(e))
    print("Attempting to add parent directory to Python path...")
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    print("Updated Python path:", sys.path)
    from dashboard import create_app

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "flask.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)
logger.info("Creating Flask application...")

# Create Flask application
app = create_app()
logger.info("Flask application created successfully")
