---
name: index-docs
description: Own ARCHITECTURE.md's structural prose (Overview, Building blocks, and the Deployment View reference stub whose content comes from record-deployment-view), host ARCHITECTURE-FORMAT.md, and insert its missing section skeletons. Owns the generic trigger-generation, scan/match, and row-sync mechanic for any markdown table with a Trigger condition column (Services, Concepts, or custom), driven by caller-supplied table/row metadata rather than a fixed schema. Called by grill-design and the record-* skills. Does not create ARCHITECTURE.md and does not author its index rows' content.
---

# Index Docs

Own `ARCHITECTURE.md`'s structural prose and its two indexes (`Services`, `Crosscutting Concepts`) — the file itself is created by `bootstrap-docs`. Template: [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md).

## Rules

- **Shape, not steps.** `ARCHITECTURE.md` describes decomposition and the rules holding it together — not a spec, not a scratch pad, not a home for inlined backbone decisions. Step-by-step detail lives in code and linked Concepts.
- **Never batch.** Update `ARCHITECTURE.md` in the same change as the structure/layering shift it reflects. A stale architecture map is worse than none.
- **The owning skill authors its row.** A table row is authored directly by the skill that owns that record kind (`record-concept`, `record-service`) via **Sync index row** — never derived from the record file itself, and never hand-edited independently of it.

## Ensure section exists

Inputs: `{{sectionAnchor}}` (e.g. `Crosscutting Concepts`, the `Services` table under `Building blocks`); optionally `{{skeletonContent}}`.

1. If `{{sectionAnchor}}` already exists in `ARCHITECTURE.md`, do nothing.
2. Otherwise insert its skeleton — `{{skeletonContent}}` when the caller supplies one (custom tables), else the skeleton for that section from [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md) — at the position the template gives it.

## Generate trigger condition

Inputs: `{{recordContent}}`, `{{rowValues}}`, `{{domainGlossary}}`, `{{grillingContext}}`; optionally `{{tableMetadata}}`.

1. If the caller already has an authoritative Trigger condition value for this row (e.g. an existing cell being refined, not regenerated from scratch), return it unchanged unless the caller explicitly asks to refine it.
2. Extract entities, data shapes, behaviors, boundaries, interfaces, folders, change types, constraints.
3. Generate concise, comma-separated phrases in domain-specific language likely to arise during questioning.
4. Prefer high-signal phrases and real domain synonyms. Exclude generic phrases, title-only phrases, and the generation requirement itself.

Return one Trigger condition value. The caller writes it into the row via **Sync index row**.

## Scan and match

Inputs: `{{tableMetadata}}`, `{{touchedSurface}}`, `{{questioningContext}}`, `{{domainGlossary}}`. `{{tableMetadata}}` is the file/section boundary, headers, Trigger condition column, and row locator rules; for this file's own two tables it is implied — the caller passes only the table name (`Services`, `Crosscutting Concepts`). Callers supply the touched surface, questioning context, and glossary — never the table shape. `{{touchedSurface}}` may carry domain terms, file paths, or both; a caller that knows which files a change touches passes them, and one that only has terms passes terms.

1. Absent or empty table: no matches.
2. Absent Trigger condition column: table-contract error.
3. Read each row's Trigger condition cell; a blank cell never matches.
4. Split non-blank cells on commas; match each clause semantically against the touched surface and questioning context, using the glossary for domain terms and paraphrases.
5. Open the linked record's body only when its locator is supplied and resolvable. Having opened one, treat its cross-references (where the body names another record) as candidates and scan their rows too.
6. Report matched clauses and rationale for matches; checked clauses and rationale for non-matches.

## Sync index row

Inputs: `{{tableMetadata}}`, `{{rowMetadata}}`, `{{action}}` (`add`, `supersede`, `retire`). `{{tableMetadata}}` supplies the table boundary, headers, Trigger condition column, row locator rules. `{{rowMetadata}}` supplies row identity and explicit cell values, always caller-supplied — this skill never derives them from the record file itself.

1. `add`: append a row using the supplied headers and cell values.
2. `supersede`: update only the named cells in the located row.
3. `retire`: apply the caller's retirement marker to the located row.
4. Preserve unspecified cells, unknown columns, existing rows.
5. Apply the row change with the underlying record change. If metadata is missing or ambiguous, report it — do not guess.

Return the updated row or a concise synchronization report.
