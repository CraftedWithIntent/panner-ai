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

Assay follows **Functional Core + Imperative Shell** (ADR-001):

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

Assay uses **Ruff** for all style enforcement:

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

Assay uses semantic versioning: **MAJOR.MINOR.PATCH**

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

**Thank you for making Assay better!**
