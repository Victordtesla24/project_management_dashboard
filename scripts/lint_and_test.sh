#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"
source "${PROJECT_ROOT}/scripts/utils/common.sh"

# Initialize progress tracking
TOTAL_STEPS=4  # linting, type checking, tests, security
CURRENT_STEP=0
init_progress $TOTAL_STEPS

# Create reports directory
REPORTS_DIR="${PROJECT_ROOT}/reports"
COVERAGE_DIR="${REPORTS_DIR}/coverage"
mkdir -p "$REPORTS_DIR" "$COVERAGE_DIR" >/dev/null 2>&1

# Error handling
handle_error() {
    echo "❌ Error: $1" >&2
    exit 1
}

# Activate virtual environment
activate_venv() {
    if [ -f "${PROJECT_ROOT}/.venv/bin/activate" ]; then
        source "${PROJECT_ROOT}/.venv/bin/activate" || handle_error "Failed to activate virtual environment"
    else
        handle_error "Virtual environment not found. Please run setup_dev.sh first"
    fi
}

# Install required packages
install_packages() {
    echo "Installing required packages..."
    python3 -m pip install --quiet --upgrade pip setuptools wheel || handle_error "Failed to upgrade pip"
    
    # Create temporary requirements file
    local temp_req=$(mktemp)
    cat > "$temp_req" << EOF
flake8>=6.1.0
mypy>=1.8.0
pytest>=7.4.3
pytest-cov>=4.1.0
pytest-xdist>=3.3.1
bandit>=1.7.5
lxml>=4.9.3
types-setuptools>=57.4.2
EOF

    # Install packages
    if ! python3 -m pip install --quiet -r "$temp_req"; then
        rm -f "$temp_req"
        handle_error "Failed to install required packages"
    fi
    rm -f "$temp_req"
}

# Clean up old reports
rm -rf "${REPORTS_DIR:?}"/* 2>/dev/null || true

# Initialize test results
LINT_STATUS=0
TYPE_STATUS=0
TEST_STATUS=0
SEC_STATUS=0

# Activate virtual environment and install packages
activate_venv
install_packages

# Run linting with timeout
echo "Running code style checks..."
timeout 30s python3 -m flake8 "${PROJECT_ROOT}/dashboard" "${PROJECT_ROOT}/tests" \
    --config="${PROJECT_ROOT}/.flake8" \
    --output-file="${REPORTS_DIR}/flake8.txt" \
    --quiet \
    --exit-zero || LINT_STATUS=$?

if [ $LINT_STATUS -ne 0 ] && [ -f "${REPORTS_DIR}/flake8.txt" ]; then
    grep -E "^[^:]+:[0-9]+:[0-9]+: [EF][0-9]+ " "${REPORTS_DIR}/flake8.txt" >&2 || true
fi

# Run type checking with timeout
echo "Running type checks..."
timeout 30s python3 -m mypy "${PROJECT_ROOT}/dashboard" "${PROJECT_ROOT}/tests" \
    --config-file="${PROJECT_ROOT}/mypy.ini" \
    --txt-report="${REPORTS_DIR}/mypy.txt" \
    --no-error-summary \
    --no-pretty \
    --hide-error-context \
    --ignore-missing-imports \
    --follow-imports=skip || TYPE_STATUS=$?

if [ $TYPE_STATUS -ne 0 ] && [ -f "${REPORTS_DIR}/mypy.txt" ]; then
    grep -E "^[^:]+:[0-9]+: error: " "${REPORTS_DIR}/mypy.txt" >&2 || true
fi

# Run tests with coverage and timeout
echo "Running tests..."

# Run tests by type with shorter timeouts
for test_type in "unit" "integration" "e2e"; do
    echo "Running $test_type tests..."
    timeout 60s python3 -m pytest "${PROJECT_ROOT}/tests/${test_type}" \
        --cov="${PROJECT_ROOT}/dashboard" \
        --cov-report=html:"${COVERAGE_DIR}" \
        --cov-report=term-missing \
        --junit-xml="${REPORTS_DIR}/pytest_${test_type}.xml" \
        -v -n auto \
        --quiet \
        --no-header \
        --tb=short || TEST_STATUS=$?
done

# Run security checks with timeout
echo "Running security checks..."
timeout 30s python3 -m bandit -r "${PROJECT_ROOT}/dashboard" \
    -c "${PROJECT_ROOT}/.bandit.yaml" \
    -f txt -o "${REPORTS_DIR}/bandit.txt" \
    -ll --quiet || SEC_STATUS=$?

if [ $SEC_STATUS -ne 0 ] && [ -f "${REPORTS_DIR}/bandit.txt" ]; then
    grep -E "^Issue: \[B[0-9]+:.*\] .*Severity: HIGH" "${REPORTS_DIR}/bandit.txt" >&2 || true
fi

# Show summary
echo
echo "Test Summary:"
echo "============"
echo "Linting: $([ $LINT_STATUS -eq 0 ] && echo "✓" || echo "✗")"
echo "Type Checking: $([ $TYPE_STATUS -eq 0 ] && echo "✓" || echo "✗")"
echo "Tests: $([ $TEST_STATUS -eq 0 ] && echo "✓" || echo "✗")"
echo "Security: $([ $SEC_STATUS -eq 0 ] && echo "✓" || echo "✗")"
echo

# Exit with combined status
exit $((LINT_STATUS + TYPE_STATUS + TEST_STATUS + SEC_STATUS))
