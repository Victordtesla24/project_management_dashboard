# Project Management Dashboard

A Python-based dashboard for monitoring system and process metrics.

## Features

- Real-time system metrics monitoring (CPU, memory, disk usage)
- Process-level metrics tracking
- Historical metrics collection and visualization
- Alert system for resource usage thresholds
- Pre-commit hooks for code quality
- Type checking with mypy
- Unit tests with pytest

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/project_management_dashboard.git
cd project_management_dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Development

### Running Tests

```bash
pytest tests/
```

### Type Checking

```bash
mypy dashboard/
```

### Code Formatting

```bash
black dashboard/
```

### Linting

```bash
flake8 dashboard/
```

## Project Structure

```
project_management_dashboard/
├── dashboard/
│   ├── __init__.py
│   └── metrics/
│       ├── __init__.py
│       └── collector.py
├── tests/
│   ├── __init__.py
│   └── test_metrics_collector.py
├── .flake8
├── .pre-commit-config.yaml
├── mypy.ini
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
