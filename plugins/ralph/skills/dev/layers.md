# Architectural Layers

## Dependency Direction

Each layer only depends on layers below it. Never reference upward.

```
Client
  ↓
Manager            ← coordinates use cases (most volatile)
  ↓
Engine             ← business rules & algorithms
  ↓
ResourceAccessor   ← technical integration
  ↓
Repository (optional) ← data access pattern
  ↓
Resource           ← DB, FS, REST, Queue (least volatile)

Utilities are callable by all layers.
```

## Dependency Rules

- Manager → Engine, ResourceAccessor, Repository
- Engine → nothing (pure logic) or other Engines
- ResourceAccessor → Resource (external SDK/client)
- Repository → ResourceAccessor or Resource directly
- **Never**: Engine → Manager, ResourceAccessor → Manager, Engine → ResourceAccessor
