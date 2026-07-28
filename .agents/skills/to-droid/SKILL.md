---
name: to-droid
description: Run the droid subagent for an implementation task. Use when the task comes from plan.md/session memory or user-provided implementation text.
argumentHint: "<description> | @plan | <github-issue-url>"
---

Use the Codex subagent workflow and delegate the task to the custom agent named
`droid`. The custom agent is registered in `.codex/agents/droid.toml` and loads
the authoritative role instructions from `.agents/agents/droid.agent.md`.

Execute the commands below and substitute their output into the delegated prompt
before starting the subagent:

```
## TASK
Resolve the task from the argument:
- `<description>` — use the inline description as the task.
- `@plan` — load `plan.md` from session memory and use it as the task. If `plan.md` is missing or empty, stop and tell the user.
- `<github-issue-url>` — fetch the GitHub issue and use its title + body + comments as the task. If the URL is unreachable or not a valid issue, stop and tell the user.
- If no argument is provided, stop and ask the user for a task description.

## RECENT CHANGES
`git add -A 2>/dev/null; DIFF=$(git diff --cached 2>/dev/null); [ -n "$DIFF" ] && echo "$DIFF" || echo "No uncommitted changes"`
`git log --format="%H%n%ad%n%B---" --date=short --grep="dcode:" -n 5 2>/dev/null || echo "No commits found."`
```

Start exactly one subagent with the assembled prompt, explicitly identifying the
agent role as `droid`. If the current client does not expose named-agent
selection, include the instruction `Follow .agents/agents/droid.agent.md`
directly in the prompt so the child can apply the same workflow.
