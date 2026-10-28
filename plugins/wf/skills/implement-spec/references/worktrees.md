# Worktrees

Orchestrator-only worktree procedures; agents only receive worktree paths. Never overwrite, reset, force, or discard existing work.

## Paths

- `WORKTREES_ROOT` = `HARNESS_ROOT/workspace/REPO.worktrees` (sibling of `SOURCE_ROOT`); never derive a root from the current worktree.
- `INTEGRATION_BRANCH` = `preflight`'s `integration_branch` (`feat/<INITIATIVE_ID>`); never invent another name. Unique run suffix (*Integration setup* step 1) → append `-<suffix>` to both branch and `WORKTREE_PATH`.
- `WORKTREE_PATH` = `WORKTREES_ROOT/INITIATIVE_ID` (integration worktree on `INTEGRATION_BRANCH`).
- Parallel only: `TICKET_BRANCH(n)` = `INTEGRATION_BRANCH-t<n>`; `TICKET_WORKTREE(n)` = `WORKTREES_ROOT/INITIATIVE_ID-t<n>`, where `n` is the ticket number.
- Confirm every resolved path stays under `WORKTREES_ROOT`; never reuse an existing path or branch.

## Integration setup

1. Inspect `git -C SOURCE_ROOT worktree list --porcelain`, branch refs, and the destination. Create only missing parent directories. Existing path or proposed integration branch → stop for explicit resume or a unique run suffix.
2. Verify `workspace/` is ignored: `git -C HARNESS_ROOT check-ignore -q workspace/`. Not ignored → stop and report; never edit harness ignore files.
3. Fetch the confirmed source remote/base; record its commit as `BASE_COMMIT` (reuse Breakdown Initiative's value when set). Fetch failure → report; never use a stale base.
4. `git -C SOURCE_ROOT worktree add -b INTEGRATION_BRANCH WORKTREE_PATH BASE_COMMIT`. Verify clean, on `INTEGRATION_BRANCH`, `HEAD` = `BASE_COMMIT`.

## Integration writes

- `WORKTREE_PATH` is the sole location for integrated ticket commits, publishing, chore, app verification, and fix commits.
- One writer at a time: start a writer only after the previous result is verified. No merger subagents.
- Sequential: each verified ticket commit lands directly on `INTEGRATION_BRANCH`.
- Parallel: implementers write only in their ticket worktrees; verified ticket commits are cherry-picked here one at a time; conflicting tickets never run concurrently.
- Failed or incomplete changes: preserve them and stop advancement.

## Ticket worktrees

Parallel only.

1. **Create:** `git -C SOURCE_ROOT worktree add -b TICKET_BRANCH(n) TICKET_WORKTREE(n) <integration HEAD>`. Verify clean and `HEAD` equals the integration head; record `@prevHead(n)`.
2. **Remove after integration:** `git -C SOURCE_ROOT worktree remove TICKET_WORKTREE(n)` without force, then `git -C SOURCE_ROOT branch -D TICKET_BRANCH(n)` (cherry-picked commits are not ancestors, so `-d` refuses).
3. Dirty, unmerged, or blocked ticket worktrees: preserve and report path/branch.

## Actualize and cleanup

Run after code review. Keep `INTEGRATION_BRANCH`, the PR, and `WORKTREES_ROOT`.

1. **Fetch:** `git -C WORKTREE_PATH fetch REMOTE INTEGRATION_BRANCH`.
2. **Commit pending changes:** uncommitted changes → stage and commit with subject `chore(<INITIATIVE_ID>): commit pending changes`; record them in the report.
3. **Merge remote:** `git -C WORKTREE_PATH merge --no-edit REMOTE/INTEGRATION_BRANCH` when the remote head is not an ancestor of `HEAD`. **MUST NOT** rebase, reset, or force.
4. **Resolve conflicts:** keep both sides' intent; rerun the cheapest affected checks; commit the merge. Unresolvable → `git merge --abort`, preserve, report; skip removal.
5. **Push:** `git -C WORKTREE_PATH push REMOTE INTEGRATION_BRANCH`. Verify `HEAD` equals the remote head and the worktree is clean.
6. **Remove:** change CWD to `SOURCE_ROOT`; `git -C SOURCE_ROOT worktree remove WORKTREE_PATH` without force. Verify absent from disk and from `git worktree list`.
7. **Ticket worktrees:** confirm none remain unless preserved and reported.
8. Dirty, unpushed, or failed removal → preserve and report exact path/branch.
