# ralph plugin

## Agents

The agents are from the `crew` plugin and are invoked by `/dev` via `runSubagent`; see [dev/SKILL.md](dev/SKILL.md) steps 3 and 6 for their prompts and gating.

| Agent | Role | Defined in |
|-------|------|-----------|
| `codey-py`, `codey-ai`, `codey-dotnet` | Stack-specific implementers selected per task; unmatched work uses `general-purpose` | [crew agents](../../crew/agents) |
| `chorey` | Maintainability-review agent — reviews Codey's staged changes in step 6, gated on `STATUS: complete`; its own `STATUS` never overrides Codey's recorded outcome | [`plugins/crew/agents/chorey.agent.md`](../../crew/agents/chorey.agent.md) |
| `testy` | Executes functional scenarios via `testing-*` skills after commit/push; returns evidence for Ralph's retries and nonblocking investigation handling | [Testy](../../crew/agents/testy.agent.md) |

Ralph filters ticket queues with Python: implementation excludes `tests`, `spec`, and `hitl`; functional testing requires `tests` and excludes `spec` and `hitl`. All implementation dependencies for a spec must be complete before its functional ticket runs. Failed/incomplete tickets stay open with `tests` and `hitl`; passing tickets close with evidence.

**Via `/dev` skill** (fully automated — fetches milestone, picks tasks, loops):

```
/dev <milestone-title>
```

## Skills

| Skill | Description |
|-------|-------------|
| `/dev` | Implements approved tickets with Codey/Chorey, commits and pushes, then runs approved `tests` tickets with Testy; failures become `hitl` investigations |
| `/fix` | Apply PR review comments |
| `/address` | Address a PR's review discussion — group into issues, investigate, fix, reply; rerunnable |
| `/ralph-build` | Build the project in a caller-supplied workspace, using the harness repo's README build instructions |
| `/create-worktree` | Create/reuse an isolated git worktree in the caller-supplied codebase repo path |
| `/delete-worktree` | Remove a worktree and delete its local feature branch once development is finished (remote branch/PR untouched) |
