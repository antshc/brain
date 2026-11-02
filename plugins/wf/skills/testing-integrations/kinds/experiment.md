# Experiment Playbook

**Kind:** one uncertain technical question answered by observation, not a test run. Off the ladder: use at any rung when the task is "does / how does X behave", or when a test cannot be written before the behavior is known.

**Trigger:** "check whether", "does X", "how does Y behave", "prove", "try"; one-off cloud question at rung 2; unknown framework/runtime/UI behavior blocking a test.

The `experiment` skill owns option, artifact, playbook, and throwaway cleanup; this kind only frames, guards cloud access, and feeds back to the ladder.

## Steps

1. **State the question.** One question, assumption, success/observation criteria, out-of-scope. **Done when:** one-line question written.
2. **Load the strategy.** Read `experiment` skill's Inputs and Workflow before starting; pick `@option` from its option map (`logic | runtime | integration-local | integration-cloud | ui`) only when Discover facts already decide it, else leave it to the skill. **Done when:** Inputs known and `@option` set or deferred.
3. **Cloud option** (`integration-cloud`) → **Cloud Safety** steps 1–3 before running. **Done when:** account verified (+ confirmed for writes).
4. **Run** — *run `experiment` skill to answer one uncertain technical question with a minimal throwaway experiment, observing actual behavior of the logic, runtime, SDK/API integration, cloud resource, or UI*, filling: `@question` and `@criteria` from step 1; `@option` from step 2; `@repoFacts` = the Discover `suites` rows for the boundary (`run`, `runFrom`, `environments`, `preflight`), stack, test infra, and verified `cloudAccount`; `@limits` = **Cloud Safety** limits. Rationale: passed Discover facts let the experiment skip re-discovery and search only gaps. **Done when:** experiment skill reports Question / Method / Observation / Conclusion / Evidence / Cleanup.
5. **Cloud cleanup.** Cloud → **Cloud Safety** step 5 against the skill's reported Cleanup. **Done when:** cleanup confirmed or `n/a`.
6. **Feed back.** Answer changes the plan → return to the ladder: write or update the test at the lowest rung that now can show the behavior. **Done when:** next rung named, or `none`.

## Key Rule

One question per experiment; a failed assumption is a valid result. Experiment code never becomes the test; the test is written afterwards on the ladder.
