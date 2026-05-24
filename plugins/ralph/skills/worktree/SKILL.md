---
name: worktree
description: Create or reuse an isolated git worktree. Takes a target branch and feature branch name, creates the worktree based off origin/<target-branch>. No detection logic — callers are responsible for determining what to pass.
argument-hint: '<target-branch> <feature-branch>'
---

# Worktree Setup

Create or reuse an isolated git worktree for a feature branch based off a target branch.

**Arguments:** `<target-branch> <feature-branch>`

## Actualize Branch

Bring the current branch up to date with the latest remote changes and the target branch. Run whenever entering an existing branch.

```bash
git fetch --all --prune
git pull
git merge origin/<target-branch>
```

If the merge exits non-zero (conflicts detected):

1. Collect the list of conflicting files:
   ```bash
   git diff --name-only --diff-filter=U
   ```
2. Invoke the `csdroid` agent (or `general-purpose` if unavailable) with the following prompt:
   ```
   ## Resolve Merge Conflicts
   The following files have merge conflicts after merging origin/<target-branch> into <feature-branch>.
   Resolve each conflict, preserving the intent of both sides.
   Files: <conflict-file-list>
   ```
3. After the agent resolves the conflicts:
   ```bash
   git add .
   git merge --continue --no-edit
   ```
4. If the merge still fails, **exit** and report the unresolved files as blockers.

## 1. Check current branch

```bash
current_branch=$(git branch --show-current)
```

If `current_branch` equals `<feature-branch>`:

```bash
WORKTREE_PATH=$(pwd)
BRANCH=$current_branch
```

Run **Actualize Branch**, then jump to **Output**.

## 2. Create worktree

```bash
repo_root=$(git rev-parse --show-toplevel)
mkdir -p "$repo_root.worktrees"
git fetch --all --prune
git worktree add -b <feature-branch> "$repo_root.worktrees/<feature-branch>" "origin/<target-branch>"
```

- If the worktree already exists (exit code 128), `cd` into it and run **Actualize Branch**:
  ```bash
  cd "$repo_root.worktrees/<feature-branch>"
  ```
- If creation fails for any other reason, **exit** and report the error.

## 3. Switch into worktree

```bash
cd "$repo_root.worktrees/<feature-branch>"
```

## Output

Report the result:

```
WORKTREE_PATH: $repo_root.worktrees/<feature-branch>
BRANCH: <feature-branch>
TARGET_BRANCH: <target-branch>
```
