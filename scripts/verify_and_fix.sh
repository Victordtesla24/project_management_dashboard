#!/bin/bash
set -euo pipefail

# Redirect all output to both console and log file
exec 1> >(tee "$(cd "$(dirname "${0}")/.." && pwd)/logs/verify_and_fix.log") 2>&1

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Progress tracking
PROGRESS_CURRENT=0
PROGRESS_TOTAL=0

show_status() {
    local msg="$1"
    PROGRESS_CURRENT=$((PROGRESS_CURRENT + 1))
    if [ -f "${PROJECT_ROOT}/scripts/progress_bar.sh" ]; then
        bash "${PROJECT_ROOT}/scripts/progress_bar.sh" "$PROGRESS_CURRENT" "$PROGRESS_TOTAL" "$msg"
    else
        echo "→ $msg"
    fi
}

# Calculate total steps for progress bar
calculate_total_steps() {
    local test_count=0
    for type in "unit" "e2e" "integration" "fixtures" "reports"; do
        if [ -d "tests/$type" ]; then
            test_count=$((test_count + 1))
        fi
    done
    
    # Base steps: venv setup + deps + formatting + test suites + final report
    PROGRESS_TOTAL=$((3 + test_count))
}

# Function to setup virtual environment
setup_venv() {
    show_status "Setting up virtual environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
        python3 -m venv "${PROJECT_ROOT}/.venv"
    fi
    
    # Activate virtual environment
    source "${PROJECT_ROOT}/.venv/bin/activate" || {
        echo "❌ Failed to activate virtual environment"
        exit 1
    }
    
    # Upgrade pip in virtual environment
    python3 -m pip install --upgrade pip setuptools wheel || {
        echo "❌ Failed to upgrade pip"
        exit 1
    }
}

# Function to find Python files in relevant directories
find_python_files() {
    # Only look in src/, tests/, and dashboard/ directories
    find ./src ./tests ./dashboard -type f -name "*.py" 2>/dev/null | grep -v -E \
    -e "__pycache__" \
    -e "\.pytest_cache" \
    -e "\.mypy_cache" \
    -e "\.ruff_cache" \
    -e "\.coverage" \
    -e "htmlcov" \
    -e "\.git" \
    -e "\.venv" \
    -e "node_modules" \
    -e "build" \
    -e "dist" \
    -e "\.egg-info" \
    -e "lib" \
    -e "migrations/versions" \
    -e "reports" \
    -e "scripts" \
    -e "tests/fixtures" \
    -e "tests/reports" \
    -e "tests/e2e" \
    -e "tests/integration" \
    -e "tests/unit/test_*" || true
}

# Error handling with permission check
handle_error() {
    local error_msg="$1"
    local check_permissions="${2:-false}"
    
    echo "❌ Error: $error_msg"
    
    if [ "$check_permissions" = true ] && [ -f "${PROJECT_ROOT}/scripts/setup_permissions.sh" ]; then
        echo "🔧 Attempting to fix permissions..."
        "${PROJECT_ROOT}/scripts/setup_permissions.sh"
        return 0
    fi
    
    exit 1
}

# Create reports directory
REPORTS_DIR="${PROJECT_ROOT}/reports"
mkdir -p "$REPORTS_DIR" || handle_error "Failed to create reports directory"

# Function to install Python package
install_package() {
    local package="$1"
    show_status "Installing $package..."
    python3 -m pip install --no-cache-dir "$package" || {
        echo "❌ Failed to install $package"
        return 1
    }
    return 0
}

# Function to setup dependencies
setup_dependencies() {
    show_status "Installing dependencies..."
    
    # Install required packages
    local packages=(
        "pytest==7.4.3"
        "pytest-cov==4.1.0"
        "black==23.11.0"
        "isort==5.12.0"
        "ruff==0.1.5"
        "autoflake==2.2.1"
        "playwright==1.39.0"
        "pytest-playwright==0.4.3"
        "pytest-asyncio==0.21.1"
        "pytest-xdist==3.3.1"
        "streamlit==1.29.0"
        "streamlit-extras==0.3.5"
        "watchdog==3.0.0"
    )
    
    # Install packages with requirements
    python3 -m pip install --no-cache-dir "${packages[@]}" || {
        echo "❌ Failed to install packages"
        exit 1
    }
    
    # Check for duplicate files and optimize file locations
    show_status "Checking file structure..."
    
    # Create necessary directories if they don't exist
    mkdir -p src/pages src/components src/assets
    mkdir -p dashboard/pages dashboard/components dashboard/assets
    
    # Move misplaced files to correct locations
    find . -maxdepth 1 -name "*.py" -not -name "setup.py" -not -name "run.py" | while read -r file; do
        if [[ "$(basename "$file")" =~ ^[0-9]+_.+\.py$ || "$(basename "$file")" == "Home.py" ]]; then
            mv "$file" "src/pages/"
        fi
    done
    
    # Remove duplicate files
    find . -type f -not -path "*/\.*" -not -path "*/venv/*" -not -path "*/__pycache__/*" -print0 | \
    xargs -0 md5sum | sort | uniq -D | cut -c 35- | while read -r file; do
        if [ -f "$file" ]; then
            echo "⚠️ Removing duplicate file: $file"
            rm "$file"
        fi
    done
    
    # Verify and setup Playwright
    show_status "Setting up Playwright..."
    python3 -m pip install --upgrade pip wheel setuptools
    python3 -m playwright install-deps
    python3 -m playwright install chromium
    
    # Verify Playwright installation
    if ! python3 -c "import playwright._impl._str_utils" 2>/dev/null; then
        echo "⚠️ Reinstalling Playwright to fix missing modules..."
        python3 -m pip uninstall -y playwright pytest-playwright
        python3 -m pip install "playwright==1.39.0" "pytest-playwright==0.4.3"
        python3 -m playwright install-deps
        python3 -m playwright install chromium
    fi
}

