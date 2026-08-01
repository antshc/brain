---
name: ralph-worktree
description: Resolve the source repo (workspace source repo when present, else current repo) and create or reuse an isolated git worktree for a feature branch based off origin/<target-branch>. Branch detection is the caller's responsibility — this skill only resolves which repo to operate in.
argument-hint: '<target-branch> <feature-branch> [source-repo]'
---

# Worktree Setup

Create or reuse an isolated git worktree for a feature branch based off a target branch.

**Arguments:** `<target-branch> <feature-branch> [source-repo]`

## 0. Resolve repos

If the optional `<source-repo>` argument is given, the caller already resolved it — set `SOURCE_REPO` to that value directly and skip detection.

Otherwise, invoke the `/ralph-harness` skill to resolve `HARNESS_ROOT` and `SOURCE_REPO`.

```bash
cd "$SOURCE_REPO"
```

All subsequent commands run inside `SOURCE_REPO`. Worktrees are created as `<SOURCE_REPO>.worktrees/<feature-branch>`.

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
2. Invoke the `codey` agent (or `general-purpose` if unavailable) from the current worktree directory. Do not provide a workspace-path argument. Codey uses its invocation directory as its workspace. Pass the following prompt:
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
repo_root=$SOURCE_REPO
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
SOURCE_REPO: $SOURCE_REPO
WORKTREE_PATH: $repo_root.worktrees/<feature-branch>
BRANCH: <feature-branch>
TARGET_BRANCH: <target-branch>
```
