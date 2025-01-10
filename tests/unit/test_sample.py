import pytest


def test_sample():
    assert True


@pytest.mark.unit()
def test_addition():
    assert 1 + 1 == 2


@pytest.mark.integration()
def test_with_fixture(test_config):
    import json

    with open(test_config) as f:
        config = json.load(f)
    assert config["database"]["host"] == "localhost"


@pytest.mark.e2e()
@pytest.mark.slow()
def test_with_temp_dir(test_data_dir):
    from pathlib import Path

    temp_dir = Path(test_data_dir)
    assert temp_dir.exists()
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello, World!")
    assert test_file.read_text() == "Hello, World!"
