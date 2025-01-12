#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1" >&2
    exit 1
}

# Function to check Python version
check_python_version() {
    echo "Checking Python version..."
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))') || handle_error "Failed to get Python version"
    REQUIRED_VERSION="3.9"

    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        handle_error "Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    fi
    echo "Python version $PYTHON_VERSION detected"
}

# Function to create and activate virtual environment
create_venv() {
    echo "Setting up virtual environment..."
    VENV_DIR="${PROJECT_ROOT}/.venv"
    
    if [ -d "$VENV_DIR" ]; then
        echo "Removing existing virtual environment..."
        rm -rf "$VENV_DIR" || handle_error "Failed to remove existing virtual environment"
    fi
    
    python3 -m venv "$VENV_DIR" || handle_error "Failed to create virtual environment"
    echo "Virtual environment created"

    # Activate virtual environment
    source "${VENV_DIR}/bin/activate" || handle_error "Failed to activate virtual environment"

    # Upgrade pip
    python3 -m pip install --upgrade pip || handle_error "Failed to upgrade pip"
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    
    # Install project dependencies
    if [ -f "${PROJECT_ROOT}/setup.py" ]; then
        pip install -e ".[dev]" || handle_error "Failed to install project dependencies"
        pip install -e ".[test]" || handle_error "Failed to install test dependencies"
    else
        echo "⚠️  Warning: setup.py not found, skipping project installation"
    fi

    # Install type stubs if script exists
    if [ -f "${PROJECT_ROOT}/scripts/install_type_stubs.sh" ]; then
        bash "${PROJECT_ROOT}/scripts/install_type_stubs.sh" || handle_error "Failed to install type stubs"
    fi
}

# Function to set up pre-commit hooks
setup_pre_commit() {
    echo "Setting up pre-commit hooks..."
    if command -v pre-commit >/dev/null 2>&1; then
        pre-commit install || handle_error "Failed to install pre-commit hooks"
        pre-commit install --hook-type commit-msg || handle_error "Failed to install commit-msg hook"
    else
        echo "⚠️  Warning: pre-commit not found, skipping hook setup"
    fi
}

# Function to create necessary directories
create_directories() {
    echo "Creating necessary directories..."
    directories=(
        "logs"
        "instance"
        "coverage_report"
        "certs"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "${PROJECT_ROOT}/${dir}" || handle_error "Failed to create ${dir} directory"
    done
}

# Function to create initial configuration
create_config() {
    echo "Creating initial configuration..."
    if [ -f "${PROJECT_ROOT}/config.json.example" ] && [ ! -f "${PROJECT_ROOT}/config.json" ]; then
        cp "${PROJECT_ROOT}/config.json.example" "${PROJECT_ROOT}/config.json" || handle_error "Failed to create config.json"
        echo "Created config.json from example"
    else
        echo "config.json already exists or example not found"
    fi
}

# Function to set up Git hooks
setup_git_hooks() {
    echo "Setting up Git hooks..."
    HOOKS_DIR="${PROJECT_ROOT}/.git/hooks"
    
    if [ ! -d "$HOOKS_DIR" ]; then
        mkdir -p "$HOOKS_DIR" || handle_error "Failed to create hooks directory"
    fi

    # Create pre-push hook
    cat > "${HOOKS_DIR}/pre-push" << 'EOL' || handle_error "Failed to create pre-push hook"
#!/bin/bash
./scripts/run_tests.sh --unit
EOL
    chmod +x "${HOOKS_DIR}/pre-push" || handle_error "Failed to set pre-push hook permissions"

    # Create pre-commit hook
    cat > "${HOOKS_DIR}/pre-commit" << 'EOL' || handle_error "Failed to create pre-commit hook"
#!/bin/bash
./scripts/lint_and_test.sh
EOL
    chmod +x "${HOOKS_DIR}/pre-commit" || handle_error "Failed to set pre-commit hook permissions"
}

# Function to verify installation
verify_installation() {
    echo "Verifying installation..."
    
    # Check critical packages
    packages=("flask" "pytest" "mypy")
    for package in "${packages[@]}"; do
        if ! python3 -c "import $package" >/dev/null 2>&1; then
            echo "⚠️  Warning: $package not properly installed"
        else
            echo "✓ $package installed successfully"
        fi
    done
}

# Main script
main() {
    echo "Setting up development environment..."

    # Run setup steps
    check_python_version
    create_venv
    install_dependencies
    setup_pre_commit
    create_directories
    create_config
    setup_git_hooks
    verify_installation

    echo
    echo "✓ Development environment setup complete!"
    echo
    echo "Next steps:"
    echo "1. Review and update config.json with your settings"
    echo "2. Run './dashboard/run.sh' to start the dashboard"
    echo "3. Run './scripts/run_tests.sh' to run tests"
    echo
    echo "For more information, see README.md"
}

# Run main function
main "$@"
