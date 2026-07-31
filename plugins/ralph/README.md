# ralph plugin

## Agents

### `droid` (from the `droid` plugin)

Autonomous, technology-agnostic implementation agent. Explores repo, implements via TDD, builds, tests, records decisions. Defined in [`plugins/droid/agents/droid.agent.md`](../droid/agents/droid.agent.md); invoked by `/dev` and `/worktree` (merge-conflict resolution) via `runSubagent`.

**Invoked by `/dev`** (per task, prompt built in `dev/SKILL.md` step 4):

```
## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT CHANGES
<last 5 commits>
```

Ralph launches Droid from the worktree. The worktree path and Harness Settings remain outside the prompt; Droid independently resolves Harness Settings from its invocation directory.

**Invoked by `/worktree`** (merge-conflict resolution, smaller prompt — see `worktree/SKILL.md` step 2).

**Via `/dev` skill** (fully automated — fetches milestone, picks tasks, loops):

```
/dev <milestone-title>
```

## Skills

| Skill | Description |
|-------|-------------|
| `/dev` | AFK loop — picks next issue, invokes `droid`, pushes |
| `/fix` | Apply PR review comments |
| `/worktree` | Run the deterministic Source Repository contract and create/reuse an isolated git worktree |
