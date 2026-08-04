---
name: crew-build-check
description: Build the project and check LSP availability. Apply during the BUILD & LSP CHECK step, before implementation.
---

# Build & LSP Check

**1. Build** the project in your workspace using the "Build the solution" instructions in `$HARNESS_REPO_PATH/README.md`. On failure, report and stop — never explore a broken build.

**2. Check LSP availability** for this workspace. Available → use it for exploration (symbol lookup, go-to-definition, references) instead of raw text search. Unavailable → fall back to grep/glob/file reads.

**Emit**: "Build: pass | fail. LSP: available (using for exploration) | unavailable (skipped)."
