# WORKFLOW.md - How to Prompt Ash for Work

This document defines how to direct work across all projects and what to expect from execution.

**tl;dr:** Specify project (or use current context) → pick an issue → I handle the rest (branch → code → test → PR → review).

---

## Project Routing: Which Workspace?

### Canonical Project List

I work on everything under `/Users/philipthomas/.openclaw/workspaces/`:

| Workspace | Purpose | Status |
|-----------|---------|--------|
| **ash-orchestrator** | Primary orchestrator (you are here) | Active |
| **panner-ai** | Precision testing for AI agents | Active (Phase 1) |
| **orch-1** | Sub-orchestrator for Projects 1-10 | Placeholder |
| **orch-2** | Sub-orchestrator for Projects 11-20 | Placeholder |
| **flow-ledger** | Finance ledger system | Active |
| **game-dev** | Game development project | Active |
| *(future)* | New projects added as needed | Planned |

### How I Route Requests

**Explicit Project Specification (Preferred):**

```
Work on panner-ai M1.3

or

Start flow-ledger issue #42

or

Pick up game-dev PR review
```

I immediately resolve the workspace path (`~/.openclaw/workspaces/{project}/`) and cd into it.

**Implicit/Current Context:**

If you don't specify a project in the directive:

```
Work on M1.3
```

I assume the **current session's project context**. In the Assay session, that's `panner-ai/`. In the flow-ledger session, that's `flow-ledger/`.

**Ambiguity Resolution:**

If the project name is unclear or non-existent:

```
❓ "Work on X" — but X workspace doesn't exist
Assuming: Did you mean 'panner-ai'? Or 'orch-1'?
Action: Asking for clarification before proceeding
```

I'll never guess at workspace routing. Always ask if ambiguous.

### Workspace-Specific Workflows

Each workspace has its own:
- GitHub repo (e.g., `CraftedWithIntent/panner-ai`, `philipthomas/flow-ledger`)
- Issue tracking (GitHub issues per repo)
- CI/CD pipelines
- Tech stack & tooling

But the **work execution flow** (below) is identical across all workspaces.

---

## Directing Work: The Standard Prompt

### Simple Directive (With Implicit Project)

```
Work on M1.3: Deterministic Evaluators

or

Start issue #4

or

Pick up M1.5 and close it
```

(Assumes current session/project context)

### Simple Directive (With Explicit Project)

```
Work on panner-ai M1.3

or

Start flow-ledger issue #42

or

Handle game-dev PR #7 review
```

(Explicitly names the workspace, no ambiguity)

**What I do:**
1. Resolve workspace path
2. Read the issue fully (title, body, acceptance criteria, labels)
3. Check for blockers (open PRs, broken main, dependencies on other issues)
4. Create feature branch (naming convention depends on workspace)
5. Execute the work (code + tests)
6. Create PR with semantic commit message
7. Update issue label: `status:backlog` → `status:in-progress` → `status:review`
8. Wait for your approval/merge

### Detailed Directive (Optional)

If you want to override defaults:

```
Work on panner-ai M1.4 (LLM Judge)
- Use Claude 3.5 Sonnet, not GPT-4
- Prioritize fallback logic over perfect parsing
- Don't worry about production metrics yet, focus on happy path
```

I'll incorporate context and adjust execution accordingly.

### Batch Work (Same or Different Workspaces)

```
Start panner-ai M1.1, M1.2, M1.3 - but only create branches, don't merge yet
```

or

```
Finish panner-ai M1.5 and M1.6 back-to-back
```

or

```
Work on panner-ai M1.3, then flow-ledger #42, then game-dev PR review
```

I'll route to each workspace, batch independent work efficiently, and report completion state per project.

---

## Work Execution Flow (Same Across All Workspaces)

### Pre-Work Checklist (MANDATORY — Per MEMORY.md)

Before I write any code in ANY workspace:

1. ✅ **Navigate to correct workspace** — `cd ~/.openclaw/workspaces/{project}/`
2. ✅ **Check for open PRs** — `gh pr list --state open` must be empty
3. ✅ **Verify main branch clean** — No pending merges or conflicts
4. ✅ **Codebase Reconnaissance** — Search for existing implementations (zero duplicate policy)
5. ✅ **Run local validation suite** — Build + test must pass
6. ✅ **Update issue label** — `status:backlog` → `status:in-progress`
7. ✅ **Create feature branch** — Never work on main directly
8. ✅ Only THEN start coding

### Execution Discipline (MANDATORY)

**Branch Strategy (Workspace-Specific):**
- For Assay: `feature/M{X}.{Y}-{description}` (e.g., `feature/M1.3-deterministic-evaluators`)
- For flow-ledger: Follow existing branch conventions in that repo
- For others: Check workspace conventions
- Never commit to main directly
- Always create PR before merge

**Code Quality Gates (Workspace-Specific):**
- Linting: Follow workspace conventions (ruff, flake8, eslint, etc.)
- Type checking: Enabled where configured (pyright, mypy, etc.)
- Tests: All passing, coverage ≥ 80% where applicable
- Build: Passes local build commands (`python -m build`, `dotnet build`, etc.)

I verify gates from each workspace's CI/CD config, not hardcoded here.

**Commit Discipline:**
- Semantic commit messages: `feat(domain): description` or `fix(domain): description`
- One logical change per commit
- No merge commits; rebase on main before PR

**PR Requirements:**
- Title: Follows workspace convention (e.g., `M{X}.{Y}: Issue title` for Assay, `Issue #N: Title` for others)
- Body: Summarize changes, link to issue, note any design decisions
- Labels: Auto-added from issue
- Ready for immediate review (no drafts)

