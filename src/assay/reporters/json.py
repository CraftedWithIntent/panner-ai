"""JSON reporter for telemetry export."""

import json

from assay.executor.executor import SuiteReport
from assay.reporters.base import Reporter


class JSONReporter(Reporter):
    """JSON output reporter for telemetry and data export."""

    def report(self, suite_report: SuiteReport) -> None:
        """Serialize suite results to JSON.

        Args:
            suite_report: Complete test suite execution results.
        """
        # Convert SuiteReport to serializable dict
        report_dict = {
            "suite_name": suite_report.name,
            "total_tests": suite_report.total_tests,
            "passed_count": suite_report.passed_count,
            "failed_count": suite_report.failed_count,
            "regression_detected": suite_report.regression_detected,
            "baseline_delta": suite_report.baseline_delta or {},
            "test_reports": [
                {
                    "test_name": tr.name,
                    "passed": tr.passed,
                    "latency_ms": tr.latency_ms,
                    "assertion_results": tr.assertion_results or [],
                }
                for tr in suite_report.test_reports
            ],
        }

        # Write to file or stdout
        json_str = json.dumps(report_dict, indent=2)
        if self.config.output_path:
            self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.config.output_path.write_text(json_str)
        else:
            print(json_str)
