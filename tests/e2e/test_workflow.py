"""End-to-end tests for workflow functionality."""

import pytest
from pathlib import Path

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
    
    # Click workflow link
    page.click("text=Workflow")
    
    # Find and click button
    button = page.get_by_role("button", name="Run")
    button.click()
    
    # Wait for success message
    page.wait_for_selector("[data-testid='stSuccessMessage']")

@pytest.mark.usefixtures("server")
def test_workflow_error_handling(page):
    """Test workflow error handling."""
    # Navigate and wait for app
    page.goto("http://localhost:8000?trigger_error=true")
    page.wait_for_selector("[data-testid='stApp']")
    
    # Click workflow link
    page.click("text=Workflow")
    
    # Find and click button
    button = page.get_by_role("button", name="Run")
    button.click()
    
    # Wait for error message
    page.wait_for_selector("[data-testid='stErrorMessage']")
