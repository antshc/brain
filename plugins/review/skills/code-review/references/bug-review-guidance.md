# Bug review

Follow the shared contract; return `AXIS: bugs`. Review the entire selected diff and affected behavior; continue after the first finding.

## Inspection

- Correctness: input/state validity, null/empty/boundary cases, invariants, state transitions, cross-symbol contracts and affected callers.
- Reliability: exception propagation, fallbacks, retries/idempotency, cancellation, async tasks, races/synchronization, resource ownership/disposal, transaction boundaries, timeouts and bounded work.
- Compatibility: public interfaces, serialized/persisted formats, defaults, migrations, mixed versions, DI/config activation and deployment behavior.
- Security: authentication/authorization, input validation, secrets, trust boundaries and data exposure.
- Performance: demonstrated material hot-path, I/O/query, allocation or work-amplification regressions.

## Evidence gate

Report only when all hold: introduced by this diff; concrete triggering input/state/environment/path; code evidence demonstrates incorrect behavior and impact; author would likely fix it. Compare base behavior, inspect relevant guards, callers, contracts and tests. Trace beyond changed lines as needed; missing tests alone do not prove a defect.

Exclude speculation, unrelated pre-existing bugs, intentional changes without demonstrated defects, style and duplicate root causes. Keep unsupported candidates out of findings. When missing context prevents required coverage, return the shared failure object with unchecked scope; never return `[]` as a substitute for incomplete review. Do not claim checks ran unless executed. Use only authorized, safe checks; do not modify source or external state.

## Comment format

`[P0–P3] Imperative title` followed by one concise paragraph: trigger → incorrect behavior → impact → smallest correction. Cite exact symbols/code evidence; anchor the smallest relevant changed right-side line. One actionable defect per comment.

- P0: universal critical failure/release blocker, independent of special inputs.
- P1: urgent material defect.
- P2: ordinary actionable defect.
- P3: lower-impact defect worth fixing.

Return every qualifying net-new defect, highest priority first; no five-finding limit. Return `[]` only after complete review with no qualifying net-new findings. Quality/design suggestions belong to other axes.
