---
name: to-chorey
description: "Run a standalone Chorey maintainability review of current uncommitted work for behavior-preserving cleanup. Use when the user asks for a cleanup pass outside Ralph's autonomous loop."
---

Run `chorey` via `runSubagent` from cwd with no handoff sections. Chorey discovers and reviews the current uncommitted change set, requires `/crew-chore`, and uses `/crew-memory` when available.

Invoke Chorey even with no uncommitted work; it reports `STATUS: complete` with no files changed. Never supply `## BASELINE_COMMIT`: immediately before capture, Chorey runs `git add -A` once to stage the complete incoming change set as its defensive revert baseline. Chorey does not stage its cleanup, so verified improvements remain working-tree changes on top of that baseline.
