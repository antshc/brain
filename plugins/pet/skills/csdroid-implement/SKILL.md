---
name: csdroid-implement
description: C# implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any C# task.
---

Implement the requested C# task using the rules below.

## Load reference docs (mandatory)

Use the `HARNESS_ROOT` value provided to you by the agent (substitute its literal absolute value for `$HARNESS_ROOT`; it defaults to the current working directory when no argument was given). Then recursively scan **under** `$HARNESS_ROOT` (any subfolder) for `CODE.md` — never search outside `$HARNESS_ROOT`. If it exists, read it. You **must not** skip it if present.

**Emit**: "Loaded docs: [list]. Missing (fallback): [list]."

## Rules

- **Fallback:** when `CODE.md` is absent, match the conventions of the code you touched during EXPLORATION. Never invent conventions.
- **Placement** — match the conventions of the code touched during EXPLORATION (existing folder/layer/module structure). Never invent a new placement scheme.
- **Design** — prefer deep modules; add no speculative features.
- **Style** — write code to `CODE.md` conventions.
- **Tests** — write tests to `CODE.md` conventions whenever you add a public method, change existing behavior, or add/alter conditional logic.