# Function to fix Python formatting
fix_python_formatting() {
    local file="$1"
    show_status "Formatting $file"
    
    # Check if file is in Streamlit directory structure
    if [[ "$file" =~ ^./src/pages/ || "$file" =~ ^./dashboard/pages/ ]]; then
        # Ensure Streamlit page naming convention
        local basename=$(basename "$file")
        if [[ ! "$basename" =~ ^[0-9]+_.+\.py$ && "$basename" != "Home.py" ]]; then
            local new_name="00_${basename}"
            local dir=$(dirname "$file")
            mv "$file" "${dir}/${new_name}"
            file="${dir}/${new_name}"
        fi
    fi
    
    # Run formatters in sequence
    python3 -m isort --profile black "$file" 2>/dev/null || true
    python3 -m black --quiet "$file" 2>/dev/null || true
    python3 -m autoflake --in-place --remove-all-unused-imports "$file" 2>/dev/null || true
    python3 -m ruff check --fix --unsafe-fixes --select ALL "$file" 2>/dev/null || true
    
    # Fix Streamlit-specific patterns
    if [[ "$file" =~ ^./src/pages/ || "$file" =~ ^./dashboard/pages/ ]]; then
        # Ensure st.set_page_config is at the top
        if grep -q "st\.set_page_config" "$file"; then
            local tmp_file="${file}.tmp"
            (
                echo "import streamlit as st"
                echo "st.set_page_config(layout='wide')"
                echo
                grep -v "st\.set_page_config" "$file" | grep -v "^import streamlit as st"
            ) > "$tmp_file"
            mv "$tmp_file" "$file"
        fi
    fi
}

# Function to run and fix tests by type
run_and_fix_tests() {
    local test_type="$1"
    local max_retries=2
    local retry_count=0
    local test_status=0
    local pytest_args=()
    
    # Configure pytest arguments based on test type
    case "$test_type" in
        "unit")
            pytest_args+=("-n" "auto" "--dist=loadfile")
            ;;
        "e2e")
            pytest_args+=("--headed" "--browser=chromium")
            ;;
        *)
            pytest_args+=("-v")
            ;;
    esac
    
    show_status "Running $test_type tests..."
    
    # Ensure test discovery works
    mkdir -p "tests/$test_type"
    touch "tests/__init__.py"
    touch "tests/$test_type/__init__.py"
    
    # Clear pytest cache
    rm -rf .pytest_cache
    
    # Add project root to PYTHONPATH
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
    
    while [ $retry_count -lt $max_retries ]; do
        # Run tests with detailed output
        if python3 -m pytest "tests/$test_type" "${pytest_args[@]}" --tb=short --cache-clear 2>"${REPORTS_DIR}/${test_type}_errors.log"; then
            echo "✅ $test_type tests passed"
            return 0
        else
            test_status=$?
            retry_count=$((retry_count + 1))
            
            if [ $retry_count -lt $max_retries ]; then
                echo "⚠️ $test_type tests failed, attempt $retry_count of $max_retries. Fixing issues..."
                
                # Fix test files
                find "tests/$test_type" -name "test_*.py" -o -name "*_test.py" | while read -r test_file; do
                    fix_python_formatting "$test_file"
                done
                
                # Fix conftest files
                if [ -f "tests/$test_type/conftest.py" ]; then
                    fix_python_formatting "tests/$test_type/conftest.py"
                fi
                if [ -f "tests/conftest.py" ]; then
                    fix_python_formatting "tests/conftest.py"
                fi
            else
                echo "❌ $test_type tests failed after $max_retries attempts."
                echo "Test output:"
                cat "${REPORTS_DIR}/${test_type}_errors.log"
                return $test_status
            fi
        fi
    done
    
    return $test_status
}

# Main execution flow
echo "Starting code quality checks..."

# Calculate total steps
calculate_total_steps

# Setup virtual environment and dependencies
setup_venv
setup_dependencies

# Fix formatting for all Python files
show_status "Fixing code formatting..."
find_python_files | while read -r file; do
    fix_python_formatting "$file"
done

# Run tests in specified order
show_status "Running test suites in order..."

# Define test sequence
test_types=("unit" "e2e" "integration" "fixtures" "reports")

# Track test status
overall_test_status=0

# Run tests in sequence
for test_type in "${test_types[@]}"; do
    if [ -d "tests/$test_type" ]; then
        if ! run_and_fix_tests "$test_type"; then
            echo "⚠️ $test_type tests failed"
            overall_test_status=1
            echo "Test failures for $test_type:" >> "${REPORTS_DIR}/test_failures_summary.log"
            if [ -f "${REPORTS_DIR}/${test_type}_errors.log" ]; then
                cat "${REPORTS_DIR}/${test_type}_errors.log" >> "${REPORTS_DIR}/test_failures_summary.log"
            fi
        fi
    else
        echo "⚠️ No $test_type tests found"
    fi
done

# Report final status
if [ $overall_test_status -eq 0 ]; then
    echo "✅ All test suites completed successfully"
else
    echo "⚠️ Some test suites failed. Check ${REPORTS_DIR}/test_failures_summary.log for details"
fi

echo "✅ All tasks completed"
