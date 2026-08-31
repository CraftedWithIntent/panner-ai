# Panner AI Examples

This directory contains **complete, working examples** of AI agents tested with Panner AI.

Each example demonstrates:
- Full production-ready code
- Pydantic data validation
- LLM integration (Claude/GPT-4)
- Comprehensive test suites
- Performance benchmarks

## Quick Links

### Loan Approval Agent

**Directory:** `loan-approval-agent/`

A FastAPI service that uses Claude to evaluate loan applications and make approval decisions.

**Demonstrates:**
- HTTP endpoint design with FastAPI
- LLM-powered business logic (Claude)
- Pydantic request/response validation
- Test suite with schema, latency, and LLM judge assertions
- JSON Schema validation in Panner AI

**Quick Start:**
```bash
cd loan-approval-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
python agent.py

# In another terminal
panner-ai run tests/suites/loan_approval.yaml --reporter terminal
```

**Files:**
- `agent.py` — Full FastAPI service with Claude integration
- `requirements.txt` — Dependencies (FastAPI, Anthropic, Pydantic)
- `tests/suites/loan_approval.yaml` — 4 comprehensive test cases
- `README.md` — Detailed setup and usage guide

---

## Directory Structure

```
examples/
├── README.md                          # You are here
│
└── loan-approval-agent/               # First agent example
    ├── README.md                      # How to run this example
    ├── agent.py                       # Full FastAPI + Claude service
    ├── requirements.txt               # pip dependencies
    └── tests/
        └── suites/
            └── loan_approval.yaml     # Test suite (4 cases)
```

---

## Adding New Examples

### Step 1: Create Directory

```bash
mkdir -p examples/YOUR-AGENT-NAME/tests/suites
```

### Step 2: Implement Agent

Create `YOUR-AGENT-NAME/agent.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Your Agent")

class Input(BaseModel):
    """Agent input model."""
    name: str

class Output(BaseModel):
    """Agent output model."""
    result: str

@app.post("/process")
def process(input: Input) -> Output:
    """Process request using your logic."""
    return Output(result=f"Processed {input.name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 3: Create Test Suite

Create `YOUR-AGENT-NAME/tests/suites/test.yaml`:

```yaml
name: Your Agent Test Suite

test_cases:
  - name: basic_test
    endpoint: "http://localhost:8000/process"
    method: POST
    body:
      name: "test"
    assertions:
      - type: status_code
        expected: 200
      - type: json_schema
        schema:
          type: object
          properties:
            result:
              type: string
      - type: latency
        max_ms: 1000
```

### Step 4: Create requirements.txt

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
```

### Step 5: Add README.md

Create `YOUR-AGENT-NAME/README.md` with:
- What the agent does
- Quick start (install, run, test)
- API reference
- Test suite overview
- Troubleshooting

### Step 6: Update Examples Index

Add section to this `README.md`:

```markdown
### Your Agent Name

**Directory:** `your-agent-name/`

Brief description.

**Quick Start:**
```bash
cd your-agent-name
...
```
```

---

## Best Practices

### 1. Complete, Runnable Code

Every example should be:
- ✅ Executable without modifications
- ✅ Self-contained (no external dependencies beyond requirements.txt)
- ✅ Documented with docstrings and comments
- ✅ Tested with the Panner AI test suite

### 2. Realistic Scenarios

Choose use cases that:
- ✅ Demonstrate AI agent patterns
- ✅ Solve real business problems
- ✅ Show Claude/LLM value
- ✅ Are understandable to beginners

### 3. Test Coverage

Each example should include:
- ✅ Happy path test (successful request)
- ✅ Edge case tests (boundary conditions)
- ✅ Error handling tests (bad inputs)
- ✅ Performance tests (latency assertions)
- ✅ Semantic correctness tests (LLM judge)

### 4. Documentation

README.md must include:
- ✅ What the agent does (1-2 paragraphs)
- ✅ Architecture diagram (optional but recommended)
- ✅ Quick start (5 steps max)
- ✅ API reference (request/response models)
- ✅ Test suite overview (how many tests, what they cover)
- ✅ Troubleshooting (common errors)

---

## Test Assertion Types

Panner AI supports multiple assertion types. Use them to test different aspects:

| Type | Purpose | Example |
|------|---------|---------|
| **status_code** | HTTP response code | Check endpoint returns 200 |
| **latency** | Response time threshold | Ensure response < 1000ms |
| **json_schema** | Response structure | Validate response has required fields |
| **regex** | Text pattern matching | Check response contains expected text |
| **llm_judge** | Semantic correctness | Ask Claude "Is this response reasonable?" |

**Pro Tip:** Combine multiple assertions per test for comprehensive coverage.

---

## Running All Examples

### Run One Example

```bash
# Terminal output
panner-ai run examples/loan-approval-agent/tests/suites/loan_approval.yaml \
  --reporter terminal

# Save JSON results
panner-ai run examples/loan-approval-agent/tests/suites/loan_approval.yaml \
  --reporter json \
  --output results.json
```

### Run All Examples (CI/CD)

```bash
# Script to run all example test suites
for example in examples/*/; do
  suite="${example}tests/suites/$(ls ${example}tests/suites/ | head -1)"
  echo "Running $suite..."
  panner-ai run "$suite" --reporter terminal || exit 1
done
```

---

## Example Structure Checklist

When creating a new example, verify:

- [ ] Directory created: `examples/YOUR-AGENT/`
- [ ] `agent.py` implemented and documented
- [ ] `requirements.txt` with all dependencies
- [ ] `tests/suites/` directory with YAML test suite
- [ ] Test suite has 4+ test cases covering happy path, edge cases, errors
- [ ] `README.md` with setup, API reference, troubleshooting
- [ ] Tested locally: `python agent.py` + `panner-ai run tests/suites/...`
- [ ] All tests passing with baseline tracking

---

## Contributing Examples

To add a new example:

1. **Follow structure** — Use loan-approval-agent as template
2. **Test thoroughly** — Run locally before committing
3. **Document clearly** — README.md must be complete
4. **Keep it focused** — One agent pattern per example
5. **Submit PR** — Include all files, tests passing

See [CONTRIBUTING.md](../CONTRIBUTING.md#examples) for full details.

---

## Performance Benchmarks

| Example | Avg Response Time | Test Suite Time | LLM Calls |
|---------|-------------------|-----------------|-----------|
| Loan Approval | 1.5-2.5s | ~10s (4 tests) | 4 per run |

---

## Troubleshooting

**"Connection refused" to localhost:8000**
```bash
# Make sure agent is running
python examples/YOUR-AGENT/agent.py
```

**"ModuleNotFoundError"**
```bash
# Install dependencies
pip install -r examples/YOUR-AGENT/requirements.txt
```

**"ANTHROPIC_API_KEY not found"**
```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"
```

**Tests failing but agent works locally**
- Check endpoint URL in YAML matches running service
- Verify firewall allows connections
- Ensure API keys are set in test environment

---

## Support

- **Issues:** [GitHub Issues](https://github.com/CraftedWithIntent/panner-ai/issues)
- **Discussions:** [GitHub Discussions](https://github.com/CraftedWithIntent/panner-ai/discussions)
- **Docs:** [../../docs/](../../docs/)

---

**Happy building! 🚀**
