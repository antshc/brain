## Swimlane Diagram

<!-- Include only when "who owns this step" (which container, or which component/module inside one container) is itself a design decision — not merely step order. If ownership doesn't matter, use the flowchart instead; if the focus is messages over time between participants, use the sequence diagram instead. Delete this instruction. -->

<!-- `swimlane-beta` is a beta/experimental Mermaid diagram type (v11.16.0+) — confirm the rendering toolchain (mmdc, VS Code preview, GitHub) supports it before relying on it. Delete this instruction. -->

<!-- Mermaid technical gotchas and good practices (mermaid.ai/open-source/syntax/swimlanes.html#good-practices), consistent with the flowchart conventions:
- `swimlane-beta` (optionally followed by `TB`/`TD`/`BT`/`LR`/`RL`; defaults to `TB`) starts the diagram. Each top-level `subgraph id [Label] ... end` becomes one lane.
- Make each lane mean one kind of ownership — one container (Level 1) or one component/module (Level 2). Don't mix ownership kinds (e.g. a team lane next to a status lane) in the same diagram.
- Node shapes reuse flowchart syntax: `id([Text])` stadium for a start/end step, plain `id[Text]` rectangle for a task/activity, `id{Text}` diamond for a branching decision.
- Label every cross-lane edge (`A -->|label| B`) with what's handed off — a request, response, or condition. An unlabeled cross-lane arrow hides the handoff that's the point of the diagram.
- Put a decision node in the lane that owns/makes that decision, then route its labeled outcomes to the lanes that act on them.
- Split into Level 1 + Level 2 (or multiple Level 2 diagrams, one per container) rather than one large diagram once a single view stops being readable without tracing every arrow twice.
- Use short, stable node ids; put the descriptive text in the label so relabeling later doesn't break edges.
Delete this instruction. -->

### Level 1 — Container Swimlane: {{title}}

<!-- Lanes are containers (the deployable/runnable units from the Solution Diagram — GUI, REST API service, database, queue). Show which container performs each step of the flow. Delete this instruction. -->

<details>
<summary>{{title}} — container swimlane</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
swimlane-beta TB
  subgraph {{actorLane}} [{{actorLaneLabel}}]
    {{startNode}}([{{startLabel}}])
  end

  subgraph {{entryContainerLane}} [{{entryContainerName}}]
    {{entryStep}}[{{entryStepLabel}}]
  end

  subgraph {{ownerContainerLane}} [{{capabilityOwnerContainerName}}]
    {{decisionNode}}{{{decisionLabel}}}
    {{processStep}}[{{processStepLabel}}]
  end

  subgraph {{storeContainerLane}} [{{dataStoreContainerName}}]
    {{persistStep}}[{{persistLabel}}]
  end

  {{startNode}} -->|{{handoff1}}| {{entryStep}}
  {{entryStep}} -->|{{handoff2}}| {{decisionNode}}
  {{decisionNode}} -->|{{noOutcome}}| {{entryStep}}
  {{decisionNode}} -->|{{yesOutcome}}| {{processStep}}
  {{processStep}} -->|{{handoff3}}| {{persistStep}}

  classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
</details>

### Level 2 — Component Swimlane: {{title}} inside {{containerName}}

<!-- Scoped to one container from Level 1. Lanes are the components/modules inside that container (e.g. GUI pages, REST API controllers/modules). Show which component performs each step of the flow inside that container. Include only when internal component wiring, not just the container-level flow, is a design decision. Delete this instruction. -->

<details>
<summary>{{title}} — component swimlane ({{containerName}})</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
swimlane-beta TB
  subgraph {{entryComponentLane}} [{{entryComponentName}}]
    {{receiveStep}}([{{receiveLabel}}])
  end

  subgraph {{ownerComponentLane}} [{{capabilityOwnerComponentName}}]
    {{validateNode}}{{{validateLabel}}}
    {{moduleStep}}[{{moduleStepLabel}}]
  end

  subgraph {{dependencyComponentLane}} [{{dependencyComponentName}}]
    {{delegateStep}}[{{delegateLabel}}]
  end

  {{receiveStep}} -->|{{handoff1}}| {{validateNode}}
  {{validateNode}} -->|{{noOutcome}}| {{receiveStep}}
  {{validateNode}} -->|{{yesOutcome}}| {{moduleStep}}
  {{moduleStep}} -->|{{handoff2}}| {{delegateStep}}

  classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
</details>

<!-- Delete unused example lanes/nodes. Include only the level(s) that are decision-relevant. -->
