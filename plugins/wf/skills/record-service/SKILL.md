---
name: record-service
description: Document one building block/service in ARCHITECTURE.md's Services table, plus a full doc under docs/services/ when the service is non-trivial. Called directly by explicit user request, or by grill-design as services are identified.
---

# Record Service

Record **one building block** — its responsibility, contracts, and source layout.

Inputs: `{{buildingBlockName}}`, `{{mermaidComponentName}}`, `{{shortDescription}}`,
`{{grillingContext}}`, `{{domainGlossary}}`.

No approval gate — record a service as soon as it's identified.

## Sync the Services row — always

1. Run `/index-docs`' **Generate trigger condition** for `{{triggerCondition}}`.
2. Run `/index-docs`' **Ensure section exists** for the `Services` table under `Building blocks`.
3. Run `/index-docs`' **Sync index row** with `{{action}}` and `{{rowMetadata}}` =
   `{{buildingBlockName}}`, `{{mermaidComponentName}}`, `{{triggerCondition}}`,
   `{{shortDescription}}`, plus a link to the full doc once one exists. Never edit the table
   directly.

## Write the full doc — only when non-trivial

Write `docs/services/{{buildingBlockName}}-service.md` from
[BUILDING-BLOCK-SERVICE-FORMAT.md](./BUILDING-BLOCK-SERVICE-FORMAT.md) only when the service has
an API contract, has persisted data, or has a responsibility beyond a single line. Otherwise the
row and its summary are enough.

Filenames carry no number. Create `docs/services/` on the first such doc; do nothing if it already
exists.

