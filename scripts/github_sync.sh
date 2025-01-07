#!/bin/bash
set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Source utility functions
source "${PROJECT_ROOT}/scripts/utils/progress_bar.sh"

# Load environment variables
if [ -f "${PROJECT_ROOT}/.env" ]; then
    source "${PROJECT_ROOT}/.env"
fi

# Initialize progress tracking
TOTAL_STEPS=5
CURRENT_STEP=0
init_progress $TOTAL_STEPS

echo "🔄 Syncing with GitHub..."

# Configure Git
run_with_spinner "Configuring Git" "
    cd \"${PROJECT_ROOT}\" &&
    git config user.name \"${GITHUB_USER_NAME}\" &&
    git config user.email \"${GITHUB_USER_EMAIL}\" &&
    git config core.fileMode true &&
    git config core.autocrlf input
"

# Initialize Git repository if not already initialized
run_with_spinner "Initializing Git repository" "
    cd \"${PROJECT_ROOT}\" &&
    if [ ! -d .git ]; then
        git init
    fi &&
    git remote remove origin 2>/dev/null || true &&
    git remote add origin \"https://${GITHUB_TOKEN}@github.com/${GITHUB_USER_NAME}/${GITHUB_REPO}.git\"
"

# Add all files
run_with_spinner "Adding files" "
    cd \"${PROJECT_ROOT}\" &&
    git add -A &&
    git add -u
"

# Commit changes
run_with_spinner "Committing changes" "
    cd \"${PROJECT_ROOT}\" &&
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
        SKIP=flake8,black,isort,end-of-file-fixer,check-yaml,check-added-large-files git commit --allow-empty -m \"Initial commit: Project management dashboard\"
    else
        git add -A &&
        git add -u &&
        SKIP=flake8,black,isort,end-of-file-fixer,check-yaml,check-added-large-files git commit --allow-empty -m \"Update project management dashboard\"
    fi
"

# Push to GitHub
run_with_spinner "Pushing to GitHub" "
    cd \"${PROJECT_ROOT}\" &&
    git branch -M ${GITHUB_BRANCH} &&
    git push -u origin ${GITHUB_BRANCH} --force
"

echo "✨ GitHub sync completed successfully!"
exit 0
