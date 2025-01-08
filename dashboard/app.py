"""Main application module."""

from dashboard import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False  # Debug mode is controlled by FLASK_DEBUG env var
    )
