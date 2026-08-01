---
name: ralph-implement
description: Implementation rules. Loads skill-owned CODE.md or a technology-agnostic fallback, then applies repository conventions.
---

# Implementation

Copy this checklist and check off items as you complete them:

```
Implementation Progress:
- [ ] Step 1: Load coding guidance and explore
- [ ] Step 2: Implement the task
```

## Step 1: Load coding guidance and explore

Read sibling `CODE.md` in full. When it is absent, report the missing reference and read sibling `FALLBACK.md`.

Explore every file being modified and one neighboring file per folder. Report project structure, observed conventions, relevant implementation and test patterns, and guidance conventions not observed in the files read.

**Emit**: "Coding guidance: CODE.md" or "Coding guidance: CODE.md missing; using FALLBACK.md."

## Step 2: Implement the task

`CODE.md` wins when it speaks. Otherwise follow observed conventions.

- Reuse the existing folder, layer, and module structure.
- Make the smallest coherent change; do not add speculative behavior.
- Add or update focused checks when behavior changes.