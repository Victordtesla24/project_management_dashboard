def test_metrics_data(test_data):
    metrics = test_data["metrics"]
    assert 0 <= metrics["cpu_usage"] <= 100
    assert 0 <= metrics["memory_usage"] <= 100
    assert 0 <= metrics["disk_usage"] <= 100


def test_coverage_data(test_data):
    coverage = test_data["coverage"]
    assert 0 <= coverage["lines"] <= 100
    assert 0 <= coverage["branches"] <= 100
    assert 0 <= coverage["functions"] <= 100


def test_test_results(test_data):
    tests = test_data["tests"]
    assert tests["total"] == tests["passed"] + tests["failed"]
    assert tests["passed"] > 0
    assert tests["failed"] >= 0


def test_temp_directory(temp_test_dir):
    assert temp_test_dir.exists()
    assert temp_test_dir.is_dir()

    test_file = temp_test_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
    assert test_file.read_text() == "test content"
