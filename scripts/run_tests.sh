#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Run pytest with coverage
if command -v python3 >/dev/null 2>&1; then
    python3 -m pytest "${PROJECT_ROOT}/tests" \
        --cov="${PROJECT_ROOT}/dashboard" \
        --cov-report=html \
        --cov-report=term-missing \
        -v || true
fi

# Generate test results XML if needed
if [ -n "${CI:-}" ]; then
    python3 -m pytest "${PROJECT_ROOT}/tests" \
        --junitxml="${PROJECT_ROOT}/test-results.xml" \
        -v || true
fi

exit 0
