#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Create tracking directory structure
echo "Setting up tracking directory structure..."
directories=(
    "tracking/metrics"
    "tracking/logs"
    "tracking/reports"
    "tracking/history"
)

for dir in "${directories[@]}"; do
    full_path="${PROJECT_ROOT}/${dir}"
    mkdir -p "$full_path" || handle_error "Failed to create $dir directory"
done

# Initialize metrics file if it doesn't exist
METRICS_FILE="${PROJECT_ROOT}/tracking/metrics/implementation_metrics.json"
if [ ! -f "$METRICS_FILE" ]; then
    echo "Initializing metrics file..."
    cat > "$METRICS_FILE" << 'EOF' || handle_error "Failed to create metrics file"
{
    "metrics": {
        "code_coverage": 0,
        "test_count": 0,
        "bug_count": 0,
        "feature_count": 0,
        "last_updated": "",
        "complexity": {
            "cyclomatic": 0,
            "cognitive": 0
        },
        "quality": {
            "maintainability": 0,
            "technical_debt": 0
        }
    },
    "features": [],
    "bugs": [],
    "tests": [],
    "history": []
}
EOF
fi

# Update metrics from coverage report
echo "Updating code coverage metrics..."
COVERAGE_FILE="${PROJECT_ROOT}/reports/coverage/index.html"
if [ -f "$COVERAGE_FILE" ]; then
    coverage=$(grep -o '[0-9]\+%' "$COVERAGE_FILE" | head -1 | tr -d '%')
    if [ -n "$coverage" ]; then
        # Use temporary file for atomic update
        tmp_file=$(mktemp)
        jq --arg cov "$coverage" --arg date "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" '
            .metrics.code_coverage = ($cov|tonumber) |
            .metrics.last_updated = $date
        ' "$METRICS_FILE" > "$tmp_file" && mv "$tmp_file" "$METRICS_FILE"
    fi
fi

# Update test count
echo "Updating test metrics..."
TEST_COUNT=$(find "${PROJECT_ROOT}/tests" -name "test_*.py" -exec grep -l "def test_" {} \; | wc -l)
if [ -n "$TEST_COUNT" ]; then
    tmp_file=$(mktemp)
    jq --arg count "$TEST_COUNT" '
        .metrics.test_count = ($count|tonumber)
    ' "$METRICS_FILE" > "$tmp_file" && mv "$tmp_file" "$METRICS_FILE"
fi

# Create historical snapshot
echo "Creating historical snapshot..."
SNAPSHOT_FILE="${PROJECT_ROOT}/tracking/history/metrics_$(date +%Y%m%d_%H%M%S).json"
cp "$METRICS_FILE" "$SNAPSHOT_FILE" || handle_error "Failed to create snapshot"

# Clean up old snapshots (keep last 30 days)
find "${PROJECT_ROOT}/tracking/history" -name "metrics_*.json" -type f -mtime +30 -delete

# Generate metrics report
echo "Generating metrics report..."
REPORT_FILE="${PROJECT_ROOT}/tracking/reports/metrics_report.txt"
{
    echo "Implementation Metrics Report"
    echo "==========================="
    echo "Generated: $(date)"
    echo
    echo "Code Coverage: $(jq -r '.metrics.code_coverage' "$METRICS_FILE")%"
    echo "Test Count: $(jq -r '.metrics.test_count' "$METRICS_FILE")"
    echo "Bug Count: $(jq -r '.metrics.bug_count' "$METRICS_FILE")"
    echo "Feature Count: $(jq -r '.metrics.feature_count' "$METRICS_FILE")"
    echo "Last Updated: $(jq -r '.metrics.last_updated' "$METRICS_FILE")"
} > "$REPORT_FILE"

# Set permissions
echo "Setting permissions..."
find "${PROJECT_ROOT}/tracking" -type d -exec chmod 755 {} \;
find "${PROJECT_ROOT}/tracking" -type f -exec chmod 644 {} \;

# Verify metrics file
echo "Verifying metrics file..."
if ! jq empty "$METRICS_FILE" 2>/dev/null; then
    handle_error "Invalid JSON in metrics file"
fi

echo "✓ Implementation tracking completed"
exit 0
