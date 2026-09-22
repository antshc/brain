# Logic Prototype

Use for pure business logic, state transitions, state machines, reducers, data shapes, and transformations.

## Build

1. State the question and cases that decide it.
2. Use the repository's language/runtime.
3. Isolate the behavior in a small pure type/module:
   - reducer
   - state machine
   - pure functions over records/DTOs
   - stateful class/module only when internal state is part of the question
4. Keep I/O outside the logic.
5. Wrap it with the smallest runnable driver:
   - console/CLI app by default
   - standalone HTML when non-developers need to explore it
6. Include the happy path, important edge case, and invalid transition/action when relevant.
7. Print/render the full relevant state after each action.

## Constraints

- Keep state in memory unless persistence is being evaluated.
- Do not call real SDKs, APIs, brokers, or databases; use [INTEGRATION.md](INTEGRATION.md).
- Do not add unrelated tests or abstractions.
- Keep the validated logic portable; treat the driver as throwaway.
