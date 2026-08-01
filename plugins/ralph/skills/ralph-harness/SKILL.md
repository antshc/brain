---
name: ralph-harness
description: Resolve the Harness Root (current repo) and Source Repository (nested workspace/ repo when present, else Harness Root). Used by ralph-worktree, ralph-dev, and ralph-fix before any git operation.
---

# Harness Resolution

Resolve which repo is the Harness Root and which is the Source Repository, before any branch, worktree, or commit operation.

```bash
HARNESS_ROOT=$(pwd)
src_git=$(find "$HARNESS_ROOT/workspace" -maxdepth 2 -name .git -type d 2>/dev/null | head -n1)
if [ -n "$src_git" ]; then
  SOURCE_REPO=$(dirname "$src_git")
else
  SOURCE_REPO=$HARNESS_ROOT
fi
```

- If a `.git` directory is found under `workspace/` (including one subfolder level), the Source Repository is that repo.
- Otherwise, the Source Repository is `HARNESS_ROOT` itself.

## Output

Report the result:

```
HARNESS_ROOT: $HARNESS_ROOT
SOURCE_REPO: $SOURCE_REPO
```
