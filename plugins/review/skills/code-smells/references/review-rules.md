# Code-Smells Review Rules

These rules govern how findings for the **code-smells** axis are grounded, scoped, filtered,
and counted. Apply them to every candidate finding after evaluation.

## Grounding & scope
- Review the change as a whole, including cross-symbol design intent.
- Ground conclusions on the shared LSP summary and repository-wide evidence, confirmed with
  the `LSP Progressive Depth Code Analysis` framework from the `/lsp-depth-guidance` skill —
  not on the patch alone and not on exhaustive exploration.
- Every smell is a judgement call reported as a suggestion, never a hard defect.

## Filtering (drives the two counts)
Every candidate finding starts in the **total** count. Drop a finding — moving it to `passed`
with the rule that filtered it — when any rule below applies:

- **Evidence filter** — Do not report speculative smells. Report only smells anchored to a
  quoted hunk with a concrete symbol/line. Drop anything you cannot quote.
- **Tooling filter** — Drop anything `.editorconfig`, StyleCop, or SonarQube already enforces.
  This axis is about design smells, not formatting or analyzer-covered style.
- **Scope filter** — Drop smells outside the changed lines and their direct impact.
- **Dedup filter** — Treat existing review comments as already-covered context. Drop smells
  that match an existing comment on `file_path` + `line_number` + smell; do not restate them.

## Counting
- `candidates_total` — all candidate smell findings before filtering.
- `filtered_out` — candidates dropped by the filters above.
- `after_filter` — candidates that survived as violations (`candidates_total - filtered_out`).
- `passed` — smells checked with no match, plus the filtered-out candidates.
