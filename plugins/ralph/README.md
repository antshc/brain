# ralph plugin

## Agents

### `codey` (from the `crew` plugin)

Autonomous, technology-agnostic implementation agent. Explores repo, implements via TDD, builds, tests, records decisions. Defined in [`plugins/crew/agents/codey.agent.md`](../crew/agents/codey.agent.md); invoked by `/dev` via `runSubagent`.

**Invoked by `/dev`** (per task, prompt built in `dev/SKILL.md` step 3):

```
## TASK
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT CHANGES
<last 5 commits>
```

Ralph launches Codey from the worktree, passing `HARNESS_REPO_PATH` via a `## HARNESS` prompt section. The worktree path stays outside the prompt. Codey's `STATUS` alone governs the loop's distill, commit, and issue-handling steps; falls back to the `general-purpose` agent when Codey is unavailable.

### `chorey` (from the `crew` plugin)

Maintainability-review agent. Reviews Codey's checkpoint commit for behavior-preserving cleanup. Defined in [`plugins/crew/agents/chorey.agent.md`](../crew/agents/chorey.agent.md); invoked by `/dev` via `runSubagent`.

**Invoked by `/dev`** (per task, prompt built in `dev/SKILL.md` step 6, only when Codey reports `STATUS: complete`, after Codey's checkpoint commit lands):

```
## HARNESS
HARNESS_REPO_PATH=<$HARNESS_REPO_PATH>

## DIFF
<checkpoint commit diff>

## BASELINE_COMMIT
<checkpoint commit sha>
```

Skipped entirely when Codey's `STATUS` is `partial`/`blocked`, or when `chorey` is unavailable — the run's outcome is unchanged either way. Chorey's own `STATUS` never changes the outcome the loop records; its findings surface in its own follow-up commit body only, never Codey's.

**Via `/dev` skill** (fully automated — fetches milestone, picks tasks, loops):

```
/dev <milestone-title>
```

## Skills

| Skill | Description |
|-------|-------------|
| `/dev` | AFK loop — picks next issue, invokes `codey` then (gated) `chorey`, pushes |
| `/fix` | Apply PR review comments |
| `/create-worktree` | Create/reuse an isolated git worktree in the caller-supplied codebase repo path |
| `/delete-worktree` | Remove a worktree and delete its local feature branch once development is finished (remote branch/PR untouched) |
