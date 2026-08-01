---
name: ralph-build
description: Build the current repository and check LSP availability before implementation.
---

# Build & LSP Check

Copy this checklist and check off items as you complete them:

```
Build & LSP Check Progress:
- [ ] Step 1: Build the project
- [ ] Step 2: Check LSP availability
```

## Step 1: Build the project

Build the project in the invocation directory using its `README.md` Build the solution instructions. If it fails, report the failure and stop; do not explore a broken build.

## Step 2: Check LSP availability

Check whether an LSP is available for this workspace. Use it for exploration when available; otherwise use repository search and file reads.

**Emit**: "Build: pass | fail. LSP: available (using for exploration) | unavailable (skipped)."