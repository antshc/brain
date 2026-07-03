---
name: csdroid-implement
description: C# implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any C# task.
---

Implement the requested C# task using the rules below.

## Load reference docs (mandatory)

Load the environment first (see the `csdroid-setup` skill → **Load environment**) so `$CSDROID_HARNESS_ROOT` is set. Then locate docs `ARCHITECTURE.md`, `CODE.md`, and `TESTS.md` at `$CSDROID_HARNESS_ROOT`. For each that exists:

1. Read it. You **must not** skip a file that is present.
2. `ARCHITECTURE.md` indexes ADRs (`docs/adr/`) and SDRs (`docs/sdr/`) as a table of one-line summaries. Scan that table, pick the rows whose summary relates to the current task, and read **only those** ADR/SDR files in full.
3. Apply the rules, decisions, and strategies you found during implementation.

**Emit**: "Loaded docs: [list]. Missing (fallback): [list]."

## Rules

- Place classes per `Source Code Structure` and `Layers Dependency` from `ARCHITECTURE.md` if present; else infer placement from neighboring files and conventions found during EXPLORATION.
- Apply `Solution Design Strategy` and `Architecture Decision Records` from `ARCHITECTURE.md` if present; else follow the design choices established in existing code.
- Write code using the `CODE.md` conventions if present; else match the style of surrounding code. Prefer deep modules, avoid speculative features.
- Write tests when: adding a new public method, changing existing behavior, or touching conditional logic. Follow rules in `TESTS.md` if present; else match the existing test patterns found during EXPLORATION.