**Assay-Specific PR Format:**

*Title Format:*
```
M{X}.{Y}: Issue title
```
Example: `M1.1: Config Parser` or `M1.3: Deterministic Evaluators`

*Body Template:*
```markdown
## Description
Brief summary of changes and purpose.

## Changes
- Changed file1.py (what and why)
- Added tests for feature X
- Updated architecture docs

## Testing
- test_feature.py: X test cases passing
- Coverage: XX%
- Benchmarks: (if applicable)

## Related Issue
Closes #N

## Notes
Any additional context or Phase 1 limitations.
```

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

### Feature Issues

**You'll get:**
- Feature branch ready for review (all tests passing)
- PR with implementation + tests + updated documentation/architecture
- Exit criteria met (acceptance criteria from issue checked off)
- Clean git history (rebase, no merge commits)

**What "done" means:**
- Code merged to main
- All CI checks passing
- Tests validating new behavior
- Docs (if applicable) updated

### Documentation Issues

**You'll get:**
- New docs files (.md) in `docs/` or repo root
- Examples and quick-start guides
- All links working, formatting clean
- Ready to ship with next release

### Bug/Refactor Issues

**You'll get:**
- Root cause analysis (if applicable)
- Code changes with regression tests
- PR ready for review
- Exit criteria met

---

## Communication & Progress Updates

### During Work

If I finish in one session:
```
✅ panner-ai M1.3 complete. PR ready: #<number>
```

If work spans multiple sessions:
```
🌿 Working on flow-ledger #42. 
Status: Data model done, API endpoints 60% complete. 
Blockers: None. 
ETA: Next session (3 hours more).
```

### If I Hit a Blocker

Example: Upstream API changed, breaking tests.

```
🚫 BLOCKED: panner-ai M1.4 (LLM Judge)
Reason: Claude API rate limit exceeded during testing
Action: Needs API key refresh or fallback to mock
Awaiting: Your direction (use mock? try different model?)
```

I'll wait for your guidance before proceeding.

### When Done

```
✅ panner-ai M1.X merged to main. Branch deleted.
Next available: Ready for panner-ai M1.Y or any other project
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

- Code style (linting enforces it)
- Type safety (type checking enforces it)
- Test coverage (tests gate it)
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
❓ panner-ai M1.2 (Transport): Should concurrent request pool be 5 or 10?
Options:
  A) Pool size = 5 (conservative, safer)
  B) Pool size = 10 (faster, risk of rate limits)
  C) Configurable via suite.yaml (flexible but complex)
Recommendation: Option C (align with user config needs)
```

I'll propose and wait for your call. Never guess on design.

---

## Examples: Full Work Cycles

### Example 1: Simple Feature (Assay M1.1 — Config Parser)

```
You: Work on panner-ai M1.1

Me: 
✓ Routing: ~/.openclaw/workspaces/panner-ai/
✓ Pre-work checklist passed (main clean, no open PRs)
✓ Branch created: feature/M1.1-config-parser
✓ Code written: src/panner-ai/infrastructure/parser.py
✓ Tests added: tests/test_config_parser.py
✓ Build passing: ruff ✓ | pyright ✓ | pytest ✓
✓ PR created: #10 "M1.1: Config Parser"
```

You review & approve → I merge → Issue #2 closes automatically.

---

### Example 2: Cross-Workspace Workflow

```
You: Work on flow-ledger issue #42

Me:
✓ Routing: ~/.openclaw/workspaces/flow-ledger/
✓ Pre-work checklist passed
✓ Branch created: feature/issue-42-xxx
✓ Code written (C# / .NET stack per flow-ledger)
✓ Tests passing
✓ PR created: flow-ledger#N "Issue #42: ..."
```

You review → I merge → Back to ready state.

---

### Example 3: Batch Work (Multiple Projects)

```
You: Finish panner-ai M1.5, then flow-ledger #42, then review game-dev PR #7

Me:
✓ Assay M1.5 complete (PR #11) → merged
✓ Switch to flow-ledger, issue #42 started (branch: feature/...)
✓ Flow-ledger PR created & waiting review
✓ Switch to game-dev, PR #7 review complete
✓ All status updates provided
```

---

### Example 4: Blocked Work

```
You: Start panner-ai M1.4

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
⚠️ panner-ai M1.3 (Evaluators): Discovered that JSON schema validation needs recursive key checking
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
| 1. Route Project | Me | Project name (explicit or implicit) | Workspace path resolved |
| 2. Pick Issue | You | Issue number (M1.X, #Y, or project context) | "Got it, starting work" |
| 3. Pre-Check | Me | Issue details + workspace context | Blockers identified or clear to proceed |
| 4. Code & Test | Me | Acceptance criteria | Feature branch with passing tests |
| 5. PR | Me | Code + tests | PR #N ready for review |
| 6. Review | You | PR changes | Approved or revision requests |
| 7. Merge | Me | Approval | Main updated, issue closed |
| 8. Report | Me | Completion | Ready for next issue (any project) |

---

## Questions?

If you're unsure how to direct work, default to:

```
Work on {project} {issue}

or (if in that project's session)

Work on {issue}
```

I'll handle the rest. This document is your reference for what happens behind the scenes.

---

**Ash, Primary Orchestrator**  
All Workspaces (ash-orchestrator, panner-ai, flow-ledger, game-dev, orchestrators, future projects)  
Last Updated: 2026-08-30
