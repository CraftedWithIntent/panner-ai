# Contributing to Panner AI

Thank you for contributing! This guide explains how to develop, test, and submit changes to Panner AI.

## Setup

### Clone and install in dev mode

```bash
git clone https://github.com/CraftedWithIntent/panner-ai.git
cd panner-ai
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -e .[dev]
```

### Verify setup

```bash
pytest tests/ -v
python -m py_compile src/panner-ai/**/*.py
```

## Architecture

Panner AI follows **Functional Core + Imperative Shell** (ADR-001):

- **Functional Core**: Pure evaluators (regex, latency, JSON schema, LLM judge)
- **Imperative Shell**: CLI (Typer), HTTP executor (asyncio), reporters (file I/O)

### Code Organization

```
src/panner-ai/
├── config/           # M1.1: Config parsing (Pydantic models)
├── executor/         # M1.2: HTTP dispatcher (asyncio, semaphore)
├── evaluators/       # M1.3–M1.4: Pure evaluation functions
├── baseline/         # M1.5: Regression tracking, git versioning
├── reporters/        # M1.6: Terminal, JUnit XML, JSON output
├── cli.py            # M1.7: Typer CLI entry point
└── domain/           # Shared types (assertion specs, enums)

tests/
├── test_parser.py
├── test_executor.py
├── test_evaluators.py
├── test_llm_judge.py
├── test_baseline.py
├── test_reporters.py
├── test_cli.py
└── suites/           # M1.7: YAML test configurations (smoke, regression)
```

## Code Style

### Linting & Formatting

Panner AI uses **Ruff** for all style enforcement:

```bash
ruff check src tests         # Check only
ruff check --fix src tests   # Auto-fix
```

### Ruff Configuration

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
extend-ignore = [
  "BLE001",  # Blind exception catches (Phase 1: CLI error propagation via exit codes)
  "UP017",   # datetime.UTC not available in Python 3.11 (project minimum is 3.11+)
]
```

### Type Hints

- All functions must have parameter + return type hints
- Use `from typing import ...` for generic types
- Frozen Pydantic models for immutability: `class MyModel(BaseModel): model_config = ConfigDict(frozen=True)`

### Imports

- Group: stdlib, third-party, local (in that order)
- Alphabetical within each group
- Ruff auto-sorts on `--fix`

### Docstrings

- Use triple-quoted docstrings for all public functions, classes, modules
- Format: Google-style (Args, Returns, Raises, Example)
- Required for: CLI commands, evaluators, reporters, public APIs

## Testing

### Run tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_parser.py -v

# With coverage
pytest tests/ --cov=src/panner-ai --cov-report=term-missing

# With markers
pytest tests/ -m "not slow" -v
```

### Coverage Requirements

- Minimum: **80%**
- Target: **90%+**
- Enforced by CI/CD

### Writing Tests

**Test file naming:** `test_<module>.py`

**Mocking external services:**
```python
from unittest.mock import patch, MagicMock
import pytest

@patch("panner-ai.evaluators.llm_judge.litellm.completion")
def test_llm_judge_mocked(mock_llm):
    mock_llm.return_value = {"choices": [{"message": {"content": '{"score": 0.9}'}}]}
    # Test assertion
```

**Fixtures:**
```python
@pytest.fixture
def sample_suite_config():
    return SuiteConfig(
        name="test",
        test_cases=[
            TestCaseSpec(
                name="health",
                endpoint="http://localhost:8000/health",
                method="GET",
                assertions=[AssertionSpec(type=AssertionType.STATUS_CODE, expected=200)],
            )
        ],
    )
```

### Adding New Evaluators

1. **Create evaluator function** in `src/panner-ai/evaluators/<name>.py`:
   ```python
   def evaluate_my_check(response: httpx.Response, config: AssertionSpec) -> bool:
       """Evaluate custom assertion."""
       # Pure function, no side effects
       return True  # or False
   ```

2. **Register in pipeline** (`src/panner-ai/core/pipeline.py`):
   ```python
   EVALUATORS = {
       AssertionType.STATUS_CODE: evaluate_status_code,
       # ... existing evaluators ...
       AssertionType.MY_CHECK: evaluate_my_check,
   }
   ```

3. **Add test** in `tests/test_evaluators.py`:
   ```python
   def test_my_check_success():
       response = MagicMock(spec=httpx.Response)
       # Set up response mock
       result = evaluate_my_check(response, AssertionSpec(...))
       assert result is True
   ```

4. **Update docs**:
   - Add to README.md assertion types table
   - Update docs/domain/suite-schema.md
   - Add example YAML in tests/suites/

