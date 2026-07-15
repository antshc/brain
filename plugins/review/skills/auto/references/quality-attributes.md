# Correctness Evaluation Checklist

Use this checklist to evaluate the changes. Ground
every conclusion using the LSP analysis and in specific code evidence, not on the patch alone.

## Quality attributes

### Correctness
- **Input & state validity** — does the code handle edge cases, invalid state, nullability, and missing guards?
- **Contract integrity** — do callers, interfaces, overrides, and assumptions still hold, or does the change break them?
- **Cross-symbol consistency** — do invariants, state transitions, and partial-failure behavior stay consistent across symbols?

### Reliability
- **Error handling** — is exception handling, fallback behavior, retries, cancellation, and error propagation correct, with no silent failures?
- **Async correctness** — is task handling, cancellation propagation, and synchronization correct across async flows?
- **Concurrency safety** — is shared mutable state thread-safe and free of race conditions?

### Compatibility
- **Backward compatibility** — do serialized shapes and public contracts stay compatible for existing callers or consumers?
- **Runtime wiring** — does DI/config/runtime wiring still activate correctly (only when activation or runtime behavior may break)?

### Performance
- **Performance impact** — does the change materially affect hot paths, I/O patterns, allocations, query shape, or work amplification?

### Testability
- **Test coverage** — do existing tests cover the changed behavior, and does any uncovered high-risk scenario matter to correctness or compatibility?

For each area, conclude one of: **confirmed issue**, **plausible risk**, or **no issue found**.

## LSP workflow for this axis

This axis owns its LSP navigation end to end — there is no shared baseline. LSP analysis is mandatory; `grep`, `view`, and `bash` are NOT substitutes. Trace **contracts** — whether callers, overrides, and error/async paths still hold after the change.

**Availability check first.** Confirm LSP responds (try `hover` or `documentSymbol` on a changed file). If it fails, build the project (see `Readme.md` / `ARCHITECTURE.md`) and retry; if it still fails, say so and fall back to `grep`, `view`, and `bash`.

**Baseline (do this first).** For every changed symbol: `documentSymbol` to enumerate the changed symbols, then `goToDefinition` + `hover` to snapshot each contract — signature, return type, generics, nullability, and modifiers — and decide whether the change altered the contract or only the body. Keep this shallow; deepen only where a contract changed.

**Deepen on contract changes.** For each symbol whose contract changed:

- **Dependents** — `findReferences` to enumerate callers, then read **3–5 representative callers** (not all) and confirm each still satisfies the new contract.
- **Polymorphism** — `goToImplementation` on changed interfaces/abstracts to resolve overrides and implementers; confirm substitutability still holds.
- **Behavior** — `incomingCalls`/`outgoingCalls` to trace changed thrown/returned/error paths, state transitions, and shared-mutable or async state into the callers that consume them.

**Depth rule.** Go deep (callers, implementers, call hierarchy) only on newly introduced nullability, changed thrown/returned/error behavior, or shared-mutable/async state. Stay at the contract snapshot where the change is body-only. Do not expand the full call graph or read every reference — prefer representative, high-risk paths and stop once the contract impact is clear.

> Shared review rules (evidence, scope, deduplication) apply to this axis. See `<skill-directory>/references/review-rules.md`.
