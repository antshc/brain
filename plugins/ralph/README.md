# ralph plugin

## Agents

### `codey`

Autonomous implementation agent. It works only in its invocation directory, uses the persona confirmed by `/ralph-init`, and reports `STATUS`, `SUMMARY`, `FILES`, `GOTCHAS UPDATED`, and `NOTES`.

### `chorey`

Maintainability reviewer. It uses the persona confirmed by `/ralph-init`, verifies current uncommitted work before review, applies behavior-preserving refactors only when justified, and re-verifies only after edits.

## Skills

| Skill | Description |
|---|---|
| `/to-codey <task>` | Run Codey directly for one task |
| `/to-chorey` | Review current uncommitted work with Chorey |
| `/ralph-init` | Initialize Ralph guidance, required `VERIFY.md`, and confirmed agent personas from repository evidence |
| `/ralph-dev` | AFK loop that invokes Codey then Chorey |
| `/ralph-fix` | Apply PR review comments |
| `/ralph-worktree` | Prepare a deterministic worktree and use Codey for merge conflicts |
