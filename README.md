# Assay: Regression Testing & LLM-as-Judge for AI Agents

![Assay](https://img.shields.io/badge/Assay-Testing%20%26%20CI%2FCD-brightgreen) ![License](https://img.shields.io/badge/License-MIT-blue) ![Python](https://img.shields.io/badge/Python-3.11%2B-blue)

**Precision regression testing framework for AI agents: semantic purity & behavioral integrity verification.**

---

## The Problem

AI agents and LLM-powered applications are inherently non-deterministic. A prompt adjustment, system instruction tweak, or upstream model update can fix one edge case while silently breaking five others. Traditional testing tools (pytest, Jest) cannot evaluate semantic alignment, fuzzy constraints, probabilistic model behaviors, or complex multi-step agent workflows across commits. Teams ship to production blind—silent behavioral regressions leak past code review every day.

## The Solution: Assay

**Assay** is the precision tool that verifies the semantic purity and behavioral integrity of AI agents before they reach production. It bridges the 1848 California Gold Rush "picks and shovels" heritage with modern engineering—in mining, an assay is the precise compositional analysis determining ore purity; in AI development, Assay is the framework that catches regressions no human reviewer would spot.

### Core Value Proposition

| Metric | Without Assay | With Assay |
|--------|---------------|------------|
| Regression Detection | ✗ Manual testing, silent failures | ✓ Automated semantic checks across commits |
| LLM Judge Evaluation | ✗ No baseline scoring | ✓ Semantic alignment scoring with any model |
| Baseline Tracking | ✗ Unknown | ✓ Git-versioned performance history |
| Test Authoring | ✗ Code-heavy, brittle regex | ✓ Declarative YAML, git-friendly |
| CI Integration | ✗ Ad-hoc scripts | ✓ GitHub Action, Docker, generic CI |
| Model Support | N/A | ✗ Vendor lock-in | ✓ Model agnostic (local/open/proprietary) |

---

## What is Assay? (Product Scope)

### Core Capabilities

**Open-Source CLI & Python Library**
- Standalone `assay` command-line tool
- Importable Python library for programmatic test harnesses
- GitHub Action for CI/CD integration
- Docker container for polyglot CI runners

**Test Execution Engine**
- Asynchronous HTTP dispatch to AI agent endpoints
- Configurable concurrency and timeout management
- Environment variable hydration for secret injection
- Request/response lifecycle instrumentation

**Evaluation Strategies**
- **Deterministic Assertions:** Regex patterns, HTTP status codes, latency thresholds, JSON schema validation
- **LLM-as-a-Judge:** Score semantic alignment and behavioral correctness using structured JSON output from Claude, GPT-4, or open-source models
- **Higher-Order Reduction:** Weighted score aggregation across multiple assertions

**Baseline & Regression Tracking**
- Snapshot test performance (baseline.json) in git
- Delta computation against historical runs
- Configurable regression thresholds (pass/fail gates)

**Rich Reporting**
- Terminal UI with ANSI colors and progress indicators
- JUnit XML output for CI platform integration
- GitHub PR comments with branch comparison diffs
- JSON telemetry export for Assay Cloud sync

**Multi-Format Delivery**
- PyPI package (`assay-cli`)
- GitHub Actions Marketplace (`craftedwithintent/assay-action`)
- Docker container (GHCR: `ghcr.io/craftedwithintent/assay`)
- Homebrew formula (planned Phase 2)

---

## Who Uses Assay? (Target Personas & Customer Segments)

### Primary Personas

**AI Engineers & LLM App Developers**
- Use the free open-source CLI locally and in CI to catch prompt regressions pre-merge
- Define test suites in YAML, commit baselines to git
- Fast feedback loop during development

**Engineering Managers & Tech Leads**
- Enforce regression testing as a quality gate in PR workflows
- Ensure no silent behavioral regressions slip into production
- Build institutional confidence in AI agent reliability

**Compliance Officers & Security Teams**
- Need audit evidence that AI systems behave predictably
- Require red-teaming and adversarial test packs
- Must demonstrate due diligence to regulators and stakeholders

---

---

## Quick Start

### Installation

```bash
# Via pip
pip install assay-cli

# Via Docker
docker run -v $PWD:/app ghcr.io/craftedwithintent/assay:latest

# From source
git clone https://github.com/CraftedWithIntent/assay.git
cd assay
uv pip install -e .
```

### Basic Usage

#### 1. Local Usage

Create a test suite file (`suite.yaml`):

```yaml
suite: my-agent-tests
agent_endpoint: http://localhost:8000/chat

tests:
  - name: simple-greeting
    payload:
      message: "Hello"
    assertions:
      - type: status_code
        expected: 200
      - type: regex
        pattern: '("greeting"|"hello")'
      - type: latency
        max_ms: 500
```

Run the suite:

```bash
assay run --config suite.yaml
```

#### 2. GitHub Actions

Add to your CI workflow:

```yaml
- uses: craftedwithintent/assay-action@v1
  with:
    config: suite.yaml
```

#### 3. Docker

```bash
docker run -v $PWD:/app ghcr.io/craftedwithintent/assay:latest run -c suite.yaml
```

---

## When Do You Test? (Lifecycle Triggers)

### Pre-Commit / Local Dev
```bash
assay run --config suite.yaml
```
Rapid local runs against changed prompts, system instructions, or tool definitions.

### Pull Request / CI Stage
Full suite execution comparing target branch performance against `main` (baseline). Non-zero exit codes block merge if regressions exceed threshold.

### Scheduled Nightly / Model Drift Checks
Automated synthetic testing detecting third-party foundation model version changes. Alert teams if upstream provider behavior shifts.

### Production Incident Ingestion (Assay Cloud)
Convert real-world user failures into permanent regression test cases. Prevent the same failure from reaching production twice.

---

## How Does Assay Work? (Technical Execution & Core Mechanisms)

### Architecture: Functional Core + Imperative Shell

```
┌──────────────────────────────────────────────────────────────┐
│  User Interface Layer                                          │
│  ┌─────────────────────┐  ┌──────────────────────────────┐   │
│  │ CLI (typer)         │  │ Python Programmatic API      │   │
│  └────────────┬────────┘  └──────────────┬───────────────┘   │
└───────────────┼──────────────────────────┼──────────────────┘
                │                          │
┌───────────────┴──────────────────────────┴──────────────────┐
│ Imperative Shell (I/O, Adapters, Transport)                  │
│                                                                │
│  ┌────────────────────────┐  ┌─────────────────────────────┐ │
│  │ Config Parser          │  │ Async HTTP Agent Transport  │ │
│  │ (PyYAML/Pydantic)      │  │ (httpx with concurrency)    │ │
│  └────────────────────────┘  └─────────────────────────────┘ │
│                                                                │
│  ┌────────────────────────┐  ┌─────────────────────────────┐ │
│  │ Baseline Storage       │  │ Multi-Target Reporters      │ │
│  │ (baseline.json)        │  │ (CLI/JUnit/PR/Cloud)        │ │
│  └────────────────────────┘  └─────────────────────────────┘ │
└───────────────┬──────────────────────────────────────────────┘
                │
         [ Pure Data In ]
                │
┌───────────────┴──────────────────────────────────────────────┐
│ Functional Core (Pure Domain Logic)                           │
│                                                                │
│  Immutable Types:                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │ AssertionSpec│  │AgentResponse │  │TestCaseReport   │    │
│  └──────────────┘  └──────────────┘  └─────────────────┘    │
│                                                                │
│  Pure Evaluators (no side effects):                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Regex Match  │  │ Latency      │  │ Status Code  │       │
│  │ JSON Schema  │  │ LLM Judge    │  │ Aggregation  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────┬──────────────────────────────────────────────┘
                │
        [ Pure Data Out ]
                │
┌───────────────┴──────────────────────────────────────────────┐
│ Output (SuiteReport)                                           │
│  - Test case results                                           │
│  - Scores and deltas                                           │
│  - Pass/fail status                                           │
└───────────────────────────────────────────────────────────────┘
```

### Design Principles

**Functional Core, Imperative Shell**
- Pure, referentially transparent evaluation functions separate cleanly from asynchronous network I/O, file systems, and external services
- Easier to test, reason about, and parallelize
- No hidden side effects in domain logic

**Model Agnosticism**
- Abstract model routing layer (LiteLLM/Ollama) shields you from vendor lock-in
- Support local, open-source, and proprietary frontier models as evaluators
- Graceful fallback to deterministic assertions when LLM judge unavailable

**Declarative Test Specifications**
- YAML-first: human-readable, git-friendly, version-controlled
- Compose test suites from simple building blocks
- No code generation or DSLs—just data

**Deterministic Execution**
- Reproducible test runs across machines
- Seeded randomness (when needed)
- Clear audit trail of all decisions

---

## Delivery & Packaging (Multi-Channel Distribution)

| Distribution Channel | Target Audience | Registry | Consumption Pattern |
|---|---|---|---|
| **1. GitHub Action** | GitHub CI/CD workflows | GitHub Marketplace | `uses: craftedwithintent/assay-action@v1` |
| **2. Standalone CLI** | Local developers & general CI | PyPI (`assay-cli`) | `pip install assay-cli` → `assay run -c suite.yaml` |
| **3. Python Library** | Custom programmatic harnesses | PyPI (`assay`) | `from assay.core import evaluate_test_case` |
| **4. Docker Container** | Polyglot CI runners & air-gapped environments | GHCR | `docker run ghcr.io/craftedwithintent/assay:latest` |
| **5. Homebrew** | macOS developers (Phase 2) | Homebrew Tap | `brew install assay` |

---

## Codebase Layout

```
assay/
├── .github/workflows/
│   ├── ci.yml              # Test matrix (Python 3.11/3.12), linting, build
│   └── publish.yml         # PyPI & GitHub release publishing
├── Dockerfile              # Multi-stage runtime image
├── action.yml              # GitHub Action composite action
├── pyproject.toml          # uv-managed dependencies
├── README.md               # This file
├── WORKFLOW.md             # Execution discipline (pre-work, branch strategy, QA gates)
├── src/assay/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI entrypoint
│   ├── domain/
│   │   └── types.py        # Immutable Pydantic domain models (frozen)
│   ├── core/
│   │   ├── evaluators.py   # Pure functional evaluation logic (no side effects)
│   │   └── pipeline.py     # Pipeline reducer and score aggregation
│   └── infrastructure/
│       ├── reporters/      # Multi-target reporting (CLI, JUnit, PR, JSON)
│       └── storage/        # Baseline storage (baseline.json)
└── tests/
    └── test_functional_core.py  # Unit tests with pytest fixtures (≥80% coverage)
```

## Deployment

### Local Development

```bash
git clone https://github.com/CraftedWithIntent/assay.git
cd assay
uv pip install -e .
assay run --config suite.yaml
```

### Docker

```bash
docker run -v $PWD:/data \
  ghcr.io/craftedwithintent/assay:latest \
  run --config /data/suite.yaml
```

### CI/CD (GitHub Actions)

```yaml
- uses: craftedwithintent/assay-action@v1
  with:
    config: suite.yaml
```

---

**No Shared Dependencies:** Assay is completely decoupled from other CraftedWithIntent products. It works standalone as an open-source CLI tool.

---



---

## Architecture & Design

### Core Principles

1. **Functional Purity:** Domain logic has zero side effects; I/O is isolated to the shell
2. **Immutability:** All data structures are frozen; no hidden state mutations
3. **Composability:** Evaluators are first-class; easy to add new assertion types
4. **Determinism:** Reproducible test runs with seeded randomness
5. **Auditability:** Complete trace of all decisions and scores

### Key Design Decisions

- **YAML over Python DSL:** Humans write tests, not code
- **Model Agnosticism:** LiteLLM abstraction shields from vendor lock-in
- **Baseline in Git:** Version control for test performance history
- **Exit Codes Matter:** CI automation depends on clear pass/fail signals

---

## Features

### MVP (Phase 1)

- ✅ **Deterministic Assertions:** Regex patterns, latency thresholds, HTTP status codes, JSON schema validation
- ✅ **LLM-as-a-Judge:** Score semantic alignment and behavioral correctness using any model (Claude, GPT-4, Ollama)
- ✅ **Baseline Tracking:** Snapshot test performance in git, detect regressions across commits
- ✅ **Multi-Format Reporting:** Rich terminal UI, JUnit XML for CI platforms, GitHub PR comments with diffs, JSON telemetry
- ✅ **Model Agnostic:** Works with local, open-source, or proprietary LLMs via LiteLLM
- ✅ **Configurable Concurrency:** Parallel test execution with timeout management
- ✅ **Pure Functional Design:** Domain logic isolated from I/O; easy to test and parallelize
- ✅ **Git-Friendly:** YAML test specs and baselines version-controlled, human-readable
- ✅ **CI/CD Ready:** GitHub Actions, Docker container, generic CI runners (GitLab, CircleCI, etc.)

### Roadmap (Phase 2+)

- Phase 2: CLI cloud telemetry (`--sync` hook for Assay Cloud)
- Phase 2: Production trace-to-test converter (auto-generate test cases from logs)
- Phase 2: Compliance report generator (EU AI Act, SOC2 audits)
- Phase 3: Web dashboard (visual regression diffs, multi-PR tracking, trend analysis)  

---

## License

**Open-Source Tier:** MIT License

See LICENSE file for details.

---

## Project Status

**v0.1.0-dev** — Initial monorepo scaffold. Phase 1 implementation underway.

---

**CraftedWithIntent™** — Precision Testing for AI Systems
