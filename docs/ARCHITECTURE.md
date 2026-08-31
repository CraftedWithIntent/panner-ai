# Panner AI Architecture

## Overview

Panner AI is built on **Functional Core + Imperative Shell** (ADR-001), separating pure business logic from side effects (I/O, CLI, HTTP).

### Principles

1. **Functional Core**: Evaluators are pure functions with no side effects
2. **Imperative Shell**: CLI, HTTP client, file I/O, error handling
3. **Immutability**: Pydantic frozen models ensure data integrity
4. **Zero Duplication**: Single canonical model for each domain concept
5. **Error Propagation**: Phase 1 — no exception handlers in core; CLI propagates via exit codes

---

## Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│ CLI (Typer) — M1.6, M1.7                                           │
│ ├─ Parse arguments (--config, --reporter, --baseline-file)         │
│ ├─ Dispatch to reporters (terminal, junit, json)                    │
│ └─ Propagate exit codes (0 = pass, 1 = regression/failure)         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────────┐
│ Test Executor (M1.2)                                               │
│ ├─ Async HTTP dispatch (httpx)                                     │
│ ├─ Concurrency control (semaphore, default 5 workers)              │
│ └─ Load baseline.json for regression tracking                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────────┐
│ Evaluators Pipeline (M1.3–M1.4)  [FUNCTIONAL CORE]                 │
│ ├─ evaluate_status_code() — HTTP status matching                   │
│ ├─ evaluate_latency() — Response time threshold                    │
│ ├─ evaluate_json_schema() — JSON schema validation                 │
│ ├─ evaluate_regex() — Pattern matching                             │
│ └─ evaluate_llm_judge() — Semantic scoring (LiteLLM)               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────────┐
│ Baseline Tracker (M1.5)                                            │
│ ├─ compare() — Detect regression (delta < -0.1)                    │
│ ├─ update() — Persist baseline.json                                │
│ └─ Git integration — Track commit SHA + timestamp                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────────┐
│ Reporters (M1.6) — Generate output formats                         │
│ ├─ TerminalReporter — ANSI colored (Rich)                          │
│ ├─ JUnitReporter — XML for GitHub Actions/Jenkins                  │
│ └─ JSONReporter — Telemetry export                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Config Parsing (M1.1)

**Input:** YAML file (suite.yaml)

```yaml
name: regression
test_cases:
  - name: health
    endpoint: http://localhost:8000/health
    method: GET
    assertions:
      - type: status_code
        expected: 200
```

**Process:** 
- `parse_suite()` loads YAML via PyYAML
- Pydantic validates schema → `SuiteConfig` frozen model
- Returns validated config or raises `ConfigError`

**Output:** `SuiteConfig(name="regression", test_cases=[...])`

### 2. Test Execution (M1.2)

**Input:** `SuiteConfig`, optional `baseline.json`

**Process:**
- `TestExecutor.run()` iterates test cases
- Async httpx dispatch with semaphore (5 workers max)
- For each response: call evaluators pipeline
- Collect results → `SuiteReport(test_reports=[], regression_detected=False)`

**Output:** `SuiteReport` with all test results

### 3. Evaluation (M1.3–M1.4)

**Input:** HTTP response + assertion specs

**Process:**
- For each assertion in test case:
  - Match assertion type → call evaluator function
  - Evaluators are pure: `(response, spec) → bool | float`
  - Collect results → `AssertionResult`
- Aggregate per test → `TestReport(name, passed, latency_ms, assertions=[])`

**Evaluators:**

| Type | Logic | Output |
|------|-------|--------|
| status_code | `response.status_code == expected` | bool |
| latency | `response.elapsed.total_seconds() * 1000 <= max_ms` | bool |
| json_schema | Pydantic model validates `response.json()` | bool |
| regex | `re.search(pattern, response.text, flags)` is not None | bool |
| llm_judge | LiteLLM call to Claude/GPT-4, parse JSON score | 0.0–1.0 |

### 4. Baseline Tracking (M1.5)

**Input:** Test results + `baseline.json` (if exists)

**Process:**
- `BaselineTracker.compare(suite_report, baseline_data)`
  - For each test: compare `current_score` vs `prior_score`
  - If `current < prior - 0.1` (10% drop) → regression detected
  - Set `suite_report.regression_detected = True`
- `BaselineTracker.update(suite_report, baseline_file)`
  - Persist scores to `baseline.json`
  - Include git SHA via `subprocess.run(["git", "rev-parse", "HEAD"])`
  - Add ISO 8601 UTC timestamp

**Output:** Updated `SuiteReport` with `regression_detected` flag

### 5. Reporting (M1.6)

**Input:** `SuiteReport`

**Process:**
- CLI parses `--reporter` argument (comma-separated list)
- For each reporter:
  - Instantiate with `ReporterConfig(output_path=...)`
  - Call `.report(suite_report)` → format-specific output

**Reporters:**

| Type | Output | Format |
|------|--------|--------|
| terminal | stdout | ANSI colored table (Rich) |
| junit | file: junit-results.xml (or --output) | JUnit XML (CI integration) |
| json | file: results.json (or --output) | Complete SuiteReport JSON |

**Example Terminal Output:**
```
Test Results for: regression
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name               Status   Latency   Assertions
─────────────────────────────────────────────────
health             ✓ PASS   15ms      1/1
create_item        ✓ PASS   42ms      2/2
semantic_check     ⚠ WARN   1200ms    1/1 (score: 0.85)
not_found          ✓ PASS   8ms       1/1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 4/4 passed | Latency avg: 266ms
Regression: NOT DETECTED
```

### 6. Exit Codes (M1.7)

**Logic:**
```python
if suite_report.regression_detected or suite_report.failed_count > 0:
    exit(1)  # Blocks PR merge in CI
else:
    exit(0)  # Allows merge
```

