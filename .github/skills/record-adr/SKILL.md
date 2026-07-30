---
name: record-adr
description: Capture one localized, non-obvious architectural decision as an ADR the moment it crystallises. Owns ADR-FORMAT.md, the "when to write an ADR" gate, numbering, and the approval-gate distinction between a direct request and an offer. Called directly by explicit user request, or invoked as an offer by grill-design.
---

# Record ADR

Capture **one point-in-time, localized decision** into `docs/adr/` the moment it crystallises. Template: [ADR-FORMAT.md](./ADR-FORMAT.md).

## When to write an ADR

All three must be true — any miss, skip it:

1. **Hard to reverse** — changing your mind later carries real cost.
2. **Surprising without context** — a future reader will wonder "why on earth this way?"
3. **A real trade-off** — genuine alternatives existed; one was picked for specific reasons.

Qualifies: architectural shape (monorepo, event-sourced write model); integration patterns between contexts (domain events vs. synchronous HTTP); technology choices carrying lock-in (database, bus, auth provider, deployment target — not every library); boundary and ownership decisions, where the explicit no-s matter as much as the yes-s; deliberate deviations from the obvious path, which stop the next engineer "fixing" something intentional; constraints invisible in the code (compliance, latency contracts); rejected alternatives whose rejection is non-obvious.

## Lazy creation

Create `docs/adr/` when the first ADR is ready — not before; do nothing if it exists.

## Next record number

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

Highest four-digit `NNNN` filename prefix in `docs/adr/`, plus 1, zero-padded to four digits. An empty or absent directory returns `0001`.

## Approval gate

<!-- Deliberately duplicated in record-adr and record-concept: each skill must be self-contained. Do not factor out. -->

- **Explicit direct request** ("record an ADR for X") — approval is already given; draft and write immediately.
- **Offered by an interview-style caller** (`grill-design`) — the offer itself is the approval gate: draft it, present it, and only write once the user explicitly responds to that specific offer.

## Keeping the index in sync

When an ADR is added, superseded, or retired, run `/index-docs`' **Ensure section exists** for `Architecture Decision Records`, then its **Sync index row** in the same change — never edit the table in `ARCHITECTURE.md` directly. The index summary must match the ADR's own content.

