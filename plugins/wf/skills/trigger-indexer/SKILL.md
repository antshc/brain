---
name: trigger-indexer
description: >-
  Generate conversational trigger conditions, scan any markdown table with a Trigger condition column, and synchronize its rows without assuming a record type or schema.
---

# Trigger Indexer

Use for any markdown table with a **Trigger condition** column, including Service, ADR, Concept, and custom tables. Never assume a file, section, record type, path, `Summary` column, or fixed schema. Callers supply all table and row metadata.

## Actions

Run only the requested action. Use caller-resolved `{{placeholders}}`.

### Generate trigger condition

Inputs: `{{recordContent}}`, `{{rowValues}}`, `{{domainGlossary}}`,
`{{grillingContext}}`; optionally `{{tableMetadata}}`.

1. Extract the record's entities, data shapes, behaviors, boundaries, interfaces, folders,
   change types, and constraints.
2. Generate concise, comma-separated phrases using domain-specific language that would
   naturally arise during grilling sessions.
3. Prefer high-signal phrases and real domain synonyms. Exclude generic phrases, title-only
   phrases, and the generation requirement itself.

Return one Trigger condition value.

### Scan and match

Inputs: `{{tableMetadata}}`, `{{touchedSurface}}`, `{{grillingContext}}`,
`{{domainGlossary}}`.

1. If the table is absent or empty, return no matches.
2. If the Trigger condition column is absent, return a table-contract error.
3. Read each row, especially its Trigger condition cell. A blank cell never matches.
4. Split non-blank cells on commas. Match each clause semantically against the touched
   surface and grilling context, using the glossary for domain terms and paraphrases.
5. Open a linked record only when its locator is supplied and resolvable.
6. For matches, report the matched clauses and rationale. For non-matches, report the checked clauses and rationale.

### Keeping the indexes in sync

Inputs: `{{tableMetadata}}`, `{{rowMetadata}}`, and `{{action}}` (`add`, `supersede`, or `retire`). `{{tableMetadata}}` supplies the table boundary, headers, Trigger condition column, and row locator rules. `{{rowMetadata}}` supplies the row identity and explicit cell alues.

1. `add`: append a row using the supplied headers and cell values.
2. `supersede`: update only the named cells in the located row.
3. `retire`: apply the caller's retirement marker to the located row.
4. Preserve unspecified cells, unknown columns, and existing rows.
5. Apply the row change with the underlying record change. If metadata is missing or ambiguous, report the issue; do not guess. 

Return the updated row or a concise synchronization report.

## Errors

- Missing or empty table: no matches for **Scan and match**.
- Missing Trigger condition column: table-contract error.
- Missing or ambiguous synchronization metadata: report the issue without changing the row.

## Ownership

- Owns trigger generation, semantic scan/match/open, and row synchronization.
- Does not own document templates, file locations, table creation, or lazy-creation rules.
- Does not own caller session ledgers or completeness sweeps.
