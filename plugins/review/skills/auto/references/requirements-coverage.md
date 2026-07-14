# Requirements-coverage Evaluation Checklist

Use this checklist to evaluate the changes against the spec in the **`## Spec`** section of your prompt. Ground
every conclusion in the spec text and in specific code evidence, not on the patch alone.

## What to report

- **Missing or partial** — requirements from the spec that the diff does not fully implement.
- **Scope creep** — behavior in the diff that no requirement asked for.
- **Implemented but wrong** — requirements that appear implemented but do not match the spec's intent.

Quote the spec line for each finding. If the **`## Spec`** section is empty or absent, report "no spec available" and stop.

## LSP focus for this axis

Build on the **`LSP baseline`** section of your prompt. Work **spec-first**, tracing reachability rather than contracts, using the `LSP Progressive Depth Code Analysis` framework from `/lsp-depth-guidance`:

- Start from the baseline's **Callers (representative)** column (trace whether the changed behavior is actually wired to its callers).
- For each requirement, use go-to-definition and find-references to confirm the required behavior is actually **implemented, reachable, and wired** — not dead or unreferenced code.
- Invert the map: flag any changed symbol in the baseline that **no requirement maps to** as candidate scope creep.
- Where a requirement spans multiple symbols, follow the call chain to confirm the full behavior path exists end to end.

For each finding, conclude one of: **confirmed issue**, **plausible risk**, or **no issue found**.

> Shared review rules (evidence, scope, deduplication) apply to this axis. See `<skill-directory>/references/review-rules.md`.
