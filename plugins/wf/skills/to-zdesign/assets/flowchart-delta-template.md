## Block Diagrams (Flowcharts)

### {{capabilityTitle}}

<!-- Include only when a process flow, decision path, or component wiring is a design decision for this capability. Show decision-relevant nodes and edges, not a full system topology. Delete this instruction. -->

<!-- This diagram shows the flow DELTA for this capability: mark a node added (`:::added`) or removed (`:::removed`). There is no `:::memberChanged` equivalent for flowchart nodes — a changed node is either restyled as `:::added` (if its role is materially new) or left unstyled and described in prose. Omit unchanged nodes not needed to connect the delta. Delete this instruction. -->

<!-- Mermaid technical gotchas (verified against `mmdc` 11.16.0), consistent with the class diagram conventions:
- Node shape signals role: `(["..."])` stadium for an external actor, plain `["..."]` rectangle for a process/component, `[("...")]` cylinder for a data store/repository.
- `flowchart TD` lays out top-down; `flowchart LR` reads better for pipelines with many parallel branches. Pick whichever keeps the diagram narrower than tall (or vice versa).
- Solid arrow (`-->`) is the default edge; a labeled solid arrow (`-- text -->`) documents the condition for that edge; a dotted arrow (`-.text.->`) marks a deprecated or exceptional path.
- `subgraph Name ... end` groups existing nodes into a labeled box without redeclaring them; a `subgraph` can itself be the target of an edge.
- `classDef`/`:::` statements must come after the nodes they style are declared.
Delete this instruction. -->

<details>
<summary>{{capabilityTitle}}</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
flowchart TD
    {{actor}}(["{{actorLabel}}"])
    {{boundary}}["{{boundaryClass}}"]
    {{owner}}["{{capabilityOwnerClass}}"]
    {{store}}[("{{dependencyRepository}}")]
    {{newNode}}["{{newComponent}}"]:::added
    {{removedNode}}["{{deletedComponent}}"]:::removed

    {{actor}} --> {{boundary}}
    {{boundary}} --> {{owner}}
    {{owner}} --> {{store}}
    {{owner}} -- {{condition}} --> {{newNode}}
    {{owner}} -. deprecated .-> {{removedNode}}

    subgraph {{infrastructureGroup}}
        {{store}}
        {{removedNode}}
    end

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
    classDef added stroke:#4a7a5a,stroke-width:2px
    classDef removed stroke:#8a4a4a,stroke-width:2px
```
</details>

<!-- `added` = solid green border, new node. `removed` = solid red border, deleted node. `subgraph` groups existing nodes into a labeled box. Delete unused example nodes/classDefs/subgraphs. -->
