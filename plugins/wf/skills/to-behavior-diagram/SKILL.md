---
name: to-behavior-diagram
description: Document current behavior with a single Mermaid diagram — a solution-level C4 container/solution diagram, a flowchart, a swimlane diagram, or an implementation-level class diagram, sequence diagram, or deployment view. Use whenever a document needs a diagram showing how a capability, process, or system currently behaves — even if the user just says "add a diagram", "show the deployment", or "diagram this flow" without naming this skill. A caller that needs a *delta* (only what a capability adds/changes/removes) follows `/to-behavior-delta` skill, which applies its own delta-styling overlay on top of the diagram this skill produces.
---

Show only the elements relevant to what's being documented — never a full, unrelated system inventory. Each template's own hidden comments carry its full Mermaid element reference and gotchas; open the template file before drafting, do not compose from memory.

## Solution Diagram

Deployable/runnable containers and the actors/external systems around them, solution-level. Render as Mermaid `C4Container`. Template: [c4-container-diagram-template.md](templates/c4-container-diagram-template.md).

## Flowchart

Solution-level process flow, decision path, or component wiring. Template: [flowchart-template.md](templates/flowchart-template.md).

## Swimlane Diagram

Cross-boundary process flow where ownership is the decision — Level 1 lanes are containers, Level 2 lanes are components/modules inside one container. Template: [swimlane-diagram-template.md](templates/swimlane-diagram-template.md).

## Class Diagram

Implementation-level class responsibilities or relationships. Template: [class-diagram-template.md](templates/class-diagram-template.md).

## Sequence Diagram

Implementation-level interaction order, cross-boundary calls, or failure branching. Template: [sequence-diagram-template.md](templates/sequence-diagram-template.md).

## Deployment View

Deployment topology, hosting, or infrastructure nodes. Template: [deployment-view-template.md](templates/deployment-view-template.md).

**Done when:** the requested diagram's template was opened this run; the diagram includes only elements relevant to what's being documented (plus the minimum unstyled elements needed to connect them); no unused example element or hidden instruction remains.
