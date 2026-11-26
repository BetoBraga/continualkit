"""ContinualKit CLI — continual train, eval, compare."""

import json
from decimal import MAX_EMAX, MIN_EMIN, Context, Decimal, Inexact, InvalidOperation
from pathlib import Path

import click


@click.group()
@click.version_option()
def app() -> None:
    """ContinualKit — update your LLM without breaking what already works."""


@app.command()
@click.argument("config", required=False)
def train(config: str | None) -> None:
    """Run incremental training with replay + regularization.

    CONFIG: path to training config file (YAML or JSON).
    """
    click.echo("continualkit train — not implemented yet.")
    click.echo("Track progress: https://github.com/BetoBraga/continualkit")


@app.command()
@click.argument("config", required=False)
def eval(config: str | None) -> None:  # noqa: A001
    """Evaluate forgetting and task performance across checkpoints.

    CONFIG: path to eval config file (YAML or JSON).
    """
    click.echo("continualkit eval — not implemented yet.")
    click.echo("Track progress: https://github.com/BetoBraga/continualkit")


@app.command()
@click.argument("candidate", required=False)
@click.argument("baseline", required=False)
def compare(candidate: str | None, baseline: str | None) -> None:
    """Compare candidate checkpoint against current baseline.

    CANDIDATE: path or identifier of the candidate checkpoint.
    BASELINE:  path or identifier of the current baseline.
    """
    click.echo("continualkit compare — not implemented yet.")
    click.echo("Track progress: https://github.com/BetoBraga/continualkit")


def _scores(path: Path) -> dict[str, Decimal]:
    def unique_keys(pairs):
        scores = {}
        for key, value in pairs:
            if key in scores:
                raise ValueError(f"duplicate task: {key}")
            scores[key] = value
        return scores

    try:
        scores = json.loads(
            path.read_text(encoding="utf-8"),
            parse_float=Decimal,
            parse_int=Decimal,
            object_pairs_hook=unique_keys,
        )
    except (OSError, ValueError, InvalidOperation) as exc:
        raise click.BadParameter(f"{path.name}: {exc}") from exc
    if not isinstance(scores, dict) or not scores:
        raise click.BadParameter(f"{path.name}: expected a non-empty task-score object")
    for task, score in scores.items():
        if (
            not task.strip()
            or not isinstance(score, Decimal)
            or not score.is_finite()
            or not 0 <= score <= 1
        ):
            raise click.BadParameter(
                f"{path.name}: task names must be nonempty and scores must be numbers in [0, 1]"
            )
    return scores


def _loss_exceeds(before: Decimal, after: Decimal, threshold: Decimal) -> bool:
    """Compare before - after - threshold exactly, without expanding exponent gaps."""
    columns: dict[int, int] = {}
    for value, direction in ((before, 1), (after, -1), (threshold, -1)):
        _, digits, exponent = value.as_tuple()
        for offset, digit in enumerate(reversed(digits)):
            if digit:
                power = exponent + offset
                columns[power] = columns.get(power, 0) + direction * digit

    carry = 0
    previous = None
    for power in sorted(columns, reverse=True):
        if previous is not None and carry:
            # Across an empty column this sign cannot be reversed by the suffix.
            if previous - power > 1:
                return carry > 0
            carry *= 10
        carry += columns[power]
        # The unprocessed suffix is less than two units of this column in magnitude.
        if abs(carry) >= 2:
            return carry > 0
        previous = power
    return carry > 0


def _format_loss(before: Decimal, after: Decimal) -> str:
    if before <= after:
        return "0"
    display = Context(prec=28, Emin=MIN_EMIN, Emax=MAX_EMAX)
    loss = display.subtract(before, after)
    if display.flags[Inexact]:
        # Keep both operands exact rather than printing a rounded pass/fail boundary.
        return f"{before} - {after}"
    return str(loss)


@app.command()
@click.argument(
    "baseline", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.argument(
    "candidate", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--critical", required=True, multiple=True, help="Critical task (repeatable)."
)
@click.option(
    "--max-loss", required=True, help="Maximum absolute score loss in [0, 1]."
)
@click.pass_context
def gate(
    ctx, baseline: Path, candidate: Path, critical: tuple[str, ...], max_loss: str
) -> None:
    """Block a candidate if any selected task loses more than MAX_LOSS."""
    try:
        threshold = Decimal(max_loss)
        if not threshold.is_finite() or not 0 <= threshold <= 1:
            raise InvalidOperation
    except InvalidOperation as exc:
        raise click.BadParameter(
            "must be a finite number in [0, 1]", param_hint="--max-loss"
        ) from exc

    before = _scores(baseline)
    after = _scores(candidate)
    if before.keys() != after.keys():
        raise click.UsageError("baseline and candidate must contain the same tasks")
    if unknown := set(critical) - before.keys():
        raise click.BadParameter(
            f"unknown tasks: {', '.join(sorted(unknown))}", param_hint="--critical"
        )

    failed = False
    for task in dict.fromkeys(critical):
        blocked = _loss_exceeds(before[task], after[task], threshold)
        loss = _format_loss(before[task], after[task])
        failed |= blocked
        status = "FAIL" if blocked else "PASS"
        click.echo(f"{status} {task}: loss {loss} (max {threshold})")
    if failed:
        ctx.exit(1)
