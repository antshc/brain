---
name: doc-diagram
description: >-
  Create Mermaid architecture, flowchart, swimlane, sequence, and class diagrams. Use whenever a task needs a Mermaid diagram to show system structure, process flow, responsibility handoffs, call order, type relationships, or proposed changes.
argument-hint: "[diagram type] [current | delta] [scope]"
---

# Document a Diagram

1. **Select type and mode.** Honor the diagram type named by the caller. Otherwise infer the view from the question in the table. Ask which view if the scope leaves the choice ambiguous. Default to current mode. Use delta mode for requests to show changes. Done when the requested view and mode are known.
2. **Load and draft.** Read the selected tactic in full. Apply Architecture's **Delta routing** if needed, then open the template for the resulting view before drafting. Follow the template's drawing, styling, delta, and Mermaid rules. Ground the diagram in codebase or repository evidence. In delta mode, show added, modified, or removed elements plus the minimum unchanged context. In current mode use the base palette. Done when the diagram matches the selected view and mode and contains no unused placeholders or instruction comments.
3. **Assign a stable ID.** Reuse the ID when redrawing. For a new diagram, pick a kebab-case ID naming the subject and view. Put `%% diagram-id: {{diagramId}}` on its own line where the tactic specifies. The ID keys the Confluence attachment and Draw.io record that the `atlassian` skill's Publish page tactic publishes. Done when the diagram has one ID, unique within the target file.
4. **Check the result.** Apply the selected tactic's checks. For behavior diagrams run the layout script as specified under **Render and check order**. Done when those checks pass.

| View | Select for | Tactic | Template |
| --- | --- | --- | --- |
| System Context Diagram | One system, its actors, and external integrations | [Architecture](tactics/architecture.md) | [System context](templates/system-context-template.md) |
| Container Diagram | Deployables and their dependencies | Architecture | [Container](templates/container-diagram-template.md) |
| Component Diagram | Responsibilities within one deployable | Architecture | [Component](templates/component-diagram-template.md) |
| Deployment View | Hosting topology and runtime placement | Architecture | [Deployment](templates/deployment-view-template.md) |
| Flowchart | Process, decisions, branching, or wiring | [Behavior](tactics/behavior.md) | [Flowchart](templates/flowchart-template.md) |
| Swimlane Diagram | Step ownership and responsibility handoffs | Behavior | [Swimlane](templates/swimlane-diagram-template.md) |
| Sequence Diagram | Call order, responses, and interactions | Behavior | [Sequence](templates/sequence-diagram-template.md) |
| Class Diagram | Types, interfaces, members, and relationships | [Code](tactics/code.md) | [Class](templates/class-diagram-template.md) |
