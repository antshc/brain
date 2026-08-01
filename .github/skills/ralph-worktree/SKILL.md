---
argument-hint: <target-branch> <feature-branch>
description: Resolve the deterministic Source Repository contract and create or reuse an isolated git worktree for a feature branch based off origin/<target-branch>.
metadata:
    github-path: plugins/ralph/skills/ralph-worktree
    github-ref: refs/tags/v0.1.0-479
    github-repo: https://github.com/antshc/brain
    github-tree-sha: abfed5becc9389cab3e6791bb0dcdd88d08906c7
name: ralph-worktree
---
# Worktree Setup

Create or reuse an isolated git worktree for a feature branch based off a target branch.

**Arguments:** `<target-branch> <feature-branch>`

## 0. Resolve Harness Root

Set `HARNESS_ROOT` to the current directory.

## 1. Prepare worktree

Run the executable contract before any branch operation:

```bash
set +e
worktree_output=$(<worktree-skill-directory>/scripts/prepare_worktree.sh "$HARNESS_ROOT" <target-branch> <feature-branch>)
worktree_status=$?
set -e
```

- An absent `workspace/` selects `HARNESS_ROOT` as `SOURCE_REPO`.
- A present `workspace/` must contain exactly one direct-child Git repository. Zero candidates report `No Source Repository found in workspace: <workspace-path>` and multiple candidates report `Source Repository selection is ambiguous in workspace: <workspace-path>`.
- Selection uses only this filesystem topology; ignore editor organization and legacy repository-location configuration.
- On success, parse `SOURCE_REPO`, `WORKTREE_PATH`, `BRANCH`, and `TARGET_BRANCH` from `worktree_output`. All source code, Git, push, and PR operations run in `WORKTREE_PATH`.
- The executable creates a new worktree at `<SOURCE_REPO>.worktrees/<feature-branch>` or reuses and actualizes the requested existing worktree.
- If `worktree_status` is neither `0` nor `3`, **exit** and report the executable output.

If `worktree_status` is `3`, parse `WORKTREE_PATH` and the conflicting files from `worktree_output`, then:

1. Collect the list of conflicting files:
   ```bash
  cd "$WORKTREE_PATH"
   ```
2. Invoke the `codey` agent directly via `runSubagent` from the current Worktree Path. Do not provide a workspace-path argument. Codey uses its invocation directory as its workspace. If Codey is unavailable, report `STATUS: blocked` naming Codey; do not substitute another agent. Pass the following prompt:
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
4. If the merge still fails, **exit** and report the unresolved files as blockers. Otherwise, remove `MERGE_CONFLICTS:` and following lines from `worktree_output` before Output.

## Output

Report the success output from the executable unchanged:

```
SOURCE_REPO: $SOURCE_REPO
WORKTREE_PATH: $WORKTREE_PATH
BRANCH: <feature-branch>
TARGET_BRANCH: <target-branch>
```
