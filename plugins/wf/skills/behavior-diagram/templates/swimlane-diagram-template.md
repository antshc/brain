# Swimlane Diagram Template

Official Mermaid swimlane syntax: https://mermaid.ai/open-source/syntax/swimlanes.html

## Drawing rules

- Use Mermaid `swimlane-beta` when ownership of each step is a design decision.
- Use one ownership kind per diagram: containers at Level 1 or components/modules inside one container at Level 2.
- Do not mix ownership kinds such as teams, statuses, containers, and components in the same view.
- Ground current-state lanes, steps, and handoffs in repository/code evidence. Do not invent behavior.
- Show only decision-relevant lanes and steps.
- Split a large flow into Level 1 plus one or more Level 2 diagrams when a single view becomes hard to follow.
- `swimlane-beta` is experimental in Mermaid 11.16.0+. Confirm the target renderer supports it. If not, fall back to a `flowchart` with one `subgraph` per lane.

## Lane levels

### Level 1 — Container swimlane

- Each lane is a deployable/runnable container such as a GUI, REST API, database, queue, or worker.
- Include container name and type in the lane label, for example `[Order API - REST API]`.
- Group co-deployed artifacts that form one operational unit into one lane. A Linux service plus Bash scripts plus Ansible playbooks it runs is usually one container, not separate lanes.

### Level 2 — Component swimlane

- Scope the diagram to one Level 1 container.
- Each lane is a component/module inside that container, such as a controller, service, page, or repository.
- Include component name and type in the lane label, for example `[OrderController - Controller]`.
- Include Level 2 only when internal component ownership is decision-relevant.

## Nodes and handoffs

- `id([Text])` — start/end-like stadium node.
- `id[Text]` — task/activity rectangle.
- `id{Text}` — decision diamond.
- Put a decision node in the lane that owns the decision.
- Label every cross-lane edge with what is handed off: request, response, event, data, or condition.
- Prefix every edge label with its execution-order number, for example `1. request`.
- For mutually exclusive branches, use suffixes such as `3a.` and `3b.` and retain the suffix until branches rejoin.
- Use short, stable node IDs and descriptive labels.

## Current-mode styling

Use the repo dark palette.

```text
lineColor: #8b949e
fill: #242424
stroke: #8b949e
text: #c9d1d9
```

Keep this initialization and default class definition in current mode:

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

## Delta-mode styling

Apply only when `SKILL.md` selects **delta mode**.

Define:

```mermaid
classDef added stroke:#4a7a5a,stroke-width:1px
classDef removed stroke:#8a4a4a,stroke-width:1px
```

Then style each changed node with a separate statement:

```mermaid
class nodeId added;
class oldNodeId removed;
```

- Swimlane nodes use `class nodeId className;`; do not rely on the inline `id:::class` shorthand.
- A lane that is entirely new or removed has no supported Mermaid `subgraph` border-color hook; call out the lane state in prose.
- Show changed nodes/handoffs plus the minimum unchanged lanes and nodes needed to connect them.
- Omit unchanged lanes and nodes not needed to understand the delta.
- Do not apply delta styling in current mode.

## Mermaid constraints and gotchas

- `swimlane-beta` optionally accepts `TB`, `TD`, `BT`, `LR`, or `RL`; it defaults to `TB`.
- Each top-level `subgraph id [Label] ... end` becomes one lane.
- Avoid parentheses inside `[Label]` lane labels; they can break parsing.
- Do not use curly braces inside node label text for placeholders; Mermaid interprets `{` as a decision-node delimiter.
- Never use `click` as a node ID; it is a reserved Mermaid interaction keyword.
- Use separate `class` statements for swimlane node styling.
- Delete unused placeholders, lanes, and nodes from the final diagram.

## Output template

Replace all placeholders with real behavior. Include only the level or levels needed for the requested scope.

### Level 1 — Container Swimlane: {{title}}

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

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

</details>

### Level 2 — Component Swimlane: {{title}} inside {{containerName}}

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

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

</details>
