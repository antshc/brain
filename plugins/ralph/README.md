# ralph plugin

## Agents

### `csdroid` (from the `pet` plugin)

Autonomous C# implementation agent. Explores repo, implements via TDD, builds, tests, records decisions. Defined in [`plugins/pet/agents/csdroid.agent.md`](../pet/agents/csdroid.agent.md); invoked by `/dev` and `/worktree` (merge-conflict resolution) via `runSubagent`.

**Invoked by `/dev`** (per task, prompt built in `dev/SKILL.md` step 4):

```
## HARNESS_ROOT
<absolute path to the harness repo>

## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT CHANGES
<last 5 commits>
```

Ralph launches Csdroid from the worktree. The worktree path remains Ralph-only orchestration state and is not sent to Csdroid.

**Invoked by `/worktree`** (merge-conflict resolution, smaller prompt — see `worktree/SKILL.md` step 2).

**Via `/dev` skill** (fully automated — fetches milestone, picks tasks, loops):

```
/dev <milestone-title>
```

## Skills

| Skill | Description |
|-------|-------------|
| `/dev` | AFK loop — picks next issue, invokes `csdroid`, pushes |
| `/fix` | Apply PR review comments |
| `/worktree` | Resolve the source repo (workspace source repo when present, else current repo) and create/reuse an isolated git worktree |
