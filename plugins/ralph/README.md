# ralph plugin

## Agents

### `droid` (from the `droid` plugin)

Autonomous, technology-agnostic implementation agent. Explores repo, implements via TDD, builds, tests, records decisions. Defined in [`plugins/droid/agents/droid.agent.md`](../droid/agents/droid.agent.md); invoked by `/dev` and `/create-worktree` (merge-conflict resolution) via `runSubagent`.

**Invoked by `/dev`** (per task, prompt built in `dev/SKILL.md` step 4):

```
## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT CHANGES
<last 5 commits>
```

Ralph launches Droid from the worktree, passing `HARNESS_REPO_PATH` via a `## HARNESS` prompt section. The worktree path stays outside the prompt.

**Invoked by `/create-worktree`** (merge-conflict resolution, smaller prompt — see `create-worktree/SKILL.md` step 2).

**Via `/dev` skill** (fully automated — fetches milestone, picks tasks, loops):

```
/dev <milestone-title>
```

## Skills

| Skill | Description |
|-------|-------------|
| `/dev` | AFK loop — picks next issue, invokes `droid`, pushes |
| `/fix` | Apply PR review comments |
| `/create-worktree` | Create/reuse an isolated git worktree in the caller-supplied codebase repo path |
| `/delete-worktree` | Remove a worktree and delete its local feature branch once development is finished (remote branch/PR untouched) |
