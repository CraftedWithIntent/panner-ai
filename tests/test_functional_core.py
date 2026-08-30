"""Unit tests for functional core."""

import pytest

from assay.core.evaluators import (
    evaluate_json_schema,
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


class TestJsonSchemaEvaluator:
    def test_json_schema_valid(self):
        response = AgentResponse(
            status_code=200,
            body='{"result": "success", "count": 42}',
            latency_ms=50.0,
            headers={},
        )
        assertion = AssertionSpec(
            type=AssertionType.JSON_SCHEMA,
            schema={"required": ["result", "count"]},
        )
        result = evaluate_json_schema(assertion, response)
        assert result.passed is True
        assert result.score == 1.0

    def test_json_schema_missing_field(self):
        response = AgentResponse(
            status_code=200,
            body='{"result": "success"}',
            latency_ms=50.0,
            headers={},
        )
        assertion = AssertionSpec(
            type=AssertionType.JSON_SCHEMA,
            schema={"required": ["result", "count"]},
        )
        result = evaluate_json_schema(assertion, response)
        assert result.passed is False
        assert result.score == 0.0

    def test_json_schema_empty_required(self):
        response = AgentResponse(
            status_code=200,
            body='{"anything": "goes"}',
            latency_ms=50.0,
            headers={},
        )
        assertion = AssertionSpec(
            type=AssertionType.JSON_SCHEMA,
            schema={"required": []},
        )
        result = evaluate_json_schema(assertion, response)
        assert result.passed is True


class TestEvaluatorEdgeCases:
    def test_regex_empty_pattern(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.REGEX,
            pattern=None,
        )
        result = evaluate_regex(assertion, sample_response)
        assert result.passed is False

    def test_latency_no_threshold(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.LATENCY,
            max_latency_ms=None,
        )
        result = evaluate_latency(assertion, sample_response)
        assert result.passed is False

    def test_status_code_no_expected(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.STATUS_CODE,
            expected_status=None,
        )
        result = evaluate_status_code(assertion, sample_response)
        assert result.passed is False

    def test_json_schema_no_schema(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.JSON_SCHEMA,
            schema=None,
        )
        result = evaluate_json_schema(assertion, sample_response)
        assert result.passed is False


class TestDeterminism:
    """Verify all evaluators return consistent results across 100 iterations."""

    def test_regex_determinism(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.REGEX,
            pattern=r'"result"',
        )
        results = [evaluate_regex(assertion, sample_response) for _ in range(100)]
        assert all(r.passed is True for r in results)
        assert all(r.score == 1.0 for r in results)

    def test_latency_determinism(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.LATENCY,
            max_latency_ms=100,
        )
        results = [evaluate_latency(assertion, sample_response) for _ in range(100)]
        assert all(r.passed is True for r in results)

    def test_status_code_determinism(self, sample_response):
        assertion = AssertionSpec(
            type=AssertionType.STATUS_CODE,
            expected_status=200,
        )
        results = [evaluate_status_code(assertion, sample_response) for _ in range(100)]
        assert all(r.passed is True for r in results)
        assert all(r.score == 1.0 for r in results)

    def test_json_schema_determinism(self):
        response = AgentResponse(
            status_code=200,
            body='{"result": "success"}',
            latency_ms=50.0,
            headers={},
        )
        assertion = AssertionSpec(
            type=AssertionType.JSON_SCHEMA,
            schema={"required": ["result"]},
        )
        results = [evaluate_json_schema(assertion, response) for _ in range(100)]
        assert all(r.passed is True for r in results)
        assert all(r.score == 1.0 for r in results)
