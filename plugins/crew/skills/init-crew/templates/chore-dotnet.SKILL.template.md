---
name: chore-dotnet
description: Repository-specific .NET cleanup rules for Chorey. Used only by Chorey during behavior-preserving review.
---

# Chore .NET rules

## Hazard rules

- Never hand-edit a generated file (`*.Designer.cs`, `*.g.cs`, or anything under `obj/`/`bin/`) as part of a cleanup — regenerate it through its source instead.

## Review rules

- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

## Repository rules

<!-- Add observed repository-specific cleanup rules and protected content here. -->
