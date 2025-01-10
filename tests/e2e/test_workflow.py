"""End-to-end tests for workflow functionality."""

import pytest
from pathlib import Path
import time

def wait_for_element(page, selector, timeout=30000):
    """Wait for element to be visible."""
    try:
        page.wait_for_selector(selector, timeout=timeout, state="attached")
        return True
    except:
        return False

def test_workflow_initialization(project_root):
    """Test workflow initialization."""
    project_path = Path(project_root)
    config_path = project_path / "config" / "dashboard.json"
    assert config_path.exists()

@pytest.mark.usefixtures("server")
def test_workflow_execution(page):
    """Test workflow execution."""
    # Navigate and wait for app
    page.goto("http://localhost:8000")
    page.wait_for_selector("[data-testid='stApp']")
    
    # Click workflow link and wait for navigation
    page.click("text=Workflow")
    page.wait_for_load_state("networkidle")
    
    # Find and click button
    button = page.get_by_role("button", name="Run")
    button.click()
    
    # Wait for success message
    assert wait_for_element(page, "[data-testid='stSuccessMessage']")
    assert page.is_visible("text=Workflow Complete")

@pytest.mark.usefixtures("server")
def test_workflow_error_handling(page):
    """Test workflow error handling."""
    # Navigate and wait for app
    page.goto("http://localhost:8000?trigger_error=true")
    page.wait_for_selector("[data-testid='stApp']")
    
    # Click workflow link and wait for navigation
    page.click("text=Workflow")
    page.wait_for_load_state("networkidle")
    
    # Find and click button
    button = page.get_by_role("button", name="Run")
    button.click()
    
    # Wait for error message
    assert wait_for_element(page, "[data-testid='stErrorMessage']")
    assert page.is_visible("text=Error in workflow")
