# Logic

Route procedure for pure business logic, state transitions, state machines, reducers, data shapes and transformations.

## Workflow

1. **Cases.** State the cases that decide the claim: happy path, deciding edge case, invalid transition/action when relevant. *Done when* each case names its expected observation.
2. **Select.** Prefer existing focused tests invoking the actual implementation. No suitable test → add the smallest test or runnable driver in the repository's language/runtime calling that implementation. For a proposed algorithm with no implementation, build a minimal prototype and scope conclusions to it. Keep I/O outside pure logic. *Done when* one command exercises every deciding case against the named target, or a blocker is recorded.
3. **Run.** Execute the selected command; assert expected behavior and capture actual output per case, including relevant state after each action. *Done when* every deciding case actually executed with an assertion and captured result.

Return control for *Rerun*.

## Constraints

- Keep state in memory unless persistence is the claim.
- Do not call real SDKs, APIs, brokers or databases; a real boundary routes to Integration.
- Do not add unrelated tests or abstractions.
- A copied or rewritten model cannot establish behavior of existing production logic; invoke the actual implementation.
- Treat new drivers and prototypes as proof artifacts; keep candidate fixes separate.
