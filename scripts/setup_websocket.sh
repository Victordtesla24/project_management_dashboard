#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Check for websocket config example
if [ ! -f "${PROJECT_ROOT}/config/websocket.json.example" ]; then
    handle_error "websocket.json.example not found"
fi

# Create websocket config if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/config/websocket.json" ]; then
    echo "Creating websocket configuration..."
    cp "${PROJECT_ROOT}/config/websocket.json.example" "${PROJECT_ROOT}/config/websocket.json" || \
        handle_error "Failed to create websocket.json"
else
    # Check if example config is newer
    if [ "${PROJECT_ROOT}/config/websocket.json.example" -nt "${PROJECT_ROOT}/config/websocket.json" ]; then
        echo "Warning: websocket.json.example is newer than websocket.json"
        echo "You may want to review and update your configuration"
    fi
fi

# Validate websocket config
if [ ! -s "${PROJECT_ROOT}/config/websocket.json" ]; then
    handle_error "websocket.json is empty"
fi

# Create required websocket directories
echo "Setting up websocket directory structure..."
directories=(
    "websocket/handlers"
    "websocket/middleware"
    "websocket/utils"
)

for dir in "${directories[@]}"; do
    full_path="${PROJECT_ROOT}/${dir}"
    mkdir -p "$full_path" || handle_error "Failed to create $dir directory"

    # Add .gitkeep to preserve empty directories
    touch "$full_path/.gitkeep" 2>/dev/null || true
done

# Create default handler if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/websocket/handlers/__init__.py" ]; then
    echo "Creating default websocket handler..."
    cat > "${PROJECT_ROOT}/websocket/handlers/__init__.py" << 'EOF' || handle_error "Failed to create default handler"
"""WebSocket handlers package."""

class WebSocketHandler:
    """Base WebSocket handler."""

    async def on_connect(self, websocket):
        """Handle client connection."""
        pass

    async def on_disconnect(self, websocket):
        """Handle client disconnection."""
        pass

    async def on_message(self, websocket, message):
        """Handle incoming message."""
        pass
EOF
fi

# Create default middleware if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/websocket/middleware/__init__.py" ]; then
    echo "Creating default websocket middleware..."
    cat > "${PROJECT_ROOT}/websocket/middleware/__init__.py" << 'EOF' || handle_error "Failed to create default middleware"
"""WebSocket middleware package."""

class WebSocketMiddleware:
    """Base WebSocket middleware."""

    async def process_request(self, websocket, next_handler):
        """Process incoming request."""
        return await next_handler(websocket)

    async def process_message(self, websocket, message, next_handler):
        """Process incoming message."""
        return await next_handler(websocket, message)
EOF
fi

# Create default utils if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/websocket/utils/__init__.py" ]; then
    echo "Creating default websocket utils..."
    cat > "${PROJECT_ROOT}/websocket/utils/__init__.py" << 'EOF' || handle_error "Failed to create default utils"
"""WebSocket utilities package."""

import json
from typing import Any, Dict, Optional

def parse_message(message: str) -> Optional[Dict[str, Any]]:
    """Parse incoming WebSocket message."""
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return None

def format_message(data: Dict[str, Any]) -> str:
    """Format outgoing WebSocket message."""
    return json.dumps(data)
EOF
fi

echo "✓ WebSocket setup completed"
exit 0
