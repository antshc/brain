# Component Playbook

**Kind:** integration test of one accessor/adapter against its real dependency. Ladder rungs 1–2: database (local emulator) first, then cloud SDK/proxy (dev account).

**Trigger:** Problem or change sits in data access, persistence, queries, serialization, or a cloud SDK call. Default first rung for any reproduce or regression.

## Steps

1. **Locate the seam.** Find the accessor/repository/proxy that owns the behavior and its integration-test project (Discover suites with `level` component; repo source → test map if documented). **Done when:** class under test + test project cited.
2. **Pick dependency.** Database emulator first. Cloud only when the behavior depends on the real cloud API (IAM, quota, SDK error, eventual consistency) → [cloud.md](../../references/cloud.md) steps 1–3. One-off cloud question, no test needed → [experiment](experiment.md). **Done when:** dependency + reason written.
3. **Find or write the test.** Existing test covers it → use it. Else update the nearest test or add one next to it, reusing the project's fixtures, fakes, and test data; assert the literal expected value. **Done when:** test name + assertion written.
4. **Preflight.** Container daemon up for the emulator; cloud → accounts file / creds per `suites.preflight`. **Done when:** checks OK.
5. **Run.** From `suites.runFrom`, narrowest filter on the test project, excluding cleanup categories. **Done when:** process exited and summary read.
6. **Clean up.** Emulator containers stopped by the fixture; cloud → [cloud.md](../../references/cloud.md) step 5. **Done when:** none left, or reported.

## Key Rule

Smallest seam that shows the behavior. A failing component test is the cheapest durable reproduction; keep it as the regression guard.
