---
name: to-commit
description: Commit staged/unstaged changes using the droid agent's status report or the diff itself. Use after a droid task completes or when the user says "droid commit".
---

Commit all uncommitted changes using the format below.

**Source:** Use the agent's status report if available. Otherwise run `git add -A 2>/dev/null; DIFF=$(git diff --cached 2>/dev/null); [ -n "$DIFF" ] && echo "$DIFF" || echo "No uncommitted changes"` and derive the message from the diff.

**Format:**
```
- **SUBJECT** → Use **dcode:** prefix, than one line commit summary
- **SUMMARY** → commit body (key technical decisions)
- **FILES** → list of files changed
- **NOTES** → blockers or context for the next iteration
```
