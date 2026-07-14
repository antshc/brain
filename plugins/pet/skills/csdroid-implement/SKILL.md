---
name: csdroid-implement
description: C# implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any C# task.
---

Implement the requested C# task using the rules below.

## Load reference docs (mandatory)

Use the `HARNESS_ROOT` value provided to you by the agent (substitute its literal absolute value for `$HARNESS_ROOT`; it defaults to the current working directory when no argument was given). Then locate docs `ARCHITECTURE.md`, `CODE.md` at `$HARNESS_ROOT`. For each that exists:

1. Read it. You **must not** skip a file that is present.
2. `ARCHITECTURE.md` indexes `Architecture Decision Records` (`docs/adr/`) and `Solution Strategy` (`docs/ssr/`) as a table of one-line summaries. Scan that table, pick the rows whose summary relates to the current task, and read **only those** ADR/SSR files in full.
3. Apply the rules, decisions, and strategies you found during implementation.

**Emit**: "Loaded docs: [list]. Missing (fallback): [list]."

## Rules

- **Fallback:** when a referenced doc is absent, match the conventions of the code you touched during EXPLORATION. Never invent conventions.
- **Placement** — put classes where `Building blocks` and `Layers Dependency` (in `ARCHITECTURE.md`) dictate.
- **Design** — follow `Solution Strategy` and the ADRs (in `ARCHITECTURE.md`). Prefer deep modules; add no speculative features.
- **Style** — write code to `CODE.md` conventions.
- **Tests** — write tests to `CODE.md` conventions whenever you add a public method, change existing behavior, or add/alter conditional logic.
