#!/bin/bash
set -e

# Create Streamlit config to bypass welcome screen
mkdir -p ~/.streamlit
echo '[general]
showWarningOnDirectExecution = false

[browser]
gatherUsageStats = false' > ~/.streamlit/config.toml

echo "Starting Streamlit server..."
streamlit run src/pages/monitor.py --server.headless=true &
STREAMLIT_PID=$!
echo "Streamlit PID: $STREAMLIT_PID"

# Wait for server to be ready
echo "Waiting for Streamlit server to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=1

while ! curl -s http://localhost:8501 > /dev/null; do
    if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
        echo "Server failed to start"
        kill $STREAMLIT_PID
        exit 1
    fi
    echo "Attempt $ATTEMPT: Server not ready yet..."
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
done

echo "Server is ready!"
echo "Waiting for UI to be fully loaded..."
sleep 10

echo "Running e2e tests..."
pytest tests/e2e/test_monitor_e2e.py -v

echo "Cleaning up..."
echo "Killing Streamlit process $STREAMLIT_PID"
kill $STREAMLIT_PID || true