## PR Workflow

### Before You Start

1. **Check for open PRs:** `gh pr list --state open`
2. **Verify main clean:** `git log main --oneline | head -1`
3. **Search codebase** for existing implementations (zero duplication policy):
   ```bash
   rg "def evaluate_" src/panner-ai/evaluators/
   find src/panner-ai -name "*.py" -exec grep -l "class.*Reporter" {} +
   ```
4. **Update issue label:** `status:backlog` → `status:in-progress` (if applicable)
5. **Create feature branch:** `git checkout -b feature/ISSUE-description`

## Examples

Panner AI examples live in `examples/` and demonstrate **complete, production-ready AI agents**.

### Why Examples Matter

Examples are the best way for users to:
- ✅ Learn how to build AI agents
- ✅ See Panner AI in action
- ✅ Copy-paste working code
- ✅ Understand testing patterns

### Example Structure

Each example follows this structure:

```
examples/
├── README.md                          # Index of all examples
│
└── YOUR-AGENT-NAME/
    ├── README.md                      # Setup, API reference, troubleshooting
    ├── agent.py                       # Full agent implementation (production-ready)
    ├── requirements.txt               # Dependencies
    └── tests/
        └── suites/
            └── test_suite.yaml        # 4+ test cases (happy path, edge cases, errors)
```

### Adding a New Example

**Step 1: Create directory structure**

```bash
mkdir -p examples/YOUR-AGENT-NAME/tests/suites
```

**Step 2: Implement agent (`agent.py`)**

Requirements:
- ✅ Use FastAPI or another HTTP framework
- ✅ Include LLM integration (Claude, GPT-4, etc. via LiteLLM)
- ✅ Use Pydantic for request/response validation
- ✅ Include comprehensive docstrings
- ✅ Handle errors gracefully
- ✅ Runnable with `python agent.py` (no CLI args)
- ✅ ~200-400 lines including comments

Example template:

```python
"""Your Agent — Brief description."""

import logging
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Your Agent")
logger = logging.getLogger(__name__)

class Input(BaseModel):
    """Agent input model."""
    name: str

class Output(BaseModel):
    """Agent output model."""
    result: str

@app.post("/process", response_model=Output)
def process(input: Input) -> Output:
    """Process request using LLM reasoning."""
    # Your LLM logic here
    return Output(result=f"Processed {input.name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Step 3: Create test suite (`tests/suites/test_suite.yaml`)**

Requirements:
- ✅ 4+ test cases (happy path, edge cases, errors, performance)
- ✅ Mix of assertion types (status_code, json_schema, latency, llm_judge)
- ✅ Realistic request data
- ✅ Clear test names and descriptions

Example structure:

```yaml
name: Your Agent Test Suite
description: Comprehensive test suite

test_cases:
  - name: happy_path_test
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
          required: [result]
          properties:
            result: {type: string}
      - type: latency
        max_ms: 2000
      - type: llm_judge
        prompt: "Is this response reasonable?"
        min_score: 0.8

  - name: edge_case_test
    # ...

  - name: error_handling_test
    # ...

  - name: performance_test
    # ...
```

**Step 4: Create `requirements.txt`**

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
anthropric==0.7.1
requests==2.31.0
```

**Step 5: Create detailed `README.md`**

Must include:

- 📝 **What It Does** — 1-2 paragraphs explaining the agent
- 🏗️ **Architecture** — Diagram or text description
- 🚀 **Quick Start** — Install, run, test (5 steps max)
- 📡 **API Reference** — Request/response models with examples
- 🧪 **Test Suite Overview** — What each test case covers
- 🔧 **Troubleshooting** — Common errors and solutions
- ➡️ **Next Steps** — How to extend or modify the example

See [examples/loan-approval-agent/README.md](examples/loan-approval-agent/README.md) for a complete template.

**Step 6: Test locally**

```bash
cd examples/YOUR-AGENT-NAME

# Install deps
pip install -r requirements.txt

# Run agent
python agent.py

# In another terminal, run tests
panner-ai run tests/suites/test_suite.yaml --reporter terminal

# All tests should pass ✅
```

**Step 7: Update examples index**

Edit [examples/README.md](examples/README.md) to add your example in the "Quick Links" section:

```markdown
### Your Agent Name

**Directory:** `your-agent-name/`

Brief description of what it does.

**Quick Start:**
```bash
cd your-agent-name
pip install -r requirements.txt
python agent.py
panner-ai run tests/suites/test_suite.yaml
```
```

**Step 8: Submit PR**

