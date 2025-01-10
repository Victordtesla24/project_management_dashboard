#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Ensure logs directory exists
mkdir -p "$(dirname "${0}")/../logs"

# Flush and redirect all output to both console and log file using tee
: > "$(dirname "${0}")/../logs/setup.log"  # Truncate log file
exec > >(tee "$(dirname "${0}")/../logs/setup.log") 2>&1

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

# Create required directories
mkdir -p "$CONFIG_DIR" "$LOGS_DIR" "$REPORTS_DIR"

init_progress $TOTAL_STEPS

# Initialize base configuration
cat > "${CONFIG_DIR}/dashboard.json" << 'EOF'
{
    "metrics": {
        "collection_interval": 60,
        "enabled_metrics": ["cpu", "memory", "disk"],
        "thresholds": {
            "cpu": 80,
            "memory": 85,
            "disk": 90
        },
        "retention": {
            "days": 30,
            "max_datapoints": 10000
        },
        "alert_rules": [
            {
                "metric": "cpu",
                "threshold": 80,
                "duration": 300,
                "severity": "warning"
            }
        ],
        "aggregation": {
            "interval": 300,
            "functions": ["avg", "max", "min"]
        }
    },
    "websocket": {
        "host": "localhost",
        "port": 8765,
        "ssl": false
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "dashboard",
        "user": "dashboard",
        "password": ""
    },
    "logging": {
        "level": "INFO",
        "file": "logs/dashboard.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "ui": {
        "theme": "light",
        "refresh_interval": 10,
        "max_datapoints": 100,
        "layout": {
            "sidebar": true,
            "charts": ["cpu", "memory", "disk"]
        }
    }
}
EOF

# Error handling function
handle_error() {
    local exit_code=$?
    local line_number=$1
    echo "❌ Error on line ${line_number}: Command exited with status ${exit_code}"
    cleanup_and_exit ${exit_code}
}
trap 'handle_error ${LINENO}' ERR

