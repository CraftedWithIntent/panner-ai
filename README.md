# Panner AI

**Precision testing tool for AI agents with baseline tracking and LLM-powered evaluation.**

## What is Panner AI?

Panner AI is a test framework designed for AI systems that interact with APIs. It combines traditional HTTP testing (status codes, response times, JSON validation) with LLM-powered semantic correctness evaluation, baseline tracking, and multi-format reporting.

### Problem

Testing AI agents is hard. Traditional test assertions (status codes, latency) catch infrastructure failures. But they don't catch semantic regressions — when the agent's logic degrades subtly. Panner AI bridges this gap by treating LLM judges as first-class test evaluators.

## Quick Start

### Install

```bash
pip install panner-ai
```

### Run a test suite

```bash
panner-ai run tests/suites/smoke.yaml --reporter terminal
```

### With baseline tracking (regression detection)

```bash
panner-ai run tests/suites/regression.yaml \
  --reporter terminal,json \
  --output results.json \
  --baseline-file baseline.json
```

## Build Your First Agent

Panner AI shines when testing **AI agents** — services that use LLMs to make decisions. Here's a complete example:

### Example: Loan Approval Agent

A FastAPI service that uses Claude to evaluate loan applications:

**1. Create agent service (`agent.py`)**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from anthropic import Anthropic

app = FastAPI()
client = Anthropic()

class LoanApplication(BaseModel):
    name: str
    income: float
    credit_score: int
    loan_amount: float

class LoanDecision(BaseModel):
    approved: bool
    interest_rate: float
    reason: str
    risk_score: float

