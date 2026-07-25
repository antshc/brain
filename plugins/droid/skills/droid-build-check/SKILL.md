---
name: droid-build-check
description: Build the project and check LSP availability. Apply during the BUILD & LSP CHECK step, before implementation.
---

# Build & LSP Check

```
Build & LSP Check Progress:
- [ ] Step 1: Build the project
- [ ] Step 2: Check LSP availability
```

## Step 1: Build the project

Build the project in your workspace using the "Build the solution" instructions in `$HARNESS_ROOT/README.md` (located under `HARNESS_ROOT`). If it fails, report the failure and stop — do not explore a broken build.

## Step 2: Check LSP availability

Check whether an LSP (language server) is available for this workspace.
- **If available**, use it for exploration (symbol lookup, go-to-definition, references) instead of raw text search.
- **If not available**, skip LSP usage and fall back to grep/glob/file reads during exploration.

**Emit**: "Build: pass | fail. LSP: available (using for exploration) | unavailable (skipped)."
