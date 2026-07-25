---
name: droid-implement
description: Implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any task.
---

Implement the task. Do not skip any step below.

## Step 1: Load CODE.md (mandatory)

Read `CODE_PATH` (resolved by the agent during INPUT) in full when set. Never skip this check, even for trivial tasks.

**Emit**: "Loaded: CODE.md" or "CODE.md not found — EXPLORATION is the fallback."

## Step 2: Explore (mandatory, always — not just when CODE.md is missing)

Delegate to the `Explore` subagent (thoroughness: medium). Never explore ad hoc. Give it the task, the file(s) being modified, and the full `CODE.md` contents when loaded. Require it to:
- Read every file being modified plus one neighboring file per folder to confirm conventions
- Report project structure, code conventions, relevant existing code, and test patterns
- Cross-check each `CODE.md` convention against the code read; flag every convention it could **not** confirm

**Emit**: "Explored files: [list]. Conventions found: [list]. CODE.md conventions not observed: [list or none]. Layer placement: [layer]."

## Step 3: Implement

Write the code change now. `CODE.md` wins when it speaks. When it is missing or silent on a topic, EXPLORATION's observed conventions are the fallback — never invent conventions, never guess.

- **Placement** — reuse the existing folder/layer/module structure only. Inventing a new placement scheme is forbidden.
- **Design** — deep modules only. No speculative features.
- **Style** — follow `CODE.md`.
- **Tests** — required per `CODE.md` whenever you add a public method, change existing behavior, or add/alter conditional logic. Do not skip tests to save time.
