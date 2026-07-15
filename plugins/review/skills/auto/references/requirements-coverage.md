# Requirements-coverage Evaluation Checklist

Use this checklist to evaluate the changes against the spec in the **`## Spec`** section of your prompt. Ground
every conclusion in the spec text and in specific code evidence, not on the patch alone.

## What to report

- **Missing or partial** — requirements from the spec that the diff does not fully implement.
- **Scope creep** — behavior in the diff that no requirement asked for.
- **Implemented but wrong** — requirements that appear implemented but do not match the spec's intent.

Quote the spec line for each finding. If the **`## Spec`** section is empty or absent, report "no spec available" and stop.

## LSP workflow for this axis

This axis owns its LSP navigation end to end — there is no shared baseline. LSP analysis is mandatory; `grep`, `view`, and `bash` are NOT substitutes. Work **spec-first**, tracing **reachability and wiring** rather than contracts.

**Availability check first.** Confirm LSP responds (try `hover` or `documentSymbol` on a changed file). If it fails, build the project (see `Readme.md` / `ARCHITECTURE.md`) and retry; if it still fails, say so and fall back to `grep`, `view`, and `bash`.

**Baseline (do this first).** `documentSymbol` to enumerate the changed symbols, then one `findReferences` sweep per symbol to see whether the changed behavior is actually wired to callers. Use this map as the spine for the reachability checks below.

**Trace each requirement.**

- **Implemented & reachable** — for each requirement, `goToDefinition` + `findReferences` to confirm the required behavior exists and is referenced, not dead or unreferenced code.
- **Scope creep** — invert the map: flag any changed symbol that **no requirement maps to** as candidate scope creep.
- **End-to-end path** — where a requirement spans multiple symbols, follow `outgoingCalls`/`incomingCalls` to confirm the full behavior path exists from entry point to effect.

**Depth rule.** Trace only far enough to confirm each requirement is implemented, reachable, and wired; stop once reachability is established. Prefer representative call paths over exhaustive expansion of the call graph.

For each finding, conclude one of: **confirmed issue**, **plausible risk**, or **no issue found**.

> Shared review rules (evidence, scope, deduplication) apply to this axis. See `<skill-directory>/references/review-rules.md`.
