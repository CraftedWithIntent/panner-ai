"""JUnit XML reporter for CI integration."""

import xml.etree.ElementTree as ET

from panner_ai.executor.executor import SuiteReport
from panner_ai.reporters.base import Reporter


class JUnitReporter(Reporter):
    """JUnit XML output reporter for CI/CD integration."""

    def report(self, suite_report: SuiteReport) -> None:
        """Generate JUnit XML report from suite results.

        Args:
            suite_report: Complete test suite execution results.
        """
        # Build XML structure
        testsuites = ET.Element("testsuites")
        testsuite = ET.SubElement(
            testsuites,
            "testsuite",
            name=suite_report.name,
            tests=str(suite_report.total_tests),
            failures=str(suite_report.failed_count),
        )

        # Add test cases
        for test_report in suite_report.test_reports:
            testcase = ET.SubElement(
                testsuite,
                "testcase",
                name=test_report.name,
                time=str((test_report.latency_ms or 0) / 1000.0),
            )

            # Add failure element if test failed
            if not test_report.passed:
                failure_msg = f"Test failed: {test_report.name}"
                if test_report.assertion_results:
                    failure_msg += "\n" + "\n".join(
                        f"  {r!s}" for r in test_report.assertion_results
                    )
                ET.SubElement(testcase, "failure", message=failure_msg)

            # Add regression warning as system-out
            if suite_report.baseline_delta:
                regression_msg = ", ".join(
                    f"{k}: {v:+.2%}" for k, v in suite_report.baseline_delta.items()
                )
                system_out = ET.SubElement(testcase, "system-out")
                system_out.text = regression_msg

        # Write to file or stdout
        tree = ET.ElementTree(testsuites)
        if self.config.output_path:
            self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
            tree.write(
                self.config.output_path,
                encoding="utf-8",
                xml_declaration=True,
            )
        else:
            # Write to stdout
            ET.dump(testsuites)
