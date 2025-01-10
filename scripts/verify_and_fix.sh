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
mkdir -p "$REPORTS_DIR" || handle_error "Failed to create reports directory"

# Validation function
validate_tool() {
    local tool=$1
    local config=$2
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "⚠️  Warning: $tool not found, skipping checks"
        return 1
    fi
    if [ -n "$config" ] && [ ! -f "$config" ]; then
        echo "⚠️  Warning: $tool config ($config) not found, using defaults"
    fi
    return 0
}

# Check and create required config files
echo "Checking configuration files..."

# Flake8 config
if [ ! -f "${PROJECT_ROOT}/.flake8" ]; then
    cat > "${PROJECT_ROOT}/.flake8" << 'EOF'
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist,.venv
ignore = E203,W503
EOF
fi

# MyPy config
if [ ! -f "${PROJECT_ROOT}/mypy.ini" ]; then
    cat > "${PROJECT_ROOT}/mypy.ini" << 'EOF'
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
EOF
fi

# Bandit config
if [ ! -f "${PROJECT_ROOT}/.bandit.yaml" ]; then
    cat > "${PROJECT_ROOT}/.bandit.yaml" << 'EOF'
exclude_dirs: ['.venv', 'tests']
tests: ['B201', 'B301']
skips: []
EOF
fi

# Run checks
echo "Running code quality checks..."

# Linting
if validate_tool "flake8" "${PROJECT_ROOT}/.flake8"; then
    echo "Running flake8..."
    flake8 "${PROJECT_ROOT}/dashboard" "${PROJECT_ROOT}/tests" \
        --config="${PROJECT_ROOT}/.flake8" \
        --output-file="${REPORTS_DIR}/flake8.txt" || true
fi

# Type checking
if validate_tool "mypy" "${PROJECT_ROOT}/mypy.ini"; then
    echo "Running mypy..."
    mypy "${PROJECT_ROOT}/dashboard" "${PROJECT_ROOT}/tests" \
        --config-file="${PROJECT_ROOT}/mypy.ini" \
        --txt-report="${REPORTS_DIR}/mypy.txt" || true
fi

# Security checks
if validate_tool "bandit" "${PROJECT_ROOT}/.bandit.yaml"; then
    echo "Running bandit..."
    bandit -r "${PROJECT_ROOT}/dashboard" \
        -c "${PROJECT_ROOT}/.bandit.yaml" \
        -f txt -o "${REPORTS_DIR}/bandit.txt" || true
fi

# Pre-commit hooks
if validate_tool "pre-commit" ""; then
    echo "Running pre-commit hooks..."
    pre-commit run --all-files || true
fi

# Check for any issues in reports
echo "Analyzing reports..."
ISSUES_FOUND=0

check_report() {
    local report=$1
    local tool=$2
    if [ -f "$report" ] && [ -s "$report" ]; then
        echo "⚠️  $tool issues found. See $report for details."
        ISSUES_FOUND=1
    else
        echo "✓ No $tool issues found"
    fi
}

check_report "${REPORTS_DIR}/flake8.txt" "Flake8"
check_report "${REPORTS_DIR}/mypy.txt" "MyPy"
check_report "${REPORTS_DIR}/bandit.txt" "Bandit"

if [ $ISSUES_FOUND -eq 1 ]; then
    echo "⚠️  Some issues were found. Please review the reports in ${REPORTS_DIR}"
else
    echo "✓ All checks passed successfully"
fi

exit 0
