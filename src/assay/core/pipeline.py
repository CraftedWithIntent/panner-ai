"""Pure pipeline reducer: orchestrates evaluators without I/O."""

from assay.core.evaluators import get_evaluator
from assay.domain.types import (
    AgentResponse,
    AssertionSpec,
    SuiteReport,
    TestCaseReport,
)


def evaluate_test_case(
    test_name: str,
    endpoint: str,
    payload: dict,
    response: AgentResponse,
    assertions: list[AssertionSpec],
) -> TestCaseReport:
    """Pure evaluation of one test case against all assertions."""
    evaluations = []

    for assertion in assertions:
        evaluator = get_evaluator(assertion.type)
        result = evaluator(assertion, response)
        evaluations.append(result)

    total_score = sum(e.score for e in evaluations) / len(evaluations) if evaluations else 0.0

    return TestCaseReport(
        test_name=test_name,
        endpoint=endpoint,
        payload=payload,
        response=response,
        evaluations=evaluations,
        overall_score=total_score,
    )


def aggregate_suite(
    suite_name: str,
    test_cases: list[TestCaseReport],
    baseline_delta: float | None = None,
) -> SuiteReport:
    """Pure aggregation: reduces test cases into suite-level report."""
    passed_count = sum(1 for tc in test_cases if tc.overall_score >= 0.8)
    failed_count = len(test_cases) - passed_count
    overall_score = sum(tc.overall_score for tc in test_cases) / len(test_cases) if test_cases else 0.0

    return SuiteReport(
        suite_name=suite_name,
        test_cases=test_cases,
        baseline_delta=baseline_delta,
        passed_count=passed_count,
        failed_count=failed_count,
        overall_score=overall_score,
    )
