# Worktrees

Orchestrator-only worktree procedures; agents only receive worktree paths. Never overwrite, reset, force, or discard existing work.

## Paths

- `HARNESS_ROOT` = `preflight`'s `harness_root`: `git rev-parse --show-toplevel` run from the agent session's launch folder, not the current CWD. **MUST NOT** re-resolve it from a git worktree or nested repo (e.g. code repo under `workspace/`) after a `cd`.
- `WORKTREES_ROOT` = `HARNESS_ROOT/.worktrees/<REPO>`, `<REPO>` = source repository name from `OWNER/REPO`. Same root for both layouts: harness repo only (`SOURCE_ROOT` = `HARNESS_ROOT`) and harness with sub-repositories (`SOURCE_ROOT` = `HARNESS_ROOT/workspace/<REPO>`). Never derive a root from the current worktree or `SOURCE_ROOT`. `HARNESS_ROOT/.worktrees/` or its `<REPO>/` child already exists → reuse it; absent → create it (`mkdir -p`).
- `INTEGRATION_BRANCH` = `preflight`'s `integration_branch` (`feat/<INITIATIVE_ID>`); never invent another name. Unique run suffix (*Integration setup* step 1) → append `-<suffix>` to both branch and `WORKTREE_PATH`.
- `WORKTREE_PATH` = `WORKTREES_ROOT/INITIATIVE_ID` (integration worktree on `INTEGRATION_BRANCH`).
- Parallel only: `TICKET_BRANCH(n)` = `INTEGRATION_BRANCH-t<n>`; `TICKET_WORKTREE(n)` = `WORKTREES_ROOT/INITIATIVE_ID-t<n>`, where `n` is the ticket number.
- Confirm every resolved path stays under `WORKTREES_ROOT`; never reuse an existing worktree path (the `INITIATIVE_ID` leaf) or branch.

## Worktree root setup

Idempotent; before the first `git worktree add`. Add only missing entries; preserve other content and comments; never commit. Report every file changed.

1. **Git:** `git -C HARNESS_ROOT check-ignore -q .worktrees/`. Not ignored → append `/.worktrees/` to `git -C HARNESS_ROOT rev-parse --path-format=absolute --git-path info/exclude`; recheck. Still not ignored (tracked negation) → stop and report.
2. **VS Code:** `HARNESS_ROOT/.vscode/settings.json` (create if absent) holds `"search.exclude": {"**/.worktrees": true}` and `"files.watcherExclude": {"**/.worktrees/**": true}`; merge into existing objects.
3. **JetBrains:** only when `HARNESS_ROOT/.idea/` exists. Rider (`.idea/.idea.*/.idea/`) → `indexLayout.xml` `<explicitExcludes>` holds `<Path>` to `HARNESS_ROOT/.worktrees` relative to the solution directory. Other IDEs → each `.idea/*.iml` `<content>` whose url resolves to `HARNESS_ROOT` holds `<excludeFolder url="<content url>/.worktrees" />`.

Done when the git check passes and existing editor configs exclude `.worktrees`.

## Integration setup

1. Inspect `git -C SOURCE_ROOT worktree list --porcelain`, branch refs, and the destination. Create only missing parent directories. Existing path or proposed integration branch → stop for explicit resume or a unique run suffix.
2. Run *Worktree root setup*.
3. Fetch the confirmed source remote/base; record its commit as `BASE_COMMIT` (reuse Breakdown Initiative's value when set). Fetch failure → report; never use a stale base.
4. `git -C SOURCE_ROOT worktree add -b INTEGRATION_BRANCH WORKTREE_PATH BASE_COMMIT`. Verify clean, on `INTEGRATION_BRANCH`, `HEAD` = `BASE_COMMIT`.

## Integration writes

- `WORKTREE_PATH` is the sole location for integrated ticket commits, publishing, chore, app verification, and fix commits.
- One writer at a time: start a writer only after the previous result is verified. No merger subagents.
- Sequential: each verified ticket commit lands directly on `INTEGRATION_BRANCH`.
- Parallel: implementers write only in their ticket worktrees; verified ticket commits are cherry-picked here one at a time; tickets with a `file` conflict never run concurrently. `soft` conflicts may run concurrently; a textual conflict at cherry-pick goes to the rebase rework round, a contract break to the post-merge check.
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
