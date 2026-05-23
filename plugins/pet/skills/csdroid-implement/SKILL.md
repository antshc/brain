---
name: csdroid-implement
description: Implement C# changes using project conventions, tests, and module design rules. Use when working on C# code in pet projects.
---

# Implementation

Implement the requested C# change. 
Write code using [style.md](references/style.md)

## Rules

- Follow [layers.md](references/layers.md) for module structure and dependencies.
- Use tests when behavior changes or risk is non-trivial. Follow Testing and mocking [tests.md](references/tests.md)
- Tests verify behavior through public interfaces, not internals.
- Prefer small public surfaces with deep implementation. Follow [design.md](references/design.md).
- Avoid speculative features.
- Refactor only when behavior is covered and feedback is green.
