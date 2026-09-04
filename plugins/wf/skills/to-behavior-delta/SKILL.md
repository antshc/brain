---
name: to-behavior-delta
description: Write a Mermaid diagram delta into a feature design document — a solution-level C4 container/solution diagram, a flowchart delta, or an implementation-level class diagram delta, sequence diagram delta, or deployment view delta. Use whenever a feature design document needs a decision-relevant diagram showing what changed (added/removed/modified nodes, classes, steps, or deployment topology) — even if the user just says "add a diagram" or "show the deployment change" without naming this skill.
---

Show only the diagram delta — decision-relevant elements added, modified, or removed for this capability, never a full system inventory. Each template's own hidden comments carry its full Mermaid element reference and gotchas; open the template file before drafting, do not compose from memory.

| Kind | Use for | Template |
| --- | --- | --- |
| Solution Diagram (`C4Container`) | Deployable/runnable containers and the actors/external systems around them, solution-level | [c4-container-diagram-template.md](templates/c4-container-diagram-template.md) |
| Flowchart delta | Solution-level process flow, decision path, or component wiring | [flowchart-delta-template.md](templates/flowchart-delta-template.md) |
| Class diagram delta | Implementation-level class responsibilities or relationships, decided | [class-diagram-delta-template.md](templates/class-diagram-delta-template.md) |
| Sequence diagram delta | Implementation-level interaction order, cross-boundary calls, or failure branching, decided | [sequence-diagram-delta-template.md](templates/sequence-diagram-delta-template.md) |
| Deployment view delta | Deployment topology, hosting, or infrastructure node changes for the feature | [deployment-view-delta-template.md](templates/deployment-view-delta-template.md) |

**Done when:** the requested diagram's template was opened this run; only elements the capability adds, modifies, or removes are styled or included (plus the minimum unstyled elements needed to connect them); the diagram uses the template's own delta styling convention (`:::added`/`:::removed`/`:::memberChanged` for flowchart/class, `UpdateElementStyle` border-color convention for C4Container/C4Deployment, `NEW:`/`CHANGED:` labels for sequence); no unused example element or hidden instruction remains.
