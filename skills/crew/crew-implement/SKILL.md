---
name: crew-implement
description: Implementation rules — style, layers, design, and tests. Apply during the IMPLEMENTATION step of any task.
---

# Implementation

Copy this checklist and check off each item as you complete it:

```
- [ ] 1 Load CODE_PATHS, then explore
- [ ] 2 Implement
```

## 1. Load CODE_PATHS, then explore (mandatory, always)

Read every path in `CODE_PATHS` (resolved by the agent during INPUT, one per matched Stack) in full. **Emit**: "Loaded: [list of CODE-<stack>.md paths]" or "No CODE.md resolved — no Stack matched, or every matched Stack's file is absent."

Delegate to the `Explore` subagent (thoroughness: medium) whether or not any `CODE_PATHS` loaded — never explore ad hoc. Give it the task, the files being modified, and the full contents of every loaded `CODE_PATHS` file. Require it to:

- Read every file being modified plus one neighboring file per folder to confirm conventions
- Report project structure, code conventions, relevant existing code, and test patterns
- Cross-check each loaded convention against the code read; flag every one it could **not** confirm

**Emit**: "Explored files: [list]. Conventions found: [list]. Loaded conventions not observed: [list or none]. Layer placement: [layer]."

## 2. Implement

Loaded `CODE_PATHS` content wins when it speaks. When none loaded or a convention is silent, use the exploration's observed conventions — never invent, never guess.

- **Placement** — reuse the existing folder/layer/module structure only; inventing a new scheme is forbidden.
- **Design** — deep modules only, no speculative features.
- **Style** — follow the loaded `CODE_PATHS` files.
- **Tests** — required per the loaded `CODE_PATHS` files for every new public method, behavior change, or added/altered conditional. Never skip them to save time.
