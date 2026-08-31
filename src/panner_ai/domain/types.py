"""Immutable domain types & value objects."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class AssertionType(str, Enum):
    """Deterministic assertion strategies."""
    REGEX = "regex"
    LATENCY = "latency"
    STATUS_CODE = "status_code"
    JSON_SCHEMA = "json_schema"
    LLM_JUDGE = "llm_judge"


@dataclass(frozen=True)
class AssertionSpec:
    """Immutable assertion specification."""
    type: AssertionType
    pattern: str | None = None
    max_latency_ms: int | None = None
    expected_status: int | None = None
    schema: dict[str, Any] | None = None
    judge_prompt: str | None = None
    threshold: float = 0.8


@dataclass(frozen=True)
class AgentResponse:
    """Immutable HTTP response from agent endpoint."""
    status_code: int
    body: str
    latency_ms: float
    headers: dict[str, str]


@dataclass(frozen=True)
class EvaluationResult:
    """Immutable result of a single assertion evaluation."""
    assertion: AssertionSpec
    passed: bool
    score: float
    message: str


@dataclass(frozen=True)
class TestCaseReport:
    """Immutable result of evaluating one test case."""
    test_name: str
    endpoint: str
    payload: dict[str, Any]
    response: AgentResponse
    evaluations: list[EvaluationResult]
    overall_score: float


@dataclass(frozen=True)
class SuiteReport:
    """Immutable aggregated report for entire test suite run."""
    suite_name: str
    test_cases: list[TestCaseReport]
    baseline_delta: float | None = None
    passed_count: int = 0
    failed_count: int = 0
    overall_score: float = 0.0