# Cleanup function
cleanup_and_exit() {
    local exit_code=$1
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

    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [ "$(printf '%s\n' "3.9" "$python_version" | sort -V | head -n1)" != "3.9" ]; then
        printf "\r\033[K❌ Python 3.9+ is required (found $python_version)\n"
        exit 1
    fi

    # Check required system tools
    local required_tools=("git" "curl" "gcc" "make" "openssl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            printf "\r\033[K❌ Required tool not found: $tool\n"
            exit 1
        fi
    done

    # Check system memory
    local min_memory_mb=2048
    local available_memory
    if [[ "$OSTYPE" == "darwin"* ]]; then
        available_memory=$(sysctl -n hw.memsize | awk '{print $0/1024/1024}')
    else
        available_memory=$(free -m | awk '/^Mem:/{print $2}')
    fi

    if (( available_memory < min_memory_mb )); then
        printf "\r\033[K❌ Insufficient memory. Required: ${min_memory_mb}MB, Available: ${available_memory}MB\n"
        exit 1
    fi

    # Check disk space
    local min_space_gb=5
    local available_space
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS specific disk space check
        available_space=$(df -g . | awk 'NR==2 {print $4}')
    else
        # Linux specific disk space check
        available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
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
        rm -rf .venv
    fi

    python3 -m venv .venv
    source .venv/bin/activate

    # Upgrade pip and install wheel
    pip install --upgrade pip wheel setuptools
}

# Install dependencies function
install_dependencies() {
    # First upgrade pip and install wheel
    run_with_spinner "Upgrading pip and installing wheel" "
        python3 -m pip install --upgrade pip wheel setuptools
    "

    # Install dependencies with progress tracking
    run_with_spinner "Installing project dependencies" "
        source .venv/bin/activate &&
        python3 -m pip install -r requirements.txt &&
        python3 -m pip install -r requirements-dev.txt
    "

    # Initialize pre-commit hooks
    if [ -f ".git/hooks" ]; then
        run_with_spinner "Setting up pre-commit hooks" "
            source .venv/bin/activate &&
            pre-commit install
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

    if [ ! -f "$script" ]; then
        ((CURRENT_STEP++))
        return 0
    fi

    chmod +x "$script"

    # Export current progress, virtual environment and Python path to subscript
    export _PARENT_PROGRESS=1
    export VIRTUAL_ENV_PATH="${PROJECT_ROOT}/.venv"
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

    # Ensure virtual environment exists
    if [ ! -d "${VIRTUAL_ENV_PATH}" ]; then
        setup_virtual_environment
    fi

    # Calculate percentage based on current step (each step is 5%)
    local percentage=$((current_step * 5))
    # Ensure percentage doesn't exceed 100
    [ $percentage -gt 100 ] && percentage=100

    # Ensure virtual environment exists and is activated
    if [ ! -d "${VIRTUAL_ENV_PATH}" ]; then
        printf "\r\033[K❌ Virtual environment not found at ${VIRTUAL_ENV_PATH}\n"
        return 1
    fi

    # Run script with virtual environment and capture its output
    temp_output=$(mktemp)
    (source "${VIRTUAL_ENV_PATH}/bin/activate" 2>/dev/null && bash "$script" 2>&1 | tee "$temp_output") &
    local script_pid=$!

    # Show spinner while script is running
    while kill -0 $script_pid 2>/dev/null; do
        local spinner_char="${SPINNER_CHARS:$spinner_index:1}"
        # Clear line and print progress
        printf "\r\033[K%b%s%b Running %s %s %3d%%" \
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
        # Print final state with checkmark
        printf "\r\033[K%b✓%b %s completed successfully %s %3d%%\n" \
            "${GREEN}" "${RESET}" \
            "$message" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
        return 0
    else
        # Print final state with X and error details
        printf "\r\033[K%b✗%b %s failed %s %3d%%\n" \
            "${RED}" "${RESET}" \
            "$message" \
            "$(draw_progress_bar $percentage $BAR_WIDTH)" \
            "$percentage"
        if [ -f "$temp_output" ]; then
            printf "\nError output:\n"
            tail -n 5 "$temp_output"
            rm -f "$temp_output"
        fi
        return 1
    fi
}

# Platform-specific setup
setup_platform_specific() {
    printf "\r\033[KSkipping platform-specific package installation (optional)\n"
    printf "\r\033[KTo install required packages manually:\n"
    printf "\r\033[K- PostgreSQL\n"
    printf "\r\033[K- Redis\n"
    printf "\r\033[K- InfluxDB\n"
    printf "\r\033[KRefer to your system's package manager documentation for installation instructions.\n"
    return 0
}

# Main execution
main() {
    # Initialize failed services tracking
    declare -a failed_services=()
    export failed_services

    # Clear line and print initial message with progress bar
    printf "\r\033[K%b🚀%b Running project setup %s %3d%%" \
        "${BLUE}" "${RESET}" \
        "$(draw_progress_bar 0 $BAR_WIDTH)" \
        0
    sleep $SPINNER_DELAY  # Brief pause to show initial state

    # Core setup sequence
    run_with_spinner "Validating system requirements" validate_system_requirements || exit 1
    run_with_spinner "Setting up virtual environment" setup_virtual_environment || exit 1
    run_with_spinner "Installing dependencies" install_dependencies || exit 1
    run_with_spinner "Platform-specific setup" setup_platform_specific || exit 1

    # Install additional dependencies
    run_with_spinner "Installing additional packages" "
        source .venv/bin/activate
        pip install lxml  # Required for MyPy reporting
    "

    # Initialize configuration with error handling
    if [ -f "${PROJECT_ROOT}/dashboard/config/__init__.py" ]; then
        source "${PROJECT_ROOT}/.venv/bin/activate"
        python3 -c "
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('setup')

sys.path.insert(0, '${PROJECT_ROOT}')

try:
    from dashboard.config import init_config
    from dashboard.config.defaults import DEFAULT_CONFIG

    config_path = os.path.join('${CONFIG_DIR}', 'dashboard.json')

    if not os.path.exists(config_path):
        logger.info('Creating default configuration...')
        import json
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

    logger.info('Initializing configuration...')
    init_config(config_path)
    logger.info('Configuration initialized successfully')
except Exception as e:
    logger.error(f'Failed to initialize config: {e}')
    sys.exit(1)
"
    fi

    # Execute scripts in optimized dependency order with strict error handling
    declare -a failed_services=()

    # Group 1: Critical Environment Setup (foundational)
    printf "\n\r\033[K%b📦%b Running critical environment setup...\n" "${BLUE}" "${RESET}"

    # Environment and permissions setup with proper error handling
    for critical_setup in "setup_env:Environment" "setup_permissions:Permissions"; do
        script_name="${critical_setup%%:*}"
        display_name="${critical_setup#*:}"

        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/${script_name}.sh" "${display_name} Setup" $CURRENT_STEP; then
            printf "\r\033[K❌ Critical failure: ${display_name} setup failed. Exiting...\n"
            exit 1
        fi
    done

    # Group 2: Development Environment (depends on env and permissions)
    printf "\n\r\033[K%b📦%b Running development setup...\n" "${BLUE}" "${RESET}"

    # Type stubs should be installed before test environment
    if ! run_script_with_retry "${PROJECT_ROOT}/scripts/install_type_stubs.sh" "Type Stubs Installation" $CURRENT_STEP; then
        printf "\r\033[K❌ Failed to install type stubs. This may affect development experience.\n"
        failed_services+=("type_stubs")
    fi

    # Test environment setup depends on permissions and type stubs
    if ! run_script_with_retry "${PROJECT_ROOT}/scripts/setup_test_env.sh" "Test Environment Setup" $CURRENT_STEP; then
        printf "\r\033[K❌ Failed to setup test environment. This will affect testing capabilities.\n"
        failed_services+=("test_env")
    fi

    # Group 3: Core Services (depends on env, permissions, and dev setup)
    printf "\n\r\033[K%b📦%b Running core services setup...\n" "${BLUE}" "${RESET}"

    # Setup core services in order
    for service in "dashboard" "websocket" "monitor"; do
        service_name=$(echo "$service" | tr '[:lower:]' '[:upper:]' | cut -c1)$(echo "$service" | cut -c2-)

        # Check if dependent services failed
        case "$service" in
            "websocket")
                if printf '%s\n' "${failed_services[@]}" | grep -q '^dashboard$'; then
                    printf "\r\033[K⚠️  Skipping %s setup (dashboard service failed)\n" "$service"
                    failed_services+=("$service")
                    continue
                fi
                ;;
            "monitor")
                if printf '%s\n' "${failed_services[@]}" | grep -q '^websocket$'; then
                    printf "\r\033[K⚠️  Skipping %s setup (websocket service failed)\n" "$service"
                    failed_services+=("$service")
                    continue
                fi
                ;;
        esac

        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/setup_${service}.sh" "${service_name} Service Setup" $CURRENT_STEP; then
            printf "\r\033[K❌ Failed to setup %s service.\n" "$service"
            failed_services+=("$service")
        fi
    done

    # Group 4: Quality Assurance (depends on test environment and services)
    printf "\n\r\033[K%b📦%b Running quality checks...\n" "${BLUE}" "${RESET}"

    # Only run if test environment setup succeeded
    if [ ${#failed_services[@]} -eq 0 ] || ! printf '%s\n' "${failed_services[@]}" | grep -q '^test_env$'; then
        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/verify_and_fix.sh" "Code Verification" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Code verification failed. Some issues may need manual review.\n"
        fi

        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/lint_and_test.sh" "Linting and Testing" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Linting and testing failed. Please review test reports.\n"
        fi
    else
        printf "\r\033[K⚠️  Skipping quality checks due to test environment setup failure.\n"
        ((CURRENT_STEP+=2))
    fi

    # Group 5: Documentation (depends on successful core setup)
    printf "\n\r\033[K%b📦%b Running documentation setup...\n" "${BLUE}" "${RESET}"

    # Only proceed with documentation if core services are running
    if [ ${#failed_services[@]} -eq 0 ] || ! printf '%s\n' "${failed_services[@]}" | grep -q '^dashboard$\|^websocket$'; then
        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/create_update_docs.sh" "Documentation Generation" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Documentation generation failed. Manual documentation update may be needed.\n"
        fi

        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/sync_docs.sh" "Documentation Sync" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Documentation sync failed. Please sync documentation manually.\n"
        fi
    else
        printf "\r\033[K⚠️  Skipping documentation due to core service failures.\n"
        ((CURRENT_STEP+=2))
    fi

    # Group 6: Tracking & Demo (optional, depends on successful setup)
    printf "\n\r\033[K%b📦%b Running final steps...\n" "${BLUE}" "${RESET}"

    # Track implementation even if some services failed
    if ! run_script_with_retry "${PROJECT_ROOT}/scripts/track_implementation.sh" "Implementation Tracking" $CURRENT_STEP; then
        printf "\r\033[K⚠️  Implementation tracking failed but continuing...\n"
    fi

    # Only run demo if core services are working
    if [ ${#failed_services[@]} -eq 0 ] || ! printf '%s\n' "${failed_services[@]}" | grep -q '^dashboard$\|^websocket$'; then
        if ! run_script_with_retry "${PROJECT_ROOT}/scripts/demo_progress.sh" "Demo Setup" $CURRENT_STEP; then
            printf "\r\033[K⚠️  Demo setup failed but continuing...\n"
        fi
    else
        printf "\r\033[K⚠️  Skipping demo setup due to core service failures.\n"
        ((CURRENT_STEP++))
    fi

    # Skip GitHub sync since it's optional
    printf "\r\033[K⚠️  Skipping GitHub sync (optional)\n"
    ((CURRENT_STEP++))

    # Show final completion
    printf "\r\033[K%b✓%b Setup completed %s %3d%%\n" \
        "${GREEN}" "${RESET}" \
        "$(draw_progress_bar 100 $BAR_WIDTH)" \
        100
}

# Run main function
main "$@"
