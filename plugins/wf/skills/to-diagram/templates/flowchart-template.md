## Flowchart

### {{title}}

<!-- Include only when a process flow, decision path, or component wiring is a design decision. Show decision-relevant nodes and edges, not a full system topology. Delete this instruction. -->

<!-- Mermaid technical gotchas (verified against `mmdc` 11.16.0), consistent with the class diagram conventions:
- Node shape signals role: `(["..."])` stadium for an external actor, plain `["..."]` rectangle for a process/component, `[("...")]` cylinder for a data store/repository.
- `flowchart TD` lays out top-down; `flowchart LR` reads better for pipelines with many parallel branches. Pick whichever keeps the diagram narrower than tall (or vice versa).
- Solid arrow (`-->`) is the default edge; a labeled solid arrow (`-- text -->`) documents the condition for that edge; a dotted arrow (`-.text.->`) marks a deprecated or exceptional path.
- `subgraph Name ... end` groups existing nodes into a labeled box without redeclaring them; a `subgraph` can itself be the target of an edge.
Delete this instruction. -->

<details>
<summary>{{title}}</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
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

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
</details>

<!-- `subgraph` groups existing nodes into a labeled box. Delete unused example nodes/subgraphs. -->
