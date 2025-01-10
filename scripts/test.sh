#!/bin/bash

# Import utility functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils/common.sh"
source "$SCRIPT_DIR/utils/logger.sh"

# Function to run tests
run_tests() {
    local test_path=${1:-"dashboard/tests/test_core.py"}
    local coverage_min=${2:-70}

    log_info "Running tests..."

    # Run pytest with coverage
    pytest "$test_path" \
        --verbose \
        --cov=dashboard \
        --cov-report=term-missing \
        --cov-fail-under="$coverage_min"

    local status=$?

    if [ $status -eq 0 ]; then
        log_success "All tests passed successfully!"
    else
        log_error "Tests failed with status: $status"
    fi

    return $status
}

# Function to show help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --path PATH     Specify test path (default: dashboard/tests/test_core.py)"
    echo "  --coverage N    Minimum coverage percentage (default: 70)"
    echo "  --help         Show this help message"
}

# Main function
main() {
    # Parse arguments
    local test_path="dashboard/tests/test_core.py"
    local coverage_min=70

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --path)
                test_path="$2"
                shift 2
                ;;
            --coverage)
                coverage_min="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Check virtual environment
    check_venv || exit 1

    # Run tests
    run_tests "$test_path" "$coverage_min"
}

# Run main function with all arguments
main "$@"
