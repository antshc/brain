# Test assessment

1. Locate existing tests for the original defect and affected observable behavior. Inspect fixtures, assertions, mocks, skips, and runner configuration; do not equate a filename or coverage percentage with protection. Done when each relevant behavior has an identified test or a recorded gap.
2. Map each risk to the existing test's real failure mechanism, assertion, and test level. A unit test that mocks away a failing boundary does not cover that boundary; a single-caller test does not cover a multi-caller failure. Check whether the asserted output would fail for the original defect and important regressions. Done when seam and assertion strength are explained with `file:line` evidence.
3. Separate intended behavior changes from behavior to preserve. Prioritize missing cases by likelihood and impact: original symptom, invariant/boundary cases, integration contracts, failure paths, cancellation/concurrency/idempotency where affected. Recommend the lowest test level that exercises the actual mechanism. Done when each gap names input/setup, observable expected result, test level, and priority; do not merely echo current implementation.
4. Return a concise mapping. If no correct seam exists, report that limitation instead of recommending a shallow test. No gaps found means only the inspected risks have suitable tests, not that the fix is verified. If tests cannot be inspected, report incomplete coverage and inaccessible scope.

| Risk / behavior | Existing test and evidence | Seam / assertion quality | Gap, priority, recommended case and level |
|---|---|---|---|
| Concrete failure mechanism | Test identifier and `file:line`, or none found | Reaches mechanism and fails on wrong observable output, or limitation | Specific input → expected result, or no identified gap |

In `assess-tests`, stop after the mapping. Do not edit tests or run the entire suite. Run a narrow diagnostic test only when necessary to judge a claimed assertion; report its exact command and result. In `full`, return the gaps to Workflow for safeguards and execution.
