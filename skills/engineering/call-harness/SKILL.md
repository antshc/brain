---
name: call-harness
description: Access files or run commands in the repository containing this repository-installed skill, even when invoked from a nested Git repository or subagent cwd.
---

# Call Harness

Use the repository containing this installed skill as the **Harness Repo Path**. The caller's cwd may be a nested repository with its own `.git`; cwd never determines the harness.

`<skill-directory>` is the directory containing this `SKILL.md`: take the absolute path used to read this file and strip the trailing `/SKILL.md`.

Resolve once:

```bash
HARNESS_REPO_PATH="$(python3 <skill-directory>/scripts/harness_path.py)"
```

Resolve an existing harness-relative file or directory:

```bash
TARGET="$(python3 <skill-directory>/scripts/harness_path.py <relative-path>)"
```

Use `$TARGET` to read/run that resource. For repository commands, use `git -C "$HARNESS_REPO_PATH" ...` or run the command with `$HARNESS_REPO_PATH` as its working directory.

The resolver anchors Git lookup at the skill directory, not cwd, so a nested repository cannot capture resolution. A target path must stay inside the harness repository and must exist.

This skill requires repository installation: the installed `call-harness` directory must itself live inside the harness repository.
