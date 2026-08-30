"""Unit tests for functional core."""

import pytest

from assay.core.evaluators import (
    evaluate_latency,
    evaluate_regex,
    evaluate_status_code,
)
from assay.domain.types import (
    AgentResponse,
    AssertionSpec,
    AssertionType,
)


@pytest.fixture
def sample_response():
    return AgentResponse(
        status_code=200,
        body='{"result": "success"}',
        latency_ms=45.5,
        headers={"content-type": "application/json"},
    )


class TestRegexEvaluator:
    def test_regex_match(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.REGEX,
            pattern=r'"result"',
        )
        result = evaluate_regex(assertion, sample_response)
        assert result.passed is True
        assert result.score == 1.0

    def test_regex_no_match(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.REGEX,
            pattern=r'"missing"',
        )
        result = evaluate_regex(assertion, sample_response)
        assert result.passed is False
        assert result.score == 0.0


class TestLatencyEvaluator:
    def test_latency_within_threshold(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.LATENCY,
            max_latency_ms=100,
        )
        result = evaluate_latency(assertion, sample_response)
        assert result.passed is True

    def test_latency_exceeds_threshold(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.LATENCY,
            max_latency_ms=30,
        )
        result = evaluate_latency(assertion, sample_response)
        assert result.passed is False


class TestStatusCodeEvaluator:
    def test_status_match(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.STATUS_CODE,
            expected_status=200,
        )
        result = evaluate_status_code(assertion, sample_response)
        assert result.passed is True
        assert result.score == 1.0

    def test_status_mismatch(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.STATUS_CODE,
            expected_status=404,
        )
        result = evaluate_status_code(assertion, sample_response)
        assert result.passed is False
        assert result.score == 0.0
