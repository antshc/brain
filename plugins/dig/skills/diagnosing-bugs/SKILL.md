---
description: Use when asked to fix, repair, or debug-and-fix a hard bug — confirms the root cause, writes a regression test at the correct seam, applies the fix, verifies, and cleans up.
name: diagnosing-bugs
argument-hint: "{{bugDescription}}"
---
# Diagnosing Bugs

Root cause first, fix second.

## Root cause

*Run `diagnosing-root-cause` skill to run the diagnosis loop on `{{bugDescription}}` — hard bug: broken, throwing, or failing.*

*Use `diagnosis-session-log` skill to reuse the same shared hypothesis log (`logPath`) of checked hypotheses, verification, and evidence.*

Require from root cause: `loopCmd :=` red-capable command from Phase 1; `minRepro :=` minimised scenario from Phase 2.

Do not duplicate root-cause investigation logic in this skill.

**Gate:** no `confirmed` hypothesis in `logPath` → stop; return the blocker and what was tried. Apply no fix.

## Phase 6: Fix + regression test

Fix the confirmed mechanism, not the symptom; minimal diff.

Write the regression test **before the fix**, but only if there is a **correct seam** for it.

A correct seam is one where the test exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (single-caller test when the bug needs multiple callers, unit test that can't replicate the chain that triggered the bug), a regression test there gives false confidence.

**If no correct seam exists, that itself is the finding.** Note it. The codebase architecture is preventing the bug from being locked down. Report it in Output as the missing-seam finding; apply the fix without a test and verify via `loopCmd`.

If a correct seam exists:

1. Turn `minRepro` into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run `loopCmd` against the original (un-minimised) scenario.

## Phase 7: Cleanup

Required before declaring done:

- [ ] Original (un-minimised) repro no longer reproduces (re-run `loopCmd`)
- [ ] Regression test passes (or absence of seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed (`grep` the prefix)
- [ ] Throwaway prototypes deleted (or moved to a clearly-marked debug location)
- [ ] The hypothesis that turned out correct is stated in the commit / PR message, so the next debugger learns

## Output

Return:
- confirmed root cause;
- The hypothesis that turned out correct is stated for the commit / PR message, so the next debugger learns
- fix summary;
- regression-test result or missing-seam finding;
- verification of the original scenario;
- `logPath` shared hypothesis log path.
