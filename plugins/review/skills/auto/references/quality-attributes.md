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

> Shared review rules (evidence, scope, deduplication) apply to this axis. See `<skill-directory>/references/review-rules.md`.
