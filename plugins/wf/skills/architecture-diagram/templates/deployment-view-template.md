# Deployment View Template

Official Mermaid C4 syntax: https://mermaid.ai/open-source/syntax/c4.html

## Drawing rules

- Render deployment views as Mermaid `C4Deployment`.
- Show only decision-relevant deployment topology, hosting, runtimes, and deployed containers.
- Prefer deployment semantics over exhaustive production topology.
- Ground current-state elements in repository/code evidence. Do not invent hosts, runtimes, or services.
- Group artifacts that ship and run together into one deployable container.

## C4 element reference

- `Deployment_Node(alias, "Label", "Type", "Description") { ... }` — deployment environment, data center, host, VM, device, cluster, runtime, or infrastructure node.
- `Node(alias, "Label", "Type", "Description") { ... }` — short form of `Deployment_Node`; use when it improves readability.
- `Node_L` / `Node_R` — left/right aligned deployment-node variants; use only to fix layout.
- `Container(alias, "Label", "Technology", "Description")` — deployed runnable unit.
- `ContainerDb(alias, "Label", "Technology", "Description")` — deployed data store.
- `ContainerQueue(alias, "Label", "Technology", "Description")` — deployed queue or broker endpoint.
- `Container_Ext(alias, "Label", "Technology", "Description")` — externally owned deployed unit when needed.
- `Rel(from, to, "Label", "Technology")` — runtime call or data flow.
- `Rel_L`, `Rel_R`, `Rel_U`, `Rel_D` — directional layout variants; use only to fix collisions.
- `UpdateElementStyle(...)` — per-element styling.
- `UpdateRelStyle(...)` — per-relationship styling.

## Deployment modeling rules

- Start the diagram with `C4Deployment`.
- Use `Deployment_Node` or `Node` for every deployment location: environment, region, data center, cluster, VM, host, device, runtime, or nested infrastructure node.
- Nest deployment nodes when the topology is hierarchical, for example data center → VM → runtime.
- Place deployed `Container`, `ContainerDb`, `ContainerQueue`, or `Container_Ext` elements inside the deployment node that actually hosts them.
- Use the node `Type` for infrastructure/runtime technology when useful; use `Description` for deployment role or placement details when needed.
- Do not use `Container_Boundary`, `System_Boundary`, or generic `Boundary` to represent deployment topology.
- Do not model source files, classes, scripts, or provisioning files as separate containers unless independently deployed/runnable.
- Do not create relationships solely because elements share the same deployment node.
- Statement order affects layout; declare a deployment node immediately before the elements or nested nodes it hosts.
- Keep labels explicit enough to show placement, runtime, and responsibility.

## Relationships

- Relationship direction must match the actual runtime interaction or data flow.
- Include protocol/technology only when architecturally relevant.
- Prefer meaningful action labels over vague labels such as `Uses`.
- Use directional relationship variants only for layout correction.

## Labels and descriptions

- Use human-readable deployment labels.
- Node type should identify hosting/runtime technology when useful.
- Node description should explain deployment role or placement, not implementation trivia.
- Container technology should identify the deployed runtime or platform when useful.
- Container description should explain responsibility.
- Quote every label, description, type, and technology argument.

## Current-mode styling

Use the repo dark palette.

For internal deployed elements:

```text
$fontColor="#c9d1d9"
$bgColor="#2a2a2a"
$borderColor="#8b949e"
```

For `Container_Ext`, use `$bgColor="#1a1a1a"`.

Apply one `UpdateElementStyle` per deployed element and one `UpdateRelStyle` per relationship:

```text
$textColor="#c9d1d9"
$lineColor="#8b949e"
```

## Delta-mode styling

Apply only when `SKILL.md` selects **delta mode**.

- added: `#4a7a5a`
- removed: `#8a4a4a`
- modified or unchanged connection context: `#8b949e`

Use `UpdateElementStyle(alias, $borderColor="...")` and matching `UpdateRelStyle(..., $lineColor="...")` for changed relationships.

Show changed deployment nodes/elements plus the minimum unchanged context needed to connect them.

For in-place changes not visible through topology, add:

```md
**Behaviour changes**
- + added behavior
- - removed behavior
- ~ modified behavior
```

Use this for runtime replacements, instance resizing, scaling-policy changes, or other in-place deployment changes. Omit when none exist.

## Mermaid C4 constraints and gotchas

- `C4Deployment` uses `Deployment_Node` / `Node` for deployment topology.
- C4 has no `classDef` / `:::` styling.
- Use `UpdateElementStyle` and `UpdateRelStyle` for palette control.
- Quote all labels, descriptions, types, and technologies.
- Every alias must be unique and contain no spaces.
- Declare each element once.
- `Deployment_Node` / `Node` can be nested for deeper deployment/runtime structure.
- Mermaid C4 layout is statement-order-sensitive.
- Do not rely on diagram-wide `themeVariables` for C4 palette matching.

## Output template

Replace all placeholders with real deployment topology. Add or remove deployment nodes, containers, stores, and relationships to match the actual scope. Do not retain unused example elements.

<details>
<summary>{{title}}</summary>

```mermaid
---
config:
  c4:
    c4ShapePadding: 20
---
%% diagram-id: {{diagramId}}
C4Deployment
    title Deployment diagram for {{title}}

    Deployment_Node({{environmentAlias}}, "{{environmentLabel}}", "{{environmentType}}", "{{environmentDescription}}") {
        Deployment_Node({{hostAlias}}, "{{hostLabel}}", "{{hostType}}", "{{hostDescription}}") {
            Node({{runtimeAlias}}, "{{runtimeLabel}}", "{{runtimeType}}", "{{runtimeDescription}}") {
                Container({{componentAlias}}, "{{buildingBlockName}}", "{{technology}}", "{{responsibility}}")
            }
        }
        Deployment_Node({{dataNodeAlias}}, "{{dataNodeLabel}}", "{{dataNodeType}}", "{{dataNodeDescription}}") {
            ContainerDb({{storeAlias}}, "{{storeName}}", "{{storeTechnology}}", "{{whatItStores}}")
        }
    }

    Rel({{componentAlias}}, {{storeAlias}}, "{{whatItDoes}}", "{{protocol}}")

    UpdateElementStyle({{componentAlias}}, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle({{storeAlias}}, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateRelStyle({{componentAlias}}, {{storeAlias}}, $textColor="#c9d1d9", $lineColor="#8b949e")
```

</details>
