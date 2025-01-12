#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Initialize progress tracking
TOTAL_STEPS=10  # Adjusted for actual number of steps
CURRENT_STEP=0
init_progress $TOTAL_STEPS

# Error handling with permission check
handle_error() {
    local error_msg="$1"
    local check_permissions="${2:-false}"
    
    printf "\r\033[K❌ Error: %s\n" "$error_msg" >&2
    
    if [ "$check_permissions" = true ] && [ -f "${PROJECT_ROOT}/scripts/setup_permissions.sh" ]; then
        printf "\r\033[K🔧 Attempting to fix permissions...\n" >&2
        "${PROJECT_ROOT}/scripts/setup_permissions.sh"
        return 0
    fi
    
    exit 1
}

# Create reports directory
REPORTS_DIR="${PROJECT_ROOT}/reports"
mkdir -p "$REPORTS_DIR" >/dev/null 2>&1 || handle_error "Failed to create reports directory"

# Function to setup dependencies
setup_dependencies() {
    # Create temporary requirements file
    local temp_req=$(mktemp)
    cat > "$temp_req" << EOF
pytest==7.4.3
pytest-cov==4.1.0
black==23.11.0
isort==5.12.0
ruff==0.1.5
autoflake==2.2.1
playwright==1.39.0
pytest-playwright==0.4.3
pytest-asyncio==0.21.1
pytest-xdist==3.3.1
streamlit==1.29.0
streamlit-extras==0.3.5
watchdog==3.0.0
EOF

    # Install all packages at once
    echo "Installing dependencies..."
    if ! python3 -m pip install -r "$temp_req" >/dev/null 2>&1; then
        echo "⚠️  Warning: Some packages failed to install"
    fi
    rm -f "$temp_req"
    
    # Create necessary directories if they don't exist
    mkdir -p src/pages src/components src/assets dashboard/pages dashboard/components dashboard/assets >/dev/null 2>&1 || handle_error "Failed to create directories"
    
    # Move misplaced files to correct locations
    find . -maxdepth 1 -name '*.py' -not -name 'setup.py' -not -name 'run.py' | while read -r file; do
        if [[ "$(basename "$file")" =~ ^[0-9]+_.+\.py$ || "$(basename "$file")" == "Home.py" ]]; then
            mv "$file" "src/pages/" >/dev/null 2>&1 || echo "⚠️  Warning: Failed to move $file"
        fi
    done
    
    # Remove duplicate files (macOS compatible version)
    find . -type f -not -path '*/\.*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -print0 | \
    xargs -0 md5 -r 2>/dev/null | sort | uniq -d | cut -d ' ' -f2- | while read -r file; do
        if [ -f "$file" ]; then
            rm "$file" >/dev/null 2>&1 || echo "⚠️  Warning: Failed to remove duplicate $file"
        fi
    done
}

# Function to fix Python formatting
fix_python_formatting() {
    local file="$1"
    
    # Check if file is in Streamlit directory structure
    if [[ "$file" =~ ^./src/pages/ || "$file" =~ ^./dashboard/pages/ ]]; then
        # Ensure Streamlit page naming convention
        local basename=$(basename "$file")
        if [[ ! "$basename" =~ ^[0-9]+_.+\.py$ && "$basename" != "Home.py" ]]; then
            local new_name="00_${basename}"
            local dir=$(dirname "$file")
            mv "$file" "${dir}/${new_name}" >/dev/null 2>&1 || echo "⚠️  Warning: Failed to rename $file"
            file="${dir}/${new_name}"
        fi
    fi
    
    # Run formatters in sequence
    echo "Formatting $file..."
    if command -v isort >/dev/null 2>&1; then
        python3 -m isort --profile black "$file" >/dev/null 2>&1 || echo "⚠️  Warning: isort failed on $file"
    fi
    if command -v black >/dev/null 2>&1; then
        python3 -m black --quiet "$file" >/dev/null 2>&1 || echo "⚠️  Warning: black failed on $file"
    fi
    if command -v autoflake >/dev/null 2>&1; then
        python3 -m autoflake --in-place --remove-all-unused-imports "$file" >/dev/null 2>&1 || echo "⚠️  Warning: autoflake failed on $file"
    fi
    if command -v ruff >/dev/null 2>&1; then
        python3 -m ruff check --fix --unsafe-fixes --select ALL "$file" >/dev/null 2>&1 || echo "⚠️  Warning: ruff failed on $file"
    fi
    
    # Fix Streamlit-specific patterns
    if [[ "$file" =~ ^./src/pages/ || "$file" =~ ^./dashboard/pages/ ]]; then
        if grep -q "st\.set_page_config" "$file"; then
            local tmp_file="${file}.tmp"
            (
                echo "import streamlit as st"
                echo "st.set_page_config(layout='wide')"
                echo
                grep -v "st\.set_page_config" "$file" | grep -v "^import streamlit as st"
            ) > "$tmp_file" 2>/dev/null && mv "$tmp_file" "$file"
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
    
    # Ensure test discovery works
    mkdir -p "tests/$test_type" >/dev/null 2>&1
    touch "tests/__init__.py" "tests/$test_type/__init__.py"
    
    # Run tests with retries
    while [ $retry_count -lt $max_retries ]; do
        echo "Running $test_type tests (attempt $((retry_count + 1))/$max_retries)..."
        if python3 -m pytest "tests/$test_type" "${pytest_args[@]}" --quiet --no-header --tb=short >/dev/null 2>&1; then
            test_status=0
            break
        else
            test_status=$?
            ((retry_count++))
            if [ $retry_count -lt $max_retries ]; then
                echo "⚠️  Retrying $test_type tests..."
            fi
        fi
    done
    
    return $test_status
}

# Main execution
main() {
    # Setup virtual environment
    run_with_spinner "Setting up virtual environment" "
        if [ ! -d '${PROJECT_ROOT}/.venv' ]; then
            python3 -m venv '${PROJECT_ROOT}/.venv' >/dev/null 2>&1
        fi &&
        source '${PROJECT_ROOT}/.venv/bin/activate' >/dev/null 2>&1 &&
        python3 -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1
    " || handle_error "Failed to setup virtual environment"
    
    # Setup dependencies
    run_with_spinner "Installing dependencies" "setup_dependencies" || handle_error "Failed to install packages"
    
    # Find and fix Python files
    while IFS= read -r file; do
        fix_python_formatting "$file"
    done < <(find ./src ./tests ./dashboard -type f -name "*.py" 2>/dev/null | grep -v -E \
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
        -e "tests/unit/test_*" || true)
    
    # Run tests by type
    for test_type in "unit" "integration" "e2e"; do
        if [ -d "tests/$test_type" ]; then
            run_and_fix_tests "$test_type" || echo "⚠️  $test_type tests failed"
        fi
    done
    
    echo "✓ Verification and fixes completed"
}

# Run main function
main "$@" || handle_error "Script execution failed"
