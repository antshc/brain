---
name: resolve-harness
description: Resolve Harness Settings from the nearest ancestor .harness.json.user file.
---

# Resolve Harness

Run from cwd. `<skill-directory>` is the directory containing this SKILL.md file: take the absolute path you used to read this file and strip the trailing `/SKILL.md`. Never derive it any other way, and never search the filesystem for it (e.g. do not run `find`, `ls -R`, or similar).

```bash
python3 <skill-directory>/scripts/resolve_harness.py
```

If you cannot confidently identify `<skill-directory>` from the path you read, treat this skill as unavailable — do not search the filesystem to locate it. Callers already define the fallback for an unavailable skill (use cwd as `HARNESS_REPO_PATH`).

Search cwd and ancestors for the nearest `.harness.json.user`; do not use Git or modify the filesystem.

- Found: emit one JSON object on stdout — `{harnessRepoPath, harness, atl, ...}`, one key per plugin section present in the file, `harness` and `atl` defaulting to `{}` when absent. Never emits a `credentials` key or any secret it holds — callers needing a credential read it from the file directly, in the step that uses it.
- Missing: emit `{"harnessRepoPath": "", "harness": {}, "atl": {}}` to stdout, explain cwd fallback on stderr, exit successfully.
- Invalid (not parseable JSON, or not a JSON object): write the error to stderr and exit non-zero.

Retain the emitted JSON only for this invocation, as `HARNESS_SETTINGS`. Use its `harnessRepoPath` value as `HARNESS_REPO_PATH`. If the skill is unavailable or `harnessRepoPath` is empty, use cwd as `HARNESS_REPO_PATH`.