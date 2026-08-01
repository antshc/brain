---
description: Run the Chorey agent to review the current uncommitted work. Use after implementation and before commit.
metadata:
    github-path: plugins/ralph/skills/to-chorey
    github-ref: refs/tags/v0.1.0-479
    github-repo: https://github.com/antshc/brain
    github-tree-sha: 65034b477a409588f834ffc9514dca700a6671af
name: to-chorey
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
