#!/bin/bash
set -euo pipefail

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Python virtual environment
VENV_DIR="${PROJECT_ROOT}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

# Constants
MAX_RETRIES=3
RETRY_DELAY=5

# Color codes for logging
COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${COLOR_BLUE}INFO: $1${COLOR_NC}"
}

log_warning() {
    echo -e "${COLOR_YELLOW}WARNING: $1${COLOR_NC}" >&2
}

log_error() {
    echo -e "${COLOR_RED}ERROR: $1${COLOR_NC}" >&2
}

log_success() {
    echo -e "${COLOR_GREEN}SUCCESS: $1${COLOR_NC}"
}

# Error handling function
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "Failed at line ${line_number} with exit code ${exit_code}"
    return ${exit_code}
}

# Trap errors
trap 'handle_error ${LINENO}' ERR

# Ensure virtual environment exists with proper error handling
ensure_venv() {
    if [[ ! -d "${VENV_DIR}" ]]; then
        log_info "Creating virtual environment..."
        if ! command -v python3 &> /dev/null; then
            log_error "Python 3 is not installed"
            return 1
        fi

        if ! python3 -m venv "${VENV_DIR}"; then
            log_error "Failed to create virtual environment"
            return 1
        fi

        if ! "${VENV_PYTHON}" -m pip install --upgrade pip; then
            log_error "Failed to upgrade pip"
            return 1
        fi
    fi

    # Verify virtual environment
    if ! "${VENV_PYTHON}" --version &> /dev/null; then
        log_error "Virtual environment verification failed"
        return 1
    fi

    return 0
}

# Check if a Python package is installed
check_package() {
    local package_name=$1
    "${VENV_PYTHON}" -m pip show "${package_name}" &> /dev/null
}

# Install a Python package with retry logic
install_package() {
    local package_name=$1
    local retry_count=0

    while [[ ${retry_count} -lt ${MAX_RETRIES} ]]; do
        if "${VENV_PYTHON}" -m pip install "${package_name}"; then
            log_success "Installed ${package_name}"
            return 0
        fi
        retry_count=$((retry_count + 1))
        log_warning "Failed to install ${package_name}, attempt ${retry_count} of ${MAX_RETRIES}"
        sleep "${RETRY_DELAY}"
    done

    log_error "Failed to install ${package_name} after ${MAX_RETRIES} attempts"
    return 1
}

# Create backup of a file or directory
create_backup() {
    local path=$1
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="${PROJECT_ROOT}/backups/${timestamp}"

    if [[ ! -e "${path}" ]]; then
        log_error "Path does not exist: ${path}"
        return 1
    fi

    mkdir -p "${backup_dir}" || {
        log_error "Failed to create backup directory"
        return 1
    }

    if cp -r "${path}" "${backup_dir}/"; then
        log_success "Created backup of ${path} in ${backup_dir}"
        return 0
    else
        log_error "Failed to create backup of ${path}"
        return 1
    fi
}

# Verify required commands are available
verify_command() {
    local cmd=$1
    if ! command -v "${cmd}" &> /dev/null; then
        log_error "Required command not found: ${cmd}"
        return 1
    fi
    return 0
}

# Export variables
export PROJECT_ROOT
export VENV_DIR
export VENV_PYTHON
export MAX_RETRIES
export RETRY_DELAY
