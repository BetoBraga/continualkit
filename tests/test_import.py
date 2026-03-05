"""Smoke tests — package imports and CLI entry point."""

import continualkit
from continualkit.cli import app


def test_package_version() -> None:
    assert hasattr(continualkit, "__version__")
    assert isinstance(continualkit.__version__, str)
    assert continualkit.__version__ == "0.1.0"


def test_submodules_importable() -> None:
    from continualkit import compare, eval, replay, train  # noqa: F401


def test_cli_app_exists() -> None:
    assert callable(app)
