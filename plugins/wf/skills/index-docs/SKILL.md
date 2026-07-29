---
name: index-docs
description: Own ARCHITECTURE.md's structural prose (Overview, Building blocks, Deployment View), host ARCHITECTURE-FORMAT.md, insert missing section skeletons into ARCHITECTURE.md, and own the generic trigger-generation, scan/match, and row-sync mechanic for any markdown table with a Trigger condition column (Services, ADR, Concept, or custom), driven by caller-supplied table/row metadata rather than a fixed schema. Called by grill-design and the record-* skills. Does not create ARCHITECTURE.md and does not author its index rows' content.
---

# Index Docs

Own `ARCHITECTURE.md`'s structural prose and the three indexes it hosts (`Services`,
`Architecture Decision Records`, `Crosscutting Concepts`).
Template: [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md).

## Inline-update discipline

Update `ARCHITECTURE.md` in the same change as the structure/layering shift it reflects — never batch. A stale architecture map is worse than none.

## Keep it in its lane

`ARCHITECTURE.md` describes **shape and rules**, not implementation detail — not a spec, not a scratch pad, not a place for inlined backbone decisions. Step-by-step detail lives in code and linked Concepts.

## Existence and sections

`bootstrap-docs` mandatorily creates `ARCHITECTURE.md` with its required sections only. Everything inside the file is this skill's: the structural prose, the three indexes, and the section skeletons.

## Ensure section exists

Inputs: `{{sectionAnchor}}` (e.g. `Architecture Decision Records`, `Crosscutting Concepts`, the `Services` table under `Building blocks`); optionally `{{skeletonContent}}`.

1. If `{{sectionAnchor}}` already exists in `ARCHITECTURE.md`, do nothing.
2. Otherwise insert its skeleton — `{{skeletonContent}}` when the caller supplies one (custom tables), else the skeleton for that section from [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md) — at the position the template gives it.

## Generate trigger condition

Inputs: `{{recordContent}}`, `{{rowValues}}`, `{{domainGlossary}}`, `{{grillingContext}}`; optionally `{{tableMetadata}}`.

1. Extract entities, data shapes, behaviors, boundaries, interfaces, folders, change types, constraints.
2. Generate concise, comma-separated phrases in domain-specific language likely to arise during grilling.
3. Prefer high-signal phrases and real domain synonyms. Exclude generic phrases, title-only    phrases, and the generation requirement itself.

Return one Trigger condition value.

## Scan and match

Inputs: `{{tableMetadata}}`, `{{touchedSurface}}`, `{{grillingContext}}`, `{{domainGlossary}}`.
For this file's own tables, `{{tableMetadata}}` is `Services`, `Architecture Decision Records`, or
`Crosscutting Concepts` (file/section boundary, headers, Trigger condition column, row locator
rules). Callers (`grill-design`) supply the touched surface, grilling context, glossary — never the table shape.

1. Absent or empty table: no matches.
2. Absent Trigger condition column: table-contract error.
3. Read each row's Trigger condition cell; a blank cell never matches.
4. Split non-blank cells on commas; match each clause semantically against the touched surface and grilling context, using the glossary for domain terms and paraphrases.
5. Open a linked record only when its locator is supplied and resolvable.
6. Report matched clauses and rationale for matches; checked clauses and rationale for non-matches.

## Sync index row

Inputs: `{{tableMetadata}}`, `{{rowMetadata}}`, `{{action}}` (`add`, `supersede`, `retire`). `{{tableMetadata}}` supplies the table boundary, headers, Trigger condition column, row locator rules. `{{rowMetadata}}` supplies row identity and explicit cell values. Callers (`record-adr`, `record-concept`, `record-service`) supply `{{rowMetadata}}` and `{{action}}`; this skill applies the change.

1. `add`: append a row using the supplied headers and cell values.
2. `supersede`: update only the named cells in the located row.
3. `retire`: apply the caller's retirement marker to the located row.
4. Preserve unspecified cells, unknown columns, existing rows.
5. Apply the row change with the underlying record change. If metadata is missing or ambiguous, report it — do not guess.

Return the updated row or a concise synchronization report.

## Errors

- Missing or empty table: no matches for **Scan and match**.
- Missing Trigger condition column: table-contract error.
- Missing or ambiguous synchronization metadata: report the issue without changing the row.

