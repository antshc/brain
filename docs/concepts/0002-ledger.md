# Ledger

## Purpose

A long-running `grill-design` session has two problems a long context window doesn't solve on its own: it risks re-opening or re-scanning the same Concept, ADR, or service record repeatedly, and it holds Decisions, Feature Decisions, and Feature Assumptions that are not durable — a Feature Decision or Feature Assumption is never written to any repository document, and even a Decision destined for one isn't written until the user approves it, so nothing on disk survives a session restart or context compaction to recover any of them. The Ledger is a session-scoped, externally persisted record covering both: what has already been opened or scanned, and what has been decided or assumed so far — checked before any re-scope decision or conflict classification instead of relying on recall over a long context window.

Durable artifacts (`ARCHITECTURE.md`, ADRs, Concepts, `CONTEXT.md`) are the opposite case: they are already durable on disk, so the Ledger does not duplicate their content — it only tracks which of them have been opened this session.

## Design Guidance

- Persist via the memory tool at `/memories/session/domain-model-ledger.md`. Create it lazily on the first write of any kind — not up front.
- Three sections, each with its own line grammar:

**`## Opened records`** — one line per Concept/ADR/service record, path-anchored (never a row number — row numbers renumber on index sync and collide across tables):
  - `{{path}} — opened, trigger matched: "{{clause}}"`
  - `{{path}} — opened, direct: {{topic}}`
  - `{{path}} — skipped, checked "{{clause1}}", "{{clause2}}": no match`
  - Never a range (`docs/adr/0001..0003 — skipped` is not a legal line) — one line per record, always.

**`## Touched surface`** — the accumulated surface terms (module, boundary, service, entity, data shape, behavior, interface, change type) extracted from user answers so far this session. This is the cache key that makes a `skipped` verdict re-checkable: a `skipped` row is only valid for the surface known at the turn it was written.
  - Before discussing any module, boundary, or service, check whether it introduces a term not yet in `## Touched surface`.
    - **No new term** — reason over the in-context index copy; no scan, no write.
    - **New term(s)** — append to `## Touched surface`, then scan only the not-yet-`opened` rows against the new terms, updating their lines in place (never appending a duplicate).

**`## Decisions / assumptions`** — one line per item, position in the section carries pending/cleared status (no `pending veto` suffix needed):
  - `{{item}} — assumed, evidence: "{{source}}"` — a Feature Assumption: model-resolved, ledger-only, never recorded.
  - `{{item}} — decided by user, feature decision, grounded: "{{source}}"` — a Feature Decision: scoped to the current feature (fails the ADR/Concept gate, resolves no glossary term), ledger-only, never recorded, same durability as a Feature Assumption.
  - `{{item}} — decided by user, recorded: {{path}}` — a Decision written to a durable document (`ARCHITECTURE.md`, an ADR, a Concept, or `CONTEXT.md`), logged the same turn it's written.
  - `{{item}} — rejected, reason: "{{source}}"`
  - A Feature Assumption and a Feature Decision both live here **only** — never written to `ARCHITECTURE.md`, an ADR, a Concept, or `CONTEXT.md`. A Feature Assumption becomes eligible for a durable write only once the user clears it at the closing veto sweep, at which point it is a Decision and is written then (its line switches to `decided by user, recorded: {{path}}`).

- Once any section grows large, stop re-scanning everything on every re-scope — compress resolved terms and decisions into a short summary, rely on that plus the Ledger, and re-open a full record only when a specific detail is needed again.
- The Ledger belongs to the caller holding the session (e.g. `grill-design`), not to `trigger-indexer` — the indexer only returns match verdicts; tracking what is already open, what surface has been touched, and what has been decided is the caller's own state.

## Exceptions

- A record retired mid-session is only reflected on the *next* index scan — content the caller already opened earlier in the same session is not retroactively invalidated by the Ledger; that is a scan/match concern (see the `Trigger Indexer` Concept), not the Ledger's own.
