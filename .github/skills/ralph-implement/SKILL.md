---
description: Implementation rules. Loads skill-owned CODE.md or a technology-agnostic fallback, then applies repository conventions.
metadata:
    github-path: plugins/ralph/skills/ralph-implement
    github-ref: refs/tags/v0.1.0-479
    github-repo: https://github.com/antshc/brain
    github-tree-sha: 3ce9be92538b172b2bc8f9efeef6b3da709795d7
name: ralph-implement
---
# Implementation

Copy this checklist and check off items as you complete them:

```
Implementation Progress:
- [ ] Step 1: Load coding guidance and explore
- [ ] Step 2: Implement the task
```

## Initialize guidance

When `/ralph-init` requests setup, preserve substantive sibling `CODE.md`; otherwise create it from `templates/CODE.template.md` and add only repository-evidenced conventions.

## Step 1: Load coding guidance and explore

Read sibling `CODE.md` in full.
Explore every file being modified and one neighboring file per folder. 
Report project structure, observed conventions, relevant implementation and test patterns, and guidance conventions not observed in the files read.

**Emit**: "Combined conventions from CODE.md and from the exploration, use them for task implementation."

## Step 2: Implement the task

`CODE.md` wins when it speaks. Otherwise follow observed conventions.

- Reuse the existing folder, layer, and module structure.
- Make the smallest coherent change; do not add speculative behavior.
- Add or update focused checks when behavior changes.
