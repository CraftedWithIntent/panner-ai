"""
Loan Approval Agent — FastAPI service with Claude integration.

This example demonstrates a complete AI agent that processes loan applications
and makes approval decisions using Claude as the reasoning engine. It includes:

- FastAPI service with `/apply` endpoint
- Request validation (Pydantic models)
- Integration with Anthropic Claude API
- Structured decision output (approval status + reasoning)
- Error handling and logging
"""

import json
import logging
import os
from typing import Optional

from anthropic import Anthropic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Loan Approval Agent", version="1.0.0")

# Initialize Anthropic client (uses ANTHROPIC_API_KEY env var)
client = Anthropic()


# ============================================================================
# Request/Response Models
# ============================================================================


class LoanApplication(BaseModel):
    """Loan application request."""

    name: str = Field(..., min_length=1, description="Applicant name")
    income: float = Field(..., gt=0, description="Annual income in USD")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount in USD")
    employment_years: float = Field(
        ..., ge=0, description="Years of employment history"
    )
    existing_debt: float = Field(default=0, ge=0, description="Existing debt in USD")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "income": 75000,
                "credit_score": 720,
                "loan_amount": 20000,
                "employment_years": 5,
                "existing_debt": 5000,
            }
        }


class LoanDecision(BaseModel):
    """Loan approval decision."""

    approved: bool = Field(..., description="Whether loan was approved")
    interest_rate: Optional[float] = Field(
        default=None, ge=0, description="Interest rate if approved, None if denied"
    )
    reason: str = Field(..., description="Reasoning for the decision")
    risk_score: float = Field(0.0, ge=0.0, le=1.0, description="Risk score (0=low, 1=high)")

    class Config:
        json_schema_extra = {
            "example": {
                "approved": True,
                "interest_rate": 5.5,
                "reason": "Strong credit profile with stable employment. Debt-to-income ratio is healthy.",
                "risk_score": 0.25,
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


# ============================================================================
# LLM-Powered Loan Approval Logic
# ============================================================================


def evaluate_loan_application(application: LoanApplication) -> LoanDecision:
    """
    Use Claude to evaluate a loan application and make an approval decision.

    This function demonstrates:
    - Structured prompting for consistent JSON output
    - Claude conversation API for decision reasoning
    - Response parsing and validation

    Args:
        application: Loan application with applicant details

    Returns:
        LoanDecision with approval status, interest rate, reasoning, and risk score
    """

    # Calculate financial metrics
    debt_to_income_ratio = (
        (application.existing_debt / application.income) * 100
        if application.income > 0
        else 0
    )
    loan_to_income_ratio = (application.loan_amount / application.income) * 100

    # Prepare context for Claude
    evaluation_prompt = f"""
You are a loan approval officer evaluating a loan application.

Applicant Information:
- Name: {application.name}
- Annual Income: ${application.income:,.2f}
- Credit Score: {application.credit_score}/850
- Requested Loan Amount: ${application.loan_amount:,.2f}
- Employment History: {application.employment_years} years
- Existing Debt: ${application.existing_debt:,.2f}

Financial Metrics:
- Debt-to-Income Ratio: {debt_to_income_ratio:.1f}%
- Loan-to-Income Ratio: {loan_to_income_ratio:.1f}%

Evaluation Criteria:
1. Credit Score: 750+ (excellent), 700-749 (good), 650-699 (fair), <650 (poor)
2. Debt-to-Income Ratio: <36% (good), 36-50% (acceptable), >50% (problematic)
3. Employment: 2+ years stable employment is preferred
4. Loan-to-Income: <20% (preferred), 20-40% (acceptable), >40% (risky)

Based on these criteria, provide a loan decision in JSON format:
{{
    "approved": true/false,
    "interest_rate": 3.5-12.5 (or null if denied),
    "reason": "Clear explanation of the decision",
    "risk_score": 0.0-1.0
}}

Guidelines:
- Credit score > 750 + DTI < 36% = typically approve at lower rates
- Credit score 700-750 + DTI < 45% = typically approve at moderate rates
- Credit score < 650 or DTI > 50% = typically deny
- Adjust rates based on employment stability and overall risk profile
- Keep reasoning concise but thorough

Return ONLY valid JSON, no additional text.
"""

    try:
        # Call Claude API with structured prompt
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": evaluation_prompt}],
        )

        # Extract and parse response
        response_text = message.content[0].text
        logger.info(f"Claude response: {response_text}")

        # Parse JSON from Claude's response
        decision_data = json.loads(response_text)

        # Validate and construct LoanDecision
        decision = LoanDecision(
            approved=decision_data.get("approved", False),
            interest_rate=decision_data.get("interest_rate"),
            reason=decision_data.get("reason", "Unable to determine"),
            risk_score=decision_data.get("risk_score", 0.5),
        )

        return decision

    except json.JSONDecodeError as e:\n        logger.error(f"Failed to parse Claude response as JSON: {e}")
        raise ValueError("Invalid response format from LLM evaluation")
    except Exception as e:\n        logger.error(f"Error evaluating loan: {e}")
        raise


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with status and version
    """
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/apply", response_model=LoanDecision)
def apply_for_loan(application: LoanApplication) -> LoanDecision:
    """
    Process a loan application and return approval decision.

    This endpoint:
    1. Validates the application data (Pydantic)
    2. Sends application to Claude for evaluation
    3. Returns structured decision with interest rate and reasoning

    Args:
        application: LoanApplication with applicant details

    Returns:
        LoanDecision with approval status, interest rate, and reasoning

    Raises:
        HTTPException: If evaluation fails
    """
    try:
        logger.info(f"Processing application for {application.name}")
        decision = evaluate_loan_application(application)
        logger.info(f"Decision: approved={decision.approved}, rate={decision.interest_rate}")
        return decision
    except ValueError as e:\n        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:\n        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during evaluation")


# ============================================================================
# Development / Testing
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    # Run locally: uvicorn agent:app --reload --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
