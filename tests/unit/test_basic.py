"""Basic tests to verify test setup."""


def test_basic():
    """Basic test to verify pytest is working."""
    assert True


def test_project_root(project_root):
    """Test project_root fixture."""
    assert project_root.endswith("project_management_dashboard")


def test_test_config(test_config):
    """Test test_config fixture."""
    assert test_config.endswith("test_config.json")


def test_test_data_dir(test_data_dir):
    """Test test_data_dir fixture."""
    assert test_data_dir is not None
