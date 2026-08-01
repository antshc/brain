---
name: ralph-build
description: Use when the initialized Build & LSP Check gate needs repository-specific BUILD.md guidance.
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