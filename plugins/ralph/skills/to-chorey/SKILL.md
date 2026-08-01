---
name: to-chorey
description: Run the Chorey agent to review the current uncommitted work. Use after implementation and before commit.
---

# Run Chorey

Run the `chorey` agent directly via `runSubagent` in the invocation directory. Do not pass a workspace path.

If the `chorey` agent is unavailable, report:

```
STATUS: blocked
SUMMARY: Chorey agent unavailable
FILES: none
GOTCHAS UPDATED: none
NOTES: Install or enable the Ralph Chorey agent.
```