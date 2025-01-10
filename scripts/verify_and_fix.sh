#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source progress bar utilities
PROGRESS_BAR_SCRIPT="${PROJECT_ROOT}/scripts/utils/progress_bar.sh"
if [ -f "$PROGRESS_BAR_SCRIPT" ]; then
    source "$PROGRESS_BAR_SCRIPT"
    # Calculate total steps for progress bar
    TOTAL_STEPS=0
    # Count test directories
    for test_type in "unit" "e2e" "integration" "fixtures" "reports"; do
        [ -d "tests/$test_type" ] && ((TOTAL_STEPS++))
    done
    # Add steps for each major operation
    TOTAL_STEPS=$((TOTAL_STEPS + 7)) # 7 for major operations (formatting, imports, etc.)
    init_progress $TOTAL_STEPS
else
    echo "⚠️ Progress bar utilities not found, continuing without visual feedback..."
    # Define dummy functions if progress bar script is not available
    draw_progress_bar() { :; }
    update_progress() { :; }
    run_with_spinner() { eval "$2"; }
fi

# Function to run operation with progress
run_operation() {
    local operation_name="$1"
    local cmd="$2"
    
    if [ -f "$PROGRESS_BAR_SCRIPT" ]; then
        echo -n "Running $operation_name..."
        if ! run_with_spinner "$operation_name" "$cmd"; then
            printf "\r\033[K❌ %s failed\n" "$operation_name"
            return 1
        fi
        printf "\r\033[K✅ %s completed\n" "$operation_name"
    else
        echo "Running $operation_name..."
        if ! eval "$cmd"; then
            echo "❌ $operation_name failed"
            return 1
        fi
        echo "✅ $operation_name completed"
    fi
    return 0
}

# Define excluded paths - strictly limit scope
EXCLUDE_PATTERN=".venv/* .git/* __pycache__/* *.pyc build/* dist/* *.egg-info/* lib/* node_modules/* .pytest_cache/* .mypy_cache/* .ruff_cache/* .coverage/* htmlcov/*"

