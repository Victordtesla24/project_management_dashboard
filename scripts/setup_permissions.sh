#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: Failed to set permissions for $1"
    exit 1
}

# Logging function
log_message() {
    local level=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message"
}

# Set directory permissions recursively
log_message "INFO" "Setting directory permissions..."
find "${PROJECT_ROOT}" -type d -exec chmod 755 {} \; 2>/dev/null || {
    log_message "ERROR" "Failed to set directory permissions"
    handle_error "directory permissions"
}

# Set file permissions with error handling and logging
set_permissions() {
    local pattern=$1
    local perms=$2
    local type=$3
    log_message "INFO" "Setting $type files ($pattern) to $perms..."
    find "${PROJECT_ROOT}" -type f -name "$pattern" -exec chmod "$perms" {} + 2>/dev/null || {
        log_message "ERROR" "Failed to set permissions for $pattern files"
        handle_error "$pattern files"
    }
}

# Executable files
set_permissions "*.sh" 755 "script"
set_permissions "*.py" 644 "python"

# Configuration files
set_permissions "*.json" 644 "configuration"
set_permissions "*.yaml" 644 "configuration"
set_permissions "*.yml" 644 "configuration"
set_permissions "*.ini" 644 "configuration"
set_permissions "*.conf" 644 "configuration"

# Documentation files
set_permissions "*.md" 644 "documentation"
set_permissions "*.rst" 644 "documentation"

# Log files
set_permissions "*.log" 644 "log"

# Special files with logging
log_message "INFO" "Setting permissions for special files..."

# Environment files
if [ -f "${PROJECT_ROOT}/.env" ]; then
    chmod 600 "${PROJECT_ROOT}/.env" 2>/dev/null || {
        log_message "ERROR" "Failed to set permissions for .env file"
        handle_error ".env"
    }
    log_message "INFO" "Set .env permissions to 600"
fi

if [ -f "${PROJECT_ROOT}/.env.example" ]; then
    chmod 644 "${PROJECT_ROOT}/.env.example" 2>/dev/null || {
        log_message "ERROR" "Failed to set permissions for .env.example file"
        handle_error ".env.example"
    }
    log_message "INFO" "Set .env.example permissions to 644"
fi

# Ensure log directory is writable
if [ -d "${PROJECT_ROOT}/logs" ]; then
    chmod 775 "${PROJECT_ROOT}/logs" 2>/dev/null || {
        log_message "ERROR" "Failed to set permissions for logs directory"
        handle_error "logs directory"
    }
    log_message "INFO" "Set logs directory permissions to 775"
fi

log_message "INFO" "All permissions set successfully"
exit 0