---

## Module Organization

### src/panner-ai/

```
config/
├── parser.py        # parse_suite() + validation
└── __init__.py

executor/
├── executor.py      # TestExecutor class (M1.2)
└── __init__.py

evaluators/
├── __init__.py      # Registry of all evaluators
├── status_code.py   # evaluate_status_code()
├── latency.py       # evaluate_latency()
├── json_schema.py   # evaluate_json_schema()
├── regex.py         # evaluate_regex()
└── llm_judge.py     # evaluate_llm_judge() (M1.4)

core/
├── pipeline.py      # Evaluator dispatch logic
└── __init__.py

baseline/
├── tracker.py       # BaselineTracker class (M1.5)
└── __init__.py

reporters/
├── base.py          # Abstract Reporter class (M1.6)
├── terminal.py      # TerminalReporter (Rich)
├── junit.py         # JUnitReporter (xml.etree)
├── json.py          # JSONReporter (json module)
└── __init__.py

domain/
├── types.py         # Shared domain models (AssertionType enum, etc.)
└── __init__.py

cli.py              # Typer CLI entry point (M1.6)
__init__.py         # Package exports
```

### tests/

```
test_parser.py          # M1.1 config parsing
test_executor.py        # M1.2 HTTP dispatch
test_evaluators.py      # M1.3 evaluators
test_llm_judge.py       # M1.4 LLM integration
test_baseline.py        # M1.5 baseline tracking
test_reporters.py       # M1.6 report generation
test_cli.py             # M1.6 CLI integration
suites/
├── smoke.yaml          # M1.7 fast tests
└── regression.yaml     # M1.7 full suite
```

---

## Key Design Decisions

### 1. Pydantic v2 Frozen Models

All domain models use `frozen=True` to prevent mutation:

```python
class SuiteConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    test_cases: list[TestCaseSpec]
```

**Why:** Immutability enables functional composition and reduces bugs.

### 2. Async HTTP Execution (asyncio + httpx)

```python
async def run(self) -> SuiteReport:
    async with httpx.AsyncClient() as client:
        tasks = [self._execute_test(client, tc) for tc in config.test_cases]
        reports = await asyncio.gather(*tasks)
    return SuiteReport(test_reports=reports, ...)
```

**Why:** Non-blocking I/O scales to many tests; semaphore prevents resource exhaustion.

### 3. LiteLLM Abstraction

```python
import litellm
response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
)
```

**Why:** Single integration point supports OpenAI, Anthropic, Cohere, etc. without vendor lock-in.

### 4. Baseline Tracking with Git SHA

```python
commit_sha = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    capture_output=True,
    text=True,
).stdout.strip()
```

**Why:** Historical baseline linked to commit enables trend analysis across refactors.

### 5. Reporter Pattern (Abstract Base)

```python
class Reporter(ABC):
    @abstractmethod
    def report(self, suite_report: SuiteReport) -> None:
        pass
```

**Why:** Extensible design; adding new format (HTML, Slack) requires only 1 new subclass.

### 6. Regression Threshold: -0.1 (10%)

```python
if current_score < prior_score - 0.1:
    regression_detected = True
```

**Why:** Phase 1 hardcoded threshold; Phase 2 makes configurable. Prevents flaky tests from blocking PRs while catching real regressions.

---

## Extension Points

### Adding a New Evaluator

1. **Create evaluator function** (`src/panner-ai/evaluators/my_check.py`):
   ```python
   def evaluate_my_check(response: httpx.Response, spec: AssertionSpec) -> bool | float:
       """Pure function, no side effects."""
       return True  # or score (0.0–1.0) for LLM-like evaluators
   ```

2. **Add to AssertionType enum** (`src/panner-ai/domain/types.py`):
   ```python
   class AssertionType(str, Enum):
       MY_CHECK = "my_check"
   ```

3. **Register in pipeline** (`src/panner-ai/core/pipeline.py`):
   ```python
   EVALUATORS = {
       AssertionType.MY_CHECK: evaluate_my_check,
       # ... others ...
   }
   ```

4. **Add tests** and update docs

### Adding a New Reporter

1. **Create reporter class** (inherit from `Reporter`):
   ```python
   class MyReporter(Reporter):
       def report(self, suite_report: SuiteReport) -> None:
           # Implement format-specific logic
           pass
   ```

2. **Export in CLI** (`src/panner-ai/cli.py`):
   ```python
   reporters_map = {
       "my_format": MyReporter,
       # ... others ...
   }
   ```

3. **Add tests** and usage example

---

## Performance Characteristics

| Component | Latency | Throughput |
|-----------|---------|------------|
| Config parsing | <10ms | N/A |
| HTTP dispatch (5 workers) | 5–1000ms | ~5 concurrent |
| Evaluators (per test) | 1–2000ms | Depends on evaluator type |
| LLM judge (per test) | 1000–3000ms | ~0.3–1 req/sec |
| Baseline I/O | <50ms | N/A |
| Report generation | <100ms | N/A |
| **Total (8 tests, no LLM)** | ~2–3 seconds | N/A |
| **Total (8 tests, with LLM)** | ~30–50 seconds | N/A |

---

## Future Extensions (Phase 2+)

- **Authentication:** OAuth2, API keys, mTLS support
- **Advanced reporting:** HTML, Markdown, Slack webhooks
- **Custom evaluators:** Plugin system for user-defined assertions
- **Load testing:** Configurable concurrency, ramp-up profiles
- **Report filtering:** Tag-based, environment-based test selection
- **Performance profiling:** Latency P50/P95/P99 tracking
- **Distributed testing:** Multiple runners, result aggregation

---

**For contribution guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md). For quickstart, see [README.md](../README.md).**
