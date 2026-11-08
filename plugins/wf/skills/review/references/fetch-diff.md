# Fetch PR diff

Resolve and fetch the PR, follow the requested route's setup, then [build the per-file diff](#build-the-per-file-diff). Only the parent prepares the snapshot. Give reviewers the returned paths and commit IDs.

## Resolve and fetch the PR

1. Resolve `SOURCE_ROOT` from the explicit caller input, current checkout, or harness workspace. Verify it is an existing Git repository and select `REMOTE` whose URL identifies the PR's `OWNER/REPO` (the base repository, including for fork PRs). If no unique match exists, ask for the path or remote and wait. Record caller HEAD, status, and existing worktrees.
2. Read `gh pr view PR_NUMBER --repo OWNER/REPO --json url,title,body,headRefOid,baseRefOid`. Retain `REVIEW_HEAD`, `REVIEW_BASE`, title, and body. Choose unused temporary refs under `refs/review/RUN_ID/`.
3. Fetch the PR head through the verified remote with `git -C SOURCE_ROOT fetch --no-tags REMOTE refs/pull/PR_NUMBER/head:refs/review/RUN_ID/head`. Fetch the exact `REVIEW_BASE` SHA into `refs/review/RUN_ID/base`. Verify both refs against the captured SHAs. On mismatch or unavailable objects, clean up and reacquire or report incomplete acquisition. Resolve `REVIEW_MERGE_BASE` with `git -C SOURCE_ROOT merge-base REVIEW_BASE REVIEW_HEAD`. For a shallow history, fetch the required ancestry or report the blocker.

## Code

Use a fresh detached review worktree in the existing repository. **MUST NOT** clone, copy the repository, reuse the implementation worktree, or switch or reset the caller checkout. Capture `HARNESS_ROOT` before changing directories, choose the leaf `review-pr-PR_NUMBER-RUN_ID`, and create a unique run-owned `DIFF_DIR` outside the repository and all worktrees.

*Run `worktrees` skill to create an isolated worktree* with `HARNESS_ROOT`, `SOURCE_ROOT`, repository name, run ID, selected leaf and detached `REVIEW_HEAD`. Use the returned path as `REVIEW_REPO` and save the ownership record in `DIFF_DIR`. On a partial creation, preserve the temporary refs and report the path until Reconcile confirms its state. Use this new worktree for source inspection; no implementation branch checkout, clone or new branch. Done when the fresh review worktree is verified.

After building the diff, re-read the PR head and base. On change, follow Cleanup, then reacquire. After two changed-snapshot retries, report a stale review. Return `SOURCE_ROOT`, `REVIEW_REPO`, `DIFF_DIR`, `MANIFEST`, head/base/merge-base, metadata, and cleanup ownership.

On failure, follow [Cleanup](#cleanup). Retain worktree ownership information for reconciliation after a partial creation.

## HITL

Use the interactive session's matching checkout. If its status is dirty, stop and ask before checkout. Run `gh pr checkout PR_NUMBER --repo OWNER/REPO`, then capture `COMMIT_ID` with `git rev-parse HEAD`. Require it to equal `REVIEW_HEAD`. On mismatch, stop and reacquire before review. Set `REVIEW_REPO` to the checked-out repository and create a run-owned `DIFF_DIR` under `bin/review_diff/`.

After building the diff, verify PR head and base still match the fetched snapshot. If either changed, clean up this attempt and reacquire before the review starts. After two changed-snapshot retries, report a stale review. Return the reviewed `COMMIT_ID`, `DIFF_DIR`, and `MANIFEST`. On success, delete only this run's temporary refs using `git update-ref -d REF EXPECTED_SHA` and retain the diff for the session. On failure, also remove this run's diff directory. Leave the interactive checkout in place.

## Build the per-file diff

Generate the full fetched PR change from the pinned commits using `git -C REVIEW_REPO diff --no-ext-diff --no-textconv --find-renames REVIEW_MERGE_BASE REVIEW_HEAD`. Inventory files with `--name-status -z` and additions/deletions with `--numstat -z` over the same range/options. Inspect binary, deleted and renamed files explicitly; inaccessible content is uncovered scope, not an empty diff. Split per-file patches into unique numbered files in `DIFF_DIR`; write `_manifest.tsv` as `REAL_PATH<TAB>DIFF_FILENAME`, using exact Git destination paths (old paths for deletions). Decode Git-quoted names, use literal pathspecs, preserve rename metadata, and verify every inventory entry appears once. Unsupported tab/newline paths block manifest creation; never flatten paths into colliding filenames. Done when inventory, manifest and patches cover the same pinned range.

Use `DIFF_DIR/_manifest.tsv` as `MANIFEST`. Anchor inline comments to exact manifest paths and commentable right-side changed lines. Retain unanchored findings with their reason.

## Cleanup

After retaining findings and evidence, leave `REVIEW_REPO` and *run `worktrees` skill to remove the finished worktree* with its saved ownership record and pinned `REVIEW_HEAD`. Retain the temporary refs until removal is verified so the pinned snapshot remains recoverable. Preserve/report dirty worktrees or failed removal; never recursively delete a registered worktree. After successful removal (or if creation never occurred), delete only this run's temporary refs using `git update-ref -d REF EXPECTED_SHA`, then remove its diff/temp directory. Preserve caller worktrees, branch refs, HEAD and files; report any unexpected change. Keep fetched Git objects in the shared database; no pruning/GC.
