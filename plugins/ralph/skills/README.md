# ralph plugin

## Agents

Both agents are from the `crew` plugin and are invoked by `/dev` via `runSubagent`; see [dev/SKILL.md](dev/SKILL.md) steps 3 and 6 for their prompts and gating.

| Agent | Role | Defined in |
|-------|------|-----------|
| `codey` | Autonomous, technology-agnostic implementation agent (explores, implements via TDD, builds, tests) — invoked per task in step 3; falls back to `general-purpose` when unavailable | [`agents/crew/codey.agent.md`](../../agents/crew/codey.agent.md) |
| `chorey` | Maintainability-review agent — reviews Codey's checkpoint commit in step 6, gated on `STATUS: complete`; its own `STATUS` never overrides Codey's recorded outcome | [`agents/crew/chorey.agent.md`](../../agents/crew/chorey.agent.md) |

**Via `/dev` skill** (fully automated — fetches milestone, picks tasks, loops):

```
/dev <milestone-title>
```

## Skills

| Skill | Description |
|-------|-------------|
| `/dev` | AFK loop — picks next issue, invokes `codey` then (gated) `chorey`, pushes |
| `/fix` | Apply PR review comments |
| `/address` | Address a PR's review discussion — group into issues, investigate, fix, reply; rerunnable |
| `/ralph-build` | Build the project in a caller-supplied workspace, using the harness repo's README build instructions |
| `/create-worktree` | Create/reuse an isolated git worktree in the caller-supplied codebase repo path |
| `/delete-worktree` | Remove a worktree and delete its local feature branch once development is finished (remote branch/PR untouched) |
