"""Reporter base class and interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from panner_ai.executor.executor import SuiteReport


@dataclass(frozen=True)
class ReporterConfig:
    """Reporter configuration (immutable)."""

    output_path = None  # None = stdout


class Reporter(ABC):
    """Abstract reporter interface for suite results."""

    def __init__(self, config: ReporterConfig | None = None) -> None:
        """Initialize reporter.

        Args:
            config: Reporter configuration (output path, etc.)
        """
        self.config = config or ReporterConfig()

    @abstractmethod
    def report(self, suite_report: SuiteReport) -> None:
        """Generate report from suite results.

        Args:
            suite_report: Complete test suite execution results.
        """
