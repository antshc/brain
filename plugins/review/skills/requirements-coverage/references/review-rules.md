# Requirements-Coverage Review Rules

These rules govern how findings for the **requirements-coverage** axis are grounded, scoped,
filtered, and counted. Apply them to every candidate finding after evaluation.

## Grounding & scope
- Judge the diff only against the spec supplied in the input payload. Do not invent requirements.
- Every finding must quote the exact spec line (or, for scope creep, the diff hunk plus the
  absence of any spec line requesting it).
- Confirm wiring with the shared LSP summary and the `LSP Progressive Depth Code Analysis`
  framework from the `/lsp-depth-guidance` skill before concluding a requirement is missing.

## Filtering (drives the two counts)
Every candidate finding starts in the **total** count. Drop a finding — moving it to `passed`
with the rule that filtered it — when any rule below applies:

- **Spec-anchor filter** — Do not report speculative gaps. Report only findings anchored to a
  quoted spec line and specific code evidence. Drop anything you cannot anchor.
- **Scope filter** — Drop findings about behavior outside this PR's stated scope.
- **Dedup filter** — Treat existing review comments as already-covered context. Drop findings
  that match an existing comment on `file_path` + `line_number` + requirement; do not restate them.

## Counting
- `candidates_total` — all candidate findings before filtering.
- `filtered_out` — candidates dropped by the filters above.
- `after_filter` — candidates that survived as violations (`candidates_total - filtered_out`).
- `passed` — requirements confirmed implemented correctly, plus the filtered-out candidates.
