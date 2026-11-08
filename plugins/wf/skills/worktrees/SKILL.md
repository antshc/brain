---
name: worktrees
description: >-
  Manage local Git worktrees. Use to inspect a checkout, create an isolated worktree, reuse a recorded worktree, or remove a finished worktree.
---

# Worktrees

The caller owns repository routing, fetch, branch naming, overlays, integration, publication, branch deletion and editor exclusions.

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

## Reference

Before creating or removing, read [Helper](references/helper.md) in full. Report its result, changed exclude files and blockers.

## Gotchas

Git exit 128 covers multiple errors. Check disk and registration before treating the path as occupied.
