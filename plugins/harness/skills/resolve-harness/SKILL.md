---
name: resolve-harness
description: Resolve Harness Settings from the nearest ancestor .harness.env file.
---

# Resolve Harness

Run from cwd. `<skill-directory>` is the directory containing this SKILL.md file — you already know this path from where the skill was loaded; never search the filesystem for it (e.g. do not run `find`):

```bash
python3 <skill-directory>/scripts/resolve_harness.py
```

Search cwd and ancestors for the nearest `.harness.env`; do not use Git or modify the filesystem.

- Found: emit every `KEY=value`; require non-empty `HARNESS_ROOT`.
- Missing: emit `HARNESS_ROOT=` to stdout, explain cwd fallback on stderr, exit successfully.
- Invalid: write the error to stderr and exit non-zero.

Retain emitted `HARNESS_SETTINGS` only for this invocation. If the skill is unavailable or `HARNESS_ROOT` is empty, use cwd as `HARNESS_ROOT`.