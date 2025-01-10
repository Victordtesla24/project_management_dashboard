#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Check for .env.example
if [ ! -f "${PROJECT_ROOT}/.env.example" ]; then
    handle_error ".env.example file not found"
fi

# Create or update .env file
if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    echo "Creating new .env file from .env.example..."
    cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env" || handle_error "Failed to create .env file"
else
    # Check if .env.example has been modified more recently than .env
    if [ "${PROJECT_ROOT}/.env.example" -nt "${PROJECT_ROOT}/.env" ]; then
        echo "Warning: .env.example is newer than .env"
        echo "You may want to review and update your .env file"
    fi
fi

# Validate .env file
if [ ! -s "${PROJECT_ROOT}/.env" ]; then
    handle_error ".env file is empty"
fi

echo "✓ Environment setup completed"
exit 0
