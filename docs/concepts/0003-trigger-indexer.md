---
id: "0003"
title: Trigger Indexer
trigger: >-
  adding a new indexed table or row type, trigger phrases missing domain language, index rows drifting out of
  sync with their records, a caller re-implementing scan or match logic inline, deciding whether an indexed
  record applies to the current change, a blank Trigger condition cell
summary: >-
  Generates concise conversational trigger phrases and centralizes semantic scan/match plus add/supersede/retire
  synchronization for any markdown table with a Trigger condition column, with caller-supplied metadata and
  preservation of unknown columns.
default: >-
  Route trigger generation, scan/match, and row synchronization for any Trigger-condition table through the
  indexing skill, passing table and row metadata rather than re-implementing the logic in the caller.
owns:
  - "index-table trigger generation, matching, and row synchronization"
applies_to:
  - plugins/wf/**
  - ARCHITECTURE.md
related: ["0001", "0002"]
---

# Trigger Indexer

## Purpose

Any markdown table with a Trigger condition column risks two failure modes if every caller re-implements its own
logic: inconsistent scan/match behavior between callers, and rows drifting out of sync with the records they
list. Centralizing trigger generation, semantic scan/match, and row synchronization behind one skill gives every
caller the same table contract and updates a row in the same change that changes its record.

## Rules

- An index table with a Trigger condition column MUST be owned end to end by the indexing skill.
- The indexing skill MUST NOT hardcode a file, section, directory, record type, or Summary column.
- A caller MUST supply the table, column, and row metadata.
- Trigger clauses MUST be split on commas and matched semantically against the supplied touched surface and
  grilling context.
- A blank Trigger condition cell MUST NOT match.
- A row title or summary MUST NOT substitute for a missing trigger clause.
- A row MUST be added, superseded, or retired in the same change as its underlying record.
- Columns and cells the caller did not name MUST be preserved.

## Design Guidance

Trigger conditions are concise, comma-separated, domain-specific phrases drawn from the record, the glossary,
and the grilling context, so they sound natural in the session. That is a generation requirement, not literal
row text.

This record does not own document templates, file locations, table creation, or lazy-creation rules — those stay
with the owning document skill — nor a caller's session state, which is [0002](0002-ledger.md).

## Exceptions

- `trigger-indexer` writes directly to whichever table the caller supplies, even when its containing file is otherwise owned by another Resource Access Skill (`manage-docs`) — see the `Resource Access Skill` Concept's own Exceptions for the reciprocal note.
