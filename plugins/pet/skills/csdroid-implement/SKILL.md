---
name: csdroid-implement
description: C# implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any C# task.
---

Implement the requested C# task using the rules below.

## Load reference docs (mandatory)

Use the optional `CODE_PATH` value resolved by the agent during INPUT. When it is provided, read that `CODE.md` in full. When it is unresolved, use the fallback below.

**Emit**: "Loaded docs: [list]. Missing (fallback): [list]."

## Rules

- **Fallback:** when `CODE.md` is absent, match the conventions of the code you touched during EXPLORATION. Never invent conventions.
- **Placement** — match the conventions of the code touched during EXPLORATION (existing folder/layer/module structure). Never invent a new placement scheme.
- **Design** — prefer deep modules; add no speculative features.
- **Style** — write code to `CODE.md` conventions.
- **Tests** — write tests to `CODE.md` conventions whenever you add a public method, change existing behavior, or add/alter conditional logic.
