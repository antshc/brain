---
name: to-diagram
description: Document behavior with a Mermaid diagram — a solution-level C4 container/solution diagram, flowchart, swimlane diagram, class diagram, sequence diagram, or deployment view. Use for current-state diagrams and diagram deltas. When the user asks for a delta, changes, additions, removals, or modifications, use delta mode and the delta color overlay.
---

# To Diagram

Show only elements relevant to what is being documented. Ground current-state elements in the actual codebase; use repository exploration instead of guessing.

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including requests such as `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show the relevant current behavior and use the matching template's existing color schema unchanged.
- **Delta mode:** show only added, modified, or removed elements, plus the minimum unchanged context needed to connect them. Use the matching template's existing base colors plus the delta overlay below.

## 2. Select and open the template

Each template's hidden comments contain its Mermaid element reference and gotchas. Open the matching template before drafting; do not compose from memory.

### Solution / Container Diagram

Deployable/runnable containers and the actors/external systems around them, solution-level. Render as Mermaid `C4Container`. Template: [c4-container-diagram-template.md](templates/c4-container-diagram-template.md).

### Flowchart

Solution-level process flow, decision path, or component wiring. Template: [flowchart-template.md](templates/flowchart-template.md).

### Swimlane Diagram

Cross-boundary process flow where ownership is the decision — Level 1 lanes are containers, Level 2 lanes are components/modules inside one container. Template: [swimlane-diagram-template.md](templates/swimlane-diagram-template.md).

### Class Diagram

Implementation-level class responsibilities or relationships. Template: [class-diagram-template.md](templates/class-diagram-template.md).

### Sequence Diagram

Implementation-level interaction order, cross-boundary calls, or failure branching. Template: [sequence-diagram-template.md](templates/sequence-diagram-template.md).

### Deployment View

Deployment topology, hosting, or infrastructure nodes. Template: [deployment-view-template.md](templates/deployment-view-template.md).

## 3. Delta overlay

Apply only in delta mode.

- **Solution / Container Diagram:** C4 has no `classDef` / `:::`. Use `UpdateElementStyle(alias, $borderColor="...")`: added `#4a7a5a`, removed `#8a4a4a`, modified or unchanged connection context `#8b949e`. Use the same colors with `UpdateRelStyle(..., $lineColor="...")` for added/removed relationships. Show only changed containers/systems/actors plus minimum context. Add a `**Behaviour changes**` bullet list using `+` / `-` / `~` for modified elements whose change is not visible from added/removed topology.
- **Class Diagram:** mark added classes `:::added`, removed classes `:::removed`, changed classes `:::memberChanged` with `[add]`/`[rem]`-prefixed members; add `classDef added stroke:#4a7a5a,stroke-width:2px`, `classDef removed stroke:#8a4a4a,stroke-width:2px`, and `classDef memberChanged stroke:#8b949e,stroke-width:2px,stroke-dasharray:5 5`. Show only new, modified, and deleted classes/fields/methods; omit unchanged members of a changed class. Intermediate classes needed only to complete a connection stay unstyled and list only members used by that connection.
- **Flowchart:** mark added nodes `:::added` and removed nodes `:::removed`; add `classDef added stroke:#4a7a5a,stroke-width:2px` and `classDef removed stroke:#8a4a4a,stroke-width:2px`. There is no `memberChanged` equivalent: restyle a materially changed node as added, or leave it unstyled and describe the change in prose. Omit unchanged nodes not needed to connect the delta.
- **Swimlane Diagram:** use the same `:::added` / `:::removed` convention and colors as Flowchart. A lane that is itself entirely new or removed has no supported Mermaid border-color hook on `subgraph`; call it out in prose. Omit unchanged nodes and lanes not needed to connect the delta.
- **Sequence Diagram:** Mermaid sequence diagrams have no `:::` styling mechanism. Mark a new or changed step with a `note over` call-out or a leading `NEW:` / `CHANGED:` label in the message text. Omit lifelines and messages that are unchanged and not needed to connect the delta.
- **Deployment View:** use `UpdateElementStyle(alias, $borderColor="...")`: added `#4a7a5a`, removed `#8a4a4a`, unchanged context `#8b949e`. Add a `**Behaviour changes**` bullet list using `+` / `-` / `~` for in-place node changes not visible through added/removed elements, such as resized instances, runtime changes, or scaling-policy changes. Omit the list when none exist.

Do not copy delta styling into current mode. Current mode uses the base palette; delta mode uses the delta overlay.

**Done when:** the matching template was opened this run; current mode uses the template's existing colors; delta mode uses the delta overlay and includes only changed elements plus minimum context; the diagram kind uses its own rules; no unused placeholder or hidden instruction remains.
