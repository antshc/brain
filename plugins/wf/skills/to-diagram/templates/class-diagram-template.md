## Class Diagram

### {{title}}

<!-- Include only when class responsibilities or relationships are design decisions. Show decision-relevant classes and relationships, not a source-code inventory. Do not diagram subsystem/system-service boundaries or project-assembly containers — describe those in Solution Overview prose instead. Relationship semantics: `--|>` inheritance (requires `: Extends` label), `o--` aggregation (contained instances outlive the container — scoped/singleton DI dependencies), `*--` composition (contained instances die with the container — transient DI dependencies or `new`-created instances), `..>` dependency (requires `: Use` label), `..|>` interface implementation. Delete this instruction. -->

<!-- Mermaid technical gotchas (verified against `mmdc` 11.16.0):
- Interface box: use the `<<Interface>>` annotation inside the member block, not a naming convention.
- Comments are `%%` on their own line only. There is no inline `//` or `#` comment syntax inside a class body — text after `//` is parsed as a return-type annotation, not stripped.
- `namespace Name { class ... }` groups classes by layer/module — use one per architectural layer this diagram touches (e.g. Api, Domain, Infrastructure).
- Out of scope for zdesign class diagrams: subsystem/system-service boundary boxes and "C# Project assembly" container boxes — these describe deployment/packaging groupings, not class-level design decisions. If one is itself a design decision, describe it in `Solution Overview` prose or the solution-level `flowchart` instead.
Delete this instruction. -->

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

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
</details>

<!-- `note for ClassName "..."` is optional — add it only for a short explanation that doesn't belong in the class body. Delete unused example classes/notes. -->
