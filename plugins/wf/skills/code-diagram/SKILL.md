---
name: code-diagram
description: Document implementation-level code structure with a Mermaid class diagram. Use for class responsibilities, fields, methods, inheritance, interfaces, dependencies, composition, aggregation, and class-level deltas.
---

# Code Diagram

Show only elements relevant to what is being documented. Ground current-state elements in the actual codebase; use repository exploration instead of guessing.

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show relevant current classes and relationships with the template's colors unchanged.
- **Delta mode:** show changed classes/members/relationships plus minimum unchanged context, using the base palette plus the delta overlay below.

## 2. Open the template

Open [class-diagram-template.md](templates/class-diagram-template.md) before drafting. Its hidden comments own Mermaid syntax and relationship gotchas. Do not compose from memory.

Use a class diagram for implementation-level class responsibilities or relationships. Do not use it for deployable units, infrastructure topology, or process flow.

## 3. Delta overlay

Apply only in delta mode.

Mark added classes `:::added`, removed classes `:::removed`, changed classes `:::memberChanged` with `[add]`/`[rem]`-prefixed members. Add:

- `classDef added stroke:#4a7a5a,stroke-width:1px`
- `classDef removed stroke:#8a4a4a,stroke-width:1px`
- `classDef memberChanged stroke:#8b949e,stroke-width:1px,stroke-dasharray:5 5`

Show only new, modified, and deleted classes/fields/methods. Omit unchanged members of a changed class. Intermediate classes needed only to complete a connection stay unstyled and list only members used by that connection.

Do not copy delta styling into current mode.

**Done when:** the class template was opened this run; current mode uses the template's existing colors; delta mode includes only changed classes/members plus minimum context; no unused placeholder or hidden instruction remains.
