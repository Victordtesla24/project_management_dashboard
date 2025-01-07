#!/bin/bash
set -euo pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Source the progress bar utility
source "${SCRIPT_DIR}/utils/progress_bar.sh"

# Initialize progress
init_progress 3

# Clear screen and show header
clear
printf "\n🐙 Setting Up GitHub v1.0.0\n\n"

# Create GitHub Actions directory
run_with_spinner "Creating GitHub Actions directory" \
    mkdir -p "${PROJECT_ROOT}/.github/workflows"

# Create GitHub Actions workflow file
run_with_spinner "Creating GitHub Actions workflow" \
cat > "${PROJECT_ROOT}/.github/workflows/ci.yml" << 'EOL'
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        python -m pytest tests/
    - name: Run type checks
      run: |
        mypy dashboard/
EOL

# Create GitHub issue templates
run_with_spinner "Creating issue templates" \
    mkdir -p "${PROJECT_ROOT}/.github/ISSUE_TEMPLATE" && \
cat > "${PROJECT_ROOT}/.github/ISSUE_TEMPLATE/bug_report.md" << 'EOL'
---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Additional context**
Add any other context about the problem here.
EOL

cat > "${PROJECT_ROOT}/.github/ISSUE_TEMPLATE/feature_request.md" << 'EOL'
---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: enhancement
assignees: ''

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
EOL

# Complete progress
complete_progress "GitHub setup completed"
