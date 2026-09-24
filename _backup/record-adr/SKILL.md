---
name: record-adr
description: Capture one localized, non-obvious architectural decision as an ADR the moment it crystallises. Owns the "when to write an ADR" gate, numbering, and the choice between extending an existing record and creating a new one; doc-decision renders the record. Called directly by explicit user request, or invoked by grill-design.
---

# Record ADR

Capture **one point-in-time, localized decision** into `docs/adr/` the moment it crystallises.

A rule that turns out to constrain what gets built, to define a term, or to say how a file is worded belongs in another home — Run `/record-concept`' skill **Where the rule belongs** to route it.

## When to write an ADR

All three must be true — any miss, skip it:

1. **Hard to reverse** — changing your mind later carries real cost.
2. **Surprising without context** — a future reader will wonder "why on earth this way?"
3. **A real trade-off** — genuine alternatives existed; one was picked for specific reasons.

Qualifies: architectural shape (monorepo, event-sourced write model); integration patterns between contexts (domain events vs. synchronous HTTP); technology choices carrying lock-in (database, bus, auth provider, deployment target — not every library); boundary and ownership decisions, where the explicit no-s matter as much as the yes-s; deliberate deviations from the obvious path, which stop the next engineer "fixing" something intentional; constraints invisible in the code (compliance, latency contracts); rejected alternatives whose rejection is non-obvious.

## Extend or create

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

Runs before any write. A near-duplicate record is worse than a longer one: it splits authority over a decision area, and the `owns` key can then name only one of them.

1. Run `/index-docs`' skill **Scan and match** over the `Architecture Decision Records` and `Crosscutting Concepts` tables with this decision's surface — its terms and the paths it governs.
2. A matched record whose scope or `owns` already covers this decision area → **extend it**: amend the body, and sharpen `default`, `owns`, `trigger`, or `applies_to` to cover the new case. Resync its row via **Sync index row**. Stop here.
3. No match covers the area → **create** a new ADR. Its `owns` phrases must not collide with any existing record's — a phrase belongs to exactly one record.

## Lazy creation

Create `docs/adr/` when the first ADR is ready — not before; do nothing if it exists.

## Next record number

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

Highest four-digit `NNNN` filename prefix in `docs/adr/`, plus 1, zero-padded to four digits. An empty or absent directory returns `0001`.

## Approval gate

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

- **Explicit direct request** ("record an ADR for X") — approval is already given; draft and write immediately.
- **Invoked by an interview-style caller** (`grill-design`) — the caller already owns the decision to record, whether it came from the user's answer or from the caller's own assumption. Write immediately; never stop to offer, confirm, or defer. The user reviews the result in `git diff`.

## Write the record

Write this frontmatter first:

```md
---
id: "{{nnnn}}"
title: {{decisionTitle}}
trigger: >-
	{{comma-separated trigger clauses}}
summary: >-
	{{one-paragraph summary}}
default: >-
	{{the choice to take when the design doesn't state one}}
owns: ["{{decision area}}"]
applies_to:
	- {{path glob}}
related: ["{{nnnn}}"]
---
```

| Key | Required | Value |
|-----|----------|-------|
| `id` | yes | Quoted four-digit record number, matching the filename prefix. |
| `title` | yes | Same text as the body heading and the index row's Decision cell. |
| `trigger` | yes | Comma-separated clauses naming the change types that make this decision apply. Source of truth for the index's Trigger condition cell. |
| `summary` | yes | The index row's Summary cell, verbatim. |
| `default` | yes | One sentence naming the choice to take when the design doesn't state one. `index-docs` prepends it to the index row's Summary cell. State the choice, never the reference implementation that embodies it. |
| `owns` | no | Decision-area phrases this record has sole authority over. Add one only where another record could plausibly claim the same area; a phrase may appear in exactly one record. |
| `applies_to` | no | Repo-relative path globs the decision governs. Widens matching only: a glob miss never overrides a `trigger` clause hit. |
| `related` | no | Quoted ids of Concepts or ADRs a reader must also load. Keep bidirectional. |

Use folded block scalars (`>-`) for `trigger`, `summary`, and `default`; all three routinely contain `:`, backticks, and `→`.

Run `/doc-decision` skill with **full** format and the established decision context. Append its output after the frontmatter, then write the complete record to `docs/adr/{{nnnn}}-{{slug}}.md`.

## Keeping the index in sync

When an ADR is added, superseded, or retired, Run `/index-docs`' skill **Ensure section exists** for `Architecture Decision Records`, then its **Sync index row** in the same change — never edit the table in `ARCHITECTURE.md` directly. The index summary must match the ADR's own content.

