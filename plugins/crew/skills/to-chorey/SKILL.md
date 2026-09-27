---
name: to-chorey
description: "Run a standalone Chorey maintainability review of current uncommitted work for behavior-preserving cleanup. Use when the user asks for a cleanup pass outside Ralph's autonomous loop."
---

Pass the prompt below to `runSubagent`:`chorey`.

Run `/resolve-harness` skill and retain its emitted `HARNESS_REPO_PATH`. If it is unavailable or emits an empty value, omit the `## HARNESS` section entirely — Chorey falls back to cwd itself.

Chorey discovers uncommitted files and matches their review rules through `/crew-review`.

```
## HARNESS
HARNESS_REPO_PATH=<resolved path>
```

Invoke Chorey even with no uncommitted work — it reports `STATUS: complete` with no files changed rather than being skipped.

Never supply a `## BASELINE_COMMIT` section here — this entry point has no guaranteed checkpoint commit, so Chorey stays on its uncommitted-diff review with the manual-snapshot revert.
