---
name: behavior-diagram
description: Document software behavior with a Mermaid flowchart, swimlane diagram, or sequence diagram. Use for process flows, decision paths, ownership handoffs, interaction order, cross-boundary calls, failure branching, and their deltas.
---

# Behavior Diagram

## When to use

Use this skill to document software behavior as one of:

### Flowchart

Show a process flow, decision path, or component wiring when ownership and message timing are not the primary concern.

### Swimlane Diagram

Show a cross-boundary process flow when ownership of each step matters. Use container lanes at Level 1 and component/module lanes inside one container at Level 2.

### Sequence Diagram

Show interaction order, cross-boundary calls, returns, activation, or failure branching when message order over time matters.

## Reference

Official Mermaid syntax:

- Flowchart: https://mermaid.ai/open-source/syntax/flowchart.html
- Swimlanes: https://mermaid.ai/open-source/syntax/swimlanes.html
- Sequence diagram: https://mermaid.ai/open-source/syntax/sequenceDiagram.html

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including requests such as `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show the relevant current behavior.
- **Delta mode:** show only added, modified, or removed behavior, plus the minimum unchanged context needed to connect it.

## 2. Select diagram and open its template

### Flowchart

Open [flowchart-template.md](templates/flowchart-template.md).

### Swimlane Diagram

Open [swimlane-diagram-template.md](templates/swimlane-diagram-template.md).

### Sequence Diagram

Open [sequence-diagram-template.md](templates/sequence-diagram-template.md).

Open the selected template before drafting. Follow its drawing, styling, delta, and Mermaid rules; do not compose from memory.

Ground current-state elements in the actual codebase or repository evidence. Do not guess. Show only elements relevant to what is being documented.

**Done when:** the selected template was opened this run; the selected diagram follows its rules; current mode uses the base palette; delta mode uses the diagram-specific delta rules and minimum context; no unused placeholder or instruction-only comment remains.
