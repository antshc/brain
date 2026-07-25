# Trigger Indexer

**Status:** Accepted

## Purpose

Any markdown table with a Trigger condition column (e.g. `ARCHITECTURE.md`'s `Crosscutting Concepts` and `Architecture Decision Records` indexes) risks two failure modes if every caller re-implements its own logic: inconsistent scan/match verdicts between callers, and rows drifting out of sync with the records they list. This concept centralizes both the read side (scan and match) and the write side (keep rows in sync) behind one skill so every caller gets identical, deterministic verdicts and every record add/supersede/retire updates its index row in the same change.

## Design Guidance

- Any index table with a Trigger condition column — not limited to Concepts/ADRs — is owned end to end by the `trigger-indexer` skill. It is resource-agnostic: `{{indexFile}}`, `{{indexSection}}`, and `{{recordDirectory}}`/`{{recordPath}}` are always supplied by the caller in context; the skill hardcodes none of them.
- **Read side ("Scan and match"):** trigger clauses are split on commas and matched literally against the change's touched surface (entity/data shape, endpoint, folder, change type). This is deterministic — no session or caller state affects the verdict.
- **Write side ("Keeping the indexes in sync"):** add/supersede/retire the index row in the same change that adds, changes, or retires the underlying record — never batched separately.
- Callers (`manage-docs`, `domain-modeling`, `to-tickets`, and any skill needing to check whether a Concept/ADR applies) invoke the skill's actions rather than re-implementing scan/match or sync logic inline.
- Does not own: document templates, file locations, or lazy-creation rules for `CONTEXT.md`, `ARCHITECTURE.md`, Concepts, or ADRs — that stays with `manage-docs`. Does not own a caller's session ledger or closing completeness sweeps — see the `Ledger` Concept.

## Exceptions

- `trigger-indexer` writes directly to whichever file holds the index table (e.g. `ARCHITECTURE.md`), even when that file is otherwise owned by another Resource Access Skill (`manage-docs`) — see the `Resource Access Skill` Concept's own Exceptions for the reciprocal note.
