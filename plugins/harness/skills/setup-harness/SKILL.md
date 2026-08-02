---
name: setup-harness
description: Create or update the Harness Configuration File in the current directory — resolving both the Harness Repo Path and the Codebase Repo Path, merging into an existing file rather than overwriting it.
disable-model-invocation: true
---

# Setup Harness

Run from the intended harness directory. Resolve its physical absolute path:

```bash
harnessRepoPath=$(pwd -P)
```

The actual source code may live in a separate repo under `workspace/`. Probe for it (same probe `/create-worktree` runs before any branch or worktree operation):

```bash
src_git=$(find "$harnessRepoPath/workspace" -maxdepth 2 -name .git -type d 2>/dev/null | head -n1)
if [ -n "$src_git" ]; then
  codebaseRepoPath=$(dirname "$src_git")
else
  codebaseRepoPath=$harnessRepoPath
fi
```

- If a `.git` directory is found under `workspace/` (including one subfolder level), `codebaseRepoPath` is that repo.
- Otherwise, `codebaseRepoPath` falls back to `harnessRepoPath`.

## No existing file

If `$PWD/.harness.env` does not exist, create it:

```bash
printf 'HARNESS_REPO_PATH=%s\nCODEBASE_REPO_PATH=%s\n' "$harnessRepoPath" "$codebaseRepoPath" > .harness.env
```

## Existing file — merge, never overwrite wholesale

`.harness.env` is gitignored — there is no undo, so never rewrite it wholesale. Merge instead:

1. Set `HARNESS_REPO_PATH` to `$harnessRepoPath` — update the line in place if present, else append it.
2. Set `CODEBASE_REPO_PATH` to `$codebaseRepoPath` — update the line in place if present, else append it.
3. Drop any legacy `HARNESS_ROOT=` line entirely — it is superseded by `HARNESS_REPO_PATH`.
4. Preserve every other line byte-for-byte, in its original order.

Emit the created path, or the merged settings plus a report of which lines were set, added, or dropped.