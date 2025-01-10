Configuration
=============

This guide covers all configuration options for the Project Management Dashboard.

Configuration Files
-----------------

The dashboard uses several configuration files:

* ``config/dashboard.json``: Main application configuration
* ``config/websocket.json``: WebSocket server settings
* ``config/influxdb.json``: Metrics storage configuration
* ``config/prometheus.json``: Prometheus integration settings

Main Configuration (dashboard.json)
--------------------------------

Basic Settings
~~~~~~~~~~~~

.. code-block:: json

    {
        "server": {
            "host": "localhost",
            "port": 8000,
            "debug": false,
            "workers": 4
        },
        "logging": {
            "level": "INFO",
            "file": "logs/dashboard.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "max_size": 10485760,
            "backup_count": 5
        }
    }

Database Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "dashboard",
            "user": "dashboard_user",
            "password": "your_secure_password",
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30
        }
    }

Metrics Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "metrics": {
            "collection_interval": 60,
            "retention_days": 30,
            "enabled_metrics": [
                "cpu",
                "memory",
                "disk",
                "network"
            ],
            "thresholds": {
                "cpu": 80,
                "memory": 85,
                "disk": 90
            }
        }
    }

WebSocket Configuration (websocket.json)
------------------------------------

.. code-block:: json

    {
        "websocket": {
            "host": "localhost",
            "port": 8765,
            "ssl": false,
            "cert_file": null,
            "key_file": null,
            "ping_interval": 30,
            "ping_timeout": 10,
            "max_connections": 1000,
            "auth_required": true
        }
    }

InfluxDB Configuration (influxdb.json)
----------------------------------

.. code-block:: json

    {
        "influxdb": {
            "url": "http://localhost:8086",
            "token": "your-influxdb-token",
            "org": "your-organization",
            "bucket": "dashboard-metrics",
            "batch_size": 5000,
            "flush_interval": 10000
        }
    }

Prometheus Configuration (prometheus.json)
-------------------------------------

.. code-block:: json

    {
        "prometheus": {
            "enabled": true,
            "port": 9090,
            "path": "/metrics",
            "labels": {
                "environment": "production",
                "service": "dashboard"
            }
        }
    }

Environment Variables
------------------

The following environment variables can override configuration file settings:

.. code-block:: bash

    # Server Configuration
    DASHBOARD_HOST=localhost
    DASHBOARD_PORT=8000
    DASHBOARD_DEBUG=false
    DASHBOARD_WORKERS=4

    # Database Configuration
    DASHBOARD_DB_HOST=localhost
    DASHBOARD_DB_PORT=5432
    DASHBOARD_DB_NAME=dashboard
    DASHBOARD_DB_USER=dashboard_user
    DASHBOARD_DB_PASSWORD=your_secure_password

    # Logging Configuration
    DASHBOARD_LOG_LEVEL=INFO
    DASHBOARD_LOG_FILE=logs/dashboard.log

    # Metrics Configuration
    DASHBOARD_METRICS_INTERVAL=60
    DASHBOARD_METRICS_RETENTION=30

    # WebSocket Configuration
    DASHBOARD_WS_HOST=localhost
    DASHBOARD_WS_PORT=8765

    # InfluxDB Configuration
    DASHBOARD_INFLUXDB_URL=http://localhost:8086
    DASHBOARD_INFLUXDB_TOKEN=your-token

    # Prometheus Configuration
    DASHBOARD_PROMETHEUS_ENABLED=true
    DASHBOARD_PROMETHEUS_PORT=9090

Security Considerations
--------------------

Sensitive Data
~~~~~~~~~~~~

* Never commit configuration files containing sensitive data
* Use environment variables for secrets in production
* Rotate API tokens and passwords regularly

SSL/TLS Configuration
~~~~~~~~~~~~~~~~~~

Enable SSL for production deployments:

.. code-block:: json

    {
        "server": {
            "ssl": true,
            "cert_file": "/path/to/cert.pem",
            "key_file": "/path/to/key.pem"
        }
    }

Authentication Settings
~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "auth": {
            "secret_key": "your-secret-key",
            "token_expiration": 3600,
            "max_failed_attempts": 5,
            "lockout_duration": 300,
            "password_policy": {
                "min_length": 12,
                "require_uppercase": true,
                "require_lowercase": true,
                "require_numbers": true,
                "require_special": true
            }
        }
    }

CORS Configuration
~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "cors": {
            "allowed_origins": [
                "https://example.com",
                "https://dashboard.example.com"
            ],
            "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
            "allowed_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["X-Total-Count"],
            "max_age": 3600,
            "allow_credentials": true
        }
    }

Rate Limiting
~~~~~~~~~~~

.. code-block:: json

    {
        "rate_limit": {
            "enabled": true,
            "requests_per_minute": 60,
            "burst_size": 100,
            "strategy": "sliding_window",
            "by_ip": true
        }
    }

Configuration Validation
---------------------

The dashboard validates configuration files on startup. Common validation errors include:

* Missing required fields
* Invalid data types
* Invalid port numbers
* Invalid file paths
* Unreachable services

To validate configuration without starting the server::

    python -m dashboard.config validate

Configuration Reloading
--------------------

Some configuration changes can be applied without restart:

* Logging settings
* Metrics thresholds
* Rate limits
* CORS settings

To reload configuration::

    curl -X POST http://localhost:8000/api/v1/config/reload

Or use the admin interface:

1. Navigate to Settings > Configuration
2. Make changes
3. Click "Apply Changes"

Best Practices
-----------

1. Use environment-specific configuration files
2. Keep sensitive data in environment variables
3. Regularly audit configuration files
4. Use version control for configuration templates
5. Document all custom configuration
6. Test configuration changes in staging
7. Back up configuration before changes
8. Use configuration management tools
