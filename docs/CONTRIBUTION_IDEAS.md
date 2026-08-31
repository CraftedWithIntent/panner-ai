# Contribution Ideas for Panner AI

Welcome! This document outlines **20+ contribution opportunities** for Panner AI, organized by difficulty level with impact analysis and implementation guidance.

## How to Use This Guide

1. **Pick an idea** that interests you (🟢 Easy → 🟡 Medium → 🔴 Hard)
2. **Review acceptance criteria** to understand the scope
3. **Check implementation hints** for where to start
4. **Open a GitHub issue** (we'll have pre-created ones for top 10 easy/medium ideas)
5. **Discuss in the issue** before coding (5 minutes to align)
6. **Submit a PR** (max 5 files per PR)
7. **Get feedback** and iterate

---

## 🟢 Easy Issues (Good First Contributions)

These are perfect entry points — no deep system knowledge required. Estimated effort: **0.5–2 hours**.

### 1. Add `header_check` Evaluator

**Description:** Add a new assertion type to validate HTTP response headers (e.g., `Content-Type: application/json`, `Authorization` presence).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (headers are critical for API contracts)
- ⚙️ **Effort:** 0.5 hours
- **Value:** Tests can now verify CORS, security headers, content type negotiation

**Acceptance Criteria:**
- [ ] New evaluator function `evaluate_header_check()` in `src/panner-ai/evaluators/headers.py`
- [ ] Assertion type `AssertionType.HEADER_CHECK` added to domain
- [ ] YAML schema updated in `docs/domain/suite-schema.md`
- [ ] Test suite in `tests/test_evaluators.py` (3+ test cases)
- [ ] Example YAML in `tests/suites/`
- [ ] README.md updated with header_check documentation
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In src/panner-ai/evaluators/headers.py
def evaluate_header_check(response: httpx.Response, config: AssertionSpec) -> bool:
    """Check if headers match expected values or patterns."""
    header_name = config.header_name  # e.g., "Content-Type"
    expected_value = config.expected_value  # e.g., "application/json"
    # Return True if header matches, False otherwise
```

**Why It Matters:**
- API contracts depend on headers (Content-Type, Authorization, etc.)
- Users testing multi-language clients need header validation
- Enables security header verification (X-Frame-Options, X-Content-Type-Options)

**Related GitHub Issue:** `#good-first-issue-header-check`

---

### 2. Add Retry Logic to HTTP Executor

**Description:** Implement exponential backoff + retry logic for transient failures (5xx, timeouts). Allow users to configure max_retries and retry_delay_ms in YAML.

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (flaky network tests are a major pain point)
- ⚙️ **Effort:** 1 hour
- **Value:** CI pipelines fail less often due to transient errors

**Acceptance Criteria:**
- [ ] Retry mechanism in `src/panner-ai/executor/http_executor.py`
- [ ] Config fields: `max_retries` (default 3), `retry_delay_ms` (default 100)
- [ ] Exponential backoff: delay *= 2 on each retry
- [ ] YAML schema updated (`docs/domain/suite-schema.md`)
- [ ] Example YAML in `tests/suites/`
- [ ] Tests verify retry on 503, timeout, connection error
- [ ] Tests verify no retry on 4xx
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In src/panner-ai/executor/http_executor.py
async def execute_with_retries(
    client: httpx.AsyncClient,
    request: TestCaseRequest,
    max_retries: int = 3,
    retry_delay_ms: int = 100,
) -> httpx.Response:
    """Execute HTTP request with exponential backoff retry."""
    for attempt in range(max_retries + 1):
        try:
            return await client.request(...)
        except (httpx.TimeoutException, ServerError):
            if attempt < max_retries:
                await asyncio.sleep(retry_delay_ms / 1000 * (2 ** attempt))
            else:
                raise
```

**Why It Matters:**
- Tests fail intermittently on network hiccups (noise in CI)
- Users write duplicate retry logic in their agents
- Panner AI can handle this centrally

**Related GitHub Issue:** `#good-first-issue-retry-logic`

---

### 3. Add XML Schema Validation Evaluator

**Description:** New assertion type for validating XML response bodies (DTD or XSD schema validation).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (SOAP/XML APIs still exist in enterprise)
- ⚙️ **Effort:** 1 hour
- **Value:** Panner AI supports legacy/enterprise systems

**Acceptance Criteria:**
- [ ] New evaluator `evaluate_xml_schema()` in `src/panner-ai/evaluators/xml.py`
- [ ] Assertion type `AssertionType.XML_SCHEMA` added
- [ ] Support inline XSD and external XSD via URL
- [ ] YAML schema updated
- [ ] 4+ test cases (valid XML, invalid, malformed, missing elements)
- [ ] Example YAML in `tests/suites/`
- [ ] README.md updated
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In src/panner-ai/evaluators/xml.py
from lxml import etree

def evaluate_xml_schema(response: httpx.Response, config: AssertionSpec) -> bool:
    """Validate XML response against XSD schema."""
    xml_doc = etree.fromstring(response.content)
    xsd_doc = etree.XMLSchema(etree.fromstring(config.schema))
    return xsd_doc.validate(xml_doc)
```

**Why It Matters:**
- Enterprise APIs (SOAP, banking systems) return XML
- JSON-only tools miss entire market segment
- Users testing XML-based agents need validation

**Related GitHub Issue:** `#good-first-issue-xml-schema`

---

### 4. Add HTML Report Generator

**Description:** New reporter that generates a beautiful HTML dashboard of test results (status, timing, assertion details, charts).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (visibility for non-technical stakeholders)
- ⚙️ **Effort:** 1.5 hours
- **Value:** Managers can review test results visually

**Acceptance Criteria:**
- [ ] New reporter class in `src/panner-ai/reporters/html.py`
- [ ] HTML template with CSS (inline styles, no external dependencies)
- [ ] Shows: test name, status (pass/fail), timing, assertion results
- [ ] Include summary chart: X pass/Y fail/Z skipped
- [ ] Responsive design (mobile-friendly)
- [ ] CLI option: `--reporter html` with output file
- [ ] Tests verify HTML structure and content
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In src/panner-ai/reporters/html.py
def generate_html_report(results: List[TestResult]) -> str:
    """Generate HTML report from test results."""
    html = """
    <html>
    <head>
        <title>Panner AI Test Report</title>
        <style>/* Inline CSS */</style>
    </head>
    <body>
        <!-- Summary stats -->
        <!-- Test results table -->
    </body>
    </html>
    """
    return html
```

**Why It Matters:**
- Terminal output hard to share with PMs/product
- HTML reports integrate with CI/CD dashboards
- Visual representation helps identify patterns

**Related GitHub Issue:** `#good-first-issue-html-report`

---

### 5. Add Slack Integration for Test Results

**Description:** New reporter that posts test results to Slack (channel, thread, with emojis and formatting).

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (team visibility in real-time)
- ⚙️ **Effort:** 1.5 hours
- **Value:** Engineers stay informed without leaving Slack

**Acceptance Criteria:**
- [ ] New reporter in `src/panner-ai/reporters/slack.py`
- [ ] Reads `SLACK_WEBHOOK_URL` env var
- [ ] Formats message: "✅ 8 passed, ❌ 2 failed, ⏱️ 12.3s"
- [ ] Posts to Slack channel via incoming webhook
- [ ] Includes test details (expandable thread)
- [ ] Config: `--reporter slack` with webhook URL option
- [ ] Tests mock Slack API calls
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In src/panner-ai/reporters/slack.py
import httpx

def post_to_slack(webhook_url: str, results: List[TestResult]) -> None:
    """Post test results to Slack channel."""
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    
    message = {
        "text": f"✅ {passed} passed, ❌ {failed} failed",
        "blocks": [/* Message blocks */]
    }
    
    httpx.post(webhook_url, json=message)
```

**Why It Matters:**
- Async agents run in CI; results often missed
- Slack notifications keep team in sync
- Helps catch regressions immediately

**Related GitHub Issue:** `#good-first-issue-slack-integration`

---

### 6. Add Performance Baseline Tracking

**Description:** Extend baseline.json to track response latency over time (not just LLM scores). Detect performance regressions (e.g., 100ms → 500ms).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (performance matters as much as correctness)
- ⚙️ **Effort:** 1 hour
- **Value:** Catch performance regressions early

**Acceptance Criteria:**
- [ ] Extend `src/panner-ai/baseline/tracker.py` to store latency metrics
- [ ] Add `latency_ms` field to baseline.json per test
- [ ] Detect regression: 50% latency increase (configurable threshold)
- [ ] Report: "Latency regression: was 100ms, now 500ms"
- [ ] Tests verify baseline comparisons
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# Update baseline.json structure:
{
  "suite_name": "regression",
  "tests": [
    {
      "name": "api_call",
      "latency_ms": 125,  # NEW
      "llm_score": 0.95,
      "commit_sha": "a0ebd54",
      "timestamp": "2026-08-31T10:44:00Z"
    }
  ]
}
```

**Why It Matters:**
- Performance regressions creep in slowly (hard to detect)
- Users want to know if agent got slower
- Baseline tracking already exists; extend it naturally

**Related GitHub Issue:** `#good-first-issue-perf-baseline`

---

### 7. Add Custom Environment Variable Support

**Description:** Allow YAML test configs to reference environment variables (e.g., `${API_KEY}`, `${BASE_URL}`).

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (secrets management is critical)
- ⚙️ **Effort:** 0.5 hours
- **Value:** Test suites work in CI without hardcoding secrets

**Acceptance Criteria:**
- [ ] Parser detects `${VAR_NAME}` in YAML
- [ ] Replaces with `os.getenv("VAR_NAME")`
- [ ] Fails gracefully if env var missing (clear error message)
- [ ] Works in: endpoint URL, body, headers, assertions
- [ ] Tests verify substitution and error handling
- [ ] Doc example in README.md or CONTRIBUTION_IDEAS.md
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In src/panner-ai/config/parser.py
import re
import os

def resolve_env_vars(value: str) -> str:
    """Replace ${VAR_NAME} with environment variable."""
    pattern = r'\$\{(\w+)\}'
    def replacer(match):
        var_name = match.group(1)
        env_value = os.getenv(var_name)
        if env_value is None:
            raise ValueError(f"Environment variable {var_name} not set")
        return env_value
    return re.sub(pattern, replacer, value)
```

**Why It Matters:**
- Tests need API keys, URLs that vary by environment
- Hardcoding secrets = security risk
- Users already expect this pattern

**Related GitHub Issue:** `#good-first-issue-env-vars`

---

### 8. Add Response Body Size Validation

**Description:** New assertion type to validate response body size (max/min bytes). Catches accidentally huge responses or empty payloads.

**Impact/Effort Matrix:**
- 🎯 **Impact:** Low (edge case but useful)
- ⚙️ **Effort:** 0.5 hours
- **Value:** Catch unexpected response bloat

**Acceptance Criteria:**
- [ ] New evaluator `evaluate_response_size()` in `src/panner-ai/evaluators/size.py`
- [ ] Assertion fields: `min_bytes`, `max_bytes` (optional)
- [ ] YAML schema updated
- [ ] 3+ test cases (under limit, over limit, exactly at limit)
- [ ] Example YAML in `tests/suites/`
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
def evaluate_response_size(response: httpx.Response, config: AssertionSpec) -> bool:
    """Check response body size within bounds."""
    size = len(response.content)
    if config.min_bytes and size < config.min_bytes:
        return False
    if config.max_bytes and size > config.max_bytes:
        return False
    return True
```

**Why It Matters:**
- Catch memory leaks (huge responses)
- Verify edge case handling (empty responses)
- Simple but practical

**Related GitHub Issue:** `#good-first-issue-response-size`

---

### 9. Add Test Case Name Filtering

**Description:** CLI flag `--filter` or `--test-name` to run only matching test cases (e.g., `panner-ai run suite.yaml --filter "smoke"` runs only tests with "smoke" in name).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (DX improvement for debugging)
- ⚙️ **Effort:** 1 hour
- **Value:** Faster iteration (don't run full suite every time)

**Acceptance Criteria:**
- [ ] CLI option `--filter` added to `src/panner-ai/cli.py`
- [ ] Filter logic in executor (skip non-matching tests)
- [ ] Supports regex patterns
- [ ] Tests verify filtering behavior
- [ ] CLI help text updated
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In src/panner-ai/cli.py
@app.command()
def run(
    suite_file: str,
    filter: str = typer.Option(None, help="Filter test cases by name (regex)")
):
    """Run test suite with optional name filtering."""
    # Parse suite
    # Filter test_cases by name
    # Execute filtered tests
```

**Why It Matters:**
- Running 100-test suite for 1 fix is slow
- Developers need fast feedback loop
- Industry standard feature

**Related GitHub Issue:** `#good-first-issue-test-filter`

---

### 10. Add Assertion Negation Support

**Description:** Allow negating assertions (e.g., "status_code should NOT be 500"). Add `negate: true` field to assertions.

**Impact/Effort Matrix:**
- 🎯 **Impact:** Low (edge case)
- ⚙️ **Effort:** 0.5 hours
- **Value:** Express negative constraints elegantly

**Acceptance Criteria:**
- [ ] Add `negate: bool` field to `AssertionSpec`
- [ ] Update all evaluators to check negate flag
- [ ] YAML schema updated
- [ ] 2+ test cases per evaluator (with/without negate)
- [ ] Example YAML in `tests/suites/`
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In evaluators, wrap result with negate check
def evaluate_status_code(response: httpx.Response, config: AssertionSpec) -> bool:
    result = response.status_code == config.expected
    return not result if config.negate else result
```

**Why It Matters:**
- Express "must NOT be 500" elegantly
- Avoid double-negative logic in YAML
- Reduces need for separate assertion types

**Related GitHub Issue:** `#good-first-issue-assertion-negation`

---

## 🟡 Medium Issues (Intermediate Contributors)

Estimated effort: **2–4 hours**. Requires understanding of Panner AI internals, but still manageable.

### 11. Add GraphQL Support

**Description:** New executor for GraphQL queries (not just HTTP REST). Support GraphQL schema validation and query verification.

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (GraphQL adoption increasing)
- ⚙️ **Effort:** 2 hours
- **Value:** Test GraphQL APIs as easily as REST

**Acceptance Criteria:**
- [ ] New executor in `src/panner-ai/executor/graphql_executor.py`
- [ ] Support: query, mutation, introspection
- [ ] YAML schema for GraphQL test cases
- [ ] Validate response against schema
- [ ] Example YAML in `tests/suites/`
- [ ] Tests verify query execution and response validation
- [ ] Documentation in README.md
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
- Use `gql` library for GraphQL queries
- Validate response against GraphQL schema
- Similar structure to HTTP executor but GraphQL-specific

**Why It Matters:**
- GraphQL is mainstream now (GitHub API, etc.)
- REST-only tools miss growing API landscape
- Users testing GraphQL agents need dedicated support

---

### 12. Add Custom Evaluator Plugin System

**Description:** Allow users to define custom evaluators in Python (loaded at runtime) without modifying Panner AI source.

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (flexibility for advanced users)
- ⚙️ **Effort:** 2 hours
- **Value:** Power users can extend without forking

**Acceptance Criteria:**
- [ ] Plugin loader in `src/panner-ai/core/plugins.py`
- [ ] Users define evaluator in `custom_evaluators.py`
- [ ] Plugin system loads evaluators at runtime
- [ ] YAML field: `type: custom:my_evaluator`
- [ ] Example plugin in `examples/`
- [ ] Tests verify plugin loading and execution
- [ ] Documentation in `docs/`
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
- Use `importlib` to dynamically load Python modules
- Convention: users put custom evaluators in `panner_plugins.py`
- Register evaluators in plugin registry

**Why It Matters:**
- Custom logic varies by organization
- Users shouldn't fork to add proprietary checks
- Plugin model is industry standard

---

### 13. Add Database Assertion Type

**Description:** New assertion: verify test results in a database query (e.g., "after POST /user, did it create a row in users table?").

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (integration testing is crucial)
- ⚙️ **Effort:** 2 hours
- **Value:** Test side effects, not just API responses

**Acceptance Criteria:**
- [ ] New evaluator `evaluate_database()` in `src/panner-ai/evaluators/database.py`
- [ ] Support: SQLite, PostgreSQL (via sqlalchemy or drivers)
- [ ] YAML fields: `database_url`, `query`, `expected_rows`
- [ ] Verify query returns expected number of rows or field values
- [ ] Example YAML in `tests/suites/`
- [ ] Tests use in-memory SQLite
- [ ] Documentation in README.md
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
def evaluate_database(response: httpx.Response, config: AssertionSpec) -> bool:
    """Query database and validate results."""
    import sqlalchemy
    engine = sqlalchemy.create_engine(config.database_url)
    result = engine.execute(config.query)
    rows = result.fetchall()
    return len(rows) == config.expected_rows
```

**Why It Matters:**
- API tests should verify persistence
- Catch lost writes and data corruption
- Integration testing is critical for AI agents

---

### 14. Add Multi-Step Workflow Support

**Description:** YAML syntax to run test cases in sequence with data passing (output from test A → input for test B).

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (complex workflows common in AI systems)
- ⚙️ **Effort:** 2.5 hours
- **Value:** Test multi-step agent workflows

**Acceptance Criteria:**
- [ ] YAML schema for workflow syntax (e.g., `depends_on: test_a`)
- [ ] Variable extraction from previous responses (e.g., `{{ test_a.response.id }}`)
- [ ] Sequential executor that respects dependencies
- [ ] Example workflow in `tests/suites/`
- [ ] Tests verify variable substitution and sequencing
- [ ] Documentation in docs/
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```yaml
# YAML example
test_cases:
  - name: create_user
    endpoint: "http://localhost:8000/users"
    method: POST
    body: {name: "Alice"}
    
  - name: get_user
    endpoint: "http://localhost:8000/users/{{ create_user.response.id }}"
    method: GET
    depends_on: [create_user]
```

**Why It Matters:**
- Real workflows: create → update → delete
- AI agents often have multi-step reasoning
- Currently no good way to test sequences

---

### 15. Add OpenAPI Spec Validation

**Description:** Validate test cases against OpenAPI/Swagger spec (ensure requests match schema, responses conform).

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (OpenAPI is standard in industry)
- ⚙️ **Effort:** 2 hours
- **Value:** Catch API contract violations early

**Acceptance Criteria:**
- [ ] Loader for OpenAPI spec (YAML/JSON)
- [ ] Validator in `src/panner-ai/evaluators/openapi.py`
- [ ] Verify: request conforms to spec, response matches schema
- [ ] YAML field: `openapi_spec_url` or inline spec
- [ ] CLI option: `--validate-openapi`
- [ ] Example YAML in `tests/suites/`
- [ ] Tests verify spec validation
- [ ] Documentation in README.md
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
- Use `openapi-spec-validator` package
- Validate request against spec parameters/bodies
- Validate response against spec response schemas

**Why It Matters:**
- OpenAPI is contract spec, not enforced by HTTP
- Users need confidence tests match published API
- Catches version mismatches early

---

### 16. Add Response Time Percentile Tracking

**Description:** Extend baseline to track latency percentiles (p50, p95, p99), not just averages. Detect tail latency regressions.

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (SLA compliance requires percentiles)
- ⚙️ **Effort:** 2 hours
- **Value:** Catch slow tail cases (p99 > SLA)

**Acceptance Criteria:**
- [ ] Extend baseline tracker to collect latency samples
- [ ] Calculate p50, p95, p99 across multiple runs
- [ ] Store in baseline.json
- [ ] Detect regression: p99 > threshold
- [ ] Report percentile breakdowns
- [ ] Tests verify percentile calculations
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
- Keep sliding window of latency samples
- Use `numpy.percentile` or manual sorting
- Report in baseline: `latency_percentiles: {p50: 100, p95: 250, p99: 500}`

**Why It Matters:**
- Average latency can hide tail issues
- SLAs are defined by p99, not p50
- Users care about worst-case performance

---

### 17. Add Retry-on-Assertion-Failure

**Description:** Allow test cases to retry if assertions fail (useful for eventual consistency testing).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (distributed systems need this)
- ⚙️ **Effort:** 1.5 hours
- **Value:** Test eventual consistency elegantly

**Acceptance Criteria:**
- [ ] YAML fields: `retry_on_failure`, `max_retries`, `retry_delay_ms`
- [ ] Retry executor logic that respects these fields
- [ ] Report: "Test passed on retry 2 of 3"
- [ ] Example YAML in `tests/suites/`
- [ ] Tests verify retry behavior on assertion failures
- [ ] Documentation in README.md
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```yaml
test_cases:
  - name: eventually_consistent_read
    endpoint: "http://localhost:8000/items/1"
    retry_on_failure:
      max_retries: 5
      retry_delay_ms: 500
```

**Why It Matters:**
- Distributed systems: write takes time to replicate
- Tests fail intermittently due to timing
- Elegant way to handle eventual consistency

---

### 18. Add Request/Response Logging to Baseline

**Description:** Store full request/response bodies in baseline for debugging (with compression to keep file size reasonable).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (debugging is painful without details)
- ⚙️ **Effort:** 1.5 hours
- **Value:** Easy root cause analysis of test failures

**Acceptance Criteria:**
- [ ] Extend baseline.json to include compressed request/response
- [ ] Use gzip compression to keep file size low
- [ ] Add flag: `--baseline-with-logs` (off by default)
- [ ] Provide CLI to extract/decompress logs
- [ ] Tests verify compression/decompression
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# In baseline tracker
import gzip
import base64

def compress_response(response_text: str) -> str:
    """Compress response for storage in baseline."""
    compressed = gzip.compress(response_text.encode())
    return base64.b64encode(compressed).decode()
```

**Why It Matters:**
- Baseline only stores scores; hard to debug failures
- Full request/response crucial for root cause analysis
- Compression keeps file size manageable

---

### 19. Add Concurrent Test Run Reporting

**Description:** Improve reporter output when tests run concurrently (avoid garbled terminal output, show progress bar).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Low (UX improvement)
- ⚙️ **Effort:** 2 hours
- **Value:** Better experience with large test suites

**Acceptance Criteria:**
- [ ] Progress bar in terminal reporter
- [ ] Thread-safe output buffer (no interleaved text)
- [ ] Show: tests running, completed, remaining
- [ ] Update in real-time as tests complete
- [ ] Tests verify output formatting
- [ ] Works with `--reporter terminal`
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
- Use `rich` library for progress bar
- Queue-based output to avoid race conditions
- Collect results, display at end if concurrent

**Why It Matters:**
- 100-test suite with 5 workers: output is garbled
- Progress bar gives confidence tests are running
- Professional polish

---

### 20. Add Cost Estimation for LLM Judge

**Description:** Track token usage + cost of LLM judge assertions. Display in report: "LLM cost: $0.15 for 100 tests".

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (cost is real concern for power users)
- ⚙️ **Effort:** 1.5 hours
- **Value:** Understand operational costs

**Acceptance Criteria:**
- [ ] LLM judge evaluator returns token counts
- [ ] Aggregate token counts in reporter
- [ ] Calculate cost using provider pricing (OpenAI, Anthropic)
- [ ] Display in report: "Tokens: 50,000 | Cost: $0.15"
- [ ] Tests verify token counting and cost calculation
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
# LLM judge returns
class LLMJudgeResult:
    score: float
    tokens_used: int
    cost_usd: float
```

**Why It Matters:**
- LLM calls add up quickly
- Users need to budget for testing
- Transparency builds trust

---

## 🔴 Hard Issues (Advanced Contributors)

Estimated effort: **4+ hours**. Requires deep knowledge of Panner AI architecture, async patterns, and/or complex algorithms.

### 21. Implement Bayesian Regression Detection

**Description:** Replace simple threshold-based regression detection (10% drop) with Bayesian model that accounts for variance and natural fluctuation.

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (fewer false positives)
- ⚙️ **Effort:** 4 hours
- **Value:** Confidence-based regression reporting

**Acceptance Criteria:**
- [ ] Bayesian model in `src/panner-ai/baseline/bayesian.py`
- [ ] Track score distribution (mean, std dev) over time
- [ ] Compute posterior probability of regression
- [ ] Report: "P(regression | data) = 95%" instead of binary pass/fail
- [ ] Tests verify Bayesian calculations (use synthetic data)
- [ ] Maintain backward compatibility with old baseline.json
- [ ] Documentation in docs/
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
- Model score as normal distribution
- Compute z-score: (new_score - baseline_mean) / baseline_std
- Use scipy.stats for Bayesian inference

**Why It Matters:**
- LLM scores naturally fluctuate
- Single low score ≠ regression
- Probabilistic approach more robust

---

### 22. Add Distributed Test Coordination

**Description:** Support running test suites across multiple machines (distributed load testing). Coordinate via Redis or similar.

**Impact/Effort Matrix:**
- 🎯 **Impact:** High (enterprise feature)
- ⚙️ **Effort:** 4+ hours
- **Value:** Test high-load scenarios

**Acceptance Criteria:**
- [ ] Coordinator service (Redis-backed)
- [ ] Worker registration and heartbeat
- [ ] Load distribution across workers
- [ ] Result aggregation
- [ ] Docker compose example
- [ ] CLI: `--distributed --coordinator redis://localhost:6379`
- [ ] Tests verify coordination logic
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
- Use Redis for job queue and state
- Workers pull tests from queue, report results
- Coordinator aggregates results from workers

**Why It Matters:**
- Enterprise testing at scale
- Test agent performance under load
- Competitive with specialized load testing tools

---

### 23. Add Time-Series Anomaly Detection

**Description:** Detect unusual patterns in latency/score time series using statistical anomaly detection (e.g., Isolation Forest). Alert when metrics deviate from historical patterns.

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (proactive alerting)
- ⚙️ **Effort:** 3 hours
- **Value:** Catch subtle performance degradation

**Acceptance Criteria:**
- [ ] Anomaly detector in `src/panner-ai/baseline/anomaly.py`
- [ ] Use sklearn Isolation Forest or similar
- [ ] Train model on historical baseline data
- [ ] Flag anomalies (z-score > threshold)
- [ ] Report: "Anomaly detected: latency spike"
- [ ] Tests verify anomaly detection
- [ ] Documentation in docs/
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
from sklearn.ensemble import IsolationForest

def detect_anomaly(new_score: float, historical_scores: List[float]):
    """Detect if new score is anomalous."""
    X = np.array(historical_scores).reshape(-1, 1)
    model = IsolationForest(contamination=0.1)
    model.fit(X)
    return model.predict([[new_score]])[0] == -1  # -1 = anomaly
```

**Why It Matters:**
- Gradual degradation is hard to spot
- Machine learning can catch patterns humans miss
- Proactive alerting > reactive debugging

---

### 24. Add Result Diff Visualization

**Description:** Generate visual diff of assertion results between two test runs (show what changed, what stayed same).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (debugging)
- ⚙️ **Effort:** 3 hours
- **Value:** Easy root cause analysis

**Acceptance Criteria:**
- [ ] Diff generator in `src/panner-ai/reporters/diff.py`
- [ ] Compare: test results, latency, LLM scores
- [ ] Highlight changes (green/red)
- [ ] Generate HTML or terminal diff output
- [ ] Example: `panner-ai diff baseline.json results.json`
- [ ] Tests verify diff logic
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
- Deep JSON comparison (use difflib for text)
- Color-coded output for terminal
- Side-by-side HTML view

**Why It Matters:**
- Regression investigation requires comparison
- Visual diffs are faster than reading JSON
- Helps identify exactly what broke

---

### 25. Add Custom Reporting Framework

**Description:** Extensible reporter architecture so users can create custom reporters without modifying source (similar to evaluators plugin system).

**Impact/Effort Matrix:**
- 🎯 **Impact:** Medium (customization)
- ⚙️ **Effort:** 2.5 hours
- **Value:** Power users can create domain-specific reports

**Acceptance Criteria:**
- [ ] Reporter plugin system in `src/panner-ai/core/plugins.py`
- [ ] Users define reporter class extending `BaseReporter`
- [ ] Auto-register custom reporters
- [ ] CLI: `--reporter custom:my_reporter`
- [ ] Example custom reporter in `examples/`
- [ ] Tests verify plugin loading
- [ ] Documentation in docs/
- [ ] All tests pass with 80%+ coverage

**Implementation Hints:**
```python
class BaseReporter(ABC):
    @abstractmethod
    def report(self, results: List[TestResult]) -> str:
        pass
```

**Why It Matters:**
- Different teams need different report formats
- Custom reporters avoid duplication
- Plugin model scales with community

---

## Implementation Guide

### Start Here

1. **Pick an issue** from the lists above (🟢 Easy recommended for first contribution)
2. **Open a GitHub issue** to discuss before coding
3. **Follow the workflow** in CONTRIBUTING.md
4. **Reference acceptance criteria** to know when you're done
5. **Submit a PR** with implementation + tests

### Difficulty Levels

- **🟢 Easy (0.5–2 hours):** Perfect for learning Panner AI. No deep architecture knowledge needed.
- **🟡 Medium (2–4 hours):** Requires understanding of evaluators, baseline tracking, or executor patterns.
- **🔴 Hard (4+ hours):** Advanced knowledge of async patterns, statistics, or system architecture.

### General Acceptance Criteria (All PRs)

Every contribution must:
- ✅ Pass all tests (pytest, coverage ≥ 80%)
- ✅ Follow Ruff linting rules (`ruff check --fix`)
- ✅ Include type hints on all functions
- ✅ Have docstrings (Google style)
- ✅ Update README.md or docs/ if adding new feature
- ✅ Update CHANGELOG.md with entry
- ✅ Add example YAML in `tests/suites/` if applicable
- ✅ Max 5 files per PR

### Testing Checklist

```bash
# Before submitting PR
pytest tests/ -v --cov=src/panner-ai --cov-report=term-missing
ruff check --fix src tests
mypy src/panner-ai/  # if mypy is configured
```

### Communication

- **Issue discussion:** Ask questions in the GitHub issue before implementing
- **Code review:** Be responsive to reviewer feedback
- **Collaborate:** Mention `@philipthomas` if stuck
- **No mega-PRs:** Keep scope to 5 files max; split large features into multiple PRs

---

## FAQ

**Q: What if I want to contribute an idea not on this list?**

A: Great! Open an issue first to discuss. Make sure it aligns with Panner AI's mission: "Precision testing for AI agents."

**Q: How do I know if my implementation is done?**

A: Check all items in "Acceptance Criteria" for your issue. If all are ✅, you're done.

**Q: Can I work on multiple issues at once?**

A: Sure, but keep PRs focused (max 5 files). Multiple issues can be in multiple PRs.

**Q: What if I get stuck?**

A: Post in the GitHub issue or open a Discussion. The community is here to help.

**Q: Will my contribution be merged?**

A: If it meets acceptance criteria and follows Panner AI coding standards, yes! We actively want to merge contributions.

---

## Thank You!

Thank you for contributing to Panner AI! Whether you fix a typo or ship a new evaluator, you're helping build the best testing tool for AI agents. 💙

Questions? Issues? Reach out:
- **GitHub Issues:** [panner-ai/issues](https://github.com/CraftedWithIntent/panner-ai/issues)
- **GitHub Discussions:** [panner-ai/discussions](https://github.com/CraftedWithIntent/panner-ai/discussions)
- **Email:** support@craftedwithintent.com