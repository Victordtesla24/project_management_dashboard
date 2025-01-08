#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Create WebSocket config if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/config/websocket.json" ]; then
    cat > "${PROJECT_ROOT}/config/websocket.json" << EOF
{
    "port": 8765,
    "host": "localhost"
}
EOF
fi

# Ensure correct permissions
chmod 644 "${PROJECT_ROOT}/config/websocket.json"

# Verify Python dependencies
if [ -d "${PROJECT_ROOT}/.venv" ]; then
    source "${PROJECT_ROOT}/.venv/bin/activate"
    python3 -m pip install -q websockets
fi

exit 0
