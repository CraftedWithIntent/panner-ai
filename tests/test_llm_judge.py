"""Tests for LLM-as-Judge evaluator and infrastructure."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from panner_ai.domain.types import AssertionSpec, AssertionType
from panner_ai.evaluators.llm_judge import evaluate_llm_judge
from panner_ai.infrastructure.llm import LLMClient, LLMResponse


@pytest.mark.asyncio
async def test_evaluate_llm_judge_high_score():
    """Test LLM judge with high semantic alignment."""
    assertion = AssertionSpec(
        type=AssertionType.LLM_JUDGE,
        judge_prompt="Response should correctly state that 2+2=4",
        threshold=0.8,
    )

    # Mock LLM response
    mock_llm_response = LLMResponse(
        score=0.95,
        reasoning="Response correctly identifies 2+2=4",
        tokens_used=45,
    )

    with patch.object(
        LLMClient, "judge_semantic_alignment", new_callable=AsyncMock
    ) as mock_judge:
        mock_judge.return_value = mock_llm_response

        result = await evaluate_llm_judge(
            assertion,
            response_text="The sum of 2 and 2 equals 4.",
        )

    assert result.passed is True
    assert result.score == 0.95
    assert "LLM judgment" in result.message


@pytest.mark.asyncio
async def test_evaluate_llm_judge_low_score():
    """Test LLM judge with low semantic alignment."""
    assertion = AssertionSpec(
        type=AssertionType.LLM_JUDGE,
        judge_prompt="Response should state 2+2=4",
        threshold=0.8,
    )

    mock_llm_response = LLMResponse(
        score=0.3,
        reasoning="Response incorrectly states 2+2=5",
        tokens_used=42,
    )

    with patch.object(
        LLMClient, "judge_semantic_alignment", new_callable=AsyncMock
    ) as mock_judge:
        mock_judge.return_value = mock_llm_response

        result = await evaluate_llm_judge(
            assertion,
            response_text="The sum of 2 and 2 equals 5.",
        )

    assert result.passed is False
    assert result.score == 0.3


@pytest.mark.asyncio
async def test_evaluate_llm_judge_no_prompt():
    """Test LLM judge with missing judge_prompt."""
    assertion = AssertionSpec(
        type=AssertionType.LLM_JUDGE,
        judge_prompt=None,  # Missing!
    )

    result = await evaluate_llm_judge(
        assertion,
        response_text="Some response",
    )

    assert result.passed is False
    assert result.score == 0.0
    assert "No judge prompt" in result.message


@pytest.mark.asyncio
async def test_evaluate_llm_judge_custom_threshold():
    """Test LLM judge with custom pass threshold."""
    assertion = AssertionSpec(
        type=AssertionType.LLM_JUDGE,
        judge_prompt="Check if response is good",
        threshold=0.6,  # Custom threshold
    )

    mock_llm_response = LLMResponse(
        score=0.65,
        reasoning="Barely passes",
        tokens_used=40,
    )

    with patch.object(
        LLMClient, "judge_semantic_alignment", new_callable=AsyncMock
    ) as mock_judge:
        mock_judge.return_value = mock_llm_response

        result = await evaluate_llm_judge(
            assertion,
            response_text="Response",
        )

    assert result.passed is True
    assert result.score == 0.65


class TestLLMClient:
    """Test LLM infrastructure layer."""

    @pytest.mark.asyncio
    async def test_llm_client_initialization(self):
        """Test LLM client initialization."""
        client = LLMClient(model="gpt-4")
        assert client.model == "gpt-4"
        assert client.total_tokens_used == 0
        assert client.requests_made == 0

    @pytest.mark.asyncio
    async def test_llm_client_default_model(self):
        """Test LLM client uses gpt-4 by default."""
        with patch.dict("os.environ", {}, clear=True):
            client = LLMClient()
            assert client.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_llm_client_env_model(self):
        """Test LLM client reads model from env var."""
        with patch.dict("os.environ", {"LLM_MODEL": "claude-opus"}):
            client = LLMClient()
            assert client.model == "claude-opus"

    @pytest.mark.asyncio
    async def test_parse_json_response_valid(self):
        """Test JSON parsing with valid response."""
        response = '{"score": 0.87, "reasoning": "Good answer"}'
        parsed = LLMClient._parse_json_response(response)

        assert parsed["score"] == 0.87
        assert parsed["reasoning"] == "Good answer"

    @pytest.mark.asyncio
    async def test_parse_json_response_invalid(self):
        """Test JSON parsing with invalid JSON."""
        response = "This is not JSON"
        parsed = LLMClient._parse_json_response(response)

        assert parsed["score"] == 0.5
        assert "Failed to parse" in parsed["reasoning"]

    @pytest.mark.asyncio
    async def test_parse_json_response_invalid_type(self):
        """Test JSON parsing with non-dict response."""
        response = '["not", "a", "dict"]'
        parsed = LLMClient._parse_json_response(response)

        assert parsed["score"] == 0.5
        assert "Invalid response format" in parsed["reasoning"]

    def test_estimated_cost_gpt4(self):
        """Test cost estimation for GPT-4."""
        client = LLMClient(model="gpt-4")
        client.total_tokens_used = 1000

        cost = client.estimated_cost
        # GPT-4: ~$0.045/1K tokens average
        assert 0.04 < cost < 0.05

    def test_estimated_cost_gpt35(self):
        """Test cost estimation for GPT-3.5-turbo."""
        client = LLMClient(model="gpt-3.5-turbo")
        client.total_tokens_used = 1000

        cost = client.estimated_cost
        # GPT-3.5-turbo: ~$0.001/1K tokens
        assert 0.0008 < cost < 0.0012

    def test_estimated_cost_claude_opus(self):
        """Test cost estimation for Claude Opus."""
        client = LLMClient(model="claude-opus")
        client.total_tokens_used = 1000

        cost = client.estimated_cost
        # Claude Opus: ~$0.045/1K tokens average
        assert 0.04 < cost < 0.05

    def test_estimated_cost_claude_sonnet(self):
        """Test cost estimation for Claude Sonnet."""
        client = LLMClient(model="claude-sonnet")
        client.total_tokens_used = 1000

        cost = client.estimated_cost
        # Claude Sonnet: ~$0.009/1K tokens average
        assert 0.008 < cost < 0.01


class TestLLMClientJudgment:
    """Test LLM judgment via infrastructure layer."""

    @pytest.mark.asyncio
    async def test_judge_semantic_alignment_success(self):
        """Test successful semantic alignment judgment."""
        client = LLMClient(model="gpt-4")

        # Mock litellm response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"score": 0.92, "reasoning": "Excellent"}'
        mock_response.usage.prompt_tokens = 30
        mock_response.usage.completion_tokens = 15

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await client.judge_semantic_alignment(
                response="The answer is 42",
                expected="Should explain why 42 is the answer",
            )

        assert result.score == 0.92
        assert result.reasoning == "Excellent"
        assert result.tokens_used == 45
        assert client.total_tokens_used == 45
        assert client.requests_made == 1

    @pytest.mark.asyncio
    async def test_judge_semantic_alignment_invalid_json_fallback(self):
        """Test fallback when LLM returns invalid JSON."""
        client = LLMClient(model="gpt-4")

        # Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is not JSON"
        mock_response.usage.prompt_tokens = 30
        mock_response.usage.completion_tokens = 10

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await client.judge_semantic_alignment(
                response="Some response",
                expected="Expected output",
            )

        assert result.score == 0.5  # Fallback score
        assert "Failed to parse" in result.reasoning

    @pytest.mark.asyncio
    async def test_judge_semantic_alignment_score_clamped(self):
        """Test score is clamped to [0.0, 1.0]."""
        client = LLMClient(model="gpt-4")

        # Mock response with out-of-range score
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"score": 1.5, "reasoning": "Out of range"}'
        mock_response.usage.prompt_tokens = 30
        mock_response.usage.completion_tokens = 10

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await client.judge_semantic_alignment(
                response="Response",
                expected="Expected",
            )

        assert result.score == 1.0  # Clamped to max

    @pytest.mark.asyncio
    async def test_judge_semantic_alignment_negative_score_clamped(self):
        """Test negative score is clamped to 0.0."""
        client = LLMClient(model="gpt-4")

        # Mock response with negative score
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"score": -0.5, "reasoning": "Bad"}'
        mock_response.usage.prompt_tokens = 30
        mock_response.usage.completion_tokens = 10

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await client.judge_semantic_alignment(
                response="Response",
                expected="Expected",
            )

        assert result.score == 0.0  # Clamped to min


class TestJudgmentDeterminism:
    """Verify LLM judgment responses are deterministic with mocking."""

    @pytest.mark.asyncio
    async def test_llm_determinism_mocked(self):
        """Test determinism with 10 mocked LLM calls."""
        assertion = AssertionSpec(
            type=AssertionType.LLM_JUDGE,
            judge_prompt="Is response correct?",
            threshold=0.8,
        )

        mock_response = LLMResponse(
            score=0.88,
            reasoning="Consistent response",
            tokens_used=40,
        )

        with patch.object(
            LLMClient, "judge_semantic_alignment", new_callable=AsyncMock
        ) as mock_judge:
            mock_judge.return_value = mock_response

            # Run 10 times
            results = []
            for _ in range(10):
                result = await evaluate_llm_judge(
                    assertion,
                    response_text="Test response",
                )
                results.append(result)

        # All should be identical
        assert all(r.score == 0.88 for r in results)
        assert all(r.passed is True for r in results)
        assert all(r.message == results[0].message for r in results)
