---
name: principles
description: >-
  Load only the engineering principles a task needs, verbatim, from an indexed list. Use when a step cites a principle by name, e.g. 'laziness protocol', 'attack the premise'. Not for running checks → `experiment`; debugging → `diagnosing-bugs`.
---

# Principles

Indexed engineering principles. Bodies are verbatim from [cursor/plugins pstack](https://github.com/cursor/plugins/tree/main/pstack/skills) `principle-*` skills; cross-links became bold names.

## Load

1. Set `@needed` to every principle the caller names, plus each row whose **Load when** matches the current task. Done when `@needed` is listed by name.
2. Read each `@needed` file fully from this skill's base directory. **MUST NOT** load unmatched rows. Done when every `@needed` file is read to end of file.
3. Apply each loaded principle at its trigger point. A bold name inside a body that is not loaded is context, not a load trigger.

## Index

| Principle | Load when | File |
|---|---|---|
| Attack the premise | two or more fixes sharing one premise failed the same gate | [principles/attack-the-premise.md](principles/attack-the-premise.md) |
| Boundary discipline | wiring validation, error handling, or framework adapters | [principles/boundary-discipline.md](principles/boundary-discipline.md) |
| Deep modules | shaping or changing a contract, interface, seam, or adapter | [principles/deep-modules.md](principles/deep-modules.md) |
| Encode lessons in structure | writing the same instruction twice, or a recurring correction | [principles/encode-lessons-in-structure.md](principles/encode-lessons-in-structure.md) |
| Exhaust the design space | novel UI interaction or architectural decision with no precedent | [principles/exhaust-the-design-space.md](principles/exhaust-the-design-space.md) |
| Explain the number | before measuring, or trusting, reporting, or acting on a measured number | [principles/explain-the-number.md](principles/explain-the-number.md) |
| Fix root causes | debugging | [principles/fix-root-causes.md](principles/fix-root-causes.md) |
| Foundational thinking | before writing logic; choosing core types, scaffold vs feature order, shared state | [principles/foundational-thinking.md](principles/foundational-thinking.md) |
| In your own words | stating intent before review or design | [principles/in-your-own-words.md](principles/in-your-own-words.md) |
| Laziness protocol | refactoring, judging diff size, or tempted to add abstractions or layers | [principles/laziness-protocol.md](principles/laziness-protocol.md) |
| Make operations idempotent | commands, lifecycle steps, or loops amid crashes, restarts, retries | [principles/make-operations-idempotent.md](principles/make-operations-idempotent.md) |
| Minimize reader load | reviewing or shaping code that is hard to trace | [principles/minimize-reader-load.md](principles/minimize-reader-load.md) |
| Outcome-oriented execution | planned rewrites and migrations with explicit phase boundaries | [principles/outcome-oriented-execution.md](principles/outcome-oriented-execution.md) |
| Prove it works | after completing a task, before declaring done | [principles/prove-it-works.md](principles/prove-it-works.md) |
| Redesign from first principles | integrating a new requirement into an existing design | [principles/redesign-from-first-principles.md](principles/redesign-from-first-principles.md) |
| Separate before serializing shared state | concurrent actors might write the same file, branch, key, or state | [principles/separate-before-serializing-shared-state.md](principles/separate-before-serializing-shared-state.md) |
| Sequence verifiable units | multi-step work (sweeps, migrations, similar edits); stacking commits and PRs | [principles/sequence-verifiable-units.md](principles/sequence-verifiable-units.md) |
| Subtract before you add | sequencing an addition, refactor, or rewrite | [principles/subtract-before-you-add.md](principles/subtract-before-you-add.md) |
| Test behavior, not implementation | writing, changing, or keeping a test | [principles/test-behavior-not-implementation.md](principles/test-behavior-not-implementation.md) |
