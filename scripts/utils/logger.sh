#!/bin/bash

# Enable strict mode
set -euo pipefail
IFS=$'\n\t'

# Colors for output
COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m'

# Log levels
LOG_LEVEL_DEBUG=0
LOG_LEVEL_INFO=1
LOG_LEVEL_WARN=2
LOG_LEVEL_ERROR=3

# Current log level (default: INFO)
CURRENT_LOG_LEVEL=${LOG_LEVEL:-1}

# Logging functions
log_debug() {
    if [[ $CURRENT_LOG_LEVEL -le $LOG_LEVEL_DEBUG ]]; then
        echo -e "${COLOR_BLUE}[DEBUG] $1${COLOR_NC}" >&2
    fi
}

log_info() {
    if [[ $CURRENT_LOG_LEVEL -le $LOG_LEVEL_INFO ]]; then
        echo -e "${COLOR_GREEN}[INFO] $1${COLOR_NC}" >&2
    fi
}

log_warn() {
    if [[ $CURRENT_LOG_LEVEL -le $LOG_LEVEL_WARN ]]; then
        echo -e "${COLOR_YELLOW}[WARN] $1${COLOR_NC}" >&2
    fi
}

log_error() {
    if [[ $CURRENT_LOG_LEVEL -le $LOG_LEVEL_ERROR ]]; then
        echo -e "${COLOR_RED}[ERROR] $1${COLOR_NC}" >&2
    fi
}

# File logging
log_to_file() {
    local level=$1
    local message=$2
    local log_file="${PROJECT_ROOT}/logs/dashboard.log"

    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$log_file")"

    # Append log message with timestamp
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$log_file"
}

# Export functions
export -f log_debug
export -f log_info
export -f log_warn
export -f log_error
export -f log_to_file
