---
name: record-deployment-view
description: Document the system's production deployment topology in DEPLOYMENT.md — a C4 deployment diagram plus per-node hosting detail (VM host paths, Docker images/volumes/ports, orchestrated workloads, managed/serverless). Owns DEPLOYMENT.md and DEPLOYMENT-VIEW-FORMAT.md, and keeps ARCHITECTURE.md's Deployment View section pointing at it. Called by explicit user request.
---

# Record Deployment View

Record **where the building blocks actually run** — nodes, containers, host paths, and the connections between them — into `DEPLOYMENT.md` at the repo root. Template: [DEPLOYMENT-VIEW-FORMAT.md](./DEPLOYMENT-VIEW-FORMAT.md).

Inputs: `{{systemName}}`, `{{deploymentNodes}}`, `{{hostingModel}}`, `{{grillingContext}}`, `{{domainGlossary}}`.

No approval gate — record the topology as soon as it's identified.

## Lazy creation

Create `DEPLOYMENT.md` from [DEPLOYMENT-VIEW-FORMAT.md](./DEPLOYMENT-VIEW-FORMAT.md) on the first run; update it in place if it exists. It is not a bootstrap document — `bootstrap-docs` never creates it.

## Reuse the building blocks

Every `Container`/`ContainerDb`/`ContainerQueue` alias in the diagram is an existing `Services` row in `ARCHITECTURE.md` — same `{{mermaidComponentName}}`, so the two diagrams line up. An alias with no row is a gap: run `/record-service` skill for it first, then place it here.

## Pick the hosting-model block

Per deployment node, choose exactly one detail block from the template — **Virtual machine**, **Container**, **Orchestrated**, or **Managed / serverless**. A host running several models nests child `Deployment_Node`s, one per model, rather than merging blocks into one node.

Fill only what's established. An unknown port, image tag, or host path is left as a `{{placeholder}}` or omitted — never invented.

## Keep ARCHITECTURE.md pointing here

Run `/index-docs`' skill **Ensure section exists** for `Deployment View`, passing `{{skeletonContent}}` = the link to `DEPLOYMENT.md` plus 1-3 keyword-dense sentences naming the hosting model, node kinds, and runtime technologies — enough for an agent to decide whether to load the full document. Never edit `ARCHITECTURE.md` directly.

Re-run it whenever the hosting model or node set changes, so the stub's keywords still match the topology.

## Rules

- **Production only.** One target topology. Dev, CI, and staging variants belong in the repo's own dev docs, not here.
- **Runtime placement, not code structure.** What runs where, on which host, over which wire. Module layout and responsibilities stay in `Building blocks`.
- **Locations, never values.** Name the secret store, env var, or mounted file that carries a credential — never the credential.
- **Never batch.** Update `DEPLOYMENT.md` in the same change as the infrastructure shift it reflects.
