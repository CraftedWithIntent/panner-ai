# Panner AI: Precision Testing for AI Agents

![License](https://img.shields.io/badge/License-MIT-blue) ![Python](https://img.shields.io/badge/Python-3.11%2B-blue)

**Test framework for AI agents. Combines HTTP testing (status codes, JSON validation) with LLM-powered semantic evaluation, baseline tracking, and regression detection.**

## The Problem

Testing AI agents is hard. Traditional assertions (status codes, latency) catch infrastructure failures. But they don't catch **semantic regressions** — when the agent's logic degrades subtly.

Panner AI bridges this gap by treating LLM judges (Claude, GPT-4) as first-class test evaluators.

## The Solution

```yaml
# Define test cases with semantic assertions
- name: approve_strong_credit
  endpoint: "http://localhost:8000/apply"
  method: POST
  body:
    name: "Alice"
    income: 100000
    credit_score: 780
  assertions:
    - type: status_code
      expected: 200
    - type: json_schema
      schema: { ... }
    - type: llm_judge  # ← LLM evaluates semantic correctness
      prompt: "Is this approval decision reasonable?"
      min_score: 0.85
```

Run:
```bash
panner-ai run tests/suites/loan_approval.yaml --reporter terminal --baseline-file baseline.json
```

Output:
```
✅ approve_strong_credit (1.8s) — 3/3 assertions passed
✅ deny_poor_credit (1.9s) — 2/2 assertions passed
Summary: 2 passed, 0 failed
```

## Installation

```bash
pip install panner-ai
```

## Quick Start

### 1. Create a test suite (YAML)

```yaml
name: Loan Approval Tests
test_cases:
  - name: approve_good_credit
    endpoint: "http://localhost:8000/apply"
    method: POST
    body:
      name: "Alice"
      income: 100000
      credit_score: 780
      loan_amount: 15000
    assertions:
      - type: status_code
        expected: 200
      - type: llm_judge
        prompt: "Is this a reasonable approval?"
        min_score: 0.85
```

### 2. Run tests

```bash
panner-ai run tests/loan_approval.yaml --reporter terminal
```

### 3. Track regressions

```bash
panner-ai run tests/loan_approval.yaml \
  --reporter terminal,json \
  --output results.json \
  --baseline-file baseline.json
```

## Key Features

| Feature | Details |
|---------|---------|
| **Async HTTP Testing** | Concurrent requests (5 workers by default) |
| **Assertion Types** | Status code, latency, JSON schema, regex, LLM judge |
| **LLM-as-Judge** | Semantic correctness via Claude/GPT-4 |
| **Baseline Tracking** | Regression detection (10% score drop threshold) |
| **Multi-format Reports** | Terminal, JUnit XML (CI), JSON (telemetry) |
| **GitHub Actions** | Built-in CI/CD integration |

## Assertion Types

- **status_code** — HTTP response code validation
- **latency** — Response time threshold (max_ms)
- **json_schema** — Response body schema validation
- **regex** — Pattern matching on response body
- **llm_judge** — Semantic correctness (0.0–1.0 score)

## Configuration

```bash
panner-ai run [OPTIONS] SUITE

Options:
  --reporter, -r       Output format (terminal, junit, json)
  --output, -o         Output file path
  --baseline-file, -b  Path to baseline.json for regression detection
  --help               Show help
```

## Regression Detection

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

**Regression threshold:** Score drop > 10% blocks PR merge in CI.

## Architecture

**Functional Core + Imperative Shell:**
- Pure evaluators (regex, latency, LLM judge)
- Immutable domain types
- Async HTTP executor with concurrency control
- Storage-agnostic baseline tracking

## Examples

Complete, production-ready examples in the repository:

- **[examples/loan-approval-agent/](https://github.com/CraftedWithIntent/panner-ai/tree/main/examples)** — Full FastAPI agent with test suite
  - 300+ lines of production code
  - Comprehensive test suite (4+ test cases)
  - Detailed setup and API reference

Run locally:
```bash
cd examples/loan-approval-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY="***"
python agent.py
panner-ai run tests/suites/loan_approval.yaml --reporter terminal
```

## Performance

- Smoke tests: <1 minute
- Regression suite: ~5 minutes
- Concurrency: 5 workers (configurable)
- LLM evaluation: ~1-2 seconds per test (vendor dependent)

## Testing

```bash
pytest tests/ -v --cov=src/panner_ai --cov-report=term-missing
```

Minimum coverage: 80% (enforced by CI/CD)

## GitHub Actions

Built-in CI/CD integration with:
- Smoke tests (2 fast checks, <1min)
- Regression tests (8 comprehensive tests, ~5min)
- Artifact upload (90-day retention)
- PR checks with JUnit XML parsing

## Documentation

- **[Full README](https://github.com/CraftedWithIntent/panner-ai)** — Comprehensive guide
- **[CONTRIBUTING.md](https://github.com/CraftedWithIntent/panner-ai/blob/main/CONTRIBUTING.md)** — Development setup, contribution ideas
- **[Suite Schema](https://github.com/CraftedWithIntent/panner-ai/blob/main/docs/domain/suite-schema.md)** — Full YAML schema
- **[Contribution Ideas](https://github.com/CraftedWithIntent/panner-ai/blob/main/docs/CONTRIBUTION_IDEAS.md)** — 25+ ideas by difficulty level
- **[Examples](https://github.com/CraftedWithIntent/panner-ai/tree/main/examples)** — Production-ready agent examples

## Contributing

We welcome contributions! See [CONTRIBUTING.md](https://github.com/CraftedWithIntent/panner-ai/blob/main/CONTRIBUTING.md) for:
- Setup instructions
- Code standards (Ruff linting, 80%+ coverage)
- PR workflow
- Contribution ideas (🟢 easy to 🔴 hard)

**All skill levels welcome.** Good first issues labeled [#good-first-issue](https://github.com/CraftedWithIntent/panner-ai/labels/good%20first%20issue).

## Support

- 🐛 [GitHub Issues](https://github.com/CraftedWithIntent/panner-ai/issues) — Bug reports, feature requests
- 💬 [GitHub Discussions](https://github.com/CraftedWithIntent/panner-ai/discussions) — Questions, ideas
- 📖 [Full Repository](https://github.com/CraftedWithIntent/panner-ai) — Source, examples, docs

## License

MIT License — See [LICENSE](https://github.com/CraftedWithIntent/panner-ai/blob/main/LICENSE) for details.

---

**Completely standalone:** Works with any HTTP API and LLM provider. Part of the [CraftedWithIntent](https://github.com/CraftedWithIntent) ecosystem for production AI systems.
