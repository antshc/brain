## Class Diagram

<!-- Include only when class responsibilities or relationships are design decisions. Show decision-relevant classes and relationships, not a source-code inventory. Delete this instruction. -->

```mermaid
classDiagram
    direction LR
    class {{boundaryClass}}
    class {{capabilityOwnerClass}}
    class {{dependencyClass}}
    {{boundaryClass}} --> {{capabilityOwnerClass}} : delegates
    {{capabilityOwnerClass}} --> {{dependencyClass}} : {{relationship}}
```
