# Worktrees

Orchestrator-only worktree procedures. Implementation workers run in the launch directory the orchestrator sets. Never overwrite, reset, force, or discard existing work.

## Paths

- `HARNESS_ROOT` = `preflight`'s `harness_root`: `git rev-parse --show-toplevel` run from the agent session's launch folder, not the current CWD. **MUST NOT** re-resolve it from a git worktree or nested repo (e.g. code repo under `workspace/`) after a `cd`.
- `WORKTREES_ROOT` = `HARNESS_ROOT/.worktrees/<REPO>`, `<REPO>` = source repository name from `OWNER/REPO`. Same root for both layouts: harness repo only (`SOURCE_ROOT` = `HARNESS_ROOT`) and harness with sub-repositories (`SOURCE_ROOT` = `HARNESS_ROOT/workspace/<REPO>`). Never derive a root from the current worktree or `SOURCE_ROOT`.
- `INTEGRATION_BRANCH` = the new branch validated by preflight or the exact branch from a verified resume checkpoint.
- For a new run, use the integration branch slug as the single-segment worktree leaf under `WORKTREES_ROOT`. On resume use the recorded path.
- Parallel only: assign unused stable worker ordinals, one per qualified ticket. *Run `github` tactic **Name branch*** for the worker suffix and use the resulting branch slug as its worktree leaf. Record the exact branch and path by ticket key in the publication checkpoint before creating the worktree. Reuse that mapping for retries and resume. Recover a legacy mapping from its verified worktree record before reuse.
- Confirm every resolved path stays under `WORKTREES_ROOT`; reuse existing paths or branches only after explicit resume verifies their recorded ownership.

## Integration setup

Verify the preflight-pinned `BASE_COMMIT` exists locally. Use that SHA without fetching or re-resolving the branch. Check the path and local and remote refs. Collision → stop for verified resume or select a unique run suffix through the naming tactic and revalidate the ref before creation. Persist the final branch and path before launch.

*Run `github` Worktrees tactic to create an isolated worktree* at `WORKTREE_PATH` on `INTEGRATION_BRANCH` from `BASE_COMMIT`. Generate the stable run ID before creation. Supply it with `HARNESS_ROOT`, `SOURCE_ROOT`, and repository name. Persist the returned record at `RUN_DIR/worktrees/integration.json` before any worker launch. Verify the path and branch match preflight and use the shared skill's blocker if creation fails.

## Integration writes

- `WORKTREE_PATH` is the sole location for integrated ticket commits, publishing, and chore; preserve it for the caller’s post-implementation checks.
- One writer at a time: start a writer only after the previous result is verified. No merger subagents.
- Sequential: each verified ticket commit lands directly on `INTEGRATION_BRANCH`.
- Parallel: implementers write only in their ticket worktrees; the orchestrator applies verified ticket commits here one at a time and commits after the integration check. Tickets with a `file` conflict never run concurrently. `soft` conflicts may run concurrently. Follow the parallel reference for integration rework.
- Failed or incomplete changes: preserve them and stop advancement.

## Ticket worktrees

Parallel only.

1. **Create:** *Run `github` Worktrees tactic to create an isolated worktree* at `TICKET_WORKTREE(key)` on `TICKET_BRANCH(key)` from the pinned integration HEAD. Save its ownership record at `RUN_DIR/worktrees/<key>.json` and record `@prevHead(key)` before launch.
2. **Remove after integration:** Wait for the worker to exit and verify the ticket result is integrated or the worktree is a verified no-change result. *Run `github` Worktrees tactic to remove the finished worktree* using the ticket record and last verified ticket HEAD. After verified removal, confirm the local ticket branch still points to that HEAD, then delete only that branch with `git -C SOURCE_ROOT branch -D TICKET_BRANCH(key)` (a cherry-picked commit may not be an ancestor). Preserve and report changed refs or blocked removal.
3. Dirty, unmerged, or blocked ticket worktrees: preserve and report path/branch.

## Preserve integration worktree

Keep `INTEGRATION_BRANCH`, the PR, `WORKTREES_ROOT`, `WORKTREE_PATH`, `RUN_DIR`, and `EVIDENCE_ROOT` after implementation. Return their absolute pointers and clean/pushed status in *Implementation handoff*. The caller owns later synchronization, app verification, code review, integration worktree removal, and spec closure. Dirty, unpushed, blocked, or incomplete work stays preserved with its exact path/branch and reason.
