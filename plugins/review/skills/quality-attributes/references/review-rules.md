# Quality-Attributes Review Rules

These rules govern how findings for the **quality-attributes** axis are grounded, scoped,
filtered, and counted. Apply them to every candidate finding after evaluation.

## Grounding & scope
- Review the change as a whole, including cross-symbol behavior and likely design intent.
- Ground conclusions on the shared LSP summary and repository-wide evidence, confirmed with
  the `LSP Progressive Depth Code Analysis` framework from the `/lsp-depth-guidance` skill —
  not on the patch alone and not on exhaustive exploration.

## Filtering (drives the two counts)
Every candidate finding starts in the **total** count. Drop a finding — moving it to `passed`
with the rule that filtered it — when any rule below applies:

- **Evidence filter** — Do not report speculative issues. Report only findings supported by
  specific code evidence. Drop anything not anchored to a concrete symbol/line.
- **Scope filter** — Drop findings outside the changed lines and their direct impact.
- **Tooling filter** — Drop anything CI already enforces (analyzers, style, formatting).
- **Dedup filter** — Treat existing review comments as already-covered context. Drop findings
  that match an existing comment on `file_path` + `line_number` + area; do not restate them.

## Counting
- `candidates_total` — all candidate findings before filtering.
- `filtered_out` — candidates dropped by the filters above.
- `after_filter` — candidates that survived as violations (`candidates_total - filtered_out`).
- `passed` — checklist items concluded **no issue found**, plus the filtered-out candidates.
