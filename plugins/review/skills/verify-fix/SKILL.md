---
name: verify-fix
description: >-
  Verify bug fixes with executable regression evidence. Use for 'verify this fix', regression-safety review, 'blast radius / what could this change break', or 'assess tests / test coverage gaps'.
---

# Verify fix

## Inputs and routing

Accept a diff, commit, branch, local change, or PR checkout; optional explicit form: `verify-fix <full|impact|assess-tests> <target>`. Infer mode from clear intent; no flag required. Ask when target, comparison baseline, or conflicting mode intent is ambiguous.

| Intent | Mode | Work |
|---|---|---|
| Verify this fix; review fix regressions | `full` (default) | Correctness, impact, test assessment, missing tests, execution, verdict |
| Blast radius; what else could break; explicit `impact` | `impact` | Impact investigation and critical proof only |
| Assess tests; missing regression tests; explicit `assess-tests` | `assess-tests` | Existing-test mapping and prioritized gaps only |

**MUST NOT** silently expand a focused mode into full verification. Resolve bundled paths from this skill's base directory; read each selected reference in full. No other skill is required.

## Constraints

- **MUST NOT** change production code in any mode. Report source defects to the implementer. Add/update persistent tests only in `full` or on explicit request.
- `impact` permits safe disposable proof harnesses; `assess-tests` is read-only by default and permits only narrowly necessary diagnostic test runs, disclosed in the report. Neither runs a broad test campaign.
- **MUST** preserve unrelated dirty worktree changes. Inspect status before work; use isolated temporary worktrees for baseline comparisons. Never reset/clean the user's checkout.
- **MUST NOT** post PR comments, commit, push, or deploy merely to produce evidence. Use authorized safe checks; report blocked unsafe or production-impacting commands instead of executing them without authorization.
- **MUST** redact secrets, credentials, and customer data from captured evidence. Use environment variables for credentials; quote only signal-bearing output.
- **MUST** distinguish intended behavior changes from regressions. Protect pre-existing correct behavior, not known incorrect behavior.

## Scope and baseline

Identify repository instructions, target/head, pre-fix baseline, original bug/repro if available, changed paths, affected behavior, and test entry points. Pin commit IDs for committed targets; record local diff/state for uncommitted targets. For PRs, read title/body and commits through available read-only GitHub tooling; compare the checked-out head against the PR baseline. If the target changes during verification, reassess affected evidence before reporting.

When exploring the codebase, read `GLOSSARY.md` (if it exists) to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.

Done when scope and baseline are explicit, or ambiguity has been returned for clarification. Missing original-defect evidence is a stated limitation; do not invent it.

## Workflow

1. Resolve Inputs and routing, then Scope and baseline. Continue only for a resolved target.
2. `impact`: read and execute [Change impact analysis](references/impact-analysis.md); then go directly to Report. Done when critical facts have executed proof or are explicitly unproven.
3. `assess-tests`: read and execute [Test assessment](references/test-assessment.md); then go directly to Report. Done when relevant risks map to tests and prioritized gaps, without test-writing side effects.
4. `full`: execute Correctness review. Done when the fix mechanism and candidate defects are evidence-backed or identified as unchecked.
5. Read and execute [Change impact analysis](references/impact-analysis.md), then [Test assessment](references/test-assessment.md). Done when critical safety facts and risk-to-test gaps are recorded.
6. Read and execute [Bug reproduction](references/bug-reproduction.md). Add focused tests for the original defect and important behavior-preservation gaps where a correct seam exists. Done when red/green evidence, original-scenario results, and test changes exist, or missing evidence/seams are explicit.
7. Read and execute [Verification strategies](references/verification-strategies.md). Run relevant existing and new tests safely; expand proportionate to risk. Done when required checks have actual results or named blockers, and run-owned temporary artifacts are cleaned up or accounted for.
8. Report. Continue independent checks when one is blocked; never convert missing evidence into a pass.

## Correctness review

Trace how the existing fix addresses the reported root cause. Review the entire selected diff and affected behavior; continue after the first finding.

### Inspection

- Correctness: input/state validity, null/empty/boundary cases, invariants, state transitions, cross-symbol contracts and affected callers.
- Reliability: exception propagation, fallbacks, retries/idempotency, cancellation, async tasks, races/synchronization, resource ownership/disposal, transaction boundaries, timeouts and bounded work.
- Compatibility: public interfaces, serialized/persisted formats, defaults, migrations, mixed versions, DI/config activation and deployment behavior.
- Security: authentication/authorization, input validation, secrets, trust boundaries and data exposure.
- Performance: demonstrated material hot-path, I/O/query, allocation or work-amplification regressions.

### Evidence gate

Report only when all hold: introduced by this diff; concrete triggering input/state/environment/path; code evidence demonstrates incorrect behavior and impact; author would likely fix it. Compare base behavior, inspect relevant guards, callers, contracts and tests. Trace beyond changed lines as needed; missing tests alone do not prove a defect.

Exclude speculation, unrelated pre-existing bugs, intentional changes without demonstrated defects, style and duplicate root causes. Keep unsupported candidates out of findings. Record a defect the fix leaves unresolved separately from introduced regressions; compare the original symptom with fixed behavior. Cite real `file:line` evidence, including guards, callers, contracts, and tests beyond changed lines. Absence of a search match alone is not proof of safety.

Include every qualifying defect's trigger, incorrect behavior, and impact; order by impact. Missing context means unchecked scope, not a clean review. Do not claim checks ran unless executed.

## Report

Read [Verification report](references/verification-report.md) and return the selected mode's report. Full verdict: `FAILED` for a relevant confirmed defect/regression or required-check failure; otherwise `INCONCLUSIVE` for essential missing evidence or blocked execution; `VERIFIED` only when required checks passed and no critical unverified risk remains. Focused modes return assessments, not a full-verification verdict.

Run a closing completeness sweep: re-read the requested scope and map each obligation to evidence across code, tests, failure/compatibility paths, and residual limitations. Resolve uncovered work within the selected mode or report it explicitly. Never guarantee absence of every possible regression.

## Attribution

Impact method adapted from Cursor pstack's blast-radius; reproduction/regression-test instructions adapted from [Matt Pocock's diagnosing-bugs](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs). These are source attributions, not runtime dependencies.
