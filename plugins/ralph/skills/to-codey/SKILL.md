---
name: to-codey
description: Run the Codey agent for one implementation task. Use when a developer supplies a task, plan, or GitHub issue URL.
argumentHint: "<description> | @plan | <github-issue-url>"
---

# Run Codey

Resolve `{{input}}` into exactly one task:

- `<description>`: use the inline description.
- `@plan`: load `plan.md` from session memory; if it is missing or empty, report `STATUS: blocked` with that reason.
- `<github-issue-url>`: fetch the issue title, body, and comments; if unavailable or invalid, report `STATUS: blocked` with that reason.
- Missing input: report `STATUS: blocked` because a task is required.

Collect current uncommitted changes and the five most recent `rcode:` commits, then run the `codey` agent directly via `runSubagent` in the invocation directory with:

```
## TASK
{{task}}

## RECENT CHANGES
{{recentChanges}}
```

Do not pass a workspace path. If the `codey` agent is unavailable, report:

```
STATUS: blocked
SUMMARY: Codey agent unavailable
FILES: none
GOTCHAS UPDATED: none
NOTES: Install or enable the Ralph Codey agent.
```