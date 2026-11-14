# Logic

Route procedure for pure business logic, state transitions, state machines, reducers, data shapes and transformations.

## Workflow

1. **Cases.** State the cases that decide the claim: happy path, deciding edge case, invalid transition/action when relevant. *Done when* each case names its expected observation.
2. **Build.** Isolate the behavior in the repository's language/runtime as a small pure type/module: reducer, state machine, pure functions over records/DTOs; a stateful class/module only when internal state is part of the claim. Keep I/O outside the logic. Wrap it with the smallest runnable driver: console/CLI app by default, standalone HTML when non-developers need to explore it. *Done when* one command runs every case.
3. **Run.** Execute the driver once; print/render the full relevant state after each action. *Done when* actual output per case is captured against its expected observation.

Return control for *Rerun*.

## Constraints

- Keep state in memory unless persistence is the claim.
- Do not call real SDKs, APIs, brokers or databases; a real boundary routes to Integration.
- Do not add unrelated tests or abstractions.
- Keep the validated logic portable; treat the driver as throwaway.
