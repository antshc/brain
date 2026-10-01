---
description: Diagnose and fix hard bugs and performance regressions — establish the root cause, lock it with a regression test, apply the fix, verify, and clean up.
name: diagnosing-bugs
argument-hint: "{{bugDescription}}"
---
# Diagnosing Bugs

Root cause first, fix second.

## Root cause

Run `diagnosing-root-cause` for `{{bugDescription}}`.

Use the same shared hypothesis log:
`repository root/docs/tmp/{{bugSlug}}/diagnosis.md`.

Do not duplicate root-cause investigation logic in this skill. Continue only after a confirmed root cause is returned.

## Fix + regression test

Write the regression test before the fix when a correct test seam exists.

A correct seam MUST exercise the real bug pattern as it occurs at the relevant boundary/call path.

1. Turn the minimal repro into a failing regression test.
2. Observe the failure.
3. Apply the fix.
4. Observe the test pass.
5. Re-run the original un-minimised repro.

If no correct seam exists, record that as a finding in the user-facing result; do not create a misleading shallow test.

## Shared log

The shared diagnosis log remains hypothesis-only.

MUST NOT write tests, fixes, cleanup, phase state, artifacts, or commands to it.

If fixing reveals a new causal hypothesis that must be checked, verify it and append it using `diagnosis-session-log`. Otherwise leave the log unchanged.

## Cleanup

Before declaring done:
- original repro no longer reproduces;
- regression test passes, or missing seam is explicitly stated;
- temporary debug instrumentation removed;
- throwaway prototypes removed or clearly isolated;
- relevant focused tests pass.

## Output

Return:
- confirmed root cause;
- fix summary;
- regression-test result or missing-seam finding;
- verification of the original scenario;
- shared hypothesis log path.

Do not persist a root-cause summary unless an explicit handoff/persistence workflow is invoked.
