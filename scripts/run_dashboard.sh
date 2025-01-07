#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Save original progress values
_ORIG_CURRENT_STEP=$CURRENT_STEP
_ORIG_TOTAL_STEPS=$TOTAL_STEPS

# Initialize local progress tracking
CURRENT_STEP=0
TOTAL_STEPS=5
init_progress $TOTAL_STEPS

echo "🚀 Starting dashboard..."

# Check dependencies
run_with_spinner "Checking dependencies" "
    python3 -m pip install -q streamlit prometheus_client psutil || true
"

# Create dashboard service
run_with_spinner "Creating dashboard service" "
    cat > \"${PROJECT_ROOT}/metrics/dashboard.service\" << EOL
[Unit]
Description=Project Management Dashboard Service
After=network.target

[Service]
Type=simple
Environment=STREAMLIT_SERVER_PORT=8000
ExecStart=/usr/local/bin/streamlit run dashboard/main.py --server.port 8000 --server.address 0.0.0.0
WorkingDirectory=${PROJECT_ROOT}
Restart=always

[Install]
WantedBy=multi-user.target
EOL
"

# Start metrics collector
run_with_spinner "Starting metrics collector" "
    python3 -m dashboard.metrics &>/dev/null &
    echo \$! > \"${PROJECT_ROOT}/.collector.pid\"
"

# Start dashboard application
run_with_spinner "Starting dashboard application" "
    cd \"${PROJECT_ROOT}\" &&
    streamlit run dashboard/main.py --server.port 8000 --server.address 0.0.0.0 &>/dev/null &
    echo \$! > \"${PROJECT_ROOT}/.dashboard.pid\"
"

# Verify services
run_with_spinner "Verifying services" "
    sleep 5 &&
    curl -s http://localhost:8000 >/dev/null &&
    pgrep -f 'python3 -m dashboard.metrics' >/dev/null
"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

echo "✨ Dashboard is running at http://localhost:8000"

exit 0
