# Integration

Merge a caller-approved local result into its named integration branch. The caller owns allowed paths, evidence acceptance and conflict decisions; Git owns local mechanics. No fetch, push or merge into another branch is implied.

1. Verify the absolute checkout, current symbolic branch and full HEAD equal the caller's integration branch and expected SHA. Require a clean index/worktree and no merge/rebase/cherry-pick in progress. Resolve the supplied full result SHA to a commit. Done when target and incoming identity are pinned.
2. Inspect `git -C <checkout> diff --name-status <expected-head>...<result-sha>` and the complete incoming diff against caller scope. Existing `git merge-base --is-ancestor <result-sha> HEAD` success means already integrated; return current HEAD without another merge. Failed reads block the operation. Done when the caller accepts the incoming paths/content or ancestry proves reuse.
3. Recheck expected HEAD, then `git -C <checkout> merge --no-edit <result-sha>`. On conflict retain the branch, worktree and conflict state; report paths and return control to caller. Resolve only unambiguous caller-scoped changes; no reset, automatic theirs/ours or force. Done when merge succeeds or the exact conflict is recorded.
4. Confirm the symbolic branch is unchanged, the result is an ancestor of HEAD, retained artifacts exist and index/worktree are clean. Return result SHA and integrated HEAD; caller performs document reconciliation. Done when verified locally; no remote publication.
