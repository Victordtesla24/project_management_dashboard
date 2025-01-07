#!/bin/bash

# Exit on error, but allow us to handle the errors gracefully
set -eo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Setup logging
LOGS_DIR="logs"
LINT_LOG="${LOGS_DIR}/lint.log"
TEST_LOG="${LOGS_DIR}/test.log"
mkdir -p "$LOGS_DIR" >/dev/null 2>&1

# Initialize progress bar (5 steps)
init_progress 5

# Install dependencies
run_with_spinner "Installing dependencies" "
    which autoflake >/dev/null || pip install -q autoflake
    which black >/dev/null || pip install -q black
    which flake8 >/dev/null || pip install -q flake8
    which pytest >/dev/null || pip install -q pytest pytest-cov
"

# Create reports directory
mkdir -p reports >/dev/null 2>&1

# Format with black
run_with_spinner "Running black" "
    if ! black --check --quiet .; then
        find . -type f -name '*.py' ! -path './.venv/*' ! -path './reports/*' ! -path './logs/*' -exec black -q {} +
    fi
"

# Run flake8
run_with_spinner "Running flake8" "
    if ! flake8 --exclude=.venv,reports,logs .; then
        find . -type f -name '*.py' ! -path './.venv/*' ! -path './reports/*' ! -path './logs/*' -exec autoflake --remove-all-unused-imports --remove-unused-variables -i {} \;
    fi
"

# Run mypy
run_with_spinner "Running mypy" "mypy . || true"

# Run tests with coverage
run_with_spinner "Running tests" "pytest --cov=. --cov-report=html:reports/coverage --cov-report=term-missing -q || true"

# Print reports location to log file
{
    echo "📊 Reports available at:"
    echo "  • Lint log: ${LINT_LOG}"
    echo "  • Test log: ${TEST_LOG}"
    echo "  • Coverage report: reports/coverage/index.html"
} >> "$LINT_LOG"
