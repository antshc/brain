---
name: crew-implement
description: Implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any task.
---

# Implementation

Copy this checklist and check off each item as you complete it:

```
- [ ] 1 Load CODE.md, then explore
- [ ] 2 Implement
```

## 1. Load CODE.md, then explore (mandatory, always)

Read `CODE_PATH` (resolved by the agent during INPUT) in full when set. **Emit**: "Loaded: CODE.md" or "CODE.md not found."

Delegate to the `Explore` subagent (thoroughness: medium) whether or not `CODE.md` loaded — never explore ad hoc. Give it the task, the files being modified, and the full `CODE.md` contents when loaded. Require it to:

- Read every file being modified plus one neighboring file per folder to confirm conventions
- Report project structure, code conventions, relevant existing code, and test patterns
- Cross-check each `CODE.md` convention against the code read; flag every one it could **not** confirm

**Emit**: "Explored files: [list]. Conventions found: [list]. CODE.md conventions not observed: [list or none]. Layer placement: [layer]."

## 2. Implement

`CODE.md` wins when it speaks. When it is missing or silent, use the exploration's observed conventions — never invent, never guess.

- **Placement** — reuse the existing folder/layer/module structure only; inventing a new scheme is forbidden.
- **Design** — deep modules only, no speculative features.
- **Style** — follow `CODE.md`.
- **Tests** — required per `CODE.md` for every new public method, behavior change, or added/altered conditional. Never skip them to save time.
