"""LLM abstraction layer for vendor-agnostic LLM access (OpenAI, Anthropic, etc.)."""

import json
import os
from dataclasses import dataclass

import litellm


@dataclass(frozen=True)
class LLMResponse:
    """Immutable LLM response with usage tracking."""
    score: float
    reasoning: str
    tokens_used: int = 0


class LLMClient:
    """Vendor-agnostic LLM client supporting OpenAI and Anthropic."""

    def __init__(self, model: str | None = None):
        """Initialize LLM client.
        
        Args:
            model: Model name (e.g., 'gpt-4', 'claude-opus').
                   Defaults to env var LLM_MODEL or 'gpt-4'.
        """
        self.model = model or os.getenv("LLM_MODEL", "gpt-4")
        self.total_tokens_used = 0
        self.requests_made = 0

    async def judge_semantic_alignment(
        self,
        response: str,
        expected: str,
    ) -> LLMResponse:
        """Judge semantic alignment between response and expected output.
        
        Args:
            response: Agent's actual response text
            expected: Human description of expected correctness
            
        Returns:
            LLMResponse with score [0.0, 1.0] and reasoning
        """
        prompt = self._build_prompt(response, expected)

        try:
            # Call LLM with structured JSON response format
            llm_response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert evaluator. Rate semantic alignment "
                            "between responses and expected outputs. "
                            "Always respond with valid JSON: {\"score\": float, \"reasoning\": string}"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=256,
            )

            # Extract response text
            content = llm_response.choices[0].message.content
            tokens_used = (
                llm_response.usage.prompt_tokens + llm_response.usage.completion_tokens
            )

            # Track usage
            self.total_tokens_used += tokens_used
            self.requests_made += 1

            # Parse JSON
            parsed = self._parse_json_response(content)
            score = float(parsed.get("score", 0.5))
            reasoning = str(parsed.get("reasoning", ""))

            # Validate score range
            score = max(0.0, min(1.0, score))

            return LLMResponse(
                score=score,
                reasoning=reasoning,
                tokens_used=tokens_used,
            )

        except Exception as e:\n            # Phase 1: Errors propagate
            raise RuntimeError(f"LLM judgment failed: {e}") from e

    @staticmethod
    def _build_prompt(response: str, expected: str) -> str:
        """Build evaluation prompt."""
        return (
            f"Rate semantic alignment (0.0–1.0):\n\n"
            f"Expected correctness:\n{expected}\n\n"
            f"Actual response:\n{response}\n\n"
            f"Provide JSON: {{'score': <float>, 'reasoning': '<explanation>'}}"
        )

    @staticmethod
    def _parse_json_response(content: str) -> dict:
        """Parse JSON from LLM response, return dict."""
        try:
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                return {"score": 0.5, "reasoning": "Invalid response format"}
            return parsed
        except json.JSONDecodeError:
            return {"score": 0.5, "reasoning": "Failed to parse JSON"}

    @property
    def estimated_cost(self) -> float:
        """Estimate cost based on token usage.
        
        Pricing (as of 2026):
        - GPT-4: $0.03/1K input, $0.06/1K output
        - GPT-3.5-turbo: $0.0005/1K input, $0.0015/1K output
        - Claude Opus: $0.015/1K input, $0.075/1K output
        - Claude Sonnet: $0.003/1K input, $0.015/1K output
        """
        if "gpt-4" in self.model.lower():
            return (self.total_tokens_used / 1000) * 0.045  # avg in/out
        elif "gpt-3.5" in self.model.lower():
            return (self.total_tokens_used / 1000) * 0.001
        elif "claude-opus" in self.model.lower():
            return (self.total_tokens_used / 1000) * 0.045
        elif "claude-sonnet" in self.model.lower():
            return (self.total_tokens_used / 1000) * 0.009
        else:
            return (self.total_tokens_used / 1000) * 0.03  # conservative estimate
