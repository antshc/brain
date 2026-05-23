---
name: to-droid
description: Run the csdroid subagent for a C# implementation task. Use when the task comes from plan.md/session memory or user-provided implementation text.
---

Invoke `runSubagent`:`csdroid`  with the following prompt (substitute actual values):

```
## TASK
- Use `plan.md` from session memory if present.
- If the user provided implementation details, use those instead — they take priority over `plan.md`.

## RECENT CHANGES
`Get diff of all changed uncommitted files, or "No uncommitted changes" if none.`
`git log --format="%H%n%ad%n%B---" --date=short --grep="dcode" -n 5 2>/dev/null || echo "No commits found."`
```