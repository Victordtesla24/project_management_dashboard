#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Validation function
validate_source() {
    local source=$1
    local type=$2
    if [ ! -f "$source" ]; then
        handle_error "Source $type not found: $source"
    fi
}

# Create documentation directory structure
echo "Setting up documentation directory structure..."
directories=(
    "build"
    "source/_static"
    "source/_templates"
    "api"
    "guides"
    "guides/user"
    "guides/developer"
    "guides/deployment"
)

for dir in "${directories[@]}"; do
    full_path="${PROJECT_ROOT}/docs/${dir}"
    mkdir -p "$full_path" || handle_error "Failed to create $dir directory"
done

# Sync documentation files
echo "Synchronizing documentation files..."

# Function to sync a file with backup
sync_file() {
    local source=$1
    local dest=$2
    local type=$3

    # Validate source exists
    validate_source "$source" "$type"

    # Create backup if destination exists
    if [ -f "$dest" ]; then
        cp "$dest" "${dest}.backup" || handle_error "Failed to create backup of $type"
    fi

    # Copy file
    cp "$source" "$dest" || handle_error "Failed to sync $type"
    echo "✓ Synced $type"
}

# Sync configuration files
sync_file "${PROJECT_ROOT}/docs_latest/conf.py" "${PROJECT_ROOT}/docs/source/conf.py" "configuration"
sync_file "${PROJECT_ROOT}/docs_latest/index.rst" "${PROJECT_ROOT}/docs/source/index.rst" "index"

# Sync guide files
guide_files=(
    "user_guide/index.rst:guides/user/index.rst"
    "developer_guide/index.rst:guides/developer/index.rst"
    "installation.rst:guides/deployment/installation.rst"
    "usage.rst:guides/user/usage.rst"
)

for file_pair in "${guide_files[@]}"; do
    source_file="${PROJECT_ROOT}/docs_latest/${file_pair%%:*}"
    dest_file="${PROJECT_ROOT}/docs/${file_pair#*:}"

    if [ -f "$source_file" ]; then
        sync_file "$source_file" "$dest_file" "guide $(basename "$source_file")"
    fi
done

# Sync API documentation if it exists
if [ -d "${PROJECT_ROOT}/docs_latest/api" ]; then
    echo "Synchronizing API documentation..."
    rsync -av --delete \
        "${PROJECT_ROOT}/docs_latest/api/" \
        "${PROJECT_ROOT}/docs/api/" || handle_error "Failed to sync API documentation"
fi

# Set permissions
echo "Setting documentation permissions..."
find "${PROJECT_ROOT}/docs" -type d -exec chmod 755 {} \;
find "${PROJECT_ROOT}/docs" -type f -exec chmod 644 {} \;

# Clean up old backups
echo "Cleaning up old backups..."
find "${PROJECT_ROOT}/docs" -name "*.backup" -type f -mtime +7 -delete

# Verify synchronization
echo "Verifying documentation synchronization..."
verification_failed=0

verify_file() {
    local file=$1
    if [ ! -f "$file" ]; then
        echo "⚠️  Missing file: $file"
        verification_failed=1
    fi
}

verify_file "${PROJECT_ROOT}/docs/source/conf.py"
verify_file "${PROJECT_ROOT}/docs/source/index.rst"
verify_file "${PROJECT_ROOT}/docs/guides/user/index.rst"

if [ $verification_failed -eq 1 ]; then
    echo "⚠️  Some documentation files are missing"
    exit 1
fi

echo "✓ Documentation synchronization completed"
exit 0
