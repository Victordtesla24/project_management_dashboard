#!/bin/bash

set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Kill any existing processes
pkill -f 'python.*flask' || true
pkill -f 'python.*dashboard.metrics' || true
pkill -f 'run_dashboard.sh' || true
sleep 2  # Wait for processes to terminate
rm -f "${PROJECT_ROOT}/.collector.pid" "${PROJECT_ROOT}/.dashboard.pid"

# Verify no existing processes
if pgrep -f 'python.*flask|python.*dashboard.metrics|run_dashboard.sh' > /dev/null; then
    echo "Error: Failed to kill existing processes"
    exit 1
fi

# Wait for ports to be available with timeout
timeout=30
elapsed=0
while lsof -i :8000 >/dev/null 2>&1 || lsof -i :8765 >/dev/null 2>&1 || lsof -i :9090 >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        echo "Error: Timeout waiting for ports 8000, 8765, and 9090 to be available"
        exit 1
    fi
    echo "Waiting for ports 8000, 8765, and 9090 to be available..."
    sleep 1
    elapsed=$((elapsed + 1))
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

# Check dependencies
run_with_spinner "Checking dependencies" "
    ${PYTHON} -m pip install -q flask flask-cors prometheus_client psutil pandas || true
"

# Start metrics collector
run_with_spinner "Starting metrics collector" "
    cd \"${PROJECT_ROOT}\" &&
    ${PYTHON} -m dashboard.metrics > logs/metrics.log 2>&1 &
    echo \$! > \"${PROJECT_ROOT}/.collector.pid\"
"

# Start dashboard application
run_with_spinner "Starting dashboard application" "
    cd \"${PROJECT_ROOT}\" &&
    export PYTHONPATH=\"${PROJECT_ROOT}:\${PYTHONPATH:-}\" &&
    export FLASK_APP=dashboard.app &&
    export FLASK_DEBUG=0 &&
    ${PYTHON} -m flask run --host=0.0.0.0 --port=8000 > logs/flask.log 2>&1 &
    echo \$! > \"${PROJECT_ROOT}/.dashboard.pid\"
"

# Verify services
run_with_spinner "Verifying services" "
    max_attempts=30
    attempt=0
    
    while [ \$attempt -lt \$max_attempts ]; do
        # Check Flask application
        if ! pgrep -f '${PYTHON} -m flask run' >/dev/null 2>&1; then
            echo \"Flask application failed to start\"
            cat logs/flask.log
            exit 1
        fi
        
        # Check metrics collector
        if ! pgrep -f '${PYTHON} -m dashboard.metrics' >/dev/null 2>&1; then
            echo \"Metrics collector failed to start\"
            cat logs/metrics.log
            exit 1
        fi
        
        # Check if Flask is responding to health check
        HEALTH_CHECK=$(curl -s http://localhost:8000/health)
        if [ "$HEALTH_CHECK" = '{"status":"ok"}' ]; then
            # Both processes are running and Flask is responding
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

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

echo "✨ Dashboard is running at http://localhost:8000"

exit 0
