"""Regression gate contract: per-task policy, not just a good average."""

import json

import pytest
from click.testing import CliRunner

from continualkit.cli import app


def run_gate(tmp_path, candidate, threshold="0.05", *, baseline=None):
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    if baseline is None:
        baseline = '{"critical": 0.9, "other": 0.4}'
    baseline_path.write_text(baseline, encoding="utf-8")
    payload = candidate if isinstance(candidate, str) else json.dumps(candidate)
    candidate_path.write_text(payload, encoding="utf-8")
    return CliRunner().invoke(
        app,
        [
            "gate",
            str(baseline_path),
            str(candidate_path),
            "--critical",
            "critical",
            "--max-loss",
            threshold,
        ],
    )


def test_critical_regression_is_not_hidden_by_improvement(tmp_path):
    result = run_gate(tmp_path, {"critical": 0.82, "other": 0.99})
    assert result.exit_code == 1
    assert "FAIL critical: loss 0.08" in result.output


def test_loss_equal_to_threshold_passes(tmp_path):
    result = run_gate(tmp_path, {"critical": 0.85, "other": 0.1})
    assert result.exit_code == 0
    assert "PASS critical: loss 0.05" in result.output


@pytest.mark.parametrize(
    "candidate",
    [
        {"other": 0.99},
        {"critical": float("nan"), "other": 0.99},
        {"critical": True, "other": 0.99},
    ],
)
def test_bad_scores_cannot_pass_the_gate(tmp_path, candidate):
    result = run_gate(tmp_path, candidate)
    assert result.exit_code == 2
    assert "Error:" in result.output
    assert "PASS" not in result.output


def test_loss_just_above_decimal_limit_does_not_round_into_a_pass(tmp_path):
    result = run_gate(
        tmp_path,
        '{"critical": 0.85}',
        baseline='{"critical": 0.900000000000000000000000000001}',
    )
    assert result.exit_code == 1
    assert (
        "FAIL critical: loss 0.900000000000000000000000000001 - 0.85" in result.output
    )


@pytest.mark.parametrize("threshold, expected", [("1", 0), ("0.999", 1)])
def test_sparse_decimal_exponent_does_not_require_expanding_the_gap(
    tmp_path, threshold, expected
):
    result = run_gate(
        tmp_path,
        '{"critical": 1e-1000000000}',
        threshold,
        baseline='{"critical": 1}',
    )
    assert result.exit_code == expected
    assert "loss 1 - 1E-1000000000" in result.output
