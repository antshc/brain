---
name: review-fix
description: >-
  Review an implemented fix or change for downstream breakage and missing regression tests. Use for 'review this fix', 'blast radius', 'what could this break', 'assess tests', 'test coverage gaps', or 'are these tests enough'.
---

# Fix review

Review a change's indirect risks and whether existing tests would catch regressions. Route by the request; do not expand focused requests into the other analysis.

## Route

| Request | Load from this skill directory | Result |
|---|---|---|
| "Blast radius", "what could break", change-impact question | [Impact analysis](references/impact-analysis.md) | Confirmed and cleared risks, critical safety fact, executable proof or explicit unproven status |
| "Assess tests", "test gaps", "are these tests enough" | [Test assessment](references/test-assessment.md) | Risk-to-test map, assertion quality, prioritized missing cases |
| "Review this fix", regression-safety review, explicit both | Both references, impact first | Impact findings followed by test coverage against those risks |

Resolve the references relative to this `SKILL.md`, never the caller's working directory. **Read each selected reference completely.** A focused request runs only its selected procedure.

## Prepare scope

1. Accept a diff, commit, branch, local change, or PR; optional original defect. Identify repository instructions, target head, comparison baseline, changed paths, affected observable behavior, and relevant test entry points. Ask if target or baseline is ambiguous.
2. Pin committed refs to SHAs. For PRs, inspect the actual PR head and base, title, body, and commits rather than the caller's current branch. For local changes, record dirty-worktree state without altering it. Read `GLOSSARY.md` and relevant ADRs when present.
3. Execute the selected procedure. In combined mode, pass confirmed and plausible impact risks to the test assessment; distinguish proven defects from unproven assumptions and test gaps. Recheck the pinned head before reporting when remote state may have changed.

## Constraints

- **MUST NOT** edit tracked production code or existing tests, post PR comments, commit, push, or deploy. Preserve unrelated work; never reset or clean the user's checkout.
- Impact analysis may create a disposable script or test to execute real code; use an isolated, run-owned location and clean it afterward. Report exact command, output, and proof level. If safe execution is unavailable, mark the claim unproven.
- Test assessment is read-only; run only a narrow diagnostic test when needed to inspect an assertion. **MUST NOT** run the whole suite or create persistent tests.
- Redact secrets, credentials, and customer data. Distinguish source evidence, observed execution, and inference. Missing evidence is a limitation, never a pass.

## Report

- Impact only: follow *What to hand back* in the impact reference.
- Tests only: follow *Report* in the test-assessment reference.
- Combined: state scope and baseline; report what changed, critical safety fact and proof, confirmed/cleared/unproven risks, then the risk-to-test table and prioritized missing cases. Include commands, results, limits, and the cheapest next verification.
- Neither absent risks nor absent gaps means the entire fix is verified; qualify the inspected scope.

## Completion criteria

- All selected references ran; every affected behavior has a supported risk verdict or named uncertainty.
- Critical safety facts have executed evidence or are marked unproven; test findings identify assertions and concrete missing cases.
- No tracked code/test edits or remote mutations occurred; temporary proof artifacts are accounted for.
