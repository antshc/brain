---
name: create-worktree
description: Resolve the source repo (workspace source repo when present, else current repo) and create or reuse an isolated git worktree for a feature branch, based off the existing origin/<feature-branch> when one exists, otherwise off origin/<target-branch>. Branch detection is the caller's responsibility — this skill only resolves which repo to operate in.
argument-hint: '<target-branch> <feature-branch>'
---

# Create Worktree

Create or reuse an isolated git worktree for a feature branch based off a target branch.

**Arguments:** `<target-branch> <feature-branch>`

## 0. Resolve source repo

If `/resolve-harness` is available, invoke it from the current directory and retain every emitted `KEY=value` line as `HARNESS_SETTINGS` for this invocation. Use its `HARNESS_ROOT` value.

- If the skill is unavailable, or it emits `HARNESS_ROOT=`, set `HARNESS_ROOT` to the current directory.
- If the available skill exits non-zero, **exit** and report its error.

The actual source code may live in a separate repo under `workspace/` in `HARNESS_ROOT`. Resolve which repo to develop in **before** any branch or worktree operation.

```bash
src_git=$(find "$HARNESS_ROOT/workspace" -maxdepth 2 -name .git -type d 2>/dev/null | head -n1)
if [ -n "$src_git" ]; then
  SOURCE_REPO=$(dirname "$src_git")
else
  SOURCE_REPO=$HARNESS_ROOT
fi
cd "$SOURCE_REPO"
```

- If a `.git` directory is found under `workspace/` (including one subfolder level), develop in that source repo.
- Otherwise, fall back to the current (harness) repo.

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
2. Invoke the `droid` agent (or `general-purpose` if unavailable) from the current worktree directory. Do not provide a workspace-path or harness-settings argument. Droid resolves its own Harness Settings. Pass the following prompt:
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
if git rev-parse --verify --quiet "origin/<feature-branch>" > /dev/null; then
  base_ref="origin/<feature-branch>"
else
  base_ref="origin/<target-branch>"
fi
git worktree add -b <feature-branch> "$repo_root.worktrees/<feature-branch>" "$base_ref"
```

Preferring an existing `origin/<feature-branch>` preserves commits from a prior run on the same branch; falling back to `origin/<target-branch>` is the fresh-branch case.

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
