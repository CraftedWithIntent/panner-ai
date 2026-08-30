import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from assay.config.parser import SuiteConfig


@dataclass(frozen=True)
class AgentResponse:
    """Immutable response from agent endpoint."""

    status_code: int
    body: str | dict
    headers: dict[str, str]
    latency_ms: float


@dataclass(frozen=True)
class TestCaseReport:
    """Immutable test case execution report."""

    name: str
    passed: bool
    response: AgentResponse
    assertion_results: list[dict[str, Any]]
    latency_ms: float


@dataclass(frozen=True)
class SuiteReport:
    """Immutable suite execution report."""

    name: str
    total_tests: int
    passed_count: int
    failed_count: int
    test_reports: list[TestCaseReport]
    baseline_delta: dict[str, float] | None
    regression_detected: bool


class TestExecutor:
    """Orchestrate async HTTP requests and coordinate test execution.

    Responsibilities:
    - Load suite config and optional baseline
    - Send async HTTP requests to agent endpoint
    - Measure latency and capture responses
    - Parallelize with concurrency control (max_workers)
    - Aggregate results into SuiteReport
    - Compute baseline regression
    """

    def __init__(
        self,
        config: SuiteConfig,
        baseline_file: str | None = None,
        max_workers: int = 5,
    ):
        """Initialize executor.

        Args:
            config: Parsed SuiteConfig from M1.1
            baseline_file: Path to baseline.json for regression comparison
            max_workers: Max concurrent HTTP requests (default 5)
        """
        self.config = config
        self.baseline_file = baseline_file or "baseline.json"
        self.max_workers = max_workers
        self.baseline: dict[str, float] | None = None

    def _load_baseline(self) -> dict[str, float] | None:
        """Load baseline.json if it exists.

        Returns:
            Dict of test_name -> score, or None if file does not exist
        """
        baseline_path = Path(self.baseline_file)
        if baseline_path.exists():
            try:
                with open(baseline_path) as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                return None
        return None

    async def _execute_single_test(
        self, client: httpx.AsyncClient, test_spec
    ) -> tuple[str, AgentResponse]:
        """Execute a single test case and measure latency.

        Args:
            client: httpx AsyncClient for HTTP requests
            test_spec: TestCaseSpec from config

        Returns:
            Tuple of (test_name, AgentResponse)

        Raises:
            httpx.TimeoutError: If request exceeds timeout_ms
        """
        timeout_sec = test_spec.timeout_ms / 1000.0

        start_time = time.time()
        try:
            response = await client.post(
                self.config.agent_url,
                json=test_spec.payload,
                timeout=timeout_sec,
            )
        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            agent_response = AgentResponse(
                status_code=0,
                body=f"Timeout after {test_spec.timeout_ms}ms",
                headers={},
                latency_ms=latency_ms,
            )
            return test_spec.name, agent_response

        latency_ms = (time.time() - start_time) * 1000

        try:
            body = response.json()
        except (json.JSONDecodeError, ValueError):
            body = response.text

        agent_response = AgentResponse(
            status_code=response.status_code,
            body=body,
            headers=dict(response.headers),
            latency_ms=latency_ms,
        )

        return test_spec.name, agent_response

    async def run(self) -> SuiteReport:
        """Execute all test cases with concurrency control.

        Returns:
            SuiteReport with all results and baseline comparison
        """
        self.baseline = self._load_baseline()

        semaphore = asyncio.Semaphore(self.max_workers)

        async def bounded_execute(client, spec):
            async with semaphore:
                return await self._execute_single_test(client, spec)

        async with httpx.AsyncClient() as client:
            tasks = [
                bounded_execute(client, spec) for spec in self.config.test_cases
            ]
            results = await asyncio.gather(*tasks, return_exceptions=False)

        test_reports = []
        for test_name, agent_response in results:
            passed = 200 <= agent_response.status_code < 300

            test_report = TestCaseReport(
                name=test_name,
                passed=passed,
                response=agent_response,
                assertion_results=[],
                latency_ms=agent_response.latency_ms,
            )
            test_reports.append(test_report)

        total_tests = len(test_reports)
        passed_count = sum(1 for r in test_reports if r.passed)
        failed_count = total_tests - passed_count

        baseline_delta = None
        regression_detected = False
        if self.baseline:
            baseline_delta = {}
            for report in test_reports:
                prior_score = self.baseline.get(report.name)
                if prior_score is not None:
                    current_score = 1.0 if report.passed else 0.0
                    delta = current_score - prior_score
                    baseline_delta[report.name] = delta
                    if delta < 0:
                        regression_detected = True

        return SuiteReport(
            name=self.config.name,
            total_tests=total_tests,
            passed_count=passed_count,
            failed_count=failed_count,
            test_reports=test_reports,
            baseline_delta=baseline_delta,
            regression_detected=regression_detected,
        )
