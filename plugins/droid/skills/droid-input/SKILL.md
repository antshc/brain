---
name: droid-input
description: Resolve Harness Settings and the CODE/VERIFY/MEMORY/LOG paths. Apply during the INPUT step, before guardrails.
---

# Input

```
Input Progress:
- [ ] Step 1: Resolve Harness Settings
- [ ] Step 2: Resolve CODE_PATH, VERIFY_PATH, MEMORY_PATH, LOG_PATH
- [ ] Step 3: Handle missing paths (create LOG.md if missing; log discovery-gap entry for any other missing path)
```

## Step 1: Resolve Harness Settings

1. If `/resolve-harness` is available, invoke it from cwd; retain emitted `KEY=value` lines as invocation-scoped `HARNESS_SETTINGS`; set `HARNESS_ROOT` from its value.
2. If unavailable or it emits `HARNESS_ROOT=`, set `HARNESS_ROOT` to cwd.
3. If available but exits non-zero, stop as blocked.

**Workspace = cwd.** Run all code, Git, build, test, and exploration commands there; do not determine whether it is a worktree or change directories to establish a workspace.

## Step 2: Resolve CODE_PATH, VERIFY_PATH, MEMORY_PATH, LOG_PATH

```text
CODE_PATH, VERIFY_PATH, MEMORY_PATH, LOG_PATH := matching HARNESS_SETTINGS values
scan HARNESS_ROOT recursively once only for each missing path: CODE.md, VERIFY.md, MEMORY.md, LOG.md
use matching discovered paths  # at most one per filename; do not resolve duplicates
```

Substitute `HARNESS_ROOT` literally wherever `$HARNESS_ROOT` appears.

## Step 3: Handle missing paths

- If `LOG_PATH` is missing: create `$HARNESS_ROOT/LOG.md`; `LOG_PATH` := that path.
- If `CODE_PATH`, `VERIFY_PATH`, or `MEMORY_PATH` is missing: append one pre-phase droid-log discovery-gap entry to `LOG_PATH` — `category := other; severity := note; problem := every missing filename`.
- Do not create missing `CODE.md`, `VERIFY.md`, or `MEMORY.md`. The discovery-gap entry is separate from the end-of-run problem log.
- Pass each resolved `*_PATH` only to its applicable skill; never pass a workspace path.

**Emit**: "HARNESS_ROOT=<path> (resolver | fallback cwd). Workspace=<cwd>. Resolved: CODE=<path | missing>, VERIFY=<path | missing>, MEMORY=<path | missing>, LOG=<path>."
