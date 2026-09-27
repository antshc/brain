---
name: to-commit
description: "Commit current staged or unstaged work after a Codey task completes, or when the user asks to commit it. Derive the message from Codey's report or the diff; require confirmation for partial or blocked work."
---

Commit all uncommitted changes using the format below.

**Gate:** a status report of `partial` or `blocked` means the work is unverified. Surface the status and its NOTES, and commit only after the user confirms. (`ralph:dev` makes its own checkpoint commit on an isolated worktree branch instead — it never routes through this skill.)

**Source:** Use the agent's status report if available. Otherwise run `git add -A 2>/dev/null; DIFF=$(git diff --cached 2>/dev/null); [ -n "$DIFF" ] && echo "$DIFF" || echo "No uncommitted changes"` and derive the message from the diff.

**Format:**
```
- **SUBJECT** → Use **ccode:** prefix, than one line commit summary
- **SUMMARY** → commit body (key technical decisions)
- **FILES** → list of files changed
- **NOTES** → blockers or context for the next iteration
```