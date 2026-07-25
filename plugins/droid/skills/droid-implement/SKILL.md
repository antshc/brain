---
name: droid-implement
description: Implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any task.
---

Implement the requested task using the rules below.

## Load reference docs (mandatory)

Use the optional `CODE_PATH` value resolved by the agent during INPUT. When it is provided, read that `CODE.md` in full. When it is unresolved, use the fallback below.

**Emit**: "Loaded: CODE.md" or "CODE.md not found — using EXPLORATION fallback."

## Exploration

Run exploration via the `Explore` subagent (thoroughness: medium) — do not explore ad hoc. Pass it the task, the file(s) being modified, and the full contents of `CODE.md` when loaded. Instruct it to:
- Read at least the file(s) being modified and one neighboring file in the same folder to confirm conventions
- Report project structure, code conventions, relevant existing code, and test patterns in use
- Cross-check every convention listed in `CODE.md` against the code it reads, and report which `CODE.md` conventions it could **not** confirm/observe in the explored code

**Emit**: "Explored files: [list]. Conventions found: [list]. CODE.md conventions not observed: [list or none]. Layer placement: [layer]."

## Rules

When `CODE.md` is unresolved or silent on a topic, match the conventions of the code touched during EXPLORATION instead — never invent conventions.

- **Placement** — existing folder/layer/module structure; never invent a new placement scheme.
- **Design** — prefer deep modules; add no speculative features.
- **Style** — `CODE.md` conventions.
- **Tests** — `CODE.md` conventions whenever you add a public method, change existing behavior, or add/alter conditional logic.
