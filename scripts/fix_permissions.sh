#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1" >&2
    exit 1
}

echo "Fixing file permissions..."

# Remove executable permissions from all files
find . -type f -exec chmod -x {} + || handle_error "Failed to remove executable permissions"

# Add executable permissions back to shell scripts
find . -type f -name "*.sh" -exec chmod +x {} + || handle_error "Failed to set shell script permissions"

# Add executable permissions to Python entry point scripts if they exist
for script in run.py wsgi.py dashboard/run.py; do
    if [ -f "$script" ]; then
        chmod +x "$script" || handle_error "Failed to set permission for $script"
    fi
done

echo "✓ Permissions fixed successfully"
exit 0
