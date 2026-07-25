# Ledger

**Status:** Accepted

## Purpose

A long-running grilling/domain-modeling session risks re-opening or re-scanning the same Concept, ADR, or service record repeatedly, or losing track of what has already been validated once the transcript grows past what fits usefully in context. A Ledger is a session-scoped, externally persisted record of every record opened so far — checked before any re-scope decision instead of relying on recall over a long context window.

## Design Guidance

- Persist via the memory tool at `/memories/session/domain-model-ledger.md`. Create it lazily on the first record opened — not up front.
- One line per record: `{{path}} — opened for {{topic}}`.
- Before discussing any module, boundary, or service, check the ledger:
  - **Already listed** — its full record is loaded; don't re-open or re-scan the index for it.
  - **Not listed** — this is a re-scope: re-read the index, re-apply the relevance test, and append the result to the ledger.
- Once the ledger grows large, stop re-scanning everything on every re-scope — compress resolved terms and decisions into a short summary, rely on that plus the ledger, and re-open a full record only when a specific detail is needed again.
- The Ledger belongs to the caller holding the session (e.g. `domain-modeling`), not to `trigger-indexer` — the indexer only returns match verdicts; tracking what is already open is the caller's own state.

## Exceptions

- A record retired mid-session is only reflected on the *next* index scan — content the caller already opened earlier in the same session is not retroactively invalidated by the Ledger; that is a scan/match concern (see the `Trigger Indexer` Concept), not the Ledger's own.
