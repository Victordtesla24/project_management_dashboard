#!/bin/bash

# Exit on error
set -e

# Function to check if virtual environment is active
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Error: Virtual environment not activated"
        echo "Please activate your virtual environment first:"
        echo "source .venv/bin/activate"
        exit 1
    fi
}

# Function to run unit tests
run_unit_tests() {
    echo "Running unit tests..."
    pytest dashboard/tests/unit/ \
        --verbose \
        --cov=dashboard \
        --cov-report=term-missing \
        --cov-report=html:coverage_report/unit \
        "$@"
}

# Function to run integration tests
run_integration_tests() {
    echo "Running integration tests..."
    pytest dashboard/tests/integration/ \
        --verbose \
        --cov=dashboard \
        --cov-report=term-missing \
        --cov-report=html:coverage_report/integration \
        "$@"
}

# Function to run E2E tests
run_e2e_tests() {
    echo "Running E2E tests..."
    pytest dashboard/tests/e2e/ \
        --verbose \
        --cov=dashboard \
        --cov-report=term-missing \
        --cov-report=html:coverage_report/e2e \
        "$@"
}

# Function to run all tests
run_all_tests() {
    echo "Running all tests..."
    pytest dashboard/tests/ \
        --verbose \
        --cov=dashboard \
        --cov-report=term-missing \
        --cov-report=html:coverage_report/all \
        "$@"
}

# Function to run tests with specific markers
run_marked_tests() {
    local marker=$1
    shift
    echo "Running tests marked with '$marker'..."
    pytest -m "$marker" \
        --verbose \
        --cov=dashboard \
        --cov-report=term-missing \
        --cov-report=html:coverage_report/"$marker" \
        "$@"
}

# Function to clean coverage reports
clean_coverage() {
    echo "Cleaning coverage reports..."
    rm -rf coverage_report/
    rm -f .coverage
}

# Function to show help message
show_help() {
    echo "Usage: $0 [OPTIONS] [PYTEST_ARGS...]"
    echo
    echo "Options:"
    echo "  --unit         Run unit tests only"
    echo "  --integration  Run integration tests only"
    echo "  --e2e          Run E2E tests only"
    echo "  --all          Run all tests (default)"
    echo "  --clean        Clean coverage reports"
    echo "  --marked TAG   Run tests with specific marker"
    echo "  --parallel     Run tests in parallel"
    echo "  --failed       Run only failed tests"
    echo "  --help         Show this help message"
    echo
    echo "Additional arguments are passed to pytest"
}

# Main script
main() {
    # Check if virtual environment is active
    check_venv

    # Default test type
    TEST_TYPE="all"
    PARALLEL=""
    EXTRA_ARGS=()

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --unit)
                TEST_TYPE="unit"
                shift
                ;;
            --integration)
                TEST_TYPE="integration"
                shift
                ;;
            --e2e)
                TEST_TYPE="e2e"
                shift
                ;;
            --all)
                TEST_TYPE="all"
                shift
                ;;
            --clean)
                clean_coverage
                exit 0
                ;;
            --marked)
                TEST_TYPE="marked"
                MARKER="$2"
                shift 2
                ;;
            --parallel)
                PARALLEL="-n auto"
                shift
                ;;
            --failed)
                EXTRA_ARGS+=("--lf")
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                EXTRA_ARGS+=("$1")
                shift
                ;;
        esac
    done

    # Add parallel flag if specified
    if [ -n "$PARALLEL" ]; then
        EXTRA_ARGS+=("$PARALLEL")
    fi

    # Run appropriate tests
    case "$TEST_TYPE" in
        unit)
            run_unit_tests "${EXTRA_ARGS[@]}"
            ;;
        integration)
            run_integration_tests "${EXTRA_ARGS[@]}"
            ;;
        e2e)
            run_e2e_tests "${EXTRA_ARGS[@]}"
            ;;
        marked)
            run_marked_tests "$MARKER" "${EXTRA_ARGS[@]}"
            ;;
        all)
            run_all_tests "${EXTRA_ARGS[@]}"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
