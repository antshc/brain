---
name: ralph-chore
description: Review verified uncommitted changes for behavior-preserving maintainability refactors.
---

# Maintainability Review

Copy this checklist and check off items as you complete them:

```
Maintainability Review Progress:
- [ ] Step 1: Inspect the reviewed change set
- [ ] Step 2: Identify justified refactors
- [ ] Step 3: Apply or report findings
```

## Initialize guidance

When `/ralph-init` requests setup, preserve substantive sibling `CHORE.md`; otherwise create it from `templates/CHORE.template.md` and add only repository-evidenced review rules.

## Step 1: Inspect the reviewed change set

Read sibling `CHORE.md` in full. Inspect staged, unstaged, and untracked files in the current invocation directory. Read each changed file and only the directly required neighboring code needed to establish behavior.

## Step 2: Identify justified refactors

`CHORE.md` wins when it speaks. Otherwise consider duplication, unclear boundaries, avoidable complexity, stale comments, and inconsistent local conventions. Do not report speculative redesigns or concerns outside the reviewed change set.

## Step 3: Apply or report findings

Apply a refactor only when it preserves behavior and is limited to reviewed changes and directly required neighbors. Otherwise report the finding without changing files.

**Emit**: "Maintainability findings: [applied refactors or none]."