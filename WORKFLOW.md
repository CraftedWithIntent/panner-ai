# WORKFLOW.md - How to Prompt Ash for Work on Assay

This document defines how to direct work on Assay and what to expect from execution.

**tl;dr:** Pick an issue → tell me the issue number → I handle the rest (branch → code → test → PR → review).

---

## Directing Work: The Standard Prompt

### Simple Directive

```
Work on M1.3: Deterministic Evaluators

or

Start issue #4

or

Pick up M1.5 and close it
```

**What I do:**
1. Read the issue fully (title, body, acceptance criteria, labels)
2. Check for blockers (open PRs, broken main, dependencies on other issues)
3. Create feature branch: `git checkout -b feature/M{X}.{Y}-{description}`
4. Execute the work (code + tests)
5. Create PR with semantic commit message
6. Update issue label: `status:backlog` → `status:in-progress` → `status:review`
7. Wait for your approval/merge

### Detailed Directive (Optional)

If you want to override defaults:

```
Work on M1.4 (LLM Judge)
- Use Claude 3.5 Sonnet, not GPT-4
- Prioritize fallback logic over perfect parsing
- Don't worry about production metrics yet, focus on happy path
```

I'll incorporate context and adjust execution accordingly.

### Batch Work (Multiple Issues)

```
Start M1.1, M1.2, M1.3 - but only create feature branches, don't merge yet
```

or

```
Finish M1.5 and M1.6 back-to-back
```

I'll batch independent work efficiently and report completion state.

---

## Work Execution Flow

### Pre-Work Checklist (MANDATORY — Per MEMORY.md)

Before I write any code:

1. ✅ **Check for open PRs** — `gh pr list --state open` must be empty
2. ✅ **Verify main branch clean** — No pending merges or conflicts
3. ✅ **Codebase Reconnaissance** — Search for existing implementations (zero duplicate policy)
4. ✅ **Run local validation suite** — Build + test must pass
5. ✅ **Update issue label** — `status:backlog` → `status:in-progress`
6. ✅ **Create feature branch** — Never work on main directly
7. ✅ Only THEN start coding

### Execution Discipline (MANDATORY)

**Branch Strategy:**
- Feature branch: `feature/M{X}.{Y}-{description}` (e.g., `feature/M1.3-deterministic-evaluators`)
- Never commit to main directly
- Always create PR before merge

**Code Quality Gates:**
- Linting: `ruff check src tests` (0 violations)
- Type checking: `pyright src` (strict mode, 0 errors)
- Tests: `pytest tests --cov=src/assay` (all passing, coverage ≥ 80%)
- Build: `python -m build` (clean wheel + sdist)

**Commit Discipline:**
- Semantic commit messages: `feat(domain): description` or `fix(domain): description`
- One logical change per commit
- No merge commits; rebase on main before PR

**PR Requirements:**
- Title: `M{X}.{Y}: Issue title here`
- Body: Summarize changes, link to issue, note any design decisions
- Labels: Auto-added from issue
- Ready for immediate review (no drafts)

### State Transitions

```
status:backlog → status:in-progress (when I start work)
                → status:review (when PR created)
                → status:done (when merged to main)
```

If I hit a blocker:
```
status:in-progress → status:blocked (with comment explaining blocker)
```

You unblock → I resume immediately and move to `status:review`.

---

## Expected Outcomes Per Issue Type

### Feature Issues (M1.1–M1.7)

**You'll get:**
- Feature branch ready for review (all tests passing)
- PR with implementation + tests + updated architecture docs
- Exit criteria met (acceptance criteria from issue checked off)
- Clean git history (rebase, no merge commits)

**What "done" means:**
- Code merged to main
- All CI checks passing
- Tests validating new behavior
- Docs (if applicable) updated

### Documentation Issues (M1.8)

**You'll get:**
- New docs files (.md) in `docs/` or repo root
- Examples (YAML configs, quick-start, etc.) in `test_suites/`
- All links working, formatting clean
- Ready to ship with v0.1.0

---

## Communication & Progress Updates

### During Work

If I finish in one session:
```
✅ M1.3 complete. PR ready: #<number>
```

If work spans multiple sessions:
```
🌿 Working on M1.5. 
Status: Config parser done, baseline storage 70% complete. 
Blockers: None. 
ETA: Next session (2 hours more).
```

### If I Hit a Blocker

Example: Upstream API changed, breaking tests.

```
🚫 BLOCKED: M1.4 (LLM Judge)
Reason: Claude API rate limit exceeded during testing
Action: Needs API key refresh or fallback to mock
Awaiting: Your direction (use mock? try different model?)
```

