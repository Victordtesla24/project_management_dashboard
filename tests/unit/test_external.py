"""Test cases that run tests as subprocesses."""
import os
import sys
import tempfile
from subprocess import CalledProcessError, run
from typing import Generator

import pytest


@pytest.fixture()
def temp_script() -> Generator[str, None, None]:
    """Create a temporary Python script."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        yield f.name
    # Clean up after test
    try:
        os.unlink(f.name)
    except OSError:
        pass  # Ignore cleanup errors


def test_subprocess_execution(temp_script: str) -> None:
    """Test basic subprocess execution."""
    # Write test script
    with open(temp_script, "w") as f:
        f.write('print("Hello from subprocess")')

    try:
        # Run the script in a subprocess
        result = run([sys.executable, temp_script], capture_output=True, text=True, check=True)
        assert result.stdout.strip() == "Hello from subprocess"
        assert result.returncode == 0
    except CalledProcessError as e:
        pytest.fail(f"Subprocess failed with return code {e.returncode}: {e.stderr}")


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Environment variable handling differs on Windows",
)
def test_environment_vars(temp_script: str) -> None:
    """Test subprocess with environment variables."""
    # Write test script
    with open(temp_script, "w") as f:
        f.write('import os; print(os.environ.get("TEST_VAR", ""))')

    try:
        # Run with custom environment
        env = os.environ.copy()
        env["TEST_VAR"] = "test_value"
        result = run(
            [sys.executable, temp_script], env=env, capture_output=True, text=True, check=True,
        )
        assert result.stdout.strip() == "test_value"
        assert result.returncode == 0
    except CalledProcessError as e:
        pytest.fail(f"Subprocess failed with return code {e.returncode}: {e.stderr}")


def test_subprocess_error_handling(temp_script: str) -> None:
    """Test subprocess error handling."""
    # Write invalid Python script
    with open(temp_script, "w") as f:
        f.write("print(undefined_variable)")  # This will raise a NameError

    # Run script and expect failure
    with pytest.raises(CalledProcessError) as exc_info:
        run([sys.executable, temp_script], capture_output=True, text=True, check=True)
    assert exc_info.value.returncode != 0
    assert "NameError" in exc_info.value.stderr


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows-specific test")
def test_windows_specific_env(temp_script: str) -> None:
    """Test Windows-specific environment handling."""
    # Write test script
    with open(temp_script, "w") as f:
        f.write('import os; print(os.environ.get("SYSTEMROOT", ""))')

    try:
        # Run with Windows environment
        env = os.environ.copy()
        result = run(
            [sys.executable, temp_script], env=env, capture_output=True, text=True, check=True,
        )
        assert result.stdout.strip()  # Should have SYSTEMROOT value
        assert result.returncode == 0
    except CalledProcessError as e:
        pytest.fail(f"Subprocess failed with return code {e.returncode}: {e.stderr}")
