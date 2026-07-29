---
name: track-ledger
description: Own the session ledger at /memories/session/domain-model-ledger.md — its file location, section names, line grammar, and compression rule. Records which Concept/ADR/service records have been opened or skipped, the surface terms touched so far, and every decision or assumption staged this session. Called by grill-design; owns the grammar only, never when to log or whether an item survives a veto.
---

# Track Ledger

Own the session ledger at `/memories/session/domain-model-ledger.md`. Persist via the memory tool.
Create it **lazily**, on the first write of any kind — never up front.

Three sections, each with its own line grammar. Callers decide *when* to write; this skill decides
*how* the line reads.

## Log opened record

Writes into `Opened records` — one line per record, path-anchored. Never a row number (numbers
renumber on index sync and collide across tables). Never a range.

* `{{path}} — opened, trigger matched: "{{clause}}"`
* `{{path}} — opened, direct: {{topic}}`
* `{{path}} — skipped, checked "{{clause1}}", "{{clause2}}": no match`

Update an existing line in place; never append a duplicate for the same `{{path}}`.

Returns the written line.

## Append surface term

Writes into `Touched surface` — the accumulated surface terms (module, boundary, service,
entity, data shape, behavior, interface, change type) extracted from the session so far. This is
the cache key that makes a `skipped` verdict re-checkable: a `skipped` line is only valid for the
surface known at the turn it was written.

Appends only terms not already present.

Returns which of the supplied terms were new — the caller's trigger for a re-scan.

## Log decision

Writes into `Decisions / assumptions` — one line per item; position in the section carries
pending/cleared status, so no `pending veto` suffix is needed.

* `{{item}} — assumed, evidence: "{{source}}"`
* `{{item}} — decided by user, feature decision, grounded: "{{source}}"`
* `{{item}} — decided by user, recorded: {{path}}`
* `{{item}} — rejected, reason: "{{source}}"`

Also rewrites or deletes an existing line, located by `{{item}}` — used when a staged item is
cleared or vetoed at the end of a session.

Returns the written line, or confirmation of the rewrite/deletion.

## Compression

Once a section grows large, stop reproducing it in full: compress resolved terms and decisions into
a short summary at the top of the section, keep the individual lines that are still pending, and
re-open a full record only when a specific detail is needed again.

