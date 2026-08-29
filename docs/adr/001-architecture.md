# ADR 001: Assay Architecture — Functional Core + Imperative Shell for Regression Testing

## Status
Accepted

## Context

Assay is a regression testing framework for AI agents. Traditional testing tools fail on semantic evaluation—a prompt adjustment or model update can fix one edge case while silently breaking five others. The framework must:

1. Execute test suites asynchronously against agent endpoints
2. Evaluate semantic correctness using LLM-as-a-judge with no vendor lock-in
3. Track baseline performance across commits (git-versioned)
4. Report results across multiple formats (CLI, JUnit, PR comments, JSON)
5. Handle non-deterministic model behaviors with reproducible scoring

## Decision

Adopt a **Functional Core + Imperative Shell** architecture:

- **Functional Core**: Pure, immutable domain logic (evaluators, scoring, aggregation)
  - No side effects; all types frozen (Pydantic `frozen=True`)
  - Evaluators are first-class functions: regex match, latency check, JSON schema, LLM judge
  - Composable pipeline: test case → [assertions] → scores → aggregation → report
  
- **Imperative Shell**: I/O, transport, state management
  - Config parsing (PyYAML → dataclasses)
  - Async HTTP dispatch to agent endpoints (httpx)
  - Baseline storage (baseline.json in git)
  - Multi-target reporters (CLI, JUnit XML, GitHub PR, JSON)

## Consequences

### Benefits
✅ **Testability**: Pure functions = 100% coverage without mocks  
✅ **Composability**: Add new assertion types by extending evaluators  
✅ **Determinism**: Reproducible test runs across machines  
✅ **Parallelization**: No shared state; safe to parallelize evaluations  
✅ **Auditability**: Complete trace of all scoring decisions  

### Trade-offs
⚠️ Imperative shell adds complexity for file I/O and HTTP coordination  
⚠️ Immutability enforced (no performance optimization via mutation)  
⚠️ DSL-driven config (YAML) requires learning test syntax

## Architecture Diagram

### Request Flow
```mermaid
flowchart TD
    A["Test Suite YAML"] -->|Parse| B["Config Parser"]
    B -->|Immutable Config| C["Test Executor"]
    C -->|Async HTTP| D["Agent Endpoint"]
    D -->|Response| E["Evaluators Pipeline"]
    E -->|Regex Match| F["Assertion Results"]
    E -->|Status Code| F
    E -->|Latency Check| F
    E -->|LLM Judge| F
    F -->|Score Aggregation| G["Suite Report"]
    G -->|Baseline Delta| H{Regression?}
    H -->|Pass| I["Exit 0"]
    H -->|Fail| J["Exit 1 + Report"]
    J -->|CLI/JUnit/PR| K["Reporter Output"]
```

### Component Interaction Sequence
```mermaid
sequenceDiagram
    participant User as User/CLI
    participant Parser as Config Parser
    participant Executor as Test Executor
    participant Agent as Agent Endpoint
    participant Evaluators as Evaluators
    participant Storage as Baseline Storage
    participant Reporter as Reporter

    User->>Parser: Load suite.yaml
    Parser->>Parser: Validate & deserialize
    Parser->>Executor: Immutable SuiteConfig
    
    Executor->>Agent: HTTP POST (payload)
    Agent-->>Executor: AgentResponse
    
    Executor->>Evaluators: evaluate_test_case(response, assertions)
    Evaluators->>Evaluators: Apply regex matcher
    Evaluators->>Evaluators: Check status code
    Evaluators->>Evaluators: Measure latency
    Evaluators->>Evaluators: LLM judge (semantic score)
    Evaluators-->>Executor: TestCaseReport
    
    Executor->>Storage: Load baseline.json
    Storage-->>Executor: Prior scores
    
    Executor->>Executor: Compute delta & regression
    Executor->>Reporter: SuiteReport
    Reporter->>Reporter: Render CLI/JUnit/PR
    Reporter-->>User: Pass/Fail exit code
```

## Implementation Details

### Domain Types (Functional Core)
```python
@dataclass(frozen=True)
class AssertionSpec:
    type: Literal["regex", "status_code", "latency", "json_schema", "llm_judge"]
    expected: Any
    tolerance: Optional[float] = None

@dataclass(frozen=True)
class TestCaseReport:
    test_name: str
    passed: bool
    scores: Dict[str, float]
    violations: List[str]
    latency_ms: float
```

### Evaluators (Pure Functions)
```python
def evaluate_regex(response: str, pattern: str) -> bool:
    return bool(re.search(pattern, response))

def evaluate_latency(latency_ms: float, max_ms: float) -> bool:
    return latency_ms <= max_ms

def evaluate_llm_judge(response: str, assertion: AssertionSpec) -> float:
    # Returns similarity score (0.0–1.0), no side effects
    score = model.judge_semantic_alignment(response, assertion.expected)
    return score
```
\n### CI Integration
- **GitHub Actions**: Composite action + container
- **Exit codes**: 0 (all pass), 1 (regressions detected)
- **Baseline tracking**: baseline.json committed to main branch

## Related Decisions
- ADR-002: Model agnosticism via LiteLLM abstraction
- ADR-003: YAML test specs for human-readable, git-friendly definitions
