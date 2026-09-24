# Ledger

## Purpose

A long-running grilling or domain-modeling session risks re-opening the same Concept or service record
repeatedly, or losing track of what has already been validated once the transcript grows past what fits usefully
in context. A Ledger is a session-scoped, externally persisted record of every record opened so far, checked
before any re-scope decision instead of relying on recall.

## Rules

- A Ledger MUST be persisted via the memory tool at `/memories/session/domain-model-ledger.md`.
- A Ledger MUST be created lazily, on the first record opened, never up front.
- A Ledger MUST carry one line per record, in the form `{{path}} — opened for {{topic}}`.
- A caller MUST check the Ledger before discussing any module, boundary, or service.
- A record already listed MUST NOT be re-opened or re-scanned.
- A Ledger MUST be owned by the caller holding the session, never by the indexing skill.

## Design Guidance

A path not listed in the Ledger is a re-scope: re-read the index, re-apply the relevance test, and append the
result. A path already listed means its full record is loaded — reason over what is in context.

Once the Ledger grows large, stop reproducing it whole on every re-scope. Compress resolved terms and settled
decisions into a short summary at the top of the section, keep pending lines verbatim, and re-open a full record
only when a specific detail is needed again.

## Exceptions

- A record retired mid-session is only reflected on the *next* index scan — content the caller already opened
  earlier in the same session is not retroactively invalidated by the Ledger; that is a scan/match concern (see
  [structure-trigger-indexer](structure-trigger-indexer.md)), not the Ledger's own.
