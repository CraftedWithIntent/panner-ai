# Loan Approval Agent Example

This directory contains a **complete, working example** of an AI agent built with Panner AI for testing and validation.

## What It Does

The **Loan Approval Agent** is a FastAPI service that:

1. Accepts loan applications via HTTP POST
2. Uses Claude (Anthropic) as the decision engine
3. Returns structured approval decisions with interest rates and reasoning
4. Integrates seamlessly with Panner AI for comprehensive testing

### Architecture

```
Client HTTP Request
    ↓
FastAPI /apply endpoint
    ↓
Pydantic validation
    ↓
Claude API (LLM reasoning)
    ↓
Structured JSON decision
    ↓
Response to client
```

## Quick Start

### 1. Install Dependencies

```bash
cd examples/loan-approval-agent
pip install -r requirements.txt
```

**Requirements:**
- Python 3.11+
- FastAPI (HTTP framework)
- Uvicorn (async HTTP server)
- Anthropic SDK (Claude integration)
- Pydantic (data validation)

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from [Anthropic Console](https://console.anthropic.com)

### 3. Run the Agent

```bash
python agent.py
```

Server starts at `http://localhost:8000`

### 4. Test with cURL

```bash
curl -X POST http://localhost:8000/apply \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "income": 75000,
    "credit_score": 720,
    "loan_amount": 20000,
    "employment_years": 5,
    "existing_debt": 5000
  }'
```

**Response:**
```json
{
  "approved": true,
  "interest_rate": 5.5,
  "reason": "Strong credit profile with stable employment. Debt-to-income ratio is healthy.",
  "risk_score": 0.25
}
```

### 5. Test with Panner AI

```bash
# Navigate to repo root
cd ../..

# Run the test suite
panner-ai run examples/loan-approval-agent/tests/suites/loan_approval.yaml \
  --reporter terminal \
  --baseline-file baseline.json
```

## Test Suite Overview

The `tests/suites/loan_approval.yaml` includes 4 comprehensive test cases:

| Test | Purpose | Expected Outcome |
|------|---------|------------------|
| `approve_strong_credit_low_debt` | Happy path: excellent credit + low debt | ✅ Approval at favorable rate |
| `approve_good_credit_moderate_debt` | Balanced case: good credit + moderate debt | ✅ Approval at moderate rate |
| `deny_poor_credit_high_debt` | Rejection case: poor credit + high debt | ❌ Denial or very high rate |
| `validate_endpoint_performance` | Performance & schema validation | ✅ <5s response time |

### Assertion Types Used

- **status_code** — HTTP 200 success
- **json_schema** — Response structure validation (Pydantic-compatible)
- **latency** — Response time threshold (max 5 seconds)
- **llm_judge** — Semantic correctness via Claude (min score: 0.75-0.85)

## API Reference

### POST /apply

**Request Body:**
```json
{
  "name": "string (required)",
  "income": "float (required, > 0)",
  "credit_score": "integer (required, 300-850)",
  "loan_amount": "float (required, > 0)",
  "employment_years": "float (required, >= 0)",
  "existing_debt": "float (optional, default: 0)"
}
```

**Response (200 OK):**
```json
{
  "approved": "boolean",
  "interest_rate": "float | null (null if denied)",
  "reason": "string (explanation)",
  "risk_score": "float (0.0-1.0)"
}
```

**Error Response (400/500):**
```json
{
  "detail": "string (error message)"
}
```

### GET /health

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Decision Logic

Claude evaluates applications using:

1. **Credit Score** — 750+ (excellent), 700-749 (good), 650-699 (fair), <650 (poor)
2. **Debt-to-Income Ratio** — <36% (good), 36-50% (acceptable), >50% (problematic)
3. **Employment History** — 2+ years preferred for stability
4. **Loan-to-Income Ratio** — <20% (preferred), 20-40% (acceptable), >40% (risky)

Interest rates range from **3.5% to 12.5%** based on risk profile.

## Running Tests Locally

### With Panner AI

```bash
# Terminal output (colored)
panner-ai run examples/loan-approval-agent/tests/suites/loan_approval.yaml \
  --reporter terminal

# With baseline tracking (regression detection)
panner-ai run examples/loan-approval-agent/tests/suites/loan_approval.yaml \
  --reporter terminal,json \
  --output results.json \
  --baseline-file baseline.json
```

### With pytest (direct Python testing)

```bash
# Test the agent module directly
pytest examples/loan-approval-agent/ -v
```

## Extending This Example

### Add More Test Cases

Edit `tests/suites/loan_approval.yaml`:

```yaml
  - name: edge_case_new_grad
    endpoint: "http://localhost:8000/apply"
    method: POST
    body:
      name: "Emma Lee"
      income: 50000
      credit_score: 680
      loan_amount: 8000
      employment_years: 0.5
      existing_debt: 0
    assertions:
      - type: status_code
        expected: 200
      - type: llm_judge
        prompt: "New graduate with entry-level job. Should decision reflect limited employment history?"
        min_score: 0.75
```

### Modify Decision Criteria

Edit the `evaluation_prompt` in `agent.py` to adjust:
- Credit score thresholds
- Interest rate ranges
- Risk assessment weights
- Debt-to-income limits

### Connect to Real Loan System

Extend `agent.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

@app.post("/apply")
def apply_for_loan(application: LoanApplication) -> LoanDecision:
    decision = evaluate_loan_application(application)
    
    # Persist to database
    db = get_db()
    application_record = ApplicationRecord(
        name=application.name,
        approved=decision.approved,
        interest_rate=decision.interest_rate
    )
    db.add(application_record)
    db.commit()
    
    return decision
```

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Claude API latency | ~1-2 seconds |
| Pydantic validation | <10ms |
| Full request-to-response | 1.5-2.5 seconds |
| Test suite (4 cases) | ~10 seconds |

## Troubleshooting

**Error: "ANTHROPIC_API_KEY not found"**
```bash
export ANTHROPIC_API_KEY="your-key"
python agent.py
```

**Error: "Connection refused" to localhost:8000**
- Ensure agent is running: `python agent.py`
- Check port 8000 is available: `lsof -i :8000`

**Error: "Invalid response format from LLM evaluation"**
- Claude response parsing failed (rare)
- Check API key has correct permissions
- Review Claude API response format

**Tests failing but agent works locally**
- Verify `http://localhost:8000/apply` is accessible from test environment
- Check firewall rules
- Ensure ANTHROPIC_API_KEY is set in CI/CD environment

## Next Steps

1. **Run this example** — `python agent.py`, then test with cURL
2. **Run the test suite** — `panner-ai run examples/loan-approval-agent/tests/suites/loan_approval.yaml`
3. **Modify test cases** — Edit `tests/suites/loan_approval.yaml` for your use case
4. **Extend the agent** — Add database persistence, email notifications, etc.
5. **Create your own agent** — Use this as a template for other AI workflows

---

**Happy testing! 🎉**
