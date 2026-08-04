---
name: to-chorey
description: Run the Chorey subagent to review uncommitted work for behavior-preserving cleanup. Use standalone, outside the autonomous loop, when uncommitted changes (from Codey or elsewhere) need a review pass.
---

Run the commands below, substitute their output into the prompt, then pass it to `runSubagent`:`chorey`.

Run `/resolve-harness` skill and retain its emitted `HARNESS_REPO_PATH`. If it is unavailable or emits an empty value, omit the `## HARNESS` section entirely — Chorey falls back to cwd itself.

```
## HARNESS
HARNESS_REPO_PATH=<resolved path>

## DIFF
`git add -A 2>/dev/null; DIFF=$(git diff --cached 2>/dev/null); [ -n "$DIFF" ] && echo "$DIFF" || echo "No uncommitted changes"`
```

Invoke Chorey even with no uncommitted work — it reports `STATUS: complete` with no files changed rather than being skipped.

Never supply a `## BASELINE_COMMIT` section here — this entry point has no guaranteed checkpoint commit, so Chorey stays on its uncommitted-diff review with the manual-snapshot revert.
