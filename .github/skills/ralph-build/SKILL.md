---
description: Use when the initialized Build & LSP Check gate needs repository-specific BUILD.md guidance.
metadata:
    github-path: plugins/ralph/skills/ralph-build
    github-ref: refs/tags/v0.1.0-479
    github-repo: https://github.com/antshc/brain
    github-tree-sha: e6d15898de964cadfb9882fd61221218ae68a5bf
name: ralph-build
---
# Build & LSP Check

Copy this checklist and check off items as you complete them:

```
Build & LSP Check Progress:
- [ ] Step 1: Build the project
- [ ] Step 2: Check LSP availability
```

## Initialize guidance

When `/ralph-init` requests setup after Build is enabled, preserve substantive sibling `BUILD.md`; otherwise create it from `templates/BUILD.template.md` and add only repository-evidenced early build steps.

## Step 1: Run build guidance

Read sibling `BUILD.md` in full and follow its build steps in order. If it fails, report the failure and stop; do not explore a broken build.

## Step 2: Check LSP availability

Check whether an LSP is available for this workspace. Use it for exploration when available; otherwise use repository search and file reads.

**Emit**: "Build: pass | fail. LSP: available (using for exploration) | unavailable (skipped)."
