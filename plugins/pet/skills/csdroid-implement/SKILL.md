---
name: csdroid-implement
description: C# implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any C# task.
---

Implement the requested C# task using the rules below.

- Write code using the `CODE-STYLE.md` conventions. 
- Place classes per `Source Code Structure` and `Layers Dependency` in `ARCHITECTURE.md`.
- Apply `Solution Design Strategy` and `Architecture Decision Records` from `ARCHITECTURE.md`.
- Prefer deep modules, avoid speculative features. Follow [deep-modules.md](./deep-modules.md).
- Write tests when: adding a new public method, changing existing behavior, or touching conditional logic. Follow rules in the `TESTS-STYLE.md` file.