```bash
git add examples/YOUR-AGENT-NAME/
git add examples/README.md
git commit -m "feat: Add YOUR-AGENT-NAME example"
gh pr create --title "feat: Add YOUR-AGENT-NAME example"
```

### Example Quality Checklist

Before submitting an example, verify:

- [ ] `agent.py` is complete and production-ready (no TODOs)
- [ ] `agent.py` uses LLM (Claude, GPT-4, etc.)
- [ ] `agent.py` has comprehensive docstrings
- [ ] `agent.py` handles errors and logs properly
- [ ] `requirements.txt` lists all dependencies with pinned versions
- [ ] `tests/suites/test_suite.yaml` has 4+ test cases
- [ ] Test cases cover happy path, edge cases, errors, and performance
- [ ] Test assertions use multiple types (status_code, json_schema, latency, llm_judge)
- [ ] `README.md` has all required sections
- [ ] `README.md` includes working Quick Start instructions
- [ ] API reference shows all request/response fields
- [ ] All tests pass when running locally
- [ ] Agent runs with `python agent.py` (no CLI args)
- [ ] Example is realistic and solves a real problem
- [ ] Code follows Ruff style guidelines (`ruff check --fix`)
- [ ] Example is added to [examples/README.md](examples/README.md)

### Example Ideas

Looking for example ideas? Consider:

- **Document Processing** — Extract entities from PDFs/images using Claude vision
- **Code Review Bot** — Use Claude to analyze and review code PRs
- **Customer Support Classifier** — Route support tickets to teams using LLM reasoning
- **Content Moderation** — Check user-generated content for violations
- **Multi-step Workflow** — Agent that breaks down complex tasks into steps
- **Real-time Chat** — WebSocket endpoint that streams Claude responses
- **Data Validation** — Semantic validation (e.g., "Does this bio sound realistic?")
- **Test Data Generator** — Create realistic test data using an LLM

### During Development

- Keep scope small: **Max 5 files per PR** (excludes lockfiles, .sln, .csproj, generated files)
- Build frequently: `dotnet build FlowLedger.sln /p:TreatWarningsAsErrors=true` (or Python equivalent)
- Run tests: `pytest tests/ --cov=src/panner-ai`
- Update CHANGELOG.md with your changes

### Submitting PR

1. **Commit message format:**
   ```
   feat: Brief description (M1.X: Component if applicable)

   Longer explanation of what changed and why.
   Include test coverage summary.
   Fixes #ISSUE_NUMBER.
   ```

2. **Create PR via CLI:**
   ```bash
   git push origin feature/ISSUE-description
   gh pr create --title "feat: M1.X: Brief description" \
     --body "Detailed description, testing notes, architecture decisions"
   ```

3. **Wait for CI:** All checks must pass (ruff, pytest, type checking)

4. **Address feedback:** Push fixes to same branch (auto-updates PR)

5. **Merge:** Author squashes + merges (never fast-forward)
   ```bash
   gh pr merge <PR_NUMBER> --squash
   ```

6. **Delete branch** after merge:
   ```bash
   git branch -d feature/ISSUE-description
   git push origin --delete feature/ISSUE-description
   ```

## Release Process

### Version Bumping

Panner AI uses semantic versioning: **MAJOR.MINOR.PATCH**

- **MAJOR:** Breaking API changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes

### Release Checklist

1. **Update version** in `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"
   ```

2. **Update CHANGELOG.md** with release notes

3. **Tag commit:**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

4. **Build and publish to PyPI:**
   ```bash
   pip install build twine
   python -m build
   twine upload dist/panner-ai-0.2.0-py3-none-any.whl
   ```

## Troubleshooting

### "SyntaxError: unexpected character after line continuation character"

**Cause:** Literal `\n` escape sequence in exception handlers (tool escaping issue)

**Fix:** Use Python string methods to avoid escape sequences:
```python
# DO NOT: write literal \n
# DO: Use chr() or f-strings
code = "except Exception as e:" + chr(10) + "    pass"
```

### "ruff: BLE001 Do not catch blind exception"

**Rationale:** Phase 1 design uses broad exception handlers for CLI error propagation. Suppressed in config.

**If adding new exception handler:** Document why in code comment.

### Test failures on Python 3.12+

**Check:** `datetime.UTC` vs. `datetime.timezone.utc` compatibility

**Solution:** Use version-aware import:
```python
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc
```

## Questions?

- Open a GitHub Issue: [Issues](https://github.com/CraftedWithIntent/panner-ai/issues)
- Start a Discussion: [Discussions](https://github.com/CraftedWithIntent/panner-ai/discussions)
- Review architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

**Thank you for making Panner AI better!**
