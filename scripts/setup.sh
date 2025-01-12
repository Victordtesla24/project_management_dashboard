#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"
source "${PROJECT_ROOT}/scripts/utils/common.sh"

# Initialize progress tracking and configuration
TOTAL_STEPS=19  # Adjusted for actual number of scripts and steps
CURRENT_STEP=0

# Ensure required directories exist
CONFIG_DIR="${PROJECT_ROOT}/config"
LOGS_DIR="${PROJECT_ROOT}/logs"
REPORTS_DIR="${PROJECT_ROOT}/reports"

# Create required directories silently
mkdir -p "$CONFIG_DIR" "$LOGS_DIR" "$REPORTS_DIR" >/dev/null 2>&1

init_progress $TOTAL_STEPS

# Error handling function
handle_error() {
    local exit_code=$?
    local line_number=$1
    printf "\r\033[K❌ Error on line ${line_number}: Command exited with status ${exit_code}\n" >&2
    if [ -f "$temp_output" ] && [ -s "$temp_output" ]; then
        printf "\nError details:\n" >&2
        tail -n 5 "$temp_output" >&2
        rm -f "$temp_output"
    fi
    cleanup_and_exit ${exit_code}
}
trap 'handle_error ${LINENO}' ERR

# Cleanup function
cleanup_and_exit() {
    local exit_code=$1
    # Clean up temp files
    rm -f "/tmp/setup_progress."*
    # Deactivate virtual environment if active
    if [ -n "${VIRTUAL_ENV:-}" ]; then
        deactivate 2>/dev/null || true
    fi
    exit ${exit_code}
}

