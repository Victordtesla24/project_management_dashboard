#!/bin/bash

# Remove executable permissions from all files
find . -type f -exec chmod -x {} \;

# Add executable permissions back to shell scripts
find . -type f -name "*.sh" -exec chmod +x {} \;

# Add executable permissions to Python scripts that need it
chmod +x run.py
chmod +x wsgi.py
chmod +x dashboard/run.py
