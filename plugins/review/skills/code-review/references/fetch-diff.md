# Fetch PR diff

Acquire one immutable review snapshot before analysis. Use an isolated temporary clone; never switch/reset the caller checkout or recreate an implementation worktree.

1. Read PR metadata with `gh pr view PR_NUMBER --repo OWNER/REPO --json url,title,body,headRefOid,baseRefOid`. Retain `REVIEW_HEAD`, `REVIEW_BASE` and body. Done when identities and both SHAs are resolved.
2. Create a unique run-owned temporary directory outside the caller repository; set `REVIEW_REPO` to its `repo` child and `DIFF_DIR` to its `diff` child. Clone with `gh repo clone OWNER/REPO REVIEW_REPO -- --no-checkout`. Fetch `refs/pull/PR_NUMBER/head` and the exact base commit into that clone, verify the fetched head equals `REVIEW_HEAD`, and check out detached `REVIEW_HEAD`. If PR refs or commits cannot be acquired, stop with incomplete review; never substitute another revision. Done when clone HEAD matches the captured PR head.
3. Compute `REVIEW_MERGE_BASE` using `git -C REVIEW_REPO merge-base REVIEW_BASE REVIEW_HEAD`. Generate the complete diff from merge-base to head with `git diff --no-ext-diff --no-textconv --find-renames REVIEW_MERGE_BASE REVIEW_HEAD`. Inventory changed files using `git diff --name-status -z` and additions/deletions using `--numstat -z` with the same revisions/options. Inspect binary, deleted and renamed files explicitly; inaccessible content is uncovered scope, not an empty diff. Done when inventory and diff cover the same pinned range.
4. Split per-file patches into unique numbered files in `DIFF_DIR`; write `_manifest.tsv` as `REAL_PATH<TAB>DIFF_FILENAME`, using exact Git destination paths (old path for deletions). Decode Git-quoted names correctly; do not flatten paths into filenames, which can collide. If a path contains tabs/newlines and cannot be represented by the manifest, stop and report unsupported input. Use literal pathspecs when generating per-file patches; preserve rename metadata. Verify every inventory entry is represented exactly once. Done when manifest and patches are complete.
5. Re-read PR head/base; if either changed, discard only this run's temporary snapshot and restart acquisition. Return `REVIEW_REPO`, `DIFF_DIR`, manifest, head/base/merge-base and metadata to the parent. Done when snapshot identity is confirmed.

Only the parent acquires the snapshot. Reviewers use these paths without refetching. Retain evidence/results before removing the run-owned temporary directory after review. Never remove unrelated directories.

## Anchors

Use exact manifest paths for posting. Only commentable right-side changed lines qualify for inline posting; never invent anchors for deleted/binary files. Retain actionable findings without valid anchors as unposted findings with reason; do not hide them as a clean review. Check the current head/base again before posting.