# Function to find Python files excluding .venv and other patterns
find_python_files() {
    find . -type f -name "*.py" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.pytest_cache/*" \
    ! -path "*/.mypy_cache/*" \
    ! -path "*/.ruff_cache/*" \
    ! -path "*/.coverage/*" \
    ! -path "*/htmlcov/*" \
    ! -path "*/.git/*" \
    ! -path "*/.venv/*" \
    ! -path "*/node_modules/*" \
    ! -path "*/build/*" \
    ! -path "*/dist/*" \
    ! -path "*/*.egg-info/*" \
    ! -path "*/lib/*" \
    ! -path "*/migrations/versions/*" \
    ! -path "*/reports/*" \
    ! -path "*/scripts/*" \
    ! -path "*/tests/fixtures/*" \
    ! -path "*/tests/reports/*"
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

# Function to update directory structure for Streamlit
update_directory_structure() {
    echo "📁 Updating directory structure for Streamlit..."
    
    # Create Streamlit standard directories
    mkdir -p "${PROJECT_ROOT}/src/pages"
    mkdir -p "${PROJECT_ROOT}/src/components"
    mkdir -p "${PROJECT_ROOT}/src/utils"
    mkdir -p "${PROJECT_ROOT}/src/data"
    mkdir -p "${PROJECT_ROOT}/src/models"
    mkdir -p "${PROJECT_ROOT}/src/services"
    mkdir -p "${PROJECT_ROOT}/src/styles"
    mkdir -p "${PROJECT_ROOT}/src/assets"
    mkdir -p "${PROJECT_ROOT}/config"
    mkdir -p "${PROJECT_ROOT}/tests/unit"
    mkdir -p "${PROJECT_ROOT}/tests/integration"
    mkdir -p "${PROJECT_ROOT}/tests/e2e"
    mkdir -p "${PROJECT_ROOT}/docs"
    
    # Move files to appropriate directories
    echo "Moving files to Streamlit directory structure..."
    
    # Move Python files to src directory
    find . -maxdepth 1 -type f -name "*.py" ! -name "setup.py" ! -name "conftest.py" -exec mv {} "${PROJECT_ROOT}/src/" \; 2>/dev/null || true
    
    # Move utility files
    find . -type f -name "*utils*.py" ! -path "*/src/*" -exec mv {} "${PROJECT_ROOT}/src/utils/" \; 2>/dev/null || true
    
    # Move component files
    find . -type f -name "*component*.py" ! -path "*/src/*" -exec mv {} "${PROJECT_ROOT}/src/components/" \; 2>/dev/null || true
    
    # Move service files
    find . -type f -name "*service*.py" ! -path "*/src/*" -exec mv {} "${PROJECT_ROOT}/src/services/" \; 2>/dev/null || true
    
    # Move model files
    find . -type f -name "*model*.py" ! -path "*/src/*" -exec mv {} "${PROJECT_ROOT}/src/models/" \; 2>/dev/null || true
    
    # Move test files to appropriate test directories
    find . -type f -name "test_*.py" ! -path "*/tests/*" -exec mv {} "${PROJECT_ROOT}/tests/unit/" \; 2>/dev/null || true
    find . -type f -name "*_test.py" ! -path "*/tests/*" -exec mv {} "${PROJECT_ROOT}/tests/unit/" \; 2>/dev/null || true
    
    # Move integration tests
    find "${PROJECT_ROOT}/tests/unit" -type f -name "*integration*.py" -exec mv {} "${PROJECT_ROOT}/tests/integration/" \; 2>/dev/null || true
    
    # Move e2e tests
    find "${PROJECT_ROOT}/tests/unit" -type f -name "*e2e*.py" -exec mv {} "${PROJECT_ROOT}/tests/e2e/" \; 2>/dev/null || true
    
    # Create main Streamlit file if it doesn't exist
    if [ ! -f "${PROJECT_ROOT}/src/Home.py" ]; then
        cat > "${PROJECT_ROOT}/src/Home.py" <<EOL
"""Main Streamlit application file."""
import streamlit as st

st.set_page_config(
    page_title="Project Management Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Project Management Dashboard")
st.write("Welcome to the Project Management Dashboard!")
EOL
    fi
    
    # Create .streamlit config if it doesn't exist
    mkdir -p "${PROJECT_ROOT}/.streamlit"
    if [ ! -f "${PROJECT_ROOT}/.streamlit/config.toml" ]; then
        cat > "${PROJECT_ROOT}/.streamlit/config.toml" <<EOL
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
EOL
    fi
    
    # Create requirements.txt if it doesn't exist
    if [ ! -f "${PROJECT_ROOT}/requirements.txt" ]; then
        cat > "${PROJECT_ROOT}/requirements.txt" <<EOL
streamlit>=1.24.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.3.0
isort>=5.12.0
ruff>=0.0.280
autoflake>=2.2.0
radon>=6.0.0
EOL
    fi
    
    # Create setup.py if it doesn't exist
    if [ ! -f "${PROJECT_ROOT}/setup.py" ]; then
        cat > "${PROJECT_ROOT}/setup.py" <<EOL
"""Setup script for the project."""
from setuptools import find_packages, setup

setup(
    name="project_management_dashboard",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.8",
)
EOL
    fi
    
    # Create README.md if it doesn't exist
    if [ ! -f "${PROJECT_ROOT}/README.md" ]; then
        cat > "${PROJECT_ROOT}/README.md" <<EOL
# Project Management Dashboard

A Streamlit-based dashboard for project management and monitoring.

## Setup

1. Clone the repository
2. Create a virtual environment: \`python -m venv .venv\`
3. Activate the virtual environment:
   - Windows: \`.venv\\Scripts\\activate\`
   - Unix/macOS: \`source .venv/bin/activate\`
4. Install dependencies: \`pip install -r requirements.txt\`

## Running the Application

\`\`\`bash
streamlit run src/Home.py
\`\`\`

## Development

- Run tests: \`./scripts/run_tests.sh\`
- Fix code quality: \`./scripts/verify_and_fix.sh\`
EOL
    fi
}

# Function to fix permissions
fix_permissions() {
    echo "🔒 Fixing permissions..."
    
    # Fix script permissions
    find "${PROJECT_ROOT}/scripts" -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    
    # Fix Python file permissions
    find_python_files | while read -r file; do
        chmod 644 "$file" 2>/dev/null || true
    done
    
    # Fix directory permissions
    find "${PROJECT_ROOT}" -type d -exec chmod 755 {} \; 2>/dev/null || true
    
    # Ensure .venv/bin has execute permissions if it exists
    if [ -d "${PROJECT_ROOT}/.venv/bin" ]; then
        chmod -R +x "${PROJECT_ROOT}/.venv/bin" 2>/dev/null || true
    fi
    
    # Run setup_permissions.sh if it exists
    if [ -f "${PROJECT_ROOT}/scripts/setup_permissions.sh" ]; then
        echo "Running setup_permissions.sh..."
        "${PROJECT_ROOT}/scripts/setup_permissions.sh"
    fi
}

# Function to fix Python formatting
fix_python_formatting() {
    echo "🔍 Checking Python formatting..."
    
    find_python_files | while read -r file; do
        if [ ! -f "$file" ] || [ ! -r "$file" ] || [ ! -w "$file" ]; then
            echo "Skipping $file (not a regular file or no read/write permissions)"
            continue
        fi
        
        echo "Fixing formatting in $file"
        
        # Run isort to organize imports
        python3 -m isort --profile black "$file" 2>/dev/null || true
        
        # Run black for consistent formatting
        python3 -m black --quiet "$file" 2>/dev/null || true
        
        # Run autoflake to remove unused imports
        python3 -m autoflake --in-place --remove-all-unused-imports "$file" 2>/dev/null || true
        
        # Run ruff to fix additional issues
        python3 -m ruff check --fix --unsafe-fixes \
            --select E,F,W,C,I,N,UP,B,A,COM,C4,T10,T20,RET,SLF,ARG,PTH,PL,RUF "$file" 2>/dev/null || true
        
        # Run ruff again with pylint rules
        python3 -m ruff check --fix --unsafe-fixes \
            --select PLR,PLW "$file" 2>/dev/null || true
        
        # Run black one final time to ensure consistent formatting
        python3 -m black --quiet "$file" 2>/dev/null || true
    done
}

# Fix line length issues
fix_line_length() {
    echo "Fixing line length issues..."
    find_python_files | while read -r file; do
        if grep -l "^.*.\{101\}.*$" "$file" > /dev/null 2>&1; then
            echo "Fixing long lines in $file"
            # First try black
            python3 -m black --line-length 100 "$file" 2>/dev/null || true
            if grep -l "^.*.\{101\}.*$" "$file" > /dev/null 2>&1; then
                # If black could not fix it, try ruff
                python3 -m ruff check --fix --select E501 "$file" 2>/dev/null || true
            fi
        fi
    done
}

# Function to fix indentation
fix_indentation() {
    echo "🔧 Fixing indentation..."
    
    find_python_files | while read -r file; do
        echo "Fixing indentation in $file"
        python3 -m black --quiet "$file" 2>/dev/null || true
    done
}

# Fix unused imports
fix_unused_imports() {
    echo "Fixing unused imports..."
    find_python_files | while read -r file; do
        echo "Fixing unused imports in $file"
        python3 -m autoflake --in-place --remove-all-unused-imports "$file" 2>/dev/null || true
        python3 -m ruff check --fix --select F401 "$file" 2>/dev/null || true
        python3 -m isort "$file" --profile black 2>/dev/null || true
    done
}

# Fix code complexity issues
fix_code_complexity() {
    echo "Fixing code complexity issues..."
    find_python_files | while read -r file; do
        echo "Attempting to fix complex code in $file"
        python3 -m ruff check --fix --select C901 "$file" 2>/dev/null || true
        python3 -m ruff check --fix --select PLR0911,PLR0912,PLR0913,PLR0915 "$file" 2>/dev/null || true
    done
}

# Function to fix blank lines between functions
fix_blank_lines() {
    echo "📝 Fixing blank lines between functions..."
    find_python_files | while read -r file; do
        echo "Fixing blank lines in $file"
        python3 -m black --quiet "$file" 2>/dev/null || true
    done
}

# Function to detect and consolidate duplicate code
fix_duplicate_code() {
    echo "🔍 Detecting and fixing duplicate code..."
    
    # Create a temporary directory for duplicate code analysis
    TEMP_DIR=$(mktemp -d)
    DUPLICATES_REPORT="${TEMP_DIR}/duplicates.json"
    
    # Use radon to find similar code blocks
    echo "Scanning for duplicate code..."
    python3 -m radon raw $(find_python_files) > "$DUPLICATES_REPORT" 2>/dev/null || true
    
    if [ -s "$DUPLICATES_REPORT" ]; then
        echo "Processing duplicate code findings..."
        REPORT_PATH="$DUPLICATES_REPORT"
        TEMP_PATH="$TEMP_DIR"
        python3 - <<EOF
import os
import ast
from collections import defaultdict
from difflib import SequenceMatcher
import glob
import shutil

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.readlines()
    except:
        return []

def write_file_content(file_path, content):
    try:
        with open(file_path, 'w') as f:
            f.writelines(content)
    except:
        pass

def get_code_blocks(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        blocks = {}
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = node.end_lineno
                block_lines = content.split('\n')[start:end]
                blocks[node.name] = {
                    'type': node.__class__.__name__,
                    'start': start,
                    'end': end,
                    'code': '\n'.join(block_lines)
                }
    except:
        blocks = {}
    
    return blocks

def is_similar(code1, code2, threshold=0.85):
    return SequenceMatcher(None, code1, code2).ratio() > threshold

def find_similar_blocks(blocks_dict):
    similar_groups = []
    processed = set()
    
    for file1, blocks1 in blocks_dict.items():
        for name1, details1 in blocks1.items():
            if (file1, name1) in processed:
                continue
                
            current_group = [(file1, name1, details1)]
            processed.add((file1, name1))
            
            for file2, blocks2 in blocks_dict.items():
                for name2, details2 in blocks2.items():
                    if (file2, name2) in processed:
                        continue
                    
                    if (file1 != file2 or name1 != name2) and \
                       details1['type'] == details2['type'] and \
                       is_similar(details1['code'], details2['code']):
                        current_group.append((file2, name2, details2))
                        processed.add((file2, name2))
            
            if len(current_group) > 1:
                similar_groups.append(current_group)
    
    return similar_groups

def find_similar_files(file_paths, threshold=0.85):
    similar_groups = []
    processed = set()
    
    for file1 in file_paths:
        if file1 in processed:
            continue
            
        try:
            with open(file1, 'r') as f:
                content1 = f.read()
        except:
            continue
            
        current_group = [file1]
        processed.add(file1)
        
        for file2 in file_paths:
            if file2 in processed:
                continue
                
            try:
                with open(file2, 'r') as f:
                    content2 = f.read()
            except:
                continue
                
            if file1 != file2 and is_similar(content1, content2, threshold):
                current_group.append(file2)
                processed.add(file2)
        
        if len(current_group) > 1:
            similar_groups.append(current_group)
    
    return similar_groups

def ensure_streamlit_structure(file_path):
    """Ensure file is in the correct Streamlit directory structure."""
    if not file_path.startswith('./src/'):
        base_name = os.path.basename(file_path)
        if 'pages' in file_path.lower():
            target_dir = './src/pages'
        elif 'component' in file_path.lower():
            target_dir = './src/components'
        elif 'util' in file_path.lower():
            target_dir = './src/utils'
        elif 'model' in file_path.lower():
            target_dir = './src/models'
        elif 'service' in file_path.lower():
            target_dir = './src/services'
        elif 'data' in file_path.lower():
            target_dir = './src/data'
        elif 'style' in file_path.lower():
            target_dir = './src/styles'
        elif 'asset' in file_path.lower():
            target_dir = './src/assets'
        else:
            target_dir = './src'
        
        os.makedirs(target_dir, exist_ok=True)
        new_path = os.path.join(target_dir, base_name)
        if os.path.exists(file_path):
            shutil.move(file_path, new_path)
        return new_path
    return file_path

# Scan all Python files
python_files = [f.strip() for f in os.popen('find . -type f -name "*.py" ! -path "*/.venv/*" ! -path "*/__pycache__/*"').readlines()]

# Find similar files
similar_file_groups = find_similar_files(python_files)

# Process similar files
for group in similar_file_groups:
    # Keep the file with the most comprehensive name or in the most appropriate location
    best_file = min(group, key=lambda x: (
        0 if '/src/utils/' in x else
        1 if '/src/components/' in x else
        2 if '/src/services/' in x else
        3 if '/src/models/' in x else
        4 if '/src/' in x else 5,
        len(x)
    ))
    
    # Ensure the best file is in the correct Streamlit directory structure
    best_file = ensure_streamlit_structure(best_file)
    
    # Remove other files in the group
    for file_path in group:
        if file_path != best_file:
            try:
                os.remove(file_path)
                print(f"Removed duplicate file: {file_path} (consolidated into {best_file})")
            except:
                pass

# Scan all Python files for code blocks
all_blocks = {}
for file_path in python_files:
    if os.path.exists(file_path):
        blocks = get_code_blocks(file_path)
        if blocks:
            all_blocks[file_path] = blocks

# Find and process similar code blocks
similar_groups = find_similar_blocks(all_blocks)

for group in similar_groups:
    # Choose the best location for the consolidated code
    best_location = min(group, key=lambda x: 
        (0 if '/src/utils/' in x[0] else
         1 if '/src/components/' in x[0] else
         2 if '/src/services/' in x[0] else
         3 if '/src/models/' in x[0] else
         4 if '/src/' in x[0] else 5,
         len(x[0]))
    )[0]
    
    # Ensure the location follows Streamlit structure
    best_location = ensure_streamlit_structure(best_location)
    
    # Get the best implementation from the group
    best_impl = max(group, key=lambda x: len(x[2]['code'].strip()))[2]
    block_name = group[0][1]
    block_type = best_impl['type']
    
    # Determine the target file
    if '/src/utils/' in best_location:
        target_file = best_location
    else:
        target_file = './src/utils/common.py'
        if not os.path.exists(os.path.dirname(target_file)):
            os.makedirs(os.path.dirname(target_file))
        if not os.path.exists(target_file):
            with open(target_file, 'w') as f:
                f.write('"""Common utility functions and classes."""\n\n')
    
    # Add the consolidated code to the target file
    target_content = read_file_content(target_file)
    if not any(block_name in line for line in target_content):
        target_content.append('\n\n' + best_impl['code'])
        write_file_content(target_file, target_content)
    
    # Remove duplicates and add imports
    for file_path, name, details in group:
        if file_path != target_file:
            file_lines = read_file_content(file_path)
            if file_lines:
                # Add import at the top if not present
                import_line = f'from {os.path.splitext(os.path.relpath(target_file, os.path.dirname(file_path)))[0]} import {block_name}\n'
                if not any(import_line in line for line in file_lines):
                    file_lines.insert(0, import_line)
                # Remove the duplicate code
                del file_lines[details['start']:details['end']]
                write_file_content(file_path, file_lines)
                print(f"Moved {block_type.lower()} '{block_name}' from {file_path} to {target_file}")

# Cleanup
os.remove('${REPORT_PATH}')
os.rmdir('${TEMP_PATH}')
EOF
    else
        echo "No significant code duplicates found."
    fi
}

# Function to run and fix tests by type
run_and_fix_tests() {
    local test_type="$1"
    local max_retries=2
    local retry_count=0
    local test_status=0
    
    echo "🧪 Running $test_type tests..."
    
    # Ensure test discovery works
    mkdir -p "tests/$test_type"
    touch "tests/__init__.py"
    touch "tests/$test_type/__init__.py"
    
    # Clear pytest cache to ensure fresh test discovery
    rm -rf .pytest_cache
    
    # Add project root to PYTHONPATH
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
    
    while [ $retry_count -lt $max_retries ]; do
        # First try test collection
        if ! python3 -m pytest "tests/$test_type" --collect-only -q >"${REPORTS_DIR}/${test_type}_collection.log" 2>&1; then
            echo "⚠️ Test discovery failed for $test_type. Fixing import issues..."
            # Fix import issues in test files
            find "tests/$test_type" -name "test_*.py" -o -name "*_test.py" | while read -r test_file; do
                fix_linter_errors "$test_file"
            done
            retry_count=$((retry_count + 1))
            continue
        fi
        
        # Run the tests
        if python3 -m pytest "tests/$test_type" -v --cache-clear 2>"${REPORTS_DIR}/${test_type}_errors.log"; then
            echo "✅ $test_type tests passed"
            return 0
        else
            test_status=$?
            retry_count=$((retry_count + 1))
            
            if [ $retry_count -lt $max_retries ]; then
                echo "⚠️ $test_type tests failed, attempt $retry_count of $max_retries. Fixing issues..."
                
                # Fix all test files in the directory
                find "tests/$test_type" -name "test_*.py" -o -name "*_test.py" | while read -r test_file; do
                    fix_linter_errors "$test_file"
                done
                
                # Fix any conftest.py files
                if [ -f "tests/$test_type/conftest.py" ]; then
                    fix_linter_errors "tests/$test_type/conftest.py"
                fi
                if [ -f "tests/conftest.py" ]; then
                    fix_linter_errors "tests/conftest.py"
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

# Function to fix linter errors systematically
fix_linter_errors() {
    local file="$1"
    local max_retries=2
    local retry_count=0
    local error_file="${REPORTS_DIR}/linter_errors.log"
    
    echo "🔍 Fixing linter errors in $file..."
    
    # Create reports directory if it doesn't exist
    mkdir -p "${REPORTS_DIR}"
    
    while [ $retry_count -lt $max_retries ]; do
        # Run comprehensive linting with detailed error output
        python3 -m ruff check "$file" > "$error_file" 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ Linting passed for $file"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        
        if [ $retry_count -lt $max_retries ]; then
            echo "⚠️ Fixing linter errors, attempt $retry_count of $max_retries..."
            
            # First try autoflake for unused imports
            python3 -m autoflake --in-place --remove-all-unused-imports "$file" 2>/dev/null || true
            
            # Then run black for formatting
            python3 -m black --quiet "$file" 2>/dev/null || true
            
            # Run isort for import sorting
            python3 -m isort --profile black "$file" 2>/dev/null || true
            
            # Apply fixes based on error types
            if grep -q "F401\|F403\|F405" "$error_file"; then
                echo "📦 Fixing unused imports and star imports..."
                python3 -m autoflake --in-place --remove-all-unused-imports --expand-star-imports "$file"
            fi
            
            if grep -q "E\|W" "$error_file"; then
                echo "🔧 Fixing style errors and warnings..."
                python3 -m ruff check --fix --select E,W "$file"
            fi
            
            if grep -q "I" "$error_file"; then
                echo "📝 Fixing import order..."
                python3 -m isort --profile black "$file"
            fi
            
            # Run ruff with all rules and fixes
            python3 -m ruff check --fix --unsafe-fixes --select ALL "$file" || true
            
            # Final black pass
            python3 -m black --quiet "$file" || true
            
            # Check if any errors remain
            if ! python3 -m ruff check "$file" > "$error_file" 2>&1; then
                echo "⚠️ Some linter errors remain in $file:"
                cat "$error_file"
            fi
        else
            echo "❌ Failed to fix all linter errors in $file after $max_retries attempts"
            echo "Remaining errors:"
            cat "$error_file"
            return 1
        fi
    done
}

# Update the main execution flow to use progress
echo "Running code quality checks..."

# Update directory structure first
run_operation "Directory Structure Update" "update_directory_structure" || handle_error "Failed to update directory structure" true

# Fix permissions only if needed
if ! find_python_files >/dev/null 2>&1; then
    run_operation "Permission Fix" "${PROJECT_ROOT}/scripts/setup_permissions.sh"
fi

# Fix formatting issues
run_operation "Python Formatting" "fix_python_formatting" || handle_error "Failed to fix Python formatting" true

# Fix specific issues in sequence
run_operation "Unused Imports" "fix_unused_imports" || handle_error "Failed to fix unused imports" true
run_operation "Indentation" "fix_indentation" || handle_error "Failed to fix indentation" true
run_operation "Line Length" "fix_line_length" || handle_error "Failed to fix line length" true
run_operation "Blank Lines" "fix_blank_lines" || handle_error "Failed to fix blank lines" true
run_operation "Code Complexity" "fix_code_complexity" || handle_error "Failed to fix code complexity" true

# Detect and fix duplicate code
run_operation "Duplicate Code" "fix_duplicate_code" || handle_error "Failed to fix duplicate code" true

# Run tests systematically
echo "🧪 Running tests systematically..."

# Run each test type separately
for test_type in "unit" "e2e" "integration" "fixtures" "reports"; do
    if [ -d "tests/$test_type" ]; then
        run_operation "Testing $test_type" "run_and_fix_tests '$test_type'" || echo "⚠️ $test_type tests failed, but continuing with other tests..."
    fi
done

# Fix any remaining linter errors
echo "🔍 Fixing any remaining linter errors..."
find_python_files | while read -r file; do
    run_operation "Linting $(basename "$file")" "fix_linter_errors '$file'" || echo "⚠️ Could not fix all linter errors in $file"
done

# Run final formatting pass
find_python_files | while read -r file; do
    run_operation "Final Format $(basename "$file")" "
        python3 -m black --quiet '$file' 2>/dev/null || true
        python3 -m isort --profile black '$file' 2>/dev/null || true
        python3 -m ruff check --fix --select ALL '$file' 2>/dev/null || true
    "
done

echo "✅ All tasks completed."
