## Class Diagrams

### {{capabilityTitle}}

<!-- Include only when class responsibilities or relationships are design decisions. Show decision-relevant classes and relationships, not a source-code inventory. Do not diagram subsystem/system-service boundaries or project-assembly containers — describe those in Solution Overview prose instead. Relationship semantics: `--|>` inheritance (requires `: Extends` label), `o--` aggregation (contained instances outlive the container — scoped/singleton DI dependencies), `*--` composition (contained instances die with the container — transient DI dependencies or `new`-created instances), `..>` dependency (requires `: Use` label), `..|>` interface implementation. Delete this instruction. -->

<!-- This diagram shows the DELTA of this capability, not the full class model: only new, modified, and deleted classes, fields, and methods belong here — omit unchanged members of a changed class. Mark classes added (`:::added`), removed (`:::removed`), or changed (`:::memberChanged` + `[add]`/`[rem]`-prefixed members). If an intermediate class is needed only to complete a connection between two delta classes and is itself unchanged, include it with no `:::` class and list only the public field(s)/method(s) that connection actually uses — not its full member list. -->

<!-- Mermaid technical gotchas (verified against `mmdc` 11.16.0):
- Interface box: use the `<<Interface>>` annotation inside the member block, not a naming convention.
- Attach `:::added`/`:::removed`/`:::memberChanged` inline on the class's own declaration, in the same statement as its member block. A separate later `class ClassName:::style` or `cssClass "ClassName" style` statement silently fails once the class already has a `{ }` body — no error emitted, no styling applied.
- Comments are `%%` on their own line only. There is no inline `//` or `#` comment syntax inside a class body — text after `//` is parsed as a return-type annotation, not stripped.
- `cssClass` requires quotes around the node id: `cssClass "ClassName" styleName` — unquoted ids raise a parse error.
- `classDef` and `cssClass`/`:::` statements must come after the classes they style are declared.
- Out of scope for zdesign class diagrams: subsystem/system-service boundary boxes and "C# Project assembly" container boxes — these describe deployment/packaging groupings, not class-level design decisions. If one is itself a design decision, describe it in `Solution Overview` prose or the solution-level `flowchart` instead.
Delete this instruction. -->

<details>
<summary>{{capabilityTitle}}</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
classDiagram
    class {{boundaryClass}}
    class {{capabilityOwnerClass}}
    class {{dependencyInterface}} {
        +method(type) type
    }
    class {{newClass}}:::added {
        +field : type
        +method(type) type
    }
    class {{deletedClass}}:::removed
    class {{changedClass}}:::memberChanged {
        +[add] newMethod(type) type
    }

    {{boundaryClass}} --> {{capabilityOwnerClass}}
    {{capabilityOwnerClass}} *-- {{newClass}}
    {{newClass}} ..|> {{dependencyInterface}}

    note for {{capabilityOwnerClass}} "{{oneLineResponsibilityNote}}"

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
    classDef added stroke:#4a7a5a,stroke-width:2px
    classDef removed stroke:#8a4a4a,stroke-width:2px
    classDef memberChanged stroke:#8b949e,stroke-width:2px,stroke-dasharray: 4 3
```
</details>

<!-- `added` = solid green border, entirely new class. `removed` = solid red border, entirely deleted class. `memberChanged` = dashed gray border, unchanged class with an `[add]`/`[rem]`-prefixed member. `{{dependencyInterface}}` above is an example intermediate/pass-through class: unstyled (not part of the delta), showing only the one member the connection uses. `note for ClassName "..."` is optional — add it only for a short explanation that doesn't belong in the class body. Delete unused example classes/classDefs/notes. -->
