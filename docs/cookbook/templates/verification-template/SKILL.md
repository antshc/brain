---
name: verification-template
description: Verifies completed features, integrations, and regression fixes against exit criteria and real artifacts, with direct evidence and a closing completeness sweep.
---

<!-- @: Copy into a concrete skill folder; rename folder and frontmatter name, then replace all task placeholders. -->

# Verification

## Exit criteria
- Contract: {{contract|Required observable outcomes and boundaries}}
1. Map each outcome to a real check. *Done when* every criterion has a testable observation.

## Check matrix
- {{checks|Criterion, input, expected output, actual output, result}}
2. Test consumer-visible and failure paths; capture evidence. *Done when* expected and observed results are recorded.
- MUST NOT substitute compile success, self-report, or mocked behavior for a required live result.

## Evidence and exceptions
- {{evidence|Logs, captured output, actual artifacts, source paths}}
- {{unrun|Failed, blocked, unavailable, or deferred checks with reason}}
- MUST NOT report an unrun guard as passing.

## Completeness sweep
3. Last, re-read the task and account for every explicit and implied obligation. *Done when* no unverified scope is hidden.
- {{coverage|Requirement-to-evidence mapping and uncovered scope}}

## Completion criteria
- Every exit criterion has passing evidence or a clearly reported failure or blocker.

## Related recipe
- [Verification, exit criteria, completeness sweep](../../verification-exit-criteria-completeness-sweep.md)
