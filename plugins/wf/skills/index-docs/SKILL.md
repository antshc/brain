---
name: index-docs
description: Own ARCHITECTURE.md's structural prose (Overview, Building blocks, Deployment View), host ARCHITECTURE-FORMAT.md, and insert its missing section skeletons. Owns the generic trigger-generation, scan/match, and row-sync mechanic for any markdown table with a Trigger condition column (Services, ADR, Concept, or custom), driven by caller-supplied table/row metadata rather than a fixed schema. Called by grill-design and the record-* skills. Does not create ARCHITECTURE.md and does not author its index rows' content.
---

# Index Docs

Own `ARCHITECTURE.md`'s structural prose and the three indexes it hosts (`Services`, `Architecture Decision Records`, `Crosscutting Concepts`) — the file itself is created by `bootstrap-docs`. Template: [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md).

## Rules

- **Shape, not steps.** `ARCHITECTURE.md` describes decomposition and the rules holding it together — not a spec, not a scratch pad, not a home for inlined backbone decisions. Step-by-step detail lives in code and linked Concepts.
- **Never batch.** Update `ARCHITECTURE.md` in the same change as the structure/layering shift it reflects. A stale architecture map is worse than none.
- **The record owns its row.** When a linked record carries YAML frontmatter, the table is a projection of it — never an independent copy. On disagreement, frontmatter wins.

## Record frontmatter as row source

Records under `docs/concepts/` and `docs/adr/` may open with YAML frontmatter (see the owning `record-*` skill's `*-FORMAT.md`). Where present, it — not the table — is the source of truth for the row.

Default key→column mapping, overridable by `{{tableMetadata}}`:

| Frontmatter key | Column |
|-----------------|--------|
| `id` | `#`, rendered as a link to the record path |
| `title` | the record-name column (`Concept`, `Decision`, `Service`) |
| `trigger` | `Trigger condition` |
| `summary` | `Summary`, preceded by `default` |
| `default` | `Summary`, as a leading `**Default:** {{default}}` sentence before `summary` |
| `owns` | not a column; read by callers from the frontmatter |

Rules:

- Read frontmatter with a YAML parse of the block between the leading `---` fences. `trigger`, `summary`, and `default` are commonly folded block scalars (`>-`) — fold them to a single line before writing the cell, and collapse runs of whitespace.
- The `Summary` cell is the concatenation `**Default:** {{default}} {{summary}}` — a `default` edit forces a row resync just as a `summary` edit does. A record with no `default` yields the summary alone.
- **Reading frontmatter is not opening the record.** The block is bounded and cheap, so it may always be read once a row's locator resolves. "Open" elsewhere in this skill means loading the record **body**, which stays gated on a matching verdict. A row's `default` therefore reaches a caller without opening anything.
- A record without frontmatter falls back to caller-supplied `{{rowValues}}`; never invent the missing keys.
- Never edit a cell to resolve a mismatch with its record. Resync the row from frontmatter, or fix the record's frontmatter — never both independently.

## Ensure section exists

Inputs: `{{sectionAnchor}}` (e.g. `Architecture Decision Records`, `Crosscutting Concepts`, the `Services` table under `Building blocks`); optionally `{{skeletonContent}}`.

1. If `{{sectionAnchor}}` already exists in `ARCHITECTURE.md`, do nothing.
2. Otherwise insert its skeleton — `{{skeletonContent}}` when the caller supplies one (custom tables), else the skeleton for that section from [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md) — at the position the template gives it.

## Generate trigger condition

Inputs: `{{recordContent}}`, `{{rowValues}}`, `{{domainGlossary}}`, `{{grillingContext}}`; optionally `{{tableMetadata}}`.

1. If `{{recordContent}}` already carries a `trigger` frontmatter key, return it unchanged — it is authoritative; do not regenerate.
2. Extract entities, data shapes, behaviors, boundaries, interfaces, folders, change types, constraints.
3. Generate concise, comma-separated phrases in domain-specific language likely to arise during grilling.
4. Prefer high-signal phrases and real domain synonyms. Exclude generic phrases, title-only phrases, and the generation requirement itself.

Return one Trigger condition value. The caller writes it into the record's frontmatter; the row is then synced from there.

## Scan and match

Inputs: `{{tableMetadata}}`, `{{touchedSurface}}`, `{{grillingContext}}`, `{{domainGlossary}}`. `{{tableMetadata}}` is the file/section boundary, headers, Trigger condition column, and row locator rules; for this file's own three tables it is implied — the caller passes only the table name (`Services`, `Architecture Decision Records`, `Crosscutting Concepts`). Callers supply the touched surface, grilling context, and glossary — never the table shape. `{{touchedSurface}}` may carry domain terms, file paths, or both; a caller that knows which files a change touches passes them, and one that only has terms passes terms.

1. Absent or empty table: no matches.
2. Absent Trigger condition column: table-contract error.
3. Read each row's Trigger condition cell; a blank cell never matches.
4. Split non-blank cells on commas; match each clause semantically against the touched surface and grilling context, using the glossary for domain terms and paraphrases.
5. Where `{{touchedSurface}}` carries file paths, also read the linked record's frontmatter and match those paths against its `applies_to` globs. A glob hit is a match even when no trigger clause fires; a glob **miss never overrides a trigger-clause match** — `applies_to` only widens the verdict, never narrows it. A record with no `applies_to`, or one whose globs are `**`, is decided on trigger clauses alone.
6. Open the linked record's body only when its locator is supplied and resolvable. Having opened one, treat its `related` ids as candidates and scan their rows too.
7. Report matched clauses and rationale for matches; checked clauses and rationale for non-matches. Where a match came from `applies_to` rather than a trigger clause, say so — it usually means the Trigger condition cell has a gap worth refining.

## Sync index row

Inputs: `{{tableMetadata}}`, `{{rowMetadata}}`, `{{action}}` (`add`, `supersede`, `retire`). `{{tableMetadata}}` supplies the table boundary, headers, Trigger condition column, row locator rules. `{{rowMetadata}}` supplies row identity and explicit cell values, or the path of a frontmatter-bearing record to project the row from. Callers supply `{{rowMetadata}}` and `{{action}}`; this skill applies the change.

1. When `{{rowMetadata}}` names a record path, parse its frontmatter and derive cells via the key→column mapping above; explicit cell values in `{{rowMetadata}}` override derived ones.
2. `add`: append a row using the supplied headers and cell values.
3. `supersede`: update only the named cells in the located row.
4. `retire`: apply the caller's retirement marker to the located row.
5. Preserve unspecified cells, unknown columns, existing rows.
6. Apply the row change with the underlying record change. If metadata is missing or ambiguous, report it — do not guess.

Return the updated row or a concise synchronization report.

