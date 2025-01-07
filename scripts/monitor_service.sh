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

echo "🔍 Setting up monitoring service..."

# Create monitoring directories
run_with_spinner "Creating monitoring directories" "
    mkdir -p \"${PROJECT_ROOT}/metrics\" &&
    mkdir -p \"${PROJECT_ROOT}/logs\"
"

# Create service file
run_with_spinner "Creating service file" "
    cat > \"${PROJECT_ROOT}/metrics/monitor.service\" << EOL
[Unit]
Description=Project Management Dashboard Monitoring Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -m dashboard.monitor
WorkingDirectory=${PROJECT_ROOT}
Restart=always

[Install]
WantedBy=multi-user.target
EOL
"

# Install dependencies
run_with_spinner "Installing dependencies" "
    python3 -m pip install -q prometheus_client psutil || true
"

# Start monitoring service
run_with_spinner "Starting monitoring service" "
    python3 -m dashboard.monitor &>/dev/null &
"

# Verify service status
run_with_spinner "Verifying service status" "
    sleep 2 &&
    pgrep -f 'python3 -m dashboard.monitor' >/dev/null
"

# Restore original progress values
CURRENT_STEP=$_ORIG_CURRENT_STEP
TOTAL_STEPS=$_ORIG_TOTAL_STEPS
export CURRENT_STEP TOTAL_STEPS

exit 0
