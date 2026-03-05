"""ContinualKit CLI — continual train, eval, compare."""

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
