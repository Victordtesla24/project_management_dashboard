#!/bin/bash

# Exit on error
set -e

# Function to check Python version
check_python_version() {
    echo "Checking Python version..."
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.9"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        echo "Error: Python $REQUIRED_VERSION or higher is required"
        exit 1
    fi
    echo "Python version $PYTHON_VERSION detected"
}

# Function to create virtual environment
create_venv() {
    echo "Setting up virtual environment..."
    if [ -d ".venv" ]; then
        echo "Virtual environment already exists"
    else
        python3 -m venv .venv
        echo "Virtual environment created"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    
    # Install project in development mode
    pip install -e ".[dev]"
    
    # Install test dependencies
    pip install -e ".[test]"
    
    # Install type stubs
    ./scripts/install_type_stubs.sh
}

# Function to set up pre-commit hooks
setup_pre_commit() {
    echo "Setting up pre-commit hooks..."
    pre-commit install
    pre-commit install --hook-type commit-msg
}

# Function to create necessary directories
create_directories() {
    echo "Creating necessary directories..."
    mkdir -p logs
    mkdir -p instance
    mkdir -p coverage_report
    mkdir -p certs
}

# Function to create initial configuration
create_config() {
    echo "Creating initial configuration..."
    if [ ! -f "config.json" ]; then
        cp config.json.example config.json
        echo "Created config.json from example"
    else
        echo "config.json already exists"
    fi
}

# Function to set up Git hooks
setup_git_hooks() {
    echo "Setting up Git hooks..."
    
    # Create pre-push hook
    cat > .git/hooks/pre-push << 'EOL'
#!/bin/bash
./scripts/run_tests.sh --unit
EOL
    chmod +x .git/hooks/pre-push
    
    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOL'
#!/bin/bash
./scripts/lint_and_test.sh
EOL
    chmod +x .git/hooks/pre-commit
}

# Function to verify installation
verify_installation() {
    echo "Verifying installation..."
    
    # Run basic checks
    python3 -c "import flask; print('Flask installed successfully')"
    python3 -c "import pytest; print('Pytest installed successfully')"
    python3 -c "import mypy; print('Mypy installed successfully')"
    
    # Run a basic test
    ./scripts/run_tests.sh --unit --quiet || true
}

# Function to show completion message
show_completion() {
    echo
    echo "Development environment setup complete!"
    echo
    echo "Next steps:"
    echo "1. Review and update config.json with your settings"
    echo "2. Run './dashboard/run.sh' to start the dashboard"
    echo "3. Run './scripts/run_tests.sh' to run tests"
    echo
    echo "For more information, see README.md"
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
    show_completion
}

# Run main function
main "$@"
