---
name: worktree
description: Create or reuse an isolated git worktree. Takes a target branch and feature branch name, creates the worktree based off origin/<target-branch>. No detection logic — callers are responsible for determining what to pass.
argument-hint: '<target-branch> <feature-branch>'
---

# Worktree Setup

Create or reuse an isolated git worktree for a feature branch based off a target branch.

**Arguments:** `<target-branch> <feature-branch>`

## 1. Create worktree

```bash
repo_root=$(git rev-parse --show-toplevel)
mkdir -p "$repo_root.worktrees"
git fetch --all --prune
git worktree add -b <feature-branch> "$repo_root.worktrees/<feature-branch>" "origin/<target-branch>"
```

- If the worktree already exists (exit code 128), reuse it:
  ```bash
  cd "$repo_root.worktrees/<feature-branch>"
  git pull origin <target-branch> --rebase
  ```
- If creation fails for any other reason, **exit** and report the error.

## 2. Switch into worktree

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
