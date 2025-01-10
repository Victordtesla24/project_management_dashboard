"""Temporary Flask application for testing."""
import logging

from flask import Flask, jsonify  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/health")
def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint called")
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    logger.info("Starting Flask application...")
    app.run(host="0.0.0.0", port=8000)
