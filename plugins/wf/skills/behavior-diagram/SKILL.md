---
name: behavior-diagram
description: Document software behavior with a Mermaid flowchart, swimlane diagram, or sequence diagram. Use for process flows, decision paths, ownership handoffs, interaction order, cross-boundary calls, failure branching, and their deltas.
---

# Behavior Diagram

Show only elements relevant to what is being documented. Ground current-state elements in the actual codebase; use repository exploration instead of guessing.

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show relevant current behavior with the selected template's colors unchanged.
- **Delta mode:** show changed elements plus minimum unchanged context, with the selected template's base colors plus the delta rules below.

## 2. Select and open the template

Open the matching template before drafting; do not compose from memory.

### Flowchart

Solution-level process flow, decision path, or component wiring. Use Swimlane instead when ownership of steps matters; use Sequence instead when message order between participants matters. Template: [flowchart-template.md](templates/flowchart-template.md).

### Swimlane Diagram

Cross-boundary process flow where ownership is the decision. Level 1 lanes are containers; Level 2 lanes are components/modules inside one container. Use Flowchart when ownership does not matter; use Sequence when message order over time is the focus. Template: [swimlane-diagram-template.md](templates/swimlane-diagram-template.md).

### Sequence Diagram

Interaction order, cross-boundary calls, or failure branching. Use Swimlane when step ownership is the decision rather than message order. Template: [sequence-diagram-template.md](templates/sequence-diagram-template.md).

## 3. Delta overlay

Apply only in delta mode.

### Flowchart

Mark added nodes `:::added` and removed nodes `:::removed`; add `classDef added stroke:#4a7a5a,stroke-width:1px` and `classDef removed stroke:#8a4a4a,stroke-width:1px`. There is no `memberChanged` equivalent: restyle a materially changed node as added, or leave it unstyled and describe the change in prose. Omit unchanged nodes not needed to connect the delta.

### Swimlane Diagram

Style changed nodes with `classDef added ...` / `classDef removed ...` plus a separate `class nodeId added;` / `class nodeId removed;` statement per node. A lane that is entirely new or removed has no supported Mermaid border-color hook on `subgraph`; call it out in prose. Omit unchanged nodes and lanes not needed to connect the delta.

### Sequence Diagram

Mermaid sequence diagrams have no `:::` styling mechanism. Mark a new, changed, or removed step with a `note over` call-out or a leading `NEW:` / `CHANGED:` / `REMOVED:` label in message text. Use `REMOVED:` for a call that no longer happens but must stay visible for context. Omit lifelines and messages that are unchanged and not needed to connect the delta.

Do not copy delta styling into current mode.

**Done when:** the matching template was opened this run; current mode uses the template's existing colors; delta mode contains only changed behavior plus minimum context; the diagram kind uses its own rules; no unused placeholder or hidden instruction remains.
