import pytest

def test_sample():
    assert True

@pytest.mark.unit
def test_addition():
    assert 1 + 1 == 2

@pytest.mark.integration
def test_with_fixture(test_config):
    assert test_config['database']['host'] == 'localhost'

@pytest.mark.e2e
@pytest.mark.slow
def test_with_temp_dir(temp_dir):
    assert temp_dir.exists()
    test_file = temp_dir / 'test.txt'
    test_file.write_text('Hello, World!')
    assert test_file.read_text() == 'Hello, World!'
