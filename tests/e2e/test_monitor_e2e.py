"""End-to-end tests for system monitoring."""

import pytest
from pathlib import Path
import time

def wait_for_element(page, selector, timeout=30000):
    """Wait for element to be visible."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except:
        return False

@pytest.mark.usefixtures("server")
def test_monitor_startup(page):
    """Test monitor initialization."""
    # Navigate and wait for app container
    page.goto("http://localhost:8000")
    assert wait_for_element(page, "[data-testid='stApp']")
    
    # Click monitor link
    page.click("text=Monitor")
    
    # Wait for title
    assert wait_for_element(page, "h1:has-text('System Monitor')")
    
    # Wait for metrics
    assert wait_for_element(page, "div:has-text('CPU Usage')")
    assert wait_for_element(page, "div:has-text('Memory Usage')")

@pytest.mark.usefixtures("server")
def test_monitor_data_refresh(page):
    """Test monitor data refresh."""
    # Navigate and wait for app container
    page.goto("http://localhost:8000")
    assert wait_for_element(page, "[data-testid='stApp']")
    
    # Click monitor link
    page.click("text=Monitor")
    
    # Wait for initial metrics
    assert wait_for_element(page, "div:has-text('CPU Usage')")
    assert wait_for_element(page, "div:has-text('Memory Usage')")
    
    # Get initial values
    initial_text = page.content()
    
    # Wait for refresh
    time.sleep(6)
    
    # Get updated values
    updated_text = page.content()
    
    # Content should be different after refresh
    assert initial_text != updated_text

@pytest.mark.usefixtures("server")
def test_monitor_error_handling(page):
    """Test monitor error handling."""
    # Navigate with error parameter
    page.goto("http://localhost:8000?error=true")
    assert wait_for_element(page, "[data-testid='stApp']")
    
    # Click monitor link
    page.click("text=Monitor")
    
    # Wait for error message
    assert wait_for_element(page, "div:has-text('Error fetching system metrics')")
