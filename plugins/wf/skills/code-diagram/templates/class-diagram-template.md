# Class Diagram Template

Official Mermaid class diagram syntax: https://mermaid.ai/open-source/syntax/classDiagram.html

## Drawing rules

- Use Mermaid `classDiagram` for implementation-level class responsibilities and relationships.
- Show decision-relevant classes, members, and relationships, not a source-code inventory.
- Ground current-state classes, members, and relationships in repository/code evidence. Do not invent implementation details.
- Do not use a class diagram for deployable units, infrastructure topology, subsystem boundaries, or process flow.
- Do not model project/assembly or system-service boundary boxes as classes.
- Prefer readable implementation structure over exhaustive class coverage.

## Classes, members, and grouping

- Use `<<Interface>>` inside the class member block to mark an interface.
- Use `namespace Name { ... }` to group classes by implementation layer/module when that grouping is relevant.
- Include only fields and methods needed to communicate the design decision.
- Use `note for ClassName "..."` only for a short responsibility or constraint that does not belong in the class body.
- Prefer stable code identifiers from the repository over invented architectural names at class level.

## Relationship semantics

- `--|>` — inheritance; label it `: Extends`.
- `..|>` — interface implementation.
- `o--` — aggregation; use when the contained instance can outlive the container, such as scoped/singleton DI dependencies.
- `*--` — composition; use when the contained instance lifetime belongs to the container, such as transient or `new`-created instances.
- `..>` — dependency; label it `: Use`.
- `-->` — directed association/reference when a more specific lifetime relationship is not intended.
- Relationship direction and kind must match the actual implementation.

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

Mark:

- Added classes: `:::added`.
- Removed classes: `:::removed`.
- Changed classes: `:::memberChanged` and prefix changed members with `[add]` or `[rem]`.

Define:

```mermaid
classDef added stroke:#4a7a5a,stroke-width:1px
classDef removed stroke:#8a4a4a,stroke-width:1px
classDef memberChanged stroke:#8b949e,stroke-width:1px,stroke-dasharray:5 5
```

- Show only new, modified, and deleted classes, fields, methods, and relationships.
- Omit unchanged members of a changed class.
- Intermediate classes needed only to complete a connection stay base-styled and list only members used by that connection.
- Show changed implementation plus the minimum unchanged context needed to connect it.
- Do not apply delta styling in current mode.

## Mermaid constraints and gotchas

- Mermaid comments are `%%` on their own line.
- Do not use inline `//` or `#` comments inside a class body; they are parsed as diagram content rather than stripped comments.
- Use the `<<Interface>>` annotation rather than encoding interface-ness only in the class name.
- `namespace` groups implementation layers/modules; it is not a subsystem or deployment boundary.
- Delete unused placeholders, classes, members, relationships, namespaces, and notes from the final diagram.

## Output template

Replace all placeholders with real code structure. Add or remove classes, members, namespaces, relationships, and notes to match the actual scope.

<details>
<summary>{{title}}</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
classDiagram
    namespace {{apiLayer}} {
        class {{boundaryClass}}
    }
    namespace {{domainLayer}} {
        class {{capabilityOwnerClass}}
        class {{dependencyInterface}} {
            <<Interface>>
            +method(type) type
        }
        class {{relatedClass}} {
            +field : type
            +method(type) type
        }
    }

    {{boundaryClass}} --> {{capabilityOwnerClass}}
    {{capabilityOwnerClass}} *-- {{relatedClass}}
    {{relatedClass}} ..|> {{dependencyInterface}}

    note for {{capabilityOwnerClass}} "{{oneLineResponsibilityNote}}"

    classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

</details>
