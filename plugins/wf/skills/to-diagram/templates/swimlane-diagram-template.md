## Swimlane Diagram

<!-- Include only when "who owns this step" (which container, or which component/module inside one container) is itself a design decision — not merely step order. If ownership doesn't matter, use the flowchart instead; if the focus is messages over time between participants, use the sequence diagram instead. Delete this instruction. -->

<!-- `swimlane-beta` is a beta/experimental Mermaid diagram type (v11.16.0+) — confirm the rendering toolchain (mmdc, VS Code preview, GitHub) supports it before relying on it. Delete this instruction. -->

<!-- Mermaid technical gotchas and good practices (mermaid.ai/open-source/syntax/swimlanes.html#good-practices), consistent with the flowchart conventions:
- `swimlane-beta` (optionally followed by `TB`/`TD`/`BT`/`LR`/`RL`; defaults to `TB`) starts the diagram. Each top-level `subgraph id [Label] ... end` becomes one lane. Include the container or component type in the lane label separated by a dash (e.g. `[Web Portal - GUI]`, `[Order Service - REST API]`, `[Database Name - Database]`). Do not use parentheses `()` inside the `[Label]` brackets as it can break parsing.
- Do not use curly braces `{}` inside any node label text (e.g. a placeholder like `{build_number}`) — Mermaid's parser reads `{` as the start of a diamond/decision node and errors even mid-label (e.g. `got 'DIAMOND_START'`). Write placeholders without braces (`build-number`, `build_number value`) instead.
- Make each lane mean one kind of ownership — one container (Level 1) or one component/module (Level 2). Don't mix ownership kinds (e.g. a team lane next to a status lane) in the same diagram.
- Node shapes reuse flowchart syntax: `id([Text])` stadium for a start/end step, plain `id[Text]` rectangle for a task/activity, `id{Text}` diamond for a branching decision.
- Label every cross-lane edge with what's handed off — a request, response, or condition. An unlabeled cross-lane arrow hides the handoff that's the point of the diagram.
- Prefix every edge label with its execution-order step number (for example, `1. request`). For mutually exclusive outcomes from a decision, use the same number plus a branch suffix (for example, `3a. rejected` and `3b. approved`), then retain that suffix for following steps until the branches rejoin.
- Put a decision node in the lane that owns/makes that decision, then route its labeled outcomes to the lanes that act on them.
- Split into Level 1 + Level 2 (or multiple Level 2 diagrams, one per container) rather than one large diagram once a single view stops being readable without tracing every arrow twice.
- Use short, stable node ids; put the descriptive text in the label so relabeling later doesn't break edges.
Delete this instruction. -->

### Level 1 — Container Swimlane: {{title}}

<!-- Lanes are containers (the deployable/runnable units from the Solution Diagram — GUI, REST API service, database, queue). Include the container type or technology in the lane label separated by a dash (e.g. [Web Portal - GUI], [Order API - REST API], [Database Name - Database]). Show which container performs each step of the flow. Delete this instruction. -->

<details>
<summary>{{title}} — container swimlane</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
swimlane-beta TB
  subgraph {{actorLane}} [{{actorLaneLabel}} - {{actorType}}]
    {{startNode}}([{{startLabel}}])
  end

  subgraph {{entryContainerLane}} [{{entryContainerName}} - {{entryContainerType}}]
    {{entryStep}}[{{entryStepLabel}}]
  end

  subgraph {{ownerContainerLane}} [{{capabilityOwnerContainerName}} - {{ownerContainerType}}]
    {{decisionNode}}{{{decisionLabel}}}
    {{processStep}}[{{processStepLabel}}]
  end

  subgraph {{storeContainerLane}} [{{dataStoreContainerName}} - {{storeContainerType}}]
    {{persistStep}}[{{persistLabel}}]
  end

  {{startNode}} -->|1. {{handoff1}}| {{entryStep}}
  {{entryStep}} -->|2. {{handoff2}}| {{decisionNode}}
  {{decisionNode}} -->|3a. {{noOutcome}}| {{entryStep}}
  {{decisionNode}} -->|3b. {{yesOutcome}}| {{processStep}}
  {{processStep}} -->|4b. {{handoff3}}| {{persistStep}}

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
</details>

### Level 2 — Component Swimlane: {{title}} inside {{containerName}}

<!-- Scoped to one container from Level 1. Lanes are the components/modules inside that container (e.g. GUI pages, REST API controllers/modules). Include the component type in the lane label separated by a dash (e.g. [OrderController - Controller], [OrderService - Service]). Show which component performs each step of the flow inside that container. Include only when internal component wiring, not just the container-level flow, is a design decision. Delete this instruction. -->

<details>
<summary>{{title}} — component swimlane ({{containerName}})</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
swimlane-beta TB
  subgraph {{entryComponentLane}} [{{entryComponentName}} - {{entryComponentType}}]
    {{receiveStep}}([{{receiveLabel}}])
  end

  subgraph {{ownerComponentLane}} [{{capabilityOwnerComponentName}} - {{ownerComponentType}}]
    {{validateNode}}{{{validateLabel}}}
    {{moduleStep}}[{{moduleStepLabel}}]
  end

  subgraph {{dependencyComponentLane}} [{{dependencyComponentName}} - {{dependencyComponentType}}]
    {{delegateStep}}[{{delegateLabel}}]
  end

  {{receiveStep}} -->|1. {{handoff1}}| {{validateNode}}
  {{validateNode}} -->|2a. {{noOutcome}}| {{receiveStep}}
  {{validateNode}} -->|2b. {{yesOutcome}}| {{moduleStep}}
  {{moduleStep}} -->|3b. {{handoff2}}| {{delegateStep}}

  classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
</details>

<!-- Delete unused example lanes/nodes. Include only the level(s) that are decision-relevant. -->
