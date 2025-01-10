#!/bin/bash
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${0}")/.." && pwd)"

# Error handling
handle_error() {
    echo "❌ Error: $1"
    exit 1
}

# Check for dashboard config example
if [ ! -f "${PROJECT_ROOT}/config/dashboard.json.example" ]; then
    handle_error "dashboard.json.example not found"
fi

# Create dashboard config if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/config/dashboard.json" ]; then
    echo "Creating dashboard configuration..."
    cp "${PROJECT_ROOT}/config/dashboard.json.example" "${PROJECT_ROOT}/config/dashboard.json" || \
        handle_error "Failed to create dashboard.json"
else
    # Check if example config is newer
    if [ "${PROJECT_ROOT}/config/dashboard.json.example" -nt "${PROJECT_ROOT}/config/dashboard.json" ]; then
        echo "Warning: dashboard.json.example is newer than dashboard.json"
        echo "You may want to review and update your configuration"
    fi
fi

# Validate dashboard config
if [ ! -s "${PROJECT_ROOT}/config/dashboard.json" ]; then
    handle_error "dashboard.json is empty"
fi

# Create and validate required directories
echo "Setting up dashboard directory structure..."
directories=(
    "static/css"
    "static/js"
    "static/img"
    "static/fonts"
    "templates"
    "templates/partials"
    "templates/layouts"
)

for dir in "${directories[@]}"; do
    full_path="${PROJECT_ROOT}/dashboard/${dir}"
    mkdir -p "$full_path" || handle_error "Failed to create $dir directory"

    # Add .gitkeep to preserve empty directories
    touch "$full_path/.gitkeep" 2>/dev/null || true
done

# Create default index.html if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/dashboard/templates/index.html" ]; then
    echo "Creating default index.html..."
    cat > "${PROJECT_ROOT}/dashboard/templates/index.html" << 'EOF' || handle_error "Failed to create index.html"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Management Dashboard</title>
</head>
<body>
    <h1>Welcome to Project Management Dashboard</h1>
    <p>Dashboard is successfully installed.</p>
</body>
</html>
EOF
fi

# Create default base template if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/dashboard/templates/base.html" ]; then
    echo "Creating base template..."
    cat > "${PROJECT_ROOT}/dashboard/templates/base.html" << 'EOF' || handle_error "Failed to create base.html"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Project Management Dashboard{% endblock %}</title>
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        {% block header %}{% endblock %}
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>
        {% block footer %}{% endblock %}
    </footer>
    {% block scripts %}{% endblock %}
</body>
</html>
EOF
fi

# Create default CSS file if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/dashboard/static/css/main.css" ]; then
    echo "Creating main CSS file..."
    cat > "${PROJECT_ROOT}/dashboard/static/css/main.css" << 'EOF' || handle_error "Failed to create main.css"
/* Base styles */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --background-color: #f8f9fa;
    --text-color: #212529;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
    margin: 0;
    padding: 0;
}

/* Layout */
header {
    background-color: var(--primary-color);
    color: white;
    padding: 1rem;
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

footer {
    background-color: var(--secondary-color);
    color: white;
    padding: 1rem;
    text-align: center;
    position: fixed;
    bottom: 0;
    width: 100%;
}
EOF
fi

# Create default JavaScript file if it doesn't exist
if [ ! -f "${PROJECT_ROOT}/dashboard/static/js/main.js" ]; then
    echo "Creating main JavaScript file..."
    cat > "${PROJECT_ROOT}/dashboard/static/js/main.js" << 'EOF' || handle_error "Failed to create main.js"
// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
});
EOF
fi

echo "✓ Dashboard setup completed"
exit 0
