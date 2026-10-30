# Reproduce Playbook

**Strategy:** depth. Applied on top of a kind; drives one failure to root cause.

**Trigger:** A test fails or is flaky. Get it red reliably, find the root cause, prove it green on the same surface.

## Steps

1. **Pin the failure.** Collect test name, environment, failing output (assertion / exception / log). From CI → pull its report. **Done when:** exact test + first error line recorded.
2. **Reproduce red** at the lowest SKILL.md ladder rung that can show it: [component](../kinds/component.md) (DB, then cloud) → [functional-slice](../kinds/functional-slice.md) (mock, in-process, real cloud) → [local-runtime](../kinds/local-runtime.md) (REST, then GUI). No test shows it → update or add one at that rung; behavior unknown → [experiment](../kinds/experiment.md) first. Narrowest filter. **Done when:** observed red with the same error; rung + reason for skipped rungs recorded.
3. **Flaky → measure.** Run the single test N times (start 5–10) with the same filter; record pass/fail count and differing errors. Vary one factor at a time (parallelism, ordering, timing, environment). **Done when:** failure rate + the factor that changes it recorded, or "not reproducible in N runs" with evidence.
4. **Root cause.** 2–3 hypotheses; eliminate with runtime evidence (logs, traces, state in mock/DB, cloud listing). Distinguish product bug vs test bug (shared state, ordering, timeouts, leaked resources, eventual consistency). **Done when:** one hypothesis survives with evidence.
5. **Optional challenge.** Fix crosses a boundary, or root cause contested → *run `architect` interrogate to adversarially attack the change before code*. **Done when:** run, or skipped with one-line reason.
6. **Fix + verify green** with the same command and filter as step 2. Flaky → repeat the step 3 run count; all pass. **Done when:** green summary read; flaky pass rate N/N.
7. **Neighbors.** Run the test's area filter once to catch collateral breakage. **Done when:** area summary read.

## Key Rule

No fix without red first. Same surface, same filter, same run count for red and green; "passed once" does not prove a flaky fix.
