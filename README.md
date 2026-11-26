# ContinualKit

**What did your model retain after the update?**

ContinualKit is an early-stage Python toolkit for evaluating regression after an LLM update. Today it can calculate mean forgetting and check critical tasks against a loss threshold, using task scores that you already have. It does not run model inference or fine-tuning.

## Run a score comparison

Python 3.10 or newer. This example needs no GPU, model weights, dataset download, or API key. The installation step needs access to the Python package index unless the build and runtime dependencies are already cached.

```sh
git clone https://github.com/BetoBraga/continualkit.git
cd continualkit
python -m venv .venv
# Activate: .venv\Scripts\Activate.ps1 (PowerShell) or source .venv/bin/activate (bash)
python -m pip install -e .
continual --version
python examples/score_regression.py
```

If you only want the example and already have the checkout, set `$env:PYTHONPATH = "src"` in PowerShell or run `PYTHONPATH=src python examples/score_regression.py` in bash. Then run the example as shown above in PowerShell. The metric and example use only the standard Python runtime in this mode.

Output from the included [example](examples/score_regression.py):

```text
support_qa: 0.90 -> 0.80 | loss: 0.10
tool_selection: 0.70 -> 0.75 | loss: 0.00
mean forgetting: 0.05 (5.0 percentage points)
```

### How to read it

The baseline is the first set of scores; the candidate is the second. They must cover the same, nonempty set of tasks. For each task the metric takes `max(0, baseline - candidate)`; it treats gains as zero loss so a gain on one task cannot erase a regression on another. Then it averages equally across tasks. Here the 10-point drop and zero loss average to **5 percentage points**. That interpretation assumes normalized higher-is-better scores. The library does not check score ranges or collect the scores for you.

These scores are **fictional inputs**, not model outputs or a benchmark. A real comparison needs a fixed evaluation set, scoring procedure and baseline, and the same conditions for both checkpoints. Inspect per-task results too: a mean can hide a large drop on one task.

## Gate an update on a critical task

Use the same task names and numeric, higher-is-better scores in [0, 1] in both JSON files. This example sets a five-percentage-point maximum loss:

```sh
continual gate examples/baseline.json examples/candidate.json --critical support_qa --max-loss 0.05
```

The example exits with status 1: the 10-point loss on `support_qa` exceeds the threshold even though `tool_selection` improved. Repeat `--critical` to check multiple tasks. All selected tasks must pass; a loss equal to the threshold passes. The command exits with status 0 on pass and 2 for invalid input. It checks precomputed scores, not model behavior directly.

## What is implemented

| Available now | Not implemented |
| --- | --- |
| `continualkit.eval.compute_forgetting` and its tests | Training, model inference, managed release automation and rollback |
| CLI installation/help and version | The `train`, `eval` and `compare` subcommands are placeholders |
| Small example with fixed scores and a critical-task CLI gate | A validated reference benchmark or production pipeline |

## Contribute

Install the development extras with `python -m pip install -e ".[dev]"`. Run `python -m pytest`, `ruff check .`, and `ruff format --check .`. CI runs lint and tests on Python 3.10–3.12. The example is a walkthrough; automated tests cover averaging, gains, mismatched tasks, empty input and the example’s output.

See [CONTRIBUTING.md](CONTRIBUTING.md), [issues](https://github.com/BetoBraga/continualkit/issues) and the [Apache 2.0 license](LICENSE).
