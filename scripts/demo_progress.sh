#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Create demo directory structure
echo "Setting up demo directory structure..."
directories=(
    "static/demo/data"
    "static/demo/charts"
    "static/demo/screenshots"
    "static/demo/reports"
)

for dir in "${directories[@]}"; do
    full_path="${PROJECT_ROOT}/dashboard/${dir}"
    mkdir -p "$full_path" || handle_error "Failed to create $dir directory"
done

# Generate demo data
echo "Generating demo data..."

# Progress data
PROGRESS_FILE="${PROJECT_ROOT}/dashboard/static/demo/data/progress.json"
cat > "$PROGRESS_FILE" << 'EOF' || handle_error "Failed to create progress data"
{
    "tasks": [
        {
            "id": "TASK-001",
            "name": "Project Setup",
            "description": "Initial project configuration and environment setup",
            "progress": 100,
            "status": "completed",
            "start_date": "2024-01-01",
            "end_date": "2024-01-02",
            "assignee": "John Doe"
        },
        {
            "id": "TASK-002",
            "name": "Database Implementation",
            "description": "Set up and configure database schemas",
            "progress": 75,
            "status": "in_progress",
            "start_date": "2024-01-03",
            "end_date": "2024-01-07",
            "assignee": "Jane Smith"
        },
        {
            "id": "TASK-003",
            "name": "API Development",
            "description": "Implement REST API endpoints",
            "progress": 50,
            "status": "in_progress",
            "start_date": "2024-01-04",
            "end_date": "2024-01-08",
            "assignee": "Bob Wilson"
        },
        {
            "id": "TASK-004",
            "name": "Frontend Development",
            "description": "Build user interface components",
            "progress": 25,
            "status": "in_progress",
            "start_date": "2024-01-05",
            "end_date": "2024-01-10",
            "assignee": "Alice Brown"
        },
        {
            "id": "TASK-005",
            "name": "Testing",
            "description": "Implement test suites and run QA",
            "progress": 0,
            "status": "pending",
            "start_date": "2024-01-11",
            "end_date": "2024-01-15",
            "assignee": "Charlie Davis"
        }
    ],
    "metadata": {
        "total_tasks": 5,
        "completed_tasks": 1,
        "in_progress_tasks": 3,
        "pending_tasks": 1,
        "overall_progress": 50,
        "last_updated": "2024-01-15T12:00:00Z"
    }
}
EOF

# Generate metrics data
METRICS_FILE="${PROJECT_ROOT}/dashboard/static/demo/data/metrics.json"
cat > "$METRICS_FILE" << 'EOF' || handle_error "Failed to create metrics data"
{
    "performance": {
        "response_time": {
            "avg": 250,
            "min": 100,
            "max": 500,
            "p95": 450
        },
        "throughput": {
            "requests_per_second": 100,
            "concurrent_users": 50
        },
        "errors": {
            "rate": 0.1,
            "count": 5
        }
    },
    "resources": {
        "cpu": {
            "usage": 45,
            "cores": 4
        },
        "memory": {
            "usage": 65,
            "total": 16384
        },
        "disk": {
            "usage": 55,
            "total": 1024
        }
    }
}
EOF

# Generate chart data
CHART_FILE="${PROJECT_ROOT}/dashboard/static/demo/charts/chart_data.json"
cat > "$CHART_FILE" << 'EOF' || handle_error "Failed to create chart data"
{
    "daily_progress": [
        {"date": "2024-01-01", "completed": 5, "pending": 15},
        {"date": "2024-01-02", "completed": 8, "pending": 12},
        {"date": "2024-01-03", "completed": 12, "pending": 8},
        {"date": "2024-01-04", "completed": 15, "pending": 5},
        {"date": "2024-01-05", "completed": 18, "pending": 2}
    ],
    "resource_usage": [
        {"timestamp": "2024-01-01T00:00:00Z", "cpu": 45, "memory": 65, "disk": 55},
        {"timestamp": "2024-01-02T00:00:00Z", "cpu": 50, "memory": 70, "disk": 58},
        {"timestamp": "2024-01-03T00:00:00Z", "cpu": 48, "memory": 68, "disk": 60},
        {"timestamp": "2024-01-04T00:00:00Z", "cpu": 52, "memory": 72, "disk": 62},
        {"timestamp": "2024-01-05T00:00:00Z", "cpu": 55, "memory": 75, "disk": 65}
    ]
}
EOF

# Generate demo report
REPORT_FILE="${PROJECT_ROOT}/dashboard/static/demo/reports/demo_report.md"
cat > "$REPORT_FILE" << 'EOF' || handle_error "Failed to create demo report"
# Project Management Dashboard Demo

## Overview
This demo showcases the key features and capabilities of the Project Management Dashboard.

## Features Demonstrated
1. Task Progress Tracking
2. Resource Monitoring
3. Performance Metrics
4. Chart Visualizations

## Sample Data
The demo includes sample data for:
- Project tasks and their progress
- System resource utilization
- Performance metrics
- Historical trends

## Usage
Access the dashboard at http://localhost:3000 to view the demo.
EOF

# Set permissions
echo "Setting permissions..."
find "${PROJECT_ROOT}/dashboard/static/demo" -type d -exec chmod 755 {} \;
find "${PROJECT_ROOT}/dashboard/static/demo" -type f -exec chmod 644 {} \;

# Verify demo files
echo "Verifying demo files..."
verification_failed=0

verify_file() {
    local file=$1
    if [ ! -f "$file" ]; then
        echo "⚠️  Missing file: $file"
        verification_failed=1
    elif [ ! -s "$file" ]; then
        echo "⚠️  Empty file: $file"
        verification_failed=1
    fi
}

verify_file "$PROGRESS_FILE"
verify_file "$METRICS_FILE"
verify_file "$CHART_FILE"
verify_file "$REPORT_FILE"

# Verify JSON files are valid
for json_file in "$PROGRESS_FILE" "$METRICS_FILE" "$CHART_FILE"; do
    if ! jq empty "$json_file" 2>/dev/null; then
        echo "⚠️  Invalid JSON in: $json_file"
        verification_failed=1
    fi
done

if [ $verification_failed -eq 1 ]; then
    handle_error "Demo data verification failed"
fi

echo "✓ Demo data generation completed"
exit 0
