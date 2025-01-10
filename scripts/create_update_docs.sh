#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Validation function
validate_tool() {
    local tool=$1
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "⚠️  Warning: $tool not found, skipping related documentation"
        return 1
    fi
    return 0
}

# Create documentation directory structure
echo "Setting up documentation directory structure..."
directories=(
    "build"
    "build/html"
    "source/_static"
    "source/_templates"
    "source/api"
    "source/guides"
    "source/tutorials"
    "source/examples"
)

for dir in "${directories[@]}"; do
    full_path="${PROJECT_ROOT}/docs/${dir}"
    mkdir -p "$full_path" || handle_error "Failed to create $dir directory"
    touch "$full_path/.gitkeep" 2>/dev/null || true
done

# Create default Sphinx configuration if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/docs/source/conf.py" ]; then
    echo "Creating Sphinx configuration..."
    cat > "${PROJECT_ROOT}/docs/source/conf.py" << 'EOF' || handle_error "Failed to create conf.py"
# Configuration file for Sphinx documentation builder

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'Project Management Dashboard'
copyright = '2024, Your Organization'
author = 'Your Organization'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = 'Project Management Dashboard Documentation'

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
EOF
fi

# Create index file if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/docs/source/index.rst" ]; then
    echo "Creating documentation index..."
    cat > "${PROJECT_ROOT}/docs/source/index.rst" << 'EOF' || handle_error "Failed to create index.rst"
Welcome to Project Management Dashboard
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guides/index
   tutorials/index
   api/index
   examples/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
EOF
fi

# Generate API documentation
echo "Generating API documentation..."
if validate_tool "sphinx-apidoc"; then
    sphinx-apidoc -f -o "${PROJECT_ROOT}/docs/source/api" "${PROJECT_ROOT}/dashboard" \
        -H "API Reference" \
        -A "Your Organization" \
        -V "1.0.0" \
        --separate \
        --module-first \
        --full || handle_error "Failed to generate API documentation"
fi

# Build HTML documentation
echo "Building HTML documentation..."
if validate_tool "sphinx-build"; then
    sphinx-build -b html \
        -d "${PROJECT_ROOT}/docs/build/doctrees" \
        -W \
        --color \
        -n \
        "${PROJECT_ROOT}/docs/source" \
        "${PROJECT_ROOT}/docs/build/html" || handle_error "Failed to build documentation"
fi

# Create PDF documentation if available
if validate_tool "sphinx-build" && validate_tool "latexmk"; then
    echo "Building PDF documentation..."
    sphinx-build -b latex \
        -d "${PROJECT_ROOT}/docs/build/doctrees" \
        "${PROJECT_ROOT}/docs/source" \
        "${PROJECT_ROOT}/docs/build/latex" || true

    # Build PDF if latex build succeeded
    if [ -f "${PROJECT_ROOT}/docs/build/latex/projectmanagementdashboard.tex" ]; then
        (cd "${PROJECT_ROOT}/docs/build/latex" && make) || true
    fi
fi

# Set permissions
echo "Setting documentation permissions..."
find "${PROJECT_ROOT}/docs" -type d -exec chmod 755 {} \;
find "${PROJECT_ROOT}/docs" -type f -exec chmod 644 {} \;

# Verify documentation
echo "Verifying documentation..."
if [ -f "${PROJECT_ROOT}/docs/build/html/index.html" ]; then
    echo "✓ HTML documentation built successfully"
else
    echo "⚠️  HTML documentation build failed"
fi

if [ -f "${PROJECT_ROOT}/docs/build/latex/projectmanagementdashboard.pdf" ]; then
    echo "✓ PDF documentation built successfully"
else
    echo "⚠️  PDF documentation not available"
fi

echo "✓ Documentation update completed"
exit 0
