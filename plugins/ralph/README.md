# ralph plugin

## Agents

### `codey`

Autonomous, technology-agnostic implementation agent. It works only in its invocation directory and reports `STATUS`, `SUMMARY`, `FILES`, `GOTCHAS UPDATED`, and `NOTES`.

### `chorey`

Technology-agnostic maintainability reviewer. It verifies current uncommitted work before review, applies behavior-preserving refactors only when justified, and re-verifies only after edits.

## Skills

| Skill | Description |
|---|---|
| `/to-codey <task>` | Run Codey directly for one task |
| `/to-chorey` | Review current uncommitted work with Chorey |
| `/ralph-init` | Manually initialize absent Ralph guidance from repository evidence |
| `/ralph-dev` | AFK loop that invokes Codey then Chorey |
| `/ralph-fix` | Apply PR review comments |
| `/ralph-worktree` | Prepare a deterministic worktree and use Codey for merge conflicts |
