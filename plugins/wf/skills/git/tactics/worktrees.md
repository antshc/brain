## Constraints

- Capture the absolute harness root before changing directories. From a linked worktree, require an explicit or recorded root. Verify the source checkout against the intended repository and pass it separately.
- Use the bundled Python helper for creation and removal under `<harness-root>/.worktrees/<repo-name>/<worktree-name>`. Block on missing tooling or unverifiable state.
- Preserve dirty, locked and unowned worktrees. **MUST NOT** force, reset, prune or recursively delete a worktree.

## Tactics

Recheck tactics when the caller's goal or observed Git state changes.

**Inspect** — when checkout state is unknown, compare the exact path on disk with `git -C SOURCE worktree list --porcelain -z`. If present, read the linked Git directory, branch or detached state, HEAD, lock and status including untracked and ignored files. Return verified state or report missing or conflicting evidence.

**Create** — when the caller needs isolation, use an unused managed path, pinned local commit and new branch or detached HEAD. Persist the verified creation's ownership record outside the worktree.

**Reuse** — when the caller permits reuse, match the caller's record to `brain-worktree.json` in the linked Git directory. Verify exact path, linked Git directory, source common Git directory, owner, ownership token, expected branch or detached state and expected HEAD. Reuse only a clean, unlocked match. Report blockers.

**Remove** — when cleanup is authorized, wait for writers to exit and verify the work is recoverable. Use the ownership record and expected current HEAD. Confirm both path and registration are absent or report what remains.

**Reconcile** — after a collision, interruption or partial result, inspect before retrying. Retry only from verified ownership or a fresh unused target. Preserve unexpected worktrees and report the last verified state.

## Create

Pass repository name, single-segment worktree name, pinned local commit and `--new-branch BRANCH` or `--detach`. The helper verifies commit, managed path and unused destination, configures the harness's local Git exclude if needed and reads back registration, branch or detached state, HEAD and cleanliness.

```text
GIT_TOOL worktree create --harness ROOT --source CHECKOUT --repo-name NAME --name LEAF --commit SHA --owner RUN_ID --new-branch BRANCH
```

Persist `record` as standalone JSON outside the worktree. The linked Git directory records the same ownership token.

## Remove

Supply `--recoverable` only after verifying the caller's completion policy. Run outside the target. If source is target, use another checkout of the same repository. Pass expected current HEAD, which can differ from creation SHA. The helper verifies ownership, registration and identity, preserves locked or dirty worktrees including ignored and untracked files, blocks if index flags can hide edits, and removes without force.

```text
GIT_TOOL worktree remove --harness ROOT --source CHECKOUT --record FILE --expect-head SHA --recoverable
```

## Results

The helper emits one JSON object on stdout.

| Field | Content |
|---|---|
| `status` | `created`, `removed`, `absent` or `blocked`. |
| `record` | On creation, `owner` is the caller's run ID, `token` is the generation identity, `path` is the canonical worktree path, `commonDir` is the source Git common directory, `gitDir` is the linked Git directory, `branch` is the local branch or null for detached HEAD, and `head` is the creation SHA. |
| `changedExcludeFiles` | On creation, paths changed by the helper. Empty if none. |
| `path` | Canonical target path when resolved. `removed` means both disk path and registration are gone. `absent` means both were already missing. |
| `branch` | Requested branch on creation when the target resolves, or null for detached. |
| `reason` | On `blocked`, the failure reason. |

```json
{"status":"created","record":{"owner":"review-42","token":"example-token","path":"/harness/.worktrees/repo/review-42","commonDir":"/source/.git","gitDir":"/source/.git/worktrees/review-42","branch":null,"head":"0123456789abcdef0123456789abcdef01234567"},"changedExcludeFiles":[]}
```

A blocked operation exits nonzero and reports the reason on stderr. Interruptions or partial results can leave a new path or branch. Use Reconcile before retrying.

Use `worktree inspect` with `--repo-name` and `--name`, or with `--record`. For `worktree reuse` or `worktree reconcile` of an existing checkout, supply `--record` and `--expect-head`. A blocked reconciliation leaves ownership and files untouched.
