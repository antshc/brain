---
name: record-adr
description: Capture one localized, non-obvious architectural decision as an ADR the moment it crystallises. Owns ADR-FORMAT.md, the "when to write an ADR" gate, numbering, and the approval-gate distinction between a direct request and an offer. Called directly by explicit user request, or invoked as an offer by grill-design.
---

# Record ADR

Capture **one point-in-time, localized decision** into `docs/adr/` the moment it crystallises. Use
[ADR-FORMAT.md](./ADR-FORMAT.md) for the template, the "when to write" gate, and what qualifies.

## Lazy creation

Ask `bootstrap-docs` whether `docs/adr/` exists; if absent, create it when the **first ADR is
ready** — not before. Number sequentially: scan `docs/adr/` for the highest existing `NNNN` and
increment by one.

## Approval gate

- **Explicit direct request** ("record an ADR for X") — approval is already given; draft and write
  immediately.
- **Offered by an interview-style caller** (`grill-design`) — the offer itself is the approval
  gate: draft it, present it, and only write once the user explicitly responds to that specific
  offer.

## Keeping the index in sync

When an ADR is added, superseded, or retired, call `index-docs`' **Sync index row** in
the same change — never edit the `Architecture Decision Records` table in `ARCHITECTURE.md`
directly. The index summary must match the ADR's own content.

## Ownership

- Owns: `ADR-FORMAT.md`'s template, the "when to write an ADR" gate, numbering, and the
  approval-gate distinction.
- Does **not** own: file/directory existence-and-creation mechanics (`bootstrap-docs`' job), or the
  `Architecture Decision Records` table's row sync (`index-docs`' job).
