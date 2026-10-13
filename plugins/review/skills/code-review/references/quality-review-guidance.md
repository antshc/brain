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

### Compatibility
- **Backward compatibility**: serialized shapes and public contracts for existing consumers.
- **Runtime wiring**: DI/config activation only where runtime behavior may break.

### Performance
- **Material impact**: hot paths, I/O patterns, allocations, query shape, work amplification.

### Testability
- **Coverage**: changed behavior and uncovered high-risk correctness or compatibility scenarios.

For each area, conclude internally: confirmed issue, evidence-backed plausible risk, or no issue found. Emit only actionable findings under the shared contract.

## LSP workflow

1. Enumerate changed symbols: types, methods, properties, fields, interfaces, records, constructors. Keep the baseline shallow.
2. Deepen on changed contracts: find references and read 3-5 representative high-risk callers; resolve implementations/overrides for changed interfaces or abstracts; confirm callers' assumptions and substitutability.
3. Trace incoming/outgoing calls for changed thrown/returned/error paths, state transitions, and shared-mutable or async state into consumers. Stop once contract impact is clear.

Perform caller and implementation checks for every changed contract. Deepen call-path tracing only for newly introduced nullability, changed thrown/returned/error behavior, or shared-mutable/async state. Stay at the contract snapshot for body-only changes without those risks; do not expand the full call graph or read every reference.

## Comment format

Return each `REVIEW_COMMENT` as a posting-ready body: `issue → impact → fix`.

- One issue; name the exact symbol or code path and triggering input, state, or execution condition.
- Explain the observable correctness, reliability, compatibility, performance, or testability impact in one sentence. Distinguish confirmed behavior from a conditional risk; state the evidence-backed condition.
- Suggest the smallest viable fix; for coverage gaps, name the missing scenario and expected behavior.
- Start with the issue, without classification labels or prefixes (`suggest`, `suggestion`, `nit`, `bug`). Keep only essential context; remove praise, repetition, hedging, and background.