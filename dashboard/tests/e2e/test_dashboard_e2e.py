import asyncio
import json
import multiprocessing
import os
import time
from collections.abc import AsyncGenerator

import pytest
from playwright.async_api import Browser, BrowserContext, Page

from dashboard.app import create_app
from dashboard.websocket.server import MetricsWebSocket


def run_flask_app():
    """Run Flask application for testing."""
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "LAYOUTS": {
                "default": {"name": "Default Layout"},
                "minimal": {"name": "Minimal Layout"},
            },
        }
    )
    app.template_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"
    )
    app.static_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static"
    )
    app.run(port=5000, use_reloader=False)


def run_websocket_server(config_path):
    """Run WebSocket server for testing."""
    ws_server = MetricsWebSocket(config_path)
    asyncio.run(ws_server.start_server())


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser_context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Create browser context for tests."""
    context = await browser.new_context(viewport={"width": 1280, "height": 720})
    yield context
    await context.close()


@pytest.fixture
async def page(browser_context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Create new page for each test."""
    page = await browser_context.new_page()
    yield page
    await page.close()


@pytest.fixture(scope="session")
def app_url():
    """Get application URL."""
    return "http://localhost:5000"


@pytest.fixture(scope="session")
def test_config(tmp_path_factory):
    """Create test configuration."""
    config_dir = tmp_path_factory.mktemp("config")
    config_path = config_dir / "config.json"

    config = {
        "environment": "test",
        "metrics": {
            "collection_interval": 5,
            "enabled_metrics": ["cpu", "memory", "disk"],
            "thresholds": {"cpu": 80, "memory": 90, "disk": 85},
        },
        "websocket": {"host": "localhost", "port": 8765, "ssl": False},
        "influxdb": {
            "url": "http://localhost:8086",
            "token": "test-token",
            "org": "test-org",
            "bucket": "test-bucket",
        },
    }

    config_path.write_text(json.dumps(config))
    return str(config_path)


@pytest.fixture(scope="session")
def flask_server():
    """Start Flask server for tests."""
    server = multiprocessing.Process(target=run_flask_app)
    server.start()
    time.sleep(2)  # Give server time to start

    yield server

    server.terminate()
    server.join()


@pytest.fixture(scope="session")
def websocket_server(test_config):
    """Start WebSocket server for tests."""
    server = multiprocessing.Process(target=run_websocket_server, args=(test_config,))
    server.start()
    time.sleep(2)  # Give server time to start

    yield server

    server.terminate()
    server.join()


class TestDashboardE2E:
    async def login(self, page: Page, app_url: str):
        """Helper method to perform login."""
        await page.goto(f"{app_url}/login")
        await page.fill("input[name='username']", "test_user")
        await page.fill("input[name='password']", "test_password")
        async with page.expect_navigation():
            await page.click("button[type='submit']")

    @pytest.mark.asyncio
    async def test_login_flow(self, page: Page, app_url: str, flask_server):
        """Test user login flow."""
        # Navigate to login page
        await page.goto(f"{app_url}/login")

        # Fill login form
        await page.fill("input[name='username']", "test_user")
        await page.fill("input[name='password']", "test_password")

        # Submit form and wait for navigation
        async with page.expect_navigation():
            await page.click("button[type='submit']")

        # Verify redirect to dashboard
        assert page.url == f"{app_url}/"

        # Verify dashboard elements
        assert await page.is_visible("#metrics-panel")
        assert await page.is_visible("#alerts-panel")

    @pytest.mark.asyncio
    async def test_metric_updates(self, page: Page, app_url: str, flask_server, websocket_server):
        """Test real-time metric updates."""
        await self.login(page, app_url)

        # Wait for initial metrics
        await page.wait_for_selector("#cpu-metric")

        # Get initial values
        initial_cpu = await page.text_content("#cpu-value")

        # Wait for update
        await asyncio.sleep(5)

        # Get updated values
        updated_cpu = await page.text_content("#cpu-value")

        # Values should be different
        assert initial_cpu != updated_cpu

    @pytest.mark.asyncio
    async def test_configuration_changes(self, page: Page, app_url: str, flask_server):
        """Test configuration update flow."""
        await self.login(page, app_url)

        # Navigate to settings
        await page.click("#settings-button")

        # Update threshold
        await page.fill("#cpu-threshold", "85")

        # Save changes
        async with page.expect_response("**/api/config"):
            await page.click("#save-settings")

        # Verify success message
        assert await page.is_visible(".success-message")

    @pytest.mark.asyncio
    async def test_websocket_reconnection(
        self, page: Page, app_url: str, flask_server, websocket_server
    ):
        """Test WebSocket reconnection behavior."""
        await self.login(page, app_url)

        # Wait for WebSocket connection
        await page.wait_for_selector("#connection-status.connected")

        # Simulate connection loss
        await page.evaluate("window.dashboardWS.close()")

        # Wait for reconnection
        await page.wait_for_selector("#connection-status.connected")

    @pytest.mark.asyncio
    async def test_error_handling(self, page: Page, app_url: str, flask_server):
        """Test error handling in UI."""
        await self.login(page, app_url)

        # Trigger invalid request
        async with page.expect_response("**/api/metrics"):
            await page.evaluate("fetch('/api/metrics?invalid=true')")

        # Verify error message
        assert await page.is_visible(".error-message")

    @pytest.mark.asyncio
    async def test_performance_metrics(self, page: Page, app_url: str, flask_server):
        """Test performance metrics collection."""
        await self.login(page, app_url)

        # Get performance metrics
        metrics = await page.evaluate(
            """() => {
            const entries = performance.getEntriesByType('navigation');
            return entries[0].toJSON();
        }"""
        )

        # Verify metrics
        assert metrics["domContentLoadedEventEnd"] - metrics["domContentLoadedEventStart"] < 1000
        assert metrics["loadEventEnd"] - metrics["loadEventStart"] < 2000
