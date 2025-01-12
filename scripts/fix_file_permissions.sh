#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1" >&2
    exit 1
}

echo "Setting file permissions..."

# Combine multiple file type permissions into a single find command for better performance
find . \( \
    -name "*.py" -o \
    -name "*.json" -o \
    -name "*.yaml" -o \
    -name "*.yml" -o \
    -name "*.md" -o \
    -name "*.html" -o \
    -name "*.css" -o \
    -name "*.js" -o \
    -name "*.rst" -o \
    -name "*.txt" -o \
    -name "*.ini" -o \
    -name "*.service" \
    \) -type f -exec chmod 644 {} + || handle_error "Failed to set regular file permissions"

# Set executable permissions for shell scripts
find . -type f -name "*.sh" -exec chmod 755 {} + || handle_error "Failed to set shell script permissions"

# Set specific file permissions efficiently
for file in .env.example .gitignore .flake8 .bandit.yaml .pre-commit-config.yaml .clinerules; do
    if [ -f "$file" ]; then
        chmod 644 "$file" || handle_error "Failed to set permission for $file"
    fi
done

# Set directory permissions in a single command
find . -type d -exec chmod 755 {} + || handle_error "Failed to set directory permissions"

# Ensure logs directory exists and has correct permissions
mkdir -p logs || handle_error "Failed to create logs directory"
chmod 775 logs || handle_error "Failed to set logs directory permissions"

echo "✓ File permissions set successfully"
exit 0
