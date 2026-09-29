---
name: init-harness
description: Create or update the Harness Configuration File in the current directory, and install the harness's pull command.
disable-model-invocation: true
---

# Setup Harness

Run from the intended harness directory.

## 1. Ensure the settings file exists

If `$PWD/.harness.json.user` does not exist, create it holding `{}`. Never overwrite an existing file — every other plugin's section lives in it, and this skill only ensures it exists.

## 2. Keep it out of version control

```bash
git check-ignore -q .harness.json.user
```

Non-zero exit → append `*.user` to `.gitignore` (create the file if needed) and report it. Never write `.harness.json.user` itself into `.gitignore` — the existing `*.user` pattern is the intended match.

## 3. Install the pull command

Resolve `<skill-directory>` the same way as `/resolve-harness`: strip the trailing `/SKILL.md` from the path you used to read this file. Copy `<skill-directory>/scripts/pull-repos.py` to `$PWD/pull-repos.py`:

- Destination absent → copy it, report "created".
- Destination present and byte-identical → leave it, report "unchanged".
- Destination present and differs → overwrite it, report "updated".

`pull-repos.py` is committed at the harness root — it is the only reader of `harness.repos` and reads its sibling `.harness.json.user` directly.

Emit the settings-file status (created/already present) and the pull-command status (created/updated/unchanged).
