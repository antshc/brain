# Tests gap

Map each behavior a change affects to the existing test that protects it, judge whether that test would really fail on a regression, and return prioritized gaps.

## Inputs

Accept a diff, commit, branch, local change, or PR; optional bug report or original defect. Ask when the target or comparison baseline is ambiguous.

## Constraints

- **MUST NOT** edit production code or tests. Recommend cases; write none.
- Read-only by default. Run a narrow diagnostic test only when needed to judge a claimed assertion; report its exact command and result. **MUST NOT** run the whole suite.
- **MUST** preserve unrelated dirty worktree changes; never reset/clean the user's checkout.
- **MUST NOT** post PR comments, commit, or push, or deploy.
- **MUST** redact secrets, credentials, and customer data from quoted evidence.

## Scope

Use the confirmed and plausible risks from Blast radius when the user requests both analyses. Identify repository instructions, target head, baseline, original defect if available, changed paths, affected observable behavior, and test entry points. Pin commit IDs for committed targets; record local diff state for uncommitted ones. For PRs, read title, body, and commits through read-only GitHub tooling and inspect the PR head, not the caller's branch. Read `GLOSSARY.md` (if it exists) and ADRs in the touched area.

Done when target, baseline, and affected behaviors are explicit, or ambiguity is returned for clarification. Missing original-defect evidence is a stated limitation; do not invent it.

## Steps

1. Locate existing tests for the original defect and affected observable behavior. Inspect fixtures, assertions, mocks, skips, and runner configuration; do not equate a filename or coverage percentage with protection. Done when each relevant behavior has an identified test or a recorded gap.
2. Map each risk to the existing test's real failure mechanism, assertion, and test level. A unit test that mocks away a failing boundary does not cover that boundary; a single-caller test does not cover a multi-caller failure. Check whether the asserted output would fail for the original defect and important regressions. Done when seam and assertion strength are explained with `file:line` evidence.
3. Separate intended behavior changes from behavior to preserve. Prioritize missing cases by likelihood and impact: original symptom, invariant/boundary cases, integration contracts, failure paths, cancellation/concurrency/idempotency where affected. Recommend the lowest test level that exercises the actual mechanism. Done when each gap names input/setup, observable expected result, test level, and priority; do not merely echo current implementation.
4. If no correct seam exists, report that limitation instead of recommending a shallow test. If tests cannot be inspected, report incomplete coverage and the inaccessible scope. Done when every limitation is recorded.

## Report

| Risk / behavior | Existing test and evidence | Seam / assertion quality | Gap, priority, recommended case and level |
|---|---|---|---|
| Concrete failure mechanism | Test identifier and `file:line`, or none found | Reaches mechanism and fails on wrong observable output, or limitation | Specific input → expected result, or no identified gap |

Recheck the pinned head before reporting when remote state may have changed. Follow the table with: scope and baseline inspected, any diagnostic command run with its result, and limitations. No gaps found means only the inspected risks have suitable tests, not that the change is verified.

## Completion criteria

- Every affected behavior appears in the table with a test citation or an explicit gap.
- Every gap names input/setup, expected observable result, test level, and priority.
- No test or production file was modified.
