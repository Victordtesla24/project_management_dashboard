import json
import time


def test_complete_workflow(project_root, test_data, temp_test_dir):
    # Step 1: Setup
    assert project_root.exists()
    config_dir = project_root / "config"
    assert config_dir.exists()

    # Step 2: Create test data
    metrics_file = temp_test_dir / "metrics.json"
    metrics_file.write_text(json.dumps(test_data["metrics"]))
    assert metrics_file.exists()

    # Step 3: Process data
    processed_data = {
        "timestamp": time.time(),
        "metrics": json.loads(metrics_file.read_text()),
        "status": "processed",
    }

    processed_file = temp_test_dir / "processed.json"
    processed_file.write_text(json.dumps(processed_data))
    assert processed_file.exists()

    # Step 4: Verify results
    loaded_data = json.loads(processed_file.read_text())
    assert loaded_data["metrics"] == test_data["metrics"]
    assert loaded_data["status"] == "processed"
    assert isinstance(loaded_data["timestamp"], (int, float))
