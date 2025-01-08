#!/bin/bash

# Exit on error
set -e

# Function to check if virtual environment is active
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Error: Virtual environment not activated"
        echo "Please activate your virtual environment first:"
        echo "source .venv/bin/activate"
        exit 1
    fi
}

# Function to install type stubs
install_stubs() {
    echo "Installing type stubs..."
    
    # Core dependencies
    pip install types-Flask
    pip install types-Werkzeug
    pip install types-requests
    pip install types-python-dateutil
    pip install types-PyYAML
    pip install types-psutil
    pip install types-aiohttp
    pip install types-redis
    pip install types-setuptools
    pip install types-six
    pip install types-urllib3
    
    # Testing dependencies
    pip install types-pytest
    pip install types-pytest-lazy-fixture
    
    # Development dependencies
    pip install types-click
    pip install types-docutils
    pip install types-Markdown
    pip install types-pyOpenSSL
    pip install types-cryptography
    
    echo "Type stubs installation complete!"
}

# Function to verify installations
verify_installations() {
    echo "Verifying installations..."
    
    # Create a temporary Python file for imports
    TMP_FILE=$(mktemp)
    cat > "$TMP_FILE" << EOL
from typing import *
import flask
import werkzeug
import requests
import dateutil
import yaml
import psutil
import aiohttp
import redis
import setuptools
import six
import urllib3
import pytest
import click
import docutils
import markdown
import OpenSSL
import cryptography
EOL
    
    # Run mypy on the temporary file
    if mypy "$TMP_FILE"; then
        echo "All type stubs verified successfully!"
    else
        echo "Warning: Some type stubs may not be working correctly"
    fi
    
    # Clean up
    rm "$TMP_FILE"
}

# Function to update existing stubs
update_stubs() {
    echo "Updating existing type stubs..."
    pip install --upgrade types-*
    echo "Type stubs update complete!"
}

# Main script
main() {
    # Check if virtual environment is active
    check_venv
    
    # Parse command line arguments
    case "$1" in
        --update)
            update_stubs
            ;;
        --verify)
            verify_installations
            ;;
        *)
            install_stubs
            verify_installations
            ;;
    esac
}

# Run main function with all arguments
main "$@"
