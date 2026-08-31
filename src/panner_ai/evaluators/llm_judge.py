"""LLM-as-Judge evaluator: Semantic correctness scoring via Claude/GPT-4."""

from panner_ai.domain.types import (
    AssertionSpec,
    EvaluationResult,
)
from panner_ai.infrastructure.llm import LLMClient


async def evaluate_llm_judge(
    assertion: AssertionSpec,
    response_text: str,
    model: str | None = None,
) -> EvaluationResult:
    """Judge semantic alignment using LLM (Claude/GPT-4).
    
    Args:
        assertion: AssertionSpec with judge_prompt (expected correctness description)
        response_text: Agent's response to evaluate
        model: LLM model to use (defaults to env var or gpt-4)
        
    Returns:
        EvaluationResult with score [0.0, 1.0] from LLM judgment
        
    Raises:
        RuntimeError: If LLM API call fails (Phase 1: errors propagate)
    """
    if not assertion.judge_prompt:
        return EvaluationResult(
            assertion=assertion,
            passed=False,
            score=0.0,
            message="No judge prompt (expected correctness) provided",
        )

    # Create LLM client
    client = LLMClient(model=model)

    # Call LLM for semantic judgment
    llm_response = await client.judge_semantic_alignment(
        response=response_text,
        expected=assertion.judge_prompt,
    )

    # Extract score from LLM response
    score = llm_response.score
    passed = score >= (assertion.threshold or 0.8)

    return EvaluationResult(
        assertion=assertion,
        passed=passed,
        score=score,
        message=f"LLM judgment: {llm_response.reasoning[:100]}...",
    )
