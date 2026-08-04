---
name: create-worktree
description: Create or reuse an isolated git worktree for a feature branch in the given codebase repo path, based off the existing origin/<feature-branch> when one exists, otherwise off origin/<target-branch>. Branch detection is the caller's responsibility.
argument-hint: '<codebase-repo-path> <target-branch> <feature-branch>'
---

# Create Worktree

Create or reuse an isolated git worktree for a feature branch based off a target branch.

**Arguments:** `<codebase-repo-path> <target-branch> <feature-branch>`

The path is supplied by the caller — this skill performs no resolution of its own.

`<skill-directory>` is the directory containing this SKILL.md file: take the absolute path you used to read this file and strip the trailing `/SKILL.md`. Never derive it any other way, and never search the filesystem for it.

```bash
python <skill-directory>/scripts/create_worktree.py <codebase-repo-path> <target-branch> <feature-branch>
```

This performs, in order:

- If the current branch already equals `<feature-branch>`: skip worktree creation, actualize the branch (fetch, pull, merge `origin/<target-branch>`) in place, and report the current directory as `WORKTREE_PATH`.
- Otherwise, create a worktree at `<codebase-repo-path>.worktrees/<feature-branch>`, based on `origin/<feature-branch>` if it exists, otherwise `origin/<target-branch>`. Preferring an existing `origin/<feature-branch>` preserves commits from a prior run on the same branch; falling back to `origin/<target-branch>` is the fresh-branch case.
- If the worktree already exists at that path, reuse it and actualize the branch instead of failing.
- If worktree creation fails for any other reason, the script exits non-zero and reports the error.

## Handling a merge conflict

If the script exits with a merge-conflict error (exit code 2), it prints the list of conflicting files to stderr. The affected directory is whichever one was being actualized: `<codebase-repo-path>` itself when the current branch already equalled `<feature-branch>`, otherwise `<codebase-repo-path>.worktrees/<feature-branch>`.

1. `cd` into the affected directory.
2. Resolve each conflict directly in the current context, preserving the intent of both sides.
3. Stage and continue the merge:
   ```bash
   git add .
   git merge --continue --no-edit
   ```
4. If the merge still fails, **exit** and report the unresolved files as blockers. The script never resolves conflicts itself.

## Output

On success, the script prints to stdout:

```
CODEBASE_REPO_PATH: <codebase-repo-path>
WORKTREE_PATH: <worktree-path>
BRANCH: <feature-branch>
TARGET_BRANCH: <target-branch>
```

Parse this output; switch into `WORKTREE_PATH` for all subsequent commands.

## Exit codes

- `0` — success.
- `1` — usage error (wrong argument count, or `<codebase-repo-path>` does not exist).
- `2` — merge conflict during branch actualization; see **Handling a merge conflict**.
- `3` — worktree creation failed for a reason other than the worktree already existing. **Exit** and report the error.
- `4` — `git pull` or `git merge` failed during branch actualization for a reason other than a merge conflict (e.g. missing upstream tracking, network, or auth failure). The real git error is printed to stderr. **Exit** and report the error — this is not a conflict to resolve.
