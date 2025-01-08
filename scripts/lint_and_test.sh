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

# Function to run black formatter
run_black() {
    echo "Running black formatter..."
    black dashboard tests --check --diff --line-length=100
}

# Function to run isort
run_isort() {
    echo "Running isort..."
    isort dashboard tests --check-only --diff --profile=black --line-length=100
}

# Function to run flake8
run_flake8() {
    echo "Running flake8..."
    flake8 dashboard tests
}

# Function to run mypy
run_mypy() {
    echo "Running mypy..."
    mypy dashboard
}

# Function to run bandit
run_bandit() {
    echo "Running bandit security checks..."
    bandit -r dashboard -c .bandit.yaml
}

# Function to run unit tests
run_tests() {
    echo "Running unit tests..."
    pytest dashboard/tests/unit/ \
        --quiet \
        --cov=dashboard \
        --cov-report=term-missing \
        --cov-fail-under=80
}

# Function to show summary
show_summary() {
    local status=$1
    echo
    if [ $status -eq 0 ]; then
        echo "All checks passed successfully!"
    else
        echo "Some checks failed. Please fix the issues and try again."
    fi
}

# Function to run all checks
run_all_checks() {
    local status=0
    
    # Run each check and capture status
    run_black || status=$?
    run_isort || status=$?
    run_flake8 || status=$?
    run_mypy || status=$?
    run_bandit || status=$?
    run_tests || status=$?
    
    return $status
}

# Function to show help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --black       Run black formatter only"
    echo "  --isort       Run isort only"
    echo "  --flake8      Run flake8 only"
    echo "  --mypy        Run mypy only"
    echo "  --bandit      Run bandit only"
    echo "  --tests       Run unit tests only"
    echo "  --all         Run all checks (default)"
    echo "  --help        Show this help message"
}

# Main script
main() {
    # Check if virtual environment is active
    check_venv
    
    # Parse arguments
    if [ $# -eq 0 ]; then
        # No arguments, run all checks
        run_all_checks
        status=$?
    else
        # Process specific arguments
        status=0
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --black)
                    run_black || status=$?
                    shift
                    ;;
                --isort)
                    run_isort || status=$?
                    shift
                    ;;
                --flake8)
                    run_flake8 || status=$?
                    shift
                    ;;
                --mypy)
                    run_mypy || status=$?
                    shift
                    ;;
                --bandit)
                    run_bandit || status=$?
                    shift
                    ;;
                --tests)
                    run_tests || status=$?
                    shift
                    ;;
                --all)
                    run_all_checks || status=$?
                    shift
                    ;;
                --help)
                    show_help
                    exit 0
                    ;;
                *)
                    echo "Unknown option: $1"
                    show_help
                    exit 1
                    ;;
            esac
        done
    fi
    
    # Show summary and exit with appropriate status
    show_summary $status
    exit $status
}

# Run main function with all arguments
main "$@"
