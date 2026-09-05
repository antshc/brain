---
name: resolve-harness
description: Resolve Harness Settings from the nearest ancestor .harness.env file.
---

# Resolve Harness

Run from cwd. `<skill-directory>` is the directory containing this SKILL.md file: take the absolute path you used to read this file and strip the trailing `/SKILL.md`. Never derive it any other way, and never search the filesystem for it (e.g. do not run `find`, `ls -R`, or similar).

```bash
python3 <skill-directory>/scripts/resolve_harness.py
```

If you cannot confidently identify `<skill-directory>` from the path you read, treat this skill as unavailable — do not search the filesystem to locate it. Callers already define the fallback for an unavailable skill (use cwd as `HARNESS_REPO_PATH`).

Search cwd and ancestors for the nearest `.harness.env`; do not use Git or modify the filesystem.

- Found: emit every `KEY=value`; require non-empty `HARNESS_REPO_PATH`.
- Missing: emit `HARNESS_REPO_PATH=` to stdout, explain cwd fallback on stderr, exit successfully.
- Invalid: write the error to stderr and exit non-zero.

Retain emitted `HARNESS_SETTINGS` only for this invocation. If the skill is unavailable or `HARNESS_REPO_PATH` is empty, use cwd as `HARNESS_REPO_PATH`.