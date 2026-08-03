---
name: to-chorey
description: Run the Chorey subagent to review uncommitted work for behavior-preserving cleanup. Use standalone, outside the autonomous loop, when uncommitted changes (from Codey or elsewhere) need a review pass.
---

Execute the commands below and substitute their output into the prompt before passing it to the subagent via `runSubagent`:`chorey`:

## Resolve Harness Settings

Run the `/resolve-harness` skill and retain its emitted `HARNESS_REPO_PATH` for this invocation. If the skill is unavailable or emits `HARNESS_REPO_PATH=` (empty), omit the `## HARNESS` section below entirely — Chorey falls back to cwd on its own.

```
## HARNESS
HARNESS_REPO_PATH=<resolved path>

## UNCOMMITTED WORK
`git add -A 2>/dev/null; DIFF=$(git diff --cached 2>/dev/null); [ -n "$DIFF" ] && echo "$DIFF" || echo "No uncommitted changes"`
```

Invoke Chorey even when there is no uncommitted work — it reports `STATUS: complete` with no files changed rather than being skipped; a review pass over nothing is a safe, valid outcome.
