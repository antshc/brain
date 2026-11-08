# Helper

Run from the worktrees skill directory with separate absolute harness and source checkout paths. The caller verifies source routing.

## Create

Pass repository name, single-segment worktree name, pinned local commit and `--new-branch BRANCH` or `--detach`. The helper verifies commit, managed path and unused destination, configures the harness's local Git exclude if needed and reads back registration, branch or detached state, HEAD and cleanliness.

```text
python3 scripts/worktrees.py create --harness ROOT --source CHECKOUT --repo-name NAME --name LEAF --commit SHA --owner RUN_ID --new-branch BRANCH
```

Persist `record` as standalone JSON outside the worktree. The linked Git directory records the same ownership token.

## Remove

Supply `--recoverable` only after verifying the caller's completion policy. Run outside the target. If source is target, use another checkout of the same repository. Pass expected current HEAD, which can differ from creation SHA. The helper verifies ownership, registration and identity, preserves locked or dirty worktrees including ignored and untracked files, blocks if index flags can hide edits, and removes without force.

```text
python3 scripts/worktrees.py remove --harness ROOT --source CHECKOUT --record FILE --expect-head SHA --recoverable
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
