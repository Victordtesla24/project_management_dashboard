Getting Started
===============

This guide will help you get the Project Management Dashboard up and running.

System Requirements
-----------------

Software Dependencies
~~~~~~~~~~~~~~~~~~

* Python 3.9 or higher
* PostgreSQL 12+
* Redis 6+
* Node.js 16+ (for frontend development)

Operating Systems
~~~~~~~~~~~~~~

* Linux (Ubuntu 20.04+, CentOS 8+)
* macOS 11+
* Windows 10/11 with WSL2

Hardware Requirements
~~~~~~~~~~~~~~~~~

* CPU: 2+ cores
* RAM: 4GB minimum, 8GB recommended
* Storage: 20GB free space

Installation
-----------

Using pip
~~~~~~~~

1. Create a virtual environment::

    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows

2. Install the package::

    pip install project-management-dashboard

From Source
~~~~~~~~~

1. Clone the repository::

    git clone https://github.com/yourusername/project_management_dashboard.git
    cd project_management_dashboard

2. Create a virtual environment::

    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows

3. Install dependencies::

    pip install -r requirements.txt

4. Run the setup script::

    ./scripts/setup.sh

Docker Installation
~~~~~~~~~~~~~~~~

1. Pull the image::

    docker pull yourusername/project-management-dashboard:latest

2. Run the container::

    docker run -d -p 8000:8000 -p 8765:8765 yourusername/project-management-dashboard:latest

Initial Configuration
------------------

1. Copy the example configuration::

    cp config.json.example config.json

2. Edit the configuration file::

    {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "dashboard",
            "user": "dashboard_user",
            "password": "your_secure_password"
        },
        "websocket": {
            "host": "localhost",
            "port": 8765
        }
    }

3. Set up environment variables::

    export DASHBOARD_CONFIG_PATH=/path/to/config.json
    export DASHBOARD_LOG_LEVEL=INFO

Database Setup
------------

1. Create the database::

    createdb dashboard

2. Run migrations::

    python -m dashboard.db upgrade

3. Create initial user::

    python -m dashboard.users create-admin

Running the Dashboard
------------------

Development Server
~~~~~~~~~~~~~~~

Start the development server::

    python run.py

Production Deployment
~~~~~~~~~~~~~~~~~

1. Configure a production web server (e.g., Nginx)::

    server {
        listen 80;
        server_name dashboard.example.com;

        location / {
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /ws {
            proxy_pass http://localhost:8765;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }

2. Start the application server::

    gunicorn -w 4 -b 127.0.0.1:8000 dashboard.wsgi:app

3. Start the WebSocket server::

    python -m dashboard.websocket

4. Start the metrics collector::

    python -m dashboard.metrics collect

Verification
----------

1. Access the dashboard::

    http://localhost:8000

2. Log in with default credentials::

    Username: admin
    Password: admin

3. Change the default password immediately.

Next Steps
---------

* Review the :doc:`configuration` guide for detailed settings
* Set up :doc:`metrics` collection
* Configure :doc:`alerts`
* Explore the :doc:`api` documentation

Troubleshooting
-------------

Common Issues
~~~~~~~~~~~

* **Database Connection**: Verify PostgreSQL is running and credentials are correct
* **WebSocket Error**: Check if port 8765 is available
* **Permission Issues**: Ensure proper file permissions in the config directory

Getting Help
~~~~~~~~~~

* Check the :doc:`troubleshooting` guide
* Search the `Issue Tracker <https://github.com/yourusername/project_management_dashboard/issues>`_
* Join our `Community Forum <https://forum.example.com>`_
