# Changelog

All notable changes to Assay are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-31

### Added

- **M1.1: Config Parser** — YAML configuration parsing with Pydantic v2 frozen models
  - `parse_suite()` loads and validates SuiteConfig, TestCaseSpec, AssertionSpec
  - Comprehensive error messages for malformed YAML
  - Support for inline YAML body definitions

- **M1.2: HTTP Transport Layer** — Async HTTP test execution with concurrency control
  - `TestExecutor` class with httpx async client
  - Semaphore-based concurrency (default: 5 workers, configurable)
  - Baseline loading and automatic regression detection flag
  - Comprehensive exception handling for network failures

- **M1.3: Evaluator Pipeline** — Pure functional evaluators for test assertions
  - `evaluate_status_code()` — HTTP response code matching
  - `evaluate_latency()` — Response time threshold validation (milliseconds)
  - `evaluate_json_schema()` — Response body JSON schema validation (Pydantic)
  - `evaluate_regex()` — Response body regex pattern matching (with flags)
  - Pipeline orchestration: `evaluate_test_case()`, `aggregate_suite()`
  - Determinism verification via 100-iteration tests

- **M1.4: LLM-as-Judge** — Semantic correctness evaluation via Claude/GPT-4
  - `evaluate_llm_judge()` — Structured JSON response parsing (0.0–1.0 score)
  - LiteLLM abstraction for vendor independence (OpenAI, Anthropic, others)
  - Environment variable configuration (LLM_MODEL, OPENAI_API_KEY, ANTHROPIC_API_KEY)
  - Cost tracking: Token usage + estimated spend per model
  - Graceful fallback: Default score 0.5 on JSON parse error
  - 15 comprehensive mocked tests (zero real API calls in CI)

- **M1.5: Baseline Tracking & Regression Detection** — Historical test score tracking
  - `BaselineTracker` class with `compare()` and `update()` methods
  - Regression detection logic: delta < -0.1 (10% drop threshold)
  - Git commit SHA tracking via subprocess `git rev-parse HEAD`
  - ISO 8601 UTC timestamp recording
  - Baseline persistence to `baseline.json` (git-versioned for trend analysis)
  - Version-aware datetime.UTC import for Python 3.11+ compatibility

- **M1.6: CLI & Multi-Format Reporters** — Command-line interface and report generation
  - `assay run` CLI command with Typer framework
  - Reporter pattern: Abstract base class + 3 concrete implementations
  - `TerminalReporter` — ANSI colored output via Rich library (tables, summary stats)
  - `JUnitReporter` — JUnit XML format for GitHub Actions and Jenkins integration
  - `JSONReporter` — JSON telemetry export for analytics and dashboards
  - Multi-reporter dispatch: `--reporter terminal,junit,json` (comma-separated)
  - Smart output defaults: Terminal → stdout, JUnit/JSON → files with sensible names
  - Exit codes: 0 (all pass, no regressions), 1 (failures or regression detected)
  - Configuration options: `--config`, `--reporter`, `--output`, `--baseline-file`

- **M1.7: GitHub Actions CI/CD Integration** — Automated testing in GitHub workflows
  - `.github/workflows/assay.yml` workflow with 2-stage pipeline
  - `smoke-tests` job: Fast baseline validation (2 tests, <1 minute, gates regression)
  - `regression-tests` job: Full suite (8 tests, ~5 minutes, comprehensive coverage)
  - Artifact upload: 90-day retention for test reports and telemetry
  - Test reporting: JUnit XML parsed as GitHub PR checks + annotations
  - Exit codes propagated: Blocks PR merge on failures/regressions (exit 1)
  - Pre-configured test suites:
    - `tests/suites/smoke.yaml` — Health check + root endpoint
    - `tests/suites/regression.yaml` — CRUD operations, latency, error handling

- **M1.8: Documentation & Release** — Comprehensive user and developer documentation
  - `README.md` — Project overview, quick start, architecture, usage examples
  - `CONTRIBUTING.md` — Setup, code style, testing, PR workflow, release process
  - `CHANGELOG.md` — This file (release history)
  - `docs/ARCHITECTURE.md` — Deep-dive system design, data flow, extension points
  - PyPI metadata: description, readme, homepage, repository, keywords
  - GitHub milestone tracking: `M21-status.md` updated with completion status

### Fixed

- **Hotfix: cli.py Syntax Errors** — Fixed literal backslash-n escape sequences
  - Replaced `except Exception as e:\n        ` (literal) with proper newline characters\n  - Updated `pyproject.toml` to suppress BLE001 linting rule (Phase 1 error propagation)\n  - Removed unused `ReporterConfig` import from `reporters/json.py`

### Changed

- Moved `SuiteReport` to canonical location in `executor.executor` (eliminated duplication)
- Ruff configuration: Added `BLE001` to `extend-ignore` list with rationale

### Dependencies

- **typer** 0.12+ — CLI framework
- **rich** 13+ — Terminal output formatting (ANSI colors, tables)
- **httpx** 0.24+ — Async HTTP client
- **pydantic** 2.0+ — Data validation and serialization
- **litellm** 1.0+ — Vendor-agnostic LLM interface
- **pytest** 7.0+ — Testing framework (dev dependency)
- **pytest-cov** 4.0+ — Code coverage reporting (dev dependency)

### Architecture

- **Functional Core + Imperative Shell (ADR-001)**: Pure evaluators (core) separated from CLI/I/O (shell)
- **Zero Code Duplication**: Single SuiteReport model, reusable evaluator functions, abstract reporter pattern
- **Concurrency Control**: Semaphore-based async dispatch (5 workers default)
- **Immutable Data Models**: Pydantic frozen=True for all core types
- **Error Propagation**: Phase 1 — no exception handling in core; CLI propagates via exit codes
- **Git Integration**: Baseline versioning with commit SHA + timestamp

### Test Coverage

- **Total Tests**: 48+ test methods across all milestones
- **Coverage Target**: ≥80% (enforced by CI/CD)
- **Mocking Strategy**: All external services mocked (LLM, HTTP) — zero real API calls in CI
- **Determinism Verification**: 100-iteration tests for all evaluators

### Known Limitations (Phase 1)

- No conditional test skipping (Phase 2 feature)
- No advanced report filtering (Phase 2 feature)
- Baseline regression threshold hardcoded to -0.1 (Phase 2: configurable)
- No authentication support in HTTP executor (Phase 2: OAuth2, API keys)
- Limited custom assertion types (Phase 2: user-defined evaluators via plugins)

---

## Roadmap (Phase 2+)

- [ ] Authentication support (OAuth2, API keys, JWT)
- [ ] Conditional test skipping (environment-based, tag-based)
- [ ] Advanced reporting (HTML, Markdown, Slack integration)
- [ ] Plugin system for custom evaluators
- [ ] Configurable baseline thresholds
- [ ] Performance profiling integration
- [ ] Load testing mode (variable concurrency, ramp-up)

---

**For detailed architecture and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).**
