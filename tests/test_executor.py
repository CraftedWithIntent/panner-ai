import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from assay.config.parser import SuiteConfig, TestCaseSpec
from assay.executor.executor import (
    AgentResponse,
    SuiteReport,
    TestCaseReport,
    TestExecutor,
)


@pytest.fixture
def mock_suite_config():
    test_cases = [
        TestCaseSpec(
            name="test_1",
            payload={"query": "What is 2+2?"},
            assertions=[],
            timeout_ms=5000,
        ),
        TestCaseSpec(
            name="test_2",
            payload={"query": "What is 3+3?"},
            assertions=[],
            timeout_ms=5000,
        ),
    ]
    return SuiteConfig(
        name="test-suite",
        description="Test suite for executor",
        agent_url="http://localhost:8000/api/agent",
        test_cases=test_cases,
        baseline_file=None,
    )


class TestAgentResponse:
    def test_agent_response_frozen(self):
        response = AgentResponse(
            status_code=200,
            body={"result": "ok"},
            headers={"content-type": "application/json"},
            latency_ms=50.0,
        )

        with pytest.raises(AttributeError):
            response.status_code = 500


class TestBaselineLoading:
    def test_load_baseline_exists(self):
        baseline_data = {"test_1": 1.0, "test_2": 0.5}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(baseline_data, f)
            baseline_file = f.name
        try:
            executor = TestExecutor(config=MagicMock(), baseline_file=baseline_file)
            loaded = executor._load_baseline()
            assert loaded == baseline_data
        finally:
            Path(baseline_file).unlink()

    def test_load_baseline_missing(self):
        executor = TestExecutor(config=MagicMock(), baseline_file="/nonexistent/baseline.json")
        loaded = executor._load_baseline()
        assert loaded is None


class TestExecuteSingleTest:
    @pytest.mark.asyncio
    async def test_execute_single_test_success(self, mock_suite_config):
        executor = TestExecutor(config=mock_suite_config)
        test_spec = mock_suite_config.test_cases[0]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "4"}
        mock_response.text = '{"result": "4"}'
        mock_response.headers = {"content-type": "application/json"}
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        test_name, response = await executor._execute_single_test(mock_client, test_spec)
        assert test_name == "test_1"
        assert response.status_code == 200
        assert response.body == {"result": "4"}
        assert response.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_execute_single_test_timeout(self, mock_suite_config):
        executor = TestExecutor(config=mock_suite_config)
        test_spec = mock_suite_config.test_cases[0]
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.TimeoutError("timeout")
        test_name, response = await executor._execute_single_test(mock_client, test_spec)
        assert test_name == "test_1"
        assert response.status_code == 0
        assert response.latency_ms >= 0


class TestExecutorRun:
    @pytest.mark.asyncio
    async def test_run_multiple_tests(self, mock_suite_config):
        executor = TestExecutor(config=mock_suite_config, max_workers=2)
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {"result": "4"}
        mock_response_1.headers = {}
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {"result": "6"}
        mock_response_2.headers = {}
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.side_effect = [mock_response_1, mock_response_2]
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            report = await executor.run()
        assert report.total_tests == 2
        assert report.passed_count == 2
        assert report.failed_count == 0

    @pytest.mark.asyncio
    async def test_run_empty_suite(self):
        config = SuiteConfig(
            name="empty",
            description="Empty",
            agent_url="http://localhost:8000",
            test_cases=[],
            baseline_file=None,
        )
        executor = TestExecutor(config=config)
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            report = await executor.run()
        assert report.total_tests == 0
        assert report.passed_count == 0
        assert report.failed_count == 0
