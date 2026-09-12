---
name: code-diagram
description: Document implementation-level code structure with a Mermaid class diagram. Use for class responsibilities, fields, methods, inheritance, interfaces, dependencies, composition, aggregation, and class-level deltas.
---

# Code Diagram

## When to use

Use this skill to document implementation-level code structure as a Mermaid class diagram.

### Class Diagram

Show class responsibilities, fields, methods, inheritance, interfaces, dependencies, composition, aggregation, and class-level changes.

Do not use it for deployable units, infrastructure topology, or process flow.

## Reference

Official Mermaid class diagram syntax: https://mermaid.ai/open-source/syntax/classDiagram.html

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including requests such as `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show the relevant current classes and relationships.
- **Delta mode:** show only added, modified, or removed classes, members, or relationships, plus the minimum unchanged context needed to connect them.

## 2. Open the template

Open [class-diagram-template.md](templates/class-diagram-template.md) before drafting.

Follow its drawing, styling, delta, relationship, and Mermaid rules; do not compose from memory.

Ground current-state elements in the actual codebase or repository evidence. Do not guess. Show only elements relevant to what is being documented.

**Done when:** the class template was opened this run; current mode uses the base palette; delta mode uses the class-specific delta rules and minimum context; no unused placeholder or instruction-only comment remains.

## 3. Assign a diagram id

`diagramId := kebab-case id naming this diagram's subject and view, unique within the file it lands in, e.g. `order-domain-classes``

Write it as `%% diagram-id: {{diagramId}}` on its own line — after the `%%{init: …}%%` theme directive and immediately above the `classDiagram` line, as the output template shows.

The id is the diagram's published identity: `/publish-page` names its Confluence attachment and Draw.io record after it, so a republish replaces that diagram in place. Redrawing a diagram that already carries an id keeps that id; a fresh id publishes a second copy beside the old one.

**Done when:** the diagram carries exactly one `%% diagram-id` line, reused from the diagram it redraws when there is one, and unique among the ids already in the target file.
