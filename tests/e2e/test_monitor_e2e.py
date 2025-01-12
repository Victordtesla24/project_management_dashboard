"""End-to-end tests for system monitoring."""

import time
import pytest
from playwright.sync_api import expect, Page


def wait_for_element(page: Page, selector: str, timeout: int = 30000) -> bool:
    """Wait for element to be visible."""
    try:
        page.wait_for_selector(selector, timeout=timeout, state="attached")
        return True
    except Exception as e:
        print(f"Error waiting for element {selector}: {e}")
        return False


@pytest.mark.usefixtures("server")
@pytest.mark.flaky(reruns=2)
def test_monitor_startup(page: Page) -> None:
    """Test monitor initialization."""
    try:
        # Navigate and wait for app container
        page.goto("http://localhost:8000", wait_until="networkidle")
        assert wait_for_element(page, "[data-testid='stApp']")

        # Click monitor link and wait for navigation
        expect(page.locator("text=Monitor")).to_be_visible()
        page.click("text=Monitor")
        page.wait_for_load_state("networkidle")

        # Wait for title
        assert wait_for_element(page, "h1:has-text('System Monitor')")

        # Wait for metrics with data-testid
        assert wait_for_element(page, "[data-testid='cpu-metric']")
        assert wait_for_element(page, "[data-testid='memory-metric']")
    except Exception as e:
        pytest.fail(f"Test failed: {e}")


@pytest.mark.usefixtures("server")
@pytest.mark.flaky(reruns=2)
def test_monitor_data_refresh(page: Page) -> None:
    """Test monitor data refresh."""
    try:
        # Navigate and wait for app container
        page.goto("http://localhost:8000", wait_until="networkidle")
        assert wait_for_element(page, "[data-testid='stApp']")

        # Click monitor link and wait for navigation
        expect(page.locator("text=Monitor")).to_be_visible()
        page.click("text=Monitor")
        page.wait_for_load_state("networkidle")

        # Wait for initial metrics
        assert wait_for_element(page, "[data-testid='cpu-metric']")
        assert wait_for_element(page, "[data-testid='memory-metric']")

        # Get initial values
        initial_text = page.content()

        # Wait for refresh
        time.sleep(6)

        # Get updated values
        updated_text = page.content()

        # Content should be different after refresh
        assert initial_text != updated_text
    except Exception as e:
        pytest.fail(f"Test failed: {e}")


@pytest.mark.usefixtures("server")
@pytest.mark.flaky(reruns=2)
def test_monitor_error_handling(page: Page) -> None:
    """Test monitor error handling."""
    try:
        # Navigate with error parameter
        page.goto("http://localhost:8000?error=true", wait_until="networkidle")
        assert wait_for_element(page, "[data-testid='stApp']")

        # Click monitor link and wait for navigation
        expect(page.locator("text=Monitor")).to_be_visible()
        page.click("text=Monitor")
        page.wait_for_load_state("networkidle")

        # Wait for error message
        assert wait_for_element(page, "[data-testid='error-message']")
        assert page.is_visible("text=Error fetching system metrics")
    except Exception as e:
        pytest.fail(f"Test failed: {e}")
