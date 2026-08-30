"""Typer CLI entrypoint for Assay."""

import asyncio
from pathlib import Path

import typer

from assay.config.parser import parse_suite
from assay.executor.executor import TestExecutor
from assay.reporters import JSONReporter, JUnitReporter, ReporterConfig, TerminalReporter

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
    reporter: str = typer.Option(
        "terminal",
        "--reporter",
        "-r",
        help="Output format: terminal, junit, json, or comma-separated list.",
    ),
    output: str = typer.Option(
        "",
        "--output",
        "-o",
        help="Output file path (for junit/json; ignored for terminal).",
    ),
    baseline_file: str = typer.Option(
        "baseline.json",
        "--baseline-file",
        "-b",
        help="Path to baseline.json for regression detection.",
    ),
) -> None:
    """Run test suite against AI agent endpoints."""
    config_path = Path(config)
    if not config_path.exists():
        typer.echo(f"Error: Config file not found: {config}", err=True)
        raise typer.Exit(code=1)

    # Parse suite config
    try:
        suite_config = parse_suite(config_path)
    except Exception as e:\n        typer.echo(f"Error parsing config: {e}", err=True)
        raise typer.Exit(code=1)

    # Execute test suite
    executor = TestExecutor(
        config=suite_config,
        baseline_file=baseline_file,
    )

    try:
        suite_report = asyncio.run(executor.run())
    except Exception as e:\n        typer.echo(f"Error executing suite: {e}", err=True)
        raise typer.Exit(code=1)

    # Parse reporter list
    reporters_requested = [r.strip() for r in reporter.split(",")]
    reporters_map = {
        "terminal": TerminalReporter,
        "junit": JUnitReporter,
        "json": JSONReporter,
    }

    # Generate reports
    for reporter_name in reporters_requested:
        if reporter_name not in reporters_map:
            typer.echo(
                f"Error: Unknown reporter: {reporter_name}",
                err=True,
            )
            raise typer.Exit(code=1)

        reporter_class = reporters_map[reporter_name]

        # Determine output path
        output_path = None
        if output and reporter_name in ("junit", "json"):
            output_path = Path(output)
        elif reporter_name == "junit" and not output:
            output_path = Path("junit-results.xml")
        elif reporter_name == "json" and not output:
            output_path = Path("results.json")

        config = ReporterConfig(output_path=output_path)
        reporter_instance = reporter_class(config)

        try:
            reporter_instance.report(suite_report)
        except Exception as e:\n            typer.echo(f"Error generating {reporter_name} report: {e}", err=True)
            raise typer.Exit(code=1)

    # Exit with appropriate code
    exit_code = (
        1
        if suite_report.regression_detected or suite_report.failed_count > 0
        else 0
    )
    raise typer.Exit(code=exit_code)


@app.command()
def version() -> None:
    """Display Assay version."""
    typer.echo("assay 0.1.0")


if __name__ == "__main__":
    app()
