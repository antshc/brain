# Flowchart Template

Official Mermaid flowchart syntax: https://mermaid.ai/open-source/syntax/flowchart.html

## Drawing rules

- Use Mermaid `flowchart` for a process flow, decision path, or component wiring.
- Show decision-relevant nodes and edges, not a full system topology.
- Use a swimlane diagram instead when ownership of steps matters.
- Use a sequence diagram instead when message order between participants matters.
- Ground current-state nodes and relationships in repository/code evidence. Do not invent behavior.
- Show only elements relevant to the requested scope.
- Prefer readable flow over exhaustive detail.

## Nodes and grouping

- `(["..."])` — external actor/start-like stadium node.
- `["..."]` — process or component rectangle.
- `[("...")]` — data store/repository cylinder.
- `{...}` — decision diamond when a branch is explicit.
- `subgraph Name ... end` — group related existing nodes without redeclaring them.
- Use short, stable node IDs and descriptive labels.
- Never use `click` as a node ID; it is a reserved Mermaid interaction keyword.

## Relationships

- `-->` — normal directed flow.
- `-- text -->` — directed flow with a condition or handoff label.
- `-.text.->` — deprecated, exceptional, or non-primary path.
- Relationship direction must match the actual process or data-flow direction.
- Label decisions and non-obvious handoffs with meaningful text.
- Use `flowchart TD` for top-down flows and `flowchart LR` for wide pipelines when it improves readability.

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

- Added node: `:::added` with `classDef added stroke:#4a7a5a,stroke-width:1px`.
- Removed node: `:::removed` with `classDef removed stroke:#8a4a4a,stroke-width:1px`.
- There is no class-diagram-style `memberChanged` equivalent. For a materially changed node, either style it as added when the replacement is what matters, or leave it base-styled and describe the change in prose.
- Show changed nodes/edges plus the minimum unchanged context needed to connect them.
- Omit unchanged nodes not needed to understand the delta.
- Do not apply delta styling in current mode.

## Mermaid constraints and gotchas

- A `subgraph` can group existing nodes and can itself be an edge target.
- Mermaid parsing can report a reserved-ID error on a later edge instead of the offending node declaration; avoid `click` as an ID.
- Pick `TD` or `LR` based on readability rather than convention.
- Delete unused placeholders and example nodes from the final diagram.

## Output template

Replace all placeholders with real behavior. Add or remove nodes, groups, and relationships to match the actual scope.

<details>
<summary>{{title}}</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: {{diagramId}}
flowchart TD
    {{actor}}(["{{actorLabel}}"])
    {{boundary}}["{{boundaryClass}}"]
    {{owner}}["{{capabilityOwnerClass}}"]
    {{store}}[("{{dependencyRepository}}")]

    {{actor}} --> {{boundary}}
    {{boundary}} --> {{owner}}
    {{owner}} --> {{store}}
    {{owner}} -- {{condition}} --> {{store}}

    subgraph {{infrastructureGroup}}
        {{store}}
    end

    classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

</details>
