# ralph plugin

## Agents

### `ralphy-coder`

Autonomous implementation agent. Explores repo, implements via TDD, builds, tests, commits, updates the issue.

**Direct invocation** (via `@ralphy-coder` in chat):

```
Implement the following GitHub issue.

## TASK
- Issue: #42
- Title: Add retry logic to payment client
- Body: <paste issue body>

## RECENT COMMITS
<last 5 commits for context>
```

**Via `/dev` skill** (fully automated — fetches PRD, picks tasks, loops):

```
/dev
```

## Skills

| Skill | Description |
|-------|-------------|
| `/dev` | AFK loop — picks next issue, invokes `ralphy-coder`, pushes |
| `/fix` | Apply PR review comments |
| `/worktree` | Create/reuse isolated git worktree |
