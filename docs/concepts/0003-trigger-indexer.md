# Trigger Indexer

**Status:** Accepted

## Purpose

Any markdown table with a Trigger condition column risks two failure modes if every caller re-implements its own logic: inconsistent scan/match behavior between callers, and rows drifting out of sync with the records they list. This concept centralizes trigger generation, semantic scan/match, and row synchronization behind one skill so every caller can use the same table contract and every record add/supersede/retire updates its row in the same change.

## Design Guidance

- Any index table with a Trigger condition column — including Service, ADR, Concept, and custom tables — is owned end to end by the `trigger-indexer` skill. The caller supplies table, column, and row metadata; the skill hardcodes no file, section, directory, record type, or Summary column.
- **Generation:** trigger conditions are concise, comma-separated, domain-specific phrases chosen from the record, glossary, and grilling context so they sound natural in the session. The generation requirement is guidance, not literal row text.
- **Read side ("Scan and match"):** trigger clauses are split on commas and matched semantically against the supplied touched surface and grilling context. Blank cells never match; row titles and summaries do not substitute for a missing clause.
- **Write side ("Keeping the indexes in sync"):** add/supersede/retire the supplied row in the same change that adds, changes, or retires the underlying record, preserving unknown columns and unspecified cells.
- Callers (`manage-docs`, `domain-modeling`, `to-tickets`, and any skill needing to decide whether an indexed record applies) invoke the skill's actions rather than re-implementing generation, scan/match, or sync logic inline.
- Does not own: document templates, file locations, table creation, or lazy-creation rules — that stays with the owning document skill. Does not own a caller's session ledger or closing completeness sweeps — see the `Ledger` Concept.

## Exceptions

- `trigger-indexer` writes directly to whichever table the caller supplies, even when its containing file is otherwise owned by another Resource Access Skill (`manage-docs`) — see the `Resource Access Skill` Concept's own Exceptions for the reciprocal note.
