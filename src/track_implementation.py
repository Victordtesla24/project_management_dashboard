import json
import logging
import time
from datetime import datetime
from pathlib import Path

import git

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("implementation_tracker")


def count_lines(file_path):
    try:
        with open(file_path) as f:
            return len(f.readlines())
    except:
        return 0


def get_git_stats():
    try:
        repo = git.Repo(".")
        commits = list(repo.iter_commits())
        return {
            "total_commits": len(commits),
            "last_commit": (commits[0].committed_datetime.isoformat() if commits else None),
            "active_branch": repo.active_branch.name,
        }
    except:
        return {"total_commits": 0, "last_commit": None, "active_branch": "unknown"}


def track_implementation():
    project_root = Path(".")

    # Count files by type
    python_files = list(project_root.rglob("*.py"))
    shell_files = list(project_root.rglob("*.sh"))
    test_files = list(project_root.glob("tests/**/*.py"))
    doc_files = list(project_root.glob("docs/**/*"))

    # Calculate metrics
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "files": {
            "python": len(python_files),
            "shell": len(shell_files),
            "tests": len(test_files),
            "docs": len(doc_files),
        },
        "lines": {
            "python": sum(count_lines(f) for f in python_files),
            "shell": sum(count_lines(f) for f in shell_files),
            "tests": sum(count_lines(f) for f in test_files),
        },
        "git": get_git_stats(),
        "components": {
            "core": {
                "total": 8,
                "completed": sum(1 for f in python_files if "core" in str(f)),
            },
            "dashboard": {
                "total": 6,
                "completed": sum(1 for f in python_files if "dashboard" in str(f)),
            },
            "tests": {"total": 5, "completed": len(test_files)},
        },
    }

    # Calculate completion percentages
    for component in metrics["components"]:
        total = metrics["components"][component]["total"]
        completed = metrics["components"][component]["completed"]
        metrics["components"][component]["percentage"] = (
            (completed / total * 100) if total > 0 else 0
        )

    return metrics


def main():
    tracking_dir = Path("tracking")
    tracking_dir.mkdir(exist_ok=True)
    metrics_file = tracking_dir / "implementation_metrics.json"

    logger.info("Starting implementation tracking")
    while True:
        try:
            metrics = track_implementation()
            metrics_file.write_text(json.dumps(metrics, indent=2))
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error tracking implementation: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
