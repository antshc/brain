# Install Ralph and set up the harness

Follow this file only on explicit request in Copilot CLI. Confirm the intended Git harness root before installation and use it as CWD. WF may delegate this recipe with the explicit harness root. Resolve assets from this file's directory. Sets up `.github/skills/harness/`: copies the `harness` skill from template, ensures its settings file exists, installs its pull command. **MUST NOT** migrate an existing root-level `.harness.json.user` — clean installs only.

## Install the Copilot plugin

1. Check `copilot plugin marketplace list --json`. If `brain` is absent, run `copilot plugin marketplace add antshc/brain`. Use the existing Brain marketplace when it points to that repository or to this installer checkout for local testing. Stop on a source conflict.
2. Check `copilot plugin list --json`. Install a missing plugin with `copilot plugin install ralph@brain`. Local marketplaces can show uninstalled entries as disabled with `source: live`. For these entries, check only the matching `enabledPlugins` key in Copilot settings. An absent key permits the initial install; an explicit `false` is disabled. Recheck that `ralph` is enabled from `brain` and that its version matches [plugin.json](../plugin.json). Report policy blocks, disabled installs, version mismatches, and failed commands before writing target files. Leave upgrades and enablement of existing installs to the user.

## Workflow

`settingsPath := .github/skills/harness/.harness.json.user` (CWD). Stop before writing files if this path is tracked.

**1 — Copy the `harness` skill template.** `installDir :=` parent of this `install.md`'s absolute path from context. Copy `<installDir>/harness.SKILL.template.md` → CWD `.github/skills/harness/SKILL.md`, always overwriting.

```bash
python3 -c "
from pathlib import Path
import shutil
dest = Path('.github/skills/harness/SKILL.md')
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copy('<installDir>/harness.SKILL.template.md', dest)
"
```

**2 — Gitignore the settings file only.**

```bash
git check-ignore -q "$settingsPath" || echo "NOT IGNORED"
```

`NOT IGNORED` → append `.harness.json.user` line to CWD `.gitignore` (create if needed). Confirm the settings path is ignored before continuing. Keep the folder trackable.

**3 — Ensure the settings file exists.** If absent, create it holding `{}`. Preserve existing contents.

**4 — Install the pull command.** Copy `<installDir>/scripts/pull-repos.py` → CWD `.github/skills/harness/pull-repos.py`, always overwriting. It is the only reader of `repos` and reads its sibling `.harness.json.user` directly.

**5 — Report.** Plugin installed or reused; skill copied; settings-file status (created/already present); `.gitignore` status; pull-command status (created/overwritten).

## Rules

- Generated skill only under CWD `.github/skills/harness/`, never a plugin folder.
- `SKILL.md` and `pull-repos.py` always overwritten; the settings file never overwritten.
- No migration of a root-level `.harness.json.user` — report it if found, but do not move or read it.

## Gotchas

- **MUST NOT** `find`/`grep`/`ls -R` for this skill's directory or template; derive from this `install.md`'s absolute path in context.
- Resolve target paths from the confirmed harness root. Leave target changes uncommitted.

## Completion criteria

- Copied `SKILL.md` byte-identical to the template; `pull-repos.py` byte-identical to its source.
- `.harness.json.user` exists (`{}` when new) and is gitignored.
- On rerun the settings file is untouched; `SKILL.md` and `pull-repos.py` are refreshed.
