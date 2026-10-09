---
name: record-building-block
description: Document one Deployable in ARCHITECTURE.md's Deployables table, plus a full record under docs/building-blocks/ unless the repository documents itself. Called directly by explicit user request, or by grill-design as Deployables are identified.
---

# Record Building Block

Record **one building block** — its responsibility, dependencies, interfaces, source layout, Concepts, and ADRs.

Inputs: `{{buildingBlockName}}`, `{{mermaidComponentName}}`, `{{shortDescription}}`, `{{location}}` (`workspace/<repo>[/subpath]` or an absolute path, plus its `origin` URL), `{{grillingContext}}`, `{{domainGlossary}}`.

No approval gate — record a building block as soon as it's identified.

## Sync the Deployables row — always

1. Run `/index-docs`' skill **Generate trigger condition** for `{{triggerCondition}}`.
2. Run `/index-docs`' skill **Ensure section exists** for the `Deployables` table under `Building blocks`.
3. Run `/index-docs`' skill **Sync index row** with `{{action}}` and `{{rowMetadata}}` = `{{buildingBlockName}}`, `{{mermaidComponentName}}`, `{{triggerCondition}}`, `{{shortDescription}}`, `{{location}}`, plus a link to the full doc — the harness record below, or the repository's own documentation when it documents this block itself (no harness record in that case). Never edit the table directly.

## Write the full doc — unless the repository documents itself

Write `docs/building-blocks/{{slug}}.md` from [BUILDING-BLOCK-FORMAT.md](./BUILDING-BLOCK-FORMAT.md) — one required record per Deployable — unless `{{location}}`'s own repository already documents this block; in that case the Deployables row links to that doc instead, and this record is not written. Create `docs/building-blocks/` on the first such doc; do nothing if it exists.

Add the **Flow view** when the block's lifecycle or process is the point — e.g. a transient VM's/container's/sandbox's create → attach → run → detach → delete, a batch job's or pipeline's stages, a multi-step handoff — since a static C4 view shows it poorly. Draw it with `/doc-behavior-diagram`.

## Redraw the system context — on add, supersede, or retire

Run `/doc-architecture-diagram` skill to redraw `docs/building-blocks/system-context.md`'s `C4Context` and solution-level `C4Container` diagrams whenever a Deployable is added, superseded, or retired. Run `/index-docs`' skill **Ensure section exists** for `Context` linking `docs/building-blocks/system-context.md`.

