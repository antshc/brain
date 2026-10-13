# Quality-attributes review

Follow the parent's shared review contract. Review the complete change for this axis; return `AXIS: quality-attributes`.

## Quality attributes

### Correctness
- **Input and state validity**: edge cases, invalid state, nullability, missing guards.
- **Contract integrity**: callers, interfaces, overrides, and assumptions still hold.
- **Cross-symbol consistency**: invariants, state transitions, partial-failure behavior.

### Reliability
- **Error handling**: exceptions, fallbacks, retries, cancellation, propagation; no silent failures.
- **Async correctness**: task handling, cancellation propagation, synchronization.
- **Concurrency safety**: shared mutable state, thread safety, races.
- **Resource and operation lifecycle**: ownership, cleanup on success, failure, and cancellation; transaction boundaries; retry idempotency; timeouts and bounded work.

### Compatibility
- **Backward compatibility**: serialized shapes and public contracts for existing consumers.
- **Boundary compatibility**: external consumers, persisted formats, defaults, migrations, and mixed-version behavior where relevant. Inspect schemas, configuration, and contract tests beyond LSP references.
- **Runtime wiring**: DI/config activation only where runtime behavior may break.

### Performance
- **Material impact**: hot paths, I/O patterns, allocations, query shape, work amplification.

### Testability
- **Coverage**: report gaps only for specific changed, high-risk behavior with a stated expected result. Include tests for an already reported defect in that finding's fix, not as a separate issue.

For each area, conclude internally: confirmed issue, evidence-backed plausible risk, or no issue found. Emit only actionable findings under the shared contract.

For each finding, connect changed behavior to a supported triggering condition and observable impact. Check relevant guards and handling before reporting; exclude unrelated pre-existing issues.

## Investigation guidance

Assess changed contracts and behavior, including body-only changes with downstream effects. Inspect relevant callers, implementations, and runtime boundaries to establish triggering conditions and impact. Sample representative paths; expand where assumptions or failure modes differ.

## Comment format

Return each `REVIEW_COMMENT` as a posting-ready body: `issue → impact → fix`.

- One issue; name the exact symbol or code path and triggering input, state, or execution condition.
- Explain the observable correctness, reliability, compatibility, performance, or testability impact in one sentence. Distinguish confirmed behavior from a conditional risk; state the evidence-backed condition.
- Suggest the smallest viable fix; for coverage gaps, name the missing scenario and expected behavior.
- Start with the issue, without classification labels or prefixes (`suggest`, `suggestion`, `nit`, `bug`). Keep only essential context; remove praise, repetition, hedging, and background.