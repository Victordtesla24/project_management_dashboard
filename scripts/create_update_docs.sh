#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Initialize progress bar (5 steps)
init_progress 5

echo "📚 Creating/updating documentation..."

# Create documentation structure
run_with_spinner "Creating documentation structure" "
    mkdir -p \"${PROJECT_ROOT}/docs/source\" &&
    mkdir -p \"${PROJECT_ROOT}/docs/build/html\" &&
    mkdir -p \"${PROJECT_ROOT}/docs/source/_static\" &&
    mkdir -p \"${PROJECT_ROOT}/docs/source/_templates\"
"

# Create Sphinx configuration
run_with_spinner "Creating Sphinx configuration" "
    cat > \"${PROJECT_ROOT}/docs/source/conf.py\" << 'EOF'
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'Project Management Dashboard'
copyright = '2024, Your Organization'
author = 'Your Organization'

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
html_title = 'Project Management Dashboard'
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
EOF
"

# Create documentation index
run_with_spinner "Creating documentation index" "
    cat > \"${PROJECT_ROOT}/docs/source/index.rst\" << 'EOF'
Welcome to Project Management Dashboard
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   development
   changelog

Introduction
-----------
The Project Management Dashboard is a comprehensive monitoring and management solution
that provides real-time insights into system metrics, test coverage, and project status.

Features
--------
* Real-time system metrics monitoring
* Test coverage tracking and reporting
* Project status visualization
* Automated documentation generation
* Continuous integration support

Quick Start
----------
1. Clone the repository
2. Run \`setup.sh\` to initialize the environment
3. Start the dashboard using \`run_dashboard.sh\`
4. Access the dashboard at http://localhost:8501

For more detailed information, please refer to the installation and usage guides.

Indices and tables
==================
* :ref:\`genindex\`
* :ref:\`modindex\`
* :ref:\`search\`
EOF
"

# Create additional documentation files
run_with_spinner "Creating additional documentation" "
    # Installation guide
    cat > \"${PROJECT_ROOT}/docs/source/installation.rst\" << 'EOF'
Installation Guide
================

Prerequisites
------------
* Python 3.8 or higher
* pip package manager
* Git

Installation Steps
----------------
1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/your-org/project-management-dashboard.git
   cd project-management-dashboard
   \`\`\`

2. Run the setup script:
   \`\`\`bash
   ./scripts/setup.sh
   \`\`\`

3. Verify the installation:
   \`\`\`bash
   ./scripts/verify_and_fix.sh
   \`\`\`

Configuration
------------
The dashboard can be configured by editing the following files:
* \`config/dashboard.json\` - Dashboard settings
* \`config/metrics.json\` - Metrics collection settings
* \`.env\` - Environment variables
EOF

    # Usage guide
    cat > \"${PROJECT_ROOT}/docs/source/usage.rst\" << 'EOF'
Usage Guide
==========

Starting the Dashboard
-------------------
1. Activate the virtual environment:
   \`\`\`bash
   source .venv/bin/activate
   \`\`\`

2. Start the dashboard:
   \`\`\`bash
   ./scripts/run_dashboard.sh
   \`\`\`

3. Open your browser and navigate to http://localhost:8501

Features
-------
* **System Metrics**: Monitor CPU, memory, and disk usage
* **Test Coverage**: Track test coverage and quality metrics
* **Project Status**: View project health and progress
* **Documentation**: Access auto-generated documentation

Customization
-----------
The dashboard can be customized by:
* Adding new metrics collectors
* Creating custom visualizations
* Modifying the update frequency
* Configuring alert thresholds
EOF
"

# Generate documentation
run_with_spinner "Generating documentation" "
    cd \"${PROJECT_ROOT}/docs\" &&
    sphinx-build -b html source build/html
"

echo "✨ Documentation created/updated successfully!"
