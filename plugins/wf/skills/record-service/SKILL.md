---
name: record-service
description: Document one building block/service — its purpose, contracts, and source layout — the moment it's non-trivial enough to warrant a full doc. Owns BUILDING-BLOCK-SERVICE-FORMAT.md and the "non-trivial" gate. The Services table row is mandatory whenever a service exists in ARCHITECTURE.md; the full doc is optional and lazy. Called directly by explicit user request, or invoked by grill-design as services are identified.
---

# Record Service

Document **one building block/service** — its responsibility, contracts, and source layout — the
moment it warrants a full doc. Use
[BUILDING-BLOCK-SERVICE-FORMAT.md](./BUILDING-BLOCK-SERVICE-FORMAT.md) for the template.

This differs from `record-adr`/`record-concept` in three ways — don't copy their pattern blindly:

## No numbering

The filename is `{{buildingBlockName}}-service.md` — not `NNNN-slug.md`. Services aren't
point-in-time records; they're named after the building block they document.

## Row is mandatory, full doc is optional

The `Services` table lives under `ARCHITECTURE.md`'s required `Building blocks` section, so it
always exists once `ARCHITECTURE.md` does. Add or update a row **every time** a service is
documented — but create the linked `docs/services/{{buildingBlockName}}-service.md` file only when
the service is **non-trivial**:

- it has an API contract, or
- it has persisted data, or
- its responsibility is more than a trivial single-line description.

Otherwise, skip the full doc — the row and its summary are enough.

## Lazy creation

Create `docs/services/` only when the full doc is warranted (per the non-trivial gate above) — not
on every row addition: create the directory if it's missing, do nothing if it exists. Services are
not numbered — see **No numbering** above.

## Keeping the index in sync

Call `index-docs`' **Sync index row** for the `Services` table row every time a service
is added or updated — regardless of whether the full doc is written — never edit the table in
`ARCHITECTURE.md` directly.

