# Experiment Playbook

**Kind:** one uncertain technical question answered by observation, not a test run. Off the ladder: use at any rung when the task is "does / how does X behave", or when a test cannot be written before the behavior is known.

**Trigger:** "check whether", "does X", "how does Y behave", "prove", "try"; one-off cloud question at rung 2; unknown framework/runtime/UI behavior blocking a test.

## Steps

1. **State the question.** One question, assumption, success/observation criteria, out-of-scope. **Done when:** one-line question written.
2. **Pick the option** by uncertainty; combine when needed:

| Option | Uncertainty | Typical artifact |
| --- | --- | --- |
| logic | pure logic, state, transitions, data shape | small console / script |
| runtime | framework, hosting, middleware, DI, serializer, concurrency, container | minimal app, test host, compose |
| integration — local | SDK / REST / DB / broker against an emulator or local service | existing integration-test infra, `curl` |
| integration — cloud | real cloud API, IAM, quota, resource state | cloud CLI first; SDK test for client behavior |
| ui | visual / interaction behavior | existing frontend route |

   **Done when:** option(s) + artifact named.
3. **Cloud option** → [cloud.md](../../references/cloud.md) steps 1–3 before running. **Done when:** account verified (+ confirmed for writes).
4. **Run** — *run `experiment` to answer one uncertain technical question with a minimal throwaway experiment, observing actual behavior of the logic, runtime, SDK/API integration, cloud resource, or UI*; pass the question, option, and the Discover facts (stack, test infra, account). **Done when:** experiment skill reports Question / Method / Observation / Conclusion / Evidence / Cleanup.
5. **Clean up.** Throwaway code removed; cloud → [cloud.md](../../references/cloud.md) step 5. **Done when:** cleanup reported.
6. **Feed back.** Answer changes the plan → return to the ladder: write or update the test at the lowest rung that now can show the behavior. **Done when:** next rung named, or `none`.

## Key Rule

One question per experiment; a failed assumption is a valid result. Experiment code never becomes the test; the test is written afterwards on the ladder.
