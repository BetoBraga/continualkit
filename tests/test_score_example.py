"""Keep the documented no-model walkthrough executable."""

import os
import subprocess
import sys
from pathlib import Path


def test_score_regression_demo():
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(root / "src"))
    run = subprocess.run(
        [sys.executable, "examples/score_regression.py"],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert run.stdout.splitlines() == [
        "support_qa: 0.90 -> 0.80 | loss: 0.10",
        "tool_selection: 0.70 -> 0.75 | loss: 0.00",
        "mean forgetting: 0.05 (5.0 percentage points)",
    ]
