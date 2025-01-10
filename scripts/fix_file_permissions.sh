#!/bin/bash

# Set correct permissions for different file types
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type f -name "*.json" -exec chmod 644 {} \;
find . -type f -name "*.yaml" -exec chmod 644 {} \;
find . -type f -name "*.yml" -exec chmod 644 {} \;
find . -type f -name "*.md" -exec chmod 644 {} \;
find . -type f -name "*.html" -exec chmod 644 {} \;
find . -type f -name "*.css" -exec chmod 644 {} \;
find . -type f -name "*.js" -exec chmod 644 {} \;
find . -type f -name "*.rst" -exec chmod 644 {} \;
find . -type f -name "*.txt" -exec chmod 644 {} \;
find . -type f -name "*.ini" -exec chmod 644 {} \;
find . -type f -name "*.service" -exec chmod 644 {} \;

# Set executable permissions only for shell scripts
find . -type f -name "*.sh" -exec chmod 755 {} \;

# Set specific permissions for special files
chmod 644 .env.example
chmod 644 .gitignore
chmod 644 .flake8
chmod 644 .bandit.yaml
chmod 644 .pre-commit-config.yaml
chmod 644 .clinerules

# Set directory permissions
find . -type d -exec chmod 755 {} \;

# Ensure logs directory has correct permissions
mkdir -p logs
chmod 775 logs
