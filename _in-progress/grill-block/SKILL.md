# Grill Building Blocks

arc42 Building Block View (§5) can drive design through iterative decomposition. A grilling skill examines each block until responsibility, boundaries, interfaces, dependencies, ownership, and quality concerns are clear.

## Process

```
Requirements
    ↓
Solution Strategy (arc42 §4)
    ↓
Level 1 Building Blocks
    ↓
Grill each block
    ↓
Split / merge / redefine
    ↓
Level 2
    ↓
Repeat until responsibilities are clear
```

## For each block, grill:

- Responsibility
- Boundary and exclusions
- Public interfaces
- Dependencies and cycles
- Data ownership
- Quality attributes
- Runtime and failure behavior
- Volatility
- Team and code ownership

## Then decide:

**KEEP** | **SPLIT** | **MERGE** | **REMOVE**

## Success Criteria

Stop when each block has:
- A clear responsibility
- Stable boundary
- Explicit interface
- Minimal dependencies
- A natural mapping to a module, project, or package
