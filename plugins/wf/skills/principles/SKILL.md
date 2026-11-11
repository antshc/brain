---
name: principles
description: >-
  Load only the engineering principles a task needs, verbatim, from an indexed list. Use when a step cites a principle by name, e.g. 'laziness protocol', 'attack the premise'. Not for running checks → `prove`; debugging → `diagnosing-bugs`.
---

# Principles

Indexed engineering principles. Bodies are verbatim from [cursor/plugins pstack](https://github.com/cursor/plugins/tree/main/pstack/skills) `principle-*` skills; cross-links became bold names and skill-call wording follows the repository invocation contract. The seven additions (Build the lever, Experience first, Guard the context window, Migrate callers, then delete legacy APIs, Model the domain, Never block on the human, Type system discipline) use [pinned source 5866df5](https://github.com/cursor/plugins/tree/5866df557357d005b3c0c9d3da0d9e739b4bdde3/pstack/skills); only frontmatter removal and principle-link/name normalization were applied.

## Load

1. **MUST** read this entire `SKILL.md` through EOF before selection. Continue truncated reads; descriptions, summaries and the Index alone do not count. Done when the full skill is loaded.
2. Set `@needed` to every principle the caller names, plus each row whose **Load when** matches the current task. Done when `@needed` is listed by name.
3. Resolve every selected Index path against this skill's actual installation folder, never caller CWD or an upstream checkout. **MUST** read each file through EOF before application; continue truncated reads. **MUST NOT** load unmatched rows. Done when every selected file has a completed full read.
4. Apply loaded principles at their trigger points. Re-evaluate selection when task or phase changes. A bold name inside a body is context, not a recursive load trigger. Done when applicable decisions follow the loaded principles.

Unknown name, unavailable skill or unreadable file → report the exact gap; block dependent decisions and continue independent work. **MUST NOT** substitute memory, summaries or partial reads. Fresh workers load for themselves. Reuse completed reads only while their full content remains available and unchanged; reload after context loss.

## Index

| Principle | Load when | File |
|---|---|---|
| Attack the premise | two or more fixes sharing one premise failed the same gate | [principles/attack-the-premise.md](principles/attack-the-premise.md) |
| Boundary discipline | wiring validation, error handling, or framework adapters | [principles/boundary-discipline.md](principles/boundary-discipline.md) |
| Build the lever | nontrivial edits, migrations, analyses or verification need a rerunnable artifact | [principles/build-the-lever.md](principles/build-the-lever.md) |
| Deep modules | shaping or changing a contract, interface, seam, or adapter | [principles/deep-modules.md](principles/deep-modules.md) |
| Encode lessons in structure | writing the same instruction twice, or a recurring correction | [principles/encode-lessons-in-structure.md](principles/encode-lessons-in-structure.md) |
| Exhaust the design space | novel UI interaction or architectural decision with no precedent | [principles/exhaust-the-design-space.md](principles/exhaust-the-design-space.md) |
| Experience first | product, UX, scope or consumer/maintainer experience tradeoffs | [principles/experience-first.md](principles/experience-first.md) |
| Explain the number | before measuring, or trusting, reporting, or acting on a measured number | [principles/explain-the-number.md](principles/explain-the-number.md) |
| Fix root causes | debugging | [principles/fix-root-causes.md](principles/fix-root-causes.md) |
| Foundational thinking | before writing logic; choosing core types, scaffold vs feature order, shared state | [principles/foundational-thinking.md](principles/foundational-thinking.md) |
| Guard the context window | large outputs, long files, repeated reads or fan-out planning | [principles/guard-the-context-window.md](principles/guard-the-context-window.md) |
| In your own words | stating intent before review or design | [principles/in-your-own-words.md](principles/in-your-own-words.md) |
| Laziness protocol | refactoring, judging diff size, or tempted to add abstractions or layers | [principles/laziness-protocol.md](principles/laziness-protocol.md) |
| Make operations idempotent | commands, lifecycle steps, or loops amid crashes, restarts, retries | [principles/make-operations-idempotent.md](principles/make-operations-idempotent.md) |
| Migrate callers, then delete legacy APIs | replacing an internal API; coordinated migration is possible and external compatibility is not required | [principles/migrate-callers-then-delete-legacy-apis.md](principles/migrate-callers-then-delete-legacy-apis.md) |
| Minimize reader load | reviewing or shaping code that is hard to trace | [principles/minimize-reader-load.md](principles/minimize-reader-load.md) |
| Model the domain | stateful or branch-heavy logic, or repeated shape assumptions across files | [principles/model-the-domain.md](principles/model-the-domain.md) |
| Never block on the human | routine reversible execution choices would otherwise prompt for permission | [principles/never-block-on-the-human.md](principles/never-block-on-the-human.md) |
| Outcome-oriented execution | planned rewrites and migrations with explicit phase boundaries | [principles/outcome-oriented-execution.md](principles/outcome-oriented-execution.md) |
| Prove it works | after completing a task, before declaring done | [principles/prove-it-works.md](principles/prove-it-works.md) |
| Redesign from first principles | integrating a new requirement into an existing design | [principles/redesign-from-first-principles.md](principles/redesign-from-first-principles.md) |
| Separate before serializing shared state | concurrent actors might write the same file, branch, key, or state | [principles/separate-before-serializing-shared-state.md](principles/separate-before-serializing-shared-state.md) |
| Sequence verifiable units | multi-step work (sweeps, migrations, similar edits); stacking commits and PRs | [principles/sequence-verifiable-units.md](principles/sequence-verifiable-units.md) |
| Subtract before you add | sequencing an addition, refactor, or rewrite | [principles/subtract-before-you-add.md](principles/subtract-before-you-add.md) |
| Test behavior, not implementation | writing, changing, or keeping a test | [principles/test-behavior-not-implementation.md](principles/test-behavior-not-implementation.md) |
| Type system discipline | designing or reviewing types, signatures, semantic primitives, variants or parsed external data | [principles/type-system-discipline.md](principles/type-system-discipline.md) |
