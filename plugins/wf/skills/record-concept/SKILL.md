---
name: record-concept
description: Capture one structural, reusable, backbone-defining architectural rule as a Crosscutting Concept the moment it crystallises. Owns CONCEPT-FORMAT.md, the "when to write a Concept" gate, numbering, and the approval-gate distinction between a direct request and an offer. Called directly by explicit user request, or invoked as an offer by grill-design.
---

# Record Concept

Capture **one backbone rule** — the top-level decomposition, or a pattern every feature of a given
kind must follow — into `docs/concepts/` the moment it crystallises. Use
[CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md) for the template.

## When to write a Concept

Write one (instead of, or in addition to, an ADR) only when all three are true:

1. **Structural** — it shapes the top-level decomposition or mandates a pattern, rather than
   settling one local question.
2. **Reusable** — future features of the same kind are expected to follow it every time.
3. **Backbone-defining** — it is one of the foundational decisions that hold the architecture
   together and constrain everything built on top of it.

If any of the three is missing, skip the Concept — an ADR (see `record-adr`) may be the better fit
instead.

## Lazy creation

Create `docs/concepts/` when the **first Concept is ready** — not before: create the directory if
it's missing, do nothing if it exists. Number the file per this skill's own **Next record number**
(see [CONCEPT-FORMAT.md](./CONCEPT-FORMAT.md)). The timing gate, directory creation, and numbering
are all this skill's own mechanics.

## Approval gate

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

- **Explicit direct request** ("record a Concept for X") — approval is already given; draft and
  write immediately.
- **Offered by an interview-style caller** (`grill-design`) — the offer itself is the approval gate: draft it, present it, and only write once the user explicitly responds to that specific offer.

## Keeping the index in sync

When a Concept is added, superseded, or retired, run `/index-docs`' **Ensure section exists** for
`Crosscutting Concepts`, then its **Sync index row** in the same change — never edit the table in
`ARCHITECTURE.md` directly.

