---
name: csdroid-implement
description: Implement C# changes using project conventions, tests, and module design rules. Use when working on C# code in pet projects.
---

# Implementation

Implement the requested C# change.

## Rules

- Follow [style.md](references/style.md).
- Use tests when behavior changes or risk is non-trivial.
- Tests verify behavior through public interfaces, not internals.
- Prefer small public surfaces with deep implementation.
- Avoid speculative features.
- Refactor only when behavior is covered and feedback is green.

## References

- Testing and mocking rules: [tests.md](references/tests.md)
- Module/interface design: [design.md](references/design.md)
