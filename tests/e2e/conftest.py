from pathlib import Path
from typing import Any, Generator
from playwright.sync_api import Browser, BrowserContext, Page, Playwright
import pytest


@pytest.fixture(scope="session")
def browser_context_args() -> dict[str, Any]:
    """Override browser context args."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True
        }


@pytest.fixture
def browser(playwright: Playwright) -> Generator[Browser, None, None]:
    """Create browser for each test."""
    browser = None
    try:
        browser = playwright.chromium.launch(
            args=['--no-sandbox'],
            headless=True
            )
        yield browser
    finally:
        if browser:
            try:
                browser.close()
            except Exception:
                pass


@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create context for each test."""
    context = None
    try:
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
            )
        context.set_default_timeout(30000)  # Set timeout after creation
        yield context
    finally:
        if context:
            try:
                context.close()
            except Exception:
                pass


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create page for each test."""
    page = None
    try:
        page = context.new_page()
        assert page is not None, "Failed to create page"
        page.set_default_timeout(30000)  # 30 seconds timeout
        yield page
    finally:
        if page:
            try:
                page.close()
            except Exception:
                pass


@pytest.fixture()
def test_data() -> dict[str, Any]:
    """Test data fixture."""
    return {
        "metrics": {
            "cpu": {"percent": 50.0, "count": 8, "frequency": 2.4},
            "memory": {"percent": 60.0, "total": 16000, "used": 9600},
            "disk": {"percent": 70.0, "total": 500000, "used": 350000}
            },
        "timestamp": "2024-03-21T12:00:00",
        "uptime": 3600
        }


@pytest.fixture()
def metrics_dir(project_root: str) -> Path:
    """Metrics directory fixture."""
    metrics_dir = Path(project_root) / "metrics" / "data"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return metrics_dir


@pytest.fixture()
def logs_dir(project_root: str) -> Path:
    """Logs directory fixture."""
    logs_dir = Path(project_root) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


@pytest.fixture(autouse=True)
def setup_monitor_env(metrics_dir: Path, logs_dir: Path) -> None:
    """Setup monitor environment fixture."""
    config_dir = metrics_dir.parent
    config_file = config_dir / "monitor_config.json"
    config_file.write_text(
        """{
            "collection_interval": 1,
            "metrics": {
                "cpu": true,
                "memory": true,
                "disk": true,
                "network": true,
                "load": true
            },
            "processes": [
                {
                    "name": "python",
                    "pattern": "python",
                    "metrics": ["cpu", "memory", "threads"]
                }
            ]
        }"""
        )
