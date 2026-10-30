# Regression Playbook

**Strategy:** breadth. Applied on top of a kind; answers "what changed".

**Trigger:** Run an area, category, or full integration suite before merge or release, or after a broad change.

## Steps

1. **Scope.** Map changed paths to test projects via the repo's source → test trigger map if documented; else run the area filter covering the change. **Done when:** project list + filter written.
2. **Baseline (optional).** Need to tell new failures from known ones → run the same filter on the base branch, or take the last CI report. **Done when:** baseline failures listed, or skipped.
3. **Run bottom-up the SKILL.md ladder.** [component](../kinds/component.md) tests for changed accessors (DB emulator; cloud only when asked) → [functional-slice](../kinds/functional-slice.md) area filter on mock, excluding cleanup / destructive categories → in-process / real cloud only when asked → [local-runtime](../kinds/local-runtime.md) scenario sets only for user-visible flows (REST, then GUI). Gap in coverage → update or add a test at the lowest rung. **Done when:** summary read per rung run.
4. **Triage failures.** Each failure → new / known (baseline) / flaky (re-run once in isolation). Do not fix inside this playbook; new real failures → [reproduce](reproduce.md). **Done when:** every failure classified.
5. **Report.** Totals, delta vs baseline, classified failure list, results path. **Done when:** reported.

## Key Rule

A regression run answers "what changed", not "is it green". Report the delta against a baseline, and classify every failure before calling it done.
