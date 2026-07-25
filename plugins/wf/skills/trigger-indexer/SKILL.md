---
name: trigger-indexer
description: Scans and syncs any index table with a Trigger condition column (Crosscutting Concepts, ADRs, or any future index type) — matches a change's touched surface against each row's trigger clauses to decide which full records to open, and keeps rows current on add/supersede/retire. Called by manage-docs, domain-modeling, to-tickets, and any skill that needs to check whether a Concept or ADR applies before it re-implements the check itself.
---

# Trigger Indexer

Sole owner of index-table mechanics for any markdown table that has a **Trigger condition**
column — not limited to the `Crosscutting Concepts` or `Architecture Decision Records` indexes in `ARCHITECTURE.md`; any future indexed record type (e.g. a Building-block service index) uses the
same two actions. Callers invoke the actions below rather than re-implementing the scan/match or row-sync logic inline.

This skill is resource-agnostic by design: it holds no hardcoded index file, section, or record directory. Every caller must supply `{{indexFile}}`, `{{indexSection}}`, and (for sync) `{{recordDirectory}}`/`{{recordPath}}` explicitly in context at invoke time — never assume the caller means `ARCHITECTURE.md`'s Concepts/ADR sections or `docs/concepts/`/`docs/adr/` unless the caller actually passed those values.

# Actions

Find the heading matching the requested operation and follow its steps exactly — do not skip steps or improvise an alternative command. Each action reads its inputs as `{{placeholder}}` variables already in the caller's context and states what it returns.

## Scan and match

Reads `{{indexFile}}` (e.g. `ARCHITECTURE.md`), `{{indexSection}}` (e.g. `Crosscutting Concepts`, `Architecture Decision Records`, or any other section with a Trigger condition column), and `{{touchedSurface}}` (the current change's entity/data shape, endpoint, folder, or change type) from context.

1. If `{{indexFile}}` doesn't exist yet, or `{{indexSection}}`'s table has no rows, return no    matches — this is not an error.
2. For every row in the table:
   - A blank Trigger condition cell is a documentation gap — never treat it as a universal match.
   - Split the cell on commas into clauses. Check each clause literally against `{{touchedSurface}}` — never substitute the row's title/summary for this test.
   - Any single clause match → the row matches. Open the full linked record at the row's linked doc path.
   - No clause matches → the row is skipped; record which clause(s) were checked.
3. This is a deterministic, literal clause match — no session or caller state affects the verdict. Two callers scanning the same table for the same `{{touchedSurface}}` always get the same verdicts.

**Returns:** per row, a matched/skipped verdict (the specific matched clause when matched, or the clause(s) checked when skipped), plus the full text of every matched record.

## Keeping the indexes in sync

`{{indexFile}}` (or any other file holding an index table) is the entry point a reader scans
before designing. Every record in `{{recordDirectory}}` (e.g. `docs/concepts/`, `docs/adr/`, or any
other indexed record type's directory) must appear in its index table with a matching Trigger
condition and summary cell — nothing is added, superseded, or retired without this action running
in the same change. Link, don't inline — keep the full record content out of the index file so the
map stays scannable.

Reads `{{indexFile}}`, `{{indexSection}}`, `{{recordDirectory}}` (the directory new record files
live in), `{{recordPath}}`, `{{triggerCondition}}`, `{{summary}}`, and `{{action}}` (`add` |
`supersede` | `retire`) from context.

1. `add` — append a new row to `{{indexSection}}`'s table linking `{{recordPath}}` (the new record file created under `{{recordDirectory}}`), with `{{triggerCondition}}` and `{{summary}}` filled in.
2. `supersede` — update the existing row's Trigger condition and summary cells in place.
3. `retire` — mark the row retired (e.g. strike through or annotate it) without deleting it.

Apply the row change immediately, in the same change that adds, supersedes, or retires the underlying record — never batch it separately.

**Returns:** nothing.

## Troubleshooting (all actions)

**`{{indexFile}}` or `{{indexSection}}` doesn't exist yet**: not a failure. **Scan and match** returns no rows (per its step 1); **Keeping the indexes in sync**'s caller creates the file/section first via `/manage-docs`'s `Lazy creation` rule, then retries.

---

# Ownership boundaries

- Owns: the scan/match/open (read) logic and the add/supersede/retire (write) logic for any index table with a Trigger condition column.
- Does not own: document templates, file locations, or lazy-creation rules for `CONTEXT.md`, `ARCHITECTURE.md`, Concepts, or ADRs — those stay with `/manage-docs`.
- Does not own: a caller's session ledger (which records it has already opened this session) or closing completeness sweeps — those are consumers of this skill's verdicts, not part of it (e.g. `/domain-modeling` owns both).
- A record retired mid-session is only reflected on the *next* scan — content a caller already opened earlier in the same session is not retroactively invalidated; that's the caller's own ledger's concern, not this skill's.
