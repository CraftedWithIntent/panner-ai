"""Pure functional evaluators - MVP version (exception handlers added in Phase 1)."""

import json
import re
from collections.abc import Callable

from assay.domain.types import (
    AgentResponse,
    AssertionSpec,
    AssertionType,
    EvaluationResult,
)


def evaluate_regex(assertion: AssertionSpec, response: AgentResponse) -> EvaluationResult:
    """Pure regex evaluation against response body."""
    if not assertion.pattern:
        return EvaluationResult(
            assertion=assertion,
            passed=False,
            score=0.0,
            message="No regex pattern provided",
        )

    match = re.search(assertion.pattern, response.body)
    passed = match is not None
    score = 1.0 if passed else 0.0
    return EvaluationResult(
        assertion=assertion,
        passed=passed,
        score=score,
        message=f"Pattern {'found' if passed else 'not found'}",
    )


def evaluate_latency(assertion: AssertionSpec, response: AgentResponse) -> EvaluationResult:
    """Pure latency threshold evaluation."""
    if assertion.max_latency_ms is None:
        return EvaluationResult(
            assertion=assertion,
            passed=False,
            score=0.0,
            message="No max latency specified",
        )

    passed = response.latency_ms <= assertion.max_latency_ms
    score = 1.0 - min(response.latency_ms / assertion.max_latency_ms, 1.0)
    return EvaluationResult(
        assertion=assertion,
        passed=passed,
        score=score,
        message=f"Latency: {response.latency_ms}ms",
    )


def evaluate_status_code(assertion: AssertionSpec, response: AgentResponse) -> EvaluationResult:
    """Pure HTTP status code evaluation."""
    if assertion.expected_status is None:
        return EvaluationResult(
            assertion=assertion,
            passed=False,
            score=0.0,
            message="No expected status code",
        )

    passed = response.status_code == assertion.expected_status
    score = 1.0 if passed else 0.0
    return EvaluationResult(
        assertion=assertion,
        passed=passed,
        score=score,
        message=f"Status: {response.status_code}",
    )


def evaluate_json_schema(assertion: AssertionSpec, response: AgentResponse) -> EvaluationResult:
    """Pure JSON schema validation."""
    if not assertion.schema:
        return EvaluationResult(
            assertion=assertion,
            passed=False,
            score=0.0,
            message="No schema provided",
        )

    body_json = json.loads(response.body)
    required_keys = assertion.schema.get("required", [])
    missing_keys = [k for k in required_keys if k not in body_json]
    passed = len(missing_keys) == 0
    score = 1.0 if passed else 0.0
    return EvaluationResult(
        assertion=assertion,
        passed=passed,
        score=score,
        message=f"Schema check: {'passed' if passed else 'failed'}",
    )


def get_evaluator(assertion_type: AssertionType) -> Callable:
    """Router: returns the appropriate evaluator function.
    
    Note: LLM_JUDGE evaluator is async and requires special handling in pipeline.
    See assay.evaluators.llm_judge for async variant.
    """
    evaluators = {
        AssertionType.REGEX: evaluate_regex,
        AssertionType.LATENCY: evaluate_latency,
        AssertionType.STATUS_CODE: evaluate_status_code,
        AssertionType.JSON_SCHEMA: evaluate_json_schema,
    }
    return evaluators.get(assertion_type, lambda _, __: EvaluationResult(
        assertion=AssertionSpec(type=AssertionType.REGEX),
        passed=False,
        score=0.0,
        message="Unknown assertion type",
    ))
