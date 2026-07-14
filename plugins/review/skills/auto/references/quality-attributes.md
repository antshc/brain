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

## LSP focus for this axis

Build on the **`LSP baseline`** section of your prompt. For every symbol the baseline flags as a **contract change**, escalate to Level 2/3 using the `LSP Progressive Depth Code Analysis` framework from `/lsp-depth-guidance`:

- Start from the baseline's **Contract, Nullability, Overrides** columns (broken assumptions, missing guards, contract drift).
- **Dependents** — run find-references on the symbol; confirm every caller and implementer still satisfies the new contract.
- **Behavior** — trace changed return/thrown/error paths, state transitions, and side effects into the callers that consume them.
- **Polymorphism** — resolve overrides and interface implementations; confirm substitutability still holds.

Prioritize depth on newly introduced nullability, changed thrown/returned/error behavior, and shared-mutable or async state. Stay at Level 1 where the baseline shows a body-only change.

> Shared review rules (evidence, scope, deduplication) apply to this axis. See `<skill-directory>/references/review-rules.md`.
