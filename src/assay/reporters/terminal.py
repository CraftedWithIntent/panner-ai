"""Terminal reporter with ANSI colors using Rich."""

from rich.console import Console
from rich.table import Table

from assay.executor.executor import SuiteReport
from assay.reporters.base import Reporter, ReporterConfig


class TerminalReporter(Reporter):
    """ANSI-colored terminal output reporter."""

    def __init__(self, config: ReporterConfig | None = None) -> None:
        """Initialize terminal reporter.

        Args:
            config: Reporter config (ignored for terminal; always stdout).
        """
        super().__init__(config)
        self.console = Console()

    def report(self, suite_report: SuiteReport) -> None:
        """Print colored suite results to terminal.

        Args:
            suite_report: Complete test suite execution results.
        """
        # Test results table
        table = Table(title=f"Suite: {suite_report.name}")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")

        for test_report in suite_report.test_reports:
            status_icon = "✓" if test_report.passed else "✗"
            status_color = "green" if test_report.passed else "red"
            status_text = f"[{status_color}]{status_icon} {'PASS' if test_report.passed else 'FAIL'}[/{status_color}]"

            # Build details string
            details_parts = []
            if test_report.latency_ms:
                details_parts.append(f"{test_report.latency_ms:.1f}ms")

            # Add assertion results
            if test_report.assertion_results:
                for assertion_result in test_report.assertion_results:
                    if isinstance(assertion_result, dict):
                        status = assertion_result.get("passed", "unknown")
                        assertion_type = assertion_result.get("type", "unknown")
                        details_parts.append(f"{assertion_type}: {status}")

            details = ", ".join(details_parts)
            table.add_row(test_report.name, status_text, details)

        self.console.print(table)

        # Summary section
        summary_lines = [
            "\n[bold]Summary:[/bold]",
            f"  Passed: {suite_report.passed_count}/{suite_report.total_tests}",
            f"  Failed: {suite_report.failed_count}/{suite_report.total_tests}",
        ]

        if suite_report.baseline_delta:
            delta_str = ", ".join(
                f"{k}: {v:+.2%}" for k, v in suite_report.baseline_delta.items()
            )
            baseline_color = "green" if all(v >= 0 for v in suite_report.baseline_delta.values()) else "red"
            summary_lines.append(
                f"  Baseline Delta: [{baseline_color}]{delta_str}[/{baseline_color}]"
            )

        for line in summary_lines:
            self.console.print(line)

        # Overall status
        if suite_report.failed_count > 0:
            self.console.print("[red][bold]❌ FAILURES DETECTED[/bold][/red]")
        elif suite_report.regression_detected:
            self.console.print("[yellow][bold]⚠ REGRESSION DETECTED[/bold][/yellow]")
        else:
            self.console.print("[green][bold]✅ ALL PASSED[/bold][/green]")