@app.post("/apply", response_model=LoanDecision)
def apply_for_loan(application: LoanApplication) -> LoanDecision:
    """Use Claude to evaluate and approve/deny loan."""
    prompt = f"""
    Evaluate this loan application:
    - Applicant: {application.name}
    - Income: ${application.income:,}
    - Credit Score: {application.credit_score}/850
    - Loan Amount: ${application.loan_amount:,}
    
    Return JSON: {{"approved": bool, "interest_rate": float, "reason": str, "risk_score": float}}
    """
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    decision_data = json.loads(message.content[0].text)
    return LoanDecision(**decision_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**2. Create test suite (`tests/suites/loan_approval.yaml`)**

```yaml
name: Loan Approval Test Suite
test_cases:
  - name: approve_strong_credit
    endpoint: "http://localhost:8000/apply"
    method: POST
    body:
      name: "Alice Johnson"
      income: 100000
      credit_score: 780
      loan_amount: 15000
    assertions:
      - type: status_code
        expected: 200
      - type: json_schema
        schema:
          type: object
          required: [approved, interest_rate, reason, risk_score]
          properties:
            approved: {type: boolean}
            interest_rate: {type: number, minimum: 3.5, maximum: 12.5}
            reason: {type: string}
            risk_score: {type: number, minimum: 0.0, maximum: 1.0}
      - type: llm_judge
        prompt: "Is this approval decision reasonable for an excellent-credit applicant?"
        min_score: 0.85

  - name: deny_poor_credit
    endpoint: "http://localhost:8000/apply"
    method: POST
    body:
      name: "Bob Davis"
      income: 45000
      credit_score: 620
      loan_amount: 25000
    assertions:
      - type: status_code
        expected: 200
      - type: llm_judge
        prompt: "Should this high-risk application be denied or approved with high interest?"
        min_score: 0.75
```

**3. Install and run**

```bash
# Install dependencies
pip install fastapi uvicorn anthropic pydantic

# Start agent (background)
python agent.py &

# Run test suite
panner-ai run tests/suites/loan_approval.yaml --reporter terminal

# Expected output
# ✅ approve_strong_credit (1.8s) — 3/3 assertions passed
# ✅ deny_poor_credit (1.9s) — 2/2 assertions passed
# Summary: 2 passed, 0 failed
```

**4. Add baseline tracking (regression detection)**

```bash
panner-ai run tests/suites/loan_approval.yaml \
  --reporter terminal,json \
  --output results.json \
  --baseline-file baseline.json

cat baseline.json
# {
#   "suite_name": "loan_approval",
#   "tests": [
#     {"name": "approve_strong_credit", "score": 0.95, "commit_sha": "a0ebd54", "timestamp": "2026-08-31T10:44:00Z"},
#     {"name": "deny_poor_credit", "score": 0.88, "commit_sha": "a0ebd54", "timestamp": "2026-08-31T10:44:00Z"}
#   ]
# }
```

### Full Working Example

A complete, production-ready agent example is in the **[examples/loan-approval-agent/](examples/loan-approval-agent/)** directory:

- ✅ Full `agent.py` with error handling, logging, and documentation
- ✅ `requirements.txt` with all dependencies
- ✅ Comprehensive test suite with 4 test cases
- ✅ Detailed `README.md` with setup, API reference, and troubleshooting

**Clone and run locally:**

```bash
cd examples/loan-approval-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-api-key-here"
python agent.py

# In another terminal
panner-ai run tests/suites/loan_approval.yaml --reporter terminal
```

See [examples/README.md](examples/README.md) for more agent examples and how to create your own.

## Features

- **Async HTTP testing** — Concurrent requests with semaphore control (default: 5 workers)
- **Pure evaluators** — Regex, latency, status code, JSON schema validation
- **LLM-as-Judge** — Semantic correctness via Claude/GPT-4 (vendor-agnostic LiteLLM)
- **Baseline tracking** — Regression detection (10% score drop threshold) with git versioning
- **Multi-format reports** — Terminal (ANSI colored), JUnit XML (CI integration), JSON (telemetry)
- **GitHub Actions integration** — Smoke + regression test pipeline, artifact upload
- **Zero code duplication** — Functional core + imperative shell architecture (ADR-001)

## Architecture

Panner AI uses a **Functional Core + Imperative Shell** pattern:

```
┌─ Config Parser (M1.1) ─────────────────────┐
│  YAML → Pydantic frozen models              │
└─────────────────────────────────────────────┘
                    ↓
┌─ HTTP Executor (M1.2) ────────────────────┐
│  Async dispatch, concurrency control        │
└─────────────────────────────────────────────┘
                    ↓
┌─ Evaluators (M1.3–M1.4) ──────────────────┐
│  Pure functions: regex, latency, LLM judge  │
└─────────────────────────────────────────────┘
                    ↓
┌─ Baseline Tracker (M1.5) ─────────────────┐
│  Regression detection, git versioning       │
└─────────────────────────────────────────────┘
                    ↓
┌─ Reporters (M1.6) ────────────────────────┐
│  Terminal, JUnit XML, JSON output           │
└─────────────────────────────────────────────┘
                    ↓
┌─ CLI & GitHub Actions (M1.7) ─────────────┐
│  Exit codes: 0 (pass), 1 (regression)      │
└─────────────────────────────────────────────┘
```

## Usage Examples

### Smoke Tests (Fast Baseline)

```yaml
name: Smoke Test Suite
test_cases:
  - name: health_check
    endpoint: "http://localhost:8000/health"
    method: GET
    assertions:
      - type: status_code
        expected: 200
      - type: latency
        max_ms: 500
```

### Regression Suite (Full CRUD)

```yaml
name: Regression Test Suite
test_cases:
  - name: create_item
    endpoint: "http://localhost:8000/api/items"
    method: POST
    body:
      name: "Test Item"
    assertions:
      - type: status_code
        expected: 201
      - type: json_schema
        schema:
          type: object
          properties:
            id:
              type: string

  - name: semantic_check
    endpoint: "http://localhost:8000/api/items/1/validate"
    method: POST
    assertions:
      - type: llm_judge
        prompt: "Is the response semantically correct for a validation endpoint?"
        min_score: 0.8
```

### Custom Evaluator

```yaml
test_cases:
  - name: custom_regex
    endpoint: "http://localhost:8000/api/status"
    method: GET
    assertions:
      - type: regex
        pattern: "status.*ok"
        flags: "i"
```

## CLI Reference

```
panner-ai run [OPTIONS] SUITE

Positional Arguments:
  SUITE                  Path to test suite YAML configuration file (default: suite.yaml)

Options:
  --reporter, -r FORMAT          Output format: terminal, junit, json, or comma-separated
                                 (default: terminal)
  --output, -o PATH              Output file path (for junit/json; ignored for terminal)
  --baseline-file, -b PATH       Path to baseline.json for regression detection
                                 (default: baseline.json)
  --help                         Show this message and exit

Examples:
  panner-ai run suite.yaml
  panner-ai run tests/suites/smoke.yaml --reporter terminal,json --output results.json
  panner-ai run tests/suites/regression.yaml --baseline-file baseline.json --reporter junit
```

## Configuration

Full YAML schema: [docs/domain/suite-schema.md](docs/domain/suite-schema.md)

### Assertion Types

- **status_code** — HTTP response code match
- **latency** — Response time threshold (max_ms)
- **json_schema** — Response body JSON schema validation
- **regex** — Response body regex pattern match
- **llm_judge** — Semantic correctness via Claude/GPT-4 (min_score 0.0–1.0)

### Evaluators

| Type | Input | Output | Notes |
|------|-------|--------|-------|
| status_code | response.status | pass/fail | Exact match |
| latency | response.elapsed | pass/fail | Max threshold |
| json_schema | response.json() | pass/fail | Pydantic validation |
| regex | response.text | pass/fail | With flags support |
| llm_judge | response.text + prompt | 0.0–1.0 | Vendor-agnostic (OpenAI/Anthropic) |

## Testing

### Run test suite locally

```bash
pytest tests/ -v --cov=src/panner-ai --cov-report=term-missing
```

### Coverage target

Minimum 80% (enforced by CI/CD)

### Add new evaluator

1. Implement pure function in `src/panner-ai/evaluators/`
2. Add test cases in `tests/test_evaluators.py`
3. Register in `src/panner-ai/core/pipeline.py`
4. Update CHANGELOG.md + docs/ARCHITECTURE.md

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Setup instructions
- Code style + linting rules
- PR workflow (max 5 files per PR)
- How to add new reporters, evaluators, assertion types

**Regression Tracking & Regression Detection**

Panner AI stores test scores in `baseline.json`:

```json
{
  "suite_name": "regression",
  "tests": [
    {
      "name": "semantic_check",
      "score": 0.95,
      "commit_sha": "a0ebd54",
      "timestamp": "2026-08-31T01:21:00Z"
    }
  ]
}
```

**Regression threshold:** Score drop > 10% (e.g., 0.95 → 0.85 = regression detected)

When regression is detected:
- Exit code: `1` (blocks PR merge in CI)
- Report includes delta and prior baseline
- Engineer reviews + updates baseline or fixes code

## GitHub Actions Integration

`.github/workflows/panner-ai.yml` provides:

- **Smoke tests** (2 fast checks, <1min) — gates regression tests
- **Regression tests** (8 comprehensive tests, ~5min) — full suite
- **Artifact upload** — 90-day retention for reports
- **PR checks** — JUnit XML parsed as GitHub test reporting

## Performance

- Smoke suite: <1 minute
- Regression suite: ~5 minutes
- Concurrency: 5 workers (configurable via semaphore)
- LLM evaluation: ~1-2 seconds per test (vendor dependent, cached in baseline)

## Licensing

MIT License — See [LICENSE](LICENSE)

## Support

- Issues: [GitHub Issues](https://github.com/CraftedWithIntent/panner-ai/issues)
- Discussions: [GitHub Discussions](https://github.com/CraftedWithIntent/panner-ai/discussions)
- Documentation: [docs/](docs/)

---

**Built for testing AI systems that care about correctness.**
