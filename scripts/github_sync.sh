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
        handle_error "$tool is not installed"
    fi
}

# Check required tools
echo "Checking required tools..."
validate_tool "git"
validate_tool "gh" # GitHub CLI

# Load environment variables
if [ -f "${PROJECT_ROOT}/.env" ]; then
    source "${PROJECT_ROOT}/.env"
else
    handle_error ".env file not found"
fi

# Initialize GitHub repository if needed
echo "Initializing GitHub repository..."
if [ ! -d "${PROJECT_ROOT}/.git" ]; then
    git init "${PROJECT_ROOT}" || handle_error "Failed to initialize git repository"
fi

# Configure git with .env credentials
git config user.name "${GITHUB_USER_NAME}" || handle_error "Failed to set git user name"
git config user.email "${GITHUB_USER_EMAIL}" || handle_error "Failed to set git email"

# Stage files
echo "Staging files..."
git add . || handle_error "Failed to stage files"

# Generate commit message based on changes
generate_commit_message() {
    local changes=""
    # Get list of changed files
    local changed_files=$(git diff --cached --name-status)
    # Get detailed diff stats
    local diff_stats=$(git diff --cached --stat)
    # Get actual content changes
    local diff_content=$(git diff --cached --unified=1)

    # Start with a descriptive prefix based on the type of changes
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
        # Analyze the types of changes
        local types=""
        if echo "$changed_files" | grep -q "^A"; then
            types="${types}feat: New files added, "
        fi
        if echo "$changed_files" | grep -q "^M"; then
            types="${types}update: Files modified, "
        fi
        if echo "$changed_files" | grep -q "^D"; then
            types="${types}chore: Files removed, "
        fi
        # Remove trailing comma and space
        types=$(echo "$types" | sed 's/, $//')

        # Add change type summary
        changes+="$types\n\n"

        # Add affected components
        local files_changed=$(echo "$changed_files" | cut -f2)
        changes+="Modified components:\n"
        changes+=$(echo "$files_changed" | xargs -n1 dirname | sort -u | grep -v '^.$' | sed 's/^/- /')

        # Add detailed changes
        changes+="\n\nChanges summary:\n$diff_stats"

        # Add specific code changes (limited to keep message reasonable)
        local code_changes=$(echo "$diff_content" | grep '^[+-][^+-]' | head -n 10)
        if [ ! -z "$code_changes" ]; then
            changes+="\n\nKey changes:\n$code_changes"
        fi
    else
        changes="initial: Project initialization and setup\n\nInitial commit with project structure and base configuration"
    fi

    echo "$changes"
}

# Create commit with generated message
echo "Creating commit..."
commit_msg=$(generate_commit_message)
git commit -m "$commit_msg" || handle_error "Failed to create commit"

# Set up GitHub remote if not already set
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "https://github.com/${GITHUB_USER_NAME}/${GITHUB_REPO}.git" || handle_error "Failed to add GitHub remote"
fi

# Push to GitHub using token for authentication
echo "Pushing to GitHub..."
git push https://${GITHUB_TOKEN}@github.com/${GITHUB_USER_NAME}/${GITHUB_REPO}.git ${GITHUB_BRANCH} || handle_error "Failed to push to GitHub"

echo "✓ GitHub synchronization completed"
exit 0
