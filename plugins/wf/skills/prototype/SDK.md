# SDK Prototype

A throwaway integration test that answers "does this SDK call behave as I expect?" — the response shape, an error path, a pagination quirk — before the real module commits to it.

If the question is about a state model or data shape rather than a live call — wrong branch. Use [LOGIC.md](LOGIC.md).

## Placement and naming

Never a new ad-hoc project — place the test as a sibling to the production code it exercises, following the same naming convention the target repo already uses for its production namespaces:

- **Single-component** — a sibling `*.IntegrationTests` project/class named after the exact production namespace it targets. E.g. `Repository.IntegrationTests` for a repository/accessor wrapping an AWS call, or `Aws*.IntegrationTests` or `Azure*.IntegrationTests` for a compute layer.
- **Cross-component** — when the question spans more than one internal component, a test class under an `Areas/CrossComponents` folder inside the entry-point/gateway's own IntegrationTests project instead of a new project. E.g. `Api*.IntegrationTests`.

Either shape rarely hand-rolls a new HTTP client — it reuses whatever SDK client and fixture wiring the sibling `IntegrationTests` project already establishes.

## Process

1. State the question at the top of the test class: which call, and what you're checking about it (response shape, an error path, a limit, a pagination quirk).
2. Write the test using the existing integration-test conventions of the repo under prototyping — its client setup, its fixtures, its test base classes. Exercise the real SDK call; don't stub the boundary you're trying to learn about.
3. Assert on the actual response shape, not just "it didn't throw" — the assertions are the artifact; they're what later gets copied into real validation logic.
4. Run it. A failing assertion here is the answer, not a bug — it's telling you the SDK behaves differently than assumed.
5. Capture the answer and the prototype the way [SKILL.md](SKILL.md) describes: fold the validated call/shape into the real module (the response mapping, the error handling, the retry policy), then move the test itself onto the throwaway branch that keeps it as a primary source.
