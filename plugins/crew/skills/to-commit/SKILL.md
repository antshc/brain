---
name: to-commit
description: Commit staged/unstaged changes using Codey's status report or the diff itself. Use after a Codey task completes or when the user says "commit".
---

Commit all uncommitted changes using the format below.

**Gate:** a status report of `partial` or `blocked` means the work is unverified. Surface the status and its NOTES, and commit only after the user confirms. (`ralph:dev` makes its own checkpoint commit on an isolated worktree branch instead — it never routes through this skill.)

`<skill-directory>` is the directory containing this SKILL.md file: take the absolute path you used to read this file and strip the trailing `/SKILL.md`. Never derive it any other way, and never search the filesystem for it.

**Source:** Use the agent's status report if available. Otherwise run `python <skill-directory>/scripts/staged_diff.py` and derive the message from the diff.

**Format:**
```
- **SUBJECT** → Use **ccode:** prefix, than one line commit summary
- **SUMMARY** → commit body (key technical decisions)
- **FILES** → list of files changed
- **NOTES** → blockers or context for the next iteration
```