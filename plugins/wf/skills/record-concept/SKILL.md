---
name: record-concept
description: Capture one structural, reusable, backbone-defining architectural rule as a Crosscutting Concept the moment it crystallises. Owns CONCEPT-FORMAT.md, the "when to write a Concept" gate, numbering, and the approval-gate distinction between a direct request and an offer. Called directly by explicit user request, or invoked as an offer by grill-design.
---

# Record Concept

Capture **one backbone rule** — the top-level decomposition, or a pattern every feature of a given kind must follow — into `docs/concepts/` the moment it crystallises. Use [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md) for the template.

## When to write a Concept

Write one (instead of, or in addition to, an ADR) only when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather than settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it is one of the foundational decisions that hold the architecture together and constrain everything built on top of it.

If any of the three is missing, skip the Concept — an ADR (see `record-adr`) may be the better fit instead.

## Lazy creation

Create `docs/concepts/` when the first Concept is ready — not before; do nothing if it exists.

## Next record number

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

Highest four-digit `NNNN` filename prefix in `docs/concepts/`, plus 1, zero-padded to four digits. An empty or absent directory returns `0001`.

## Frontmatter is mandatory

Every Concept opens with the YAML frontmatter block defined in [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md#frontmatter). It is the machine-readable contract for the record, and the source of truth for its `ARCHITECTURE.md` index row.

1. Author `id`, `title`, `status`, `trigger`, `summary`, `applies_to` before writing the body — they force the "does this apply to me?" decision up front.
2. Derive `trigger` with `/index-docs`' **Generate trigger condition**, then write the returned value into frontmatter — not straight into the table.
3. `status` lives in frontmatter only. Never restate it as a `**Status:**` line in the body.
4. `related` is bidirectional: adding `related: ["0009"]` here means adding this record's id to `0009`'s `related` in the same change. A one-directional link is lost to any reader arriving from the other side.
5. Superseding or retiring a Concept updates its frontmatter `status` first; the index row follows from it.

## Keeping the index in sync

When a Concept is added, superseded, or retired, run `/index-docs`' **Ensure section exists** for `Crosscutting Concepts`, then its **Sync index row** in the same change — never edit the table in `ARCHITECTURE.md` directly.

Pass `{{rowMetadata}}` **from the record's frontmatter**, so the table stays a projection of the files rather than a hand-maintained duplicate:

| Column | Frontmatter key |
|--------|-----------------|
| `#` | `id` (linked to the record path) |
| `Concept` | `title` |
| `Trigger condition` | `trigger` |
| `Summary` | `summary` |

If a row and its record disagree, the frontmatter wins — resync the row, don't edit the file to match the table.

## Approval gate

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

- **Explicit direct request** ("record a Concept for X") — approval is already given; draft and write immediately.
- **Offered by an interview-style caller** (`grill-design`) — the offer itself is the approval gate: draft it, present it, and only write once the user explicitly responds to that specific offer.

