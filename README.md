# Project Management Dashboard

A real-time system metrics dashboard with WebSocket support for monitoring system resources and performance metrics.

## Features

- Real-time system metrics monitoring (CPU, Memory, Disk usage)
- WebSocket-based live updates
- InfluxDB integration for metrics storage
- Prometheus integration for metrics exposition
- Configurable alert thresholds
- Authentication and session management
- Responsive web interface
- Dark/Light theme support
- Customizable dashboard layouts

## Requirements

- Python 3.9 or higher
- InfluxDB 2.x
- Node.js 14+ (for frontend development)
- Modern web browser with WebSocket support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/project-management-dashboard.git
cd project-management-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create configuration file:
```bash
cp config.json.example config.json
```

5. Edit the configuration file with your settings:
```json
{
    "environment": "development",
    "metrics": {
        "collection_interval": 5,
        "enabled_metrics": ["cpu", "memory", "disk"],
        "thresholds": {
            "cpu": 80,
            "memory": 90,
            "disk": 85
        }
    },
    "websocket": {
        "host": "localhost",
        "port": 8765,
        "ssl": false
    },
    "influxdb": {
        "url": "http://localhost:8086",
        "token": "your-token",
        "org": "your-org",
        "bucket": "metrics"
    }
}
```

## Running the Dashboard

1. Start the dashboard:
```bash
./dashboard/run.sh
```

2. Access the dashboard:
- Web interface: http://localhost:5000
- WebSocket server: ws://localhost:8765

3. Stop the dashboard:
```bash
./dashboard/stop.sh
```

## Development

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=dashboard

# Run specific test categories
pytest -m "not slow"
pytest -m "not integration"
pytest -m "not e2e"
```

4. Code formatting:
```bash
# Format code
black dashboard tests

# Sort imports
isort dashboard tests

# Type checking
mypy dashboard
```

## Testing

The project includes several types of tests:

- Unit tests: `dashboard/tests/unit/`
- Integration tests: `dashboard/tests/integration/`
- End-to-end tests: `dashboard/tests/e2e/`

To run specific test suites:

```bash
# Unit tests only
pytest dashboard/tests/unit/

# Integration tests
pytest dashboard/tests/integration/

# E2E tests
pytest dashboard/tests/e2e/
```

## Project Structure

```
project_management_dashboard/
├── dashboard/
│   ├── __init__.py
│   ├── app.py              # Flask application
│   ├── metrics.py          # Metrics collection
│   ├── routes.py           # API routes
│   ├── utils.py            # Utility functions
│   ├── config/             # Configuration management
│   ├── websocket/          # WebSocket server
│   ├── static/             # Static assets
│   └── templates/          # HTML templates
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── fixtures/         # Test fixtures
├── docs/                 # Documentation
├── scripts/             # Utility scripts
└── requirements.txt     # Dependencies
```

## Configuration

The dashboard can be configured through:

1. Configuration file (`config.json`)
2. Environment variables
3. Command line arguments

Environment variables override configuration file settings:

- `CONFIG_PATH`: Path to configuration file
- `APP_ENV`: Application environment
- `METRICS_INTERVAL`: Metrics collection interval
- `WS_PORT`: WebSocket server port
- `INFLUXDB_URL`: InfluxDB URL
- `INFLUXDB_TOKEN`: InfluxDB authentication token
- `SECRET_KEY`: Flask secret key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