# System requirements validation
validate_system_requirements() {
    # Check Python version with function from common.sh
    if ! command -v python3 >/dev/null 2>&1; then
        printf "\r\033[K❌ Python 3 not found\n"
        exit 1
    fi

    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null)
    if [ "$(printf '%s\n' "3.9" "$python_version" | sort -V | head -n1)" != "3.9" ]; then
        printf "\r\033[K❌ Python 3.9+ is required (found $python_version)\n"
        exit 1
    fi

    # Check required system tools silently
    local required_tools=("git" "curl" "gcc" "make" "openssl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            printf "\r\033[K❌ Required tool not found: $tool\n"
            exit 1
        fi
    done

    # Check system memory silently
    local min_memory_mb=2048
    local available_memory
    if [[ "$OSTYPE" == "darwin"* ]]; then
        available_memory=$(sysctl -n hw.memsize | awk '{print $0/1024/1024}' 2>/dev/null)
    else
        available_memory=$(free -m | awk '/^Mem:/{print $2}' 2>/dev/null)
    fi

    if (( available_memory < min_memory_mb )); then
        printf "\r\033[K❌ Insufficient memory. Required: ${min_memory_mb}MB, Available: ${available_memory}MB\n"
        exit 1
    fi

    # Check disk space silently
    local min_space_gb=5
    local available_space
    if [[ "$OSTYPE" == "darwin"* ]]; then
        available_space=$(df -g . | awk 'NR==2 {print $4}' 2>/dev/null)
    else
        available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//' 2>/dev/null)
    fi

    if (( available_space < min_space_gb )); then
        printf "\r\033[K❌ Insufficient disk space. Required: ${min_space_gb}GB, Available: ${available_space}GB\n"
        exit 1
    fi

    return 0
}

# Virtual environment setup
setup_virtual_environment() {
    if [ -d ".venv" ]; then
        rm -rf .venv >/dev/null 2>&1
    fi

    python3 -m venv .venv >/dev/null 2>&1
    source .venv/bin/activate >/dev/null 2>&1

    # Upgrade pip and install wheel silently
    pip install --upgrade pip wheel setuptools >/dev/null 2>&1
}

# Install dependencies function
install_dependencies() {
    # First upgrade pip and install wheel
    run_with_spinner "Upgrading pip and installing wheel" "
        python3 -m pip install --upgrade pip wheel setuptools >/dev/null 2>&1
    "

    # Install dependencies with progress tracking
    run_with_spinner "Installing project dependencies" "
        source .venv/bin/activate >/dev/null 2>&1 &&
        python3 -m pip install -r requirements.txt >/dev/null 2>&1 &&
        python3 -m pip install -r requirements-dev.txt >/dev/null 2>&1
    "

    # Initialize pre-commit hooks
    if [ -f ".git/hooks" ]; then
        run_with_spinner "Setting up pre-commit hooks" "
            source .venv/bin/activate >/dev/null 2>&1 &&
            pre-commit install >/dev/null 2>&1
        "
    fi
}

# Run script with retry logic
run_script_with_retry() {
    local script=$1
    local message=$2
    local current_step=$3
    local max_retries=3
    local retry_count=0
    local spinner_index=0
    local temp_output

    if [ ! -f "$script" ]; then
        ((CURRENT_STEP++))
        return 0
    fi

    chmod +x "$script" >/dev/null 2>&1 || {
        printf "\r\033[K❌ Failed to set execute permission on %s\n" "$script" >&2
        return 1
    }

    # Export current progress, virtual environment and Python path to subscript
    export _PARENT_PROGRESS=1
    export VIRTUAL_ENV_PATH="${PROJECT_ROOT}/.venv"
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
    export PYTHONUNBUFFERED=1
    export VERBOSE=0

    # Ensure virtual environment exists
    if [ ! -d "${VIRTUAL_ENV_PATH}" ]; then
        setup_virtual_environment >/dev/null 2>&1
    fi

    # Calculate percentage based on current step (each step is 5%)
    local percentage=$((current_step * 5))
    # Ensure percentage doesn't exceed 100
    [ $percentage -gt 100 ] && percentage=100

    # Ensure virtual environment exists and is activated
    if [ ! -d "${VIRTUAL_ENV_PATH}" ]; then
        printf "\r\033[K❌ Virtual environment not found at ${VIRTUAL_ENV_PATH}\n" >&2
        return 1
    fi

    # Run script with virtual environment and capture its output
    temp_output=$(mktemp) || {
        printf "\r\033[K❌ Failed to create temporary file\n" >&2
        return 1
    }

    {
        source "${VIRTUAL_ENV_PATH}/bin/activate" >/dev/null 2>&1
        # Redirect all output to /dev/null except errors
        exec 3>&2 # Save stderr to fd 3
        exec 2>"$temp_output" # Redirect stderr to temp file
        exec 1>/dev/null # Redirect stdout to /dev/null
        bash "$script"
        exit_status=$?
        exec 2>&3 # Restore stderr
        exit $exit_status
    } &
    local script_pid=$!

    # Show spinner while script is running
    while kill -0 $script_pid 2>/dev/null; do
        local spinner_char="${SPINNER_CHARS:$spinner_index:1}"
        # Clear line and print progress
        printf "\r\033[K%b%s%b %s %s %3d%%" \
            "${BLUE}" "$spinner_char" "${RESET}" \
            "$message" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
        spinner_index=$(( (spinner_index + 1) % ${#SPINNER_CHARS} ))
        sleep $SPINNER_DELAY
    done

    wait $script_pid
    local status=$?

    if [ $status -eq 0 ]; then
        ((CURRENT_STEP++))
        # Print final state with checkmark (without newline)
        printf "\r\033[K%b✓%b %s %s %3d%%" \
            "${GREEN}" "${RESET}" \
            "$message" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
        rm -f "$temp_output"
        return 0
    else
        # Print final state with X and error details
        printf "\r\033[K%b✗%b %s %s %3d%%" \
            "${RED}" "${RESET}" \
            "$message" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
        if [ -f "$temp_output" ] && [ -s "$temp_output" ]; then
            # Filter out INFO and DEBUG messages, only show errors
            printf "\nError output:\n" >&2
            grep -v -E "^\[(main|text)\].*INFO" "$temp_output" | grep -v "DEBUG" | grep -v "^$" >&2
        fi
        rm -f "$temp_output"
        return 1
    fi
}

# Platform-specific setup
setup_platform_specific() {
    return 0
}

# Main execution
main() {
    # Initialize failed services tracking with nounset handling
    failed_services=()
    declare -a failed_services

    # Clear line and print initial message with progress bar
    printf "\r\033[K%b🚀%b Setting up project... %s %3d%%" \
        "${BLUE}" "${RESET}" \
        "$(draw_progress_bar 0 $BAR_WIDTH)" \
        0

    # Core setup sequence
    run_with_spinner "Validating system requirements" validate_system_requirements || exit 1
    run_with_spinner "Setting up virtual environment" setup_virtual_environment || exit 1
    run_with_spinner "Installing dependencies" install_dependencies || exit 1
    run_with_spinner "Platform-specific setup" setup_platform_specific || exit 1

    # Install additional dependencies
    run_with_spinner "Installing additional packages" "
        source .venv/bin/activate >/dev/null 2>&1 &&
        pip install lxml >/dev/null 2>&1  # Required for MyPy reporting
    "

    # Initialize configuration with error handling
    if [ -f "${PROJECT_ROOT}/dashboard/config/__init__.py" ]; then
        run_with_spinner "Initializing configuration" "
            source '${PROJECT_ROOT}/.venv/bin/activate' >/dev/null 2>&1 &&
            python3 -c '
import os
import sys
import logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(\"setup\")
sys.path.insert(0, \"${PROJECT_ROOT}\")
try:
    from dashboard.config import init_config
    from dashboard.config.defaults import DEFAULT_CONFIG
    config_path = os.path.join(\"${CONFIG_DIR}\", \"dashboard.json\")
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, \"w\") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    init_config(config_path)
except Exception as e:
    logger.error(f\"Failed to initialize config: {e}\")
    sys.exit(1)
' >/dev/null 2>&1
        "
    fi

    # Execute scripts in optimized dependency order with strict error handling
    failed_services=()
    declare -a failed_services

    # Group 1: Critical Environment Setup (foundational)
    for critical_setup in "setup_env:Environment" "setup_permissions:Permissions"; do
        script_name="${critical_setup%%:*}"
        display_name="${critical_setup#*:}"

        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/${script_name}.sh" "${display_name} Setup" $CURRENT_STEP; then
            printf "\r\033[K❌ Critical failure: ${display_name} setup failed\n" >&2
            exit 1
        fi
    done

    # Group 2: Development Environment
    if ! run_script_with_retry "${PROJECT_ROOT}/scripts/install_type_stubs.sh" "Type Stubs Installation" $CURRENT_STEP; then
        printf "\r\033[K⚠️  Failed to install type stubs\n" >&2
        failed_services+=("type_stubs")
    fi

    if ! run_script_with_retry "${PROJECT_ROOT}/scripts/setup_test_env.sh" "Test Environment Setup" $CURRENT_STEP; then
        printf "\r\033[K⚠️  Failed to setup test environment\n" >&2
        failed_services+=("test_env")
    fi

    # Group 3: Core Services
    for service in "dashboard" "websocket" "monitor"; do
        service_name=$(echo "$service" | tr '[:lower:]' '[:upper:]' | cut -c1)$(echo "$service" | cut -c2-)

        # Check if dependent services failed
        case "$service" in
            "websocket")
                if [ ${#failed_services[@]} -gt 0 ] && [[ " ${failed_services[*]} " == *" dashboard "* ]]; then
                    printf "\r\033[K⚠️  Skipping %s setup (dashboard service failed)\n" "$service" >&2
                    failed_services+=("$service")
                    ((CURRENT_STEP++))
                    continue
                fi
                ;;
            "monitor")
                if [ ${#failed_services[@]} -gt 0 ] && [[ " ${failed_services[*]} " == *" websocket "* ]]; then
                    printf "\r\033[K⚠️  Skipping %s setup (websocket service failed)\n" "$service" >&2
                    failed_services+=("$service")
                    ((CURRENT_STEP++))
                    continue
                fi
                ;;
        esac

        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/setup_${service}.sh" "${service_name} Service Setup" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Failed to setup %s service\n" "$service" >&2
            failed_services+=("$service")
        fi
    done

    # Group 4: Quality Assurance
    if [ ${#failed_services[@]} -eq 0 ] || ! [[ " ${failed_services[*]} " == *" test_env "* ]]; then
        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/verify_and_fix.sh" "Code Verification" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Code verification failed\n" >&2
        fi

        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/lint_and_test.sh" "Linting and Testing" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Linting and testing failed\n" >&2
        fi
    else
        printf "\r\033[K⚠️  Skipping quality checks\n" >&2
        ((CURRENT_STEP+=2))
    fi

    # Group 5: Documentation
    if [ ${#failed_services[@]} -eq 0 ] || ! [[ " ${failed_services[*]} " == *" dashboard "* && " ${failed_services[*]} " == *" websocket "* ]]; then
        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/create_update_docs.sh" "Documentation Generation" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Documentation generation failed\n" >&2
        fi

        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/sync_docs.sh" "Documentation Sync" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Documentation sync failed\n" >&2
        fi
    else
        printf "\r\033[K⚠️  Skipping documentation\n" >&2
        ((CURRENT_STEP+=2))
    fi

    # Group 6: Tracking & Demo
    if ! run_script_with_retry "${PROJECT_ROOT}/scripts/track_implementation.sh" "Implementation Tracking" $CURRENT_STEP; then
        printf "\r\033[K⚠️  Implementation tracking failed\n" >&2
    fi

    if [ ${#failed_services[@]} -eq 0 ] || ! [[ " ${failed_services[*]} " == *" dashboard "* && " ${failed_services[*]} " == *" websocket "* ]]; then
        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/demo_progress.sh" "Demo Setup" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Demo setup failed\n" >&2
        fi
    else
        printf "\r\033[K⚠️  Skipping demo setup\n" >&2
        ((CURRENT_STEP++))
    fi

    # Skip GitHub sync
    ((CURRENT_STEP++))

    # Show final completion
    printf "\r\033[K%b✓%b Setup completed %s %3d%%\n" \
        "${GREEN}" "${RESET}" \
        "$(draw_progress_bar 100 $BAR_WIDTH)" \
        100
}

# Run main function
main "$@"

