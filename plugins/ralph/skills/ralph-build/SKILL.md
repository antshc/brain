---
name: ralph-build
description: >-
  Build the project in a given workspace from the harness README build instructions and report pass or fail. Use after worktree setup, before implementation, or when another skill needs a build gate.
argument-hint: '<harness-repo-path> <workspace-path>'
---

# Build

**Arguments:** `<harness-repo-path> <workspace-path>`

Both paths are supplied by the caller — this skill performs no resolution of its own.

**Build** the project in `<workspace-path>` using the "Build the solution" instructions in `<harness-repo-path>/README.md`. On failure, report and stop — never explore a broken build.

**Emit**: "Build: pass | fail."
