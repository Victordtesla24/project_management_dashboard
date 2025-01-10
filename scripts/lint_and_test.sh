#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Create reports directory
REPORTS_DIR="${PROJECT_ROOT}/reports"
COVERAGE_DIR="${REPORTS_DIR}/coverage"
mkdir -p "$REPORTS_DIR" "$COVERAGE_DIR" || handle_error "Failed to create report directories"

# Validation function
validate_tool() {
    local tool=$1
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "⚠️  Warning: $tool not found, skipping related checks"
        return 1
    fi
    return 0
}

# Clean up old reports
echo "Cleaning up old reports..."
rm -rf "${REPORTS_DIR:?}"/* 2>/dev/null || true

# Initialize test results
LINT_STATUS=0
TYPE_STATUS=0
TEST_STATUS=0
SEC_STATUS=0

# Run linting
echo "Running code style checks..."
if validate_tool "flake8"; then
    flake8 "${PROJECT_ROOT}/dashboard" "${PROJECT_ROOT}/tests" \
        --config="${PROJECT_ROOT}/.flake8" \
        --output-file="${REPORTS_DIR}/flake8.txt" || LINT_STATUS=$?

    if [ $LINT_STATUS -eq 0 ]; then
        echo "✓ Code style checks passed"
    else
        echo "⚠️  Code style issues found. See ${REPORTS_DIR}/flake8.txt"
    fi
fi

# Run type checking
echo "Running type checks..."
if validate_tool "mypy"; then
    mypy "${PROJECT_ROOT}/dashboard" "${PROJECT_ROOT}/tests" \
        --config-file="${PROJECT_ROOT}/mypy.ini" \
        --txt-report="${REPORTS_DIR}/mypy.txt" || TYPE_STATUS=$?

    if [ $TYPE_STATUS -eq 0 ]; then
        echo "✓ Type checks passed"
    else
        echo "⚠️  Type issues found. See ${REPORTS_DIR}/mypy.txt"
    fi
fi

# Run tests with coverage
echo "Running tests..."
if validate_tool "pytest"; then
    # Run tests in parallel if pytest-xdist is available
    XDIST_OPTS=""
    if python3 -c "import pytest_xdist" >/dev/null 2>&1; then
        XDIST_OPTS="-n auto"
    fi

    # Run tests by type
    for test_type in "unit" "integration" "e2e"; do
        echo "Running ${test_type} tests..."
        pytest "${PROJECT_ROOT}/tests" \
            -m "$test_type" \
            --cov="${PROJECT_ROOT}/dashboard" \
            --cov-report=html:${COVERAGE_DIR} \
            --cov-report=term-missing \
            --junit-xml="${REPORTS_DIR}/pytest_${test_type}.xml" \
            -v $XDIST_OPTS || TEST_STATUS=$?
    done

    if [ $TEST_STATUS -eq 0 ]; then
        echo "✓ All tests passed"
    else
        echo "⚠️  Some tests failed. See reports for details"
    fi
fi

# Run security checks
echo "Running security checks..."
if validate_tool "bandit"; then
    bandit -r "${PROJECT_ROOT}/dashboard" \
        -c "${PROJECT_ROOT}/.bandit.yaml" \
        -f txt -o "${REPORTS_DIR}/bandit.txt" || SEC_STATUS=$?

    if [ $SEC_STATUS -eq 0 ]; then
        echo "✓ Security checks passed"
    else
        echo "⚠️  Security issues found. See ${REPORTS_DIR}/bandit.txt"
    fi
fi

# Generate summary report
echo "Generating summary report..."
cat > "${REPORTS_DIR}/summary.txt" << EOF
Test Suite Summary
=================
Date: $(date)
Project: $(basename "${PROJECT_ROOT}")

Code Style Checks: $([ $LINT_STATUS -eq 0 ] && echo "✓ Passed" || echo "⚠️  Failed")
Type Checks: $([ $TYPE_STATUS -eq 0 ] && echo "✓ Passed" || echo "⚠️  Failed")
Unit Tests: $([ $TEST_STATUS -eq 0 ] && echo "✓ Passed" || echo "⚠️  Failed")
Security Checks: $([ $SEC_STATUS -eq 0 ] && echo "✓ Passed" || echo "⚠️  Failed")

For detailed reports, see:
- Code style: flake8.txt
- Type checking: mypy.txt
- Test results: pytest_*.xml
- Coverage: coverage/index.html
- Security: bandit.txt
EOF

# Check if any checks failed
if [ $((LINT_STATUS + TYPE_STATUS + TEST_STATUS + SEC_STATUS)) -gt 0 ]; then
    echo "⚠️  Some checks failed. See ${REPORTS_DIR}/summary.txt for details"
    exit 1
else
    echo "✓ All checks passed successfully"
    exit 0
fi
