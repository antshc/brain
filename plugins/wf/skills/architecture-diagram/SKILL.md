---
name: architecture-diagram
description: Document software architecture with a Mermaid solution-level C4 container diagram or deployment view. Use for current-state architecture and architecture deltas, including added, removed, or modified containers, systems, actors, relationships, hosts, runtimes, or deployment nodes.
---

# Architecture Diagram

Show only elements relevant to what is being documented. Ground current-state elements in the actual codebase; use repository exploration instead of guessing.

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including requests such as `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show the relevant current architecture and use the matching template's existing color schema unchanged.
- **Delta mode:** show only added, modified, or removed elements, plus the minimum unchanged context needed to connect them. Use the matching template's existing base colors plus the delta overlay below.

## 2. Select and open the template

Each template's hidden comments contain its Mermaid element reference and gotchas. Open the matching template before drafting; do not compose from memory.

### Solution / Container Diagram

Deployable/runnable containers and the actors/external systems around them, solution-level. Render as Mermaid `C4Container`. Template: [c4-container-diagram-template.md](templates/c4-container-diagram-template.md).

### Deployment View

Deployment topology, hosting, or infrastructure nodes. Template: [deployment-view-template.md](templates/deployment-view-template.md).

## 3. Delta overlay

Apply only in delta mode.

### Solution / Container Diagram

C4 has no `classDef` / `:::`. Use `UpdateElementStyle(alias, $borderColor="...")`: added `#4a7a5a`, removed `#8a4a4a`, modified or unchanged connection context `#8b949e`. Use the same colors with `UpdateRelStyle(..., $lineColor="...")` for added/removed relationships. Show only changed containers/systems/actors plus minimum context. Add a `**Behaviour changes**` bullet list using `+` / `-` / `~` for modified elements whose change is not visible from added/removed topology.

### Deployment View

Use `UpdateElementStyle(alias, $borderColor="...")`: added `#4a7a5a`, removed `#8a4a4a`, unchanged context `#8b949e`. Add a `**Behaviour changes**` bullet list using `+` / `-` / `~` for in-place node changes not visible through added/removed elements, such as resized instances, runtime changes, or scaling-policy changes. Omit the list when none exist.

Do not copy delta styling into current mode. Current mode uses the base palette; delta mode uses the delta overlay.

**Done when:** the matching template was opened this run; current mode uses the template's existing colors; delta mode uses the delta overlay and includes only changed elements plus minimum context; the diagram kind uses its own rules; no unused placeholder or hidden instruction remains.
