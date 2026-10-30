# Functional Slice Playbook

**Kind:** integration testing framework run. Ladder rungs 3–5. The test project starts and owns its environment (mock / fake config, in-process compose, real cloud) and asserts behavior through the app's public boundary (REST / API). Not [local-runtime](local-runtime.md): no separately started local app instance, no manual driving.

**Trigger:** Behavior spans components end to end through the public API, and a [component](component.md) test cannot show it. Or the request names functional-slice tests.

## Steps

1. **Pick environment** from `suites.environments`, lowest first; climb only when the lower one hides the behavior:
   - **mock / fake config** (rung 3): fast, no cloud.
   - **in-process / real SDK** (rung 4): framework hosts the app, real SDK calls.
   - **real cloud** (rung 5), two variants, as the repo supports:
     - **creates real instance:** E2E test provisions the app from an image / artifact in the dev account, runs, tears down.
     - **targets real deployment:** E2E test points at an existing deployed instance (URL / endpoint config).
     Real cloud → follow [cloud.md](../../references/cloud.md) steps 1–3 first.
   **Done when:** environment + selector (env var / flag / config) cited.
2. **Preflight.** Run `suites.preflight` (container daemon up, required artifacts built; cloud inputs covered by cloud.md). **Done when:** every check prints OK.
3. **Filter.** Narrowest `suites.filter`: one test → ticket/trait → area. No test shows the problem → update or add one in the suite, reusing its fixtures. **Done when:** filter string written out.
4. **Run.** From `suites.runFrom`, set the environment selector, run `suites.run`. Startup >2 min or real cloud → background + monitor. **Done when:** process exited.
5. **Read summary.** Total / passed / failed / skipped from console or `suites.results`. Failures → test name + first assertion/exception line. **Done when:** numbers reported.
6. **Tear down** containers left by the framework; real cloud → [cloud.md](../../references/cloud.md) step 5. **Done when:** none left, or kept by request / reported.

## Key Rule

Assertions live in the test project. Prove with the framework's summary, not with manual pokes at the environment.
