#!/bin/bash

set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Function to kill process using a port
kill_port_process() {
    local port=$1
    local pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process $pid using port $port"
        kill -9 $pid 2>/dev/null || true
    fi
}

# Kill any existing processes
echo "Cleaning up existing processes..."
sudo pkill -9 -f 'python.*flask' || true
sudo pkill -9 -f 'python.*dashboard.metrics' || true
sudo pkill -9 -f 'run_dashboard.sh' || true
sudo pkill -9 -f 'gunicorn' || true
sudo pkill -9 -f 'temp_run.py' || true

# Kill processes using required ports
kill_port_process 8000
kill_port_process 8765
kill_port_process 9090

sleep 5  # Wait longer for processes to terminate
rm -f "${PROJECT_ROOT}/.collector.pid" "${PROJECT_ROOT}/.dashboard.pid"

# Verify no existing processes
if pgrep -f 'python.*flask|python.*dashboard.metrics|run_dashboard.sh|gunicorn|temp_run.py' > /dev/null; then
    echo "Error: Failed to kill existing processes"
    exit 1
fi

# Verify ports are available
for port in 8000 8765 9090; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "Error: Port $port is still in use"
        exit 1
    fi
done

# Activate virtual environment if it exists
if [ -d "${PROJECT_ROOT}/.venv" ]; then
    source "${PROJECT_ROOT}/.venv/bin/activate"
    PYTHON="${PROJECT_ROOT}/.venv/bin/python3"
else
    PYTHON="python3"
fi

# Save original progress values
_ORIG_CURRENT_STEP=$CURRENT_STEP
_ORIG_TOTAL_STEPS=$TOTAL_STEPS

# Initialize local progress tracking
CURRENT_STEP=0
TOTAL_STEPS=5
init_progress $TOTAL_STEPS

echo "🚀 Starting dashboard..."

# Create log directory if it doesn't exist
mkdir -p "${PROJECT_ROOT}/logs"
chmod 777 "${PROJECT_ROOT}/logs"

# Check dependencies
run_with_spinner "Checking dependencies" "
    ${PYTHON} -m pip install -q flask flask-cors prometheus_client psutil pandas || true
"

# Start metrics collector
run_with_spinner "Starting metrics collector" "
    cd \"${PROJECT_ROOT}\" &&
    PYTHONPATH=\"${PROJECT_ROOT}\" ${PYTHON} -m dashboard.metrics > logs/metrics.log 2>&1 &
    echo \$! > \"${PROJECT_ROOT}/.collector.pid\" &&
    sleep 2 &&
    if ! ps -p \$(cat \"${PROJECT_ROOT}/.collector.pid\") > /dev/null; then
        echo \"Failed to start metrics collector\"
        cat logs/metrics.log
        exit 1
    fi
"

# Create a simple Flask runner script
cat > "${PROJECT_ROOT}/temp_run.py" << 'EOF'
import os
import sys
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/flask.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create a minimal Flask app for testing
app = Flask(__name__)

@app.route('/health')
def health_check():
    logger.info("Health check endpoint called")
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=8000)
EOF

chmod 755 "${PROJECT_ROOT}/temp_run.py"

# Start dashboard application
run_with_spinner "Starting dashboard application" "
    cd \"${PROJECT_ROOT}\" &&
    export PYTHONPATH=\"${PROJECT_ROOT}:\${PYTHONPATH:-}\" &&
    ${PYTHON} temp_run.py > logs/flask.log 2>&1 &
    echo \$! > \"${PROJECT_ROOT}/.dashboard.pid\" &&
    sleep 5  # Give Flask more time to start
"

# Verify services
run_with_spinner "Verifying services" "
    max_attempts=30
    attempt=0

    while [ \$attempt -lt \$max_attempts ]; do
        # Check Flask application
        if ! pgrep -f 'python.*temp_run.py' >/dev/null 2>&1; then
            echo \"Flask application failed to start. Checking logs...\"
            if [ -f logs/flask.log ]; then
                echo \"=== Flask Logs ===\"
                cat logs/flask.log
            else
                echo \"No Flask logs found\"
            fi
            exit 1
        fi

        # Check metrics collector
        if ! pgrep -f '${PYTHON} -m dashboard.metrics' >/dev/null 2>&1; then
            echo \"Metrics collector failed to start\"
            cat logs/metrics.log
            exit 1
        fi

        # Check if Flask is responding to health check
        HEALTH_CHECK=\$(curl -s http://localhost:8000/health)
        if [ \"\$HEALTH_CHECK\" = '{\"status\":\"ok\"}' ]; then
            # Both processes are running and Flask is responding
            update_progress \$((CURRENT_STEP + 1))
            break
        fi

        # If we're still here, check for specific failures
        if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo \"Flask health check failed on port 8000\"
            echo \"Latest Flask logs:\"
            tail -n 20 logs/flask.log
        fi

        sleep 1
        attempt=\$((attempt + 1))
    done

    if [ \$attempt -eq \$max_attempts ]; then
        echo \"Error: Services failed to start within \$max_attempts seconds. Check logs for details:\"
        echo \"Flask log:\"
        tail -n 50 logs/flask.log
        echo \"Metrics log:\"
        tail -n 50 logs/metrics.log
        exit 1
    fi
"

# Cleanup temporary files
rm -f "${PROJECT_ROOT}/temp_run.py"

# Final success message
echo "✨ Dashboard is running at http://localhost:8000"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

echo "✨ Dashboard is running at http://localhost:8000"

exit 0