I'll wait for your guidance before proceeding.

### When Done

```
✅ M1.X merged to main. Branch deleted.
Next available: Ready for M1.Y
```

---

## Approval & Review Expectations

### PR Review Workflow

1. I create PR → `status:review`
2. You review (or approve automatically)
3. If approved:
   - I merge (squash/rebase, no merge commits)
   - Delete feature branch
   - Close issue (auto-linked in PR)
4. If revisions needed:
   - You leave comments
   - I update branch with new commits
   - Ready for re-review

### No Manual Approvals Needed For

- Code style (ruff enforces it)
- Type safety (pyright enforces it)
- Test coverage (pytest gates it)
- Lint (pre-commit enforced)

**You approve for:**
- Architecture alignment
- Feature correctness
- Acceptance criteria met
- Docs quality

---

## Escalation & Decisions

If I encounter architectural ambiguity mid-task:

```
❓ M1.2 (Transport): Should concurrent request pool be 5 or 10?
Options:
  A) Pool size = 5 (conservative, safer)
  B) Pool size = 10 (faster, risk of rate limits)
  C) Configurable via suite.yaml (flexible but complex)
Recommendation: Option C (align with user config needs)
```

I'll propose and wait for your call. Never guess on design.

---

## Examples: Full Work Cycles

### Example 1: Simple Feature (M1.1 — Config Parser)

```
You: Work on M1.1

Me: 
✓ Pre-work checklist passed (main clean, no open PRs)
✓ Branch created: feature/M1.1-config-parser
✓ Code written: src/assay/infrastructure/parser.py
✓ Tests added: tests/test_config_parser.py
✓ Build passing: ruff ✓ | pyright ✓ | pytest ✓
✓ PR created: #10 "M1.1: Config Parser"
```

You review & approve → I merge → Issue #2 closes automatically.

---

### Example 2: Blocked Work (M1.4 — LLM Judge)

```
You: Start M1.4

Me:
✓ Pre-work checklist passed
✓ Branch created: feature/M1.4-llm-judge
✗ BLOCKED: Need OpenAI API key to test Claude integration
  (Currently unset in .env)

Status: status:blocked
Action: Set OPENAI_API_KEY and I'll resume
```

You set env var → I resume → Complete as usual.

---

### Example 3: Batch Work (M1.5 + M1.6)

```
You: Finish M1.5 and M1.6 back-to-back

Me:
✓ M1.5 complete (PR #11) → merged
✓ M1.6 started (branch: feature/M1.6-reporters)
✓ Tests passing, reporters rendering correctly
✓ PR #12 ready for review
```

You approve → I merge both → Both issues close.

---

## Failure Modes & Recovery

### If Main Breaks

If a regression slips into `main` during my work:

```
🚫 BROKEN MAIN: Previous PR introduced latency evaluator bug
Action: Priority 1 - reverting PR #X
```

Revert PR takes precedence. I'll fix and re-merge after main is green.

### If PR Fails CI

```
❌ CI Failed: Test coverage dropped to 72%
Action: Adding tests to raise coverage to 80%
Updated: PR #X with new commit
```

I fix on the branch and update the PR. No force-pushes to `main`.

### If I Discover Scope Creep

```
⚠️ M1.3 (Evaluators): Discovered that JSON schema validation needs recursive key checking
Current scope only handles top-level keys.

Options:
  A) Keep shallow validation (meets MVP criteria)
  B) Add deep validation (Phase 2 enhancement)
  C) Split into M1.3a (shallow) + M1.3-addendum (deep)

Recommendation: Option A (MVP-first, Phase 2 enhancement)
```

I'll propose, you decide. Work stays scoped per issue.

---

## Workflow Summary

| Step | Owner | Input | Output |
|------|-------|-------|--------|
| 1. Pick Issue | You | Issue number (M1.X or #Y) | "Got it, starting work" |
| 2. Pre-Check | Me | Issue details | Blockers identified or clear to proceed |
| 3. Code & Test | Me | Acceptance criteria | Feature branch with passing tests |
| 4. PR | Me | Code + tests | PR #N ready for review |
| 5. Review | You | PR changes | Approved or revision requests |
| 6. Merge | Me | Approval | Main updated, issue closed |
| 7. Report | Me | Completion | Ready for next issue |

---

## Questions?

If you're unsure how to direct work, default to:

```
Work on M1.X
```

I'll handle the rest. This document is your reference for what happens behind the scenes.

---

**Ash, Primary Orchestrator**  
Assay Project (v0.1.0-dev)  
Last Updated: 2026-08-30
