---
name: csdroid-implement
description: C# implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any C# task.
---

Implement the requested C# task using the rules below.

## Load reference docs (mandatory)

Use the `HARNESS_ROOT` value provided to you by the agent (substitute its literal absolute value for `$HARNESS_ROOT`; it defaults to the current working directory when no argument was given). Then recursively scan **under** `$HARNESS_ROOT` (any subfolder) for `ARCHITECTURE.md` and `CODE.md` — never search outside `$HARNESS_ROOT`. For each that exists:

1. Read it. You **must not** skip a file that is present.
2.Always scan the `ARCHITECTURE.md` indexes `Architecture Decision Records` (`docs/adr/`) and `Crosscutting Concepts` (`docs/concepts/`) as tables with a `Trigger condition` column — both resolved relative to the folder `ARCHITECTURE.md` was found in. Scan each table and match `Trigger condition` against the current implementation work; read **only those** matching ADR/Concept files in full.
3. Always scan the `Services` bullet list (under `Building blocks` in `ARCHITECTURE.md`) and load the matching service's doc (`docs/services/{{slug}}.md`) for its layer headings and Cross-Module Dependency Rules.
4. Apply the rules, decisions, and concepts you found during implementation.

**Emit**: "Loaded docs: [list]. Missing (fallback): [list]."

## Rules

- **Fallback:** when a referenced doc is absent, match the conventions of the code you touched during EXPLORATION. Never invent conventions.
- **Placement** — put classes where the loaded service doc (step 3: `docs/services/{{slug}}.md`) and the matching Concepts (step 2) dictate — layer headings and Cross-Module Dependency Rules from the service doc, layering/module/class decomposition rules from Concepts. If no service doc matched, fall back to `Building blocks` in `ARCHITECTURE.md` plus the matching Concepts alone.
- **Design** — follow the `Crosscutting Concepts` and the `Architecture Decision Records` (in `ARCHITECTURE.md`). Prefer deep modules; add no speculative features.
- **Style** — write code to `CODE.md` conventions.
- **Tests** — write tests to `CODE.md` conventions whenever you add a public method, change existing behavior, or add/alter conditional logic.
