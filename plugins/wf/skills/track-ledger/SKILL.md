---
name: track-ledger
description: Own the session ledger at /memories/session/domain-model-ledger.md — its location, section names, line grammar, and compression rule. Records which Concept/ADR/service records were opened or skipped, the surface terms touched so far, and every decision or assumption staged this session. Called by grill-design; owns the grammar only, never when to log or whether an item survives a veto.
---

# Track Ledger

Own the session ledger at `domain-model-ledger.md` — use the memory session folder, never a shell/filesystem path. Create it **lazily**, on the first write of any kind — never up front.

Three sections, each with its own line grammar. Callers decide *when* to write; this skill decides *how* the line reads.

## Log opened record

Writes into `Opened records` — one line per record, path-anchored. Never a row number (numbers renumber on index sync and collide across tables). Never a range.

* `{{path}} — opened, trigger matched: "{{clause}}"`
* `{{path}} — opened, direct: {{topic}}`
* `{{path}} — skipped, checked "{{clause1}}", "{{clause2}}": no match`

Update an existing line in place; never append a duplicate for the same `{{path}}`.

Returns the written line.

## Append surface term

Writes into `Touched surface` — the accumulated surface terms (module, boundary, service, entity, data shape, behavior, interface, change type) and concrete file/folder paths extracted from the session so far. This is the cache key that makes a `skipped` verdict re-checkable: a `skipped` line is only valid for the surface known at the turn it was written. Paths are recorded repo-relative, verbatim, and are never paraphrased into terms — they are matched as globs, not semantically.

Appends only terms not already present.

Returns which of the supplied terms were new — the caller's trigger for a re-scan.

## Log decision

Writes into `Decisions / assumptions` — one line per item; position in the section carries pending/cleared status, so no `pending veto` suffix is needed.

* `{{item}} — assumed, evidence: "{{source}}"`
* `{{item}} — decided by user, feature decision, grounded: "{{source}}"`
* `{{item}} — decided by user, recorded: {{path}}`
* `{{item}} — rejected, reason: "{{source}}"`
* `{{item}} — offered {{ADR|Concept}}, deferred: "{{reason}}"`
* `{{item}} — offered {{ADR|Concept}}, declined: "{{reason}}"`

Three further forms record a **gap in the source** rather than a decision — each names the record and key to repair, and each is resolved by the caller's closing harvest:

* `{{item}} — asked, gate miss: {{gate}}, nearest source: {{path|none}}`
* `{{item}} — vetoed, evidence was: {{path}}#{{key}}`
* `{{item}} — drift, code contradicts: {{path}}#{{key}}`

Append `, repaired: {{path}}#{{key}}` to a gap line once its fix is written; a repaired line is not reproduced under compression.

Also rewrites or deletes an existing line, located by `{{item}}` — used when a staged item is cleared or vetoed at the end of a session.

Returns the written line, or confirmation of the rewrite/deletion.

## Compression

Once a section passes ~20 lines, stop reproducing it in full: replace the resolved terms and settled decisions with a short summary at the top of the section, keep every still-pending line verbatim, and re-open a full record only when a specific detail is needed again.

