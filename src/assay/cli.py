"""Typer CLI entrypoint for Assay."""

from pathlib import Path

import typer

app = typer.Typer(
    name="assay",
    help="Precision testing tool for AI agents",
    no_args_is_help=True,
)


@app.command()
def run(
    config: str = typer.Option(
        "suite.yaml",
        "--config",
        "-c",
        help="Path to test suite YAML configuration file.",
    ),
    sync: bool = typer.Option(
        False,
        "--sync",
        help="Sync results to Assay Cloud.",
    ),
    api_key: str = typer.Option(
        "",
        "--api-key",
        help="API key for Assay Cloud.",
    ),
) -> None:
    """Run test suite against AI agent endpoints."""
    config_path = Path(config)
    if not config_path.exists():
        typer.echo(f"Error: Config file not found: {config}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Loading suite from: {config}")
    typer.echo("Phase 1 MVP: Configuration parser and transport layer coming soon...")
    raise typer.Exit(code=0)


@app.command()
def version() -> None:
    """Display Assay version."""
    typer.echo("assay 0.1.0")


if __name__ == "__main__":
    app()
